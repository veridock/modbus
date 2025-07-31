from flask import Flask, Response, request, render_template_string, jsonify
import subprocess
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration
MODBUS_UNIT = int(os.getenv('MODBUS_DEVICE_ADDRESS', '1'))


def execute_mod_command(command_args):
    """Execute mod.py command and return result"""
    try:
        cmd = ['python', 'mod.py'] + command_args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            return {
                'success': True,
                'output': result.stdout.strip(),
                'command': ' '.join(command_args)
            }
        else:
            return {
                'success': False,
                'error': result.stderr.strip() or 'Command failed',
                'command': ' '.join(command_args)
            }
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Command timeout'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def parse_coil_output(output):
    """Parse coil read output to get boolean state"""
    # Example output: "Coils [0-0]: [True]" or "Coils [0-0]: [False]"
    if '[True]' in output:
        return True
    elif '[False]' in output:
        return False
    return None


@app.route('/')
def index():
    """Main control panel HTML"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Modular Modbus Control</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background: #f0f0f0;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                color: #333;
                text-align: center;
            }
            .module-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .module {
                background: white;
                border-radius: 10px;
                padding: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                text-align: center;
            }
            .module iframe {
                border: none;
                width: 100%;
                height: 100px;
            }
            .status-bar {
                background: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .section {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .refresh-all {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            .refresh-all:hover {
                background: #45a049;
            }
            h2 {
                color: #666;
                margin-top: 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 Modular Modbus Control System</h1>

            <div class="status-bar">
                <strong>System Status:</strong> Active | 
                <strong>Time:</strong> <span id="time">{{ time }}</span> |
                <button class="refresh-all" onclick="refreshAll()">🔄 Refresh All</button>
            </div>

            <div class="section">
                <h2>Digital Outputs (Click to Toggle)</h2>
                <div class="module-grid">
                    {% for i in range(8) %}
                    <div class="module">
                        <iframe id="output-{{ i }}" 
                                src="/module/input/{{ i }}" 
                                title="Output {{ i }}"></iframe>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <div class="section">
                <h2>Digital Inputs (Read Only)</h2>
                <div class="module-grid">
                    {% for i in range(8) %}
                    <div class="module">
                        <iframe id="input-{{ i }}" 
                                src="/module/input/{{ i }}" 
                                title="Input {{ i }}"></iframe>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <div class="section">
                <h2>Direct Command Execution</h2>
                <div style="margin: 10px 0;">
                    <input type="text" id="cmd-input" placeholder="e.g., rc 0 8" style="width: 200px; padding: 5px;">
                    <button onclick="executeCommand()">Execute</button>
                    <pre id="cmd-output" style="background: #f5f5f5; padding: 10px; margin-top: 10px; min-height: 50px;"></pre>
                </div>
            </div>
        </div>

        <script>
            function refreshAll() {
                // Refresh all modules
                for (let i = 0; i < 8; i++) {
                    document.getElementById('output-' + i).src = '/module/input/' + i + '?t=' + Date.now();
                    document.getElementById('input-' + i).src = '/module/input/' + i + '?t=' + Date.now();
                }
                // Update time
                document.getElementById('time').textContent = new Date().toLocaleTimeString();
            }

            function executeCommand() {
                const cmd = document.getElementById('cmd-input').value;
                if (!cmd) return;

                fetch('/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: cmd})
                })
                .then(r => r.json())
                .then(data => {
                    const output = document.getElementById('cmd-output');
                    if (data.success) {
                        output.textContent = data.output;
                    } else {
                        output.textContent = 'Error: ' + data.error;
                    }
                });
            }

            // Auto-refresh every 5 seconds
            setInterval(refreshAll, 5000);
        </script>
    </body>
    </html>
    '''
    return render_template_string(html, time=datetime.now().strftime('%H:%M:%S'))


@app.route('/module/input/<int:channel>')
def output_module(channel):
    """Individual output button module as SVG"""
    # Read current state
    result = execute_mod_command(['rc', str(channel), '1', str(MODBUS_UNIT)])
    state = False
    if result['success']:
        state = parse_coil_output(result['output'])

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <defs>
        <style>
            .button {{ 
                cursor: pointer; 
                transition: all 0.3s;
            }}
            .button:hover {{ 
                transform: scale(1.05); 
            }}
            .button:active {{ 
                transform: scale(0.95); 
            }}
            .on {{ fill: #4CAF50; }}
            .off {{ fill: #f44336; }}
            .text {{ 
                fill: white; 
                font-family: Arial; 
                font-size: 24px; 
                font-weight: bold; 
                text-anchor: middle; 
                pointer-events: none;
            }}
            .label {{
                fill: #666;
                font-family: Arial;
                font-size: 12px;
                text-anchor: middle;
            }}
        </style>
        <script>
            function toggle() {{
                // Submit form to toggle
                window.location.href = '/module/input/{channel}';
            }}
        </script>
    </defs>

    <rect x="10" y="10" width="80" height="60" rx="10" 
          class="button {'on' if state else 'off'}" 
          onclick="toggle()"/>

    <text x="50" y="45" class="text">DO{channel}</text>
    <text x="50" y="85" class="label">{'ON' if state else 'OFF'}</text>
</svg>'''
    return Response(svg, mimetype='image/svg+xml')


@app.route('/module/input/<int:channel>')
def input_module(channel):
    """Individual input indicator module as SVG"""
    # Read current state
    result = execute_mod_command(['rd', str(channel), '1', str(MODBUS_UNIT)])
    state = False
    if result['success'] and '[True]' in result['output']:
        state = True

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <defs>
        <style>
            .indicator {{ 
                transition: all 0.3s;
            }}
            .on {{ fill: #2196F3; }}
            .off {{ fill: #9E9E9E; }}
            .text {{ 
                fill: white; 
                font-family: Arial; 
                font-size: 24px; 
                font-weight: bold; 
                text-anchor: middle; 
            }}
            .label {{
                fill: #666;
                font-family: Arial;
                font-size: 12px;
                text-anchor: middle;
            }}
        </style>
    </defs>

    <rect x="10" y="10" width="80" height="60" rx="10" 
          class="indicator {'on' if state else 'off'}"/>

    <text x="50" y="45" class="text">DI{channel}</text>
    <text x="50" y="85" class="label">{'HIGH' if state else 'LOW'}</text>
</svg>'''
    return Response(svg, mimetype='image/svg+xml')


@app.route('/module/input/<int:channel>')
def toggle_action(channel):
    """Toggle output and redirect back"""
    # First read current state
    result = execute_mod_command(['rc', str(channel), '1', str(MODBUS_UNIT)])
    current_state = False
    if result['success']:
        current_state = parse_coil_output(result['output'])

    # Toggle state
    new_state = 0 if current_state else 1
    execute_mod_command(['wc', str(channel), str(new_state), str(MODBUS_UNIT)])

    # Redirect back to the module
    return f'''
    <html>
    <head>
        <meta http-equiv="refresh" content="0;url=/module/input/{channel}">
    </head>
    <body>Toggling output {channel}...</body>
    </html>
    '''


@app.route('/execute', methods=['POST'])
def execute_command():
    """Execute arbitrary mod.py command"""
    data = request.get_json()
    command = data.get('command', '').strip().split()

    if not command:
        return jsonify({'success': False, 'error': 'No command provided'})

    result = execute_mod_command(command)
    return jsonify(result)


@app.route('/module/button/<int:channel>')
def button_module(channel):
    """Alternative button module with form submission"""
    # Read current state
    result = execute_mod_command(['rc', str(channel), '1', str(MODBUS_UNIT)])
    state = False
    if result['success']:
        state = parse_coil_output(result['output'])

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xhtml="http://www.w3.org/1999/xhtml" 
     width="100" height="100" viewBox="0 0 100 100">
    <defs>
        <style>
            .btn {{
                cursor: pointer;
                transition: all 0.3s;
            }}
            .btn:hover {{
                opacity: 0.8;
            }}
        </style>
    </defs>

    <foreignObject x="0" y="0" width="100" height="100">
        <xhtml:form action="/module/input/{channel}" method="get" 
                    style="margin:0;padding:0;height:100%;">
            <xhtml:button type="submit" style="
                width: 100%;
                height: 100%;
                border: none;
                border-radius: 10px;
                background: {'#4CAF50' if state else '#f44336'};
                color: white;
                font-size: 20px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
            ">
                DO{channel}<xhtml:br/>
                {'ON' if state else 'OFF'}
            </xhtml:button>
        </xhtml:form>
    </foreignObject>
</svg>'''
    return Response(svg, mimetype='image/svg+xml')


@app.route('/module/led/<int:channel>')
def led_module(channel):
    """Simple LED indicator module"""
    # Read input state
    result = execute_mod_command(['rd', str(channel), '1', str(MODBUS_UNIT)])
    state = False
    if result['success'] and '[True]' in result['output']:
        state = True

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 50 50">
    <circle cx="25" cy="25" r="20" 
            fill="{'#00ff00' if state else '#333333'}" 
            stroke="#000" 
            stroke-width="2">
        {f'<animate attributeName="opacity" values="1;0.3;1" dur="1s" repeatCount="indefinite"/>' if state else ''}
    </circle>
    <text x="25" y="30" text-anchor="middle" 
          font-family="Arial" font-size="12" fill="white">
        {channel}
    </text>
</svg>'''
    return Response(svg, mimetype='image/svg+xml')


@app.route('/widget/gauge/<int:register>')
def gauge_widget(register):
    """Gauge widget for analog values from holding registers"""
    # Read register value
    result = execute_mod_command(['rh', str(register), '1', str(MODBUS_UNIT)])
    value = 0
    if result['success']:
        # Parse register value from output
        try:
            # Example: "Holding registers [0-0]: [1234]"
            output = result['output']
            if '[' in output and ']' in output:
                value_str = output[output.rfind('[') + 1:output.rfind(']')]
                value = int(value_str)
        except:
            value = 0

    # Convert to percentage (assuming 0-65535 range)
    percentage = (value / 65535) * 100
    angle = (percentage / 100) * 270 - 135  # -135 to +135 degrees

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="150" height="150" viewBox="0 0 150 150">
    <defs>
        <linearGradient id="grad{register}" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#4CAF50;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#8BC34A;stop-opacity:1" />
        </linearGradient>
    </defs>

    <!-- Background circle -->
    <circle cx="75" cy="75" r="60" fill="none" stroke="#ddd" stroke-width="15"/>

    <!-- Value arc -->
    <path d="M 75,75 L 35,115 A 60,60 0 {1 if percentage > 50 else 0},1 115,115"
          fill="none" stroke="url(#grad{register})" stroke-width="15" stroke-linecap="round"
          transform="rotate({angle} 75 75)"/>

    <!-- Center circle -->
    <circle cx="75" cy="75" r="45" fill="white"/>

    <!-- Value text -->
    <text x="75" y="70" text-anchor="middle" font-family="Arial" font-size="24" font-weight="bold">
        {value}
    </text>
    <text x="75" y="90" text-anchor="middle" font-family="Arial" font-size="12" fill="#666">
        Register {register}
    </text>
    <text x="75" y="105" text-anchor="middle" font-family="Arial" font-size="10" fill="#999">
        {percentage:.1f}%
    </text>
</svg>'''
    return Response(svg, mimetype='image/svg+xml')


@app.route('/widget/switch/<int:channel>')
def widget(channel):
    """iOS-style toggle switch widget"""
    # Read current state
    result = execute_mod_command(['rc', str(channel), '1', str(MODBUS_UNIT)])
    state = False
    if result['success']:
        state = parse_coil_output(result['output'])

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="80" viewBox="0 0 200 80">
    <defs>
        <style>
            .switch-bg {{
                cursor: pointer;
                transition: fill 0.3s;
            }}
            .switch-bg.on {{ fill: #4CAF50; }}
            .switch-bg.off {{ fill: #ccc; }}
            .switch-knob {{
                transition: transform 0.3s;
                pointer-events: none;
            }}
            .label {{
                font-family: Arial;
                font-size: 14px;
                fill: #333;
            }}
        </style>
        <script>
            function toggleSwitch() {{
                window.location.href = '/module/input/{channel}';
            }}
        </script>
    </defs>

    <!-- Label -->
    <text x="10" y="45" class="label">Channel {channel}</text>

    <!-- Switch background -->
    <rect x="100" y="25" width="80" height="30" rx="15" 
          class="switch-bg {'on' if state else 'off'}"
          onclick="toggleSwitch()"/>

    <!-- Switch knob -->
    <circle cx="{165 if state else 115}" cy="40" r="12" fill="white"
            class="switch-knob"/>

    <!-- State text -->
    <text x="140" y="70" text-anchor="middle" class="label" 
          style="font-size: 12px; fill: #666;">
        {'ON' if state else 'OFF'}
    </text>
</svg>'''
    return Response(svg, mimetype='image/svg+xml')


@app.route('/widget/command/<command>')
def command_widget(command):
    """Execute predefined commands"""
    commands = {
        'all_on': {'label': 'All ON', 'color': '#4CAF50',
                   'cmd': lambda: [execute_mod_command(['wc', str(i), '1', str(MODBUS_UNIT)]) for i in range(8)]},
        'all_off': {'label': 'All OFF', 'color': '#f44336',
                    'cmd': lambda: [execute_mod_command(['wc', str(i), '0', str(MODBUS_UNIT)]) for i in range(8)]},
        'read_all': {'label': 'Read All', 'color': '#2196F3',
                     'cmd': lambda: execute_mod_command(['rc', '0', '8', str(MODBUS_UNIT)])}
    }

    if command not in commands:
        command = 'read_all'

    cmd_info = commands[command]

    # Handle actual command execution
    if request.args.get('execute') == '1':
        cmd_info['cmd']()
        return f'''<html><head>
            <meta http-equiv="refresh" content="0;url=/widget/command/{command}">
            </head><body>Executing...</body></html>'''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50" viewBox="0 0 100 50">
    <defs>
        <style>
            .cmd-btn {{
                cursor: pointer;
                transition: all 0.3s;
            }}
            .cmd-btn:hover {{
                opacity: 0.8;
            }}
            .cmd-btn:active {{
                transform: scale(0.95);
            }}
        </style>
        <script>
            function executeCmd() {{
                window.location.href = '/widget/command/{command}?execute=1';
            }}
        </script>
    </defs>

    <rect x="5" y="5" width="90" height="40" rx="5" 
          fill="{cmd_info['color']}" class="cmd-btn"
          onclick="executeCmd()"/>

    <text x="50" y="30" text-anchor="middle" 
          font-family="Arial" font-size="14" fill="white" font-weight="bold"
          pointer-events="none">
        {cmd_info['label']}
    </text>
</svg>'''
    return Response(svg, mimetype='image/svg+xml')


@app.route('/widget/status')
def status_widget():
    """System status widget"""
    # Try to read some coils to check connection
    result = execute_mod_command(['rc', '0', '1', str(MODBUS_UNIT)])
    connected = result['success']

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="100" viewBox="0 0 300 100">
    <rect x="0" y="0" width="300" height="100" fill="#f5f5f5" stroke="#ddd"/>

    <!-- Status indicator -->
    <circle cx="30" cy="30" r="10" fill="{'#4CAF50' if connected else '#f44336'}">
        {f'<animate attributeName="r" values="10;12;10" dur="2s" repeatCount="indefinite"/>' if connected else ''}
    </circle>

    <text x="50" y="35" font-family="Arial" font-size="16" fill="#333">
        Modbus Status: {'Connected' if connected else 'Disconnected'}
    </text>

    <text x="30" y="60" font-family="Arial" font-size="12" fill="#666">
        Unit: {MODBUS_UNIT} | Time: {datetime.now().strftime('%H:%M:%S')}
    </text>

    <text x="30" y="80" font-family="Arial" font-size="10" fill="#999">
        Click to refresh →
    </text>

    <rect x="250" y="65" width="40" height="20" rx="3" fill="#2196F3" 
          style="cursor: pointer;" 
          onclick="window.location.href='/widget/status?t=' + Date.now()">
    </rect>
    <text x="270" y="78" text-anchor="middle" font-family="Arial" 
          font-size="10" fill="white" pointer-events="none">
        Refresh
    </text>
</svg>'''
    return Response(svg, mimetype='image/svg+xml')


@app.route('/widget/register/<int:register>')
def register_widget(register):
    """Read/Write register widget"""
    # Read current value
    result = execute_mod_command(['rh', str(register), '1', str(MODBUS_UNIT)])
    value = 0
    if result['success']:
        try:
            output = result['output']
            if '[' in output and ']' in output:
                value_str = output[output.rfind('[') + 1:output.rfind(']')]
                value = int(value_str)
        except:
            value = 0

    # Handle write action
    if request.args.get('action') == 'write':
        new_value = request.args.get('value', '0')
        execute_mod_command(['wr', str(register), new_value, str(MODBUS_UNIT)])
        return f'''<html><head>
            <meta http-equiv="refresh" content="0;url=/widget/register/{register}">
            </head><body>Writing...</body></html>'''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xhtml="http://www.w3.org/1999/xhtml" 
     width="250" height="120" viewBox="0 0 250 120">
    <rect x="0" y="0" width="250" height="120" fill="white" stroke="#ddd"/>

    <text x="10" y="20" font-family="Arial" font-size="14" fill="#333">
        Register {register}
    </text>

    <text x="10" y="45" font-family="Arial" font-size="20" font-weight="bold" fill="#2196F3">
        Value: {value}
    </text>

    <text x="10" y="65" font-family="Arial" font-size="10" fill="#666">
        Hex: 0x{value:04X} | Bin: {bin(value)[2:].zfill(16)}
    </text>

    <foreignObject x="10" y="75" width="230" height="35">
        <xhtml:form action="/widget/register/{register}" method="get" style="margin:0;">
            <xhtml:input type="hidden" name="action" value="write"/>
            <xhtml:input type="number" name="value" value="{value}" 
                         min="0" max="65535" style="width: 100px; padding: 3px;"/>
            <xhtml:button type="submit" style="padding: 3px 10px; margin-left: 5px;">
                Write
            </xhtml:button>
        </xhtml:form>
    </foreignObject>
</svg>'''
    return Response(svg, mimetype='image/svg+xml')


@app.route('/demo')
def demo_page():
    """Demo page showing various widgets"""
    return render_template_string(open('widget.html').read())


if __name__ == "__main__":
    app.run(debug=True, port=5002, host='0.0.0.0')