#!/usr/bin/env python3
"""
Create a test PDF with explicit margins to verify the fix
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io

def create_pdf_with_margins():
    """Create a PDF with explicit margins to test the fix"""
    print("Creating PDF with explicit margins...")
    
    # Create a PDF document with proper margins (15mm top/bottom, 10mm left/right)
    output_path = "test_margins_fixed.pdf"
    doc = SimpleDocTemplate(
        output_path, 
        pagesize=A4,
        leftMargin=10*mm,      # 10mm left margin
        rightMargin=10*mm,     # 10mm right margin
        topMargin=15*mm,       # 15mm top margin
        bottomMargin=15*mm     # 15mm bottom margin
    )
    
    # Create content
    story = []
    styles = getSampleStyleSheet()
    
    # Add title
    story.append(Paragraph("Final Bill Scrutiny Sheet - Margin Test", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Add descriptive text
    story.append(Paragraph("This PDF should have proper margins:", styles['Normal']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("• 15mm top margin", styles['Normal']))
    story.append(Paragraph("• 10mm right margin", styles['Normal']))
    story.append(Paragraph("• 15mm bottom margin", styles['Normal']))
    story.append(Paragraph("• 10mm left margin", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Add a table to visualize the margins
    data = [
        ['Item No.', 'Description', 'Amount'],
        ['1', 'Test Item 1', '100.00'],
        ['2', 'Test Item 2', '200.00'],
        ['3', 'Test Item 3', '150.00'],
    ]
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    
    # Build PDF
    doc.build(story)
    print(f"✅ PDF created successfully: {output_path}")
    
    # Check file size
    import os
    file_size = os.path.getsize(output_path)
    print(f"📄 PDF file size: {file_size} bytes")
    
    return True

if __name__ == "__main__":
    try:
        success = create_pdf_with_margins()
        if success:
            print("\n🎉 PDF with margins created successfully!")
        else:
            print("\n💥 Failed to create PDF with margins!")
    except Exception as e:
        print(f"\n💥 Error creating PDF: {e}")
        import traceback
        traceback.print_exc()