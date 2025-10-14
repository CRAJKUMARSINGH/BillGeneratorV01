import pandas as pd
from enhanced_document_generator_fixed import EnhancedDocumentGenerator
import tempfile
import os

def test_bill_scrutiny_sheet():
    """Test that the Bill Scrutiny Sheet template works correctly"""
    print("🧪 Testing Bill Scrutiny Sheet Template")
    print("=" * 40)
    
    # Create test data that matches the template requirements
    title_data = {
        'Project Name': 'NH-XX Highway Improvement Project',
        'Contract No': 'NH-2025-789',
        'Work Order No': 'WO-2025-456',
        'Name of Work': 'Four-laning of NH-XX from Km. 50 to Km. 75',
        'Contractor Name': 'National Highway Constructors Pvt. Ltd.',
        'agreement_no': 'NH-2025-789',
        'name_of_work': 'Four-laning of NH-XX from Km. 50 to Km. 75',
        'name_of_firm': 'National Highway Constructors Pvt. Ltd.',
        'date_commencement': '01/01/2025',
        'date_completion': '31/12/2025',
        'actual_completion': '25/11/2025'
    }
    
    work_order_data = pd.DataFrame([
        {
            'Item No.': '1.1',
            'Description': 'Earthwork in excavation',
            'Unit': 'Cu.M',
            'Quantity Since': 2500.00,
            'Rate': 180.00,
            'Amount': 450000.00
        },
        {
            'Item No.': '1.2',
            'Description': 'Cement concrete M25',
            'Unit': 'Sq.M',
            'Quantity Since': 1200.00,
            'Rate': 850.00,
            'Amount': 1020000.00
        }
    ])
    
    extra_items_data = pd.DataFrame([
        {
            'Item No.': 'E1',
            'Description': 'Additional earthwork',
            'Unit': 'Cu.M',
            'Quantity': 150.00,
            'Rate': 200.00,
            'Amount': 30000.00
        }
    ])
    
    # Create data structure
    test_data = {
        'title_data': title_data,
        'work_order_data': work_order_data,
        'bill_quantity_data': work_order_data.copy(),
        'extra_items_data': extra_items_data
    }
    
    # Initialize document generator
    print("🔄 Initializing EnhancedDocumentGenerator...")
    generator = EnhancedDocumentGenerator(test_data)
    
    # Generate HTML documents
    print("📄 Generating HTML documents...")
    html_documents = generator.generate_all_documents()
    
    if not html_documents:
        print("❌ Failed to generate HTML documents")
        return False
    
    print(f"✅ Generated {len(html_documents)} HTML documents")
    
    # Check if Bill Scrutiny Sheet is generated
    if 'Final Bill Scrutiny Sheet' not in html_documents:
        print("❌ Bill Scrutiny Sheet not found in generated documents")
        return False
    
    bill_scrutiny_sheet = html_documents['Final Bill Scrutiny Sheet']
    
    # Check for required elements
    required_elements = [
        '<!DOCTYPE html>',
        '<title>Note Sheet</title>',
        '________ BILL SCRUTINY SHEET',
        'Running/ & Final Bill Agreement No.',
        'Chargeable Head',
        'Agreement No.',
        'Name of Work',
        'Name of Firm',
        'Amount of Work Order Rs.',
        'Actual Expenditure up to this Bill Rs.',
        'Extra Item',
        'Deductions:-',
        'S.D.II',
        'I.T.',
        'GST',
        'L.C.'
    ]
    
    passed_checks = 0
    for element in required_elements:
        if element in bill_scrutiny_sheet:
            print(f"✅ Found: {element}")
            passed_checks += 1
        else:
            print(f"❌ Missing: {element}")
    
    print(f"\n📊 Template Compliance: {passed_checks}/{len(required_elements)} checks passed")
    
    # Check for proper data rendering
    if 'NH-2025-789' in bill_scrutiny_sheet:
        print("✅ Agreement No. rendered correctly")
    else:
        print("❌ Agreement No. not rendered")
    
    if 'Four-laning of NH-XX' in bill_scrutiny_sheet:
        print("✅ Name of Work rendered correctly")
    else:
        print("❌ Name of Work not rendered")
    
    # Generate PDF
    print("\n🖨️  Generating PDF documents...")
    pdf_documents = generator.create_pdf_documents(html_documents)
    
    if not pdf_documents:
        print("❌ Failed to create PDF documents")
        return False
    
    print("✅ PDF documents generated successfully")
    
    # Check if Bill Scrutiny Sheet PDF exists
    bill_scrutiny_pdf_name = 'Final Bill Scrutiny Sheet.pdf'
    if bill_scrutiny_pdf_name in pdf_documents:
        pdf_size = len(pdf_documents[bill_scrutiny_pdf_name])
        print(f"✅ {bill_scrutiny_pdf_name}: {pdf_size} bytes")
    else:
        print(f"❌ {bill_scrutiny_pdf_name} not found in PDF documents")
        return False
    
    # Save for inspection
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save HTML for inspection
        html_path = os.path.join(temp_dir, 'bill_scrutiny_sheet.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(bill_scrutiny_sheet)
        print(f"\n💾 Bill Scrutiny Sheet HTML saved to: {html_path}")
        
        # Save PDF for inspection
        pdf_path = os.path.join(temp_dir, bill_scrutiny_pdf_name)
        with open(pdf_path, 'wb') as f:
            f.write(pdf_documents[bill_scrutiny_pdf_name])
        print(f"💾 Bill Scrutiny Sheet PDF saved to: {pdf_path}")
    
    print(f"\n🎉 BILL SCRUTINY SHEET TEST PASSED!")
    return True

if __name__ == "__main__":
    success = test_bill_scrutiny_sheet()
    if not success:
        print(f"\n💥 BILL SCRUTINY SHEET TEST FAILED!")
        exit(1)