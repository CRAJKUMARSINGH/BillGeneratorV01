#!/usr/bin/env python3
"""
Test script to verify Certificate II template and content
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_certificate_ii_template():
    """Test that the Certificate II template has the correct content"""
    template_path = Path("templates") / "certificate_ii.html"
    
    if not template_path.exists():
        print(f"❌ Template file not found: {template_path}")
        return False
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key elements in the corrected Certificate II
        required_elements = [
            "The measurements on which are based the entries in columns 1 to 6 of Account I",
            "Certified that in addition to and quite apart from the quantities of work actually executed",
            "Signature of officer preparing the bill",
            "Signature of officer authorising payment"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing elements in Certificate II template:")
            for element in missing_elements:
                print(f"  - {element}")
            return False
        
        print("✅ Certificate II template has correct content")
        return True
        
    except Exception as e:
        print(f"❌ Error reading template file: {e}")
        return False

def test_fixed_document_generator():
    """Test that the fixed document generator produces correct Certificate II"""
    try:
        from fixed_document_generator import FixedDocumentGenerator
        import pandas as pd
        
        # Create sample data with measurement information
        sample_data = {
            'title_data': {
                'Project Name': 'Sample Road Construction Project',
                'Contract No': 'PWD/RC/2024/001',
                'Work Order No': 'WO/RC/2024/001',
                'Contractor Name': 'ABC Construction Ltd',
                'Measurement Officer': 'John Smith',
                'Measurement Date': '30/04/2025',
                'Measurement Book Page': '123',
                'Measurement Book No': 'MB-001',
                'Officer Name': 'Officer Name',
                'Officer Designation': 'Site Supervisor',
                'Authorising Officer Name': 'Authorising Officer Name',
                'Authorising Officer Designation': 'Executive Engineer'
            },
            'work_order_data': pd.DataFrame([
                {
                    'Item No.': '1.1',
                    'Description': 'Earthwork in excavation',
                    'Unit': 'Cum',
                    'Quantity Since': 150.50,
                    'Quantity Upto': 300.25,
                    'Rate': 120.00
                }
            ]),
            'bill_quantity_data': pd.DataFrame([
                {
                    'Item No.': '1.1',
                    'Description': 'Earthwork in excavation',
                    'Unit': 'Cum',
                    'Quantity': 310.00,
                    'Rate': 120.00
                }
            ]),
            'extra_items_data': pd.DataFrame()
        }
        
        # Test the generator
        generator = FixedDocumentGenerator(sample_data)
        certificate_ii = generator._generate_certificate_ii()
        
        # Check for key elements in the generated Certificate II
        required_elements = [
            "The measurements on which are based the entries in columns 1 to 6 of Account I",
            "John Smith",  # Measurement officer from sample data
            "30/04/2025",  # Measurement date from sample data
            "Signature of officer preparing the bill",
            "Signature of officer authorising payment"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in certificate_ii:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing elements in generated Certificate II:")
            for element in missing_elements:
                print(f"  - {element}")
            return False
        
        print("✅ Fixed Document Generator produces correct Certificate II")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Fixed Document Generator: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Certificate II Content")
    print("=" * 40)
    
    # Test template
    print("\n1. Testing Certificate II template...")
    template_ok = test_certificate_ii_template()
    
    # Test fixed document generator
    print("\n2. Testing Fixed Document Generator...")
    generator_ok = test_fixed_document_generator()
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY:")
    print(f"  Template: {'✅ PASS' if template_ok else '❌ FAIL'}")
    print(f"  Generator: {'✅ PASS' if generator_ok else '❌ FAIL'}")
    
    if template_ok and generator_ok:
        print("\n🎉 All tests passed! Certificate II content is correct.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)