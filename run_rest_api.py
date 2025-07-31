#!/usr/bin/env python3
"""
Skrypt uruchamiający serwer REST API dla ModbusAPI
"""

import os
import sys
import json
import logging
from pathlib import Path
from functools import wraps
from typing import Dict, Any, Optional, List, Union

# Konfiguracja logowania
logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'INFO'),
    format=os.environ.get(
        'LOG_FORMAT',
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
)
logger = logging.getLogger(__name__)

# Załaduj zmienne środowiskowe z pliku .env
try:
    from dotenv import load_dotenv
    # Spróbuj załadować z różnych lokalizacji
    env_loaded = False
    if load_dotenv():
        env_loaded = True
        logger.debug('Loaded .env from current directory')
    
    parent_env = Path(__file__).parent / '.env'
    if parent_env.exists() and load_dotenv(dotenv_path=parent_env):
        env_loaded = True
        logger.debug(f'Loaded .env from {parent_env}')
    
    hyper_env = Path(__file__).parent / 'hyper' / '.env'
    if hyper_env.exists() and load_dotenv(dotenv_path=hyper_env):
        env_loaded = True
        logger.debug(f'Loaded .env from {hyper_env}')
        
    if not env_loaded:
        logger.warning('No .env file found')
        
except ImportError:
    logger.warning('python-dotenv not installed, skipping .env loading')

# Implementacja klienta Modbus
class ModbusClient:
    """Modbus client implementation"""
    
    def __init__(self, port=None, baudrate=None, timeout=None, unit=None):
        """Initialize Modbus client"""
        self.port = port or os.environ.get('MODBUS_PORT')
        self.baudrate = baudrate or int(os.environ.get('MODBUS_BAUDRATE', 9600))
        self.timeout = timeout or float(os.environ.get('MODBUS_TIMEOUT', 1.0))
        self.unit = unit or int(os.environ.get('MODBUS_DEVICE_ADDRESS', 1))
        self._connected = False
        
        # Try to auto-detect port if not specified
        if self.port is None:
            self.port = auto_detect_modbus_port()
            if self.port:
                logger.info(f"Auto-detected Modbus device at {self.port}")
            else:
                logger.warning("No Modbus device detected")
    
    def connect(self):
        """Connect to Modbus device"""
        logger.info(f"Connecting to Modbus device at {self.port}")
        self._connected = True
        return True
    
    def read_coils(self, address, count=1, unit=None):
        """Read coil values"""
        logger.info(f"Reading {count} coil(s) from address {address}")
        # Symulacja odczytu cewek
        return [True] * count
    
    def write_coil(self, address, value, unit=None):
        """Write coil value"""
        logger.info(f"Writing value {value} to coil at address {address}")
        # Symulacja zapisu cewki
        return True

def auto_detect_modbus_port():
    """Auto-detect Modbus serial port"""
    # Symulacja wykrywania portu
    return "/dev/ttyACM0"

# Implementacja REST API
try:
    from flask import Flask, request, jsonify, Response
    
    def create_rest_app(port=None, baudrate=None, timeout=None, 
                       host='0.0.0.0', api_port=5000, debug=False):
        """Create Flask application for REST API"""
        app = Flask(__name__)
        
        # Configure logging
        if not debug:
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
        
        # Create Modbus client
        modbus_client = ModbusClient(port=port, baudrate=baudrate, timeout=timeout)
        
        @app.before_request
        def connect_modbus():
            """Connect to Modbus device before each request"""
            if not modbus_client._connected:
                modbus_client.connect()
        
        @app.after_request
        def add_cors_headers(response):
            """Add CORS headers to allow cross-origin requests"""
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        
        @app.route('/status', methods=['GET'])
        def get_status():
            """Get Modbus connection status"""
            return jsonify({
                'status': 'ok',
                'connected': modbus_client._connected,
                'port': modbus_client.port,
                'baudrate': modbus_client.baudrate
            })
        
        @app.route('/coil/<int:address>', methods=['GET'])
        def read_coil(address):
            """Read single coil"""
            result = modbus_client.read_coils(address, 1)
            
            if result is None:
                return jsonify({'error': 'Failed to read coil'}), 500
                
            return jsonify({
                'address': address,
                'value': result[0],
                'value_display': 'ON' if result[0] else 'OFF'
            })
        
        @app.route('/toggle/<int:address>', methods=['POST'])
        def toggle_coil(address):
            """Toggle coil state"""
            # Read current state
            result = modbus_client.read_coils(address, 1)
            if result is None:
                return jsonify({'error': 'Failed to read coil'}), 500
                
            # Toggle state
            current_state = result[0]
            new_state = not current_state
            
            if modbus_client.write_coil(address, new_state):
                return jsonify({
                    'success': True,
                    'address': address,
                    'previous_value': current_state,
                    'previous_display': 'ON' if current_state else 'OFF',
                    'value': new_state,
                    'value_display': 'ON' if new_state else 'OFF'
                })
            else:
                return jsonify({'error': f'Failed to toggle coil {address}'}), 500
        
        @app.route('/scan', methods=['GET'])
        def scan_devices():
            """Scan for Modbus devices"""
            port = auto_detect_modbus_port()
            return jsonify({
                'devices': [{'port': port}] if port else []
            })
            
        return app
        
except ImportError:
    logger.error("Flask not installed. REST API will not be available.")
    Flask = None
    create_rest_app = None

# Main function
def main():
    """Main entry point"""
    # Pobierz konfigurację z zmiennych środowiskowych
    host = os.environ.get('MODBUSAPI_HOST', '0.0.0.0')
    port = int(os.environ.get('MODBUSAPI_PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    modbus_port = os.environ.get('MODBUS_PORT')
    baudrate = int(os.environ.get('MODBUS_BAUDRATE', 9600))
    timeout = float(os.environ.get('MODBUS_TIMEOUT', 1.0))
    
    print(f"Uruchamianie serwera REST API na {host}:{port}")
    print(f"Modbus port: {modbus_port}, baudrate: {baudrate}, timeout: {timeout}")
    
    if create_rest_app is None:
        print("Flask not installed. REST API will not be available.")
        print("Install with: pip install flask")
        sys.exit(1)
    
    # Utwórz i uruchom aplikację Flask
    app = create_rest_app(
        port=modbus_port,
        baudrate=baudrate,
        timeout=timeout,
        host=host,
        api_port=port,
        debug=debug
    )
    
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()
