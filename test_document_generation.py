#!/usr/bin/env python3
"""
Test document generation to identify where the 'no output found' issue occurs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.excel_processor import ExcelProcessor
from utils.document_generator import DocumentGenerator
from utils.pdf_merger import PDFMerger
from utils.zip_packager import ZipPackager

def test_document_generation():
    """Test the complete document generation pipeline"""
    print("🔍 Testing Document Generation Pipeline")
    print("=" * 60)
    
    # Use a test file
    test_file = "test_input_files/3rdFinalNoExtra.xlsx"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        # Step 1: Process Excel
        print("📊 Step 1: Processing Excel file...")
        processor = ExcelProcessor(test_file)
        data = processor.process_excel()
        print(f"✅ Excel processed successfully")
        print(f"   - Title data: {len(data.get('title_data', {}))} items")
        print(f"   - Work Order: {len(data.get('work_order_data', []))} rows")
        print(f"   - Bill Quantity: {len(data.get('bill_quantity_data', []))} rows")
        print(f"   - Extra Items: {len(data.get('extra_items_data', []))} rows")
        
        # Step 2: Generate Documents
        print("\n📝 Step 2: Generating documents...")
        generator = DocumentGenerator(data)
        documents = generator.generate_all_documents()
        print(f"✅ Documents generated successfully")
        print(f"   - Generated {len(documents)} documents:")
        for doc_name, doc_content in documents.items():
            content_length = len(doc_content) if doc_content else 0
            print(f"     • {doc_name}: {content_length} characters")
            if content_length == 0:
                print(f"       ⚠️  WARNING: {doc_name} is empty!")
        
        # Step 3: Create PDFs
        print("\n📄 Step 3: Creating PDF documents...")
        try:
            pdf_files = generator.create_pdf_documents(documents)
            print(f"✅ PDFs created successfully")
            print(f"   - Generated {len(pdf_files)} PDF files")
            for pdf_name, pdf_content in pdf_files.items():
                content_length = len(pdf_content) if pdf_content else 0
                print(f"     • {pdf_name}: {content_length} bytes")
                if content_length == 0:
                    print(f"       ⚠️  WARNING: {pdf_name} PDF is empty!")
        except Exception as e:
            print(f"❌ Error creating PDFs: {str(e)}")
            return False
        
        # Step 4: Merge PDFs
        print("\n📑 Step 4: Merging PDFs...")
        try:
            merger = PDFMerger()
            merged_pdf = merger.merge_pdfs(pdf_files)
            print(f"✅ PDFs merged successfully")
            print(f"   - Merged PDF size: {len(merged_pdf)} bytes")
        except Exception as e:
            print(f"❌ Error merging PDFs: {str(e)}")
            return False
        
        # Step 5: Create ZIP package
        print("\n📦 Step 5: Creating ZIP package...")
        try:
            packager = ZipPackager()
            zip_buffer = packager.create_package(documents, pdf_files, merged_pdf)
            print(f"✅ ZIP package created successfully")
            print(f"   - ZIP size: {len(zip_buffer.getvalue())} bytes")
        except Exception as e:
            print(f"❌ Error creating ZIP: {str(e)}")
            return False
        
        print("\n🎉 SUCCESS: All steps completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        print(f"📋 Full traceback:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_document_generation()
    if success:
        print("\n✅ All tests passed - the issue might be in the Streamlit UI")
    else:
        print("\n❌ Tests failed - there's an issue in the document generation pipeline")
