#!/bin/bash

echo "Starting Simple Modbus Control Panel..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Python 3 is required but not installed!"
    exit 1
fi

# Install minimal requirements if needed
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing required packages..."
    pip3 install flask flask-cors pymodbus[serial] python-dotenv
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

# Run the simplified Flask app
echo "Starting Flask server on http://localhost:5001"
echo "Open http://localhost:5001 for HTML interface"
echo "Open http://localhost:5001/modbus.svg for SVG interface"
echo ""
echo "Press Ctrl+C to stop"

python flask.py
