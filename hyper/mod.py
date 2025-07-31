#!/usr/bin/env python
"""
Modbus RTU Client for USB-RS485 Communication on Fedora
Based on PyModbus library for serial communication

Requirements:
- pymodbus[serial] library
- python-dotenv library
- USB-RS485 adapter connected to configured port
- User added to dialout group for port access

Usage:
    python mod.py
"""

import logging
import sys
import time
import os
import glob
from typing import Optional, List, Union

try:
    from pymodbus.client.serial import ModbusSerialClient
    from pymodbus.exceptions import ModbusException, ConnectionException
    from pymodbus.constants import Endian
    from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
except ImportError:
    print("Error: pymodbus library not found!")
    print("Install with: pip3 install pymodbus[serial]")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("Error: python-dotenv library not found!")
    print("Install with: pip3 install python-dotenv")
    sys.exit(1)

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_serial_ports() -> List[str]:
    """
    Find all available serial ports (ACM and USB)
    
    Returns:
        List of available serial port paths
    """
    ports = []
    
    # Check for ACM ports (USB CDC devices)
    acm_ports = glob.glob('/dev/ttyACM*')
    ports.extend(sorted(acm_ports))
    
    # Check for USB serial ports
    usb_ports = glob.glob('/dev/ttyUSB*')
    ports.extend(sorted(usb_ports))
    
    logger.info(f"Found serial ports: {ports}")
    return ports


def test_modbus_port(port: str, baudrate: int = 9600, timeout: float = 0.5) -> bool:
    """
    Test if a serial port responds to Modbus communication
    
    Args:
        port: Serial port path
        baudrate: Communication speed
        timeout: Connection timeout
        
    Returns:
        True if port responds to Modbus, False otherwise
    """
    try:
        logger.info(f"Testing Modbus on {port} at {baudrate} baud")
        
        client = ModbusSerialClient(
            method='rtu',
            port=port,
            baudrate=baudrate,
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=timeout
        )
        
        if not client.connect():
            logger.debug(f"Failed to connect to {port}")
            return False
        
        # Try to read a small number of coils from common addresses
        # Most Modbus devices respond to these basic queries
        test_addresses = [0, 1]
        test_units = [1, 2, 3]  # Common slave IDs
        
        for unit in test_units:
            for addr in test_addresses:
                try:
                    # Try reading 1 coil - minimal request
                    result = client.read_coils(address=addr, count=1, unit=unit)
                    if not result.isError():
                        logger.info(f"Modbus device found on {port} (unit {unit}, address {addr})")
                        client.close()
                        return True
                    
                    # Try reading 1 holding register
                    result = client.read_holding_registers(address=addr, count=1, unit=unit)
                    if not result.isError():
                        logger.info(f"Modbus device found on {port} (unit {unit}, address {addr})")
                        client.close()
                        return True
                        
                except Exception as e:
                    logger.debug(f"Test failed on {port} unit {unit} addr {addr}: {e}")
                    continue
        
        client.close()
        logger.debug(f"No Modbus response on {port}")
        return False
        
    except Exception as e:
        logger.debug(f"Error testing {port}: {e}")
        return False


def auto_detect_modbus_port(baudrates: List[int] = None) -> Optional[str]:
    """
    Automatically detect which serial port has a working Modbus device
    
    Args:
        baudrates: List of baud rates to test (default: common rates)
        
    Returns:
        Path to working Modbus port or None if not found
    """
    if baudrates is None:
        baudrates = [9600, 19200, 38400, 115200]  # Common Modbus baud rates
    
    ports = find_serial_ports()
    if not ports:
        logger.warning("No serial ports found")
        return None
    
    print(f"Scanning {len(ports)} serial ports for Modbus devices...")
    
    for port in ports:
        print(f"Testing {port}...")
        
        for baudrate in baudrates:
            if test_modbus_port(port, baudrate):
                print(f"✓ Modbus device detected on {port} at {baudrate} baud")
                return port
        
        print(f"✗ No Modbus response on {port}")
    
    print("No Modbus devices found on any serial port")
    return None


class ModbusRTUClient:
    """
    Modbus RTU Client for USB-RS485 communication
    """
    
    def __init__(self, 
                 port: Optional[str] = None,
                 baudrate: Optional[int] = None,
                 parity: str = 'N',
                 stopbits: int = 1,
                 bytesize: int = 8,
                 timeout: Optional[float] = None):
        """
        Initialize Modbus RTU client
        
        Args:
            port: Serial port (default: from .env MODBUS_PORT or /dev/ttyUSB0)
            baudrate: Communication speed (default: from .env MODBUS_BAUDRATE or 9600)
            parity: Parity bit ('N', 'E', 'O') (default: 'N')
            stopbits: Stop bits (default: 1)
            bytesize: Data bits (default: 8)
            timeout: Communication timeout in seconds (default: from .env MODBUS_TIMEOUT or 1.0)
        """
        # Load configuration from .env file with fallbacks
        self.port = port or os.getenv('MODBUS_PORT', '/dev/ttyUSB0')
        self.baudrate = baudrate or int(os.getenv('MODBUS_BAUDRATE', '9600'))
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.timeout = timeout or float(os.getenv('MODBUS_TIMEOUT', '1.0'))
        self.client = None
        
        logger.info(f"Initializing Modbus RTU client on {self.port}")
        logger.info(f"Parameters: {self.baudrate} {self.parity} {self.bytesize} {self.stopbits}")
        logger.info(f"Configuration loaded from .env: port={self.port}, baudrate={self.baudrate}, timeout={self.timeout}")
    
    def connect(self) -> bool:
        """
        Connect to Modbus device
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = ModbusSerialClient(
                method='rtu',
                port=self.port,
                baudrate=self.baudrate,
                parity=self.parity,
                stopbits=self.stopbits,
                bytesize=self.bytesize,
                timeout=self.timeout
            )
            
            if self.client.connect():
                logger.info(f"Successfully connected to {self.port}")
                return True
            else:
                logger.error(f"Failed to connect to {self.port}")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Modbus device"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from Modbus device")
    
    def read_coils(self, address: int, count: int, unit: int = 1) -> Optional[List[bool]]:
        """
        Read coils (discrete outputs)
        
        Args:
            address: Starting address
            count: Number of coils to read
            unit: Slave unit ID (default: 1)
            
        Returns:
            List of boolean values or None if error
        """
        try:
            result = self.client.read_coils(address=address, count=count, unit=unit)
            if result.isError():
                logger.error(f"Error reading coils: {result}")
                return None
            
            logger.info(f"Read {count} coils from address {address}: {result.bits}")
            return result.bits
            
        except Exception as e:
            logger.error(f"Error reading coils: {e}")
            return None
    
    def read_discrete_inputs(self, address: int, count: int, unit: int = 1) -> Optional[List[bool]]:
        """
        Read discrete inputs
        
        Args:
            address: Starting address
            count: Number of inputs to read
            unit: Slave unit ID (default: 1)
            
        Returns:
            List of boolean values or None if error
        """
        try:
            result = self.client.read_discrete_inputs(address=address, count=count, unit=unit)
            if result.isError():
                logger.error(f"Error reading discrete inputs: {result}")
                return None
            
            logger.info(f"Read {count} discrete inputs from address {address}: {result.bits}")
            return result.bits
            
        except Exception as e:
            logger.error(f"Error reading discrete inputs: {e}")
            return None
    
    def read_holding_registers(self, address: int, count: int, unit: int = 1) -> Optional[List[int]]:
        """
        Read holding registers
        
        Args:
            address: Starting address
            count: Number of registers to read
            unit: Slave unit ID (default: 1)
            
        Returns:
            List of register values or None if error
        """
        try:
            result = self.client.read_holding_registers(address=address, count=count, unit=unit)
            if result.isError():
                logger.error(f"Error reading holding registers: {result}")
                return None
            
            logger.info(f"Read {count} holding registers from address {address}: {result.registers}")
            return result.registers
            
        except Exception as e:
            logger.error(f"Error reading holding registers: {e}")
            return None
    
    def read_input_registers(self, address: int, count: int, unit: int = 1) -> Optional[List[int]]:
        """
        Read input registers
        
        Args:
            address: Starting address
            count: Number of registers to read
            unit: Slave unit ID (default: 1)
            
        Returns:
            List of register values or None if error
        """
        try:
            result = self.client.read_input_registers(address=address, count=count, unit=unit)
            if result.isError():
                logger.error(f"Error reading input registers: {result}")
                return None
            
            logger.info(f"Read {count} input registers from address {address}: {result.registers}")
            return result.registers
            
        except Exception as e:
            logger.error(f"Error reading input registers: {e}")
            return None
    
    def write_coil(self, address: int, value: bool, unit: int = 1) -> bool:
        """
        Write single coil
        
        Args:
            address: Coil address
            value: Boolean value to write
            unit: Slave unit ID (default: 1)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.client.write_coil(address=address, value=value, unit=unit)
            if result.isError():
                logger.error(f"Error writing coil: {result}")
                return False
            
            logger.info(f"Written coil at address {address}: {value}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing coil: {e}")
            return False
    
    def write_register(self, address: int, value: int, unit: int = 1) -> bool:
        """
        Write single holding register
        
        Args:
            address: Register address
            value: Value to write
            unit: Slave unit ID (default: 1)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.client.write_register(address=address, value=value, unit=unit)
            if result.isError():
                logger.error(f"Error writing register: {result}")
                return False
            
            logger.info(f"Written register at address {address}: {value}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing register: {e}")
            return False
    
    def write_coils(self, address: int, values: List[bool], unit: int = 1) -> bool:
        """
        Write multiple coils
        
        Args:
            address: Starting address
            values: List of boolean values to write
            unit: Slave unit ID (default: 1)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.client.write_coils(address=address, values=values, unit=unit)
            if result.isError():
                logger.error(f"Error writing coils: {result}")
                return False
            
            logger.info(f"Written {len(values)} coils starting at address {address}: {values}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing coils: {e}")
            return False
    
    def write_registers(self, address: int, values: List[int], unit: int = 1) -> bool:
        """
        Write multiple holding registers
        
        Args:
            address: Starting address
            values: List of values to write
            unit: Slave unit ID (default: 1)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.client.write_registers(address=address, values=values, unit=unit)
            if result.isError():
                logger.error(f"Error writing registers: {result}")
                return False
            
            logger.info(f"Written {len(values)} registers starting at address {address}: {values}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing registers: {e}")
            return False


def demo_usage():
    """
    Demonstration of Modbus RTU client usage
    """
    print("=== Modbus RTU Client Demo ===")
    print("Configuration loaded from .env file")
    print("Make sure your USB-RS485 adapter is connected and you have proper permissions!")
    print("Add yourself to dialout group: sudo usermod -aG dialout $USER")
    print()
    
    # Try to auto-detect Modbus port if .env port doesn't work
    configured_port = os.getenv('MODBUS_PORT', '/dev/ttyUSB0')
    
    print(f"Trying configured port: {configured_port}")
    modbus = ModbusRTUClient(port=configured_port)
    
    if not modbus.connect():
        print(f"Failed to connect to configured port {configured_port}")
        print("Attempting auto-detection...")
        
        detected_port = auto_detect_modbus_port()
        if detected_port:
            print(f"Using auto-detected port: {detected_port}")
            modbus = ModbusRTUClient(port=detected_port)
            if not modbus.connect():
                print("Failed to connect to auto-detected port!")
                return
        else:
            print("No Modbus devices found!")
            print("Check:")
            print("1. USB-RS485 adapter is connected")
            print("2. Device appears as /dev/ttyACM* or /dev/ttyUSB* (ls -l /dev/tty*)")
            print("3. You have permissions (groups command should show 'dialout')")
            print("4. Device is powered and responding")
            return
    
    print(f"Using port: {modbus.port}")
    print(f"Using baud rate: {modbus.baudrate}")
    print(f"Using timeout: {modbus.timeout}")
    print()

    # Connect to device
    if not modbus.connect():
        print("Failed to connect to Modbus device!")
        print("Check:")
        print("1. USB-RS485 adapter is connected")
        print("2. Device appears as /dev/ttyUSB0 (ls -l /dev/ttyUSB*)")
        print("3. You have permissions (groups command should show 'dialout')")
        print("4. Correct baud rate and other parameters")
        return
    
    try:
        # Example 1: Read coils
        print("\n--- Reading 8 coils from address 0 ---")
        coils = modbus.read_coils(address=0, count=8, unit=1)
        if coils:
            print(f"Coils: {coils}")
        
        # Example 2: Read holding registers
        print("\n--- Reading 4 holding registers from address 0 ---")
        registers = modbus.read_holding_registers(address=0, count=4, unit=1)
        if registers:
            print(f"Registers: {registers}")
        
        # Example 3: Write single coil
        print("\n--- Writing coil at address 0 ---")
        success = modbus.write_coil(address=0, value=True, unit=1)
        if success:
            print("Coil written successfully")
        
        # Example 4: Write single register
        print("\n--- Writing register at address 0 ---")
        success = modbus.write_register(address=0, value=1234, unit=1)
        if success:
            print("Register written successfully")
        
        # Example 5: Read input registers
        print("\n--- Reading 2 input registers from address 0 ---")
        inputs = modbus.read_input_registers(address=0, count=2, unit=1)
        if inputs:
            print(f"Input registers: {inputs}")
        
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
    except Exception as e:
        print(f"Error during operation: {e}")
    finally:
        # Always disconnect
        modbus.disconnect()


def interactive_mode():
    """
    Interactive mode for testing Modbus communication
    """
    print("=== Interactive Modbus RTU Client ===")
    print("Default configuration loaded from .env file")
    
    # Get connection parameters with .env defaults
    default_port = os.getenv('MODBUS_PORT', '/dev/ttyUSB0')
    default_baudrate = os.getenv('MODBUS_BAUDRATE', '9600')
    default_timeout = os.getenv('MODBUS_TIMEOUT', '1.0')
    
    # Ask user if they want auto-detection
    auto_detect = input("Auto-detect Modbus port? (y/N): ").strip().lower()
    
    if auto_detect in ['y', 'yes']:
        print("\nScanning for Modbus devices...")
        detected_port = auto_detect_modbus_port()
        if detected_port:
            port = detected_port
            baudrate = int(default_baudrate)  # Use default baudrate for now
        else:
            print("No devices found. Please enter manually:")
            port = input(f"Enter serial port [{default_port}]: ").strip() or default_port
            baudrate = int(input(f"Enter baud rate [{default_baudrate}]: ").strip() or default_baudrate)
    else:
        port = input(f"Enter serial port [{default_port}]: ").strip() or default_port
        baudrate = int(input(f"Enter baud rate [{default_baudrate}]: ").strip() or default_baudrate)
    
    parity = input("Enter parity (N/E/O) [N]: ").strip().upper() or 'N'
    
    modbus = ModbusRTUClient(port=port, baudrate=baudrate, parity=parity)

    if not modbus.connect():
        print("Failed to connect to Modbus device!")
        print("Check:")
        print("1. USB-RS485 adapter is connected")
        print("2. Device appears as configured port (ls -l /dev/ttyACM* /dev/ttyUSB*)")
        print("3. You have permissions (groups command should show 'dialout')")
        print("4. Correct baud rate and other parameters")
        print("5. Device is powered and responding")
        return

    print("\nConnected! Available commands:")
    print("  rc <addr> <count> [unit] - Read coils")
    print("  rh <addr> <count> [unit] - Read holding registers")
    print("  ri <addr> <count> [unit] - Read input registers")
    print("  rd <addr> <count> [unit] - Read discrete inputs")
    print("  wc <addr> <value> [unit] - Write coil (0/1)")
    print("  wr <addr> <value> [unit] - Write register")
    print("  quit - Exit")
    
    try:
        while True:
            cmd = input("\nModbus> ").strip().split()
            if not cmd:
                continue
            
            if cmd[0] == 'quit':
                break
            
            try:
                if cmd[0] == 'rc' and len(cmd) >= 3:
                    addr, count = int(cmd[1]), int(cmd[2])
                    unit = int(cmd[3]) if len(cmd) > 3 else 1
                    result = modbus.read_coils(addr, count, unit)
                    print(f"Coils: {result}")
                
                elif cmd[0] == 'rh' and len(cmd) >= 3:
                    addr, count = int(cmd[1]), int(cmd[2])
                    unit = int(cmd[3]) if len(cmd) > 3 else 1
                    result = modbus.read_holding_registers(addr, count, unit)
                    print(f"Holding registers: {result}")
                
                elif cmd[0] == 'ri' and len(cmd) >= 3:
                    addr, count = int(cmd[1]), int(cmd[2])
                    unit = int(cmd[3]) if len(cmd) > 3 else 1
                    result = modbus.read_input_registers(addr, count, unit)
                    print(f"Input registers: {result}")
                
                elif cmd[0] == 'rd' and len(cmd) >= 3:
                    addr, count = int(cmd[1]), int(cmd[2])
                    unit = int(cmd[3]) if len(cmd) > 3 else 1
                    result = modbus.read_discrete_inputs(addr, count, unit)
                    print(f"Discrete inputs: {result}")
                
                elif cmd[0] == 'wc' and len(cmd) >= 3:
                    addr, value = int(cmd[1]), bool(int(cmd[2]))
                    unit = int(cmd[3]) if len(cmd) > 3 else 1
                    result = modbus.write_coil(addr, value, unit)
                    print(f"Write coil result: {result}")
                
                elif cmd[0] == 'wr' and len(cmd) >= 3:
                    addr, value = int(cmd[1]), int(cmd[2])
                    unit = int(cmd[3]) if len(cmd) > 3 else 1
                    result = modbus.write_register(addr, value, unit)
                    print(f"Write register result: {result}")
                
                else:
                    print("Invalid command or missing parameters")
                    
            except ValueError as e:
                print(f"Invalid parameter: {e}")
            except Exception as e:
                print(f"Error: {e}")
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        modbus.disconnect()


def command_line_mode(args):
    """
    Command-line mode for direct Modbus operations
    
    Args:
        args: Command line arguments (e.g. ['wc', '0', '1'])
    """
    if len(args) < 2:
        print("Error: Not enough arguments")
        print_command_help()
        return False
    
    cmd = args[0].lower()
    
    # Auto-detect or use configured port
    configured_port = os.getenv('MODBUS_PORT', '/dev/ttyUSB0')
    modbus = ModbusRTUClient(port=configured_port)
    
    if not modbus.connect():
        print(f"Failed to connect to configured port {configured_port}")
        print("Attempting auto-detection...")
        
        detected_port = auto_detect_modbus_port()
        if detected_port:
            modbus = ModbusRTUClient(port=detected_port)
            if not modbus.connect():
                print("Failed to connect to auto-detected port!")
                return False
        else:
            print("No Modbus devices found!")
            return False
    
    try:
        # Parse command and execute
        if cmd == 'rc' and len(args) >= 3:
            addr, count = int(args[1]), int(args[2])
            unit = int(args[3]) if len(args) > 3 else 1
            result = modbus.read_coils(addr, count, unit)
            if result is not None:
                print(f"Coils [{addr}-{addr+count-1}]: {result}")
                return True
            else:
                print("Failed to read coils")
                return False
        
        elif cmd == 'rh' and len(args) >= 3:
            addr, count = int(args[1]), int(args[2])
            unit = int(args[3]) if len(args) > 3 else 1
            result = modbus.read_holding_registers(addr, count, unit)
            if result is not None:
                print(f"Holding registers [{addr}-{addr+count-1}]: {result}")
                return True
            else:
                print("Failed to read holding registers")
                return False
        
        elif cmd == 'ri' and len(args) >= 3:
            addr, count = int(args[1]), int(args[2])
            unit = int(args[3]) if len(args) > 3 else 1
            result = modbus.read_input_registers(addr, count, unit)
            if result is not None:
                print(f"Input registers [{addr}-{addr+count-1}]: {result}")
                return True
            else:
                print("Failed to read input registers")
                return False
        
        elif cmd == 'rd' and len(args) >= 3:
            addr, count = int(args[1]), int(args[2])
            unit = int(args[3]) if len(args) > 3 else 1
            result = modbus.read_discrete_inputs(addr, count, unit)
            if result is not None:
                print(f"Discrete inputs [{addr}-{addr+count-1}]: {result}")
                return True
            else:
                print("Failed to read discrete inputs")
                return False
        
        elif cmd == 'wc' and len(args) >= 3:
            addr, value = int(args[1]), bool(int(args[2]))
            unit = int(args[3]) if len(args) > 3 else 1
            result = modbus.write_coil(addr, value, unit)
            if result:
                print(f"Coil {addr} set to {'ON' if value else 'OFF'}")
                return True
            else:
                print(f"Failed to write coil {addr}")
                return False
        
        elif cmd == 'wr' and len(args) >= 3:
            addr, value = int(args[1]), int(args[2])
            unit = int(args[3]) if len(args) > 3 else 1
            result = modbus.write_register(addr, value, unit)
            if result:
                print(f"Register {addr} set to {value}")
                return True
            else:
                print(f"Failed to write register {addr}")
                return False
        
        else:
            print(f"Unknown command or invalid arguments: {' '.join(args)}")
            print_command_help()
            return False
    
    except ValueError as e:
        print(f"Invalid parameter: {e}")
        print_command_help()
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        modbus.disconnect()


def print_command_help():
    """Print help for command-line usage"""
    print("\nUsage: python mod.py <command> <args>")
    print("\nAvailable commands:")
    print("  rc <addr> <count> [unit] - Read coils")
    print("  rh <addr> <count> [unit] - Read holding registers")
    print("  ri <addr> <count> [unit] - Read input registers")
    print("  rd <addr> <count> [unit] - Read discrete inputs")
    print("  wc <addr> <value> [unit] - Write coil (0/1)")
    print("  wr <addr> <value> [unit] - Write register")
    print("\nExamples:")
    print("  python mod.py wc 0 1     # Turn ON output 0")
    print("  python mod.py wc 0 0     # Turn OFF output 0")
    print("  python mod.py rc 0 8     # Read 8 coils from address 0")
    print("  python mod.py rh 0 4     # Read 4 holding registers")
    print("  python mod.py wr 1 500   # Write 500 to register 1")
    print("\nOther modes:")
    print("  python mod.py            # Demo mode")
    print("  python mod.py --interactive  # Interactive mode")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--interactive':
            interactive_mode()
        elif sys.argv[1] in ['--help', '-h']:
            print_command_help()
        else:
            # Command-line mode with parameters
            success = command_line_mode(sys.argv[1:])
            sys.exit(0 if success else 1)
    else:
        demo_usage()
