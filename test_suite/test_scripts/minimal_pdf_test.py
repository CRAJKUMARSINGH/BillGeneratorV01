#!/usr/bin/env python3
"""
Minimal PDF generation test
"""

def test_minimal_pdf():
    """Test minimal PDF generation"""
    print("Testing minimal PDF generation...")
    
    # Test ReportLab directly
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        import io
        
        print("✅ ReportLab imported successfully")
        
        # Create a simple PDF
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.drawString(100, 750, "Test PDF Document")
        c.drawString(100, 730, "This is a minimal test.")
        c.save()
        
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        
        print(f"✅ ReportLab working: Generated PDF of {len(pdf_bytes)} bytes")
        
        # Save the PDF
        with open("minimal_test.pdf", "wb") as f:
            f.write(pdf_bytes)
        
        print("✅ PDF saved as minimal_test.pdf")
        return True
        
    except Exception as e:
        print(f"❌ ReportLab test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_minimal_pdf()