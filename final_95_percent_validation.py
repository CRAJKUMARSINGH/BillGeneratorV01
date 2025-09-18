#!/usr/bin/env python3
"""
Final Validation Script for 95% HTML-to-PDF Matching Requirement
"""

import os
import glob
import re
from bs4 import BeautifulSoup

def validate_95_percent_matching(input_directory: str) -> bool:
    """
    Validate that all HTML-to-PDF conversions achieve 95%+ matching
    
    Args:
        input_directory: Directory containing HTML and PDF files
        
    Returns:
        bool: True if all documents achieve 95%+ matching
    """
    try:
        import pdfplumber
    except ImportError:
        print("⚠️ pdfplumber not available, cannot perform detailed validation")
        return False
    
    def extract_text_from_html(html_content: str) -> str:
        """Extract clean text content from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        # Get text and normalize whitespace
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
    
    def calculate_improved_similarity(text1: str, text2: str) -> float:
        """
        Calculate improved similarity that accounts for PDF extraction artifacts
        """
        # Convert to lowercase and normalize
        text1 = re.sub(r'\s+', ' ', text1.lower()).strip()
        text2 = re.sub(r'\s+', ' ', text2.lower()).strip()
        
        # Split into words
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        # Filter out common PDF artifacts and system text
        artifacts = {
            'pdf', 'page', 'font', 'generated', 'created', 'producer', 
            'creator', 'title', 'subject', 'keywords', 'author', 'moddate',
            'creationdate', 'trapped', 'ptex', 'pdftex', 'system', 'time',
            'date', 'version', 'by', 'with', 'cid', 'obj', 'endobj', 'stream'
        }
        
        words1 = words1 - artifacts
        words2 = words2 - artifacts
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    # Find HTML files
    html_files = glob.glob(os.path.join(input_directory, "*.html"))
    
    if not html_files:
        print(f"❌ No HTML files found in {input_directory}")
        return False
    
    print(f"🔍 Validating 95%+ matching for {len(html_files)} documents...")
    
    all_valid = True
    results = []
    
    for html_file in html_files:
        pdf_file = html_file.replace('.html', '.pdf')
        
        if not os.path.exists(pdf_file):
            print(f"   ⚠️ PDF not found for {os.path.basename(html_file)}")
            all_valid = False
            continue
        
        try:
            # Read HTML content
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extract texts
            html_text = extract_text_from_html(html_content)
            pdf_text = extract_text_from_pdf(pdf_file)
            
            # Calculate similarity
            similarity = calculate_improved_similarity(html_text, pdf_text)
            results.append((os.path.basename(html_file), similarity))
            
            # Check if meets 95% requirement
            if similarity >= 0.95:
                print(f"   ✅ {os.path.basename(html_file)}: {similarity:.2%} similarity (95%+ achieved)")
            else:
                print(f"   ❌ {os.path.basename(html_file)}: {similarity:.2%} similarity (below 95%)")
                all_valid = False
                
        except Exception as e:
            print(f"   ❌ Error validating {os.path.basename(html_file)}: {str(e)}")
            all_valid = False
    
    # Summary
    if results:
        valid_count = sum(1 for _, sim in results if sim >= 0.95)
        total_count = len(results)
        success_rate = valid_count / total_count if total_count > 0 else 0
        
        print(f"\n📊 FINAL VALIDATION RESULTS:")
        print(f"   Total Documents: {total_count}")
        print(f"   95%+ Matching: {valid_count}")
        print(f"   Below 95%: {total_count - valid_count}")
        print(f"   Success Rate: {success_rate:.2%}")
        
        if all_valid:
            print("\n🎉 SUCCESS: ALL DOCUMENTS ACHIEVE 95%+ MATCHING!")
            print("   ✅ HTML-to-PDF conversion quality requirements fully met!")
        else:
            print("\n⚠️ Some documents still need optimization to reach 95%+ matching")
            print("   ℹ️ This may be due to:")
            print("      - Complex table structures causing text extraction issues")
            print("      - PDF rendering artifacts affecting text extraction")
            print("      - CSS properties that don't translate perfectly to PDF")
    
    return all_valid

def main():
    """Main validation function"""
    input_dir = "Look_urself_PDF_is_a_kids_exercise_book/test_output_2025-09-18_10-27-00"
    
    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        return
    
    print("🎯 FINAL 95% HTML-TO-PDF MATCHING VALIDATION")
    print("=" * 60)
    print(f"Input Directory: {input_dir}")
    
    # Validate matching quality
    validation_passed = validate_95_percent_matching(input_dir)
    
    if validation_passed:
        print(f"\n🏆 VALIDATION COMPLETE - REQUIREMENTS MET!")
        print("   All HTML-to-PDF conversions achieve 95%+ matching")
        print("   The system is ready for production use")
    else:
        print(f"\n⚠️ VALIDATION COMPLETE - SOME OPTIMIZATION NEEDED")
        print("   While the conversion works, some documents need improvement")
        print("   to meet the 95%+ matching requirement")

if __name__ == "__main__":
    main()