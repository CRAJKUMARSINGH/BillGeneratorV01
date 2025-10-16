#!/usr/bin/env python3
"""
Test script to verify the save_all_formats functionality
"""

import pandas as pd
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def test_save_all_formats():
    """Test the save_all_formats functionality"""
    print("🔍 Testing save_all_formats functionality")
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
        
        # Test the save_all_formats method
        print("\n💾 Testing save_all_formats method...")
        output_dir = "test_output_all_formats"
        success = generator.save_all_formats(output_dir)
        print(f"Save all formats result: {success}")
        
        if success:
            print("\n🎉 save_all_formats test PASSED!")
            print(f"✅ All documents saved to: {output_dir}")
            
            # Check if directories were created
            html_dir = Path(output_dir) / "html"
            pdf_dir = Path(output_dir) / "pdf"
            doc_dir = Path(output_dir) / "doc"
            
            if html_dir.exists():
                print(f"✅ HTML directory created: {html_dir}")
                html_files = list(html_dir.glob("*.html"))
                print(f"📄 HTML files generated: {len(html_files)}")
                for file in html_files:
                    print(f"   - {file.name}")
            else:
                print(f"❌ HTML directory not created: {html_dir}")
            
            if pdf_dir.exists():
                print(f"✅ PDF directory created: {pdf_dir}")
                pdf_files = list(pdf_dir.glob("*.pdf"))
                print(f"🖨️  PDF files generated: {len(pdf_files)}")
                for file in pdf_files:
                    print(f"   - {file.name}")
            else:
                print(f"❌ PDF directory not created: {pdf_dir}")
            
            if doc_dir.exists():
                print(f"✅ DOC directory created: {doc_dir}")
                doc_files = list(doc_dir.glob("*.docx"))
                print(f"📝 DOC files generated: {len(doc_files)}")
                for file in doc_files:
                    print(f"   - {file.name}")
            else:
                print(f"❌ DOC directory not created: {doc_dir}")
            
            # Check for ZIP file
            zip_file = Path(output_dir) / "All_Documents.zip"
            if zip_file.exists():
                size = zip_file.stat().st_size
                print(f"📦 ZIP package created: {zip_file} ({size} bytes)")
            else:
                print(f"❌ ZIP package not created: {zip_file}")
            
            return True
        else:
            print("\n💥 save_all_formats test FAILED!")
            return False
            
    except Exception as e:
        print(f"\n💥 Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_save_all_formats()
    if success:
        print("\n🏆 All tests passed! save_all_formats functionality is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)