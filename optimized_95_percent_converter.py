#!/usr/bin/env python3
"""
Optimized HTML-to-PDF Converter for 95%+ Matching
Specifically designed to handle the complex government document templates
"""

import re
import io
from typing import Dict, Any
from bs4 import BeautifulSoup

class OptimizedConverter95Percent:
    """Optimized converter specifically for 95%+ matching requirement"""
    
    def __init__(self):
        self.successful_conversions = 0
        self.total_conversions = 0
    
    def convert_documents_to_pdf(self, documents: Dict[str, str]) -> Dict[str, bytes]:
        """
        Convert HTML documents to PDF with optimized 95%+ matching
        
        Args:
            documents: Dictionary of HTML documents
            
        Returns:
            Dictionary of PDF documents as bytes
        """
        pdf_files = {}
        
        for doc_name, html_content in documents.items():
            self.total_conversions += 1
            print(f"🔄 Converting {doc_name} to PDF (Optimized 95%+ mode)...")
            
            try:
                # Use specialized processing for each document type
                pdf_bytes = self._specialized_conversion(html_content, doc_name)
                
                if pdf_bytes and len(pdf_bytes) > 0:
                    pdf_files[f"{doc_name}.pdf"] = pdf_bytes
                    self.successful_conversions += 1
                    print(f"  ✅ Successfully converted {doc_name} ({len(pdf_bytes)} bytes)")
                else:
                    raise Exception("PDF conversion produced empty result")
                    
            except Exception as e:
                print(f"  ❌ Error converting {doc_name}: {str(e)}")
                # Create error PDF
                error_pdf = self._create_simple_pdf_fallback(doc_name, str(e))
                pdf_files[f"{doc_name}.pdf"] = error_pdf
        
        success_rate = (self.successful_conversions / self.total_conversions) * 100 if self.total_conversions > 0 else 0
        print(f"\n📊 Conversion Success Rate: {success_rate:.1f}% ({self.successful_conversions}/{self.total_conversions})")
        
        return pdf_files
    
    def _specialized_conversion(self, html_content: str, doc_name: str) -> bytes:
        """Apply specialized conversion based on document type"""
        
        # Identify document type and apply specific optimizations
        if "certificate" in doc_name.lower():
            return self._convert_certificate_document(html_content, doc_name)
        elif "deviation" in doc_name.lower():
            return self._convert_deviation_document(html_content, doc_name)
        elif "extra" in doc_name.lower() and "item" in doc_name.lower():
            return self._convert_extra_items_document(html_content, doc_name)
        elif "final" in doc_name.lower() and "bill" in doc_name.lower():
            return self._convert_final_bill_document(html_content, doc_name)
        elif "first" in doc_name.lower() and "page" in doc_name.lower():
            return self._convert_first_page_document(html_content, doc_name)
        else:
            # Generic conversion for other documents
            return self._convert_generic_document(html_content, doc_name)
    
    def _convert_certificate_document(self, html_content: str, doc_name: str) -> bytes:
        """Convert certificate documents with optimized settings"""
        try:
            from xhtml2pdf import pisa
            
            # Certificate-specific preprocessing
            processed_html = self._preprocess_certificate(html_content)
            
            output = io.BytesIO()
            result = pisa.CreatePDF(
                src=processed_html,
                dest=output,
                encoding="utf-8",
                raise_exception=False
            )
            
            if result.err:
                print(f"    ⚠️ Certificate conversion warnings: {result.err}")
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            print(f"    ❌ Certificate conversion failed, trying WeasyPrint: {str(e)}")
            return self._convert_with_weasyprint(html_content, doc_name)
    
    def _convert_deviation_document(self, html_content: str, doc_name: str) -> bytes:
        """Convert deviation documents with table optimization"""
        try:
            from xhtml2pdf import pisa
            
            # Deviation-specific preprocessing for complex tables
            processed_html = self._preprocess_deviation_statement(html_content)
            
            output = io.BytesIO()
            result = pisa.CreatePDF(
                src=processed_html,
                dest=output,
                encoding="utf-8",
                raise_exception=False
            )
            
            if result.err:
                print(f"    ⚠️ Deviation conversion warnings: {result.err}")
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            print(f"    ❌ Deviation conversion failed, trying WeasyPrint: {str(e)}")
            return self._convert_with_weasyprint(html_content, doc_name)
    
    def _convert_extra_items_document(self, html_content: str, doc_name: str) -> bytes:
        """Convert extra items documents"""
        try:
            from xhtml2pdf import pisa
            
            # Extra items preprocessing
            processed_html = self._preprocess_extra_items(html_content)
            
            output = io.BytesIO()
            result = pisa.CreatePDF(
                src=processed_html,
                dest=output,
                encoding="utf-8",
                raise_exception=False
            )
            
            if result.err:
                print(f"    ⚠️ Extra items conversion warnings: {result.err}")
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            print(f"    ❌ Extra items conversion failed, trying WeasyPrint: {str(e)}")
            return self._convert_with_weasyprint(html_content, doc_name)
    
    def _convert_final_bill_document(self, html_content: str, doc_name: str) -> bytes:
        """Convert final bill documents"""
        try:
            from xhtml2pdf import pisa
            
            # Final bill preprocessing
            processed_html = self._preprocess_final_bill(html_content)
            
            output = io.BytesIO()
            result = pisa.CreatePDF(
                src=processed_html,
                dest=output,
                encoding="utf-8",
                raise_exception=False
            )
            
            if result.err:
                print(f"    ⚠️ Final bill conversion warnings: {result.err}")
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            print(f"    ❌ Final bill conversion failed, trying WeasyPrint: {str(e)}")
            return self._convert_with_weasyprint(html_content, doc_name)
    
    def _convert_first_page_document(self, html_content: str, doc_name: str) -> bytes:
        """Convert first page documents"""
        try:
            from xhtml2pdf import pisa
            
            # First page preprocessing
            processed_html = self._preprocess_first_page(html_content)
            
            output = io.BytesIO()
            result = pisa.CreatePDF(
                src=processed_html,
                dest=output,
                encoding="utf-8",
                raise_exception=False
            )
            
            if result.err:
                print(f"    ⚠️ First page conversion warnings: {result.err}")
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            print(f"    ❌ First page conversion failed, trying WeasyPrint: {str(e)}")
            return self._convert_with_weasyprint(html_content, doc_name)
    
    def _convert_generic_document(self, html_content: str, doc_name: str) -> bytes:
        """Convert generic documents"""
        try:
            from xhtml2pdf import pisa
            
            # Generic preprocessing
            processed_html = self._preprocess_generic(html_content)
            
            output = io.BytesIO()
            result = pisa.CreatePDF(
                src=processed_html,
                dest=output,
                encoding="utf-8",
                raise_exception=False
            )
            
            if result.err:
                print(f"    ⚠️ Generic conversion warnings: {result.err}")
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            print(f"    ❌ Generic conversion failed, trying WeasyPrint: {str(e)}")
            return self._convert_with_weasyprint(html_content, doc_name)
    
    def _preprocess_certificate(self, html_content: str) -> str:
        """Preprocess certificate documents"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Simplify CSS that causes issues
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                css = style_tag.string
                # Remove complex CSS functions
                css = re.sub(r'\w+\([^)]*\)[\w\-]*\([^)]*\)', '', css)
                # Convert units safely
                css = re.sub(r'(\d+(?:\.\d+)?)mm', lambda m: f"{float(m.group(1)) * 3.78:.2f}px", css)
                # Remove problematic properties
                css = css.replace('box-sizing: border-box;', '')
                css = css.replace('break-inside: avoid;', '')
                style_tag.string = css
        
        return str(soup)
    
    def _preprocess_deviation_statement(self, html_content: str) -> str:
        """Preprocess deviation statement with table optimization"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Optimize complex tables
        for table in soup.find_all('table'):
            # Remove complex column specifications that cause issues
            for colgroup in table.find_all('colgroup'):
                colgroup.decompose()
            
            # Simplify table styling
            if table.get('class'):
                table['class'] = ' '.join([cls for cls in table['class'] if 'deviation' not in cls.lower()])
        
        # Simplify CSS
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                css = style_tag.string
                # Remove complex CSS that causes parsing errors
                css = re.sub(r'\w+\([^)]*\)[\w\-]*\([^)]*\)', '', css)
                # Convert units
                css = re.sub(r'(\d+(?:\.\d+)?)mm', lambda m: f"{float(m.group(1)) * 3.78:.2f}px", css)
                # Remove problematic properties
                css = css.replace('box-sizing: border-box;', '')
                css = css.replace('break-inside: avoid;', '')
                # Keep table layout for width consistency
                style_tag.string = css
        
        return str(soup)
    
    def _preprocess_extra_items(self, html_content: str) -> str:
        """Preprocess extra items documents"""
        return self._preprocess_generic(html_content)
    
    def _preprocess_final_bill(self, html_content: str) -> str:
        """Preprocess final bill documents"""
        return self._preprocess_generic(html_content)
    
    def _preprocess_first_page(self, html_content: str) -> str:
        """Preprocess first page documents"""
        return self._preprocess_generic(html_content)
    
    def _preprocess_generic(self, html_content: str) -> str:
        """Generic preprocessing for all documents"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove complex CSS that causes parsing errors
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                css = style_tag.string
                # Remove nested CSS functions that cause 'CSSTerminalFunction' errors
                css = re.sub(r'\w+\([^)]*\)[\w\-]*\([^)]*\)', '', css)
                # Convert units safely
                css = re.sub(r'(\d+(?:\.\d+)?)mm', lambda m: f"{float(m.group(1)) * 3.78:.2f}px", css)
                # Remove only problematic properties
                css = css.replace('box-sizing: border-box;', '')
                css = css.replace('break-inside: avoid;', '')
                style_tag.string = css
        
        return str(soup)
    
    def _convert_with_weasyprint(self, html_content: str, doc_name: str) -> bytes:
        """Fallback conversion using WeasyPrint"""
        try:
            from weasyprint import HTML
            from concurrent.futures import ThreadPoolExecutor, TimeoutError
            
            # Preprocess for WeasyPrint
            processed_html = self._preprocess_for_weasyprint(html_content)
            
            # Use timeout to prevent hanging
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(lambda: HTML(string=processed_html).write_pdf())
                pdf_bytes = future.result(timeout=30)
            
            if pdf_bytes and len(pdf_bytes) > 0:
                print(f"    ✅ WeasyPrint successful for {doc_name}")
                return pdf_bytes
            else:
                raise Exception("WeasyPrint produced empty PDF")
                
        except Exception as e:
            print(f"    ❌ WeasyPrint also failed: {str(e)}")
            raise
    
    def _preprocess_for_weasyprint(self, html_content: str) -> str:
        """Preprocess HTML for WeasyPrint compatibility"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Ensure proper DOCTYPE
            if not str(soup).startswith('<!DOCTYPE'):
                return '<!DOCTYPE html>' + str(soup)
            
            return str(soup)
        except:
            return html_content
    
    def _create_simple_pdf_fallback(self, doc_name: str, error_msg: str) -> bytes:
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

def test_optimized_converter():
    """Test the optimized converter"""
    print("🧪 Testing Optimized 95%+ Converter...")
    
    # Sample HTML content
    sample_documents = {
        "Test Certificate": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Certificate</title>
            <style>
                body { font-family: Arial, sans-serif; font-size: 10pt; }
                .manual-entry { border-bottom: 1px dashed #000; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #000; padding: 4px; }
            </style>
        </head>
        <body>
            <h2>Test Certificate</h2>
            <p>Document generated on: 18/09/2025</p>
            <p>Contractor: <span class="manual-entry">Test Contractor</span></p>
            <table>
                <tr><th>Item</th><th>Description</th><th>Amount</th></tr>
                <tr><td>1</td><td>Test Item</td><td>100.00</td></tr>
            </table>
        </body>
        </html>
        """
    }
    
    converter = OptimizedConverter95Percent()
    pdf_results = converter.convert_documents_to_pdf(sample_documents)
    
    print(f"✅ Generated {len(pdf_results)} PDF documents")
    for name, content in pdf_results.items():
        print(f"   - {name}: {len(content)} bytes")
    
    return pdf_results

if __name__ == "__main__":
    test_optimized_converter()