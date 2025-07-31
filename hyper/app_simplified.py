#!/usr/bin/env python3
"""
Simplified Hyper Modbus Dashboard
Refactored version with improved code organization and reduced duplication
"""

from flask import Flask, Response, request, jsonify, redirect, render_template
import logging
import os

# Import our new utility modules
from config import *
from utils.modbus_client import modbus_client
from utils.svg_processor import svg_processor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/')
def index():
    """Main dashboard page with overview of all widgets"""
    dashboard_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hyper Modbus Control Center</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0; padding: 0;
                background: #1e1e1e; color: #fff;
            }
            .header {
                background: #2d2d2d;
                padding: 20px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            .dashboard {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px; padding: 20px;
                max-width: 1400px; margin: 0 auto;
            }
            .panel {
                background: #2d2d2d;
                border-radius: 10px; padding: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }
            .panel h2 { margin: 0 0 20px 0; color: #007acc; }
            iframe { border: none; border-radius: 5px; }
            .nav-links {
                margin: 20px 0;
            }
            .nav-links a {
                color: #007acc;
                text-decoration: none;
                margin: 0 15px;
                padding: 8px 16px;
                border: 1px solid #007acc;
                border-radius: 5px;
                transition: all 0.3s;
            }
            .nav-links a:hover {
                background: #007acc;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚡ HYPER MODBUS CONTROL CENTER</h1>
            <div class="nav-links">
                <a href="/demo">Demo Widgets</a>
                <a href="/dashboard.html">Full Dashboard</a>
                <a href="/tests">Run Tests</a>
            </div>
        </div>
        
        <div class="dashboard">
            <div class="panel">
                <h2>System Status</h2>
                <iframe src="/widget/status" width="100%" height="150"></iframe>
            </div>
            
            <div class="panel">
                <h2>Digital Outputs</h2>
                <iframe src="/widget/switch/0" width="150" height="200" style="display: inline-block;"></iframe>
                <iframe src="/widget/switch/1" width="150" height="200" style="display: inline-block;"></iframe>
            </div>
            
            <div class="panel">
                <h2>Digital Inputs</h2>
                <iframe src="/module/led/0" width="150" height="150" style="display: inline-block;"></iframe>
                <iframe src="/module/led/1" width="150" height="150" style="display: inline-block;"></iframe>
            </div>
            
            <div class="panel">
                <h2>Analog Values</h2>
                <iframe src="/widget/gauge/0" width="150" height="200" style="display: inline-block;"></iframe>
                <iframe src="/widget/gauge/1" width="150" height="200" style="display: inline-block;"></iframe>
            </div>
            
            <div class="panel">
                <h2>Register Control</h2>
                <iframe src="/widget/register/0" width="100%" height="200"></iframe>
            </div>
        </div>

        <script>
            // Auto-refresh status every 5 seconds
            setInterval(() => {
                const statusFrame = document.querySelector('iframe[src="/widget/status"]');
                if (statusFrame) {
                    statusFrame.src = statusFrame.src;
                }
            }, 5000);
        </script>
    </body>
    </html>
    """
    return dashboard_html


@app.route('/demo')
def demo_page():
    """Demo page showing various widget types"""
    demo_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Widget Demo - Hyper Modbus</title>
        <style>
            body { font-family: Arial, sans-serif; background: #1e1e1e; color: #fff; margin: 0; padding: 20px; }
            .demo-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
            .demo-item { background: #2d2d2d; padding: 15px; border-radius: 8px; text-align: center; }
            .demo-item h3 { color: #007acc; margin-top: 0; }
            iframe { border: none; border-radius: 5px; }
            .back-link { display: inline-block; margin-bottom: 20px; color: #007acc; text-decoration: none; }
        </style>
    </head>
    <body>
        <a href="/" class="back-link">← Back to Dashboard</a>
        <h1>Widget Demo</h1>
        
        <div class="demo-grid">
            <div class="demo-item">
                <h3>Switch Widget</h3>
                <iframe src="/widget/switch/0" width="180" height="200"></iframe>
            </div>
            
            <div class="demo-item">
                <h3>Button Widget</h3>
                <iframe src="/module/button/0" width="180" height="150"></iframe>
            </div>
            
            <div class="demo-item">
                <h3>LED Indicator</h3>
                <iframe src="/module/led/0" width="180" height="150"></iframe>
            </div>
            
            <div class="demo-item">
                <h3>Gauge Widget</h3>
                <iframe src="/widget/gauge/0" width="180" height="200"></iframe>
            </div>
            
            <div class="demo-item">
                <h3>Register Widget</h3>
                <iframe src="/widget/register/0" width="180" height="200"></iframe>
            </div>
            
            <div class="demo-item">
                <h3>Status Widget</h3>
                <iframe src="/widget/status" width="180" height="150"></iframe>
            </div>
        </div>
    </body>
    </html>
    """
    return demo_html


# SVG Widget endpoints using Jinja templates
@app.route('/widget/gauge/<int:register>')
def widget_gauge(register):
    """Gauge widget for analog values using SVG template"""
    value = modbus_client.read_register(register) or 0
    response = render_template('gauge.svg', register=register, value=value)
    return Response(response, mimetype='image/svg+xml')


@app.route('/module/led/<int:channel>')
def module_led(channel):
    """LED indicator module using SVG template"""
    state = modbus_client.read_coil(channel)
    response = render_template('led.svg', channel=channel, state=state)
    return Response(response, mimetype='image/svg+xml')


@app.route('/module/input/<int:channel>')
def module_input(channel):
    """Digital output widget using SVG template"""
    state = modbus_client.read_coil(channel)
    response = render_template('output.svg', channel=channel, state=state)
    return Response(response, mimetype='image/svg+xml')


@app.route('/module/dynamic/<int:channel>')
def module_dynamic(channel):
    """Dynamic digital output widget with embedded Python processing"""
    state = modbus_client.read_coil(channel)
    
    # Use the SVG processor for embedded Python blocks
    context = {
        'channel': channel,
        'state': state,
        'debug_mode': True  # Enable debug mode for testing
    }
    
    svg_content = svg_processor.process_svg('dynamic_output.svg', context)
    return Response(svg_content, mimetype='image/svg+xml')


@app.route('/module/button/<int:channel>')
def module_button(channel):
    """Button widget using existing SVG template"""
    state = modbus_client.read_coil(channel)
    response = render_template('button.svg', channel=channel, state=state)
    return Response(response, mimetype='image/svg+xml')


# Legacy endpoints for compatibility - keeping some HTML widgets
@app.route('/widget/switch/<int:channel>')
def widget_switch(channel):
    """iOS-style toggle switch widget (HTML fallback)"""
    state = modbus_client.read_coil(channel)
    state_class = "active" if state else "inactive"
    state_text = "ON" if state else "OFF"
    
    html = f"""
    <!DOCTYPE html>
    <html><head><title>Switch {channel}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 10px; background: #1e1e1e; color: #fff; text-align: center; }}
        .switch {{ position: relative; display: inline-block; width: 60px; height: 34px; margin: 10px; }}
        .switch input {{ opacity: 0; width: 0; height: 0; }}
        .slider {{ position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 34px; }}
        .slider:before {{ position: absolute; content: ""; height: 26px; width: 26px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }}
        input:checked + .slider {{ background-color: #2196F3; }}
        input:checked + .slider:before {{ transform: translateX(26px); }}
    </style></head>
    <body>
        <h3>Output {channel}</h3>
        <form method="post" action="/toggle/{channel}">
            <label class="switch">
                <input type="checkbox" {"checked" if state else ""}>
                <span class="slider" onclick="this.parentElement.parentElement.submit()"></span>
            </label>
        </form>
        <p>Status: <span class="{state_class}">{state_text}</span></p>
        <script>setTimeout(() => window.location.reload(), 2000);</script>
    </body></html>
    """
    return html


@app.route('/widget/register/<int:register>')
def widget_register(register):
    """Register read/write widget (HTML)"""
    current_value = modbus_client.read_register(register) or 0
    
    html = f"""
    <!DOCTYPE html>
    <html><head><title>Register {register}</title>
    <style>body {{ font-family: Arial, sans-serif; margin: 0; padding: 15px; background: #1e1e1e; color: #fff; text-align: center; }}</style></head>
    <body>
        <h3>Register {register}</h3>
        <p>Current Value: <strong>{current_value}</strong></p>
        <form method="post" action="/write_register/{register}">
            <input type="number" name="value" value="{current_value}" style="padding: 5px; margin: 5px; border-radius: 3px; border: 1px solid #555; background: #333; color: #fff;">
            <button type="submit" style="background: #007acc; color: white; border: none; padding: 8px 16px; border-radius: 3px; cursor: pointer;">Write</button>
        </form>
        <script>setTimeout(() => window.location.reload(), 3000);</script>
    </body></html>
    """
    return html


@app.route('/widget/status')
def widget_status():
    """System status widget (HTML)"""
    try:
        result = modbus_client.execute_command(['help'])
        status = "Connected" if result['success'] else "Error"
        status_class = "status-good" if result['success'] else "status-error"
    except:
        status = "Disconnected"
        status_class = "status-error"
    
    html = f"""
    <!DOCTYPE html>
    <html><head><title>System Status</title>
    <style>body {{ font-family: Arial, sans-serif; margin: 0; padding: 15px; background: #1e1e1e; color: #fff; text-align: center; }} .status-good {{ color: #28a745; }} .status-error {{ color: #dc3545; }}</style></head>
    <body>
        <h3>System Status</h3>
        <p class="{status_class}"><strong>{status}</strong></p>
        <small>Auto-refresh: 2s</small>
        <script>setTimeout(() => window.location.reload(), 2000);</script>
    </body></html>
    """
    return html


# Action endpoints
@app.route('/toggle/<int:channel>', methods=['POST'])
def toggle_action(channel):
    """Toggle output channel and redirect back"""
    try:
        current_state = modbus_client.read_coil(channel)
        new_state = not current_state if current_state is not None else True
        success = modbus_client.write_coil(channel, new_state)
        
        if success:
            logger.info(f"Channel {channel} toggled to {'ON' if new_state else 'OFF'}")
        else:
            logger.error(f"Failed to toggle channel {channel}")
            
    except Exception as e:
        logger.error(f"Error toggling channel {channel}: {e}")
    
    # Redirect back to the referring page or dashboard
    return redirect(request.referrer or '/')


@app.route('/write_register/<int:register>', methods=['POST'])
def write_register_action(register):
    """Write value to register"""
    try:
        value = int(request.form.get('value', 0))
        success = modbus_client.write_register(register, value)
        
        if success:
            logger.info(f"Register {register} set to {value}")
        else:
            logger.error(f"Failed to write register {register}")
            
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid value for register {register}: {e}")
    except Exception as e:
        logger.error(f"Error writing register {register}: {e}")
    
    return redirect(request.referrer or '/')


@app.route('/execute', methods=['POST'])
def execute_command():
    """Execute arbitrary mod.py command via API"""
    try:
        data = request.get_json()
        if not data or 'command' not in data:
            return jsonify({'success': False, 'error': 'Missing command parameter'})
        
        command = data['command'].strip()
        if not command:
            return jsonify({'success': False, 'error': 'Empty command'})
        
        # Split command into arguments
        command_args = command.split()
        result = modbus_client.execute_command(command_args)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/tests')
def run_tests():
    """Simple test runner endpoint"""
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Runner - Hyper Modbus</title>
        <style>
            body { font-family: Arial, sans-serif; background: #1e1e1e; color: #fff; margin: 0; padding: 20px; }
            .test-container { max-width: 800px; margin: 0 auto; }
            .back-link { display: inline-block; margin-bottom: 20px; color: #007acc; text-decoration: none; }
            .run-btn { background: #007acc; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
            .run-btn:hover { background: #005fa3; }
            #output { background: #000; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="test-container">
            <a href="/" class="back-link">← Back to Dashboard</a>
            <h1>Frontend Test Runner</h1>
            <p>Click the button below to run the frontend test suite:</p>
            <button class="run-btn" onclick="runTests()">Run Tests</button>
            <div id="output"></div>
        </div>
        
        <script>
            async function runTests() {
                const output = document.getElementById('output');
                output.textContent = 'Running tests...\\n';
                
                try {
                    const response = await fetch('/api/run_tests', { method: 'POST' });
                    const result = await response.json();
                    output.textContent = result.output;
                } catch (error) {
                    output.textContent = 'Error running tests: ' + error.message;
                }
            }
        </script>
    </body>
    </html>
    """
    return test_html


@app.route('/api/run_tests', methods=['POST'])
def api_run_tests():
    """API endpoint to run tests"""
    try:
        import subprocess
        result = subprocess.run(
            ['python', 'run_tests.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout + result.stderr,
            'return_code': result.returncode
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f'Error running tests: {str(e)}',
            'return_code': -1
        })


# Serve the original dashboard.html if requested
@app.route('/dashboard.html')
def dashboard_html():
    """Serve the original dashboard HTML file"""
    try:
        with open('dashboard.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Dashboard file not found", 404


if __name__ == "__main__":
    logger.info("Starting Hyper Modbus Dashboard (Simplified)")
    app.run(debug=FLASK_DEBUG, port=FLASK_PORT, host=FLASK_HOST)
