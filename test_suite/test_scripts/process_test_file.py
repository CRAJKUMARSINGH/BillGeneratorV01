#!/usr/bin/env python3
"""
Simple test script to process one of the test input files and generate documents
"""

import pandas as pd
import sys
import os
from pathlib import Path
import json
import tempfile

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.excel_processor import ExcelProcessor
from utils.document_generator import DocumentGenerator

def process_test_file():
    """Process a test file and generate documents"""
    # Use one of the test files
    test_file = "test_input_files/3rdFinalNoExtra.xlsx"
    
    print(f"Testing file: {test_file}")
    
    if not os.path.exists(test_file):
        print(f"File not found: {test_file}")
        return
    
    try:
        # Process the Excel file
        print("Creating ExcelProcessor...")
        processor = ExcelProcessor(test_file)
        print("Processing Excel file...")
        result = processor.process_excel()
        
        print("\n✅ File processed successfully!")
        print(f"Available keys: {list(result.keys())}")
        
        # Show title data
        if 'title_data' in result:
            print(f"\n📄 Title Data ({len(result['title_data'])} items):")
            for key, value in list(result['title_data'].items())[:5]:  # Show first 5 items
                print(f"  {key}: {value}")
        
        # Show work order data
        if 'work_order_data' in result:
            work_order_df = result['work_order_data']
            print(f"\n📋 Work Order Data ({len(work_order_df)} rows):")
            print(f"Columns: {list(work_order_df.columns)}")
            print("First 3 rows:")
            print(work_order_df.head(3))
        
        # Show bill quantity data
        if 'bill_quantity_data' in result:
            bill_qty_df = result['bill_quantity_data']
            print(f"\n💰 Bill Quantity Data ({len(bill_qty_df)} rows):")
            print(f"Columns: {list(bill_qty_df.columns)}")
            print("First 3 rows:")
            print(bill_qty_df.head(3))
        
        # Generate documents
        print("\n📄 Generating documents...")
        generator = DocumentGenerator(result)
        documents = generator.generate_all_documents()
        
        print(f"Generated {len(documents)} documents:")
        for doc_name in documents.keys():
            print(f"  - {doc_name}")
        
        # Create PDFs
        print("\n🖨️ Creating PDF documents...")
        pdf_files = generator.create_pdf_documents(documents)
        print(f"Created {len(pdf_files)} PDF files:")
        for pdf_name in pdf_files.keys():
            print(f"  - {pdf_name}")
        
        # Save one of the HTML documents to a file for inspection
        if documents:
            first_doc_name = list(documents.keys())[0]
            first_doc_content = documents[first_doc_name]
            
            output_file = f"test_output_{first_doc_name.replace(' ', '_').replace('/', '_')}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(first_doc_content)
            print(f"\n💾 Saved first document to: {output_file}")
        
        # Save one of the PDF documents to a file
        if pdf_files:
            first_pdf_name = list(pdf_files.keys())[0]
            first_pdf_content = pdf_files[first_pdf_name]
            
            output_file = f"test_output_{first_pdf_name.replace(' ', '_').replace('/', '_')}.pdf"
            with open(output_file, 'wb') as f:
                f.write(first_pdf_content)
            print(f"💾 Saved first PDF to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("Starting test file processing...")
    result = process_test_file()
    if result:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")