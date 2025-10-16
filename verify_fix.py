#!/usr/bin/env python3
"""
Verification script to confirm that the import error is completely resolved
"""

import sys
import traceback

def test_imports():
    """Test all the imports that were causing issues"""
    print("🔍 Verifying that the import error is resolved...")
    print("=" * 50)
    
    # Test 1: Import DocumentGenerator from enhanced_document_generator_fixed
    try:
        from enhanced_document_generator_fixed import DocumentGenerator
        print("✅ Test 1 PASSED: DocumentGenerator imported successfully")
    except ImportError as e:
        print(f"❌ Test 1 FAILED: {e}")
        return False
    except Exception as e:
        print(f"❌ Test 1 FAILED with unexpected error: {e}")
        traceback.print_exc()
        return False
    
    # Test 2: Import app module
    try:
        import app
        print("✅ Test 2 PASSED: app module imported successfully")
    except ImportError as e:
        print(f"❌ Test 2 FAILED: {e}")
        return False
    except Exception as e:
        print(f"❌ Test 2 FAILED with unexpected error: {e}")
        traceback.print_exc()
        return False
    
    # Test 3: Create an instance of DocumentGenerator
    try:
        import pandas as pd
        # Create minimal data structure
        data = {
            'title_data': {},
            'work_order_data': pd.DataFrame(),
            'bill_quantity_data': pd.DataFrame(),
            'extra_items_data': pd.DataFrame()
        }
        generator = DocumentGenerator(data)
        print("✅ Test 3 PASSED: DocumentGenerator instance created successfully")
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
        traceback.print_exc()
        return False
    
    print("=" * 50)
    print("🎉 ALL TESTS PASSED! The import error has been resolved.")
    print("The application should now start without any import errors.")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)