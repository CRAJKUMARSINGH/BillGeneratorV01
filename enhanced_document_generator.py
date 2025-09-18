#!/usr/bin/env python3
"""
Enhanced Document Generator with Fixed HTML-to-PDF Conversion
Implements all the critical fixes for PDF distortion issues
"""

import pandas as pd
import gc
from datetime import datetime
from typing import Dict, Any
import io
from functools import lru_cache
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError

class EnhancedDocumentGenerator:
    """Enhanced document generator with fixed HTML-to-PDF conversion"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.title_data = data.get('title_data', {})
        self.work_order_data = data.get('work_order_data', pd.DataFrame())
        self.bill_quantity_data = data.get('bill_quantity_data', pd.DataFrame())
        self.extra_items_data = data.get('extra_items_data', pd.DataFrame())
        
        # Set up Jinja2 environment for templates
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Prepare data for templates
        self.template_data = self._prepare_template_data()
    
    def _number_to_words(self, num):
        """Convert number to words (simplified version)"""
        if num == 0:
            return "Zero"
        
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
        teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        def convert_hundreds(n):
            result = ''
            if n >= 100:
                result += ones[n // 100] + ' Hundred '
                n %= 100
            if n >= 20:
                result += tens[n // 10] + ' '
                n %= 10
            elif n >= 10:
                result += teens[n - 10] + ' '
                n = 0
            if n > 0:
                result += ones[n] + ' '
            return result.strip()
        
        if num < 1000:
            return convert_hundreds(num)
        elif num < 100000:
            thousands = num // 1000
            remainder = num % 1000
            result = convert_hundreds(thousands) + ' Thousand '
            if remainder > 0:
                result += convert_hundreds(remainder)
            return result.strip()
        else:
            lakhs = num // 100000
            remainder = num % 100000
            result = convert_hundreds(lakhs) + ' Lakh '
            if remainder > 0:
                if remainder >= 1000:
                    result += convert_hundreds(remainder // 1000) + ' Thousand '
                    remainder %= 1000
                if remainder > 0:
                    result += convert_hundreds(remainder)
            return result.strip()
    
    def _safe_float(self, value):
        """Safely convert value to float, return 0 if conversion fails"""
        try:
            if pd.isna(value) or value == '' or value is None:
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _format_number(self, value, show_zero=False):
        """Format number with conditional display for zero values"""
        num_value = self._safe_float(value)
        if num_value == 0 and not show_zero:
            return ""
        return f"{num_value:.2f}"
    
    def _format_unit_or_text(self, value):
        """Format unit or text field, return empty string for NaN/None"""
        if pd.isna(value) or value is None or str(value).lower() in ['nan', 'none']:
            return ""
        return str(value).strip()
    
    def _safe_serial_no(self, value):
        """Safely convert serial number, return empty string if NaN or None"""
        if pd.isna(value) or value is None or str(value).lower() == 'nan':
            return ''
        return str(value).strip()
    
    def _find_column(self, df, possible_names):
        """Find column by trying multiple possible names"""
        for name in possible_names:
            if name in df.columns:
                return name
        return None
    
    def _has_extra_items(self):
        """Check if there are any extra items"""
        if isinstance(self.extra_items_data, pd.DataFrame):
            return not self.extra_items_data.empty and len(self.extra_items_data) > 0
        elif isinstance(self.extra_items_data, (list, tuple)):
            return len(self.extra_items_data) > 0
        else:
            return False
    
    def _prepare_template_data(self) -> Dict[str, Any]:
        """Prepare data structure for Jinja2 templates"""
        # Calculate totals and prepare structured data
        work_items = []
        total_amount = 0
        
        # Process work order data
        for index, row in self.work_order_data.iterrows():
            quantity_since = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
            rate = self._safe_float(row.get('Rate', 0))
            amount = quantity_since * rate
            total_amount += amount
            
            work_items.append({
                'unit': self._format_unit_or_text(row.get('Unit', '')),
                'quantity_since': quantity_since,
                'quantity_upto': self._safe_float(row.get('Quantity Upto', quantity_since)),
                'item_no': self._safe_serial_no(row.get('Item No.', row.get('Item', ''))),
                'description': row.get('Description', ''),
                'rate': rate,
                'amount_upto': amount,
                'amount_since': amount,
                'remark': row.get('Remark', '')
            })
        
        # Process extra items
        extra_items = []
        extra_total = 0
        
        if isinstance(self.extra_items_data, pd.DataFrame) and not self.extra_items_data.empty:
            for index, row in self.extra_items_data.iterrows():
                quantity = self._safe_float(row.get('Quantity', 0))
                rate = self._safe_float(row.get('Rate', 0))
                amount = quantity * rate
                extra_total += amount
                
                extra_items.append({
                    'unit': self._format_unit_or_text(row.get('Unit', '')),
                    'quantity': quantity,
                    'item_no': self._safe_serial_no(row.get('Item No.', row.get('Item', ''))),
                    'description': row.get('Description', ''),
                    'rate': rate,
                    'amount': amount,
                    'remark': row.get('Remark', '')
                })
        
        # Calculate premiums
        tender_premium_percent = self._safe_float(self.title_data.get('TENDER PREMIUM %', 0))
        premium_amount = total_amount * (tender_premium_percent / 100)
        grand_total = total_amount + premium_amount
        
        extra_premium = extra_total * (tender_premium_percent / 100)
        extra_grand_total = extra_total + extra_premium
        
        # Calculate deductions and final amounts
        sd_amount = grand_total * 0.10  # Security Deposit 10%
        it_amount = grand_total * 0.02  # Income Tax 2%
        gst_amount = grand_total * 0.02  # GST 2%
        lc_amount = grand_total * 0.01  # Labour Cess 1%
        total_deductions = sd_amount + it_amount + gst_amount + lc_amount
        net_payable = grand_total - total_deductions
        
        # Calculate totals data structure
        totals = {
            'grand_total': grand_total,
            'work_order_amount': total_amount,
            'tender_premium_percent': tender_premium_percent / 100,
            'tender_premium_amount': premium_amount,
            'final_total': grand_total,
            'extra_items_sum': extra_grand_total,
            'sd_amount': sd_amount,
            'it_amount': it_amount,
            'gst_amount': gst_amount,
            'lc_amount': lc_amount,
            'total_deductions': total_deductions,
            'net_payable': net_payable,
            'excess_amount': 0,  # Will be calculated from deviation data
            'excess_premium': 0,
            'excess_total': 0,
            'saving_amount': 0,
            'saving_premium': 0,
            'saving_total': 0,
            'net_difference': 0
        }
        
        return {
            'title_data': self.title_data,
            'work_items': work_items,
            'extra_items': extra_items,
            'totals': totals,
            'current_date': datetime.now().strftime('%d/%m/%Y'),
            'total_amount': total_amount,
            'tender_premium_percent': tender_premium_percent,
            'premium_amount': premium_amount,
            'grand_total': grand_total,
            'extra_total': extra_total,
            'extra_premium': extra_premium,
            'extra_grand_total': extra_grand_total,
            'final_total': grand_total + extra_grand_total,
            'payable_words': self._number_to_words(int(net_payable)),
            'notes': ['Work completed as per schedule', 'All measurements verified', 'Quality as per specifications']
        }
    
    def generate_all_documents(self) -> Dict[str, str]:
        """
        Generate all required documents using Jinja2 templates
        
        Returns:
            Dictionary containing all generated documents in HTML format
        """
        documents = {}
        
        try:
            # Generate individual documents using templates
            documents['First Page Summary'] = self._render_template('first_page.html')
            documents['Deviation Statement'] = self._render_template('deviation_statement.html') 
            documents['Final Bill Scrutiny Sheet'] = self._render_template('note_sheet.html')
            
            # Only generate Extra Items document if there are extra items
            if self._has_extra_items():
                documents['Extra Items Statement'] = self._render_template('extra_items.html')
            
            documents['Certificate II'] = self._render_template('certificate_ii.html')
            documents['Certificate III'] = self._render_template('certificate_iii.html')
        except Exception as e:
            print(f"Template rendering failed, falling back to programmatic generation: {e}")
            # Fallback to programmatic generation if templates fail
            documents['First Page Summary'] = self._generate_first_page()
            documents['Deviation Statement'] = self._generate_deviation_statement()
            documents['Final Bill Scrutiny Sheet'] = self._generate_final_bill_scrutiny()
            
            # Only generate Extra Items document if there are extra items
            if self._has_extra_items():
                documents['Extra Items Statement'] = self._generate_extra_items_statement()
            
            documents['Certificate II'] = self._generate_certificate_ii()
            documents['Certificate III'] = self._generate_certificate_iii()
        
        return documents
    
    def _render_template(self, template_name: str) -> str:
        """Render a Jinja2 template with the prepared data"""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**self.template_data)
        except Exception as e:
            print(f"Failed to render template {template_name}: {e}")
            raise
    
    def create_pdf_documents_fixed(self, documents: Dict[str, str]) -> Dict[str, bytes]:
        """
        FIXED: Convert HTML documents to PDF with proper formatting and no distortion
        
        Args:
            documents: Dictionary of HTML documents
            
        Returns:
            Dictionary of PDF documents as bytes
        """
        pdf_files = {}

        # Initialize PDF engines with better error handling
        render_with_weasy = None
        render_with_xhtml2pdf = None
        render_with_playwright = None
        
        # Try WeasyPrint with timeout protection (RECOMMENDED)
        try:
            from weasyprint import HTML, CSS
            def render_with_weasy(html_str: str) -> bytes:
                # Enhanced WeasyPrint with proper CSS
                try:
                    # Add print-specific CSS to prevent distortion
                    enhanced_html = self._add_print_css(html_str)
                    
                    # Use ThreadPoolExecutor with timeout to prevent hanging
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(lambda: HTML(string=enhanced_html, base_url=".").write_pdf())
                        return future.result(timeout=45)  # 45 second timeout
                except Exception as e:
                    raise Exception(f"WeasyPrint timeout or error: {str(e)}")
            render_with_weasy = render_with_weasy
        except ImportError:
            render_with_weasy = None
            
        # Fallback to xhtml2pdf with enhanced options
        try:
            from xhtml2pdf import pisa
            import io as _io
            def render_with_xhtml2pdf(html_str: str) -> bytes:
                # Enhanced xhtml2pdf with proper options to prevent distortion
                clean_html = self._enhance_html_for_pdf(html_str)
                
                output = _io.BytesIO()
                result = pisa.CreatePDF(
                    src=clean_html, 
                    dest=output, 
                    encoding="utf-8",
                    print_media=True,  # CRITICAL: Uses print CSS
                    disable_smart_shrinking=True,  # Prevents unwanted scaling
                    dpi=300,  # High quality
                    raise_exception=False
                )
                if hasattr(result, 'err') and result.err:
                    raise Exception(f"xhtml2pdf error: {result.err}")
                return output.getvalue()
            render_with_xhtml2pdf = render_with_xhtml2pdf
        except ImportError:
            render_with_xhtml2pdf = None

        # Process each document with robust error handling
        for doc_name, html_content in documents.items():
            pdf_bytes: bytes
            print(f"🔄 Processing {doc_name} for PDF conversion (FIXED)...")
            
            # First try WeasyPrint (recommended for best results)
            if render_with_weasy is not None:
                try:
                    print(f"  📄 Using WeasyPrint for {doc_name} (enhanced)...")
                    pdf_bytes = render_with_weasy(html_content)
                    print(f"  ✅ WeasyPrint successful for {doc_name} ({len(pdf_bytes)} bytes)")
                except Exception as e:
                    print(f"  ❌ WeasyPrint failed for {doc_name}: {str(e)}")
                    # Try xhtml2pdf as fallback
                    if render_with_xhtml2pdf is not None:
                        try:
                            print(f"  📄 Trying xhtml2pdf as fallback for {doc_name}...")
                            pdf_bytes = render_with_xhtml2pdf(html_content)
                            print(f"  ✅ xhtml2pdf successful for {doc_name} ({len(pdf_bytes)} bytes)")
                        except Exception as e2:
                            print(f"  ❌ xhtml2pdf also failed for {doc_name}: {str(e2)}")
                            pdf_bytes = self._create_simple_pdf_fallback(doc_name, html_content)
                    else:
                        pdf_bytes = self._create_simple_pdf_fallback(doc_name, html_content)
            # If WeasyPrint not available, try xhtml2pdf
            elif render_with_xhtml2pdf is not None:
                try:
                    print(f"  📄 Using xhtml2pdf for {doc_name} (enhanced)...")
                    pdf_bytes = render_with_xhtml2pdf(html_content)
                    print(f"  ✅ xhtml2pdf successful for {doc_name} ({len(pdf_bytes)} bytes)")
                except Exception as e:
                    print(f"  ❌ xhtml2pdf failed for {doc_name}: {str(e)}")
                    pdf_bytes = self._create_simple_pdf_fallback(doc_name, html_content)
            else:
                # No PDF engine available
                print(f"  ⚠️ No PDF engine available for {doc_name}, using fallback")
                pdf_bytes = self._create_simple_pdf_fallback(doc_name, html_content)
                    
            pdf_files[f"{doc_name}.pdf"] = pdf_bytes
        
        # Memory cleanup
        gc.collect()
        return pdf_files
    
    def _add_print_css(self, html_content: str) -> str:
        """Add enhanced print CSS to prevent PDF distortion"""
        # Enhanced print CSS to prevent distortion
        print_css = """
        <style>
        /* CRITICAL: Enhanced print CSS to prevent PDF distortion */
        @media print {
            * {
                -webkit-print-color-adjust: exact !important;
                color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            
            body {
                margin: 0;
                padding: 20px;
                font-family: Arial, sans-serif;
                font-size: 12px;
                line-height: 1.4;
            }
            
            /* Table fixes to prevent distortion */
            table {
                width: 100% !important;
                border-collapse: collapse;
                page-break-inside: auto;
                table-layout: fixed;
            }
            
            tr {
                page-break-inside: avoid;
                page-break-after: auto;
            }
            
            td, th {
                page-break-inside: avoid;
                page-break-after: auto;
                word-wrap: break-word;
                padding: 8px;
                border: 1px solid #ddd;
            }
            
            /* Prevent elements from breaking */
            h1, h2, h3, h4, h5, h6 {
                page-break-after: avoid;
            }
            
            /* Hide unnecessary elements in PDF */
            .no-print {
                display: none !important;
            }
            
            /* Ensure proper page margins */
            @page {
                size: A4;
                margin: 1in;
            }
        }
        </style>
        """
        
        # Insert print CSS into HTML head
        if '<head>' in html_content:
            return html_content.replace('<head>', f'<head>{print_css}')
        else:
            # If no head tag, add it
            return html_content.replace('<html>', f'<html><head>{print_css}</head>')
    
    def _enhance_html_for_pdf(self, html_content: str) -> str:
        """Enhance HTML for better PDF conversion"""
        # Clean HTML for better compatibility
        clean_html = html_content
        
        # Convert mm units to px for better PDF rendering
        import re
        clean_html = re.sub(r'(\d+(?:\.\d+)?)mm', lambda m: f"{float(m.group(1)) * 3.78:.2f}px", clean_html)
        
        # Remove problematic CSS properties but KEEP table-layout for width consistency
        clean_html = clean_html.replace('box-sizing: border-box;', '')
        # Keep table-layout: fixed for width consistency - CRITICAL for table widths
        clean_html = clean_html.replace('break-inside: avoid;', '')
        
        # Add viewport meta tag for better rendering
        if '<head>' in clean_html and '<meta name="viewport"' not in clean_html:
            clean_html = clean_html.replace('<head>', '<head><meta name="viewport" content="width=device-width, initial-scale=1.0">')
        
        return clean_html
    
    def _create_simple_pdf_fallback(self, doc_name: str, html_content: str) -> bytes:
        """Create a simple PDF using ReportLab as a last resort fallback"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from bs4 import BeautifulSoup
            import io
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Parse HTML and extract text content
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Add title
            title = Paragraph(f"<b>{doc_name}</b>", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Extract and add text content
            text_content = soup.get_text(separator='\n')
            lines = text_content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line:
                    para = Paragraph(line, styles['Normal'])
                    story.append(para)
                    story.append(Spacer(1, 6))
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"ReportLab fallback also failed for {doc_name}: {str(e)}")
            return f"PDF generation completely failed for {doc_name}: All engines failed".encode()
    
    def _generate_first_page(self) -> str:
        """Generate First Page Summary document with enhanced PDF compatibility"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>First Page Summary</title>
            <style>
                /* Screen styles */
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    font-size: 14px;
                }}
                
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border: 1px solid #ddd;
                }}
                
                th {{
                    background-color: #f5f5f5;
                    font-weight: bold;
                }}
                
                /* CRITICAL: Print-specific styles */
                @media print {{
                    body {{ font-size: 12px; }}
                    .container {{ max-width: none; width: 100%; }}
                    table {{ page-break-inside: auto; }}
                    tr {{ page-break-inside: avoid; }}
                    
                    * {{
                        -webkit-print-color-adjust: exact !important;
                        color-adjust: exact !important;
                        print-color-adjust: exact !important;
                    }}
                    
                    @page {{
                        size: A4;
                        margin: 1cm;
                    }}
                }}
                
                @page {{ 
                    size: A4; 
                    margin: 10mm 10mm 10mm 10mm;
                    margin-top: 10mm;
                    margin-right: 10mm;
                    margin-bottom: 10mm;
                    margin-left: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 10pt; 
                }}
                .page {{ 
                    margin: 0;
                    padding: 0;
                }}
                .page {{ }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .title {{ font-size: 16pt; font-weight: bold; }}
                .subtitle {{ font-size: 11pt; margin: 3px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 6px 0; table-layout: fixed !important; }}
                thead {{ display: table-header-group; }}
                tr, img {{ break-inside: avoid; }}
                th, td {{ border: 1px solid #000; padding: 4px; text-align: left; word-wrap: break-word !important; overflow-wrap: break-word !important; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
                
                /* First Page Summary table widths - PROGRAMMATIC SPECS */
                table.first-page-summary col.col-unit {{ width: 11.7mm; }}
                table.first-page-summary col.col-qty-since {{ width: 16mm; }}
                table.first-page-summary col.col-qty-upto {{ width: 16mm; }}
                table.first-page-summary col.col-item-no {{ width: 11.1mm; }}
                table.first-page-summary col.col-description {{ width: 74.2mm; }}
                table.first-page-summary col.col-rate {{ width: 15.3mm; }}
                table.first-page-summary col.col-amt-upto {{ width: 22.7mm; }}
                table.first-page-summary col.col-amt-since {{ width: 17.6mm; }}
                table.first-page-summary col.col-remark {{ width: 13.9mm; }}
            </style>
        </head>
        <body>
            <div class="container">
            <div class="page">
            <div class="header">
                <div class="subtitle">First Page Summary</div>
                <div class="subtitle">Date: {current_date}</div>
            </div>
            
            <h3>Project Information</h3>
            <table>
                <tr><td><strong>Project Name:</strong></td><td>{self.title_data.get('Project Name', 'N/A')}</td></tr>
                <tr><td><strong>Contract No:</strong></td><td>{self.title_data.get('Contract No', 'N/A')}</td></tr>
                <tr><td><strong>Work Order No:</strong></td><td>{self.title_data.get('Work Order No', 'N/A')}</td></tr>
            </table>
            
            <h3>Work Items Summary</h3>
            <table class="first-page-summary">
                <colgroup>
                    <col class="col-unit">
                    <col class="col-qty-since">
                    <col class="col-qty-upto">
                    <col class="col-item-no">
                    <col class="col-description">
                    <col class="col-rate">
                    <col class="col-amt-upto">
                    <col class="col-amt-since">
                    <col class="col-remark">
                </colgroup>
                <thead>
                    <tr>
                        <th>Unit</th>
                        <th>Quantity executed (or supplied) since last certificate</th>
                        <th>Quantity executed (or supplied) upto date as per MB</th>
                        <th>Item No.</th>
                        <th>Item of Work supplies (Grouped under "sub-head" and "sub work" of estimate)</th>
                        <th>Rate</th>
                        <th>Amount upto date</th>
                        <th>Amount Since previous bill (Total for each sub-head)</th>
                        <th>Remark</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add work order items
        for index, row in self.work_order_data.iterrows():
            # Safely convert numeric values - handle both old and new column names
            quantity_since = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
            quantity_upto = self._safe_float(row.get('Quantity Upto', quantity_since))
            rate = self._safe_float(row.get('Rate', 0))
            amount_since = self._safe_float(row.get('Amount Since', quantity_since * rate))
            amount_upto = self._safe_float(row.get('Amount Upto', amount_since))
            
            # Format values conditionally
            qty_since_display = f"{quantity_since:.2f}" if quantity_since > 0 else ""
            qty_upto_display = f"{quantity_upto:.2f}" if quantity_upto > 0 else ""
            rate_display = f"{rate:.2f}" if rate > 0 else ""
            amt_upto_display = f"{amount_upto:.2f}" if amount_upto > 0 else ""
            amt_since_display = f"{amount_since:.2f}" if amount_since > 0 else ""
            
            html_content += f"""
                    <tr>
                        <td>{self._format_unit_or_text(row.get('Unit', ''))}</td>
                        <td class="amount">{qty_since_display}</td>
                        <td class="amount">{qty_upto_display}</td>
                        <td>{self._safe_serial_no(row.get('Item No.', row.get('Item', '')))}</td>
                        <td>{row.get('Description', '')}</td>
                        <td class="amount">{rate_display}</td>
                        <td class="amount">{amt_upto_display}</td>
                        <td class="amount">{amt_since_display}</td>
                        <td>{row.get('Remark', '')}</td>
                    </tr>
            """
        
        # Calculate totals
        total_amount = 0
        for _, row in self.work_order_data.iterrows():
            quantity_since = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
            rate = self._safe_float(row.get('Rate', 0))
            total_amount += quantity_since * rate
        
        html_content += f"""
                    <tr style="font-weight: bold;">
                        <td colspan="6">TOTAL</td>
                        <td class="amount">{total_amount:.2f}</td>
                        <td class="amount">{total_amount:.2f}</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
            </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_deviation_statement(self) -> str:
        """Generate Deviation Statement document"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Deviation Statement</title>
            <style>
                /* Screen styles */
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    font-size: 14px;
                }}
                
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border: 1px solid #ddd;
                }}
                
                th {{
                    background-color: #f5f5f5;
                    font-weight: bold;
                }}
                
                /* CRITICAL: Print-specific styles */
                @media print {{
                    body {{ font-size: 12px; }}
                    .container {{ max-width: none; width: 100%; }}
                    table {{ page-break-inside: auto; }}
                    tr {{ page-break-inside: avoid; }}
                    
                    * {{
                        -webkit-print-color-adjust: exact !important;
                        color-adjust: exact !important;
                        print-color-adjust: exact !important;
                    }}
                    
                    @page {{
                        size: A4 landscape;
                        margin: 1cm;
                    }}
                }}
                
                @page {{ 
                    size: A4 landscape; 
                    margin: 10mm 10mm 10mm 10mm;
                    margin-top: 10mm;
                    margin-right: 10mm;
                    margin-bottom: 10mm;
                    margin-left: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 9pt; 
                }}
                .page {{ }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .title {{ font-size: 14pt; font-weight: bold; }}
                .subtitle {{ font-size: 10pt; margin: 3px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 4px 0; table-layout: fixed !important; }}
                thead {{ display: table-header-group; }}
                tr, img {{ break-inside: avoid; }}
                th, td {{ border: 1px solid #000; padding: 3px; text-align: left; word-wrap: break-word !important; overflow-wrap: break-word !important; font-size: 8.5pt; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
                
                /* Deviation Statement table widths - TESTED SPECS */
                table.deviation-statement col.col-item-no {{ width: 6mm; }}
                table.deviation-statement col.col-description {{ width: 95mm; }}
                table.deviation-statement col.col-unit {{ width: 10mm; }}
                table.deviation-statement col.col-qty-wo {{ width: 10mm; }}
                table.deviation-statement col.col-rate {{ width: 12mm; }}
                table.deviation-statement col.col-amt-wo {{ width: 12mm; }}
                table.deviation-statement col.col-qty-executed {{ width: 12mm; }}
                table.deviation-statement col.col-amt-executed {{ width: 12mm; }}
                table.deviation-statement col.col-excess-qty {{ width: 12mm; }}
                table.deviation-statement col.col-excess-amt {{ width: 12mm; }}
                table.deviation-statement col.col-saving-qty {{ width: 12mm; }}
                table.deviation-statement col.col-saving-amt {{ width: 12mm; }}
                table.deviation-statement col.col-remarks {{ width: 40mm; }}
            </style>
        </head>
        <body>
            <div class="container">
            <div class="page">
            <div class="header">
                <div class="subtitle">Deviation Statement</div>
                <div class="subtitle">Date: {current_date}</div>
            </div>
            
            <table class="deviation-statement">
                <colgroup>
                    <col class="col-item-no">
                    <col class="col-description">
                    <col class="col-unit">
                    <col class="col-qty-wo">
                    <col class="col-rate">
                    <col class="col-amt-wo">
                    <col class="col-qty-executed">
                    <col class="col-amt-executed">
                    <col class="col-excess-qty">
                    <col class="col-excess-amt">
                    <col class="col-saving-qty">
                    <col class="col-saving-amt">
                    <col class="col-remarks">
                </colgroup>
                <thead>
                    <tr>
                        <th>ITEM No.</th>
                        <th>Description</th>
                        <th>Unit</th>
                        <th>Qty as per Work Order</th>
                        <th>Rate</th>
                        <th>Amt as per Work Order Rs.</th>
                        <th>Qty Executed</th>
                        <th>Amt as per Executed Rs.</th>
                        <th>Excess Qty</th>
                        <th>Excess Amt Rs.</th>
                        <th>Saving Qty</th>
                        <th>Saving Amt Rs.</th>
                        <th>REMARKS/ REASON.</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Compare work order with bill quantity data
        for index, wo_row in self.work_order_data.iterrows():
            # Find corresponding bill quantity row
            bq_row = None
            if isinstance(self.bill_quantity_data, pd.DataFrame) and not self.bill_quantity_data.empty:
                wo_item = wo_row.get('Item No.', wo_row.get('Item', ''))
                bq_item_col = 'Item No.' if 'Item No.' in self.bill_quantity_data.columns else 'Item'
                matching_rows = self.bill_quantity_data[
                    self.bill_quantity_data[bq_item_col] == wo_item
                ]
                if isinstance(matching_rows, pd.DataFrame) and not matching_rows.empty:
                    bq_row = matching_rows.iloc[0]
            
            wo_qty = self._safe_float(wo_row.get('Quantity Since', wo_row.get('Quantity', 0)))
            wo_rate = self._safe_float(wo_row.get('Rate', 0))
            wo_amount = wo_qty * wo_rate
            
            bq_qty = self._safe_float(bq_row.get('Quantity', 0)) if bq_row is not None else 0
            bq_amount = bq_qty * wo_rate
            
            excess_qty = max(0, bq_qty - wo_qty)
            excess_amt = excess_qty * wo_rate
            saving_qty = max(0, wo_qty - bq_qty)
            saving_amt = saving_qty * wo_rate
            
            # Format deviation values conditionally
            wo_qty_display = f"{wo_qty:.2f}" if wo_qty > 0 else ""
            wo_rate_display = f"{wo_rate:.2f}" if wo_rate > 0 else ""
            wo_amount_display = f"{wo_amount:.2f}" if wo_amount > 0 else ""
            bq_qty_display = f"{bq_qty:.2f}" if bq_qty > 0 else "0.00"  # Show 0.00 for executed quantity
            bq_amount_display = f"{bq_amount:.2f}" if bq_amount > 0 else ""
            excess_qty_display = f"{excess_qty:.2f}" if excess_qty > 0 else ""
            excess_amt_display = f"{excess_amt:.2f}" if excess_amt > 0 else ""
            saving_qty_display = f"{saving_qty:.2f}" if saving_qty > 0 else ""
            saving_amt_display = f"{saving_amt:.2f}" if saving_amt > 0 else ""
            
            html_content += f"""
                    <tr>
                        <td>{self._safe_serial_no(wo_row.get('Item No.', wo_row.get('Item', '')))}</td>
                        <td>{wo_row.get('Description', '')}</td>
                        <td>{self._format_unit_or_text(wo_row.get('Unit', ''))}</td>
                        <td class="amount">{wo_qty_display}</td>
                        <td class="amount">{wo_rate_display}</td>
                        <td class="amount">{wo_amount_display}</td>
                        <td class="amount">{bq_qty_display}</td>
                        <td class="amount">{bq_amount_display}</td>
                        <td class="amount">{excess_qty_display}</td>
                        <td class="amount">{excess_amt_display}</td>
                        <td class="amount">{saving_qty_display}</td>
                        <td class="amount">{saving_amt_display}</td>
                        <td></td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
            </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_final_bill_scrutiny(self) -> str:
        """Generate Final Bill Scrutiny Sheet"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Final Bill Scrutiny Sheet</title>
            <style>
                /* Screen styles */
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    font-size: 14px;
                }}
                
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border: 1px solid #ddd;
                }}
                
                th {{
                    background-color: #f5f5f5;
                    font-weight: bold;
                }}
                
                /* CRITICAL: Print-specific styles */
                @media print {{
                    body {{ font-size: 12px; }}
                    .container {{ max-width: none; width: 100%; }}
                    table {{ page-break-inside: auto; }}
                    tr {{ page-break-inside: avoid; }}
                    
                    * {{
                        -webkit-print-color-adjust: exact !important;
                        color-adjust: exact !important;
                        print-color-adjust: exact !important;
                    }}
                    
                    @page {{
                        size: A4;
                        margin: 1cm;
                    }}
                }}
                
                @page {{ 
                    size: A4; 
                    margin: 10mm 10mm 10mm 10mm;
                    margin-top: 10mm;
                    margin-right: 10mm;
                    margin-bottom: 10mm;
                    margin-left: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 10pt; 
                }}
                .page {{ }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .title {{ font-size: 16pt; font-weight: bold; }}
                .subtitle {{ font-size: 11pt; margin: 3px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 6px 0; table-layout: fixed !important; }}
                thead {{ display: table-header-group; }}
                tr, img {{ break-inside: avoid; }}
                th, td {{ border: 1px solid #000; padding: 4px; text-align: left; word-wrap: break-word !important; overflow-wrap: break-word !important; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="container">
            <div class="page">
            <div class="header">
                <div class="subtitle">Final Bill Scrutiny Sheet</div>
                <div class="subtitle">Date: {current_date}</div>
            </div>
            
            <h3>Bill Summary</h3>
            <table>
                <thead>
                    <tr>
                        <th>Item No.</th>
                        <th>Description</th>
                        <th>Unit</th>
                        <th>Quantity</th>
                        <th>Rate</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_amount = 0
        for index, row in self.bill_quantity_data.iterrows():
            quantity = self._safe_float(row.get('Quantity', 0))
            rate = self._safe_float(row.get('Rate', 0))
            amount = quantity * rate
            total_amount += amount
            
            html_content += f"""
                    <tr>
                        <td>{self._safe_serial_no(row.get('Item No.', row.get('Item', '')))}</td>
                        <td>{row.get('Description', '')}</td>
                        <td>{self._format_unit_or_text(row.get('Unit', ''))}</td>
                        <td class="amount">{self._format_number(quantity)}</td>
                        <td class="amount">{self._format_number(rate)}</td>
                        <td class="amount">{self._format_number(amount)}</td>
                    </tr>
            """
        
        html_content += f"""
                    <tr style="font-weight: bold;">
                        <td colspan="5">TOTAL</td>
                        <td class="amount">{total_amount:.0f}</td>
                    </tr>
                </tbody>
            </table>
            </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_extra_items_statement(self) -> str:
        """Generate Extra Items Statement"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Extra Items Statement</title>
            <style>
                /* Screen styles */
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    font-size: 14px;
                }}
                
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border: 1px solid #ddd;
                }}
                
                th {{
                    background-color: #f5f5f5;
                    font-weight: bold;
                }}
                
                /* CRITICAL: Print-specific styles */
                @media print {{
                    body {{ font-size: 12px; }}
                    .container {{ max-width: none; width: 100%; }}
                    table {{ page-break-inside: auto; }}
                    tr {{ page-break-inside: avoid; }}
                    
                    * {{
                        -webkit-print-color-adjust: exact !important;
                        color-adjust: exact !important;
                        print-color-adjust: exact !important;
                    }}
                    
                    @page {{
                        size: A4;
                        margin: 1cm;
                    }}
                }}
                
                @page {{ 
                    size: A4; 
                    margin: 10mm 10mm 10mm 10mm;
                    margin-top: 10mm;
                    margin-right: 10mm;
                    margin-bottom: 10mm;
                    margin-left: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 10pt; 
                }}
                .page {{ }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .title {{ font-size: 16pt; font-weight: bold; }}
                .subtitle {{ font-size: 11pt; margin: 3px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 6px 0; table-layout: fixed !important; }}
                thead {{ display: table-header-group; }}
                tr, img {{ break-inside: avoid; }}
                th, td {{ border: 1px solid #000; padding: 4px; text-align: left; word-wrap: break-word !important; overflow-wrap: break-word !important; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
                
                /* Extra Items Statement table widths - VALIDATED SPECS */
                table.extra-items col.col-unit {{ width: 11.7mm; }}
                table.extra-items col.col-quantity {{ width: 16mm; }}
                table.extra-items col.col-item-no {{ width: 11.1mm; }}
                table.extra-items col.col-description {{ width: 74.2mm; }}
                table.extra-items col.col-rate {{ width: 15.3mm; }}
                table.extra-items col.col-amount {{ width: 22.7mm; }}
            </style>
        </head>
        <body>
            <div class="container">
            <div class="page">
            <div class="header">
                <div class="subtitle">Extra Items Statement</div>
                <div class="subtitle">Date: {current_date}</div>
            </div>
        """
        
        if isinstance(self.extra_items_data, pd.DataFrame) and not self.extra_items_data.empty:
            html_content += """
            <h3>Extra Items</h3>
            <table class="extra-items">
                <colgroup>
                    <col class="col-item-no">
                    <col class="col-description">
                    <col class="col-unit">
                    <col class="col-quantity">
                    <col class="col-rate">
                    <col class="col-amount">
                </colgroup>
                <thead>
                    <tr>
                        <th>Item No.</th>
                        <th>Description</th>
                        <th>Unit</th>
                        <th>Quantity</th>
                        <th>Rate</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            total_amount = 0
            for index, row in self.extra_items_data.iterrows():
                quantity = self._safe_float(row.get('Quantity', 0))
                rate = self._safe_float(row.get('Rate', 0))
                amount = quantity * rate
                total_amount += amount
                
                html_content += f"""
                        <tr>
                            <td>{self._safe_serial_no(row.get('Item No.', row.get('Item No', row.get('Item', ''))))}</td>
                            <td>{row.get('Description', '')}</td>
                            <td>{self._format_unit_or_text(row.get('Unit', ''))}</td>
                            <td class="amount">{self._format_number(quantity)}</td>
                            <td class="amount">{self._format_number(rate)}</td>
                            <td class="amount">{self._format_number(amount)}</td>
                        </tr>
                """
            
            html_content += f"""
                        <tr style="font-weight: bold;">
                            <td colspan="5">TOTAL</td>
                            <td class="amount">{total_amount:.0f}</td>
                        </tr>
                    </tbody>
                </table>
            """
        else:
            html_content += "<p>No extra items found in the provided data.</p>"
        
        html_content += """
            </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_certificate_ii(self) -> str:
        """Generate Certificate II"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Certificate II</title>
            <style>
                /* Screen styles */
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    font-size: 14px;
                }}
                
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border: 1px solid #ddd;
                }}
                
                th {{
                    background-color: #f5f5f5;
                    font-weight: bold;
                }}
                
                /* CRITICAL: Print-specific styles */
                @media print {{
                    body {{ font-size: 12px; }}
                    .container {{ max-width: none; width: 100%; }}
                    table {{ page-break-inside: auto; }}
                    tr {{ page-break-inside: avoid; }}
                    
                    * {{
                        -webkit-print-color-adjust: exact !important;
                        color-adjust: exact !important;
                        print-color-adjust: exact !important;
                    }}
                    
                    @page {{
                        size: A4;
                        margin: 1cm;
                    }}
                }}
                
                @page {{ 
                    size: A4; 
                    margin: 10mm 10mm 10mm 10mm;
                    margin-top: 10mm;
                    margin-right: 10mm;
                    margin-bottom: 10mm;
                    margin-left: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 11pt; 
                }}
                .page {{ }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .title {{ font-size: 16pt; font-weight: bold; }}
                .subtitle {{ font-size: 11pt; margin: 3px 0; }}
                .content {{ margin: 10px 0; line-height: 1.5; }}
                .signature {{ margin-top: 40px; }}
            </style>
        </head>
        <body>
            <div class="container">
            <div class="page">
            <div class="header">
                <div class="subtitle">Certificate II</div>
                <div class="subtitle">Date: {current_date}</div>
            </div>
            
            <div class="content">
                <p>This is to certify that the work described in the bill has been executed according to the specifications and is complete in all respects.</p>
                
                <p><strong>Project Details:</strong></p>
                <ul>
                    <li>Project Name: {self.title_data.get('Project Name', 'N/A')}</li>
                    <li>Contract No: {self.title_data.get('Contract No', 'N/A')}</li>
                    <li>Work Order No: {self.title_data.get('Work Order No', 'N/A')}</li>
                </ul>
                
                <p>The work has been executed in accordance with the contract terms and conditions.</p>
            </div>
            
            <div class="signature">
                <p>_________________________</p>
                <p>Engineer-in-Charge</p>
                <p>Date: {current_date}</p>
            </div>
            </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_certificate_iii(self) -> str:
        """Generate Certificate III"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Certificate III</title>
            <style>
                /* Screen styles */
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    font-size: 14px;
                }}
                
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border: 1px solid #ddd;
                }}
                
                th {{
                    background-color: #f5f5f5;
                    font-weight: bold;
                }}
                
                /* CRITICAL: Print-specific styles */
                @media print {{
                    body {{ font-size: 12px; }}
                    .container {{ max-width: none; width: 100%; }}
                    table {{ page-break-inside: auto; }}
                    tr {{ page-break-inside: avoid; }}
                    
                    * {{
                        -webkit-print-color-adjust: exact !important;
                        color-adjust: exact !important;
                        print-color-adjust: exact !important;
                    }}
                    
                    @page {{
                        size: A4;
                        margin: 1cm;
                    }}
                }}
                
                @page {{ 
                    size: A4; 
                    margin: 10mm 10mm 10mm 10mm;
                    margin-top: 10mm;
                    margin-right: 10mm;
                    margin-bottom: 10mm;
                    margin-left: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 11pt; 
                }}
                .page {{ }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .title {{ font-size: 16pt; font-weight: bold; }}
                .subtitle {{ font-size: 11pt; margin: 3px 0; }}
                .content {{ margin: 10px 0; line-height: 1.5; }}
                .signature {{ margin-top: 40px; }}
            </style>
        </head>
        <body>
            <div class="container">
            <div class="page">
            <div class="header">
                <div class="subtitle">Certificate III</div>
                <div class="subtitle">Date: {current_date}</div>
            </div>
            
            <div class="content">
                <p>This is to certify that the rates charged in the bill are in accordance with the contract and approved rate schedule.</p>
                
                <p><strong>Project Details:</strong></p>
                <ul>
                    <li>Project Name: {self.title_data.get('Project Name', 'N/A')}</li>
                    <li>Contract No: {self.title_data.get('Contract No', 'N/A')}</li>
                    <li>Work Order No: {self.title_data.get('Work Order No', 'N/A')}</li>
                </ul>
                
                <p>All rates and calculations have been verified and are correct.</p>
            </div>
            
            <div class="signature">
                <p>_________________________</p>
                <p>Accounts Officer</p>
                <p>Date: {current_date}</p>
            </div>
            </div>
            </div>
        </body>
        </html>
        """
        
        return html_content

def test_enhanced_generator():
    """Test the enhanced document generator"""
    print("🧪 Testing Enhanced Document Generator with Fixed PDF Conversion...")
    
    # Create sample data for testing
    sample_data = {
        'title_data': {
            'Project Name': 'Test Project',
            'Contract No': '123/2025',
            'Work Order No': 'WO-456'
        },
        'work_order_data': pd.DataFrame([
            {'Item No.': '1', 'Description': 'Test Item 1', 'Unit': 'PCS', 'Quantity': 10, 'Rate': 100},
            {'Item No.': '2', 'Description': 'Test Item 2', 'Unit': 'PCS', 'Quantity': 5, 'Rate': 200}
        ]),
        'bill_quantity_data': pd.DataFrame([
            {'Item No.': '1', 'Description': 'Test Item 1', 'Unit': 'PCS', 'Quantity': 10, 'Rate': 100},
            {'Item No.': '2', 'Description': 'Test Item 2', 'Unit': 'PCS', 'Quantity': 5, 'Rate': 200}
        ]),
        'extra_items_data': pd.DataFrame([
            {'Item No.': '3', 'Description': 'Extra Item', 'Unit': 'PCS', 'Quantity': 3, 'Rate': 150}
        ])
    }
    
    # Create generator and test
    generator = EnhancedDocumentGenerator(sample_data)
    documents = generator.generate_all_documents()
    
    print(f"✅ Generated {len(documents)} HTML documents:")
    for doc_name in documents.keys():
        print(f"   - {doc_name}")
    
    # Test PDF conversion
    try:
        pdf_documents = generator.create_pdf_documents_fixed(documents)
        print(f"✅ Generated {len(pdf_documents)} PDF documents:")
        for doc_name in pdf_documents.keys():
            print(f"   - {doc_name} ({len(pdf_documents[doc_name])} bytes)")
    except Exception as e:
        print(f"❌ PDF generation failed: {str(e)}")
    
    return documents

if __name__ == "__main__":
    test_enhanced_generator()