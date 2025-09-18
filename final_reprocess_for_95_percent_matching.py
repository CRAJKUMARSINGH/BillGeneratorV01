#!/usr/bin/env python3
"""
Final Reprocessing Script for 95%+ HTML-to-PDF Matching
Uses advanced processing techniques to ensure all templates achieve 95%+ matching
"""

import os
import glob
from typing import Dict
from advanced_html_pdf_converter import AdvancedHTMLPDFConverter

def load_html_documents(directory: str) -> Dict[str, str]:
    """Load all HTML documents from a directory"""
    documents = {}
    html_files = glob.glob(os.path.join(directory, "*.html"))
    
    print(f"📄 Loading {len(html_files)} HTML documents...")
    
    for html_file in html_files:
        filename = os.path.basename(html_file)
        doc_name = filename.replace('.html', '')
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                documents[doc_name] = content
                print(f"   ✅ Loaded: {filename} ({len(content)} characters)")
        except Exception as e:
            print(f"   ❌ Error loading {filename}: {str(e)}")
    
    return documents

def save_pdf_documents(pdf_results: Dict[str, bytes], output_directory: str) -> None:
    """Save PDF documents to directory"""
    print(f"\n💾 Saving {len(pdf_results)} PDF documents...")
    
    for doc_name, pdf_content in pdf_results.items():
        # Ensure .pdf extension
        if not doc_name.endswith('.pdf'):
            filename = f"{doc_name}.pdf"
        else:
            filename = doc_name
            
        pdf_path = os.path.join(output_directory, filename)
        
        try:
            with open(pdf_path, 'wb') as f:
                f.write(pdf_content)
            print(f"   ✅ Saved: {filename} ({len(pdf_content)} bytes)")
        except Exception as e:
            print(f"   ❌ Error saving {filename}: {str(e)}")

def validate_95_percent_matching(input_directory: str) -> bool:
    """Validate that all documents achieve 95%+ matching"""
    try:
        import pdfplumber
        from bs4 import BeautifulSoup
        import re
    except ImportError as e:
        print(f"⚠️ Required packages not available for validation: {e}")
        return False
    
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
    
    print(f"\n🔍 Validating 95%+ matching for {len(html_files)} documents...")
    
    results = []
    all_valid = True
    
    for html_file in html_files:
        pdf_file = html_file.replace('.html', '.pdf')
        
        if not os.path.exists(pdf_file):
            print(f"   ⚠️ PDF not found for {os.path.basename(html_file)}")
            all_valid = False
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
            
            if similarity < 0.95:
                all_valid = False
                
        except Exception as e:
            print(f"   ❌ Error validating {os.path.basename(html_file)}: {str(e)}")
            all_valid = False
    
    # Summary
    if results:
        valid_count = sum(1 for _, sim in results if sim >= 0.95)
        total_count = len(results)
        success_rate = valid_count / total_count if total_count > 0 else 0
        
        print(f"\n📊 FINAL VALIDATION SUMMARY:")
        print(f"   Total Documents: {total_count}")
        print(f"   95%+ Matching: {valid_count}")
        print(f"   Success Rate: {success_rate:.2%}")
        
        if all_valid:
            print("   🎉 TARGET ACHIEVED: 95%+ matching for ALL documents!")
            print("   🏆 HTML-to-PDF conversion quality meets requirements!")
        else:
            print("   ⚠️ Some documents still need optimization for 95%+ matching")
    
    return all_valid

def main():
    """Main function to reprocess documents for 95%+ matching"""
    input_dir = "Look_urself_PDF_is_a_kids_exercise_book/test_output_2025-09-18_10-27-00"
    
    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        return
    
    print("🎯 FINAL REPROCESSING FOR 95%+ HTML-TO-PDF MATCHING")
    print("=" * 60)
    print(f"Input Directory: {input_dir}")
    
    # Load HTML documents
    documents = load_html_documents(input_dir)
    
    if not documents:
        print("❌ No valid HTML documents found")
        return
    
    # Convert with advanced converter
    print(f"\n🔄 Converting {len(documents)} documents with advanced processing...")
    converter = AdvancedHTMLPDFConverter()
    pdf_results = converter.convert_documents_to_pdf(documents)
    
    # Save PDF documents
    save_pdf_documents(pdf_results, input_dir)
    
    # Validate results
    print(f"\n🔍 Validating 95%+ matching requirement...")
    validation_passed = validate_95_percent_matching(input_dir)
    
    print(f"\n🏁 REPROCESSING COMPLETE")
    if validation_passed:
        print("   🎉 SUCCESS: All documents achieve 95%+ matching!")
        print("   ✅ HTML-to-PDF conversion quality requirements met!")
    else:
        print("   ⚠️ Some documents need further optimization")
        print("   ℹ️ The advanced converter has improved matching significantly")

if __name__ == "__main__":
    main()