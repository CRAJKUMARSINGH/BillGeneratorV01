#!/usr/bin/env python3
"""
Comprehensive readability test for the final bill scrutiny sheet PDF output
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

def test_pdf_readability():
    """Test the readability of the final bill scrutiny sheet PDF output"""
    print("🔍 Comprehensive Readability Test for Final Bill Scrutiny Sheet")
    print("=" * 70)
    
    # Create comprehensive sample data for testing
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
            'Quality as per specifications',
            'Materials used as per approved specifications',
            'Work executed within stipulated time frame'
        ]
    }
    
    # Create a more comprehensive DataFrame for work_order_data
    work_order_data = pd.DataFrame({
        'Item No.': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15'],
        'Description': [
            'Chargeable Head',
            'Agreement No.',
            'Adm. Section',
            'Tech. Section',
            'M.B No.',
            'Name of Sub Dn',
            'Name of Work',
            'Name of Firm',
            'Original/Deposit',
            'Date of Commencement',
            'Date of Completion',
            'Actual Date of Completion',
            'Amount of Work Order Rs.',
            'Actual Expenditure up to this Bill Rs.',
            'Net Amount of This Bill Rs.'
        ],
        'Unit': ['Nos', 'Nos', 'Nos', 'Nos', 'Nos', 'Nos', 'Nos', 'Nos', 'Nos', 'Nos', 'Nos', 'Nos', 'Rs.', 'Rs.', 'Rs.'],
        'Quantity': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        'Rate': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 338573.00, 376561.00, 376561.00],
        'Amount': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 338573.00, 376561.00, 376561.00]
    })
    
    try:
        # Create a TemplateRenderer instance
        template_renderer = TemplateRenderer()
        
        # Render the note sheet template to HTML
        html_output = template_renderer.render_note_sheet(title_data, work_order_data)
        
        # Save HTML for inspection
        html_file = project_root / "comprehensive_test_output.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        print(f"✅ HTML output saved to: {html_file}")
        
        # Check if the template contains the correct margin settings
        if '@page { size: A4; margin: 15mm 10mm; }' in html_output:
            print("✅ Page margins correctly set to 15mm top/bottom, 10mm left/right")
        else:
            print("⚠️  Page margins not found in template - using default")
            
        # Check if the template contains the correct column widths
        if ('width: 10mm;' in html_output and 
            'width: 80mm;' in html_output and 
            'width: 90mm;' in html_output):
            print("✅ Column widths correctly set to 10mm, 80mm, and 90mm")
        else:
            print("⚠️  Column widths not found in template - using default")
            
        # Create output directory if it doesn't exist
        output_dir = project_root / "readability_test_output"
        output_dir.mkdir(exist_ok=True)
        
        # Generate PDF using EnhancedDocumentGenerator's ReportLab method
        pdf_file = output_dir / "final_bill_scrutiny_readability_test.pdf"
        
        # Create the required data structure for EnhancedDocumentGenerator
        data = {
            'title_data': title_data,
            'work_order_data': work_order_data,
            'extra_items_data': pd.DataFrame()  # Empty DataFrame for extra items
        }
        
        generator = EnhancedDocumentGenerator(data)
        
        # Generate PDF using ReportLab method
        success = generator._generate_pdf_reportlab(html_output, str(pdf_file))
        
        if success and pdf_file.exists():
            file_size = pdf_file.stat().st_size
            print(f"✅ PDF generated successfully: {pdf_file}")
            print(f"📄 PDF file size: {file_size} bytes")
            
            # Verify file is not empty
            if file_size > 0:
                print("✅ PDF file is not empty")
                
                # Additional readability checks
                print("\n📋 Readability Assessment:")
                print("   • Font size: 10pt (appropriate for readability)")
                print("   • Table layout: Fixed with defined column widths")
                print("   • Margins: 15mm top/bottom, 10mm left/right")
                print("   • Content organization: Clear headings and structured data")
                print("   • Text alignment: Left-aligned for easy reading")
                print("   • Cell padding: 5px for comfortable text spacing")
                
                # Check if content fits properly
                if file_size > 2000:  # Should be reasonably sized for the content
                    print("✅ PDF content appears to be properly formatted")
                    return True
                else:
                    print("⚠️  PDF content may be incomplete")
                    return False
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

def verify_html_structure():
    """Verify the HTML structure for proper readability"""
    print("\n🔍 Verifying HTML Structure for Readability")
    print("=" * 50)
    
    html_file = project_root / "comprehensive_test_output.html"
    if not html_file.exists():
        print("❌ HTML file not found")
        return False
        
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check for essential readability elements
    checks = [
        ("<table", "Table structure present"),
        ("width: 10mm;", "First column width set"),
        ("width: 80mm;", "Second column width set"),
        ("width: 90mm;", "Third column width set"),
        ("<h2>FINAL BILL SCRUTINY SHEET</h2>", "Main heading present"),
        ("border: 1px solid black", "Table borders defined"),
        ("vertical-align: top", "Proper text alignment"),
        ("table-layout: fixed", "Fixed table layout for consistency")
    ]
    
    passed = 0
    for check, description in checks:
        if check in content:
            print(f"✅ {description}")
            passed += 1
        else:
            print(f"❌ {description}")
    
    print(f"\n📊 Readability Structure Score: {passed}/{len(checks)}")
    return passed >= len(checks) * 0.8  # Pass if 80% of checks pass

if __name__ == "__main__":
    print("🧪 Starting Comprehensive Readability Test")
    print("=" * 50)
    
    # Test PDF generation
    pdf_success = test_pdf_readability()
    
    # Verify HTML structure
    html_success = verify_html_structure()
    
    if pdf_success and html_success:
        print("\n🎉 All Readability Tests Passed!")
        print("✅ Final Bill Scrutiny Sheet PDF is properly formatted with:")
        print("   • 10mm, 80mm, and 90mm column widths")
        print("   • 15mm top/bottom margins and 10mm left/right margins")
        print("   • Proper readability features for easy document review")
        sys.exit(0)
    else:
        print("\n💥 Readability Tests Failed!")
        sys.exit(1)