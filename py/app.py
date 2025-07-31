from flask import Flask, Response, abort, send_from_directory, request
import re
import os
from dotenv import load_dotenv
from datetime import datetime

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

        # Sandbox: only allow specific libraries + os and datetime
        local_vars = {
            "os": os,
            "datetime": datetime,
            "__file__": full_path,
            # Add your template variables here with default values
            "MODBUS_PORT": os.getenv("MODBUS_PORT", "/dev/ttyUSB0"),
            "REFRESH": int(os.getenv("REFRESH", "5000")),  # default 5 seconds
        }

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
        return Response(rendered_svg, mimetype="image/svg+xml")

    except Exception as err:
        return Response(f"<!-- Server error: {err} -->", mimetype="image/svg+xml", status=500)


@app.route('/')
def index():
    """List all .py.svg files in the current directory with preview"""
    import glob
    from pathlib import Path

    # Get all .py.svg files in the current directory
    svg_files = [f for f in glob.glob('*.py.svg') if Path(f).is_file()]

    # Generate HTML with grid layout
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SVG Files Preview</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px;
                background-color: #f5f5f5;
            }
            h1 { 
                color: #333; 
                text-align: center;
                margin-bottom: 30px;
            }
            .container { 
                max-width: 1400px; 
                margin: 0 auto;
                padding: 0 15px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                padding: 20px 0;
            }
            .svg-card {
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                overflow: hidden;
                transition: transform 0.2s;
            }
            .svg-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            .svg-preview {
                width: 100%;
                height: 200px;
                object-fit: contain;
                background: #f8f9fa;
                border-bottom: 1px solid #eee;
            }
            .svg-info {
                padding: 15px;
            }
            .svg-name {
                font-weight: bold;
                margin: 0 0 5px 0;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .svg-link {
                color: #0066cc;
                text-decoration: none;
                font-size: 14px;
            }
            .svg-link:hover {
                text-decoration: underline;
            }
            .no-files {
                text-align: center;
                color: #666;
                padding: 40px 20px;
                grid-column: 1 / -1;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                flex-wrap: wrap;
                gap: 15px;
            }
            .refresh-btn {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                text-decoration: none;
                display: inline-block;
            }
            .refresh-btn:hover {
                background: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>SVG Files Preview</h1>
                <a href="/" class="refresh-btn">⟳ Refresh List</a>
            </div>
            <div class="grid">
    """

    if not svg_files:
        html += '<div class="no-files">No .py.svg files found in the current directory.</div>'
    else:
        for file in sorted(svg_files):
            file_url = f"/{file}"
            file_name = Path(file).name
            html += f"""
                <div class="svg-card">
                    <img src="{file_url}" alt="{file_name}" class="svg-preview" 
                         onerror="this.onerror=null; this.src='data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'><text x=\'50%\' y=\'50%\' text-anchor=\'middle\' dominant-baseline=\'middle\' font-family=\'Arial\' font-size=\'10\' fill=\'#999\'>Preview not available</text></svg>'">
                    <div class="svg-info">
                        <div class="svg-name" title="{file_name}">{file_name}</div>
                        <a href="{file_url}" class="svg-link" target="_blank">Open in new tab</a>
                    </div>
                </div>
            """

    html += """
            </div>
        </div>
        <script>
            // Auto-refresh previews every 30 seconds
            setTimeout(() => {
                document.querySelectorAll('.svg-preview').forEach(img => {
                    const src = img.src;
                    img.src = '';
                    setTimeout(() => { img.src = src; }, 100);
                });
            }, 30000);
        </script>
    </body>
    </html>
    """

    return html

if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')
