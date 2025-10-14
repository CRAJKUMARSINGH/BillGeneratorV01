import pandas as pd
from enhanced_document_generator_fixed import EnhancedDocumentGenerator
import tempfile
import os

def test_complete_document_generation():
    """Test complete document generation with templates_14102025 format"""
    print("🧪 Testing Complete Document Generation")
    print("=" * 40)
    
    # Create test data
    title_data = {
        'Project Name': 'Test Road Construction Project',
        'Contract No': 'CT-2025-001',
        'Work Order No': 'WO-2025-001',
        'Name of Work': 'Road Construction and Maintenance',
        'Contractor Name': 'ABC Construction Ltd.',
        'Measurement Officer': 'John Smith',
        'Measurement Date': '15/10/2025'
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
    
    # Create data structure for EnhancedDocumentGenerator
    test_data = {
        'title_data': title_data,
        'work_order_data': work_order_data,
        'bill_quantity_data': work_order_data,  # Using same data for simplicity
        'extra_items_data': extra_items_data
    }
    
    # Initialize document generator
    generator = EnhancedDocumentGenerator(test_data)
    
    # Generate HTML documents
    print("📄 Generating HTML documents...")
    html_documents = generator.generate_all_documents()
    
    if html_documents:
        print(f"✅ Generated {len(html_documents)} HTML documents")
        for name in html_documents.keys():
            print(f"  - {name}")
            
        # Check if First Page Summary uses the template format
        first_page_content = html_documents.get('First Page Summary', '')
        if '<title>CONTRACTOR BILL</title>' in first_page_content:
            print("✅ First Page Summary uses templates_141025 format")
        else:
            print("⚠️  First Page Summary may not use templates_141025 format")
            
        # Generate PDF documents
        print("\n🖨️  Generating PDF documents...")
        pdf_documents = generator.create_pdf_documents(html_documents)
        
        if pdf_documents:
            print(f"✅ Generated {len(pdf_documents)} PDF documents")
            total_size = 0
            for name, content in pdf_documents.items():
                size = len(content)
                total_size += size
                print(f"  - {name}: {size} bytes")
            
            print(f"\n📊 Total PDF Size: {total_size} bytes ({total_size/1024:.1f} KB)")
            
            # Save to temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"\n💾 Saving documents to: {temp_dir}")
                saved_files = []
                
                for filename, pdf_bytes in pdf_documents.items():
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        with open(file_path, 'wb') as f:
                            f.write(pdf_bytes)
                        saved_files.append(file_path)
                        print(f"  ✅ Saved {filename}")
                    except Exception as e:
                        print(f"  ❌ Failed to save {filename}: {e}")
                
                print(f"\n🎉 Successfully saved {len(saved_files)} PDF files")
                return True
        else:
            print("❌ Failed to create PDF documents")
            return False
    else:
        print("❌ Failed to generate HTML documents")
        return False

if __name__ == "__main__":
    success = test_complete_document_generation()
    if success:
        print("\n🎊 Complete Document Generation Test PASSED!")
    else:
        print("\n💥 Complete Document Generation Test FAILED!")