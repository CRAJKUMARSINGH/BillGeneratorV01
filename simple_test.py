#!/usr/bin/env python3
"""
Simple test script to verify the app functionality
"""

import os
import sys
from pathlib import Path
import pandas as pd

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.excel_processor import ExcelProcessor

def test_excel_processing():
    """Test processing a sample Excel file"""
    print("Testing Excel file processing...")
    
    # Get the first test file
    input_dir = Path("INPUT_FILES")
    test_files = list(input_dir.glob("*.xlsx"))
    
    if not test_files:
        print("❌ No test files found in INPUT_FILES directory")
        return False
    
    test_file = test_files[0]
    print(f"Testing with file: {test_file.name}")
    
    try:
        # Process the Excel file
        print("Creating ExcelProcessor...")
        processor = ExcelProcessor(str(test_file))
        print("Processing Excel file...")
        result = processor.process_excel()
        
        if result and isinstance(result, dict):
            print("✅ Excel file processed successfully!")
            print(f"Available data keys: {list(result.keys())}")
            
            # Show title data
            if 'title_data' in result:
                print(f"📄 Title Data ({len(result['title_data'])} items)")
            
            # Show work order data
            if 'work_order_data' in result:
                work_order_df = result['work_order_data']
                if hasattr(work_order_df, '__len__'):
                    print(f"📋 Work Order Data ({len(work_order_df)} rows)")
                else:
                    print("📋 Work Order Data: Available")
            
            return True
        else:
            print("❌ Failed to process Excel file - no result returned")
            return False
            
    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_output_directory_structure():
    """Test the output directory structure requirements"""
    print("\nTesting output directory structure...")
    
    from datetime import datetime
    
    # Create output directory with timestamp
    output_base = Path("OUTPUT_FILES")
    timestamp = datetime.now().strftime("%Y-%m-%d")
    output_dir = output_base / timestamp
    
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created output directory: {output_dir}")
        
        # Create a test subdirectory with timestamp
        detailed_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        detailed_output_dir = output_base / detailed_timestamp
        detailed_output_dir.mkdir(exist_ok=True)
        print(f"✅ Created detailed output directory: {detailed_output_dir}")
        
        # Create a test file in the output directory
        test_file = detailed_output_dir / "test_output.txt"
        with open(test_file, "w") as f:
            f.write("This is a test output file")
        print(f"✅ Created test output file: {test_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating output directory structure: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Simple App Test")
    print("=" * 40)
    
    # Test 1: Excel processing
    test1_result = test_excel_processing()
    
    # Test 2: Output directory structure
    test2_result = test_output_directory_structure()
    
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    print(f"Excel Processing Test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Output Directory Test: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed!")
        return True
    else:
        print("\n💥 Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)