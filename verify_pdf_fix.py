import pandas as pd
from enhanced_document_generator_fixed import EnhancedDocumentGenerator
import tempfile
import os

def test_pdf_generation_fix():
    """Test that our PDF generation fixes work correctly"""
    print("🧪 Testing PDF Generation Fix")
    print("=" * 30)
    
    # Create minimal test data
    test_data = {
        'title_data': {
            'Project Name': 'Test Project',
            'Contract No': 'CT-001'
        },
        'work_order_data': pd.DataFrame([
            {
                'Item No.': '1',
                'Description': 'Test Item',
                'Unit': 'Nos',
                'Quantity Since': 10,
                'Rate': 100,
                'Amount Since': 1000
            }
        ]),
        'bill_quantity_data': pd.DataFrame([
            {
                'Item No.': '1',
                'Description': 'Test Item',
                'Unit': 'Nos',
                'Quantity': 10,
                'Rate': 100,
                'Amount': 1000
            }
        ]),
        'extra_items_data': pd.DataFrame()
    }
    
    # Initialize document generator
    generator = EnhancedDocumentGenerator(test_data)
    
    # Generate HTML documents
    print("📄 Generating HTML documents...")
    html_docs = generator.generate_all_documents()
    print(f"✅ Generated {len(html_docs)} HTML documents")
    
    # Generate PDF documents
    print("\n🖨️  Generating PDF documents...")
    pdf_docs = generator.create_pdf_documents(html_docs)
    
    if pdf_docs:
        print(f"✅ Generated {len(pdf_docs)} PDF documents")
        
        # Check sizes
        for name, content in pdf_docs.items():
            size = len(content)
            print(f"  - {name}: {size} bytes")
            
            # Verify minimum size
            if size < 100:
                print(f"  ⚠️  Warning: {name} is very small ({size} bytes)")
            elif size > 1000:
                print(f"  ✅ {name} is a reasonable size")
        
        # Save to temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"\n💾 Saving to {temp_dir}")
            for name, content in pdf_docs.items():
                file_path = os.path.join(temp_dir, name)
                with open(file_path, 'wb') as f:
                    f.write(content)
                print(f"  ✅ Saved {name}")
        
        print("\n🎉 PDF Generation Fix Test PASSED!")
        return True
    else:
        print("❌ Failed to generate PDF documents")
        print("\n💥 PDF Generation Fix Test FAILED!")
        return False

if __name__ == "__main__":
    test_pdf_generation_fix()