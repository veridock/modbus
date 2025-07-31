"""
Modbus client utilities for Hyper Dashboard
Centralized Modbus communication functions
"""

import subprocess
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ModbusClient:
    """Centralized Modbus client for command execution"""
    
    def __init__(self):
        self.timeout = 5
        
    def execute_command(self, command_args: list) -> Dict[str, Any]:
        """Execute mod.py command and return structured result"""
        try:
            # Use the virtual environment's python and set proper working directory
            import os
            venv_python = './venv/bin/python'
            mod_py_path = './mod.py'
            
            # If venv python doesn't exist, fall back to system python
            if not os.path.exists(venv_python):
                venv_python = 'python'
            
            cmd = [venv_python, mod_py_path] + command_args
            result = subprocess.run(
                cmd,
                capture_output=True, 
                text=True, 
                timeout=self.timeout,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )

            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout.strip(),
                    'command': ' '.join(command_args),
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'output': '',
                    'command': ' '.join(command_args),
                    'error': result.stderr.strip() or 'Command failed'
                }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'command': ' '.join(command_args),
                'error': 'Command timeout'
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
        result = self.execute_command(['rc', str(channel), '1'])
        
        if not result['success']:
            return None
            
        output = result['output']
        if '[True]' in output:
            return True
        elif '[False]' in output:
            return False
        return None
    
    def write_coil(self, channel: int, value: bool) -> bool:
        """Write coil state"""
        result = self.execute_command(['wc', str(channel), '1' if value else '0'])
        return result['success']
    
    def read_register(self, register: int) -> Optional[int]:
        """Read holding register value"""
        result = self.execute_command(['rh', str(register), '1'])
        
        if not result['success']:
            return None
            
        try:
            # Extract numeric value from output
            output = result['output']
            # Expected format: "Holding Registers [0-0]: [value]"
            if '[' in output and ']' in output:
                value_str = output.split('[')[-1].split(']')[0]
                return int(value_str)
        except (ValueError, IndexError):
            logger.error(f"Failed to parse register value: {result['output']}")
        
        return None
    
    def write_register(self, register: int, value: int) -> bool:
        """Write holding register value"""
        result = self.execute_command(['wh', str(register), str(value)])
        return result['success']


# Global instance
modbus_client = ModbusClient()
