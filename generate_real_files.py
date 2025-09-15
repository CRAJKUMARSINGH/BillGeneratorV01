#!/usr/bin/env python3
"""
Generate Real Output Files Script
Creates actual PDF, Word, HTML, and ZIP files from test Excel data
By: RAJKUMAR SINGH CHAUHAN (crajkumarsingh@hotmail.com)
"""

import os
import sys
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def generate_real_files():
    """Generate actual output files from test Excel data"""
    print("🚀 GENERATING REAL OUTPUT FILES")
    print("=" * 60)
    print(f"👨‍💻 By: RAJKUMAR SINGH CHAUHAN")
    print(f"📧 Email: crajkumarsingh@hotmail.com")
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Import required modules
    from utils.excel_processor import ExcelProcessor
    from utils.document_generator import DocumentGenerator
    from utils.pdf_merger import PDFMerger
    from utils.zip_packager import ZipPackager
    
    # Create output directory
    output_dir = "GENERATED_FILES"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created output directory: {output_dir}")
    
    # Get test files
    test_dir = "test_input_files"
    if not os.path.exists(test_dir):
        print(f"❌ Test directory '{test_dir}' not found!")
        return False
    
    # Get first few Excel files for demonstration
    excel_files = [f for f in os.listdir(test_dir) if f.lower().endswith(('.xlsx', '.xls'))][:3]
    
    if not excel_files:
        print(f"❌ No Excel files found in '{test_dir}'!")
        return False
    
    print(f"📄 Processing {len(excel_files)} files to generate real output...")
    print("-" * 60)
    
    for i, filename in enumerate(excel_files, 1):
        file_path = os.path.join(test_dir, filename)
        print(f"\n[{i}/{len(excel_files)}] Processing: {filename}")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            # Step 1: Process Excel
            print("  🔄 Processing Excel file...")
            processor = ExcelProcessor(file_path)
            data = processor.process_excel()
            
            # Get project name for file naming
            project_name = data.get('title_data', {}).get('Project Name', 'Project')
            clean_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()[:30]
            if not clean_name:
                clean_name = filename.replace('.xlsx', '').replace('.xls', '')
            
            # Step 2: Generate Documents
            print("  📝 Generating HTML documents...")
            generator = DocumentGenerator(data)
            documents = generator.generate_all_documents()
            
            # Create individual HTML files
            html_dir = os.path.join(output_dir, f"{clean_name}_HTML")
            if not os.path.exists(html_dir):
                os.makedirs(html_dir)
            
            for doc_name, html_content in documents.items():
                html_filename = f"{doc_name.replace(' ', '_').lower()}.html"
                html_path = os.path.join(html_dir, html_filename)
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"    ✅ Created: {html_filename}")
            
            # Step 3: Generate PDFs
            print("  📄 Generating PDF files...")
            pdf_files = generator.create_pdf_documents(documents)
            
            # Create individual PDF files
            pdf_dir = os.path.join(output_dir, f"{clean_name}_PDF")
            if not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir)
            
            for pdf_name, pdf_content in pdf_files.items():
                if isinstance(pdf_content, bytes) and len(pdf_content) > 0:
                    if not pdf_content.startswith(b"PDF generation failed"):
                        pdf_path = os.path.join(pdf_dir, pdf_name)
                        with open(pdf_path, 'wb') as f:
                            f.write(pdf_content)
                        print(f"    ✅ Created: {pdf_name} ({len(pdf_content)} bytes)")
                    else:
                        print(f"    ⚠️ Skipped: {pdf_name} (generation failed)")
            
            # Step 4: Merge PDFs
            print("  📑 Creating combined PDF...")
            merger = PDFMerger()
            merged_pdf = merger.merge_pdfs(pdf_files)
            
            if merged_pdf and len(merged_pdf) > 0:
                combined_pdf_path = os.path.join(output_dir, f"{clean_name}_COMBINED.pdf")
                with open(combined_pdf_path, 'wb') as f:
                    f.write(merged_pdf)
                print(f"    ✅ Created: {clean_name}_COMBINED.pdf ({len(merged_pdf)} bytes)")
            
            # Step 5: Create Word documents
            print("  📝 Generating Word documents...")
            word_dir = os.path.join(output_dir, f"{clean_name}_WORD")
            if not os.path.exists(word_dir):
                os.makedirs(word_dir)
            
            # Use the ZIP packager to create Word docs
            packager = ZipPackager()
            for doc_name, html_content in documents.items():
                word_filename = f"{doc_name.replace(' ', '_').lower()}.docx"
                word_path = os.path.join(word_dir, word_filename)
                try:
                    docx_bytes = packager._html_to_docx_bytes(doc_name, html_content)
                    with open(word_path, 'wb') as f:
                        f.write(docx_bytes)
                    print(f"    ✅ Created: {word_filename}")
                except Exception as e:
                    print(f"    ⚠️ Word doc failed: {word_filename} - {str(e)}")
            
            # Step 6: Create ZIP package
            print("  📦 Creating ZIP package...")
            zip_buffer = packager.create_package(documents, pdf_files, merged_pdf)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            zip_filename = f"{clean_name}_BillingDocs_{timestamp}.zip"
            zip_path = os.path.join(output_dir, zip_filename)
            
            with open(zip_path, 'wb') as f:
                f.write(zip_buffer.getvalue())
            
            total_time = time.time() - start_time
            zip_size = len(zip_buffer.getvalue()) / 1024  # KB
            
            print(f"    ✅ Created: {zip_filename} ({zip_size:.1f} KB)")
            print(f"  🎉 Completed in {total_time:.2f} seconds!")
            
        except Exception as e:
            print(f"  ❌ Error processing {filename}: {str(e)}")
            continue
    
    # Summary of generated files
    print("\n" + "=" * 60)
    print("📁 GENERATED FILES SUMMARY")
    print("=" * 60)
    
    # List all generated files
    total_files = 0
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path) / 1024  # KB
            rel_path = os.path.relpath(file_path, output_dir)
            print(f"📄 {rel_path} ({file_size:.1f} KB)")
            total_files += 1
    
    print(f"\n🎊 SUCCESS! Generated {total_files} files in '{output_dir}' directory")
    print(f"📂 Location: {os.path.abspath(output_dir)}")
    
    print("\n💡 You can now:")
    print("  • Open HTML files in your browser")
    print("  • View PDF files in any PDF reader")
    print("  • Edit Word documents in Microsoft Word")
    print("  • Extract ZIP packages to see all formats")
    
    return True

if __name__ == "__main__":
    success = generate_real_files()
    if success:
        print("\n🎉 Real file generation completed successfully!")
    else:
        print("\n❌ File generation failed!")
    
    input("\nPress Enter to continue...")