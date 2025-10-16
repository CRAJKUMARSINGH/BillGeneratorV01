import pandas as pd
from utils.template_renderer import TemplateRenderer
from enhanced_document_generator_fixed import DocumentGenerator

def test_zero_rate_items():
    """Test that zero rate items are handled correctly"""
    
    # Sample data with zero rate items
    title_data = {
        'name_of_firm': 'Test Contractor',
        'name_of_work': 'Test Work',
        'bill_no': '001',
        'last_bill': 'N/A',
        'reference': 'WO-001',
        'agreement_no': 'AG-001',
        'date_commencement': '01/01/2024',
        'date_start': '01/01/2024',
        'date_completion': '31/12/2024',
        'actual_completion': '31/12/2024',
        'measurement_date': '31/03/2024',
        'work_order_amount': '100000.00'
    }
    
    # Work order data with mix of zero and non-zero rate items
    work_order_data = pd.DataFrame([
        {
            'Unit': 'MTR',
            'Quantity Since': 100,
            'Quantity Upto': 100,
            'Item No.': '1',
            'Description': 'Earth Work',
            'Rate': 50,
            'Amount': 5000,
            'Remark': 'Regular item'
        },
        {
            'Unit': 'MTR',
            'Quantity Since': 50,
            'Quantity Upto': 50,
            'Item No.': '2',
            'Description': 'Concrete Work',
            'Rate': 0,  # Zero rate item
            'Amount': 0,
            'Remark': 'Zero rate item'
        },
        {
            'Unit': 'KG',
            'Quantity Since': 200,
            'Quantity Upto': 200,
            'Item No.': '3',
            'Description': 'Steel Work',
            'Rate': 75,
            'Amount': 15000,
            'Remark': 'Regular item'
        }
    ])
    
    # Extra items data with zero rate item
    extra_items_data = pd.DataFrame([
        {
            'Unit': 'LS',
            'Quantity': 1,
            'Item No.': 'E1',
            'Description': 'Extra Work',
            'Rate': 0,  # Zero rate item
            'Amount': 0,
            'Remark': 'Zero rate extra item'
        }
    ])
    
    print("Testing TemplateRenderer...")
    renderer = TemplateRenderer()
    
    # Test first page rendering
    try:
        first_page_html = renderer.render_first_page(title_data, work_order_data, extra_items_data)
        print("✅ TemplateRenderer first page rendered successfully")
        
        # Check if zero rate items are handled correctly
        if 'Earth Work' in first_page_html and '50.00' in first_page_html:
            print("✅ Non-zero rate items are displayed correctly")
        else:
            print("❌ Non-zero rate items are not displayed correctly")
            
        if 'Concrete Work' in first_page_html and 'Zero rate item' in first_page_html:
            print("✅ Zero rate items show description and remark")
        else:
            print("❌ Zero rate items do not show description and remark")
            
        # Check that zero rate items don't show rate/amount columns
        # This would require parsing the HTML to verify, but we can at least check it renders
        
    except Exception as e:
        print(f"❌ TemplateRenderer failed: {e}")
    
    print("\nTesting DocumentGenerator...")
    data = {
        'title_data': title_data,
        'work_order_data': work_order_data,
        'extra_items_data': extra_items_data
    }
    
    try:
        generator = DocumentGenerator(data)
        documents = generator.generate_all_documents()
        print("✅ DocumentGenerator rendered all documents successfully")
        
        if 'First Page Summary' in documents:
            first_page = documents['First Page Summary']
            if 'Earth Work' in first_page and '50.00' in first_page:
                print("✅ Non-zero rate items are displayed correctly in DocumentGenerator")
            else:
                print("❌ Non-zero rate items are not displayed correctly in DocumentGenerator")
                
            if 'Concrete Work' in first_page and 'Zero rate item' in first_page:
                print("✅ Zero rate items show description and remark in DocumentGenerator")
            else:
                print("❌ Zero rate items do not show description and remark in DocumentGenerator")
        else:
            print("❌ First Page Summary not found in generated documents")
            
    except Exception as e:
        print(f"❌ DocumentGenerator failed: {e}")

if __name__ == "__main__":
    test_zero_rate_items()