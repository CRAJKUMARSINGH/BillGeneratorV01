#!/usr/bin/env python3
"""
Test script to verify that all templates are properly linked with data
"""

import pandas as pd
import os
import sys
from jinja2 import Environment, FileSystemLoader

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.template_renderer import TemplateRenderer
from enhanced_document_generator_fixed import DocumentGenerator

def create_test_data():
    """Create comprehensive test data for all templates"""
    # Sample title data
    title_data = {
        'Project Name': 'Test Road Construction Project',
        'Contract No': 'CT-2025-001',
        'Work Order No': 'WO-2025-001',
        'Contractor Name': 'ABC Construction Ltd.',
        'Bill Number': 'First',
        'Bill Type': 'Final',
        'Measurement Officer': 'Shri Rajesh Kumar',
        'Measurement Date': '15/10/2025',
        'Measurement Book Page': '45',
        'Measurement Book No': 'MB-2025-001',
        'Officer Name': 'Shri Arun Sharma',
        'Officer Designation': 'Assistant Executive Engineer',
        'Authorising Officer Name': 'Shri Deepak Verma',
        'Authorising Officer Designation': 'Executive Engineer',
        'agreement_no': 'CT-2025-001',
        'name_of_work': 'Test Road Construction Project',
        'name_of_firm': 'ABC Construction Ltd.',
        'date_commencement': '01/01/2025',
        'date_completion': '31/12/2025',
        'actual_completion': '30/11/2025',
        'work_order_amount': '100000.00',
        'TENDER PREMIUM %': '10.00'
    }
    
    # Sample work order data
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
        }
    ])
    
    # Sample extra items data
    extra_items_data = pd.DataFrame([
        {
            'Item No.': 'E1',
            'Description': 'Emergency Repairs',
            'Unit': 'Lot',
            'Quantity': 1,
            'Rate': 5000,
            'Amount': 5000,
            'Remark': 'Urgent repair work'
        }
    ])
    
    return {
        'title_data': title_data,
        'work_order_data': work_order_data,
        'bill_quantity_data': work_order_data.copy(),
        'extra_items_data': extra_items_data
    }

def test_template_linking():
    """Test that all templates are properly linked with data"""
    print("🧪 Testing Template Data Linking")
    print("=" * 40)
    
    # Create test data
    test_data = create_test_data()
    print("✅ Test data created")
    
    # Initialize document generator
    generator = DocumentGenerator(test_data)
    print("✅ Document generator initialized")
    
    # Test template rendering
    try:
        # Test first page template
        first_page_html = generator._render_template('first_page.html')
        print("✅ First Page template rendered successfully")
        assert len(first_page_html) > 1000, "First page HTML should be substantial"
        
        # Test deviation statement template
        deviation_html = generator._render_template('deviation_statement.html')
        print("✅ Deviation Statement template rendered successfully")
        assert len(deviation_html) > 1000, "Deviation statement HTML should be substantial"
        
        # Test note sheet template
        note_sheet_html = generator._render_template('note_sheet.html')
        print("✅ Note Sheet template rendered successfully")
        assert len(note_sheet_html) > 1000, "Note sheet HTML should be substantial"
        
        # Test extra items template
        extra_items_html = generator._render_template('extra_items.html')
        print("✅ Extra Items template rendered successfully")
        assert len(extra_items_html) > 500, "Extra items HTML should be substantial"
        
        # Test certificate II template
        certificate_ii_html = generator._render_template('certificate_ii.html')
        print("✅ Certificate II template rendered successfully")
        assert len(certificate_ii_html) > 500, "Certificate II HTML should be substantial"
        
        # Test certificate III template
        certificate_iii_html = generator._render_template('certificate_iii.html')
        print("✅ Certificate III template rendered successfully")
        assert len(certificate_iii_html) > 1000, "Certificate III HTML should be substantial"
        
        print("\n🎉 All templates linked with data successfully!")
        print(f"   First Page: {len(first_page_html)} characters")
        print(f"   Deviation Statement: {len(deviation_html)} characters")
        print(f"   Note Sheet: {len(note_sheet_html)} characters")
        print(f"   Extra Items: {len(extra_items_html)} characters")
        print(f"   Certificate II: {len(certificate_ii_html)} characters")
        print(f"   Certificate III: {len(certificate_iii_html)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Template linking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_template_rendering():
    """Test direct template rendering with TemplateRenderer"""
    print("\n🧪 Testing Direct Template Rendering")
    print("=" * 40)
    
    # Create test data
    test_data = create_test_data()
    title_data = test_data['title_data']
    work_order_data = test_data['work_order_data']
    extra_items_data = test_data['extra_items_data']
    
    # Initialize template renderer
    renderer = TemplateRenderer()
    print("✅ Template renderer initialized")
    
    try:
        # Test first page rendering
        first_page_html = renderer.render_first_page(title_data, work_order_data, extra_items_data)
        print("✅ First Page rendered successfully")
        assert len(first_page_html) > 1000, "First page HTML should be substantial"
        
        # Test note sheet rendering
        note_sheet_html = renderer.render_note_sheet(title_data, work_order_data, extra_items_data)
        print("✅ Note Sheet rendered successfully")
        assert len(note_sheet_html) > 1000, "Note sheet HTML should be substantial"
        
        # Test deviation statement rendering
        deviation_html = renderer.render_deviation_statement(title_data, work_order_data, extra_items_data)
        print("✅ Deviation Statement rendered successfully")
        assert len(deviation_html) > 1000, "Deviation statement HTML should be substantial"
        
        # Test extra items rendering
        extra_items_html = renderer.render_extra_items(title_data, work_order_data, extra_items_data)
        print("✅ Extra Items rendered successfully")
        assert len(extra_items_html) > 500, "Extra items HTML should be substantial"
        
        # Test certificate II rendering
        certificate_ii_html = renderer.render_certificate_ii(title_data, work_order_data, extra_items_data)
        print("✅ Certificate II rendered successfully")
        assert len(certificate_ii_html) > 500, "Certificate II HTML should be substantial"
        
        # Test certificate III rendering
        certificate_iii_html = renderer.render_certificate_iii(title_data, work_order_data, extra_items_data)
        print("✅ Certificate III rendered successfully")
        assert len(certificate_iii_html) > 1000, "Certificate III HTML should be substantial"
        
        print("\n🎉 All direct template rendering tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Direct template rendering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Template Data Linking Test Suite")
    print("=" * 50)
    
    # Test 1: Template linking through DocumentGenerator
    test1_passed = test_template_linking()
    
    # Test 2: Direct template rendering
    test2_passed = test_direct_template_rendering()
    
    print("\n" + "=" * 50)
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED! Templates are properly linked with data.")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED! Check the output above for details.")
        sys.exit(1)