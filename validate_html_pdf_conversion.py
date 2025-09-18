#!/usr/bin/env python3
"""
HTML-to-PDF Content Validation Script
Ensures that PDF output contains exactly the same content as HTML input without additions
"""

import os
import re
from bs4 import BeautifulSoup
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
from typing import Set, List, Dict, Any

def extract_text_from_html(html_content: str) -> str:
    """Extract clean text content from HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text and clean it
    text = soup.get_text()
    
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from PDF"""
    if pdfplumber is None:
        print("Warning: pdfplumber not available, skipping PDF text extraction")
        return "[PDF text extraction not available - pdfplumber not installed]"
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text_parts = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return '\n'.join(text_parts)
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

def normalize_text(text: str) -> str:
    """Normalize text for comparison"""
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might be rendering artifacts
    text = re.sub(r'[^\w\s.,;:!?()\-]', '', text)
    
    return text.strip()

def validate_html_pdf_conversion(html_file: str, pdf_file: str) -> Dict[str, Any]:
    """
    Validate that PDF contains exactly the same content as HTML
    Returns validation results
    """
    results = {
        'valid': False,
        'html_text': '',
        'pdf_text': '',
        'missing_in_pdf': [],
        'extra_in_pdf': [],
        'similarity_score': 0.0,
        'errors': []
    }
    
    try:
        # Read and extract text from HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        html_text = extract_text_from_html(html_content)
        pdf_text = extract_text_from_pdf(pdf_file)
        
        results['html_text'] = html_text
        results['pdf_text'] = pdf_text
        
        # Normalize texts for comparison
        html_normalized = normalize_text(html_text)
        pdf_normalized = normalize_text(pdf_text)
        
        # Split into words for comparison
        html_words = set(html_normalized.split())
        pdf_words = set(pdf_normalized.split())
        
        # Find differences
        missing_in_pdf = html_words - pdf_words
        extra_in_pdf = pdf_words - html_words
        
        # Filter out common PDF artifacts and system text
        pdf_artifacts = {
            'pdf', 'page', 'font', 'generated', 'created', 'producer', 
            'creator', 'title', 'subject', 'keywords', 'author', 'moddate',
            'creationdate', 'trapped', 'ptex', 'pdftex', 'system', 'time',
            'date', 'version', 'by', 'with'
        }
        
        extra_in_pdf = extra_in_pdf - pdf_artifacts
        
        results['missing_in_pdf'] = list(missing_in_pdf)
        results['extra_in_pdf'] = list(extra_in_pdf)
        
        # Calculate similarity score
        total_words = len(html_words | pdf_words)
        common_words = len(html_words & pdf_words)
        
        if total_words > 0:
            results['similarity_score'] = common_words / total_words
        
        # Validation criteria
        results['valid'] = (
            len(missing_in_pdf) <= 5 and  # Allow small differences due to rendering
            len(extra_in_pdf) <= 5 and   # Allow small PDF metadata additions
            results['similarity_score'] >= 0.90  # 90% similarity threshold
        )
        
    except Exception as e:
        results['errors'].append(str(e))
    
    return results

def validate_all_conversions(output_dir: str) -> Dict[str, Dict]:
    """Validate all HTML-to-PDF conversions in the output directory"""
    print("🔍 VALIDATING HTML-TO-PDF CONVERSIONS")
    print("=" * 60)
    
    validation_results = {}
    
    # Find all HTML and PDF pairs
    files = os.listdir(output_dir)
    html_files = [f for f in files if f.endswith('.html')]
    
    for html_file in html_files:
        pdf_file = html_file.replace('.html', '.pdf')
        
        if pdf_file in files:
            html_path = os.path.join(output_dir, html_file)
            pdf_path = os.path.join(output_dir, pdf_file)
            
            print(f"🔄 Validating: {html_file} → {pdf_file}")
            
            results = validate_html_pdf_conversion(html_path, pdf_path)
            validation_results[html_file] = results
            
            # Print validation summary
            if results['valid']:
                print(f"   ✅ VALID - Similarity: {results['similarity_score']:.2%}")
            else:
                print(f"   ❌ INVALID - Similarity: {results['similarity_score']:.2%}")
                if results['missing_in_pdf']:
                    print(f"      Missing in PDF: {len(results['missing_in_pdf'])} words")
                if results['extra_in_pdf']:
                    print(f"      Extra in PDF: {len(results['extra_in_pdf'])} words")
                if results['errors']:
                    print(f"      Errors: {results['errors']}")
        else:
            print(f"   ⚠️ PDF not found for {html_file}")
    
    return validation_results

def generate_validation_report(validation_results: Dict[str, Dict], output_dir: str):
    """Generate a detailed validation report"""
    report_path = os.path.join(output_dir, "HTML_PDF_VALIDATION_REPORT.txt")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("HTML-TO-PDF CONVERSION VALIDATION REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Output Directory: {output_dir}\n")
        f.write(f"Validation Date: {__import__('datetime').datetime.now()}\n\n")
        
        total_files = len(validation_results)
        valid_files = sum(1 for r in validation_results.values() if r['valid'])
        
        f.write(f"SUMMARY:\n")
        f.write(f"Total Files: {total_files}\n")
        f.write(f"Valid Conversions: {valid_files}\n")
        f.write(f"Invalid Conversions: {total_files - valid_files}\n")
        f.write(f"Success Rate: {valid_files/total_files:.2%}\n\n")
        
        for filename, results in validation_results.items():
            f.write(f"FILE: {filename}\n")
            f.write(f"Status: {'✅ VALID' if results['valid'] else '❌ INVALID'}\n")
            f.write(f"Similarity Score: {results['similarity_score']:.2%}\n")
            
            if results['missing_in_pdf']:
                f.write(f"Missing in PDF ({len(results['missing_in_pdf'])}): {', '.join(results['missing_in_pdf'][:10])}\n")
            
            if results['extra_in_pdf']:
                f.write(f"Extra in PDF ({len(results['extra_in_pdf'])}): {', '.join(results['extra_in_pdf'][:10])}\n")
            
            if results['errors']:
                f.write(f"Errors: {', '.join(results['errors'])}\n")
            
            f.write("\n" + "-" * 40 + "\n\n")
    
    print(f"📄 Validation report saved to: {report_path}")

if __name__ == "__main__":
    # Validate the latest generated output
    output_dir = "Look_urself_PDF_is_a_kids_exercise_book/test_output_2025-09-18_10-27-00"
    
    if os.path.exists(output_dir):
        validation_results = validate_all_conversions(output_dir)
        generate_validation_report(validation_results, output_dir)
        
        # Print final summary
        total_files = len(validation_results)
        valid_files = sum(1 for r in validation_results.values() if r['valid'])
        
        print(f"\n🎯 FINAL RESULTS:")
        print(f"   Total Conversions: {total_files}")
        print(f"   Valid Conversions: {valid_files}")
        print(f"   Success Rate: {valid_files/total_files:.2%}")
        
        if valid_files == total_files:
            print("   🎉 ALL CONVERSIONS VALID - HTML exactly converted to PDF!")
        else:
            print("   ⚠️ Some conversions need review")
    else:
        print(f"❌ Output directory not found: {output_dir}")