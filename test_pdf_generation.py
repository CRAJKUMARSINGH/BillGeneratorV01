import pandas as pd
from enhanced_document_generator_fixed import EnhancedDocumentGenerator
import tempfile
import os

# Create sample data for testing
sample_data = {
    'title_data': {
        'Project Name': 'Test Project',
        'Contract No': 'CT-001',
        'Work Order No': 'WO-001'
    },
    'work_order_data': pd.DataFrame([
        {
            'Item No.': '1',
            'Description': 'Test Item 1',
            'Unit': 'Nos',
            'Quantity Since': 10,
            'Quantity Upto': 10,
            'Rate': 100,
            'Amount Since': 1000,
            'Amount Upto': 1000
        },
        {
            'Item No.': '2', 
            'Description': 'Test Item 2 (Zero Rate)',
            'Unit': 'Nos',
            'Quantity Since': 5,
            'Quantity Upto': 5,
            'Rate': 0,
            'Amount Since': 0,
            'Amount Upto': 0
        }
    ]),
    'bill_quantity_data': pd.DataFrame([
        {
            'Item No.': '1',
            'Description': 'Test Item 1',
            'Unit': 'Nos', 
            'Quantity': 10,
            'Rate': 100,
            'Amount': 1000
        },
        {
            'Item No.': '2',
            'Description': 'Test Item 2 (Zero Rate)',
            'Unit': 'Nos',
            'Quantity': 5,
            'Rate': 0,
            'Amount': 0
        }
    ]),
    'extra_items_data': pd.DataFrame()
}

def test_pdf_generation():
    """Test PDF generation to identify issues"""
    print("Testing PDF generation...")
    
    # Initialize document generator
    doc_generator = EnhancedDocumentGenerator(sample_data)
    
    # Generate HTML documents
    print("Generating HTML documents...")
    html_documents = doc_generator.generate_all_documents()
    
    if html_documents:
        print(f"✅ Generated {len(html_documents)} HTML documents")
        for name in html_documents.keys():
            print(f"  - {name}")
    else:
        print("❌ Failed to generate HTML documents")
        return False
    
    # Try to create PDF documents
    print("\nGenerating PDF documents...")
    pdf_documents = doc_generator.create_pdf_documents(html_documents)
    
    if pdf_documents:
        print(f"✅ Generated {len(pdf_documents)} PDF documents")
        for name in pdf_documents.keys():
            size = len(pdf_documents[name]) if pdf_documents[name] else 0
            print(f"  - {name}: {size} bytes")
            
        # Save PDFs to temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"\nSaving PDFs to {temp_dir}")
            for filename, pdf_bytes in pdf_documents.items():
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(pdf_bytes)
                print(f"  ✅ Saved {filename}")
        return True
    else:
        print("❌ Failed to create PDF documents")
        return False

if __name__ == "__main__":
    success = test_pdf_generation()
    if success:
        print("\n🎉 PDF generation test completed successfully!")
    else:
        print("\n💥 PDF generation test failed!")