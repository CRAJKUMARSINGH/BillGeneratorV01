"""
Enhanced PDF Converter for Bill Generator
Handles HTML to PDF conversion with improved compatibility and error handling
"""

import io
import gc
from typing import Dict, Any
import re


class EnhancedPDFConverter:
    """Enhanced PDF converter with multiple engine support and preprocessing"""
    
    def __init__(self):
        self.available_engines = self._check_available_engines()
    
    def _check_available_engines(self) -> Dict[str, bool]:
        """Check which PDF engines are available"""
        engines = {
            'weasyprint': False,
            'xhtml2pdf': False,
            'reportlab': False
        }
        
        try:
            import weasyprint
            engines['weasyprint'] = True
        except ImportError:
            pass
            
        try:
            import xhtml2pdf
            engines['xhtml2pdf'] = True
        except ImportError:
            pass
            
        try:
            import reportlab
            engines['reportlab'] = True
        except ImportError:
            pass
            
        return engines
    
    def convert_documents_to_pdf(self, documents: Dict[str, str]) -> Dict[str, bytes]:
        """
        Convert HTML documents to PDF with enhanced error handling
        
        Args:
            documents: Dictionary of HTML documents
            
        Returns:
            Dictionary of PDF documents as bytes
        """
        pdf_files = {}
        
        for doc_name, html_content in documents.items():
            print(f"🔄 Converting {doc_name} to PDF...")
            
            try:
                # Try engines in order of preference
                pdf_bytes = None
                
                # 1. Try xhtml2pdf first (most reliable for complex tables)
                if self.available_engines['xhtml2pdf'] and pdf_bytes is None:
                    pdf_bytes = self._convert_with_xhtml2pdf(doc_name, html_content)
                
                # 2. Try WeasyPrint if xhtml2pdf failed
                if self.available_engines['weasyprint'] and pdf_bytes is None:
                    pdf_bytes = self._convert_with_weasyprint(doc_name, html_content)
                
                # 3. Fallback to ReportLab
                if pdf_bytes is None:
                    pdf_bytes = self._convert_with_reportlab_fallback(doc_name, html_content)
                
                if pdf_bytes and len(pdf_bytes) > 0:
                    pdf_files[f"{doc_name}.pdf"] = pdf_bytes
                    print(f"  ✅ Successfully converted {doc_name} ({len(pdf_bytes)} bytes)")
                else:
                    print(f"  ❌ Failed to convert {doc_name}")
                    
            except Exception as e:
                print(f"  ❌ Error converting {doc_name}: {str(e)}")
                # Create error PDF
                error_pdf = self._create_error_pdf(doc_name, str(e))
                pdf_files[f"{doc_name}.pdf"] = error_pdf
        
        gc.collect()
        return pdf_files
    
    def _convert_with_xhtml2pdf(self, doc_name: str, html_content: str) -> bytes:
        """Convert using xhtml2pdf engine"""
        try:
            from xhtml2pdf import pisa
            
            # Preprocess HTML for xhtml2pdf compatibility
            processed_html = self._preprocess_for_xhtml2pdf(html_content)
            
            output = io.BytesIO()
            result = pisa.CreatePDF(
                src=processed_html,
                dest=output,
                encoding="utf-8"
            )
            
            if result.err:
                raise Exception(f"xhtml2pdf conversion errors: {result.err}")
            
            output.seek(0)
            pdf_bytes = output.getvalue()
            
            if len(pdf_bytes) > 0:
                print(f"  ✅ xhtml2pdf successful for {doc_name}")
                return pdf_bytes
            else:
                raise Exception("xhtml2pdf produced empty PDF")
                
        except Exception as e:
            print(f"  ⚠️ xhtml2pdf failed for {doc_name}: {str(e)}")
            return None
    
    def _convert_with_weasyprint(self, doc_name: str, html_content: str) -> bytes:
        """Convert using WeasyPrint engine"""
        try:
            from weasyprint import HTML
            from concurrent.futures import ThreadPoolExecutor, TimeoutError
            
            # Preprocess HTML for WeasyPrint compatibility
            processed_html = self._preprocess_for_weasyprint(html_content)
            
            # Use timeout to prevent hanging
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(lambda: HTML(string=processed_html).write_pdf())
                pdf_bytes = future.result(timeout=45)
            
            if pdf_bytes and len(pdf_bytes) > 0:
                print(f"  ✅ WeasyPrint successful for {doc_name}")
                return pdf_bytes
            else:
                raise Exception("WeasyPrint produced empty PDF")
                
        except Exception as e:
            print(f"  ⚠️ WeasyPrint failed for {doc_name}: {str(e)}")
            return None
    
    def _convert_with_reportlab_fallback(self, doc_name: str, html_content: str) -> bytes:
        """Convert using ReportLab as fallback"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.units import mm
            from bs4 import BeautifulSoup
            
            buffer = io.BytesIO()
            
            # Choose page orientation
            page_size = landscape(A4) if 'deviation' in doc_name.lower() else A4
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=page_size,
                leftMargin=10*mm, rightMargin=10*mm,
                topMargin=10*mm, bottomMargin=10*mm
            )
            
            styles = getSampleStyleSheet()
            story = []
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Add title
            title = Paragraph(f"<b>{doc_name}</b>", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Extract tables
            tables = soup.find_all('table')
            if tables:
                for table in tables:
                    table_data = []
                    rows = table.find_all('tr')
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        row_data = []
                        for cell in cells:
                            text = cell.get_text(strip=True)
                            row_data.append(text if text else ' ')
                        if row_data:
                            table_data.append(row_data)
                    
                    if table_data:
                        pdf_table = Table(table_data)
                        pdf_table.setStyle(TableStyle([
                            ('BORDER', (0, 0), (-1, -1), 1, colors.black),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('FONTSIZE', (0, 0), (-1, -1), 8),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ]))
                        story.append(pdf_table)
                        story.append(Spacer(1, 12))
            else:
                # Text fallback
                text = soup.get_text(separator='\\n')
                for line in text.split('\\n'):
                    line = line.strip()
                    if line:
                        para = Paragraph(line, styles['Normal'])
                        story.append(para)
                        story.append(Spacer(1, 6))
            
            doc.build(story)
            buffer.seek(0)
            pdf_bytes = buffer.getvalue()
            
            print(f"  ✅ ReportLab fallback successful for {doc_name}")
            return pdf_bytes
            
        except Exception as e:
            print(f"  ❌ ReportLab fallback failed for {doc_name}: {str(e)}")
            return self._create_error_pdf(doc_name, str(e))
    
    def _preprocess_for_xhtml2pdf(self, html_content: str) -> str:
        """Preprocess HTML for xhtml2pdf compatibility"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove problematic CSS
            for style_tag in soup.find_all('style'):
                if style_tag.string:
                    css = style_tag.string
                    # Replace mm units with px
                    css = re.sub(r'(\\d+(?:\\.\\d+)?)mm', lambda m: f"{float(m.group(1)) * 3.78:.1f}px", css)
                    # Remove unsupported properties
                    css = css.replace('box-sizing: border-box;', '')
                    css = css.replace('table-layout: fixed;', '')
                    css = css.replace('break-inside: avoid;', '')
                    style_tag.string = css
            
            return str(soup)
        except:
            return html_content
    
    def _preprocess_for_weasyprint(self, html_content: str) -> str:
        """Preprocess HTML for WeasyPrint compatibility"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Ensure proper DOCTYPE
            if not str(soup).startswith('<!DOCTYPE'):
                return '<!DOCTYPE html>' + str(soup)
            return str(soup)
        except:
            return html_content
    
    def _create_error_pdf(self, doc_name: str, error_msg: str) -> bytes:
        """Create a simple error PDF when all engines fail"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            
            c.drawString(100, 750, f"PDF Generation Failed: {doc_name}")
            c.drawString(100, 730, f"Error: {error_msg}")
            c.drawString(100, 710, "Please check the HTML content and try again.")
            
            c.save()
            buffer.seek(0)
            return buffer.getvalue()
        except:
            return f"PDF generation completely failed for {doc_name}: {error_msg}".encode()