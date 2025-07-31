#!/usr/bin/env python3
"""
Skrypt uruchamiający serwer REST API dla ModbusAPI
"""

import os
import sys
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

# Dodaj katalog główny projektu do ścieżki Pythona
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from modbusapi.modbusapi.api import create_rest_app
    
    # Pobierz konfigurację z zmiennych środowiskowych
    host = os.environ.get('MODBUSAPI_HOST', '0.0.0.0')
    port = int(os.environ.get('MODBUSAPI_PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    modbus_port = os.environ.get('MODBUS_PORT')
    baudrate = int(os.environ.get('MODBUS_BAUDRATE', 9600))
    timeout = float(os.environ.get('MODBUS_TIMEOUT', 1.0))
    
    print(f"Uruchamianie serwera REST API na {host}:{port}")
    print(f"Modbus port: {modbus_port}, baudrate: {baudrate}, timeout: {timeout}")
    
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
    
except ImportError as e:
    print(f"Błąd importu: {e}")
    print("Upewnij się, że wszystkie wymagane biblioteki są zainstalowane:")
    print("pip install -e .")
    sys.exit(1)
except Exception as e:
    print(f"Błąd: {e}")
    sys.exit(1)
