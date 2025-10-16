#!/usr/bin/env python3
"""
Simple test script to verify PDF and DOC generation
"""

import pandas as pd
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from enhanced_document_generator_fixed import DocumentGenerator

def simple_test():
    """Simple test of document generation"""
    print("🔍 Simple test of document generation")
    print("=" * 40)
    
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
        
        # Test document generation
        print("\n📄 Testing document generation...")
        documents = generator.generate_all_documents()
        print(f"Generated {len(documents)} documents")
        
        for name in documents.keys():
            print(f"  - {name}")
        
        # Test PDF generation
        print("\n🖨️  Testing PDF generation...")
        pdf_docs = generator.create_pdf_documents(documents)
        print(f"Generated {len(pdf_docs)} PDF documents")
        
        for name in pdf_docs.keys():
            print(f"  - {name}")
        
        # Test saving all formats
        print("\n💾 Testing save_all_formats...")
        success = generator.save_all_formats("simple_test_output")
        print(f"Save result: {success}")
        
        if success:
            print("\n✅ Test completed successfully!")
            return True
        else:
            print("\n❌ Test failed!")
            return False
            
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simple_test()
    sys.exit(0 if success else 1)