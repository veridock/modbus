"""
Widget rendering utilities for Hyper Dashboard
Centralized widget generation and styling
"""

from typing import Dict, Any, Optional
from utils.modbus_client import modbus_client


class WidgetRenderer:
    """Centralized widget rendering with consistent styling"""
    
    def __init__(self):
        self.base_styles = """
        <style>
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                margin: 0; 
                padding: 10px; 
                background: #1e1e1e; 
                color: #fff; 
            }
            .widget { 
                background: #2d2d2d; 
                border-radius: 8px; 
                padding: 15px; 
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            .button { 
                background: #007acc; 
                color: white; 
                border: none; 
                padding: 10px 20px; 
                border-radius: 5px; 
                cursor: pointer; 
                font-size: 14px;
                margin: 5px;
            }
            .button:hover { background: #005fa3; }
            .button.active { background: #28a745; }
            .button.inactive { background: #6c757d; }
            .input-widget { 
                background: #2d2d2d; 
                border-radius: 8px; 
                padding: 15px; 
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                cursor: pointer;
                transition: all 0.3s;
            }
            .input-widget:hover { transform: scale(1.05); }
            .output-active { 
                background: #28a745 !important; 
                color: white !important;
            }
            .output-inactive { 
                background: #6c757d !important; 
                color: #ccc !important;
            }
            .status-good { color: #28a745; }
            .status-error { color: #dc3545; }
            .status-warning { color: #ffc107; }
        </style>
        """
    
    def render_switch_widget(self, channel: int) -> str:
        """Render iOS-style toggle switch widget"""
        state = modbus_client.read_coil(channel)
        state_class = "active" if state else "inactive"
        state_text = "ON" if state else "OFF"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Switch {channel}</title>
            {self.base_styles}
            <style>
                .switch {{
                    position: relative;
                    display: inline-block;
                    width: 60px;
                    height: 34px;
                    margin: 10px;
                }}
                .switch input {{ opacity: 0; width: 0; height: 0; }}
                .slider {{
                    position: absolute;
                    cursor: pointer;
                    top: 0; left: 0; right: 0; bottom: 0;
                    background-color: #ccc;
                    transition: .4s;
                    border-radius: 34px;
                }}
                .slider:before {{
                    position: absolute;
                    content: "";
                    height: 26px; width: 26px;
                    left: 4px; bottom: 4px;
                    background-color: white;
                    transition: .4s;
                    border-radius: 50%;
                }}
                input:checked + .slider {{ background-color: #2196F3; }}
                input:checked + .slider:before {{ transform: translateX(26px); }}
            </style>
        </head>
        <body>
            <div class="widget">
                <h3>Output {channel}</h3>
                <form method="post" action="/toggle/{channel}">
                    <label class="switch">
                        <input type="checkbox" {"checked" if state else ""}>
                        <span class="slider" onclick="this.parentElement.parentElement.submit()"></span>
                    </label>
                </form>
                <p>Status: <span class="{state_class}">{state_text}</span></p>
                <script>
                    // Auto-refresh every 2 seconds
                    setTimeout(() => window.location.reload(), 2000);
                </script>
            </div>
        </body>
        </html>
        """
    
    def render_button_widget(self, channel: int) -> str:
        """Render simple button widget"""
        state = modbus_client.read_coil(channel)
        button_class = "active" if state else "inactive"
        button_text = f"Turn {'OFF' if state else 'ON'}"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Button {channel}</title>
            {self.base_styles}
        </head>
        <body>
            <div class="widget">
                <h3>Control {channel}</h3>
                <form method="post" action="/toggle/{channel}">
                    <button type="submit" class="button {button_class}">
                        {button_text}
                    </button>
                </form>
                <p>Current: <strong>{"ON" if state else "OFF"}</strong></p>
                <script>
                    setTimeout(() => window.location.reload(), 2000);
                </script>
            </div>
        </body>
        </html>
        """
    
    def render_led_widget(self, channel: int) -> str:
        """Render LED indicator widget"""
        state = modbus_client.read_coil(channel)
        led_color = "#28a745" if state else "#6c757d"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>LED {channel}</title>
            {self.base_styles}
            <style>
                .led {{
                    width: 30px;
                    height: 30px;
                    border-radius: 50%;
                    display: inline-block;
                    margin: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.5);
                }}
            </style>
        </head>
        <body>
            <div class="widget">
                <h3>Input {channel}</h3>
                <div class="led" style="background-color: {led_color};"></div>
                <p>Status: <strong>{"ACTIVE" if state else "INACTIVE"}</strong></p>
                <script>
                    setTimeout(() => window.location.reload(), 1000);
                </script>
            </div>
        </body>
        </html>
        """
    
    def render_gauge_widget(self, register: int) -> str:
        """Render gauge widget for analog values"""
        value = modbus_client.read_register(register) or 0
        percentage = min(100, max(0, (value / 1000) * 100))  # Assuming 0-1000 range
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gauge {register}</title>
            {self.base_styles}
        </head>
        <body>
            <div class="widget">
                <h3>Register {register}</h3>
                <svg width="120" height="120" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="50" fill="none" stroke="#333" stroke-width="8"/>
                    <circle cx="60" cy="60" r="50" fill="none" stroke="#007acc" stroke-width="8"
                            stroke-dasharray="{percentage * 3.14}" stroke-dashoffset="0"
                            style="transform: rotate(-90deg); transform-origin: 60px 60px;"/>
                </svg>
                <p><strong>{value}</strong></p>
                <p>{percentage:.1f}%</p>
                <script>
                    setTimeout(() => window.location.reload(), 1500);
                </script>
            </div>
        </body>
        </html>
        """
    
    def render_register_widget(self, register: int) -> str:
        """Render register read/write widget"""
        current_value = modbus_client.read_register(register) or 0
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Register {register}</title>
            {self.base_styles}
        </head>
        <body>
            <div class="widget">
                <h3>Register {register}</h3>
                <p>Current Value: <strong>{current_value}</strong></p>
                <form method="post" action="/write_register/{register}">
                    <input type="number" name="value" value="{current_value}" 
                           style="padding: 5px; margin: 5px; border-radius: 3px; border: 1px solid #555; background: #333; color: #fff;">
                    <button type="submit" class="button">Write</button>
                </form>
                <script>
                    setTimeout(() => window.location.reload(), 3000);
                </script>
            </div>
        </body>
        </html>
        """
    
    def render_status_widget(self) -> str:
        """Render system status widget"""
        try:
            # Get system information
            result = modbus_client.execute_command(['help'])
            status = "Connected" if result['success'] else "Error"
            status_class = "status-good" if result['success'] else "status-error"
        except:
            status = "Disconnected"
            status_class = "status-error"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>System Status</title>
            {self.base_styles}
        </head>
        <body>
            <div class="widget">
                <h3>System Status</h3>
                <p class="{status_class}"><strong>{status}</strong></p>
                <small>Auto-refresh: 2s</small>
                <script>
                    setTimeout(() => window.location.reload(), 2000);
                </script>
            </div>
        </body>
        </html>
        """


    def render_input_widget(self, channel: int) -> str:
        """Render clickable digital output widget (input in URL but controls outputs)"""
        state = modbus_client.read_coil(channel)
        widget_class = "output-active" if state else "output-inactive"
        status_text = "ON" if state else "OFF"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DO{channel}</title>
            {self.base_styles}
        </head>
        <body>
            <div class="input-widget {widget_class}" onclick="toggleOutput()">
                <h3>DO{channel}</h3>
                <div style="font-size: 18px; font-weight: bold;">{status_text}</div>
                <small>Click to toggle</small>
            </div>
            
            <script>
                function toggleOutput() {{
                    fetch('/toggle/{channel}', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}}
                    }}).then(() => {{
                        setTimeout(() => window.location.reload(), 500);
                    }});
                }}
                
                // Auto-refresh every 3 seconds
                setTimeout(() => window.location.reload(), 3000);
            </script>
        </body>
        </html>
        """


# Global instance
widget_renderer = WidgetRenderer()
