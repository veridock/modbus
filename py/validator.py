"""
Validator module for sanitizing and validating data before rendering.
"""
import re
import json
from xml.sax.saxutils import escape

def sanitize_for_xml(text):
    """
    Sanitize text to be safe for XML embedding.
    Escapes special characters and removes control characters.
    """
    if not text:
        return ""
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', str(text))
    
    # Escape XML special characters
    return escape(text)

def sanitize_error_message(error_msg):
    """
    Sanitize error messages for safe embedding in JSON/XML.
    """
    if not error_msg:
        return ""
    
    # Convert to string if not already
    error_str = str(error_msg)
    
    # Remove any control characters and escape special characters
    error_str = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', error_str)
    
    # Truncate to reasonable length
    return error_str[:500]

def validate_json_metadata(metadata):
    """
    Validate and sanitize metadata dictionary for JSON output.
    Ensures all values are JSON-serializable and safe.
    """
    if not isinstance(metadata, dict):
        return {}
    
    safe_metadata = {}
    
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool, type(None))):
            # Basic types are safe
            safe_value = value
        elif isinstance(value, dict):
            # Recursively validate nested dictionaries
            safe_value = validate_json_metadata(value)
        elif hasattr(value, '__dict__'):
            # Convert objects to dict if they have __dict__
            safe_value = validate_json_metadata(value.__dict__)
        elif hasattr(value, '__str__'):
            # Convert to string and sanitize
            safe_value = str(value)
        else:
            # Skip anything we can't handle
            continue
            
        safe_metadata[str(key)] = safe_value
    
    return safe_metadata

def escape_json_string(s):
    """Escape a string to be safely embedded in JSON."""
    if s is None:
        return ''
    return json.dumps(str(s))[1:-1]  # Remove the surrounding quotes

def validate_and_clean_content(content, content_type='text/html'):
    """
    Validate and clean content based on its type.
    
    Args:
        content: The content to validate/clean
        content_type: The MIME type of the content ('text/html', 'application/json', 'image/svg+xml')
        
    Returns:
        Tuple of (is_valid, cleaned_content, error_message)
    """
    if not content:
        return True, content, ""
        
    try:
        if content_type == 'application/json':
            # Parse and re-serialize JSON to ensure it's valid
            parsed = json.loads(content)
            return True, json.dumps(parsed, ensure_ascii=False), ""
            
        elif content_type == 'image/svg+xml':
            # Basic XML validation for SVG
            from xml.etree import ElementTree
            from io import StringIO
            
            # Try to parse the XML
            try:
                ElementTree.parse(StringIO(content))
                return True, content, ""
            except Exception as e:
                # If parsing fails, try to fix common issues
                fixed_content = re.sub(
                    r'&(?!amp;|lt;|gt;|apos;|quot;|#\d+;|#x[0-9a-fA-F]+;)', 
                    '&amp;', 
                    content
                )
                try:
                    ElementTree.parse(StringIO(fixed_content))
                    return True, fixed_content, "Fixed invalid XML entities"
                except Exception as e2:
                    return False, content, f"Invalid SVG/XML: {str(e2)[:200]}"
        
        # For HTML/other text content
        return True, content, ""
        
    except Exception as e:
        return False, content, f"Validation error: {str(e)[:200]}"
