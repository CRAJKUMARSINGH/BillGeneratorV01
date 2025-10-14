#!/usr/bin/env python3
"""
Test script to verify the deployable app components work correctly
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import streamlit as st
        print("✅ Streamlit import successful")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas import successful")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        from utils.excel_processor import ExcelProcessor
        print("✅ ExcelProcessor import successful")
    except ImportError as e:
        print(f"❌ ExcelProcessor import failed: {e}")
        return False
    
    try:
        from fixed_document_generator import FixedDocumentGenerator
        print("✅ FixedDocumentGenerator import successful")
    except ImportError as e:
        print(f"❌ FixedDocumentGenerator import failed: {e}")
        return False
    
    try:
        from streamlit.components.v1 import html
        print("✅ Streamlit components import successful")
    except ImportError as e:
        print(f"❌ Streamlit components import failed: {e}")
        return False
    
    return True

def test_template_files():
    """Test that all required template files exist"""
    template_dir = Path("templates")
    required_templates = [
        "first_page.html",
        "deviation_statement.html",
        "extra_items.html",
        "certificate_ii.html",
        "certificate_iii.html",
        "note_sheet.html"
    ]
    
    missing_templates = []
    for template in required_templates:
        template_path = template_dir / template
        if not template_path.exists():
            missing_templates.append(template)
        else:
            print(f"✅ Template file found: {template}")
    
    if missing_templates:
        print(f"❌ Missing template files: {missing_templates}")
        return False
    
    return True

def test_deployable_app():
    """Test that the deployable app can be imported"""
    try:
        # This will test if the app can be imported without errors
        import deployable_app
        print("✅ Deployable app import successful")
        return True
    except Exception as e:
        print(f"❌ Deployable app import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Deployable Bill Generator Components")
    print("=" * 50)
    
    # Test imports
    print("\n1. Testing imports...")
    imports_ok = test_imports()
    
    # Test template files
    print("\n2. Testing template files...")
    templates_ok = test_template_files()
    
    # Test deployable app
    print("\n3. Testing deployable app...")
    app_ok = test_deployable_app()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print(f"  Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"  Templates: {'✅ PASS' if templates_ok else '❌ FAIL'}")
    print(f"  App: {'✅ PASS' if app_ok else '❌ FAIL'}")
    
    if imports_ok and templates_ok and app_ok:
        print("\n🎉 All tests passed! The deployable app is ready for deployment.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)