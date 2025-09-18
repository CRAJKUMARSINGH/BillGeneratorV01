#!/usr/bin/env python3
"""
Validation script to check the quality of generated PDFs
"""

import os
from PyPDF2 import PdfReader

def validate_pdf_quality(pdf_path):
    """Validate the quality of a PDF file"""
    try:
        # Open and read the PDF
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            # Get basic info
            info = pdf_reader.metadata
            
            # Check if PDF has content
            first_page = pdf_reader.pages[0]
            text = first_page.extract_text()
            has_content = len(text.strip()) > 0
            
            return {
                'valid': True,
                'pages': num_pages,
                'has_content': has_content,
                'title': info.title if info and info.title else 'Unknown',
                'size': os.path.getsize(pdf_path)
            }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }

def main():
    """Validate all generated PDFs"""
    print("🔍 PDF Quality Validation")
    print("=" * 30)
    
    # Check demo output directory
    output_dirs = ['test_output_fixed', 'demo_output']
    
    for output_dir in output_dirs:
        if os.path.exists(output_dir):
            print(f"\n📂 Checking {output_dir}...")
            pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
            
            if not pdf_files:
                print("   ❌ No PDF files found")
                continue
                
            valid_count = 0
            total_count = len(pdf_files)
            
            for pdf_file in pdf_files:
                pdf_path = os.path.join(output_dir, pdf_file)
                result = validate_pdf_quality(pdf_path)
                
                if result['valid']:
                    print(f"   ✅ {pdf_file}")
                    print(f"      Pages: {result['pages']}, Size: {result['size']} bytes, Has Content: {result['has_content']}")
                    valid_count += 1
                else:
                    print(f"   ❌ {pdf_file} - Error: {result['error']}")
            
            print(f"\n   📊 Summary: {valid_count}/{total_count} PDFs are valid")
        else:
            print(f"\n📂 {output_dir} not found")

if __name__ == "__main__":
    # Install PyPDF2 if not available
    try:
        import PyPDF2
    except ImportError:
        print("Installing PyPDF2...")
        os.system("pip install PyPDF2")
        import PyPDF2
    
    main()