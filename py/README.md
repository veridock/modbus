# Python Web Application with Dynamic Content

This is a Flask-based web application that can render dynamic content using Python code embedded in HTML and SVG files.

## Features

- Dynamic rendering of `.py.html` and `.py.svg` files
- Python code execution within `<?py ... ?>` tags
- Environment variable support via `.env` file
- Template variable support with `{{ VARIABLE }}` syntax
- Automatic reloading in development mode

## File Structure

- `app.py` - Main Flask application
- `index.py.html` - Main page with test cases
- `.env` - Environment variables (create this file)
- `requirements.txt` - Python dependencies
- `start.sh` - Start the development server
- `stop.sh` - Stop the development server
- `install.sh` - Set up the development environment

## Getting Started

1. **Set up the environment**:
   ```bash
   ./install.sh
   ```

2. **Create a `.env` file** (if not already present):
   ```bash
   MODBUS_PORT=/dev/ttyUSB0
   REFRESH=5000
   # Add other environment variables as needed
   ```

3. **Start the server**:
   ```bash
   ./start.sh
   ```
   The application will be available at `http://localhost:5001`

4. **Stop the server**:
   ```bash
   ./stop.sh
   ```

## Template Structure

### Variable Definition and Usage

1. **Python Block for Logic**:
   - Define all variables in a Python block at the top of the file
   - Include all necessary imports and error handling
   - Example:
     ```python
     <?py
     import requests
     import os
     from datetime import datetime
     
     # Configuration
     MODBUS_API = os.getenv("MODBUS_API", "http://localhost:8090")
     REFRESH = os.getenv("AUTO_REFRESH_INTERVAL", "3000")
     now = datetime.now().strftime("%H:%M:%S")
     
     # Try to get status
     try:
         res = requests.get(f"{MODBUS_API}/status", timeout=2)
         data = res.json()
         connected = data.get("connected", False)
         error_msg = None
     except Exception as e:
         connected = False
         error_msg = str(e)
     
     # Derived variables
     CONNECTION = 'connected' if connected else 'disconnected'
     ?>
     ```

2. **JSON Metadata Block**:
   - Use a `<script type="application/json">` block for configuration
   - Reference variables using `{{VARIABLE}}` syntax
   - Example:
     ```xml
     <script type="application/json" id="app-metadata">
     {
         "api": {
             "baseUrl": "{{MODBUS_API}}",
             "status": "{{CONNECTION}}"
         },
         "ui": {
             "refreshInterval": {{REFRESH}},
             "lastUpdated": "{{now}}",
             "error": "{{error_msg or ''}}"
         },
         "version": "1.0.0"
     }
     </script>
     ```

3. **Key Points**:
   - Always define variables before using them in templates
   - Use uppercase for configuration variables
   - Keep the JSON structure clean and valid
   - Handle errors gracefully in the Python block
   - Use `{{variable or ''}}` to provide default empty values

## Code Style Guidelines

### Variable Usage

1. **Single Variables**: Use single variables for better readability and maintainability. This makes it easier to track where values are used and modified.

   ```python
   # Good
   MODBUS_API = os.getenv("MODBUS_API", "http://localhost:8090")
   REFRESH = os.getenv("AUTO_REFRESH_INTERVAL", "3000")
   
   # Avoid
   config = {
       "api": {
           "baseUrl": os.getenv("MODBUS_API", "http://localhost:8090"),
           "refresh": os.getenv("AUTO_REFRESH_INTERVAL", "3000")
       }
   }
   ```

2. **Python Code Blocks**: Always use `<?py print ... ?>` instead of `<?py= ... ?>` for output. This is more explicit and consistent with Python's syntax.

   ```html
   <!-- Good -->
   <p>Current time: <?py print datetime.now().strftime('%Y-%m-%d %H:%M:%S') ?></p>
   
   <!-- Avoid -->
   <p>Current time: <?py= datetime.now().strftime('%Y-%m-%d %H:%M:%S') ?></p>
   ```

3. **JSON Metadata**: When generating JSON metadata, ensure proper escaping and formatting to avoid parsing errors.

## Dynamic Content Syntax

### Python Code Blocks

Use `<?py ... ?>` to execute Python code. For output, use `<?py print ... ?>`:

```html
<p>Current time: <?py print datetime.now().strftime('%Y-%m-%d %H:%M:%S') ?></p>

<ul>
<?py
for i in range(3):
    print(f'<li>Item {i}</li>')
?>
</ul>
```

### Template Variables

Use `{{ VARIABLE }}` to insert variable values:

```html
<p>Modbus Port: {{ MODBUS_PORT }}</p>
<p>Refresh Rate: {{ REFRESH }} ms</p>
```

### Environment Variables

All environment variables are available in the template context:

```html
<p>Python Path: {{ PYTHONPATH }}</p>
<p>Current Directory: {{ PWD }}</p>
```

## Testing

To test the Python rendering functionality:

1. Start the server: `./start.sh`
2. Open `http://localhost:5001` in your browser
3. Check the "Python Rendering Tests" section for test results

## Security Notes

- Be cautious when using this in production as it allows arbitrary Python code execution
- Never expose this server to the internet without proper authentication
- Validate and sanitize all user inputs
- Keep dependencies up to date

## License

[Your License Here]
