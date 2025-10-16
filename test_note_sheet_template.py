import pandas as pd
from enhanced_document_generator_fixed import DocumentGenerator

def test_note_sheet_template():
    """Test that final bill scrutiny sheet uses the note_sheet template correctly"""
    
    # Sample data
    title_data = {
        'agreement_no': 'AG-001',
        'name_of_work': 'Test Work',
        'name_of_firm': 'Test Contractor',
        'date_commencement': '01/01/2024',
        'date_completion': '31/12/2024',
        'actual_completion': '31/12/2024',
        'work_order_amount': '100000.00',
        'net_payable': '90000.00',
        'extra_items_sum': 5000.00
    }
    
    work_order_data = pd.DataFrame([
        {
            'Unit': 'MTR',
            'Quantity Since': 100,
            'Quantity Upto': 100,
            'Item No.': '1',
            'Description': 'Earth Work',
            'Rate': 50,
            'Remark': 'Regular item'
        }
    ])
    
    extra_items_data = pd.DataFrame([
        {
            'Unit': 'LS',
            'Quantity': 1,
            'Item No.': 'E1',
            'Description': 'Extra Work',
            'Rate': 5000,
            'Remark': 'Extra item'
        }
    ])
    
    # Create document generator
    data = {
        'title_data': title_data,
        'work_order_data': work_order_data,
        'bill_quantity_data': work_order_data,  # Using same data for simplicity
        'extra_items_data': extra_items_data
    }
    
    generator = DocumentGenerator(data)
    
    print("Testing Note Sheet template rendering...")
    
    try:
        # Render note_sheet template
        note_sheet_html = generator._render_template('note_sheet.html')
        print("✅ Note Sheet template rendered successfully")
        
        # Check that it contains the correct structure
        if 'BILL SCRUTINY SHEET' in note_sheet_html:
            print("✅ Contains correct header")
        else:
            print("❌ Missing correct header")
            
        if 'Agreement No.' in note_sheet_html and 'Name of Work' in note_sheet_html:
            print("✅ Contains correct data fields")
        else:
            print("❌ Missing correct data fields")
            
        if 'Test Work' in note_sheet_html and 'Test Contractor' in note_sheet_html:
            print("✅ Contains correct data values")
        else:
            print("❌ Missing correct data values")
            
        print("✅ Note Sheet template verification completed")
        
    except Exception as e:
        print(f"❌ Error rendering Note Sheet template: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_note_sheet_template()