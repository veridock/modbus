#!/bin/bash
set -e

echo "🚀 Setting up Modbus RTU IO 8CH Control System (Python version)"
echo "================================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed!"
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

echo "✅ Python 3 is installed"

# Create and activate virtual environment
echo "🔧 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "🔄 Upgrading pip..."
pip install --upgrade pip

# Install required packages
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies installed successfully"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔧 Creating .env file with default values..."
    cat > .env << 'EOL'
# Modbus RTU Configuration
MODBUS_PORT=/dev/ttyACM0
MODBUS_BAUDRATE=9600
MODBUS_TIMEOUT=1.0
MODBUS_UNIT_ID=1

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_RUN_PORT=5001

# API Configuration
API_BASE_URL=http://localhost:${FLASK_RUN_PORT}
MODBUS_API=${API_BASE_URL}

# Application Settings
AUTO_REFRESH_INTERVAL=3000  # milliseconds
EOL
    echo "✅ .env file created with default values"
else
    echo "ℹ️  .env file already exists, skipping creation"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x start.sh
chmod +x app.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To start the application, run:"
echo "  source venv/bin/activate  # If not already activated"
echo "  ./start.sh"
echo ""
echo "Then open http://localhost:5001 in your browser"

# Deactivate virtual environment
deactivate
