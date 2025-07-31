"""
Configuration settings for Hyper Modbus Dashboard
Centralized configuration management
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Flask Configuration
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5002'))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Modbus Configuration
MODBUS_UNIT = int(os.getenv('MODBUS_DEVICE_ADDRESS', '1'))
MODBUS_PORT = os.getenv('MODBUS_PORT', '/dev/ttyUSB0')
MODBUS_BAUDRATE = int(os.getenv('MODBUS_BAUDRATE', '9600'))
MODBUS_TIMEOUT = float(os.getenv('MODBUS_TIMEOUT', '1.0'))

# Widget refresh intervals (in milliseconds)
WIDGET_REFRESH_INTERVALS = {
    'status': 2000,
    'led': 1000,
    'gauge': 1500,
    'register': 3000
}

# Default widget channels/registers
DEFAULT_CHANNELS = 8
DEFAULT_REGISTERS = 10
