import pandas as pd
from utils.template_renderer import TemplateRenderer
import os
import traceback

def test_deviation_statement_template():
    """Test the deviation statement template rendering"""
    
    # Sample title data
    title_data = {
        'agreement_no': '48/2024-25',
        'name_of_work': 'Electric Repair and MTC work at Govt. Ambedkar hostel Ambamata, Govardhanvilas, Udaipur',
        'contractor_name': 'ABC Construction Company',
        'work_order_amount': '100000.00'
    }
    
    # Sample work order data
    work_order_data = pd.DataFrame([
        {
            'Item No.': '1',
            'Description': 'Electrical Wiring',
            'Unit': 'Meter',
            'Quantity': 100,
            'Rate': 50,
            'Quantity Billed': 110,
            'Remark': 'Additional wiring required'
        },
        {
            'Item No.': '2',
            'Description': 'Switch Board Installation',
            'Unit': 'Nos',
            'Quantity': 10,
            'Rate': 200,
            'Quantity Billed': 8,
            'Remark': 'Less switch boards installed'
        },
        {
            'Item No.': '3',
            'Description': 'Light Fitting',
            'Unit': 'Nos',
            'Quantity': 20,
            'Rate': 0,  # Zero rate item
            'Quantity Billed': 25,
            'Remark': 'Extra light fittings'
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
        }
    ])
    
    # Initialize template renderer
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    renderer = TemplateRenderer(template_dir)
    
    try:
        # Test the template directly
        template = renderer.jinja_env.get_template('deviation_statement.html')
        print("✅ Template loaded successfully")
        
        # Prepare test data exactly as the render method would
        header_data = [[], [], [], [], [], [], [], [], [], [], [], [], []]  # 13 rows
        header_data[12].extend(['', '', '', '', '48/2024-25'])
        header_data[8].extend(['', 'Electric Repair and MTC work at Govt. Ambedkar hostel Ambamata, Govardhanvilas, Udaipur'])
        
        items = [
            {
                'serial_no': '1',
                'description': 'Electrical Wiring',
                'unit': 'Meter',
                'qty_wo': '100.00',
                'rate': '50.00',
                'amt_wo': '5000.00',
                'qty_bill': '110.00',
                'amt_bill': '5500.00',
                'excess_qty': '10.00',
                'excess_amt': '500.00',
                'saving_qty': '',
                'saving_amt': '',
                'remark': 'Additional wiring required'
            }
        ]
        
        summary_data = {
            'work_order_total': '7000.00',
            'executed_total': '7100.00',
            'overall_excess': '100.00',
            'overall_saving': '0.00',
            'premium': {
                'percent': 0.10
            },
            'tender_premium_f': '700.00',
            'tender_premium_h': '710.00',
            'tender_premium_j': '10.00',
            'tender_premium_l': '0.00',
            'grand_total_f': '7700.00',
            'grand_total_h': '7810.00',
            'grand_total_j': '110.00',
            'grand_total_l': '0.00',
            'net_difference': '100.00'
        }
        
        template_data = {
            'header_data': header_data,
            'data': {
                'items': items,
                'summary': summary_data
            }
        }
        
        # Try to render the template
        deviation_html = template.render(**template_data)
        
        # Check that the HTML was generated
        assert len(deviation_html) > 0, "Deviation statement HTML should not be empty"
        assert "<!DOCTYPE html>" in deviation_html, "Should contain DOCTYPE"
        assert "Deviation Statement" in deviation_html, "Should contain title"
        assert "ITEM No." in deviation_html, "Should contain table headers"
        assert "Overall Excess With Respect to the Work Order Amount Rs." in deviation_html, "Should contain net difference text"
        
        print("✅ Deviation statement template rendering test passed")
        print(f"Generated HTML length: {len(deviation_html)} characters")
        
        # Save to file for manual inspection
        with open("test_deviation_statement_output.html", "w", encoding="utf-8") as f:
            f.write(deviation_html)
        print("📄 Deviation statement saved to test_deviation_statement_output.html for inspection")
        
        return True
        
    except Exception as e:
        print(f"❌ Deviation statement template rendering test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_deviation_statement_template()