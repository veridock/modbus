#!/bin/bash
# Start script for Modbus RTU IO 8CH Control System
# Starts both FastAPI backend and PHP development server

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the root directory of the project (one level up from php directory)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# Set the path to the Python script
PYTHON_SCRIPT="$PROJECT_ROOT/api.py"
echo "Looking for API script at: $PYTHON_SCRIPT"
# Set up file paths
PID_FILE="$PROJECT_ROOT/modbus.pid"
PHP_PID_FILE="$SCRIPT_DIR/php.pid"
LOG_FILE="$PROJECT_ROOT/modbus.log"
PHP_LOG_FILE="$SCRIPT_DIR/php.log"

# Source environment variables
if [[ -f "$SCRIPT_DIR/.env" ]]; then
    source "$SCRIPT_DIR/.env"
fi

# Set defaults if not in .env
API_PORT=${API_PORT:-8090}
PHP_PORT=${PHP_PORT:-8080}
PHP_HOST=${PHP_HOST:-localhost}

# Check if services are already running
check_running_services() {
    local services_running=false
    
    if [[ -f "$PID_FILE" ]]; then
        local PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  FastAPI service is already running (PID: $PID)"
            services_running=true
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    if [[ -f "$PHP_PID_FILE" ]]; then
        local PHP_PID=$(cat "$PHP_PID_FILE")
        if ps -p $PHP_PID > /dev/null 2>&1; then
            echo "⚠️  PHP server is already running (PID: $PHP_PID)"
            services_running=true
        else
            rm -f "$PHP_PID_FILE"
        fi
    fi
    
    if [[ "$services_running" == true ]]; then
        echo "Use stop.sh to stop running services first"
        exit 1
    fi
}

# Check if Python script exists and virtual environment is set up
check_prerequisites() {
    # Ensure we're using the full path to the API script
    PYTHON_SCRIPT="$(realpath "$PYTHON_SCRIPT" 2>/dev/null || echo "$PYTHON_SCRIPT")"
    
    echo "Debug: Checking if file exists: $PYTHON_SCRIPT"
    if [[ ! -f "$PYTHON_SCRIPT" ]]; then
        echo "⚠️ Error: File not found: $PYTHON_SCRIPT"
        echo "Current directory: $(pwd)"
        echo "Directory contents of $(dirname "$PYTHON_SCRIPT"):"
        ls -la "$(dirname "$PYTHON_SCRIPT")" 2>/dev/null || echo "Could not list directory"
        exit 1
    fi
    echo "Found API script at: $PYTHON_SCRIPT"
    
    if [[ ! -d "$SCRIPT_DIR/venv" ]]; then
        echo "⚠️ Virtual environment not found. Run ./install.sh first."
        exit 1
    fi
    
    if [[ ! -f "$SCRIPT_DIR/modbus.php.svg" ]]; then
        echo "⚠️ modbus.php.svg not found in $SCRIPT_DIR"
        exit 1
    fi
}

# Start FastAPI backend service
start_fastapi() {
    echo "🚀 Starting FastAPI backend service..."
    echo "   Script: $PYTHON_SCRIPT"
    echo "   Log: $LOG_FILE"
    echo "   Port: $API_PORT"
    
    # Activate virtual environment and start the service in background
    nohup bash -c "source '$SCRIPT_DIR/venv/bin/activate' && python '$PYTHON_SCRIPT'" > "$LOG_FILE" 2>&1 &
    local SERVICE_PID=$!
    
    # Save PID to file
    echo $SERVICE_PID > "$PID_FILE"
    
    # Wait a moment to check if the service started successfully
    sleep 3
    
    if ps -p $SERVICE_PID > /dev/null 2>&1; then
        echo "✅ FastAPI service started successfully!"
        echo "   PID: $SERVICE_PID"
        echo "   URL: http://localhost:$API_PORT"
        return 0
    else
        echo "❌ Failed to start FastAPI service"
        echo "   Check log: $LOG_FILE"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Start PHP development server
start_php_server() {
    echo ""
    echo "🌐 Starting PHP development server with router..."
    echo "   Document root: $SCRIPT_DIR"
    echo "   Router: router.php"
    echo "   Log: $PHP_LOG_FILE"
    echo "   Port: $PHP_PORT"
    
    # Start PHP built-in server with router
    nohup php -d display_errors=On -d display_startup_errors=On -d error_reporting=E_ALL -S "$PHP_HOST:$PHP_PORT" -t "$SCRIPT_DIR" router.php > "$PHP_LOG_FILE" 2>&1 &
    local PHP_PID=$!
    
    # Save PID to file
    echo $PHP_PID > "$PHP_PID_FILE"
    
    # Wait a moment to check if the server started successfully
    sleep 2
    
    if ps -p $PHP_PID > /dev/null 2>&1; then
        echo "✅ PHP server with router started successfully!"
        echo "   PID: $PHP_PID"
        echo "   URL: http://$PHP_HOST:$PHP_PORT/modbus.php.svg"
        echo "   Router: Processes .php.svg files as PHP"
        # Healthcheck: czy serwer PHP odpowiada na SVG?
        sleep 2
        CURL_OUT=$(curl -s -o /dev/null -w "%{http_code}" "http://$PHP_HOST:$PHP_PORT/modbus.php.svg")
        if [[ "$CURL_OUT" != "200" ]]; then
            echo "❌ PHP serwer uruchomiony, ale plik modbus.php.svg nie odpowiada poprawnie (HTTP $CURL_OUT)!"
            echo "   Sprawdź log: $PHP_LOG_FILE oraz router.php."
            kill $PHP_PID 2>/dev/null
            rm -f "$PHP_PID_FILE"
            exit 1
        else
            echo "✅ Plik modbus.php.svg serwowany poprawnie (HTTP 200)"
            # --- Dogłębna walidacja JS przez nodejs ---
            echo "🔎 Walidacja JavaScript w modbus.php.svg przez Node.js..."
            JS_LOG_FILE="$SCRIPT_DIR/js_validation.log"
            php "$SCRIPT_DIR/validator.php" "$SCRIPT_DIR/modbus.php.svg" > "$JS_LOG_FILE" 2>&1
            if grep -q 'JavaScript syntax error' "$JS_LOG_FILE"; then
                echo "❌ Błąd składni JavaScript w modbus.php.svg! Szczegóły w $JS_LOG_FILE:"
                grep 'JavaScript syntax error' "$JS_LOG_FILE"
                kill $PHP_PID 2>/dev/null
                rm -f "$PHP_PID_FILE"
                exit 1
            else
                echo "✅ JavaScript w modbus.php.svg przeszedł walidację Node.js"
            fi
        fi
        return 0
    else
        echo "❌ Failed to start PHP server"
        echo "   Check log: $PHP_LOG_FILE"
        rm -f "$PHP_PID_FILE"
        return 1
    fi
}

# Open browser (optional)
open_browser() {
    echo ""
    echo "🌍 Opening web interface..."
    
    local WEB_URL="http://$PHP_HOST:$PHP_PORT/modbus.php.svg"
    
    # Try to open browser on different platforms
    if command -v xdg-open > /dev/null; then
        xdg-open "$WEB_URL" 2>/dev/null &
    elif command -v open > /dev/null; then
        open "$WEB_URL" 2>/dev/null &
    elif command -v start > /dev/null; then
        start "$WEB_URL" 2>/dev/null &
    else
        echo "   Manual: Open $WEB_URL in your browser"
        return 1
    fi
    
    echo "   Browser opened: $WEB_URL"
}

# Debug function to print variable values
debug_var() {
    local var_name=$1
    local var_value=${!var_name}
    echo "DEBUG: $var_name = '$var_value'"
}

# Main execution
main() {
    echo "========================================="
    echo "🚀 Starting Modbus RTU IO 8CH Control System"
    echo "========================================="
    
    # Debug output for important variables
    debug_var "SCRIPT_DIR"
    debug_var "PROJECT_ROOT"
    debug_var "PYTHON_SCRIPT"
    
    check_running_services
    check_prerequisites
    
    # Start FastAPI backend
    if ! start_fastapi; then
        echo "❌ Failed to start FastAPI backend"
        exit 1
    fi
    
    # Start PHP server
    if ! start_php_server; then
        echo "❌ Failed to start PHP server"
        echo "🛑 Stopping FastAPI service..."
        if [[ -f "$PID_FILE" ]]; then
            kill $(cat "$PID_FILE") 2>/dev/null
            rm -f "$PID_FILE"
        fi
        exit 1
    fi
    
    # Show status summary
    echo ""
    echo "========================================="
    echo "✅ All services started successfully!"
    echo "========================================="
    echo ""
    echo "🔗 Service URLs:"
    echo "   📊 API Documentation: http://localhost:$API_PORT/docs"
    echo "   📈 API Status:        http://localhost:$API_PORT/status"
    echo "   🎛️  Web Interface:     http://$PHP_HOST:$PHP_PORT/modbus.php.svg"
    echo ""
    echo "📋 Service Management:"
    echo "   🛑 Stop services:     ./stop.sh"
    echo "   📜 View FastAPI logs: tail -f $LOG_FILE"
    echo "   📜 View PHP logs:     tail -f $PHP_LOG_FILE"
    echo ""
    echo "💡 Tips:"
    echo "   • Ensure Modbus device is connected via USB-to-RS485"
    echo "   • Check .env file for configuration options"
    echo "   • Use Ctrl+C to stop if running in foreground"
    echo ""
    
    # Optionally open browser
    if [[ "$1" != "--no-browser" ]]; then
        open_browser
    fi
    
    echo "🎉 System ready! Happy controlling!"
    echo ""
}

# Run main function
main "$@"
