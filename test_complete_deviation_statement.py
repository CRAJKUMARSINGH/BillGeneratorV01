import pandas as pd
from utils.template_renderer import TemplateRenderer
from enhanced_document_generator_fixed import EnhancedDocumentGenerator
import os

def test_complete_deviation_statement():
    """Test the complete deviation statement generation including PDF conversion"""
    
    # Sample data
    sample_data = {
        'title_data': {
            'agreement_no': '48/2024-25',
            'name_of_work': 'Electric Repair and MTC work at Govt. Ambedkar hostel Ambamata, Govardhanvilas, Udaipur',
            'contractor_name': 'ABC Construction Company',
            'work_order_amount': '100000.00'
        },
        'work_order_data': pd.DataFrame([
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
        ]),
        'extra_items_data': pd.DataFrame([
            {
                'Item No.': 'E1',
                'Description': 'Emergency Repairs',
                'Unit': 'Lot',
                'Quantity': 1,
                'Rate': 5000,
                'Remark': 'Urgent repair work'
            }
        ])
    }
    
    print("🔄 Testing complete document generation with deviation statement...")
    
    try:
        # Initialize document generator
        generator = EnhancedDocumentGenerator(sample_data)
        
        # Generate all documents
        documents = generator.generate_all_documents()
        
        # Check that deviation statement was generated
        assert 'Deviation Statement' in documents, "Deviation Statement should be in generated documents"
        assert len(documents['Deviation Statement']) > 0, "Deviation Statement should not be empty"
        
        print("✅ Deviation Statement generated successfully")
        print(f"   Length: {len(documents['Deviation Statement'])} characters")
        
        # Check that it contains expected elements
        html_content = documents['Deviation Statement']
        assert '<!DOCTYPE html>' in html_content, "Should contain DOCTYPE"
        assert 'Deviation Statement' in html_content, "Should contain title"
        assert 'ITEM No.' in html_content, "Should contain table headers"
        assert 'Electrical Wiring' in html_content, "Should contain item descriptions"
        assert 'Overall Excess With Respect to the Work Order Amount Rs.' in html_content, "Should contain net difference text"
        
        print("✅ Deviation Statement contains all expected elements")
        
        # Test PDF generation for deviation statement
        print("🔄 Testing PDF generation for deviation statement...")
        
        # Create PDF documents
        pdf_documents = generator.create_pdf_documents(documents)
        
        # Check that deviation statement PDF was generated
        deviation_pdf_name = 'Deviation Statement.pdf'
        assert deviation_pdf_name in pdf_documents, f"{deviation_pdf_name} should be in generated PDFs"
        assert len(pdf_documents[deviation_pdf_name]) > 100, "Deviation Statement PDF should not be empty"
        
        print("✅ Deviation Statement PDF generated successfully")
        print(f"   Size: {len(pdf_documents[deviation_pdf_name])} bytes")
        
        # Save PDF for inspection
        with open("test_deviation_statement.pdf", "wb") as f:
            f.write(pdf_documents[deviation_pdf_name])
        print("📄 Deviation Statement PDF saved to test_deviation_statement.pdf for inspection")
        
        print("\n🎉 All tests passed! Deviation statement implementation is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_complete_deviation_statement()