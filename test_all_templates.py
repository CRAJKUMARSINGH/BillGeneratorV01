import pandas as pd
from utils.template_renderer import TemplateRenderer
import os

def test_all_templates():
    """Test all templates to ensure they're working correctly"""
    
    # Sample title data
    title_data = {
        'Measurement Officer': 'Shri Rajesh Kumar',
        'Measurement Date': '15/10/2025',
        'Measurement Book Page': '45',
        'Measurement Book No': 'MB-2025-001',
        'Officer Name': 'Shri Arun Sharma',
        'Officer Designation': 'Assistant Executive Engineer',
        'Authorising Officer Name': 'Shri Deepak Verma',
        'Authorising Officer Designation': 'Executive Engineer',
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
    
    templates_tested = []
    
    try:
        print("Testing Deviation Statement template...")
        deviation_html = renderer.render_deviation_statement(
            title_data, work_order_data, extra_items_data
        )
        assert len(deviation_html) > 0, "Deviation Statement HTML should not be empty"
        assert "<!DOCTYPE html>" in deviation_html, "Should contain DOCTYPE"
        assert "Deviation Statement" in deviation_html, "Should contain title"
        templates_tested.append("Deviation Statement")
        print("✅ Deviation Statement template test passed")
        
        print("Testing Extra Items template...")
        extra_items_html = renderer.render_extra_items(
            title_data, work_order_data, extra_items_data
        )
        assert len(extra_items_html) > 0, "Extra Items HTML should not be empty"
        assert "<!DOCTYPE html>" in extra_items_html, "Should contain DOCTYPE"
        assert "Extra Items" in extra_items_html, "Should contain title"
        templates_tested.append("Extra Items")
        print("✅ Extra Items template test passed")
        
        print("Testing Certificate II template...")
        certificate_ii_html = renderer.render_certificate_ii(
            title_data, work_order_data, extra_items_data
        )
        assert len(certificate_ii_html) > 0, "Certificate II HTML should not be empty"
        assert "<!DOCTYPE html>" in certificate_ii_html, "Should contain DOCTYPE"
        assert "CERTIFICATE AND SIGNATURES" in certificate_ii_html, "Should contain title"
        templates_tested.append("Certificate II")
        print("✅ Certificate II template test passed")
        
        print("Testing Certificate III template...")
        certificate_iii_html = renderer.render_certificate_iii(
            title_data, work_order_data, extra_items_data
        )
        assert len(certificate_iii_html) > 0, "Certificate III HTML should not be empty"
        assert "<!DOCTYPE html>" in certificate_iii_html, "Should contain DOCTYPE"
        assert "MEMORANDUM OF PAYMENTS" in certificate_iii_html, "Should contain title"
        templates_tested.append("Certificate III")
        print("✅ Certificate III template test passed")
        
        print(f"\n🎉 All templates tested successfully:")
        for template in templates_tested:
            print(f"  - {template}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_all_templates()