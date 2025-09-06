#!/usr/bin/env python3
"""
Debug script for Excel processing issues
This script helps diagnose why Excel files are not being processed correctly
"""

import pandas as pd
import os
import sys
from utils.excel_processor import ExcelProcessor

def test_excel_file(file_path):
    """Test Excel file processing with detailed debugging"""
    print("=" * 60)
    print(f"TESTING EXCEL FILE: {file_path}")
    print("=" * 60)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ ERROR: File does not exist: {file_path}")
        return False
    
    # Check file size
    file_size = os.path.getsize(file_path)
    print(f"📁 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    
    # Check file permissions
    if not os.access(file_path, os.R_OK):
        print("❌ ERROR: No read permission for file")
        return False
    else:
        print("✅ File is readable")
    
    try:
        # Test basic Excel reading
        print("\n🔍 Testing basic Excel file reading...")
        excel_file = pd.ExcelFile(file_path)
        print(f"✅ Excel file opened successfully")
        print(f"📋 Available sheets: {excel_file.sheet_names}")
        
        # Test each sheet
        for sheet_name in excel_file.sheet_names:
            print(f"\n📄 Testing sheet: '{sheet_name}'")
            try:
                df = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=5)
                print(f"   ✅ Sheet readable, shape: {df.shape}")
                print(f"   📊 Columns: {list(df.columns)}")
                if not df.empty:
                    print(f"   📝 Sample data:\n{df.head(2)}")
            except Exception as e:
                print(f"   ❌ Error reading sheet: {str(e)}")
        
        # Test with our processor
        print(f"\n🔧 Testing with ExcelProcessor...")
        processor = ExcelProcessor(file_path)
        data = processor.process_excel()
        
        print(f"\n✅ SUCCESS! Data extracted:")
        for key, value in data.items():
            if isinstance(value, pd.DataFrame):
                print(f"   {key}: {len(value)} rows")
            else:
                print(f"   {key}: {len(value) if isinstance(value, dict) else 'N/A'} items")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        print(f"📋 Full traceback:\n{traceback.format_exc()}")
        return False

def main():
    """Main function to test Excel files"""
    print("🔍 Excel Processing Debug Tool")
    print("=" * 60)
    
    # Test files in test_input_files directory
    test_dir = "test_input_files"
    if os.path.exists(test_dir):
        print(f"📁 Testing files in {test_dir} directory...")
        excel_files = [f for f in os.listdir(test_dir) if f.endswith(('.xlsx', '.xls'))]
        
        if not excel_files:
            print("❌ No Excel files found in test_input_files directory")
            return
        
        for excel_file in excel_files[:3]:  # Test first 3 files
            file_path = os.path.join(test_dir, excel_file)
            success = test_excel_file(file_path)
            if success:
                print(f"✅ {excel_file} - PASSED")
            else:
                print(f"❌ {excel_file} - FAILED")
            print()
    else:
        print(f"❌ Test directory {test_dir} not found")
    
    # Test with user-provided file
    if len(sys.argv) > 1:
        user_file = sys.argv[1]
        print(f"📁 Testing user-provided file: {user_file}")
        test_excel_file(user_file)

if __name__ == "__main__":
    main()
