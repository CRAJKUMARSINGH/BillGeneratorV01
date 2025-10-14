import pandas as pd
from utils.template_renderer import TemplateRenderer
from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def test_enhanced_generator_deviation():
    """Test the deviation statement generation through EnhancedDocumentGenerator"""
    
    # Sample data exactly as used in the real application
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
        'bill_quantity_data': pd.DataFrame([
            {
                'Item No.': '1',
                'Description': 'Electrical Wiring',
                'Unit': 'Meter',
                'Quantity': 110,
                'Rate': 50,
                'Remark': 'Additional wiring required'
            },
            {
                'Item No.': '2',
                'Description': 'Switch Board Installation',
                'Unit': 'Nos',
                'Quantity': 8,
                'Rate': 200,
                'Remark': 'Less switch boards installed'
            },
            {
                'Item No.': '3',
                'Description': 'Light Fitting',
                'Unit': 'Nos',
                'Quantity': 25,
                'Rate': 0,  # Zero rate item
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
    
    print("🔄 Testing EnhancedDocumentGenerator deviation statement generation...")
    
    try:
        # Initialize document generator
        generator = EnhancedDocumentGenerator(sample_data)
        
        # Test the deviation statement rendering directly
        print("🔄 Testing direct deviation statement rendering...")
        deviation_html = generator.template_renderer.render_deviation_statement(
            generator.title_data, generator.work_order_data, generator.extra_items_data
        )
        
        assert len(deviation_html) > 0, "Deviation statement HTML should not be empty"
        assert "<!DOCTYPE html>" in deviation_html, "Should contain DOCTYPE"
        assert "Deviation Statement" in deviation_html, "Should contain title"
        assert "ITEM No." in deviation_html, "Should contain table headers"
        
        print("✅ Direct deviation statement rendering successful")
        print(f"   Length: {len(deviation_html)} characters")
        
        # Test through the generate_all_documents method
        print("🔄 Testing through generate_all_documents method...")
        documents = generator.generate_all_documents()
        
        assert 'Deviation Statement' in documents, "Deviation Statement should be in generated documents"
        assert len(documents['Deviation Statement']) > 0, "Deviation Statement should not be empty"
        
        print("✅ Deviation Statement generated through generate_all_documents")
        print(f"   Length: {len(documents['Deviation Statement'])} characters")
        
        # Check content
        html_content = documents['Deviation Statement']
        assert '<!DOCTYPE html>' in html_content, "Should contain DOCTYPE"
        assert 'Deviation Statement' in html_content, "Should contain title"
        assert 'ITEM No.' in html_content, "Should contain table headers"
        assert 'Electrical Wiring' in html_content, "Should contain item descriptions"
        
        print("✅ Deviation Statement contains all expected elements")
        
        print("\n🎉 All tests passed! Deviation statement implementation is working correctly through EnhancedDocumentGenerator.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_enhanced_generator_deviation()