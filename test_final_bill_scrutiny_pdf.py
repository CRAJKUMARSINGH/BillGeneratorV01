#!/usr/bin/env python3
"""
Test script to generate and verify the final bill scrutiny sheet PDF output with proper margins
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.template_renderer import TemplateRenderer
from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def test_final_bill_scrutiny_pdf():
    """Test the final bill scrutiny sheet PDF generation with proper margins"""
    print("🔍 Testing Final Bill Scrutiny Sheet PDF Generation")
    print("=" * 60)
    
    # Create sample data for testing
    title_data = {
        'agreement_no': '48/2024-25',
        'name_of_work': 'Electric Repair and MTC work at Govt. Ambedkar hostel Ambamata, Govardhanvilas, Udaipur',
        'name_of_firm': 'M/s Seema Electrical Udaipur',
        'date_commencement': '01/01/2024',
        'date_completion': '30/06/2024',
        'actual_completion': '28/06/2024',
        'work_order_amount': '338573.00',
        'net_payable': '376561.00',
        'extra_items_sum': 0.0,
        'notes': [
            'Work completed as per schedule',
            'All measurements verified',
            'Quality as per specifications'
        ]
    }
    
    # Create a dummy DataFrame for work_order_data
    work_order_data = pd.DataFrame({
        'Item No.': ['1', '2', '3', '4', '5', '6', '7', '8'],
        'Description': [
            'Chargeable Head',
            'Agreement No.',
            'Adm. Section',
            'Tech. Section',
            'M.B No.',
            'Name of Sub Dn',
            'Name of Work',
            'Name of Firm'
        ],
        'Unit': ['Nos', 'Nos', 'Nos', 'Nos', 'Nos', 'Nos', 'Nos', 'Nos'],
        'Quantity': [1, 1, 1, 1, 1, 1, 1, 1],
        'Rate': [100.0, 200.0, 150.0, 120.0, 110.0, 130.0, 140.0, 160.0],
        'Amount': [100.0, 200.0, 150.0, 120.0, 110.0, 130.0, 140.0, 160.0]
    })
    
    try:
        # Create a TemplateRenderer instance
        template_renderer = TemplateRenderer()
        
        # Render the note sheet template to HTML
        html_output = template_renderer.render_note_sheet(title_data, work_order_data)
        
        # Save HTML for inspection
        html_file = project_root / "test_final_bill_scrutiny_output.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        print(f"✅ HTML output saved to: {html_file}")
        
        # Check if the template contains the correct margin settings
        if '@page { size: A4; margin: 15mm 10mm; }' in html_output:
            print("✅ Page margins correctly set to 15mm top/bottom, 10mm left/right")
        else:
            print("❌ Page margins not found or incorrect")
            return False
            
        # Check if the template contains the correct column widths
        if ('width: 10mm;' in html_output and 
            'width: 80mm;' in html_output and 
            'width: 90mm;' in html_output):
            print("✅ Column widths correctly set to 10mm, 80mm, and 90mm")
        else:
            print("❌ Column widths not found or incorrect")
            return False
            
        # Generate PDF using EnhancedDocumentGenerator
        # Create the required data structure
        data = {
            'title_data': title_data,
            'work_order_data': work_order_data,
            'extra_items_data': pd.DataFrame()  # Empty DataFrame for extra items
        }
        
        generator = EnhancedDocumentGenerator(data)
        
        # Create output directory if it doesn't exist
        output_dir = project_root / "test_outputs"
        output_dir.mkdir(exist_ok=True)
        
        # Generate PDF
        pdf_file = output_dir / "final_bill_scrutiny_test.pdf"
        success = generator._generate_pdf_reportlab(html_output, str(pdf_file))
        
        if success and pdf_file.exists():
            file_size = pdf_file.stat().st_size
            print(f"✅ PDF generated successfully: {pdf_file}")
            print(f"📄 PDF file size: {file_size} bytes")
            
            # Verify file is not empty
            if file_size > 0:
                print("✅ PDF file is not empty")
                return True
            else:
                print("❌ PDF file is empty")
                return False
        else:
            print("❌ Failed to generate PDF")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_final_bill_scrutiny_pdf()
    if success:
        print("\n🎉 Final Bill Scrutiny Sheet PDF test passed!")
        sys.exit(0)
    else:
        print("\n💥 Final Bill Scrutiny Sheet PDF test failed!")
        sys.exit(1)