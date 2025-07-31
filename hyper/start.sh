#!/bin/bash

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Creating and activating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "Installing required packages..."
    pip install --upgrade pip
    pip install flask flask-cors pymodbus[serial] python-dotenv
fi

echo "Starting Simple Modbus Control Panel..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Python 3 is required but not installed!"
    exit 1
fi

# Install minimal requirements if needed
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing required packages..."
    pip install flask flask-cors pymodbus[serial] python-dotenv
fi

# Check if mod.py exists
if [ ! -f "mod.py" ]; then
    echo "Error: mod.py not found!"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating default .env file..."
    cat > .env << EOF
# Modbus Configuration
MODBUS_PORT=/dev/ttyUSB0
MODBUS_BAUDRATE=9600
MODBUS_TIMEOUT=1.0
MODBUS_DEVICE_ADDRESS=1
EOF
fi

# Create a simple HTML file if it doesn't exist
if [ ! -f "modbus.html" ]; then
    echo "Creating default modbus.html..."
    cat > modbus.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Modbus Control Panel</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .status { padding: 10px; margin: 5px; border-radius: 5px; }
        .connected { background-color: #d4edda; color: #155724; }
        .disconnected { background-color: #f8d7da; color: #721c24; }
        button { padding: 8px 16px; margin: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Modbus RTU IO 8CH Control Panel</h1>
    <div id="status" class="status">Status: Loading...</div>
    <div id="outputs">
        <h2>Outputs</h2>
        <div id="output-buttons"></div>
    </div>
    <div id="inputs">
        <h2>Inputs</h2>
        <div id="input-status"></div>
    </div>
    <script>
        function updateStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').className = `status ${data.connected ? 'connected' : 'disconnected'}`;
                    document.getElementById('status').textContent = `Status: ${data.connected ? 'Connected' : 'Disconnected'}`;
                    
                    // Update output buttons
                    const outputButtons = document.getElementById('output-buttons');
                    outputButtons.innerHTML = '';
                    data.outputs.forEach((state, index) => {
                        const button = document.createElement('button');
                        button.textContent = `Output ${index + 1}: ${state ? 'ON' : 'OFF'}`;
                        button.onclick = () => toggleOutput(index + 1, !state);
                        outputButtons.appendChild(button);
                        outputButtons.appendChild(document.createElement('br'));
                    });
                    
                    // Update input status
                    const inputStatus = document.getElementById('input-status');
                    inputStatus.innerHTML = '';
                    data.inputs.forEach((state, index) => {
                        const div = document.createElement('div');
                        div.textContent = `Input ${index + 1}: ${state ? 'HIGH' : 'LOW'}`;
                        inputStatus.appendChild(div);
                    });
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('status').className = 'status disconnected';
                    document.getElementById('status').textContent = 'Status: Error connecting to server';
                });
        }
        
        function toggleOutput(channel, state) {
            fetch(`/control/${channel}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: state ? 'on' : 'off' })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateStatus();
                } else {
                    alert(`Error: ${data.error}`);
                }
            });
        }
        
        // Update status every second
        setInterval(updateStatus, 1000);
        
        // Initial update
        updateStatus();
    </script>
</body>
</html>
EOF
fi

# Make sure app.py is executable
chmod +x app.py

# Run the Flask app
echo -e "\nStarting Flask server on http://localhost:5000"
echo "Open http://localhost:5000 in your browser"
python app.py
