from flask import Flask, Response, jsonify, request, render_template_string
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Import your existing ModbusRTUClient
from ..mod import ModbusRTUClient, auto_detect_modbus_port

load_dotenv()

app = Flask(__name__)
CORS(app)

# Global Modbus client
modbus_client = None
device_state = {
    "connected": False,
    "outputs": [False] * 8,
    "inputs": [False] * 8,
    "error": None
}

def init_modbus():
    """Initialize Modbus connection"""
    global modbus_client, device_state
    
    try:
        # Try auto-detection first
        port = auto_detect_modbus_port()
        if port:
            modbus_client = ModbusRTUClient(port=port)
        else:
            # Use .env configuration
            modbus_client = ModbusRTUClient()
        
        if modbus_client.connect():
            device_state["connected"] = True
            device_state["error"] = None
            update_device_state()
            return True
    except Exception as e:
        device_state["error"] = str(e)
        device_state["connected"] = False
    
    return False

def update_device_state():
    """Update device state from Modbus"""
    global modbus_client, device_state
    
    if not modbus_client or not device_state["connected"]:
        return
    
    try:
        # Read outputs
        outputs = modbus_client.read_coils(0, 8, unit=1)
        if outputs:
            device_state["outputs"] = outputs[:8]
        
        # Read inputs
        inputs = modbus_client.read_discrete_inputs(0, 8, unit=1)
        if inputs:
            device_state["inputs"] = inputs[:8]
            
    except Exception as e:
        device_state["error"] = str(e)
        device_state["connected"] = False

# Initialize on startup
init_modbus()

@app.route("/")
def index():
    """Simple HTML control panel"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Modbus Control Panel</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .button { 
                width: 80px; height: 80px; margin: 5px;
                font-size: 16px; border-radius: 8px;
                cursor: pointer; transition: all 0.3s;
            }
            .button.on { background: #4CAF50; color: white; }
            .button.off { background: #f44336; color: white; }
            .status { margin: 20px 0; padding: 10px; background: #f0f0f0; }
            .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
        </style>
    </head>
    <body>
        <h1>Modbus RTU Control Panel</h1>
        <div class="status">
            <strong>Connection:</strong> <span id="connection">Checking...</span><br>
            <strong>Last Update:</strong> <span id="timestamp">-</span>
        </div>
        
        <h2>Digital Outputs</h2>
        <div class="grid" id="outputs"></div>
        
        <h2>Digital Inputs</h2>
        <div class="grid" id="inputs"></div>
        
        <script>
            function updateStatus() {
                fetch('/api/status')
                    .then(r => r.json())
                    .then(data => {
                        // Update connection status
                        document.getElementById('connection').textContent = 
                            data.connected ? 'Connected' : 'Disconnected';
                        document.getElementById('timestamp').textContent = 
                            new Date().toLocaleTimeString();
                        
                        // Update outputs
                        const outputsDiv = document.getElementById('outputs');
                        outputsDiv.innerHTML = '';
                        data.outputs.forEach((state, i) => {
                            const btn = document.createElement('button');
                            btn.className = `button ${state ? 'on' : 'off'}`;
                            btn.textContent = `DO${i}`;
                            btn.onclick = () => toggleOutput(i);
                            outputsDiv.appendChild(btn);
                        });
                        
                        // Update inputs
                        const inputsDiv = document.getElementById('inputs');
                        inputsDiv.innerHTML = '';
                        data.inputs.forEach((state, i) => {
                            const div = document.createElement('div');
                            div.className = `button ${state ? 'on' : 'off'}`;
                            div.textContent = `DI${i}`;
                            inputsDiv.appendChild(div);
                        });
                    });
            }
            
            function toggleOutput(channel) {
                fetch('/api/toggle/' + channel, { method: 'POST' })
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) updateStatus();
                    });
            }
            
            // Update every second
            setInterval(updateStatus, 1000);
            updateStatus();
        </script>
    </body>
    </html>
    '''
    return html

@app.route("/api/status")
def api_status():
    """Get current device status"""
    update_device_state()
    return jsonify(device_state)

@app.route("/api/toggle/<int:channel>", methods=["POST"])
def api_toggle(channel):
    """Toggle output channel"""
    global modbus_client, device_state
    
    if not modbus_client or not device_state["connected"]:
        return jsonify({"success": False, "error": "Not connected"})
    
    if channel < 0 or channel > 7:
        return jsonify({"success": False, "error": "Invalid channel"})
    
    try:
        # Get current state and toggle
        current_state = device_state["outputs"][channel]
        new_state = not current_state
        
        # Write to Modbus
        success = modbus_client.write_coil(channel, new_state, unit=1)
        
        if success:
            device_state["outputs"][channel] = new_state
            return jsonify({"success": True, "channel": channel, "state": new_state})
        else:
            return jsonify({"success": False, "error": "Write failed"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/modbus.svg")
def modbus_svg():
    """Simple SVG status display"""
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
    <rect width="100%" height="100%" fill="#f0f0f0"/>
    <text x="400" y="50" text-anchor="middle" font-size="30" fill="#333">
        Modbus Status: {"Connected" if device_state["connected"] else "Disconnected"}
    </text>
    
    <g transform="translate(50, 100)">
        <text font-size="20" fill="#666">Digital Outputs:</text>
        {"".join([f'<rect x="{i*90}" y="20" width="80" height="80" fill="{"#4CAF50" if device_state["outputs"][i] else "#f44336"}" rx="10"/><text x="{i*90+40}" y="65" text-anchor="middle" fill="white" font-size="16">DO{i}</text>' for i in range(8)])}
    </g>
    
    <g transform="translate(50, 250)">
        <text font-size="20" fill="#666">Digital Inputs:</text>
        {"".join([f'<rect x="{i*90}" y="20" width="80" height="80" fill="{"#2196F3" if device_state["inputs"][i] else "#9E9E9E"}" rx="10"/><text x="{i*90+40}" y="65" text-anchor="middle" fill="white" font-size="16">DI{i}</text>' for i in range(8)])}
    </g>
    
    <text x="50" y="450" font-size="14" fill="#666">
        Last Update: {datetime.now().strftime("%H:%M:%S")}
    </text>
</svg>'''
    return Response(svg, mimetype="image/svg+xml")

if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')
