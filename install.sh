#!/bin/bash
# Installation script for Modbus RTU IO 8CH Control System
# Sets up Python virtual environment, dependencies, and PHP server configuration

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="Modbus RTU IO 8CH Control System"

echo "========================================="
echo "🚀 Installing $PROJECT_NAME"
echo "========================================="

# Check system requirements
check_requirements() {
    echo "📋 Checking system requirements..."
    
    # Check Python 3
    if ! command -v python &> /dev/null; then
        echo "❌ Error: Python 3 is not installed."
        echo "   Please install Python 3.7+ before continuing."
        exit 1
    fi
    
    PYTHON_VERSION=$(python --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "✅ Python $PYTHON_VERSION found"
    
    # Check PHP
    if ! command -v php &> /dev/null; then
        echo "❌ Error: PHP is not installed."
        echo "   Please install PHP 7.4+ before continuing."
        echo "   Ubuntu/Debian: sudo apt install php php-cli"
        echo "   macOS: brew install php"
        exit 1
    fi
    
    PHP_VERSION=$(php --version | head -1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "✅ PHP $PHP_VERSION found"
    
    # Check if running on supported OS
    OS=$(uname -s)
    echo "✅ Operating System: $OS"
    
    if [[ "$OS" == "Linux" ]]; then
        echo "✅ Linux detected - USB/RS485 support available"
    elif [[ "$OS" == "Darwin" ]]; then
        echo "⚠️  macOS detected - USB/RS485 support may require additional drivers"
    else
        echo "⚠️  Unsupported OS: $OS - USB/RS485 support not guaranteed"
    fi
}

# Create Python virtual environment
setup_python_env() {
    echo ""
    echo "🐍 Setting up Python virtual environment..."
    
    cd "$SCRIPT_DIR"
    
    # Remove existing venv if requested
    if [[ "$1" == "--clean" ]] && [[ -d "venv" ]]; then
        echo "🧹 Removing existing virtual environment..."
        rm -rf venv
    fi
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "venv" ]]; then
        echo "📦 Creating virtual environment..."
        python -m venv venv
    fi
    
    # Activate virtual environment
    echo "🔌 Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    echo "⬆️  Upgrading pip..."
    pip install --upgrade pip
    
    # Install Python dependencies
    echo "📚 Installing Python dependencies..."
    pip install -r requirements.txt
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Python dependencies installed successfully"
    else
        echo "❌ Failed to install Python dependencies"
        exit 1
    fi
}

# Setup environment file
setup_environment() {
    echo ""
    echo "⚙️  Setting up environment configuration..."
    
    if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
        echo "📝 Creating .env file..."
        cat > "$SCRIPT_DIR/.env" << 'EOF'
# Modbus RTU IO 8CH Control System Configuration

# API Configuration
API_HOST=localhost
API_PORT=8090
API_BASE_URL=http://localhost:8000

# PHP Server Configuration  
PHP_HOST=localhost
PHP_PORT=8080
PHP_DOCUMENT_ROOT=./

# Modbus Device Configuration
MODBUS_DEVICE_ADDRESS=1
MODBUS_BAUDRATE=9600
MODBUS_PORT=/dev/ttyUSB0
MODBUS_TIMEOUT=1

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=modbus.log

# Session Configuration
SESSION_TIMEOUT=3600

# Development Configuration
DEBUG=false
AUTO_REFRESH_INTERVAL=3000
EOF
        echo "✅ .env file created with default configuration"
    else
        echo "✅ .env file already exists"
    fi
}

# Check hardware permissions
check_hardware_permissions() {
    echo ""
    echo "🔐 Checking hardware permissions..."
    
    # Check if user is in dialout group (required for serial port access)
    if groups | grep -q dialout; then
        echo "✅ User is in dialout group - serial port access granted"
    else
        echo "⚠️  User is not in dialout group"
        echo "   To access USB/RS485 devices, add user to dialout group:"
        echo "   sudo usermod -a -G dialout \$USER"
        echo "   Then logout and login again"
    fi
    
    # Check for common USB-to-RS485 devices
    if ls /dev/ttyUSB* 2>/dev/null || ls /dev/ttyACM* 2>/dev/null; then
        echo "✅ USB serial devices detected:"
        ls -la /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || true
    else
        echo "⚠️  No USB serial devices found"
        echo "   Connect your USB-to-RS485 converter and Modbus device"
    fi
}

# Create desktop shortcuts (optional)
create_shortcuts() {
    echo ""
    echo "🖥️  Creating shortcuts..."
    
    # Make scripts executable
    chmod +x "$SCRIPT_DIR/start.sh"
    chmod +x "$SCRIPT_DIR/stop.sh"
    
    echo "✅ Scripts made executable"
    
    # Create simple launcher script
    cat > "$SCRIPT_DIR/launch.sh" << 'EOF'
#!/bin/bash
# Quick launcher for Modbus Control System

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Modbus RTU IO 8CH Control System..."
echo "   FastAPI: http://localhost:8000"
echo "   Web UI:  http://localhost:8080/modbus.php.svg"
echo ""
echo "Press Ctrl+C to stop all services"

# Start the system
./start.sh

# Wait for user interrupt
trap 'echo ""; echo "🛑 Stopping services..."; ./stop.sh; exit 0' INT
while true; do sleep 1; done
EOF
    
    chmod +x "$SCRIPT_DIR/launch.sh"
    echo "✅ Launch script created: ./launch.sh"
}

# Run installation steps
main() {
    echo "Installation started at $(date)"
    echo ""
    
    # Parse command line arguments
    CLEAN_INSTALL=false
    for arg in "$@"; do
        case $arg in
            --clean)
                CLEAN_INSTALL=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --clean    Remove existing virtual environment and reinstall"
                echo "  --help     Show this help message"
                echo ""
                exit 0
                ;;
        esac
    done
    
    check_requirements
    
    if [[ "$CLEAN_INSTALL" == true ]]; then
        setup_python_env --clean
    else
        setup_python_env
    fi
    
    setup_environment
    check_hardware_permissions
    create_shortcuts
    
    echo ""
    echo "========================================="
    echo "✅ Installation completed successfully!"
    echo "========================================="
    echo ""
    echo "📋 Next steps:"
    echo "   1. Connect your Modbus RTU IO 8CH device via USB-to-RS485"
    echo "   2. Update .env file with your device settings if needed"
    echo "   3. Run: ./start.sh  (or ./launch.sh for guided startup)"
    echo "   4. Open: http://localhost:8080/modbus.php.svg"
    echo ""
    echo "📖 Documentation: README.md"
    echo "🔧 Configuration: .env"
    echo "📊 API Docs: http://localhost:8000/docs (after starting)"
    echo ""
    echo "🎉 Happy controlling!"
    echo ""
}

# Run main function with all arguments
main "$@"
