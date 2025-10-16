#!/usr/bin/env python3
"""
Test script to verify that the updated templates can be loaded correctly
"""

import os
import sys
from jinja2 import Environment, FileSystemLoader

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_template_loading():
    """Test that all required templates can be loaded"""
    # Set up Jinja2 environment
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # List of required templates
    required_templates = [
        'first_page.html',
        'deviation_statement.html',
        'extra_items.html',
        'certificate_ii.html',
        'certificate_iii.html',
        'note_sheet.html'
    ]
    
    print(f"Testing template loading from: {template_dir}")
    
    # Try to load each template
    for template_name in required_templates:
        try:
            template = env.get_template(template_name)
            print(f"✅ {template_name} - Loaded successfully")
        except Exception as e:
            print(f"❌ {template_name} - Failed to load: {e}")
            return False
    
    print("\n✅ All templates loaded successfully!")
    return True

if __name__ == "__main__":
    test_template_loading()