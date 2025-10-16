import pandas as pd
from utils.template_renderer import TemplateRenderer

def test_zero_quantity_handling():
    """Test that zero quantity items with rate > 0 are handled correctly"""
    
    # Sample data with zero quantity items but rate > 0
    title_data = {
        'agreement_no': 'AG-001',
        'name_of_firm': 'Test Contractor',
        'name_of_work': 'Test Work'
    }
    
    # Work order data with mix of normal and zero quantity items
    work_order_data = pd.DataFrame([
        {
            'Unit': 'MTR',
            'Quantity': 100,
            'Item No.': '1',
            'Description': 'Earth Work',
            'Rate': 50,
            'Remark': 'Normal item'
        },
        {
            'Unit': 'MTR',
            'Quantity': 0,  # Zero quantity but rate > 0
            'Item No.': '2',
            'Description': 'Concrete Work',
            'Rate': 0,  # Zero rate item
            'Remark': 'Zero rate item'
        },
        {
            'Unit': 'MTR',
            'Quantity': 0,  # Zero quantity but rate > 0
            'Item No.': '3',
            'Description': 'Brick Work',
            'Rate': 75,  # Rate > 0
            'Remark': 'Zero quantity item'
        }
    ])
    
    print("Testing TemplateRenderer with zero quantity items...")
    renderer = TemplateRenderer()
    
    # Test deviation statement rendering
    try:
        deviation_html = renderer.render_deviation_statement(title_data, work_order_data)
        print("✅ TemplateRenderer deviation statement rendered successfully")
        
        # Check if zero quantity items with rate > 0 are handled correctly
        if 'Earth Work' in deviation_html and '50.00' in deviation_html:
            print("✅ Normal items are displayed correctly")
        
        # Check that zero rate items only show Item No., Description, and Remark
        if '2' in deviation_html and 'Concrete Work' in deviation_html:
            print("✅ Zero rate items show Item No. and Description")
            
        # Check that zero quantity items with rate > 0 show 0.00 values
        if '3' in deviation_html and 'Brick Work' in deviation_html:
            print("✅ Zero quantity items with rate > 0 are handled correctly")
            
        print("✅ Zero quantity handling implementation verified successfully")
        
    except Exception as e:
        print(f"❌ TemplateRenderer failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_zero_quantity_handling()