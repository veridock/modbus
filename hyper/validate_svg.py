#!/usr/bin/env python3
"""
Script to validate SVG files using the validator module.
"""
import sys
from validator import validate_and_clean_content

def validate_svg_file(file_path):
    """
    Validate an SVG file using the validator module.
    
    Args:
        file_path (str): Path to the SVG file to validate
        
    Returns:
        tuple: (is_valid, message, cleaned_content)
    """
    try:
        # Read the SVG file
        with open(file_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        # Validate the SVG content
        is_valid, cleaned_content, error_message = validate_and_clean_content(
            svg_content, 
            content_type='image/svg+xml'
        )
        
        if is_valid:
            if cleaned_content != svg_content:
                return True, "SVG is valid but was modified during cleaning.\n" + \
                       "This usually means some content was sanitized for safety.", cleaned_content
            return True, "SVG is valid.", cleaned_content
        else:
            return False, f"SVG validation failed: {error_message}", cleaned_content
            
    except Exception as e:
        return False, f"Error validating SVG: {str(e)}", ""

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path_to_svg_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    is_valid, message, _ = validate_svg_file(file_path)
    
    if is_valid:
        print(f"✅ {message}")
        sys.exit(0)
    else:
        print(f"❌ {message}")
        sys.exit(1)
