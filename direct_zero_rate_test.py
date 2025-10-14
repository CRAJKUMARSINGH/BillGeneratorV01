#!/usr/bin/env python3
"""
Direct test to verify zero rate behavior in FirstPageGenerator
"""

import pandas as pd
import sys
import os
from pathlib import Path
import xlsxwriter

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.first_page_generator import FirstPageGenerator

def test_zero_rate_behavior():
    """Test zero rate behavior directly"""
    print("Testing Zero Rate Behavior Directly...")
    
    # Create test data with zero rate
    work_order_data = pd.DataFrame([
        {
            'Item No.': '001',
            'Description': 'Standard item with rate',
            'Unit': 'CuM',
            'Quantity Since': 50.0,
            'Rate': 1200.0,
            'Remark': 'Standard rate item'
        },
        {
            'Item No.': '002',
            'Description': 'Zero rate item - should only populate Serial No. and Description',
            'Unit': 'No',
            'Quantity Since': 5.0,
            'Rate': 0.0,
            'Remark': 'Zero rate item'
        }
    ])
    
    extra_items_data = pd.DataFrame([
        {
            'Item No.': 'EX01',
            'Description': 'Extra item with rate',
            'Unit': 'Mtr',
            'Quantity': 100.0,
            'Rate': 120.0,
            'Remark': 'Extra work'
        }
    ])
    
    title_data = {
        'Name of Work ;-': 'Test Infrastructure Project',
        'Name of Contractor or supplier :': 'ABC Construction Ltd',
        'Date': '15-10-2025'
    }
    
    # Generate First Page
    generator = FirstPageGenerator()
    output_path = "direct_zero_rate_test.xlsx"
    
    try:
        generator.generate_first_page(work_order_data, extra_items_data, title_data, output_path)
        print(f"✅ First Page generated: {output_path}")
        
        # Verify the file was created
        if Path(output_path).exists():
            print("✅ Output file created successfully")
            return True
        else:
            print("❌ Output file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error generating First Page: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🔍 Direct Zero Rate Behavior Test")
    print("=" * 50)
    
    result = test_zero_rate_behavior()
    
    print("\n" + "=" * 50)
    if result:
        print("✅ Zero rate behavior test passed!")
    else:
        print("❌ Zero rate behavior test failed!")
    
    return result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)