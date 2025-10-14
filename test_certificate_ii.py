import pandas as pd
from utils.template_renderer import TemplateRenderer
import os

def test_certificate_ii_template():
    """Test the certificate_ii template rendering"""
    
    # Sample title data
    title_data = {
        'Measurement Officer': 'Shri Rajesh Kumar',
        'Measurement Date': '15/10/2025',
        'Measurement Book Page': '45',
        'Measurement Book No': 'MB-2025-001',
        'Officer Name': 'Shri Arun Sharma',
        'Officer Designation': 'Assistant Executive Engineer',
        'Authorising Officer Name': 'Shri Deepak Verma',
        'Authorising Officer Designation': 'Executive Engineer'
    }
    
    # Sample work order data (not used for certificate but passed for consistency)
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
    
    # Sample extra items data (not used for certificate but passed for consistency)
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
        # Render the certificate_ii
        certificate_html = renderer.render_certificate_ii(
            title_data, work_order_data, extra_items_data
        )
        
        # Check that the HTML was generated
        assert len(certificate_html) > 0, "Certificate II HTML should not be empty"
        assert "<!DOCTYPE html>" in certificate_html, "Should contain DOCTYPE"
        assert "CERTIFICATE AND SIGNATURES" in certificate_html, "Should contain title"
        assert "Shri Rajesh Kumar" in certificate_html, "Should contain measurement officer name"
        assert "15/10/2025" in certificate_html, "Should contain measurement date"
        assert "MB-2025-001" in certificate_html, "Should contain measurement book number"
        assert "Shri Arun Sharma" in certificate_html, "Should contain officer name"
        assert "Assistant Executive Engineer" in certificate_html, "Should contain officer designation"
        assert "Shri Deepak Verma" in certificate_html, "Should contain authorising officer name"
        
        print("✅ Certificate II template rendering test passed")
        print(f"Generated HTML length: {len(certificate_html)} characters")
        print("Generated HTML preview:")
        print(certificate_html[:1000] + "..." if len(certificate_html) > 1000 else certificate_html)
        
        # Save to file for manual inspection
        with open("test_certificate_ii_output.html", "w", encoding="utf-8") as f:
            f.write(certificate_html)
        print("📄 Certificate II saved to test_certificate_ii_output.html for inspection")
        
        return True
        
    except Exception as e:
        print(f"❌ Certificate II template rendering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_certificate_ii_template()