#!/usr/bin/env python3
"""
Test script to verify DocumentGenerator template path calculation
"""

import os
import sys
from pathlib import Path

def test_document_generator_path():
    """Test the exact path calculation used in DocumentGenerator"""
    print("Testing DocumentGenerator template path calculation...")
    
    # This is the exact code from DocumentGenerator.__init__
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    
    print(f"__file__ = {__file__}")
    print(f"os.path.dirname(__file__) = {os.path.dirname(__file__)}")
    print(f"os.path.dirname(os.path.dirname(__file__)) = {os.path.dirname(os.path.dirname(__file__))}")
    print(f"template_dir = {template_dir}")
    
    # Check if the directory exists
    print(f"template_dir exists: {os.path.exists(template_dir)}")
    
    if os.path.exists(template_dir):
        print("✅ Template directory found")
        # List contents
        try:
            files = os.listdir(template_dir)
            html_files = [f for f in files if f.endswith('.html')]
            print(f"HTML files found: {len(html_files)}")
            for file in html_files[:5]:
                print(f"  - {file}")
        except Exception as e:
            print(f"Error listing directory: {e}")
    else:
        print("❌ Template directory NOT found")
        # Try to find where it might be
        current_dir = Path(__file__).parent
        print(f"Current directory: {current_dir}")
        
        # Check common locations
        possible_paths = [
            current_dir / 'templates',
            current_dir.parent / 'templates',
            Path('C:\\Users\\Rajkumar\\BillGeneratorV01\\templates'),
            Path('C:\\Users\\Rajkumar\\templates'),
        ]
        
        for path in possible_paths:
            print(f"Checking: {path}")
            if path.exists():
                print(f"  ✅ Found at: {path}")
                try:
                    files = os.listdir(path)
                    html_files = [f for f in files if f.endswith('.html')]
                    print(f"  HTML files: {len(html_files)}")
                except Exception as e:
                    print(f"  Error listing: {e}")
            else:
                print(f"  ❌ Not found")

if __name__ == "__main__":
    test_document_generator_path()