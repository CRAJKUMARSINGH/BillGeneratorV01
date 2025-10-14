#!/usr/bin/env python3
"""
Test script to verify Excel file processing works correctly
"""

import pandas as pd
import sys
import os
from pathlib import Path
import traceback

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.excel_processor import ExcelProcessor

def test_excel_processing():
    """Test processing a sample Excel file"""
    # Use one of the test files
    test_file = "test_input_files/3rdFinalNoExtra.xlsx"
    
    print(f"Testing Excel processing with file: {test_file}")
    
    if not os.path.exists(test_file):
        print(f"File not found: {test_file}")
        return False
    
    try:
        # Process the Excel file
        print("Creating ExcelProcessor...")
        processor = ExcelProcessor(test_file)
        print("Processing Excel file...")
        result = processor.process_excel()
        
        print("\n✅ Excel file processed successfully!")
        print(f"Available data keys: {list(result.keys())}")
        
        # Show title data
        if 'title_data' in result:
            print(f"\n📄 Title Data ({len(result['title_data'])} items):")
            for key, value in list(result['title_data'].items())[:3]:  # Show first 3 items
                print(f"  {key}: {value}")
        
        # Show work order data
        if 'work_order_data' in result:
            work_order_df = result['work_order_data']
            print(f"\n📋 Work Order Data ({len(work_order_df)} rows):")
            print(f"Columns: {list(work_order_df.columns)}")
            print("First 2 rows:")
            print(work_order_df.head(2))
        
        # Show bill quantity data
        if 'bill_quantity_data' in result:
            bill_qty_df = result['bill_quantity_data']
            print(f"\n💰 Bill Quantity Data ({len(bill_qty_df)} rows):")
            print(f"Columns: {list(bill_qty_df.columns)}")
            print("First 2 rows:")
            print(bill_qty_df.head(2))
        
        # Show extra items data
        if 'extra_items_data' in result:
            extra_items_df = result['extra_items_data']
            if hasattr(extra_items_df, 'empty') and not extra_items_df.empty:
                print(f"\n➕ Extra Items Data ({len(extra_items_df)} rows):")
                print(f"Columns: {list(extra_items_df.columns)}")
                print("First 2 rows:")
                print(extra_items_df.head(2))
            else:
                print("\n➕ Extra Items Data: None (empty)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Excel processing test...")
    success = test_excel_processing()
    if success:
        print("\n🎉 Excel processing test completed successfully!")
    else:
        print("\n💥 Excel processing test failed!")