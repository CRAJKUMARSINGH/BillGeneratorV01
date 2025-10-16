#!/usr/bin/env python3
"""
Test script to verify Jinja2 template loading
"""

import os
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

def test_jinja_template_loading():
    """Test Jinja2 template loading"""
    # Get the template directory
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    print(f"Template directory: {template_dir}")
    print(f"Template directory exists: {os.path.exists(template_dir)}")
    
    if not os.path.exists(template_dir):
        print("ERROR: Template directory does not exist!")
        return False
    
    # List files in template directory
    files = os.listdir(template_dir)
    html_files = [f for f in files if f.endswith('.html')]
    print(f"HTML template files found: {len(html_files)}")
    for file in html_files[:10]:  # Show first 10 files
        print(f"  - {file}")
    
    # Create Jinja2 environment
    print(f"\nCreating Jinja2 environment with template directory...")
    try:
        jinja_env = Environment(loader=FileSystemLoader(template_dir))
        print("✅ Jinja2 environment created successfully")
    except Exception as e:
        print(f"❌ Failed to create Jinja2 environment: {e}")
        return False
    
    # Try to load a template
    template_names = ['first_page.html', 'deviation_statement.html', 'certificate_ii.html']
    for template_name in template_names:
        print(f"\nTrying to load template: {template_name}")
        try:
            template = jinja_env.get_template(template_name)
            print(f"✅ Template '{template_name}' loaded successfully")
            print(f"   Template path: {template.filename}")
        except Exception as e:
            print(f"❌ Failed to load template '{template_name}': {e}")
    
    return True

if __name__ == "__main__":
    test_jinja_template_loading()