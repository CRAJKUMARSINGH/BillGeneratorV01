#!/usr/bin/env python3
"""
Simple test to see the actual template loading error
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from jinja2 import Environment, FileSystemLoader

def test_template_loading():
    """Test template loading with full error reporting"""
    print("Simple Template Loading Test")
    print("=" * 30)
    
    # Use the same path calculation as DocumentGenerator
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    
    print(f"Template directory: {template_dir}")
    print(f"Directory exists: {os.path.exists(template_dir)}")
    
    if os.path.exists(template_dir):
        print("Contents of template directory:")
        files = os.listdir(template_dir)
        html_files = [f for f in files if f.endswith('.html')]
        for file in html_files[:5]:
            print(f"  - {file}")
    
    print("\nCreating Jinja2 environment...")
    try:
        jinja_env = Environment(loader=FileSystemLoader(template_dir))
        print("✅ Environment created successfully")
    except Exception as e:
        print(f"❌ Environment creation failed: {e}")
        return False
    
    print("\nTrying to load first_page.html...")
    try:
        template = jinja_env.get_template('first_page.html')
        print("✅ Template loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Template loading failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_template_loading()
    sys.exit(0 if success else 1)