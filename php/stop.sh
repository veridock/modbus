#!/bin/bash
# Stop script for Modbus RTU IO 8CH Control System
# Stops both FastAPI backend and PHP development server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/modbus.pid"
PHP_PID_FILE="$SCRIPT_DIR/php.pid"
LOG_FILE="$SCRIPT_DIR/modbus.log"
PHP_LOG_FILE="$SCRIPT_DIR/php.log"

echo "🛑 Stopping Modbus RTU IO 8CH Control System..."

# Function to stop a service by PID file
stop_service() {
    local service_name="$1"
    local pid_file="$2"
    local process_name="$3"
    
    if [[ ! -f "$pid_file" ]]; then
        echo "📝 No $service_name PID file found"
        
        # Try to find and kill any running processes
        local PIDS=$(pgrep -f "$process_name")
        if [[ ! -z "$PIDS" ]]; then
            echo "🔍 Found running $service_name processes. Attempting to stop them..."
            for PID in $PIDS; do
                echo "   Killing process $PID"
                kill $PID 2>/dev/null
                sleep 1
                # Force kill if still running
                if ps -p $PID > /dev/null 2>&1; then
                    echo "   Force killing process $PID"
                    kill -9 $PID 2>/dev/null
                fi
            done
            echo "✅ Stopped $service_name processes"
            return 0
        else
            echo "ℹ️  No $service_name processes found running"
            return 1
        fi
    fi
    
    # Read PID from file
    local PID=$(cat "$pid_file")
    
    # Check if process is running
    if ps -p $PID > /dev/null 2>&1; then
        echo "🛑 Stopping $service_name (PID: $PID)..."
        
        # Try graceful shutdown first
        kill $PID 2>/dev/null
        
        # Wait up to 10 seconds for graceful shutdown
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                echo "✅ $service_name stopped gracefully"
                rm -f "$pid_file"
                return 0
            fi
            echo "   Waiting for $service_name to stop... ($i/10)"
            sleep 1
        done
        
        # Force kill if still running
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚡ Force stopping $service_name..."
            kill -9 $PID 2>/dev/null
            sleep 1
            
            if ps -p $PID > /dev/null 2>&1; then
                echo "❌ Failed to stop $service_name"
                return 1
            else
                echo "✅ $service_name force stopped"
                rm -f "$pid_file"
                return 0
            fi
        fi
    else
        echo "ℹ️  $service_name was not running (PID: $PID)"
        rm -f "$pid_file"
        return 0
    fi
}

# Main execution
main() {
    local fastapi_stopped=false
    local php_stopped=false
    
    echo ""
    echo "🔍 Checking running services..."
    
    # Stop FastAPI service
    if stop_service "FastAPI Backend" "$PID_FILE" "api.py"; then
        fastapi_stopped=true
    fi
    
    # Stop PHP server
    if stop_service "PHP Server" "$PHP_PID_FILE" "php -S"; then
        php_stopped=true
    fi
    
    echo ""
    
    # Summary
    if [[ "$fastapi_stopped" == true ]] || [[ "$php_stopped" == true ]]; then
        echo "========================================="
        echo "✅ Services stopped successfully!"
        echo "========================================="
        echo ""
        echo "📜 Log files preserved:"
        if [[ "$fastapi_stopped" == true ]]; then
            echo "   FastAPI: $LOG_FILE"
        fi
        if [[ "$php_stopped" == true ]]; then
            echo "   PHP Server: $PHP_LOG_FILE"
        fi
        echo ""
        echo "📊 Usage: tail -f <logfile> to view recent logs"
        echo "🚀 Restart: ./start.sh"
    else
        echo "ℹ️  No services were running"
        echo ""
        echo "🚀 Start services: ./start.sh"
    fi
    
    echo ""
}

# Run main function
main
