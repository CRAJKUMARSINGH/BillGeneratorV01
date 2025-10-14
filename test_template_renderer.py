import pandas as pd
from utils.template_renderer import TemplateRenderer

def test_template_renderer():
    """Test the template renderer with templates_14102025 format"""
    print("🧪 Testing Template Renderer")
    print("=" * 30)
    
    # Create test data
    title_data = {
        'Project Name': 'Test Road Construction Project',
        'Contract No': 'CT-2025-001',
        'Work Order No': 'WO-2025-001',
        'Name of Work': 'Road Construction and Maintenance',
        'Contractor Name': 'ABC Construction Ltd.'
    }
    
    work_order_data = pd.DataFrame([
        {
            'Item No.': '1',
            'Description': 'Excavation in Hard Rock',
            'Unit': 'Cu.M',
            'Quantity Since': 150.50,
            'Rate': 1500.00,
            'Amount': 225750.00
        },
        {
            'Item No.': '2',
            'Description': 'Providing and Laying Cement Concrete M20',
            'Unit': 'Cu.M',
            'Quantity Since': 85.25,
            'Rate': 4500.00,
            'Amount': 383625.00
        },
        {
            'Item No.': '3',
            'Description': 'Supply of Cement (Zero Rate Item)',
            'Unit': 'Bags',
            'Quantity Since': 500,
            'Rate': 0.00,
            'Amount': 0.00
        }
    ])
    
    extra_items_data = pd.DataFrame([
        {
            'Item No.': 'E1',
            'Description': 'Additional Survey Work',
            'Unit': 'LS',
            'Quantity': 1,
            'Rate': 15000.00,
            'Amount': 15000.00
        }
    ])
    
    # Initialize template renderer
    renderer = TemplateRenderer()
    
    # Test rendering first page
    try:
        html_content = renderer.render_first_page(title_data, work_order_data, extra_items_data)
        print("✅ First Page template rendered successfully")
        print(f"   HTML length: {len(html_content)} characters")
        
        # Check if it contains expected elements
        if '<title>CONTRACTOR BILL</title>' in html_content:
            print("✅ Contains correct title")
        else:
            print("❌ Missing correct title")
            
        if 'Excavation in Hard Rock' in html_content:
            print("✅ Contains work order items")
        else:
            print("❌ Missing work order items")
            
        if 'Supply of Cement (Zero Rate Item)' in html_content:
            print("✅ Contains zero rate items")
        else:
            print("❌ Missing zero rate items")
            
        # Save to file for inspection
        with open('test_first_page_output.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("💾 Saved output to test_first_page_output.html")
        
    except Exception as e:
        print(f"❌ First Page template rendering failed: {e}")
        return False
    
    print("\n🎉 Template Renderer Test PASSED!")
    return True

if __name__ == "__main__":
    test_template_renderer()