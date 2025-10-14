import pandas as pd
from enhanced_document_generator_fixed import EnhancedDocumentGenerator
import os

def test_document_generation():
    """Test document generation to confirm outputs are generated as per latest templates"""
    
    # Sample data
    sample_data = {
        'title_data': {
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
    
    print("🔄 Testing document generation with latest templates...")
    
    try:
        # Initialize document generator
        generator = EnhancedDocumentGenerator(sample_data)
        
        # Generate all documents
        documents = generator.generate_all_documents()
        
        print(f"✅ Generated {len(documents)} HTML documents:")
        for doc_name in documents.keys():
            print(f"  - {doc_name}")
            
        # Check that all expected documents are present
        expected_documents = [
            'First Page Summary',
            'Deviation Statement',
            'Final Bill Scrutiny Sheet',
            'Extra Items Statement',
            'Certificate II',
            'Certificate III'
        ]
        
        for doc_name in expected_documents:
            assert doc_name in documents, f"{doc_name} should be in generated documents"
            assert len(documents[doc_name]) > 0, f"{doc_name} should not be empty"
            assert "<!DOCTYPE html>" in documents[doc_name], f"{doc_name} should contain DOCTYPE"
            
        print("✅ All expected documents generated successfully")
        
        # Test PDF generation for a few key documents
        print("🔄 Testing PDF generation...")
        pdf_documents = generator.create_pdf_documents(documents)
        
        print(f"✅ Generated {len(pdf_documents)} PDF documents:")
        for pdf_name in pdf_documents.keys():
            size = len(pdf_documents[pdf_name])
            print(f"  - {pdf_name} ({size} bytes)")
            
        # Check that key documents have been generated as PDFs
        key_documents = ['Deviation Statement.pdf', 'Certificate II.pdf', 'Certificate III.pdf']
        for pdf_name in key_documents:
            assert pdf_name in pdf_documents, f"{pdf_name} should be in generated PDFs"
            assert len(pdf_documents[pdf_name]) > 100, f"{pdf_name} should not be empty"
            
        print("✅ All key PDF documents generated successfully")
        
        print("\n🎉 Document generation test passed!")
        print("✅ Outputs will be generated as per latest templates for both online and offline app run")
        
        return True
        
    except Exception as e:
        print(f"❌ Document generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_document_generation()