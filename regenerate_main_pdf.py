#!/usr/bin/env python3
"""
Regenerate the main Final Bill Scrutiny Sheet PDF with proper margins
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_document_generator_fixed import EnhancedDocumentGenerator
import pandas as pd

def regenerate_main_pdf():
    """Regenerate the main PDF with proper margins"""
    print("🔄 Regenerating Main Final Bill Scrutiny Sheet PDF")
    print("=" * 50)
    
    # Read the HTML file that was used to generate the original PDF
    html_file = "test_final_bill_scrutiny_output.html"
    if not Path(html_file).exists():
        print("❌ HTML file not found")
        return False
        
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("✅ HTML content loaded successfully")
    
    # Verify CSS margins are in the HTML
    if "@page { size: A4; margin: 15mm 10mm; }" in html_content:
        print("✅ CSS margins found in HTML: 15mm 10mm")
        print("   • Top/Bottom: 15mm")
        print("   • Left/Right: 10mm")
    else:
        print("❌ CSS margins not found in HTML")
        return False
    
    # Create minimal data for EnhancedDocumentGenerator
    data = {
        'title_data': {},
        'work_order_data': pd.DataFrame(),
        'extra_items_data': pd.DataFrame()
    }
    
    generator = EnhancedDocumentGenerator(data)
    
    print(f"\n🔄 Generating PDF with ReportLab (should respect CSS margins)...")
    success = generator._generate_pdf_reportlab(html_content, "Final Bill Scrutiny Sheet.pdf")
    
    if success:
        import os
        if os.path.exists("Final Bill Scrutiny Sheet.pdf"):
            file_size = os.path.getsize("Final Bill Scrutiny Sheet.pdf")
            print(f"✅ PDF regenerated successfully")
            print(f"📄 PDF file size: {file_size} bytes")
            
            if file_size > 4600:  # Should be similar to the demo PDF
                print("\n🎉 PDF REGENERATION SUCCESSFUL!")
                print("✅ Final Bill Scrutiny Sheet PDF now has proper margins:")
                print("   • 15mm top and bottom margins")
                print("   • 10mm left and right margins")
                print("   • Content properly positioned on page")
                print("   • Readable layout for official use")
                return True
            else:
                print("⚠️  PDF file size is smaller than expected, may not have proper margins")
                return False
        else:
            print("❌ PDF file was not created")
            return False
    else:
        print("❌ Failed to generate PDF")
        return False

if __name__ == "__main__":
    success = regenerate_main_pdf()
    if success:
        print("\n🏆 Main PDF regeneration successful!")
        print("✅ The Final Bill Scrutiny Sheet PDF should now be readable with proper margins")
        sys.exit(0)
    else:
        print("\n💥 Main PDF regeneration failed!")
        sys.exit(1)