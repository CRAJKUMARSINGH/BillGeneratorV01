import pandas as pd
import tempfile
import os
from pathlib import Path
from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def test_exact_online_mode_flow():
    """Test the exact flow that happens in online mode"""
    print("🧪 Testing Exact Online Mode Flow")
    print("=" * 40)
    
    # Create the exact same data structure as online mode
    title_data = {
        'Project Name': 'Test Project - Online Mode',
        'Contract No': 'CT-2025-001',
        'Work Order No': 'WO-2025-001',
        'Name of Work': 'Road Construction Project',
        'Contractor Name': 'ABC Construction Ltd.',
        'Bill Number': 'BILL-001',
        'Measurement Officer': 'John Smith',
        'Measurement Date': '15/10/2025',
        'Measurement Book Page': '123',
        'Measurement Book No': 'MB-001'
    }
    
    work_order_data = pd.DataFrame([
        {
            'Item No.': '1',
            'Description': 'Excavation in Hard Rock',
            'Unit': 'Cu.M',
            'Quantity Since': 0,
            'Quantity Upto': 0,
            'Rate': 1500.00,
            'Amount Since': 0,
            'Amount Upto': 0
        },
        {
            'Item No.': '2',
            'Description': 'Providing and Laying Cement Concrete M20',
            'Unit': 'Cu.M',
            'Quantity Since': 0,
            'Quantity Upto': 0,
            'Rate': 4500.00,
            'Amount Since': 0,
            'Amount Upto': 0
        },
        {
            'Item No.': '3',
            'Description': 'Supply of Cement (Zero Rate Item)',
            'Unit': 'Bags',
            'Quantity Since': 0,
            'Quantity Upto': 0,
            'Rate': 0.00,
            'Amount Since': 0,
            'Amount Upto': 0
        }
    ])
    
    bill_quantity_data = pd.DataFrame([
        {
            'Item No.': '1',
            'Description': 'Excavation in Hard Rock',
            'Unit': 'Cu.M',
            'Quantity': 150.50,
            'Rate': 1500.00,
            'Amount': 225750.00
        },
        {
            'Item No.': '2',
            'Description': 'Providing and Laying Cement Concrete M20',
            'Unit': 'Cu.M',
            'Quantity': 85.25,
            'Rate': 4500.00,
            'Amount': 383625.00
        },
        {
            'Item No.': '3',
            'Description': 'Supply of Cement (Zero Rate Item)',
            'Unit': 'Bags',
            'Quantity': 500,
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
    
    # Prepare data exactly as done in online mode
    online_data = {
        'title_data': title_data,
        'work_order_data': work_order_data,
        'bill_quantity_data': bill_quantity_data,
        'extra_items_data': extra_items_data
    }
    
    print("✅ Data structure prepared")
    
    # Initialize document generator
    doc_generator = EnhancedDocumentGenerator(online_data)
    print("✅ EnhancedDocumentGenerator initialized")
    
    # Generate HTML documents (exactly as in online mode)
    print("\n📄 Generating HTML documents...")
    html_documents = doc_generator.generate_all_documents()
    
    if not html_documents:
        print("❌ Failed to generate HTML documents")
        return False
    
    print(f"✅ Generated {len(html_documents)} HTML documents!")
    for name in html_documents.keys():
        print(f"  - {name}")
    
    # Convert HTML to PDF (exactly as in online mode)
    print("\n🖨️  Converting to PDF...")
    pdf_documents = doc_generator.create_pdf_documents(html_documents)
    
    if not pdf_documents:
        print("❌ Failed to create PDF documents")
        return False
    
    print(f"✅ Successfully created {len(pdf_documents)} PDF documents!")
    for name in pdf_documents.keys():
        size = len(pdf_documents[name]) if pdf_documents[name] else 0
        print(f"  - {name}: {size} bytes")
    
    # Save PDF files to temporary directory and collect file paths (exactly as in online mode)
    print("\n💾 Saving PDF files...")
    generated_files = []
    temp_dir = tempfile.mkdtemp()
    print(f"  Using temporary directory: {temp_dir}")
    
    for filename, pdf_bytes in pdf_documents.items():
        file_path = os.path.join(temp_dir, filename)
        try:
            with open(file_path, 'wb') as f:
                f.write(pdf_bytes)
            generated_files.append(file_path)
            print(f"  ✅ Saved {filename}")
        except Exception as e:
            print(f"  ❌ Failed to save {filename}: {e}")
            return False
    
    print(f"\n🎉 Successfully saved {len(generated_files)} files:")
    for file_path in generated_files:
        file_name = Path(file_path).name
        file_size = os.path.getsize(file_path)
        print(f"  - {file_name}: {file_size} bytes")
    
    # Test download link functionality
    print("\n🔗 Testing download link functionality...")
    for i, file_path in enumerate(generated_files):
        file_name = Path(file_path).name
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                file_data = file.read()
            print(f"  ✅ Download link ready for {file_name} ({len(file_data)} bytes)")
        else:
            print(f"  ❌ File not found: {file_name}")
            return False
    
    print("\n🎊 Exact Online Mode Flow Test PASSED!")
    return True

if __name__ == "__main__":
    success = test_exact_online_mode_flow()
    if not success:
        print("\n💥 Exact Online Mode Flow Test FAILED!")