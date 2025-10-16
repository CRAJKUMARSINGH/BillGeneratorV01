#!/usr/bin/env python3
"""
Test script to verify single input functionality
"""

import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from enhanced_document_generator_fixed import DocumentGenerator

def test_single_input_functionality():
    """Test that the single input functionality works correctly"""
    print("Testing Single Input Functionality")
    print("=" * 35)
    
    # Create minimal sample data
    sample_data = {
        'title_data': {
            'Project Name': 'Test Project',
            'Contract No': 'TEST-001',
            'Work Order No': 'WO-001',
        },
        'work_order_data': pd.DataFrame([
            {
                'Item No.': '1',
                'Description': 'Test Item',
                'Unit': 'LS',
                'Quantity': 1,
                'Rate': 1000.00,
            }
        ]),
        'bill_quantity_data': pd.DataFrame([
            {
                'Item No.': '1',
                'Description': 'Test Item',
                'Unit': 'LS',
                'Quantity': 1,
                'Rate': 1000.00,
            }
        ]),
        'extra_items_data': pd.DataFrame()
    }
    
    try:
        # Initialize the document generator
        print("🔄 Initializing DocumentGenerator...")
        generator = DocumentGenerator(sample_data)
        print("✅ DocumentGenerator initialized successfully")
        
        # Test HTML document generation
        print("\n📄 Generating HTML documents...")
        html_documents = generator.generate_all_documents()
        print(f"✅ Generated {len(html_documents)} HTML documents")
        
        # Test PDF document generation
        print("\n🖨️  Generating PDF documents...")
        pdf_documents = generator.create_pdf_documents(html_documents)
        print(f"✅ Generated {len(pdf_documents)} PDF documents")
        
        # Test all formats generation
        print("\n🎯 Generating all document formats...")
        all_formats_result = generator.generate_all_formats_and_zip()
        print(f"✅ All formats generation completed")
        print(f"  - HTML documents: {len(all_formats_result.get('html_documents', {}))}")
        print(f"  - PDF documents: {len(all_formats_result.get('pdf_documents', {}))}")
        print(f"  - DOC documents: {len(all_formats_result.get('doc_documents', {}))}")
        
        # Check if we have the expected documents
        expected_docs = [
            'First Page Summary',
            'Deviation Statement', 
            'Final Bill Scrutiny Sheet',
            'Certificate II',
            'Certificate III'
        ]
        
        print(f"\n📋 Document verification:")
        for doc_name in expected_docs:
            html_found = any(doc_name in name for name in html_documents.keys())
            pdf_found = any(doc_name in name for name in pdf_documents.keys())
            print(f"  {doc_name}: HTML={'✅' if html_found else '❌'}, PDF={'✅' if pdf_found else '❌'}")
        
        print("\n🎉 Single input functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_single_input_functionality()
    sys.exit(0 if success else 1)