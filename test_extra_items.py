import pandas as pd
from utils.template_renderer import TemplateRenderer
import os

def test_extra_items_template():
    """Test the extra items template rendering"""
    
    # Sample title data
    title_data = {
        'agreement_no': '48/2024-25',
        'name_of_work': 'Electric Repair and MTC work at Govt. Ambedkar hostel Ambamata, Govardhanvilas, Udaipur',
        'contractor_name': 'ABC Construction Company',
        'work_order_amount': '100000.00'
    }
    
    # Sample work order data (not used for extra items but passed for consistency)
    work_order_data = pd.DataFrame([
        {
            'Item No.': '1',
            'Description': 'Electrical Wiring',
            'Unit': 'Meter',
            'Quantity': 100,
            'Rate': 50,
            'Remark': 'Standard electrical work'
        }
    ])
    
    # Sample extra items data
    extra_items_data = pd.DataFrame([
        {
            'Item No.': 'E1',
            'Description': 'Emergency Repairs',
            'Unit': 'Lot',
            'Quantity': 1,
            'Rate': 5000,
            'Remark': 'Urgent repair work'
        },
        {
            'Item No.': 'E2',
            'Description': 'Additional Light Fittings',
            'Unit': 'Nos',
            'Quantity': 5,
            'Rate': 200,
            'Remark': 'Extra light fittings as per client request'
        }
    ])
    
    # Initialize template renderer
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    renderer = TemplateRenderer(template_dir)
    
    try:
        # Render the extra items using the specialized method
        print("🔄 Testing render_extra_items method...")
        extra_items_html = renderer.render_extra_items(
            title_data, work_order_data, extra_items_data
        )
        
        # Check that the HTML was generated
        assert len(extra_items_html) > 0, "Extra items HTML should not be empty"
        assert "<!DOCTYPE html>" in extra_items_html, "Should contain DOCTYPE"
        assert "Extra Items" in extra_items_html, "Should contain title"
        assert "Serial No." in extra_items_html, "Should contain table headers"
        assert "Emergency Repairs" in extra_items_html, "Should contain item descriptions"
        assert "E1" in extra_items_html, "Should contain serial numbers"
        assert "5000.00" in extra_items_html, "Should contain amounts"
        
        print("✅ Extra items template rendering test passed")
        print(f"Generated HTML length: {len(extra_items_html)} characters")
        print("Generated HTML preview:")
        print(extra_items_html[:1000] + "..." if len(extra_items_html) > 1000 else extra_items_html)
        
        # Save to file for manual inspection
        with open("test_extra_items_output.html", "w", encoding="utf-8") as f:
            f.write(extra_items_html)
        print("📄 Extra items saved to test_extra_items_output.html for inspection")
        
        return True
        
    except Exception as e:
        print(f"❌ Extra items template rendering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_extra_items_template()