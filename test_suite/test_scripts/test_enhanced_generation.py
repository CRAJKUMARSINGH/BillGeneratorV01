#!/usr/bin/env python3
"""
Test script to test enhanced document generation with programmatic fallback
"""

import pandas as pd
import sys
import os
from pathlib import Path
import traceback

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.excel_processor import ExcelProcessor
from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def test_enhanced_generation():
    """Test enhanced document generation"""
    # Use one of the test files
    test_file = "test_input_files/3rdFinalNoExtra.xlsx"
    
    print(f"Testing enhanced document generation with file: {test_file}")
    
    if not os.path.exists(test_file):
        print(f"File not found: {test_file}")
        return False
    
    try:
        # Process the Excel file
        print("1. Creating ExcelProcessor...")
        processor = ExcelProcessor(test_file)
        print("2. Processing Excel file...")
        result = processor.process_excel()
        
        print("\n✅ Excel file processed successfully!")
        
        # Show some data to verify we have content
        if 'work_order_data' in result:
            work_order_df = result['work_order_data']
            print(f"Work Order Data: {len(work_order_df)} rows")
        
        # Generate documents using enhanced generator (with programmatic fallback)
        print("\n3. Generating documents with enhanced generator...")
        generator = EnhancedDocumentGenerator(result)
        html_documents = generator.generate_all_documents()
        
        print(f"Generated {len(html_documents)} HTML documents:")
        for name, content in html_documents.items():
            print(f"  - {name}: {len(content)} characters")
        
        # Try to create PDF documents
        print("\n4. Creating PDF documents...")
        pdf_documents = generator.create_pdf_documents(html_documents)
        
        print(f"Generated {len(pdf_documents)} PDF documents:")
        for name, content in pdf_documents.items():
            size_kb = len(content) / 1024
            print(f"  - {name}: {len(content)} bytes ({size_kb:.2f} KB)")
            
            # Save to file for inspection
            filename = f"enhanced_{name.replace(' ', '_').replace('/', '_')}.pdf"
            with open(filename, 'wb') as f:
                f.write(content)
            print(f"    Saved to: {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in enhanced generation: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting enhanced document generation test...")
    success = test_enhanced_generation()
    if success:
        print("\n🎉 Enhanced document generation test completed!")
    else:
        print("\n💥 Enhanced document generation test failed!")