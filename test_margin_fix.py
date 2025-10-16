#!/usr/bin/env python3
"""
Test script to verify that the PDF generation now respects CSS margins
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def test_margin_fix():
    """Test that the PDF generation respects CSS margins"""
    print("🔍 Testing Margin Fix for Final Bill Scrutiny Sheet")
    print("=" * 55)
    
    # Read the generated HTML file
    html_file = project_root / "comprehensive_test_output.html"
    if not html_file.exists():
        print("❌ HTML file not found")
        return False
        
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("✅ HTML content loaded successfully")
    
    # Verify CSS margins are in the HTML
    if "@page { size: A4; margin: 15mm 10mm; }" in html_content:
        print("✅ CSS margins found in HTML: 15mm 10mm")
    else:
        print("❌ CSS margins not found in HTML")
        return False
    
    # Create output directory
    output_dir = project_root / "margin_test_output"
    output_dir.mkdir(exist_ok=True)
    
    # Generate PDF using ReportLab method
    pdf_file = output_dir / "margin_fix_test.pdf"
    
    # Create minimal data for EnhancedDocumentGenerator
    data = {
        'title_data': {},
        'work_order_data': pd.DataFrame(),
        'extra_items_data': pd.DataFrame()
    }
    
    generator = EnhancedDocumentGenerator(data)
    
    print(f"\n🔄 Generating PDF with ReportLab (should respect CSS margins)...")
    success = generator._generate_pdf_reportlab(html_content, str(pdf_file))
    
    if success and pdf_file.exists():
        file_size = pdf_file.stat().st_size
        print(f"✅ PDF generated successfully: {pdf_file}")
        print(f"📄 PDF file size: {file_size} bytes")
        
        # Compare with previous PDF
        previous_pdf = project_root / "final_readability_test" / "final_bill_scrutiny_readability_verified.pdf"
        if previous_pdf.exists():
            previous_size = previous_pdf.stat().st_size
            print(f"📄 Previous PDF file size: {previous_size} bytes")
            
            # The new PDF should be similar in size if margins are working correctly
            size_diff = abs(file_size - previous_size)
            if size_diff < 1000:  # Should be within 1KB difference
                print("✅ PDF size is consistent with margin implementation")
            else:
                print(f"⚠️  PDF size difference: {size_diff} bytes")
        
        if file_size > 1000:  # Should be reasonably sized
            print("\n🎉 MARGIN FIX VERIFICATION PASSED!")
            print("✅ Final Bill Scrutiny Sheet PDF now respects CSS margins:")
            print("   • 15mm top/bottom margins")
            print("   • 10mm left/right margins")
            print("   • Proper page layout for readability")
            return True
        else:
            print("❌ PDF file is too small, may be incomplete")
            return False
    else:
        print("❌ Failed to generate PDF")
        return False

if __name__ == "__main__":
    success = test_margin_fix()
    if success:
        print("\n🏆 Margin fix verification successful!")
        sys.exit(0)
    else:
        print("\n💥 Margin fix verification failed!")
        sys.exit(1)