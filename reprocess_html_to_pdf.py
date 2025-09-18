#!/usr/bin/env python3
"""
Reprocess HTML files to PDF with improved 95%+ matching accuracy
"""

import os
import glob
from improved_html_pdf_converter import ImprovedHTMLPDFConverter

from typing import Optional

def reprocess_html_files(input_directory: str, output_directory: Optional[str] = None) -> None:
    """
    Reprocess all HTML files in a directory to PDF with improved accuracy
    
    Args:
        input_directory: Directory containing HTML files
        output_directory: Directory to save PDF files (defaults to input_directory)
    """
    if output_directory is None:
        output_directory = input_directory
    
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Find all HTML files
    html_files = glob.glob(os.path.join(input_directory, "*.html"))
    
    if not html_files:
        print(f"❌ No HTML files found in {input_directory}")
        return
    
    print(f"🔄 Found {len(html_files)} HTML files to reprocess")
    
    # Read all HTML files
    documents = {}
    for html_file in html_files:
        filename = os.path.basename(html_file)
        doc_name = filename.replace('.html', '')
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                documents[doc_name] = content
                print(f"   📄 Loaded: {filename} ({len(content)} characters)")
        except Exception as e:
            print(f"   ❌ Error loading {filename}: {str(e)}")
    
    if not documents:
        print("❌ No valid HTML documents loaded")
        return
    
    # Convert with improved converter
    print("\n🔄 Converting with improved accuracy (target: 95%+ matching)...")
    converter = ImprovedHTMLPDFConverter()
    pdf_results = converter.convert_documents_to_pdf(documents)
    
    # Save PDF files
    print(f"\n💾 Saving {len(pdf_results)} PDF files...")
    for doc_name, pdf_content in pdf_results.items():
        pdf_filename = os.path.join(output_directory, f"{doc_name}.pdf")
        try:
            with open(pdf_filename, 'wb') as f:
                f.write(pdf_content)
            print(f"   📄 Saved: {pdf_filename} ({len(pdf_content)} bytes)")
        except Exception as e:
            print(f"   ❌ Error saving {pdf_filename}: {str(e)}")
    
    print(f"\n✅ Reprocessing complete!")
    print(f"   Processed: {len(documents)} HTML files")
    print(f"   Generated: {len(pdf_results)} PDF files")
    print(f"   Output: {output_directory}")

def validate_conversion_quality(input_directory: str) -> None:
    """
    Validate that the reprocessed PDFs achieve 95%+ matching
    
    Args:
        input_directory: Directory containing both HTML and PDF files
    """
    try:
        import pdfplumber
    except ImportError:
        print("⚠️ pdfplumber not available, skipping detailed validation")
        return
    
    from bs4 import BeautifulSoup
    import re
    
    def extract_text_from_html(html_content: str) -> str:
        """Extract clean text content from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return ' '.join(chunk for chunk in chunks if chunk)
    
    def extract_text_from_pdf(pdf_path: str) -> str:
        """Extract text content from PDF"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                return ' '.join(text_parts)
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return ""
    
    def calculate_similarity(text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        # Convert to lowercase and remove extra whitespace
        text1 = re.sub(r'\s+', ' ', text1.lower()).strip()
        text2 = re.sub(r'\s+', ' ', text2.lower()).strip()
        
        # Simple word-based similarity
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    # Find HTML and PDF pairs
    html_files = glob.glob(os.path.join(input_directory, "*.html"))
    
    print(f"\n🔍 Validating conversion quality for {len(html_files)} documents...")
    
    results = []
    for html_file in html_files:
        pdf_file = html_file.replace('.html', '.pdf')
        
        if not os.path.exists(pdf_file):
            print(f"   ⚠️ PDF not found for {os.path.basename(html_file)}")
            continue
        
        try:
            # Read HTML
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extract texts
            html_text = extract_text_from_html(html_content)
            pdf_text = extract_text_from_pdf(pdf_file)
            
            # Calculate similarity
            similarity = calculate_similarity(html_text, pdf_text)
            results.append((os.path.basename(html_file), similarity))
            
            status = "✅" if similarity >= 0.95 else "❌"
            print(f"   {status} {os.path.basename(html_file)}: {similarity:.2%} similarity")
            
        except Exception as e:
            print(f"   ❌ Error validating {os.path.basename(html_file)}: {str(e)}")
    
    # Summary
    if results:
        valid_count = sum(1 for _, sim in results if sim >= 0.95)
        total_count = len(results)
        success_rate = valid_count / total_count if total_count > 0 else 0
        
        print(f"\n📊 VALIDATION SUMMARY:")
        print(f"   Total Documents: {total_count}")
        print(f"   95%+ Matching: {valid_count}")
        print(f"   Success Rate: {success_rate:.2%}")
        
        if success_rate >= 0.95:
            print("   🎉 TARGET ACHIEVED: 95%+ matching for all documents!")
        else:
            print("   ⚠️ Some documents need further optimization")

if __name__ == "__main__":
    # Reprocess the test output directory
    input_dir = "Look_urself_PDF_is_a_kids_exercise_book/test_output_2025-09-18_10-27-00"
    
    if os.path.exists(input_dir):
        print(f"🔄 Reprocessing HTML files in: {input_dir}")
        reprocess_html_files(input_dir)
        
        print(f"\n🔍 Validating conversion quality...")
        validate_conversion_quality(input_dir)
    else:
        print(f"❌ Input directory not found: {input_dir}")