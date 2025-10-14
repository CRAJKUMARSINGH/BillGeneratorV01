#!/usr/bin/env python3
"""
Direct test of Excel processing functionality
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import required modules
try:
    from utils.excel_processor import ExcelProcessor
    print("✅ Successfully imported ExcelProcessor")
except ImportError as e:
    print(f"❌ Failed to import ExcelProcessor: {e}")
    sys.exit(1)

def test_single_file():
    """Test processing a single Excel file"""
    print("\nTesting single Excel file processing...")
    
    # Get test files
    input_dir = Path("INPUT_FILES")
    test_files = list(input_dir.glob("*.xlsx"))
    
    if not test_files:
        print("❌ No test files found")
        return False
    
    # Test with the first file
    test_file = test_files[0]
    print(f"Testing file: {test_file.name}")
    
    try:
        # Process the file
        processor = ExcelProcessor(str(test_file))
        result = processor.process_excel()
        
        if result:
            print("✅ File processed successfully!")
            print(f"Keys in result: {list(result.keys())}")
            
            # Check each component
            for key in ['title_data', 'work_order_data', 'bill_quantity_data']:
                if key in result:
                    data = result[key]
                    if hasattr(data, '__len__'):
                        print(f"  {key}: {len(data)} items/rows")
                    else:
                        print(f"  {key}: Present")
                else:
                    print(f"  {key}: Not found")
            
            return True
        else:
            print("❌ Processing returned no result")
            return False
            
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_files():
    """Test processing multiple files"""
    print("\nTesting multiple Excel files...")
    
    # Get test files
    input_dir = Path("INPUT_FILES")
    test_files = list(input_dir.glob("*.xlsx"))[:3]  # Test first 3 files
    
    if not test_files:
        print("❌ No test files found")
        return False
    
    print(f"Testing {len(test_files)} files:")
    
    success_count = 0
    for i, test_file in enumerate(test_files, 1):
        print(f"  [{i}/{len(test_files)}] {test_file.name}...")
        
        try:
            processor = ExcelProcessor(str(test_file))
            result = processor.process_excel()
            
            if result:
                success_count += 1
                print(f"    ✅ Success")
            else:
                print(f"    ❌ No result")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    print(f"\n📊 Results: {success_count}/{len(test_files)} files processed successfully")
    return success_count > 0

def main():
    """Main test function"""
    print("🚀 Excel Processing Direct Test")
    print("=" * 40)
    
    # Test single file
    test1 = test_single_file()
    
    # Test multiple files
    test2 = test_multiple_files()
    
    print("\n" + "=" * 40)
    print("FINAL RESULTS")
    print("=" * 40)
    print(f"Single File Test: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Multiple Files Test: {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n🎉 All Excel processing tests passed!")
        return True
    else:
        print("\n💥 Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)