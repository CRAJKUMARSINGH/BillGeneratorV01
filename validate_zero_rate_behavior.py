#!/usr/bin/env python3
"""
Validate and correct zero rate behavior to match exact VBA specification
"""

import pandas as pd
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.first_page_generator import FirstPageGenerator

def test_current_behavior():
    """Test current behavior of FirstPageGenerator"""
    print("Testing Current Zero Rate Behavior...")
    
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
        },
        {
            'Item No.': '003',
            'Description': 'Another standard item',
            'Unit': 'CuM',
            'Quantity Since': 25.5,
            'Rate': 8500.0,
            'Remark': 'Regular rate item'
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
        },
        {
            'Item No.': 'EX02',
            'Description': 'Extra zero rate item',
            'Unit': 'No',
            'Quantity': 1.0,
            'Rate': 0.0,
            'Remark': 'No charge'
        }
    ])
    
    title_data = {
        'Name of Work ;-': 'Test Infrastructure Project',
        'Name of Contractor or supplier :': 'ABC Construction Ltd',
        'Date': '15-10-2025'
    }
    
    # Generate First Page
    generator = FirstPageGenerator()
    output_path = "test_zero_rate_behavior.xlsx"
    
    try:
        generator.generate_first_page(work_order_data, extra_items_data, title_data, output_path)
        print(f"✅ First Page generated: {output_path}")
        
        # Verify the file was created
        if Path(output_path).exists():
            print("✅ Output file created successfully")
            # Clean up test file
            Path(output_path).unlink()
            print("✅ Test file cleaned up")
            return True
        else:
            print("❌ Output file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error generating First Page: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_vba_compliance():
    """Check if current implementation complies with VBA specification"""
    print("\nChecking VBA Compliance...")
    
    # According to the requirement:
    # If Rate is blank or zero:
    # - Only Serial Number (Column D) and Description (Column E) should be populated
    # - All other columns should remain blank
    
    # Current implementation in FirstPageGenerator:
    # - Populates Unit (A), Quantity Since (B), Quantity Upto (C), Serial No (D), Description (E), Rate (F)
    # - Only leaves Amount columns (G, H) blank for zero rates
    
    print("❌ Current implementation does NOT fully comply with VBA specification")
    print("   Current behavior: Populates all columns except amounts for zero rates")
    print("   Required behavior: Only populate Serial No. and Description for zero rates")
    
    return False

def main():
    """Main validation function"""
    print("🔍 Zero Rate Behavior Validation")
    print("=" * 50)
    
    # Test current behavior
    test_result = test_current_behavior()
    
    # Check VBA compliance
    compliance_result = check_vba_compliance()
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Functionality Test: {'✅ PASS' if test_result else '❌ FAIL'}")
    print(f"VBA Compliance: {'✅ PASS' if compliance_result else '❌ FAIL'}")
    
    if not compliance_result:
        print("\n⚠️  ACTION REQUIRED:")
        print("   FirstPageGenerator needs to be updated to match exact VBA specification")
        print("   For zero rates: Only populate Serial No. (D) and Description (E)")
        print("   All other columns should remain blank")
    
    return test_result and compliance_result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)