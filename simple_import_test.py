#!/usr/bin/env python3
"""
Simple test to verify imports and basic functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from utils.first_page_generator import FirstPageGenerator
        print("✅ FirstPageGenerator imported successfully")
        
        from utils.excel_processor import ExcelProcessor
        print("✅ ExcelProcessor imported successfully")
        
        import pandas as pd
        print("✅ pandas imported successfully")
        
        import xlsxwriter
        print("✅ xlsxwriter imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_instantiation():
    """Test that classes can be instantiated"""
    print("Testing instantiation...")
    
    try:
        from utils.first_page_generator import FirstPageGenerator
        generator = FirstPageGenerator()
        print("✅ FirstPageGenerator instantiated successfully")
        return True
    except Exception as e:
        print(f"❌ Instantiation error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Simple Import and Instantiation Test")
    print("=" * 50)
    
    import_result = test_imports()
    instantiation_result = test_instantiation()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Imports: {'✅ PASS' if import_result else '❌ FAIL'}")
    print(f"Instantiation: {'✅ PASS' if instantiation_result else '❌ FAIL'}")
    
    if import_result and instantiation_result:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Application components are working correctly")
        return True
    else:
        print("\n💥 SOME TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)