#!/usr/bin/env python3
"""
Test script to verify PDF column width handling
"""

import pandas as pd
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def test_pdf_column_widths():
    """Test PDF generation with column widths"""
    print("🔍 Testing PDF column width handling")
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
        
        # Generate HTML documents
        print("\n📄 Generating HTML documents...")
        html_documents = generator.generate_all_documents()
        print(f"✅ Generated {len(html_documents)} HTML documents")
        
        # Check if First Page has column widths
        first_page_html = html_documents.get('First Page Summary', '')
        if 'width:' in first_page_html:
            print("✅ First Page template has column widths")
        else:
            print("❌ First Page template missing column widths")
        
        # Generate PDF using ReportLab
        print("\n🖨️  Generating PDF with ReportLab...")
        temp_pdf_path = "test_column_widths.pdf"
        success = generator._generate_pdf_reportlab(first_page_html, temp_pdf_path)
        
        if success:
            print("✅ PDF generated successfully with ReportLab")
            # Check if file was created
            pdf_path = Path(temp_pdf_path)
            if pdf_path.exists():
                size = pdf_path.stat().st_size
                print(f"📄 PDF file created: {temp_pdf_path} ({size} bytes)")
                # Clean up
                pdf_path.unlink()
                print("🧹 Cleaned up test file")
            else:
                print("❌ PDF file was not created")
        else:
            print("❌ PDF generation failed")
            
        return success
            
    except Exception as e:
        print(f"\n💥 Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_column_widths()
    if success:
        print("\n🏆 PDF column width test completed successfully.")
        sys.exit(0)
    else:
        print("\n❌ PDF column width test failed!")
        sys.exit(1)