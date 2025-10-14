"""
Test script for legacy import functionality
"""

import pandas as pd
from migration.legacy_import import import_legacy_excel, import_legacy_csv, convert_legacy_data
import json
import os

def create_sample_legacy_files():
    """Create sample legacy files for testing"""
    # Create sample legacy Excel file (v1 format)
    v1_data = {
        'Item No': [1, 2, 3],
        'Description of Work': ['Excavation', 'Concrete Work', 'Brick Work'],
        'Unit': ['Cum', 'Cum', 'Cum'],
        'Quantity': [10.5, 5.2, 15.0],
        'Rate': [500.0, 2500.0, 1200.0],
        'Amount': [5250.0, 13000.0, 18000.0]
    }
    
    df_v1 = pd.DataFrame(v1_data)
    df_v1.to_excel('sample_legacy_v1.xlsx', index=False)
    print("Created sample_legacy_v1.xlsx")
    
    # Create sample legacy CSV file
    csv_data = {
        'S.No': [1, 2, 3],
        'Work Description': ['Steel Work', 'Painting', 'Plumbing'],
        'Work Unit': ['Kg', 'Sq.m', 'Nos'],
        'Work Qty': [100.0, 50.0, 5.0],
        'Work Rate': [80.0, 50.0, 1500.0],
        'Work Amount': [8000.0, 2500.0, 7500.0]
    }
    
    df_csv = pd.DataFrame(csv_data)
    df_csv.to_csv('sample_legacy.csv', index=False)
    print("Created sample_legacy.csv")

def test_legacy_import():
    """Test the legacy import functions"""
    print("\nTesting legacy import functions...")
    
    # Test Excel import (v1 format)
    try:
        result = import_legacy_excel('sample_legacy_v1.xlsx', 'v1')
        print("✅ Excel v1 import successful")
        print(f"   Data items: {len(result['data'])}")
        print(f"   Format version: {result['format_version']}")
    except Exception as e:
        print(f"❌ Excel v1 import failed: {e}")
    
    # Test CSV import
    try:
        result = import_legacy_csv('sample_legacy.csv')
        print("✅ CSV import successful")
        print(f"   Data items: {len(result['data'])}")
        print(f"   Format version: {result['format_version']}")
    except Exception as e:
        print(f"❌ CSV import failed: {e}")
    
    # Test data conversion
    try:
        success = convert_legacy_data('sample_legacy_v1.xlsx', 'converted_data.json', 'excel', 'v1')
        if success:
            print("✅ Data conversion successful")
            # Check if output file exists
            if os.path.exists('converted_data.json'):
                print("   Output file created")
                # Read and display a portion of the converted data
                with open('converted_data.json', 'r') as f:
                    data = json.load(f)
                    print(f"   Converted items: {len(data.get('data', []))}")
            else:
                print("   Output file not found")
        else:
            print("❌ Data conversion failed")
    except Exception as e:
        print(f"❌ Data conversion error: {e}")

def cleanup_test_files():
    """Clean up test files"""
    test_files = ['sample_legacy_v1.xlsx', 'sample_legacy.csv', 'converted_data.json']
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed {file}")

if __name__ == "__main__":
    print("Legacy Import Test Script")
    print("========================")
    
    # Create sample files
    create_sample_legacy_files()
    
    # Test import functions
    test_legacy_import()
    
    # Clean up
    cleanup_test_files()
    
    print("\nTest completed!")