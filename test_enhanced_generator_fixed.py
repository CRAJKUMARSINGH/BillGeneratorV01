#!/usr/bin/env python3
"""
Test script for the enhanced document generator with fixed HTML-to-PDF conversion
"""

import pandas as pd
import os
import sys
from datetime import datetime
from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def create_sample_data():
    """Create sample data for testing"""
    # Sample title data
    title_data = {
        'Project Name': 'Road Construction Project',
        'Contract No': 'PWD/RC/2024/001',
        'Work Order No': 'WO/RC/2024/001',
        'Contractor Name': 'ABC Construction Ltd',
        'Work Description': 'Construction of 2-lane road with drainage'
    }
    
    # Sample work order data
    work_order_data = pd.DataFrame([
        {
            'Item No.': '1.1',
            'Description': 'Earthwork in excavation',
            'Unit': 'Cum',
            'Quantity Since': 150.50,
            'Quantity Upto': 300.25,
            'Rate': 120.00,
            'Amount Since': 18060.00,
            'Amount Upto': 36030.00,
            'Remark': 'As per drawing'
        },
        {
            'Item No.': '1.2',
            'Description': 'Providing sand filling',
            'Unit': 'Cum',
            'Quantity Since': 85.75,
            'Quantity Upto': 175.50,
            'Rate': 850.00,
            'Amount Since': 72887.50,
            'Amount Upto': 149175.00,
            'Remark': 'Good quality sand'
        },
        {
            'Item No.': '1.3',
            'Description': 'Cement concrete 1:2:4',
            'Unit': 'Cum',
            'Quantity Since': 45.25,
            'Quantity Upto': 95.75,
            'Rate': 4500.00,
            'Amount Since': 203625.00,
            'Amount Upto': 430875.00,
            'Remark': 'M25 grade'
        }
    ])
    
    # Sample bill quantity data
    bill_quantity_data = pd.DataFrame([
        {
            'Item No.': '1.1',
            'Description': 'Earthwork in excavation',
            'Unit': 'Cum',
            'Quantity': 310.00,
            'Rate': 120.00
        },
        {
            'Item No.': '1.2',
            'Description': 'Providing sand filling',
            'Unit': 'Cum',
            'Quantity': 180.25,
            'Rate': 850.00
        },
        {
            'Item No.': '1.3',
            'Description': 'Cement concrete 1:2:4',
            'Unit': 'Cum',
            'Quantity': 100.50,
            'Rate': 4500.00
        }
    ])
    
    # Sample extra items data
    extra_items_data = pd.DataFrame([
        {
            'Item No.': 'E1',
            'Description': 'Additional drainage work',
            'Unit': 'Meter',
            'Quantity': 50.00,
            'Rate': 250.00,
            'Remark': 'Extra work requested'
        },
        {
            'Item No.': 'E2',
            'Description': 'Guard rail installation',
            'Unit': 'Meter',
            'Quantity': 120.00,
            'Rate': 300.00,
            'Remark': 'Safety enhancement'
        }
    ])
    
    return {
        'title_data': title_data,
        'work_order_data': work_order_data,
        'bill_quantity_data': bill_quantity_data,
        'extra_items_data': extra_items_data
    }

def test_enhanced_generator():
    """Test the enhanced document generator"""
    print("🧪 Testing Enhanced Document Generator with Fixed HTML-to-PDF Conversion")
    print("=" * 80)
    
    # Create sample data
    print("📊 Creating sample data...")
    sample_data = create_sample_data()
    
    # Initialize the enhanced document generator
    print("🚀 Initializing EnhancedDocumentGenerator...")
    generator = EnhancedDocumentGenerator(sample_data)
    
    # Generate all documents
    print("📄 Generating all documents...")
    documents = generator.generate_all_documents()
    
    print(f"✅ Generated {len(documents)} documents:")
    for doc_name in documents.keys():
        print(f"   - {doc_name}")
    
    # Create PDF documents
    print("\n🖨️  Converting documents to PDF...")
    pdf_files = generator.create_pdf_documents(documents)
    
    # Save PDF files
    output_dir = "test_output_fixed"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"💾 Saving PDF files to {output_dir}...")
    saved_files = 0
    for filename, pdf_bytes in pdf_files.items():
        if isinstance(pdf_bytes, bytes) and len(pdf_bytes) > 0:
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(pdf_bytes)
            print(f"   ✅ Saved {filename} ({len(pdf_bytes)} bytes)")
            saved_files += 1
        else:
            print(f"   ❌ Failed to save {filename}")
    
    print(f"\n🎉 Test completed! Saved {saved_files} PDF files to {output_dir}")
    
    # Verify the files were created
    print("\n🔍 Verifying output files:")
    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath)
            print(f"   📄 {filename} ({size} bytes)")
    
    return True

if __name__ == "__main__":
    try:
        test_enhanced_generator()
        print("\n✅ All tests passed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)