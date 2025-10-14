#!/usr/bin/env python3
"""
Comprehensive File Tester for BillGenerator
Processes all available input files and organizes outputs in separate folders
with date/time differentiation
"""

import pandas as pd
import sys
import os
from pathlib import Path
import json
import tempfile
import shutil
from datetime import datetime
import traceback

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.excel_processor import ExcelProcessor
from utils.document_generator import DocumentGenerator

def create_output_directory():
    """Create a timestamped output directory"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(f"test_outputs_{timestamp}")
    output_dir.mkdir(exist_ok=True)
    return output_dir

def process_single_file(file_path, output_dir):
    """Process a single Excel file and save outputs"""
    try:
        print(f"\n{'='*60}")
        print(f"Processing: {file_path.name}")
        print(f"{'='*60}")
        
        # Create subdirectory for this file's output
        file_output_dir = output_dir / file_path.stem
        file_output_dir.mkdir(exist_ok=True)
        
        # Process the Excel file
        print("Creating ExcelProcessor...")
        processor = ExcelProcessor(str(file_path))
        print("Processing Excel file...")
        result = processor.process_excel()
        
        print("✅ File processed successfully!")
        
        # Save processing results
        result_file = file_output_dir / "processing_results.json"
        with open(result_file, 'w') as f:
            # Convert DataFrame to dict for JSON serialization
            json_result = {}
            for key, value in result.items():
                if hasattr(value, 'to_dict'):
                    json_result[key] = value.to_dict('records')
                else:
                    json_result[key] = value
            json.dump(json_result, f, indent=2, default=str)
        print(f"💾 Processing results saved to: {result_file}")
        
        # Show summary
        print(f"📄 Title Data: {len(result.get('title_data', {}))} items")
        if 'work_order_data' in result:
            work_order_df = result['work_order_data']
            print(f"📋 Work Order Data: {len(work_order_df)} rows")
        if 'bill_quantity_data' in result:
            bill_qty_df = result['bill_quantity_data']
            print(f"💰 Bill Quantity Data: {len(bill_qty_df)} rows")
        if 'extra_items_data' in result:
            extra_items_df = result['extra_items_data']
            if hasattr(extra_items_df, 'empty') and not extra_items_df.empty:
                print(f"➕ Extra Items Data: {len(extra_items_df)} rows")
            else:
                print("➕ Extra Items Data: None")
        
        # Generate documents
        print("\n📄 Generating documents...")
        generator = DocumentGenerator(result)
        documents = generator.generate_all_documents()
        
        print(f"Generated {len(documents)} documents:")
        for doc_name in documents.keys():
            print(f"  - {doc_name}")
        
        # Save HTML documents
        html_dir = file_output_dir / "html_documents"
        html_dir.mkdir(exist_ok=True)
        
        for doc_name, doc_content in documents.items():
            # Clean filename
            clean_name = "".join(c for c in doc_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_name = clean_name.replace(' ', '_')
            filename = f"{clean_name}.html"
            doc_file = html_dir / filename
            
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            print(f"💾 HTML document saved: {doc_file}")
        
        # Create PDFs
        print("\n🖨️ Creating PDF documents...")
        pdf_files = generator.create_pdf_documents(documents)
        print(f"Created {len(pdf_files)} PDF files:")
        
        # Save PDF documents
        pdf_dir = file_output_dir / "pdf_documents"
        pdf_dir.mkdir(exist_ok=True)
        
        for pdf_name, pdf_content in pdf_files.items():
            # Clean filename
            clean_name = "".join(c for c in pdf_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_name = clean_name.replace(' ', '_')
            filename = f"{clean_name}.pdf"
            pdf_file = pdf_dir / filename
            
            with open(pdf_file, 'wb') as f:
                f.write(pdf_content)
            print(f"💾 PDF document saved: {pdf_file}")
        
        # Create a summary file
        summary = {
            "file_name": file_path.name,
            "processing_time": datetime.now().isoformat(),
            "documents_generated": len(documents),
            "document_names": list(documents.keys()),
            "pdf_files_generated": len(pdf_files),
            "pdf_names": list(pdf_files.keys()),
            "work_order_rows": len(result.get('work_order_data', [])),
            "bill_quantity_rows": len(result.get('bill_quantity_data', [])),
            "extra_items_rows": len(result.get('extra_items_data', [])) if hasattr(result.get('extra_items_data', []), '__len__') else 0
        }
        
        summary_file = file_output_dir / "summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"📊 Summary saved: {summary_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {str(e)}")
        # Save error information
        error_dir = output_dir / f"{file_path.stem}_ERROR"
        error_dir.mkdir(exist_ok=True)
        
        error_info = {
            "file_name": file_path.name,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        
        error_file = error_dir / "error_info.json"
        with open(error_file, 'w') as f:
            json.dump(error_info, f, indent=2)
        print(f"📝 Error details saved: {error_file}")
        return False

def run_comprehensive_test():
    """Run comprehensive test on all available input files"""
    print("🚀 Starting Comprehensive File Testing")
    print("=" * 80)
    
    # Create main output directory
    output_dir = create_output_directory()
    print(f"📂 Output directory: {output_dir}")
    
    # Collect all input files
    input_dirs = ["test_input_files", "input_files"]
    all_files = []
    
    for input_dir in input_dirs:
        if os.path.exists(input_dir):
            dir_path = Path(input_dir)
            excel_files = list(dir_path.glob("*.xlsx")) + list(dir_path.glob("*.xls"))
            all_files.extend(excel_files)
            print(f"📁 Found {len(excel_files)} files in {input_dir}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for file in all_files:
        if file.name not in seen:
            seen.add(file.name)
            unique_files.append(file)
    
    print(f"\n📊 Total unique files to process: {len(unique_files)}")
    
    if not unique_files:
        print("❌ No Excel files found in input directories!")
        return
    
    # Process each file
    successful = 0
    failed = 0
    
    for i, file_path in enumerate(unique_files, 1):
        print(f"\n[{i}/{len(unique_files)}] Processing: {file_path.name}")
        if process_single_file(file_path, output_dir):
            successful += 1
        else:
            failed += 1
    
    # Create overall summary
    print(f"\n{'='*80}")
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*80}")
    print(f"📁 Output directory: {output_dir}")
    print(f"📄 Total files processed: {len(unique_files)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success rate: {(successful/len(unique_files))*100:.1f}%" if unique_files else "0%")
    
    # Create main summary file
    main_summary = {
        "test_run": datetime.now().isoformat(),
        "output_directory": str(output_dir),
        "total_files": len(unique_files),
        "successful": successful,
        "failed": failed,
        "success_rate": (successful/len(unique_files)) if unique_files else 0,
        "processed_files": [str(f) for f in unique_files]
    }
    
    main_summary_file = output_dir / "test_summary.json"
    with open(main_summary_file, 'w') as f:
        json.dump(main_summary, f, indent=2)
    
    print(f"\n📄 Main summary saved: {main_summary_file}")
    print(f"\n🎉 Test completed! Check the output directory for results.")

if __name__ == "__main__":
    run_comprehensive_test()