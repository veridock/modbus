#!/bin/bash

echo "🚀 Starting Modular Modbus Control System..."
echo "=========================================="

# Check if mod.py exists
if [ ! -f "mod.py" ]; then
    echo "❌ Error: mod.py not found!"
    echo "Please make sure mod.py is in the same directory."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required!"
    exit 1
fi

# Create templates directory if it doesn't exist
mkdir -p templates

# Copy HTML files if they exist
if [ -f "widget.html" ]; then
    cp widget.html templates/
fi

if [ -f "dashboard.html" ]; then
    cp dashboard.html templates/
fi

# Check/create .env file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file with default settings..."
    cat > .env << EOF
# Modbus Configuration
MODBUS_PORT=/dev/ttyUSB0
MODBUS_BAUDRATE=9600
MODBUS_TIMEOUT=1.0
MODBUS_DEVICE_ADDRESS=1

# You can also use /dev/ttyACM0 for Arduino-based devices
# MODBUS_PORT=/dev/ttyACM0
EOF
    echo "✅ .env file created"
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip3 install -q flask python-dotenv pymodbus[serial] 2>/dev/null

# Test mod.py
echo "🔧 Testing mod.py..."
if python3 mod.py --help > /dev/null 2>&1; then
    echo "✅ mod.py is working"
else
    echo "⚠️  Warning: mod.py test failed, but continuing..."
fi

# Start the server
echo ""
echo "🌐 Starting Flask server..."
echo "=========================================="
echo "📍 Main Dashboard: http://localhost:5002/"
echo "📍 Demo Widgets:   http://localhost:5002/demo"
echo "📍 Custom Dashboard: http://localhost:5002/dashboard.html"
echo ""
echo "🔧 Individual Widget URLs:"
echo "   • Switch:    http://localhost:5002/widget/switch/0"
echo "   • Button:    http://localhost:5002/module/button/0"
echo "   • LED:       http://localhost:5002/module/led/0"
echo "   • Gauge:     http://localhost:5002/widget/gauge/0"
echo "   • Register:  http://localhost:5002/widget/register/0"
echo ""
echo "📝 Direct Command API:"
echo "   POST http://localhost:5002/execute"
echo "   Body: {\"command\": \"rc 0 8\"}"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="

# Run the modular app
python3 app.py