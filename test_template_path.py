#!/usr/bin/env python3
"""
Test script to verify template directory path
"""

import os
from pathlib import Path

def test_template_paths():
    """Test template directory paths"""
    # Get the current file's directory
    current_dir = Path(__file__).parent
    print(f"Current directory: {current_dir}")
    
    # Test the template directory path used in DocumentGenerator
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    print(f"Calculated template directory: {template_dir}")
    print(f"Template directory exists: {os.path.exists(template_dir)}")
    
    if os.path.exists(template_dir):
        # List files in template directory
        files = os.listdir(template_dir)
        html_files = [f for f in files if f.endswith('.html')]
        print(f"HTML template files found: {len(html_files)}")
        for file in html_files[:5]:  # Show first 5 files
            print(f"  - {file}")
    else:
        print("Template directory not found!")
        
        # Try alternative paths
        alternative_paths = [
            os.path.join(current_dir, 'templates'),
            os.path.join(current_dir, 'templates_14102025'),
            os.path.join(current_dir, 'templates_14102025', 'templates_14102025'),
        ]
        
        for path in alternative_paths:
            print(f"Checking alternative path: {path}")
            if os.path.exists(path):
                print(f"  Found! This path exists.")
                files = os.listdir(path)
                html_files = [f for f in files if f.endswith('.html')]
                print(f"  HTML template files found: {len(html_files)}")
                for file in html_files[:5]:  # Show first 5 files
                    print(f"    - {file}")
            else:
                print(f"  Not found.")

if __name__ == "__main__":
    test_template_paths()