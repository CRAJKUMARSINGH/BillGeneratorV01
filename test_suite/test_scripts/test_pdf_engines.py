#!/usr/bin/env python3
"""
Test script to check PDF engine functionality
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pdf_engines():
    """Test PDF engine functionality"""
    
    print("Testing PDF engine availability...")
    
    # Test WeasyPrint
    try:
        from weasyprint import HTML
        print("✅ WeasyPrint is available")
        
        # Test simple HTML to PDF conversion
        html_content = "<html><body><h1>Test PDF</h1><p>This is a test document.</p></body></html>"
        pdf_bytes = HTML(string=html_content).write_pdf()
        print(f"✅ WeasyPrint working: Generated PDF of {len(pdf_bytes)} bytes")
        
    except Exception as e:
        print(f"❌ WeasyPrint not available or failed: {str(e)}")
    
    # Test xhtml2pdf
    try:
        from xhtml2pdf import pisa
        import io
        print("✅ xhtml2pdf is available")
        
        # Test simple HTML to PDF conversion
        html_content = "<html><body><h1>Test PDF</h1><p>This is a test document.</p></body></html>"
        output = io.BytesIO()
        result = pisa.CreatePDF(src=html_content, dest=output, encoding="utf-8")
        
        if not result.err:
            output.seek(0)
            pdf_bytes = output.getvalue()
            print(f"✅ xhtml2pdf working: Generated PDF of {len(pdf_bytes)} bytes")
        else:
            print(f"❌ xhtml2pdf failed with error: {result.err}")
            
    except Exception as e:
        print(f"❌ xhtml2pdf not available or failed: {str(e)}")
    
    # Test ReportLab
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        import io
        print("✅ ReportLab is available")
        
        # Test simple PDF creation
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.drawString(100, 750, "Test PDF")
        c.drawString(100, 730, "This is a test document.")
        c.save()
        
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        print(f"✅ ReportLab working: Generated PDF of {len(pdf_bytes)} bytes")
        
    except Exception as e:
        print(f"❌ ReportLab not available or failed: {str(e)}")

if __name__ == "__main__":
    test_pdf_engines()