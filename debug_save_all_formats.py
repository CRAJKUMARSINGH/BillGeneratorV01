#!/usr/bin/env python3
"""
Debug script to test the save_all_formats functionality
"""

import pandas as pd
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def debug_save_all_formats():
    """Debug the save_all_formats functionality"""
    print("🔍 Debugging save_all_formats functionality")
    print("=" * 45)
    
    # Create sample data
    sample_data = {
        'title_data': {
            'Project Name': 'NH-XX Highway Improvement Project',
            'Contract No': 'NH-2025-789',
            'Work Order No': 'WO-2025-001',
            'Contractor Name': 'ABC Construction Ltd.',
            'Bill Number': 'BILL-2025-001',
            'Period From': '01/01/2025',
            'Period To': '31/03/2025'
        },
        'work_order_data': pd.DataFrame([
            {
                'Item No.': '1',
                'Description': 'Earthwork in excavation',
                'Unit': 'Cum',
                'Quantity': 150.50,
                'Rate': 600.00,
                'Amount': 90300.00,
                'Remark': 'As per drawings'
            },
            {
                'Item No.': '2',
                'Description': 'Providing and laying in position cement concrete M25',
                'Unit': 'Cum',
                'Quantity': 85.25,
                'Rate': 4500.00,
                'Amount': 383625.00,
                'Remark': 'Reinforced concrete'
            }
        ]),
        'bill_quantity_data': pd.DataFrame([
            {
                'Item No.': '1',
                'Description': 'Earthwork in excavation',
                'Unit': 'Cum',
                'Quantity': 150.50,
                'Rate': 600.00,
                'Amount': 90300.00
            },
            {
                'Item No.': '2',
                'Description': 'Providing and laying in position cement concrete M25',
                'Unit': 'Cum',
                'Quantity': 85.25,
                'Rate': 4500.00,
                'Amount': 383625.00
            }
        ]),
        'extra_items_data': pd.DataFrame([
            {
                'Item No.': 'E1',
                'Description': 'Additional Survey Work',
                'Unit': 'LS',
                'Quantity': 1,
                'Rate': 15000.00,
                'Amount': 15000.00,
                'Remark': 'Extra work'
            }
        ])
    }
    
    try:
        # Initialize the document generator
        print("🔄 Initializing EnhancedDocumentGenerator...")
        generator = EnhancedDocumentGenerator(sample_data)
        print("✅ EnhancedDocumentGenerator initialized successfully")
        
        # Test the generate_all_formats_and_zip method directly
        print("\n💾 Testing generate_all_formats_and_zip method...")
        result = generator.generate_all_formats_and_zip()
        print(f"Generate all formats result: {result}")
        print(f"Success: {result['success']}")
        if not result['success']:
            print(f"Error: {result['error']}")
            return False
            
        print(f"HTML documents count: {len(result['html_documents'])}")
        print(f"PDF documents count: {len(result['pdf_documents'])}")
        print(f"DOC documents count: {len(result['doc_documents'])}")
        
        # Print document names
        print("\nHTML Documents:")
        for name in result['html_documents'].keys():
            print(f"  - {name}")
            
        print("\nPDF Documents:")
        for name in result['pdf_documents'].keys():
            print(f"  - {name}")
            
        print("\nDOC Documents:")
        for name in result['doc_documents'].keys():
            print(f"  - {name}")
        
        # Test the save_all_formats method
        print("\n💾 Testing save_all_formats method...")
        output_dir = "debug_output_all_formats"
        success = generator.save_all_formats(output_dir)
        print(f"Save all formats result: {success}")
        
        return success
            
    except Exception as e:
        print(f"\n💥 Error during debug: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_save_all_formats()
    if success:
        print("\n🏆 Debug test completed successfully.")
        sys.exit(0)
    else:
        print("\n❌ Debug test failed!")
        sys.exit(1)