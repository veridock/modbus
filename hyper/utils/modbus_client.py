"""
Modbus client utilities for Hyper Dashboard
Centralized Modbus communication functions using modbusapi package
"""

import os
import logging
from typing import Dict, Any, Optional

# Import modbusapi package
from modbusapi.client import ModbusClient as ModbusAPIClient, auto_detect_modbus_port
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Get configuration from environment
MODBUS_PORT = os.getenv('MODBUS_PORT')
MODBUS_BAUDRATE = int(os.getenv('MODBUS_BAUDRATE', '9600'))
MODBUS_TIMEOUT = float(os.getenv('MODBUS_TIMEOUT', '1.0'))
MODBUS_DEVICE_ADDRESS = int(os.getenv('MODBUS_DEVICE_ADDRESS', '1'))


class ModbusClient:
    """Centralized Modbus client for communication"""
    
    def __init__(self):
        self.timeout = MODBUS_TIMEOUT
        self.port = MODBUS_PORT or auto_detect_modbus_port()
        self.baudrate = MODBUS_BAUDRATE
        self.unit = MODBUS_DEVICE_ADDRESS
        
        # Create ModbusAPI client
        self.client = ModbusAPIClient(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
            unit=self.unit
        )
        
    def execute_command(self, command_args: list) -> Dict[str, Any]:
        """Execute Modbus command and return structured result"""
        try:
            command = command_args[0] if command_args else ''
            
            # Map command to appropriate method
            if command == 'rc':  # Read coil
                address = int(command_args[1])
                count = int(command_args[2]) if len(command_args) > 2 else 1
                values = self.client.read_coils(address, count, self.unit)
                
                if values is None:
                    return {
                        'success': False,
                        'output': '',
                        'command': ' '.join(command_args),
                        'error': 'Failed to read coils'
                    }
                
                return {
                    'success': True,
                    'output': str(values),
                    'command': ' '.join(command_args),
                    'error': None,
                    'data': {
                        'address': address,
                        'count': count,
                        'values': values
                    }
                }
                
            elif command == 'wc':  # Write coil
                address = int(command_args[1])
                value = bool(int(command_args[2]))
                success = self.client.write_coil(address, value, self.unit)
                
                return {
                    'success': success,
                    'output': f'Coil {address} set to {"ON" if value else "OFF"}',
                    'command': ' '.join(command_args),
                    'error': None if success else 'Failed to write coil',
                    'data': {
                        'address': address,
                        'value': value
                    }
                }
                
            elif command == 'rh':  # Read holding register
                address = int(command_args[1])
                count = int(command_args[2]) if len(command_args) > 2 else 1
                values = self.client.read_holding_registers(address, count, self.unit)
                
                if values is None:
                    return {
                        'success': False,
                        'output': '',
                        'command': ' '.join(command_args),
                        'error': 'Failed to read holding registers'
                    }
                
                return {
                    'success': True,
                    'output': str(values),
                    'command': ' '.join(command_args),
                    'error': None,
                    'data': {
                        'address': address,
                        'count': count,
                        'values': values
                    }
                }
                
            elif command == 'wh':  # Write holding register
                address = int(command_args[1])
                value = int(command_args[2])
                success = self.client.write_register(address, value, self.unit)
                
                return {
                    'success': success,
                    'output': f'Register {address} set to {value}',
                    'command': ' '.join(command_args),
                    'error': None if success else 'Failed to write register',
                    'data': {
                        'address': address,
                        'value': value
                    }
                }
                
            elif command == 'ri':  # Read input register
                address = int(command_args[1])
                count = int(command_args[2]) if len(command_args) > 2 else 1
                values = self.client.read_input_registers(address, count, self.unit)
                
                if values is None:
                    return {
                        'success': False,
                        'output': '',
                        'command': ' '.join(command_args),
                        'error': 'Failed to read input registers'
                    }
                
                return {
                    'success': True,
                    'output': str(values),
                    'command': ' '.join(command_args),
                    'error': None,
                    'data': {
                        'address': address,
                        'count': count,
                        'values': values
                    }
                }
                
            elif command == 'rd':  # Read discrete input
                address = int(command_args[1])
                count = int(command_args[2]) if len(command_args) > 2 else 1
                values = self.client.read_discrete_inputs(address, count, self.unit)
                
                if values is None:
                    return {
                        'success': False,
                        'output': '',
                        'command': ' '.join(command_args),
                        'error': 'Failed to read discrete inputs'
                    }
                
                return {
                    'success': True,
                    'output': str(values),
                    'command': ' '.join(command_args),
                    'error': None,
                    'data': {
                        'address': address,
                        'count': count,
                        'values': values
                    }
                }
                
            else:
                return {
                    'success': False,
                    'output': '',
                    'command': ' '.join(command_args),
                    'error': f'Unknown command: {command}'
                }
                
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {
                'success': False,
                'output': '',
                'command': ' '.join(command_args),
                'error': str(e)
            }
    
    def read_coil(self, channel: int) -> Optional[bool]:
        """Read coil state and return boolean value"""
        values = self.client.read_coils(channel, 1, self.unit)
        
        if values is None or len(values) == 0:
            return None
            
        return values[0]
    
    def write_coil(self, channel: int, value: bool) -> bool:
        """Write coil state"""
        return self.client.write_coil(channel, value, self.unit)
        
    def read_register(self, register: int) -> Optional[int]:
        """Read holding register value"""
        values = self.client.read_holding_registers(register, 1, self.unit)
        
        if values is None or len(values) == 0:
            return None
            
        return values[0]
    
    def write_register(self, register: int, value: int) -> bool:
        """Write holding register value"""
        return self.client.write_register(register, value, self.unit)
    
    def read_input_register(self, address: int) -> Optional[int]:
        """Read input register value"""
        values = self.client.read_input_registers(address, 1, self.unit)
        
        if values is None or len(values) == 0:
            return None
            
        return values[0]
    
    def read_discrete_input(self, address: int) -> Optional[bool]:
        """Read discrete input value"""
        values = self.client.read_discrete_inputs(address, 1, self.unit)
        
        if values is None or len(values) == 0:
            return None
            
        return values[0]


# Global instance
modbus_client = ModbusClient()
