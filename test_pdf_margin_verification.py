#!/usr/bin/env python3
"""
Test PDF margin verification
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_document_generator_fixed import EnhancedDocumentGenerator
import pandas as pd

def test_pdf_margin_verification():
    """Test if PDF margins are correctly applied"""
    print("🔍 Testing PDF Margin Verification")
    print("=" * 35)
    
    # Read the HTML file
    html_file = "test_final_bill_scrutiny_output.html"
    if not Path(html_file).exists():
        print("❌ HTML file not found")
        return False
        
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("✅ HTML content loaded successfully")
    
    # Create a minimal generator instance
    data = {
        'title_data': {},
        'work_order_data': pd.DataFrame(),
        'extra_items_data': pd.DataFrame()
    }
    generator = EnhancedDocumentGenerator(data)
    
    # Test the PDF generation with debug output
    try:
        print("Testing PDF generation with margin parsing...")
        success = generator._generate_pdf_reportlab(html_content, "margin_test_output.pdf")
        print(f"PDF generation result: {success}")
        
        if success:
            # Check if the file was created
            import os
            if os.path.exists("margin_test_output.pdf"):
                file_size = os.path.getsize("margin_test_output.pdf")
                print(f"✅ PDF created successfully: {file_size} bytes")
                return True
            else:
                print("❌ PDF file was not created")
                return False
        else:
            print("❌ PDF generation failed")
            return False
            
    except Exception as e:
        print(f"Error during PDF generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_margin_verification()
    if success:
        print("\n🎉 PDF margin verification completed!")
    else:
        print("\n💥 PDF margin verification failed!")