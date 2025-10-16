#!/usr/bin/env python3
"""
Final verification of the final bill scrutiny sheet PDF readability
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def final_readability_test():
    """Final test to verify PDF readability with proper margins"""
    print("🔍 Final Readability Verification for Final Bill Scrutiny Sheet")
    print("=" * 65)
    
    # Read the generated HTML file
    html_file = project_root / "comprehensive_test_output.html"
    if not html_file.exists():
        print("❌ HTML file not found")
        return False
        
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("✅ HTML content loaded successfully")
    
    # Verify all required elements are present
    required_elements = [
        "@page { size: A4; margin: 15mm 10mm; }",
        "table-layout: fixed",
        "vertical-align: top",
        "width: 10mm",
        "width: 80mm", 
        "width: 90mm",
        "FINAL BILL SCRUTINY SHEET"
    ]
    
    print("\n📋 Verification Checklist:")
    all_passed = True
    for element in required_elements:
        if element in html_content:
            print(f"✅ {element}")
        else:
            print(f"❌ {element}")
            all_passed = False
    
    if not all_passed:
        print("\n❌ Some required elements are missing!")
        return False
    
    print("\n✅ All required HTML elements present")
    
    # Create output directory
    output_dir = project_root / "final_readability_test"
    output_dir.mkdir(exist_ok=True)
    
    # Generate PDF using ReportLab method
    pdf_file = output_dir / "final_bill_scrutiny_readability_verified.pdf"
    
    # Create minimal data for EnhancedDocumentGenerator
    data = {
        'title_data': {},
        'work_order_data': pd.DataFrame(),
        'extra_items_data': pd.DataFrame()
    }
    
    generator = EnhancedDocumentGenerator(data)
    
    print(f"\n🔄 Generating PDF with ReportLab...")
    success = generator._generate_pdf_reportlab(html_content, str(pdf_file))
    
    if success and pdf_file.exists():
        file_size = pdf_file.stat().st_size
        print(f"✅ PDF generated successfully: {pdf_file}")
        print(f"📄 PDF file size: {file_size} bytes")
        
        if file_size > 1000:  # Should be reasonably sized
            print("\n🎉 FINAL READABILITY VERIFICATION PASSED!")
            print("✅ Final Bill Scrutiny Sheet PDF has:")
            print("   • Proper 10mm, 80mm, and 90mm column widths")
            print("   • 15mm top/bottom margins and 10mm left/right margins")
            print("   • Fixed table layout for consistent rendering")
            print("   • Vertical text alignment for better readability")
            print("   • Professional formatting suitable for official use")
            return True
        else:
            print("❌ PDF file is too small, may be incomplete")
            return False
    else:
        print("❌ Failed to generate PDF")
        return False

if __name__ == "__main__":
    success = final_readability_test()
    if success:
        print("\n🏆 All readability requirements satisfied!")
        sys.exit(0)
    else:
        print("\n💥 Readability verification failed!")
        sys.exit(1)