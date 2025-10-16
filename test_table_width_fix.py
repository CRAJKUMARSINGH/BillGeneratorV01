#!/usr/bin/env python3
"""
Test script to verify the table width fix for First Page and Extra Items PDF output
"""

import pandas as pd
import tempfile
import os
from utils.document_generator import DocumentGenerator

def test_table_width_fix():
    """Test that the table width fix works correctly"""
    print("🧪 Testing Table Width Fix")
    print("=" * 30)
    
    # Create test data
    title_data = {
        'Project Name': 'NH-XX Highway Improvement Project',
        'Contract No': 'NH-2025-789',
        'Work Order No': 'WO-2025-456'
    }
    
    work_order_data = pd.DataFrame([
        {
            'Item No.': '1.1',
            'Description': 'Earthwork in excavation in ordinary soil including disposal up to 100 m lead and 3.0 m lift',
            'Unit': 'Cu.M',
            'Quantity Since': 2500.00,
            'Quantity Upto': 5000.00,
            'Rate': 180.00,
            'Amount Since': 450000.00,
            'Amount Upto': 900000.00,
            'Remark': 'Lead 80 m, Lift 2.5 m'
        },
        {
            'Item No.': '1.2',
            'Description': 'Providing and laying in position cement concrete M25 for rigid pavement',
            'Unit': 'Sq.M',
            'Quantity Since': 1200.00,
            'Quantity Upto': 2400.00,
            'Rate': 850.00,
            'Amount Since': 1020000.00,
            'Amount Upto': 2040000.00,
            'Remark': '250 mm thick'
        }
    ])
    
    extra_items_data = pd.DataFrame([
        {
            'Item No.': '2.1',
            'Description': 'Additional earthwork due to unforeseen conditions',
            'Unit': 'Cu.M',
            'Quantity': 500.00,
            'Rate': 200.00,
            'Amount': 100000.00
        }
    ])
    
    # Create document generator
    test_data = {
        'title_data': title_data,
        'work_order_data': work_order_data,
        'bill_quantity_data': work_order_data,  # Using work_order_data as bill_quantity_data for test
        'extra_items_data': extra_items_data
    }
    generator = DocumentGenerator(test_data)
    
    # Generate First Page Summary
    print("📄 Generating First Page Summary...")
    first_page_html = generator._generate_first_page()
    
    # Check that the specific table headers are present with correct widths
    expected_headers = [
        '<th style="width: 9.55mm;">S. No.</th>',
        '<th style="width: 63.83mm;">Item of Work supplies (Grouped under "sub-head" and "sub work" of estimate)</th>',
        '<th style="width: 10.06mm;">Unit</th>',
        '<th style="width: 13.76mm;">Quantity executed (or supplied) since last certificate</th>',
        '<th style="width: 13.76mm;">Quantity executed (or supplied) upto date as per MB</th>',
        '<th style="width: 13.16mm;">Rate</th>',
        '<th style="width: 19.53mm;">Upto date Amount</th>',
        '<th style="width: 15.15mm;">Amount Since previous bill (Total for each sub-head)</th>',
        '<th style="width: 11.96mm;">Remarks</th>'
    ]
    
    print("🔍 Checking First Page table headers...")
    all_headers_found = True
    for header in expected_headers:
        if header in first_page_html:
            print(f"✅ Found: {header[:50]}...")
        else:
            print(f"❌ Missing: {header[:50]}...")
            all_headers_found = False
    
    # Generate Extra Items Statement
    print("\n📄 Generating Extra Items Statement...")
    extra_items_html = generator._generate_extra_items_statement()
    
    # Check that the specific table headers are present with correct widths
    expected_extra_headers = [
        '<th style="width: 9.55mm;">Item No.</th>',
        '<th style="width: 63.83mm;">Description</th>',
        '<th style="width: 10.06mm;">Unit</th>',
        '<th style="width: 13.76mm;">Quantity</th>',
        '<th style="width: 13.16mm;">Rate</th>',
        '<th style="width: 19.53mm;">Amount</th>'
    ]
    
    print("🔍 Checking Extra Items table headers...")
    all_extra_headers_found = True
    for header in expected_extra_headers:
        if header in extra_items_html:
            print(f"✅ Found: {header[:50]}...")
        else:
            print(f"❌ Missing: {header[:50]}...")
            all_extra_headers_found = False
    
    # Check CSS column widths
    print("\n🔍 Checking CSS column widths...")
    expected_css = [
        'table.first-page-summary col.col-item-no { width: 9.55mm; }',
        'table.first-page-summary col.col-description { width: 63.83mm; }',
        'table.first-page-summary col.col-unit { width: 10.06mm; }',
        'table.first-page-summary col.col-qty-since { width: 13.76mm; }',
        'table.first-page-summary col.col-qty-upto { width: 13.76mm; }',
        'table.first-page-summary col.col-rate { width: 13.16mm; }',
        'table.first-page-summary col.col-amt-upto { width: 19.53mm; }',
        'table.first-page-summary col.col-amt-since { width: 15.15mm; }',
        'table.first-page-summary col.col-remark { width: 11.96mm; }',
        'table.extra-items col.col-item-no { width: 9.55mm; }',
        'table.extra-items col.col-description { width: 63.83mm; }',
        'table.extra-items col.col-unit { width: 10.06mm; }',
        'table.extra-items col.col-quantity { width: 13.76mm; }',
        'table.extra-items col.col-rate { width: 13.16mm; }',
        'table.extra-items col.col-amount { width: 19.53mm; }'
    ]
    
    all_css_found = True
    for css_rule in expected_css:
        if css_rule in first_page_html or css_rule in extra_items_html:
            print(f"✅ Found: {css_rule[:50]}...")
        else:
            print(f"❌ Missing: {css_rule[:50]}...")
            all_css_found = False
    
    # Save HTML for inspection
    with tempfile.TemporaryDirectory() as temp_dir:
        first_page_path = os.path.join(temp_dir, 'first_page_summary.html')
        with open(first_page_path, 'w', encoding='utf-8') as f:
            f.write(first_page_html)
        print(f"\n💾 First Page HTML saved to: {first_page_path}")
        
        extra_items_path = os.path.join(temp_dir, 'extra_items_statement.html')
        with open(extra_items_path, 'w', encoding='utf-8') as f:
            f.write(extra_items_html)
        print(f"💾 Extra Items HTML saved to: {extra_items_path}")
    
    # Final result
    if all_headers_found and all_extra_headers_found and all_css_found:
        print("\n🎉 TABLE WIDTH FIX TEST PASSED!")
        print("✅ All table headers have correct widths")
        print("✅ All CSS column width specifications are present")
        return True
    else:
        print("\n💥 TABLE WIDTH FIX TEST FAILED!")
        return False

if __name__ == "__main__":
    success = test_table_width_fix()
    if not success:
        exit(1)