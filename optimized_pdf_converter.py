#!/usr/bin/env python3
"""
Optimized PDF Converter for Bill Generator
Ensures proper A4 sizing with 10mm margins and high-quality output
"""

import io
import gc
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedPDFConverter:
    """Optimized PDF converter with proper A4 sizing and margins"""
    
    def __init__(self):
        self.available_engines = self._check_available_engines()
        self.conversion_stats = {
            'total_conversions': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'total_size': 0,
            'average_size': 0
        }
    
    def _check_available_engines(self) -> Dict[str, bool]:
        """Check which PDF conversion engines are available"""
        engines = {
            'weasyprint': False,
            'xhtml2pdf': False,
            'playwright': False,
            'reportlab': False
        }
        
        # Check WeasyPrint
        try:
            import weasyprint
            engines['weasyprint'] = True
            logger.info("✅ WeasyPrint available")
        except ImportError:
            logger.warning("❌ WeasyPrint not available")
        
        # Check xhtml2pdf
        try:
            import xhtml2pdf
            engines['xhtml2pdf'] = True
            logger.info("✅ xhtml2pdf available")
        except ImportError:
            logger.warning("❌ xhtml2pdf not available")
        
        # Check Playwright
        try:
            from playwright.async_api import async_playwright
            engines['playwright'] = True
            logger.info("✅ Playwright available")
        except ImportError:
            logger.warning("❌ Playwright not available")
        
        # Check ReportLab
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            engines['reportlab'] = True
            logger.info("✅ ReportLab available")
        except ImportError:
            logger.warning("❌ ReportLab not available")
        
        return engines
    
    def convert_documents_to_pdf(self, documents: Dict[str, str]) -> Dict[str, bytes]:
        """
        Convert HTML documents to high-quality PDFs with proper A4 sizing
        
        Args:
            documents: Dictionary of HTML documents
            
        Returns:
            Dictionary of PDF documents as bytes
        """
        pdf_files = {}
        
        for doc_name, html_content in documents.items():
            logger.info(f"🔄 Converting {doc_name} to PDF...")
            
            try:
                # Preprocess HTML for better PDF conversion
                processed_html = self._preprocess_html(html_content)
                
                # Try conversion engines in order of preference
                pdf_bytes = None
                
                # 1. Try WeasyPrint (best for complex layouts)
                if self.available_engines['weasyprint'] and pdf_bytes is None:
                    pdf_bytes = self._convert_with_weasyprint(processed_html)
                
                # 2. Try Playwright (good for modern CSS)
                if self.available_engines['playwright'] and pdf_bytes is None:
                    pdf_bytes = self._convert_with_playwright(processed_html)
                
                # 3. Try xhtml2pdf (fallback)
                if self.available_engines['xhtml2pdf'] and pdf_bytes is None:
                    pdf_bytes = self._convert_with_xhtml2pdf(processed_html)
                
                # 4. Fallback to ReportLab
                if pdf_bytes is None:
                    pdf_bytes = self._convert_with_reportlab_fallback(doc_name, processed_html)
                
                if pdf_bytes and len(pdf_bytes) > 1024:  # At least 1KB
                    pdf_files[f"{doc_name}.pdf"] = pdf_bytes
                    self.conversion_stats['successful_conversions'] += 1
                    self.conversion_stats['total_size'] += len(pdf_bytes)
                    logger.info(f"✅ Successfully converted {doc_name} ({len(pdf_bytes):,} bytes)")
                else:
                    raise Exception("PDF conversion produced invalid result")
                    
            except Exception as e:
                logger.error(f"❌ Error converting {doc_name}: {str(e)}")
                pdf_bytes = self._create_error_pdf(doc_name, str(e))
                pdf_files[f"{doc_name}.pdf"] = pdf_bytes
                self.conversion_stats['failed_conversions'] += 1
            
            finally:
                self.conversion_stats['total_conversions'] += 1
                gc.collect()  # Clean up memory
        
        # Update average size
        if self.conversion_stats['successful_conversions'] > 0:
            self.conversion_stats['average_size'] = (
                self.conversion_stats['total_size'] / self.conversion_stats['successful_conversions']
            )
        
        return pdf_files
    
    def _preprocess_html(self, html_content: str) -> str:
        """Preprocess HTML for better PDF conversion"""
        # Add proper CSS for A4 sizing and margins
        css_addition = """
        <style>
        @page {
            size: A4;
            margin: 10mm;
        }
        
        body {
            font-family: Arial, sans-serif;
            font-size: 12px;
            line-height: 1.4;
            margin: 0;
            padding: 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            page-break-inside: avoid;
        }
        
        th, td {
            border: 1px solid #000;
            padding: 4px;
            text-align: left;
            vertical-align: top;
        }
        
        th {
            background-color: #f0f0f0;
            font-weight: bold;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        .no-break {
            page-break-inside: avoid;
        }
        </style>
        """
        
        # Insert CSS into HTML head
        if '<head>' in html_content:
            html_content = html_content.replace('<head>', f'<head>{css_addition}')
        else:
            html_content = f'<html><head>{css_addition}</head><body>{html_content}</body></html>'
        
        return html_content
    
    def _convert_with_weasyprint(self, html_content: str) -> bytes:
        """Convert HTML to PDF using WeasyPrint"""
        try:
            import weasyprint
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
            
            # Create font configuration
            font_config = FontConfiguration()
            
            # Create HTML object
            html_doc = HTML(string=html_content)
            
            # Create CSS for A4 sizing
            css = CSS(string="""
                @page {
                    size: A4;
                    margin: 10mm;
                }
                
                body {
                    font-family: Arial, sans-serif;
                    font-size: 12px;
                    line-height: 1.4;
                }
                
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                
                th, td {
                    border: 1px solid #000;
                    padding: 4px;
                    text-align: left;
                }
            """, font_config=font_config)
            
            # Generate PDF
            pdf_bytes = html_doc.write_pdf(stylesheets=[css], font_config=font_config)
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"WeasyPrint conversion error: {str(e)}")
            raise
    
    def _convert_with_playwright(self, html_content: str) -> bytes:
        """Convert HTML to PDF using Playwright"""
        try:
            import asyncio
            from playwright.async_api import async_playwright
            
            async def _convert():
                async with async_playwright() as p:
                    browser = await p.chromium.launch()
                    page = await browser.new_page()
                    
                    # Set content
                    await page.set_content(html_content)
                    
                    # Generate PDF with A4 settings
                    pdf_bytes = await page.pdf(
                        format='A4',
                        margin={
                            'top': '10mm',
                            'right': '10mm',
                            'bottom': '10mm',
                            'left': '10mm'
                        },
                        print_background=True,
                        prefer_css_page_size=True
                    )
                    
                    await browser.close()
                    return pdf_bytes
            
            # Run async conversion
            return asyncio.run(_convert())
            
        except Exception as e:
            logger.error(f"Playwright conversion error: {str(e)}")
            raise
    
    def _convert_with_xhtml2pdf(self, html_content: str) -> bytes:
        """Convert HTML to PDF using xhtml2pdf"""
        try:
            from xhtml2pdf import pisa
            from io import BytesIO
            
            buffer = BytesIO()
            
            # Convert HTML to PDF
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=buffer,
                encoding='utf-8',
                link_callback=None
            )
            
            if pisa_status.err:
                raise Exception(f"xhtml2pdf error: {pisa_status.err}")
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"xhtml2pdf conversion error: {str(e)}")
            raise
    
    def _convert_with_reportlab_fallback(self, doc_name: str, html_content: str) -> bytes:
        """Fallback PDF generation using ReportLab"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import mm
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_LEFT, TA_CENTER
            from io import BytesIO
            import re
            
            buffer = BytesIO()
            
            # Create document with A4 size and 10mm margins
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                leftMargin=10*mm,
                rightMargin=10*mm,
                topMargin=10*mm,
                bottomMargin=10*mm
            )
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=12,
                alignment=TA_CENTER
            )
            
            # Parse HTML content (simplified)
            content = []
            
            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
            if title_match:
                content.append(Paragraph(title_match.group(1), title_style))
                content.append(Spacer(1, 12))
            
            # Extract tables
            table_match = re.search(r'<table.*?>(.*?)</table>', html_content, re.DOTALL | re.IGNORECASE)
            if table_match:
                table_html = table_match.group(1)
                
                # Parse table rows
                rows = re.findall(r'<tr.*?>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE)
                table_data = []
                
                for row in rows:
                    cells = re.findall(r'<t[hd].*?>(.*?)</t[hd]>', row, re.DOTALL | re.IGNORECASE)
                    if cells:
                        # Clean cell content
                        clean_cells = []
                        for cell in cells:
                            clean_cell = re.sub(r'<[^>]+>', '', cell).strip()
                            clean_cells.append(clean_cell)
                        table_data.append(clean_cells)
                
                if table_data:
                    # Create table
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    content.append(table)
            
            # Build PDF
            doc.build(content)
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"ReportLab fallback error: {str(e)}")
            raise
    
    def _create_error_pdf(self, doc_name: str, error_msg: str) -> bytes:
        """Create a simple error PDF"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import mm
            from io import BytesIO
            
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            
            # Set margins
            c.setFont("Helvetica-Bold", 16)
            c.drawString(10*mm, 250*mm, f"Error generating {doc_name}")
            
            c.setFont("Helvetica", 12)
            c.drawString(10*mm, 230*mm, f"Error: {error_msg[:100]}")
            
            c.drawString(10*mm, 210*mm, "Please check the input data and try again.")
            
            c.save()
            return buffer.getvalue()
            
        except:
            # Ultimate fallback: minimal PDF
            return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF"
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """Get conversion statistics"""
        return self.conversion_stats.copy()
    
    def validate_pdf_quality(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Validate PDF quality and return metrics"""
        quality_metrics = {
            'file_size': len(pdf_bytes),
            'is_valid_pdf': False,
            'has_content': False,
            'quality_score': 0
        }
        
        try:
            # Check if it's a valid PDF
            if pdf_bytes.startswith(b'%PDF-'):
                quality_metrics['is_valid_pdf'] = True
                quality_metrics['quality_score'] += 30
            
            # Check file size (should be > 10KB for proper documents)
            if len(pdf_bytes) > 10240:  # 10KB
                quality_metrics['has_content'] = True
                quality_metrics['quality_score'] += 40
            
            # Check for content indicators
            if b'stream' in pdf_bytes and b'endstream' in pdf_bytes:
                quality_metrics['quality_score'] += 30
            
            # Overall quality assessment
            if quality_metrics['quality_score'] >= 70:
                quality_metrics['quality_grade'] = 'A'
            elif quality_metrics['quality_score'] >= 50:
                quality_metrics['quality_grade'] = 'B'
            elif quality_metrics['quality_score'] >= 30:
                quality_metrics['quality_grade'] = 'C'
            else:
                quality_metrics['quality_grade'] = 'F'
                
        except Exception as e:
            logger.error(f"PDF quality validation error: {str(e)}")
        
        return quality_metrics

def main():
    """Test the PDF converter"""
    converter = OptimizedPDFConverter()
    
    # Test HTML content
    test_html = """
    <html>
    <head><title>Test Document</title></head>
    <body>
        <h1>Test Bill Document</h1>
        <table border="1">
            <tr><th>Item</th><th>Quantity</th><th>Rate</th><th>Amount</th></tr>
            <tr><td>Test Item 1</td><td>10</td><td>100.00</td><td>1000.00</td></tr>
            <tr><td>Test Item 2</td><td>5</td><td>200.00</td><td>1000.00</td></tr>
        </table>
    </body>
    </html>
    """
    
    # Convert to PDF
    documents = {'test_document': test_html}
    pdf_files = converter.convert_documents_to_pdf(documents)
    
    # Validate quality
    for name, pdf_bytes in pdf_files.items():
        quality = converter.validate_pdf_quality(pdf_bytes)
        print(f"PDF: {name}")
        print(f"Size: {quality['file_size']:,} bytes")
        print(f"Quality Grade: {quality['quality_grade']}")
        print(f"Valid PDF: {quality['is_valid_pdf']}")
        print()

if __name__ == "__main__":
    main()
