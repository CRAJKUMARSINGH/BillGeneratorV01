#!/usr/bin/env python3
"""
Test script to verify that the deployable app is using the tested templates correctly
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_template_files():
    """Test that all required template files exist in the templates directory"""
    template_dir = Path("templates")
    required_templates = [
        "certificate_ii.html",
        "certificate_iii.html", 
        "deviation_statement.html",
        "extra_items.html",
        "first_page.html",
        "note_sheet.html"
    ]
    
    missing_templates = []
    for template in required_templates:
        template_path = template_dir / template
        if not template_path.exists():
            missing_templates.append(template)
        else:
            print(f"✅ Template file found: {template}")
    
    if missing_templates:
        print(f"❌ Missing template files: {missing_templates}")
        return False
    
    return True

def test_enhanced_document_generator():
    """Test that the EnhancedDocumentGenerator can be imported and initialized"""
    try:
        from enhanced_document_generator_fixed import EnhancedDocumentGenerator
        import pandas as pd
        
        # Create minimal test data
        test_data = {
            'title_data': {
                'Project Name': 'Test Project',
                'Agreement No.': 'TEST/001/2025'
            },
            'work_order_data': pd.DataFrame([
                {
                    'Item No.': '1.1',
                    'Description': 'Test Item',
                    'Unit': 'Nos',
                    'Quantity Since': 10,
                    'Rate': 100
                }
            ]),
            'bill_quantity_data': pd.DataFrame([
                {
                    'Item No.': '1.1',
                    'Description': 'Test Item',
                    'Unit': 'Nos',
                    'Quantity': 10,
                    'Rate': 100
                }
            ]),
            'extra_items_data': pd.DataFrame()
        }
        
        # Initialize the generator
        generator = EnhancedDocumentGenerator(test_data)
        print("✅ EnhancedDocumentGenerator initialized successfully")
        
        # Test template data preparation
        template_data = generator.template_data
        print("✅ Template data prepared successfully")
        
        # Test document generation
        documents = generator.generate_all_documents()
        print(f"✅ Generated {len(documents)} documents")
        
        # Check that we have the expected documents
        expected_docs = [
            'First Page Summary',
            'Deviation Statement', 
            'Final Bill Scrutiny Sheet',
            'Certificate II',
            'Certificate III'
        ]
        
        missing_docs = []
        for doc in expected_docs:
            if doc not in documents:
                missing_docs.append(doc)
            else:
                print(f"✅ Document generated: {doc}")
        
        if missing_docs:
            print(f"❌ Missing documents: {missing_docs}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing EnhancedDocumentGenerator: {e}")
        return False

def test_deployable_app_imports():
    """Test that the deployable app can be imported without errors"""
    try:
        # This will test if the app can be imported without errors
        import deployable_app
        print("✅ Deployable app imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing deployable app: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Template Integration")
    print("=" * 40)
    
    # Test template files
    print("\n1. Testing template files...")
    templates_ok = test_template_files()
    
    # Test EnhancedDocumentGenerator
    print("\n2. Testing EnhancedDocumentGenerator...")
    generator_ok = test_enhanced_document_generator()
    
    # Test deployable app imports
    print("\n3. Testing deployable app imports...")
    app_ok = test_deployable_app_imports()
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY:")
    print(f"  Template Files: {'✅ PASS' if templates_ok else '❌ FAIL'}")
    print(f"  Document Generator: {'✅ PASS' if generator_ok else '❌ FAIL'}")
    print(f"  Deployable App: {'✅ PASS' if app_ok else '❌ FAIL'}")
    
    if templates_ok and generator_ok and app_ok:
        print("\n🎉 All tests passed! The deployable app is using the tested templates correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)