#!/usr/bin/env python3
"""
Demo script showing how to use the EnhancedDocumentGenerator with fixed HTML-to-PDF conversion
"""

import pandas as pd
import os
from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def main():
    """Demonstrate the enhanced document generator"""
    print("🚀 Enhanced Document Generator Demo")
    print("=" * 50)
    
    # Sample data (in a real application, this would come from your Excel processor)
    sample_data = {
        'title_data': {
            'Project Name': 'Bridge Construction Project',
            'Contract No': 'PWD/BC/2024/002',
            'Work Order No': 'WO/BC/2024/002',
            'Contractor Name': 'XYZ Infrastructure Ltd',
            'Work Description': 'Construction of RCC bridge with approach roads'
        },
        'work_order_data': pd.DataFrame([
            {
                'Item No.': '1.1',
                'Description': 'Excavation for foundation',
                'Unit': 'Cum',
                'Quantity Since': 200.00,
                'Quantity Upto': 450.00,
                'Rate': 150.00,
                'Amount Since': 30000.00,
                'Amount Upto': 67500.00,
                'Remark': 'As per drawing'
            },
            {
                'Item No.': '1.2',
                'Description': 'RCC M30 grade concrete',
                'Unit': 'Cum',
                'Quantity Since': 120.50,
                'Quantity Upto': 280.75,
                'Rate': 5200.00,
                'Amount Since': 626600.00,
                'Amount Upto': 1460900.00,
                'Remark': 'With proper curing'
            }
        ]),
        'bill_quantity_data': pd.DataFrame([
            {
                'Item No.': '1.1',
                'Description': 'Excavation for foundation',
                'Unit': 'Cum',
                'Quantity': 460.00,
                'Rate': 150.00
            },
            {
                'Item No.': '1.2',
                'Description': 'RCC M30 grade concrete',
                'Unit': 'Cum',
                'Quantity': 290.25,
                'Rate': 5200.00
            }
        ]),
        'extra_items_data': pd.DataFrame([
            {
                'Item No.': 'E1',
                'Description': 'Additional steel reinforcement',
                'Unit': 'Kg',
                'Quantity': 1500.00,
                'Rate': 80.00,
                'Remark': 'For seismic resistance'
            }
        ])
    }
    
    # Initialize the enhanced document generator
    print("🔧 Initializing EnhancedDocumentGenerator...")
    generator = EnhancedDocumentGenerator(sample_data)
    
    # Generate all documents
    print("📄 Generating all documents...")
    documents = generator.generate_all_documents()
    
    print(f"✅ Generated {len(documents)} documents:")
    for doc_name in documents.keys():
        print(f"   - {doc_name}")
    
    # Create PDF documents with enhanced quality
    print("\n🖨️  Converting documents to high-quality PDFs...")
    pdf_files = generator.create_pdf_documents(documents)
    
    # Save PDF files
    output_dir = "demo_output"
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
    
    print(f"\n🎉 Demo completed! Saved {saved_files} PDF files to {output_dir}")
    print("\n📂 Check the demo_output directory for the generated PDF files.")
    print("📋 Refer to FIXED_PDF_CONVERSION_SUMMARY.md for details on the fixes implemented.")

if __name__ == "__main__":
    main()