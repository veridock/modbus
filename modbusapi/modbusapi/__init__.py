"""
ModbusAPI - Unified API for Modbus communication
"""

__version__ = '0.1.0'

from .client import ModbusClient
from .api import create_rest_app, start_mqtt_broker
from .shell import main as shell_main

__all__ = ['ModbusClient', 'create_rest_app', 'start_mqtt_broker', 'shell_main']
