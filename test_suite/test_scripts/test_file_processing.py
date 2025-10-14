#!/usr/bin/env python3
"""
Simple test script to process one of the test input files
"""

import pandas as pd
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.excel_processor import ExcelProcessor

def test_file_processing():
    """Test processing a sample input file"""
    # Use one of the test files
    test_file = "test_input_files/3rdFinalNoExtra.xlsx"
    
    print(f"Testing file: {test_file}")
    
    if not os.path.exists(test_file):
        print(f"File not found: {test_file}")
        # Try with absolute path
        test_file = os.path.join(os.getcwd(), "test_input_files", "3rdFinalNoExtra.xlsx")
        print(f"Trying absolute path: {test_file}")
        if not os.path.exists(test_file):
            print(f"File not found with absolute path: {test_file}")
            return
    
    try:
        # Process the Excel file
        print("Creating ExcelProcessor...")
        processor = ExcelProcessor(test_file)
        print("Processing Excel file...")
        result = processor.process_excel()
        
        print("\n✅ File processed successfully!")
        print(f"Available keys: {list(result.keys())}")
        
        # Show title data
        if 'title_data' in result:
            print(f"\n📄 Title Data ({len(result['title_data'])} items):")
            for key, value in list(result['title_data'].items())[:5]:  # Show first 5 items
                print(f"  {key}: {value}")
            if len(result['title_data']) > 5:
                print(f"  ... and {len(result['title_data']) - 5} more items")
        
        # Show work order data
        if 'work_order_data' in result:
            work_order_df = result['work_order_data']
            print(f"\n📋 Work Order Data ({len(work_order_df)} rows):")
            print(f"Columns: {list(work_order_df.columns)}")
            print("First 3 rows:")
            print(work_order_df.head(3))
        
        # Show bill quantity data
        if 'bill_quantity_data' in result:
            bill_qty_df = result['bill_quantity_data']
            print(f"\n💰 Bill Quantity Data ({len(bill_qty_df)} rows):")
            print(f"Columns: {list(bill_qty_df.columns)}")
            print("First 3 rows:")
            print(bill_qty_df.head(3))
        
        # Show extra items data
        if 'extra_items_data' in result:
            extra_items_df = result['extra_items_data']
            if not extra_items_df.empty:
                print(f"\n➕ Extra Items Data ({len(extra_items_df)} rows):")
                print(f"Columns: {list(extra_items_df.columns)}")
                print("First 3 rows:")
                print(extra_items_df.head(3))
            else:
                print("\n➕ Extra Items Data: None")
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("Starting test...")
    test_file_processing()
    print("Test completed.")