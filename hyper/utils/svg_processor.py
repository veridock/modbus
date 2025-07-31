"""
SVG Template Processor with Embedded Python Support
Processes SVG templates with <?py ... ?> blocks for dynamic configuration
"""

import re
import os
import json
import requests
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class SVGProcessor:
    """Process SVG templates with embedded Python blocks"""
    
    def __init__(self, template_dir="templates"):
        self.template_dir = template_dir
        self.globals_context = {
            'requests': requests,
            'os': os,
            'json': json,
            'datetime': datetime,
            # Add common utilities
            'MODBUS_API': os.getenv("MODBUS_API", "http://localhost:5002"),
            'API_BASE_URL': os.getenv("API_BASE_URL", "http://localhost:5002"),
            'REFRESH': os.getenv("AUTO_REFRESH_INTERVAL", "3000"),
            'CONNECTION': "active",
            'error_msg': "",
            'now': datetime.now().strftime("%H:%M:%S")
        }
    
    def process_svg(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """
        Process SVG template with embedded Python blocks and context variables
        
        Args:
            template_name: Name of the SVG template file
            context: Additional context variables for template rendering
            
        Returns:
            Processed SVG content as string
        """
        if context is None:
            context = {}
        
        # Read template file
        template_path = os.path.join(self.template_dir, template_name)
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        except FileNotFoundError:
            return f"<!-- SVG Template '{template_name}' not found -->"
        
        # Merge context with globals
        execution_context = {**self.globals_context, **context}
        
        # Process embedded Python blocks
        processed_content = self._process_python_blocks(template_content, execution_context)
        
        # Process template variables ({{ variable }})
        processed_content = self._process_template_variables(processed_content, execution_context)
        
        return processed_content
    
    def _process_python_blocks(self, content: str, context: Dict[str, Any]) -> str:
        """Process <?py ... ?> blocks in the template"""
        
        def execute_python_block(match):
            python_code = match.group(1).strip()
            
            try:
                # Create a local context for execution
                local_context = context.copy()
                
                # Execute the Python code
                exec(python_code, {"__builtins__": __builtins__}, local_context)
                
                # Update the main context with any new variables
                context.update(local_context)
                
                # Return empty string (the code block is replaced with nothing)
                return ""
                
            except Exception as e:
                # Return error comment in case of execution failure
                return f"<!-- Python execution error: {str(e)} -->"
        
        # Find and process all <?py ... ?> blocks
        pattern = r'<\?py\s*(.*?)\s*\?>'
        processed_content = re.sub(pattern, execute_python_block, content, flags=re.DOTALL)
        
        return processed_content
    
    def _process_template_variables(self, content: str, context: Dict[str, Any]) -> str:
        """Process {{ variable }} placeholders in the template with Jinja filter support"""
        
        def replace_variable(match):
            expression = match.group(1).strip()
            
            try:
                # Handle Jinja-style conditional expressions (e.g., 'value' if condition else 'other')
                if ' if ' in expression and ' else ' in expression:
                    # Parse conditional expression: value_if_true if condition else value_if_false
                    parts = expression.split(' if ', 1)
                    if len(parts) == 2:
                        value_if_true = parts[0].strip().strip("'\"")
                        condition_and_else = parts[1].split(' else ', 1)
                        if len(condition_and_else) == 2:
                            condition_expr = condition_and_else[0].strip()
                            value_if_false = condition_and_else[1].strip().strip("'\"")
                            
                            # Evaluate the condition
                            if condition_expr in context:
                                condition_value = bool(context[condition_expr])
                            else:
                                # Try to evaluate as a simple expression
                                condition_value = bool(eval(condition_expr, {"__builtins__": {}}, context))
                            
                            return value_if_true if condition_value else value_if_false
                
                # Handle Jinja filters (e.g., variable|filter)
                elif '|' in expression:
                    var_part, filter_part = expression.split('|', 1)
                    var_name = var_part.strip()
                    filter_name = filter_part.strip()
                    
                    # Get the variable value
                    if '.' in var_name:
                        parts = var_name.split('.')
                        value = context
                        for part in parts:
                            value = value.get(part, '') if isinstance(value, dict) else getattr(value, part, '')
                    else:
                        value = context.get(var_name, '')
                    
                    # Apply the filter
                    if filter_name == 'lower':
                        value = str(value).lower()
                    elif filter_name == 'upper':
                        value = str(value).upper()
                    elif filter_name == 'title':
                        value = str(value).title()
                    else:
                        # Unknown filter, return as-is
                        value = str(value)
                        
                else:
                    # No filter, just get the variable
                    var_name = expression
                    if '.' in var_name:
                        parts = var_name.split('.')
                        value = context
                        for part in parts:
                            value = value.get(part, '') if isinstance(value, dict) else getattr(value, part, '')
                    else:
                        value = context.get(var_name, '{{ ' + var_name + ' }}')  # Keep original if not found
                
                return str(value)
                
            except Exception as e:
                return f"<!-- Variable error: {str(e)} -->"
        
        # Find and replace all {{ variable }} placeholders
        pattern = r'\{\{\s*([^}]+)\s*\}\}'
        processed_content = re.sub(pattern, replace_variable, content)
        
        return processed_content
    
    def get_config_json(self, context: Dict[str, Any] = None) -> str:
        """Generate configuration JSON for embedding in SVG"""
        if context is None:
            context = {}
        
        merged_context = {**self.globals_context, **context}
        
        config = {
            "api": {
                "baseUrl": merged_context.get("MODBUS_API", "http://localhost:5002"),
                "status": merged_context.get("CONNECTION", "unknown")
            },
            "ui": {
                "refreshInterval": merged_context.get("REFRESH", "3000"),
                "lastUpdated": merged_context.get("now", "unknown"),
                "error": merged_context.get("error_msg", "")
            },
            "version": "1.0.0",
            "lastUpdated": merged_context.get("now", "unknown")
        }
        
        return json.dumps(config, indent=2)


# Global processor instance
svg_processor = SVGProcessor()
