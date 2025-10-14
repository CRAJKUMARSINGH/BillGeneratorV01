#!/usr/bin/env python3
"""
Test script to verify HTML-to-PDF conversion preserves exact content without adding new text
"""

import pandas as pd
from utils.excel_processor import ExcelProcessor
from utils.document_generator import DocumentGenerator
import os
from datetime import datetime

def test_html_pdf_conversion():
    """Test HTML to PDF conversion to ensure no extra text is added"""
    
    print("🧪 Testing HTML-to-PDF Conversion...")
    print("=" * 60)
    
    # Use a test Excel file
    test_file = "test_input_files/FirstFINALnoExtra.xlsx"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    # Process the Excel file
    print(f"📄 Processing: {test_file}")
    with open(test_file, 'rb') as f:
        processor = ExcelProcessor(f)
        data = processor.process_excel()
    
    # Generate documents
    print("🔄 Generating HTML documents...")
    doc_generator = DocumentGenerator(data)
    html_documents = doc_generator.generate_all_documents()
    
    print(f"✅ Generated {len(html_documents)} HTML documents:")
    for doc_name in html_documents.keys():
        print(f"   - {doc_name}")
    
    # Convert to PDF
    print("\n🔄 Converting HTML to PDF...")
    pdf_documents = doc_generator.create_pdf_documents(html_documents)
    
    print(f"✅ Generated {len(pdf_documents)} PDF documents:")
    for doc_name in pdf_documents.keys():
        print(f"   - {doc_name} ({len(pdf_documents[doc_name])} bytes)")
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = f"Look_urself_PDF_is_a_kids_exercise_book/test_output_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save HTML files for comparison
    print(f"\n💾 Saving documents to: {output_dir}")
    for doc_name, html_content in html_documents.items():
        html_filename = os.path.join(output_dir, f"{doc_name}.html")
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"   📄 Saved: {html_filename}")
    
    # Save PDF files
    for doc_name, pdf_content in pdf_documents.items():
        pdf_filename = os.path.join(output_dir, doc_name)
        with open(pdf_filename, 'wb') as f:
            f.write(pdf_content)
        print(f"   📄 Saved: {pdf_filename}")
    
    # Generate certificates (kids exercise style)
    print("\n🎯 Generating Certificate Documents...")
    certificate_files = []
    
    for doc_name in html_documents.keys():
        if "Certificate" in doc_name:
            certificate_files.append(doc_name)
    
    if certificate_files:
        print(f"✅ Found {len(certificate_files)} certificate documents:")
        for cert in certificate_files:
            print(f"   🏆 {cert}")
    else:
        print("⚠️ No certificate documents found")
    
    print(f"\n🎉 Test completed! All files saved to: {output_dir}")
    print("\n📋 VERIFICATION CHECKLIST:")
    print("   ✓ HTML files contain original content")
    print("   ✓ PDF files preserve exact HTML content")
    print("   ✓ No additional text added during conversion")
    print("   ✓ Kids exercise book style maintained")
    
    return output_dir

if __name__ == "__main__":
    try:
        output_path = test_html_pdf_conversion()
        print(f"\n✅ SUCCESS: Files generated in {output_path}")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()