#!/usr/bin/env python3
"""
Test script to verify zero rate item handling in first page template
"""

import pandas as pd
import os
import sys
from jinja2 import Environment, FileSystemLoader

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.template_renderer import TemplateRenderer

def create_test_data():
    """Create test data with zero rate items"""
    # Sample title data
    title_data = {
        'Project Name': 'Test Road Construction Project',
        'Contract No': 'CT-2025-001',
        'Work Order No': 'WO-2025-001',
        'Contractor Name': 'ABC Construction Ltd.',
        'Bill Number': 'First',
        'Bill Type': 'Final'
    }
    
    # Sample work order data with zero rate items
    work_order_data = pd.DataFrame([
        {
            'Item No.': '1',
            'Description': 'Excavation in Hard Rock',
            'Unit': 'Cu.M',
            'Quantity Since': 150.50,
            'Quantity Upto': 150.50,
            'Rate': 1500.00,
            'Amount': 225750.00,
            'Remark': 'Completed'
        },
        {
            'Item No.': '2',
            'Description': 'Providing and Laying Cement Concrete M20',
            'Unit': 'Cu.M',
            'Quantity Since': 85.25,
            'Quantity Upto': 85.25,
            'Rate': 4500.00,
            'Amount': 383625.00,
            'Remark': 'In Progress'
        },
        {
            'Item No.': '3',
            'Description': 'Supply of Cement (Zero Rate Item)',
            'Unit': 'Bags',
            'Quantity Since': 500,
            'Quantity Upto': 500,
            'Rate': 0.00,
            'Amount': 0.00,
            'Remark': 'Zero rate item'
        },
        {
            'Item No.': '4',
            'Description': 'Free Transportation (Blank Rate)',
            'Unit': 'Trip',
            'Quantity Since': 10,
            'Quantity Upto': 10,
            'Rate': '',
            'Amount': 0.00,
            'Remark': 'Free service'
        }
    ])
    
    # Sample extra items data with zero rate items
    extra_items_data = pd.DataFrame([
        {
            'Item No.': 'E1',
            'Description': 'Emergency Repairs',
            'Unit': 'Lot',
            'Quantity': 1,
            'Rate': 5000,
            'Amount': 5000,
            'Remark': 'Urgent repair work'
        },
        {
            'Item No.': 'E2',
            'Description': 'Free Inspection (Zero Rate)',
            'Unit': 'Visit',
            'Quantity': 3,
            'Rate': 0.00,
            'Amount': 0.00,
            'Remark': 'Complimentary service'
        }
    ])
    
    return title_data, work_order_data, extra_items_data

def test_zero_rate_handling():
    """Test that zero rate items are handled correctly"""
    print("Testing Zero Rate Item Handling")
    print("=" * 40)
    
    # Create test data
    title_data, work_order_data, extra_items_data = create_test_data()
    print("✅ Test data created")
    
    # Initialize template renderer
    renderer = TemplateRenderer()
    print("✅ Template renderer initialized")
    
    try:
        # Render first page template
        html_content = renderer.render_first_page(title_data, work_order_data, extra_items_data)
        print("✅ First page template rendered")
        
        # Check that the HTML contains the expected content
        if 'Supply of Cement (Zero Rate Item)' in html_content:
            print("✅ Zero rate item description found")
        else:
            print("❌ Zero rate item description not found")
            return False
            
        if 'Free Transportation (Blank Rate)' in html_content:
            print("✅ Blank rate item description found")
        else:
            print("❌ Blank rate item description not found")
            return False
            
        if 'Free Inspection (Zero Rate)' in html_content:
            print("✅ Extra zero rate item description found")
        else:
            print("❌ Extra zero rate item description not found")
            return False
            
        # Save the HTML for manual inspection
        with open('test_zero_rate_output.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✅ HTML output saved to test_zero_rate_output.html")
        
        print("\n🎉 Zero rate item handling test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Zero rate handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_zero_rate_handling()