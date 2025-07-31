#!/usr/bin/env python3
"""
Standalone output module for Modbus RTU IO 8CH Control System.

This script provides a standalone endpoint for the output module that can be called by name
with GET parameters. It renders an SVG button that shows the current state of a digital output
and allows toggling it.

Usage:
    ./output_module.py <channel> [--port PORT] [--host HOST]
    
    or as a module:
    from output_module import app
    app.run(port=5001, host='0.0.0.0')
"""

import os
import sys
import subprocess
import argparse
from flask import Flask, Response
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
MODBUS_UNIT = int(os.getenv('MODBUS_DEVICE_ADDRESS', '1'))

def execute_mod_command(command_args):
    """Execute mod.py command and return result"""
    try:
        cmd = ['python', 'mod.py'] + command_args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        print(result)
        if result.returncode == 0:
            return {
                'success': True,
                'output': result.stdout.strip(),
                'command': ' '.join(command_args)
            }
        else:
            return {
                'success': False,
                'error': result.stderr.strip() or 'Command failed',
                'command': ' '.join(command_args)
            }
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Command timeout'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def parse_coil_output(output, channel):
    """Parse coil read output to get boolean state for a specific channel
    
    Args:
        output: Raw output from mod.py (e.g., 'Coils [0-7]: [False, False, False, False, False, False, False, False]')
        channel: The channel number (0-7) to get the state for
    
    Returns:
        bool: The state of the specified channel, or None if parsing fails
    """
    try:
        # Extract the list of coil states from the output
        start = output.find('[') + 1
        end = output.rfind(']')
        if start > 0 and end > start:
            # Get the list of states as a string, remove whitespace, and split by commas
            states_str = output[start:end].strip()
            # Handle both '[True, False]' and 'True, False' formats
            if states_str.startswith('[') and states_str.endswith(']'):
                states_str = states_str[1:-1]
            states = [s.strip().lower() == 'true' for s in states_str.split(',')]
            
            # Return the state of the requested channel if it exists
            if 0 <= channel < len(states):
                return states[channel]
    except (ValueError, IndexError, AttributeError) as e:
        print(f"Error parsing coil output: {e}")
    
    return None

def generate_svg(channel, state):
    """Generate SVG content for the output module"""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <defs>
        <style>
            .button {{ 
                cursor: pointer; 
                transition: all 0.3s;
            }}
            .button:hover {{ 
                transform: scale(1.05); 
            }}
            .button:active {{ 
                transform: scale(0.95); 
            }}
            .on {{ fill: #4CAF50; }}
            .off {{ fill: #f44336; }}
            .text {{ 
                fill: white; 
                font-family: Arial; 
                font-size: 24px; 
                font-weight: bold; 
                text-anchor: middle; 
                pointer-events: none;
            }}
            .label {{
                fill: #666;
                font-family: Arial;
                font-size: 12px;
                text-anchor: middle;
            }}
        </style>
        <script>
            function toggle() {{
                // Submit form to toggle
                window.location.href = '/action/toggle/{channel}';
            }}
        </script>
    </defs>

    <rect x="10" y="10" width="80" height="60" rx="10" 
          class="button {'on' if state else 'off'}" 
          onclick="toggle()"/>

    <text x="50" y="45" class="text">DO{channel}</text>
    <text x="50" y="85" class="label">{'ON' if state else 'OFF'}</text>
</svg>'''

@app.route('/module/output/<int:channel>')
def output_module(channel):
    """Endpoint for the output module SVG"""
    # Read all coil states (8 coils at once for efficiency)
    result = execute_mod_command(['rc', '0', '8', str(MODBUS_UNIT)])
    state = False
    
    if result['success']:
        # Parse the output to get the state of the specific channel
        state = parse_coil_output(result['output'], channel)
        if state is None:
            print(f"Warning: Could not parse state for channel {channel} from output: {result['output']}")
    else:
        print(f"Error reading coil states: {result.get('error', 'Unknown error')}")
    
    # Generate and return SVG
    svg = generate_svg(channel, state)
    return Response(svg, mimetype='image/svg+xml')

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Output Module for Modbus RTU IO 8CH Control System')
    parser.add_argument('channel', type=int, nargs='?', default=1,
                       help='Channel number (1-8)')
    parser.add_argument('--port', type=int, default=5001,
                       help='Port to run the server on (default: 5001)')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                       help='Host to bind to (default: 0.0.0.0)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    print(f"Starting output module for channel {args.channel} on http://{args.host}:{args.port}")
    app.run(port=args.port, host=args.host, debug=True)
