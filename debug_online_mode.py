import pandas as pd
import streamlit as st
from enhanced_document_generator_fixed import EnhancedDocumentGenerator
import tempfile
import os

# Simulate online mode data structure
def create_online_mode_data():
    """Create data structure similar to what online mode would generate"""
    
    # Title data (as would be collected in online mode)
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
    
    # Work order data (as entered in Step 1)
    work_order_data = pd.DataFrame([
        {
            'Item No.': '1',
            'Description': 'Excavation in Hard Rock',
            'Unit': 'Cu.M',
            'Quantity Since': 0,  # Will be updated with bill quantities
            'Quantity Upto': 0,   # Will be updated with bill quantities
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
    
    # Bill quantity data (as entered in Step 2)
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
    
    # Extra items data (as entered in Step 3, if any)
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
    
    return {
        'title_data': title_data,
        'work_order_data': work_order_data,
        'bill_quantity_data': bill_quantity_data,
        'extra_items_data': extra_items_data
    }

def test_online_mode_document_generation():
    """Test document generation with online mode data structure"""
    print("🧪 Testing Online Mode Document Generation")
    print("=" * 50)
    
    # Create online mode data
    online_data = create_online_mode_data()
    
    print("📋 Data Structure:")
    print(f"  - Title Data: {len(online_data['title_data'])} fields")
    print(f"  - Work Order Items: {len(online_data['work_order_data'])}")
    print(f"  - Bill Quantity Items: {len(online_data['bill_quantity_data'])}")
    print(f"  - Extra Items: {len(online_data['extra_items_data'])}")
    
    # Initialize document generator
    print("\n🔄 Initializing EnhancedDocumentGenerator...")
    try:
        doc_generator = EnhancedDocumentGenerator(online_data)
        print("✅ EnhancedDocumentGenerator initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize EnhancedDocumentGenerator: {e}")
        return False
    
    # Generate HTML documents
    print("\n📄 Generating HTML Documents...")
    try:
        html_documents = doc_generator.generate_all_documents()
        if html_documents:
            print(f"✅ Generated {len(html_documents)} HTML documents")
            for name in html_documents.keys():
                print(f"  - {name}")
        else:
            print("❌ Failed to generate HTML documents")
            return False
    except Exception as e:
        print(f"❌ Error generating HTML documents: {e}")
        return False
    
    # Generate PDF documents
    print("\n🖨️  Generating PDF Documents...")
    try:
        pdf_documents = doc_generator.create_pdf_documents(html_documents)
        if pdf_documents:
            print(f"✅ Generated {len(pdf_documents)} PDF documents")
            total_size = 0
            for name, content in pdf_documents.items():
                size = len(content) if content else 0
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
    except Exception as e:
        print(f"❌ Error generating PDF documents: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_online_mode_document_generation()
    if success:
        print("\n🎊 Online Mode Document Generation Test PASSED!")
    else:
        print("\n💥 Online Mode Document Generation Test FAILED!")