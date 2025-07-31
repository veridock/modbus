from flask import Flask, Response, abort, send_from_directory, request, render_template_string
import re
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from validator import validate_and_clean_content, sanitize_error_message

# Load environment variables from .env file in the current directory
load_dotenv()

app = Flask(__name__, static_folder="static")

# 🔹 Listowanie katalogów w /static/ i podkatalogach
@app.route('/static/', defaults={'req_path': ''})
@app.route('/static/<path:req_path>')
def browse_static(req_path):
    base_dir = app.static_folder
    abs_path = os.path.join(base_dir, req_path)

    if not os.path.exists(abs_path):
        return abort(404)

    if os.path.isfile(abs_path):
        return send_from_directory(base_dir, req_path)

    # Renderowanie listy plików
    files = os.listdir(abs_path)
    file_links = [
        f"<li><a href='{request.path.rstrip('/')}/{name}'>{name}</a></li>"
        for name in files
    ]
    return f"<h2>Index of /static/{req_path}</h2><ul>{''.join(file_links)}</ul>"

# 🔹 Obsługa dynamicznych plików SVG z Pythonem (np. *.py.svg)
@app.route("/<path:filename>")
def render_dynamic_svg(filename):
    if not filename.endswith(".py.svg"):
        return abort(404)

    full_path = os.path.abspath(filename)
    if not os.path.isfile(full_path):
        return abort(404)

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            svg_template = f.read()

        # Load all required environment variables with defaults
        env_vars = {
            # Core configuration
            "MODBUS_API": os.getenv("MODBUS_API", "http://localhost:8090"),
            "API_BASE_URL": os.getenv("API_BASE_URL", os.getenv("MODBUS_API", "http://localhost:8090")),
            "AUTO_REFRESH_INTERVAL": os.getenv("AUTO_REFRESH_INTERVAL", "3000"),
            "MODBUS_PORT": os.getenv("MODBUS_PORT", "/dev/ttyUSB0"),
            
            # UI Configuration
            "REFRESH": os.getenv("REFRESH", os.getenv("AUTO_REFRESH_INTERVAL", "3000")),
            
            # System variables
            "__file__": full_path,
            "now": datetime.now().strftime("%H:%M:%S"),
            
            # Libraries
            "os": os,
            "datetime": datetime,
            "json": json,
            "requests": requests
        }
        
        # Update local_vars with environment variables
        local_vars = {**os.environ, **env_vars}

        def eval_block(match):
            code = match.group(1).strip()
            try:
                if code.startswith("="):
                    return str(eval(code[1:].strip(), {}, local_vars))
                else:
                    # Handle template variables like {{ VARIABLE }}
                    if code.startswith("{{") and code.endswith("}}"):
                        var_name = code[2:-2].strip()
                        return str(local_vars.get(var_name, "{{ " + var_name + " }}"))
                    exec(code, {}, local_vars)
                    return ''
            except Exception as e:
                return f"<!-- Python error: {e} -->"

        # First process Python code blocks
        svg_processed = re.sub(r"<\?py([\s\S]*?)\?>", eval_block, svg_template)
        # Then process template variables
        rendered_svg = re.sub(r"\{\{\s*([^}]+)\s*\}\}", 
                            lambda m: str(local_vars.get(m.group(1).strip(), m.group(0))), 
                            svg_processed)
        
        # Validate and clean the final SVG content
        is_valid, cleaned_svg, error = validate_and_clean_content(
            rendered_svg, 
            content_type='image/svg+xml'
        )
        
        if not is_valid:
            app.logger.error(f"SVG validation error: {error}")
            # Return a minimal valid SVG with the error message
            error_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="100">
                <rect width="100%" height="100%" fill="#ffebee"/>
                <text x="10" y="30" font-family="Arial" font-size="12" fill="#b71c1c">
                    {sanitize_error_message(error)[:100]}
                </text>
            </svg>'''
            return Response(error_svg, mimetype="image/svg+xml")
            
        return Response(cleaned_svg, mimetype="image/svg+xml")

    except Exception as err:
        return Response(f"<!-- Server error: {err} -->", mimetype="image/svg+xml", status=500)


def render_py_file(file_path, mimetype):
    """Render a .py.* file with Python code evaluation"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Create a context with environment variables and other useful stuff
        context = {
            'os': os,
            'datetime': datetime,
            'request': request,
            'env': dict(os.environ)  # Make all environment variables available
        }
        
        # Add all environment variables to context directly for easier access
        for key, value in os.environ.items():
            context[key] = value

        def eval_code_block(match):
            code = match.group(1).strip()
            try:
                if code.startswith("="):
                    # Expression evaluation (e.g., <?py= 1+1 ?>
                    return str(eval(code[1:].strip(), {}, context))
                else:
                    # Code execution (e.g., <?py x = 42 ?>
                    exec(code, {}, context)
                    return ''
            except Exception as e:
                return f"<!-- Python error: {e} -->"

        # Process Python code blocks
        content = re.sub(r'<\?py([\s\S]*?)\?>', eval_code_block, content)
        
        # Process template variables {{ VARIABLE }}
        content = re.sub(
            r'\{\{\s*([^}]+)\s*\}\}',
            lambda m: str(context.get(m.group(1).strip(), m.group(0))),
            content
        )
        
        return Response(content, mimetype=mimetype)

    except Exception as e:
        error_msg = f"<!-- Server error: {e} -->"
        if mimetype.startswith('image/svg'):
            error_msg = f'<svg><text x="10" y="20">{error_msg}</text></svg>'
        return Response(error_msg, mimetype=mimetype, status=500)

@app.route('/')
def index():
    """Serve the main index page"""
    return render_py_file('index.py.html', 'text/html')

@app.route('/<path:filename>')
def render_file(filename):
    """Handle .py.svg and .py.html files with dynamic content"""
    if not (filename.endswith('.py.svg') or filename.endswith('.py.html')):
        return abort(404)
    
    full_path = os.path.abspath(filename)
    if not os.path.isfile(full_path):
        return abort(404)
    
    mimetype = 'image/svg+xml' if filename.endswith('.svg') else 'text/html'
    return render_py_file(full_path, mimetype)

if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')
