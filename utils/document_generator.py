import pandas as pd
import gc
from datetime import datetime
from typing import Dict, Any
import io
import asyncio
from functools import lru_cache
from jinja2 import Environment, FileSystemLoader
import os
import tempfile
from pathlib import Path

class DocumentGenerator:
    """Generates various billing documents from processed Excel data using Jinja2 templates"""
    
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
                'unit': row.get('Unit', ''),
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
                    'unit': row.get('Unit', ''),
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
    
    async def _convert_html_to_pdf_async(self, html_content: str, doc_name: str) -> bytes:
        """
        Convert HTML to PDF using Playwright for pixel-perfect rendering
        This ensures the PDF looks exactly like the HTML in a browser
        """
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set the HTML content
            await page.set_content(html_content, wait_until='networkidle')
            
            # Generate PDF with proper settings for document rendering
            pdf_bytes = await page.pdf(
                format='A4',
                print_background=True,
                margin={'top': '0mm', 'right': '0mm', 'bottom': '0mm', 'left': '0mm'},
                prefer_css_page_size=True,  # Use CSS @page size settings
                display_header_footer=False
            )
            
            await browser.close()
            return pdf_bytes
    
    def create_pdf_documents(self, documents: Dict[str, str]) -> Dict[str, bytes]:
        """
        Convert HTML documents to PDF format using Playwright for exact HTML rendering
        
        Args:
            documents: Dictionary of HTML documents
            
        Returns:
            Dictionary of PDF documents as bytes
        """
        pdf_files = {}
        
        # Check if Playwright is available
        try:
            from playwright.async_api import async_playwright
            use_playwright = True
            print("✅ Using Playwright for high-quality PDF generation")
        except ImportError:
            use_playwright = False
            print("⚠️ Playwright not available, falling back to alternative PDF engines")
        
        if use_playwright:
            # Use Playwright for pixel-perfect PDF generation
            for doc_name, html_content in documents.items():
                try:
                    print(f"🔄 Converting {doc_name} to PDF with Playwright...")
                    
                    # Run async function in sync context
                    pdf_bytes = asyncio.run(self._convert_html_to_pdf_async(html_content, doc_name))
                    
                    pdf_files[f"{doc_name}.pdf"] = pdf_bytes
                    print(f"✅ Successfully generated {doc_name}.pdf ({len(pdf_bytes)} bytes)")
                    
                except Exception as e:
                    print(f"❌ Playwright conversion failed for {doc_name}: {str(e)}")
                    # Fall back to alternative methods for this document
                    pdf_bytes = self._fallback_pdf_conversion(doc_name, html_content)
                    pdf_files[f"{doc_name}.pdf"] = pdf_bytes
        else:
            # Fallback to xhtml2pdf/WeasyPrint
            for doc_name, html_content in documents.items():
                pdf_bytes = self._fallback_pdf_conversion(doc_name, html_content)
                pdf_files[f"{doc_name}.pdf"] = pdf_bytes
        
        # Memory cleanup
        gc.collect()
        return pdf_files
    
    def _fallback_pdf_conversion(self, doc_name: str, html_content: str) -> bytes:
        """
        Fallback PDF conversion using xhtml2pdf, WeasyPrint, or ReportLab
        """
        from concurrent.futures import ThreadPoolExecutor
        
        # Initialize PDF engines
        render_with_weasy = None
        render_with_xhtml2pdf = None
        
        # Try WeasyPrint
        try:
            from weasyprint import HTML
            def render_with_weasy(html_str: str) -> bytes:
                try:
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(lambda: HTML(string=html_str, base_url=".").write_pdf())
                        return future.result(timeout=30)
                except Exception as e:
                    raise Exception(f"WeasyPrint timeout or error: {str(e)}")
        except Exception:
            render_with_weasy = None
        
        # Try xhtml2pdf
        try:
            from xhtml2pdf import pisa
            def render_with_xhtml2pdf(html_str: str) -> bytes:
                import re
                # Clean HTML for better compatibility
                clean_html = html_str
                clean_html = re.sub(r'(\d+(?:\.\d+)?)mm', lambda m: f"{float(m.group(1)) * 3.78:.0f}px", clean_html)
                clean_html = clean_html.replace('box-sizing: border-box;', '')
                clean_html = clean_html.replace('break-inside: avoid;', '')
                
                output = io.BytesIO()
                result = pisa.CreatePDF(
                    src=clean_html,
                    dest=output,
                    encoding="utf-8",
                    default_css=None,
                    link_callback=None
                )
                if hasattr(result, 'err') and result.err:
                    raise Exception(f"xhtml2pdf error: {result.err}")
                return output.getvalue()
        except Exception:
            render_with_xhtml2pdf = None
        
        # Try conversion with available engines
        print(f"🔄 Converting {doc_name} with fallback engines...")
        
        # First try xhtml2pdf
        if render_with_xhtml2pdf is not None:
            try:
                print(f"  📄 Using xhtml2pdf for {doc_name}...")
                pdf_bytes = render_with_xhtml2pdf(html_content)
                print(f"  ✅ xhtml2pdf successful for {doc_name} ({len(pdf_bytes)} bytes)")
                return pdf_bytes
            except Exception as e:
                print(f"  ❌ xhtml2pdf failed: {str(e)}")
        
        # Then try WeasyPrint
        if render_with_weasy is not None:
            try:
                print(f"  📄 Using WeasyPrint for {doc_name}...")
                pdf_bytes = render_with_weasy(html_content)
                print(f"  ✅ WeasyPrint successful for {doc_name} ({len(pdf_bytes)} bytes)")
                return pdf_bytes
            except Exception as e:
                print(f"  ❌ WeasyPrint failed: {str(e)}")
        
        # Last resort: ReportLab fallback
        print(f"  ⚠️ Using ReportLab fallback for {doc_name}")
        return self._create_simple_pdf_fallback(doc_name, html_content)
    
    def _create_simple_pdf_fallback(self, doc_name: str, html_content: str) -> bytes:
        """Create a simple PDF using ReportLab as a last resort fallback"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            from bs4 import BeautifulSoup
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Add title
            title = Paragraph(f"<b>{doc_name}</b>", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Try to extract tables
            tables = soup.find_all('table')
            if tables:
                for table in tables:
                    # Extract table data
                    table_data = []
                    for row in table.find_all('tr'):
                        row_data = []
                        for cell in row.find_all(['th', 'td']):
                            row_data.append(cell.get_text(strip=True))
                        if row_data:
                            table_data.append(row_data)
                    
                    if table_data:
                        # Create ReportLab table
                        t = Table(table_data)
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        story.append(t)
                        story.append(Spacer(1, 12))
            else:
                # Extract text if no tables
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
            print(f"⚠️ ReportLab fallback also failed for {doc_name}: {str(e)}")
            return f"PDF generation completely failed for {doc_name}: All engines failed".encode()
    
    def _generate_first_page(self) -> str:
        """Generate First Page Summary document"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>First Page Summary</title>
            <style>
                @page {{ 
                    size: A4; 
                    margin: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 10pt; 
                }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .subtitle {{ font-size: 11pt; margin: 3px 0; }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 6px 0; 
                    table-layout: fixed;
                }}
                thead {{ display: table-header-group; }}
                tr, img {{ break-inside: avoid; }}
                th, td {{ 
                    border: 1px solid #000; 
                    padding: 4px; 
                    text-align: left; 
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
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
            <table>
                <thead>
                    <tr>
                        <th style="width: 8%;">Unit</th>
                        <th style="width: 10%;">Qty Since</th>
                        <th style="width: 10%;">Qty Upto</th>
                        <th style="width: 8%;">Item No.</th>
                        <th style="width: 34%;">Description</th>
                        <th style="width: 10%;">Rate</th>
                        <th style="width: 10%;">Amt Upto</th>
                        <th style="width: 10%;">Amt Since</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add work order items
        total_amount = 0
        for index, row in self.work_order_data.iterrows():
            quantity_since = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
            quantity_upto = self._safe_float(row.get('Quantity Upto', quantity_since))
            rate = self._safe_float(row.get('Rate', 0))
            amount_since = quantity_since * rate
            amount_upto = amount_since
            total_amount += amount_since
            
            qty_since_display = f"{quantity_since:.2f}" if quantity_since > 0 else ""
            qty_upto_display = f"{quantity_upto:.2f}" if quantity_upto > 0 else ""
            rate_display = f"{rate:.2f}" if rate > 0 else ""
            amt_upto_display = f"{amount_upto:.2f}" if amount_upto > 0 else ""
            amt_since_display = f"{amount_since:.2f}" if amount_since > 0 else ""
            
            html_content += f"""
                    <tr>
                        <td>{row.get('Unit', '')}</td>
                        <td class="amount">{qty_since_display}</td>
                        <td class="amount">{qty_upto_display}</td>
                        <td>{self._safe_serial_no(row.get('Item No.', row.get('Item', '')))}</td>
                        <td>{row.get('Description', '')}</td>
                        <td class="amount">{rate_display}</td>
                        <td class="amount">{amt_upto_display}</td>
                        <td class="amount">{amt_since_display}</td>
                    </tr>
            """
        
        html_content += f"""
                    <tr style="font-weight: bold;">
                        <td colspan="6">TOTAL</td>
                        <td class="amount">{total_amount:.2f}</td>
                        <td class="amount">{total_amount:.2f}</td>
                    </tr>
                </tbody>
            </table>
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
            <title>Deviation Statement</title>
            <style>
                @page {{ 
                    size: A4 landscape; 
                    margin: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 9pt; 
                }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .subtitle {{ font-size: 10pt; margin: 3px 0; }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 4px 0; 
                    table-layout: fixed;
                }}
                thead {{ display: table-header-group; }}
                tr, img {{ break-inside: avoid; }}
                th, td {{ 
                    border: 1px solid #000; 
                    padding: 3px; 
                    text-align: left; 
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                    font-size: 8.5pt;
                }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="subtitle">Deviation Statement</div>
                <div class="subtitle">Date: {current_date}</div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%;">Item No.</th>
                        <th style="width: 25%;">Description</th>
                        <th style="width: 5%;">Unit</th>
                        <th style="width: 8%;">Qty WO</th>
                        <th style="width: 8%;">Rate</th>
                        <th style="width: 8%;">Amt WO</th>
                        <th style="width: 8%;">Qty Exec</th>
                        <th style="width: 8%;">Amt Exec</th>
                        <th style="width: 8%;">Excess Qty</th>
                        <th style="width: 8%;">Excess Amt</th>
                        <th style="width: 8%;">Saving Qty</th>
                        <th style="width: 8%;">Saving Amt</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Compare work order with bill quantity data
        for index, wo_row in self.work_order_data.iterrows():
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
            
            wo_qty_display = f"{wo_qty:.2f}" if wo_qty > 0 else ""
            wo_rate_display = f"{wo_rate:.2f}" if wo_rate > 0 else ""
            wo_amount_display = f"{wo_amount:.2f}" if wo_amount > 0 else ""
            bq_qty_display = f"{bq_qty:.2f}" if bq_qty > 0 else ""
            bq_amount_display = f"{bq_amount:.2f}" if bq_amount > 0 else ""
            excess_qty_display = f"{excess_qty:.2f}" if excess_qty > 0 else ""
            excess_amt_display = f"{excess_amt:.2f}" if excess_amt > 0 else ""
            saving_qty_display = f"{saving_qty:.2f}" if saving_qty > 0 else ""
            saving_amt_display = f"{saving_amt:.2f}" if saving_amt > 0 else ""
            
            html_content += f"""
                    <tr>
                        <td>{self._safe_serial_no(wo_row.get('Item No.', wo_row.get('Item', '')))}</td>
                        <td>{wo_row.get('Description', '')}</td>
                        <td>{wo_row.get('Unit', '')}</td>
                        <td class="amount">{wo_qty_display}</td>
                        <td class="amount">{wo_rate_display}</td>
                        <td class="amount">{wo_amount_display}</td>
                        <td class="amount">{bq_qty_display}</td>
                        <td class="amount">{bq_amount_display}</td>
                        <td class="amount">{excess_qty_display}</td>
                        <td class="amount">{excess_amt_display}</td>
                        <td class="amount">{saving_qty_display}</td>
                        <td class="amount">{saving_amt_display}</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
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
            <title>Final Bill Scrutiny Sheet</title>
            <style>
                @page {{ 
                    size: A4; 
                    margin: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 10pt; 
                }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .subtitle {{ font-size: 11pt; margin: 3px 0; }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 6px 0; 
                    table-layout: fixed;
                }}
                thead {{ display: table-header-group; }}
                tr, img {{ break-inside: avoid; }}
                th, td {{ 
                    border: 1px solid #000; 
                    padding: 4px; 
                    text-align: left; 
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="subtitle">Final Bill Scrutiny Sheet</div>
                <div class="subtitle">Date: {current_date}</div>
            </div>
            
            <h3>Bill Summary</h3>
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">Item No.</th>
                        <th style="width: 40%;">Description</th>
                        <th style="width: 10%;">Unit</th>
                        <th style="width: 13%;">Quantity</th>
                        <th style="width: 13%;">Rate</th>
                        <th style="width: 14%;">Amount</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_amount = 0
        if isinstance(self.bill_quantity_data, pd.DataFrame) and not self.bill_quantity_data.empty:
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
        else:
            html_content += """
                    <tr>
                        <td colspan="6">No bill quantity data available</td>
                    </tr>
            """
        
        html_content += f"""
                    <tr style="font-weight: bold;">
                        <td colspan="5">TOTAL</td>
                        <td class="amount">{total_amount:.0f}</td>
                    </tr>
                </tbody>
            </table>
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
            <title>Extra Items Statement</title>
            <style>
                @page {{ 
                    size: A4; 
                    margin: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 10pt; 
                }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .subtitle {{ font-size: 11pt; margin: 3px 0; }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 6px 0; 
                    table-layout: fixed;
                }}
                thead {{ display: table-header-group; }}
                tr, img {{ break-inside: avoid; }}
                th, td {{ 
                    border: 1px solid #000; 
                    padding: 4px; 
                    text-align: left; 
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="subtitle">Extra Items Statement</div>
                <div class="subtitle">Date: {current_date}</div>
            </div>
        """
        
        if isinstance(self.extra_items_data, pd.DataFrame) and not self.extra_items_data.empty:
            html_content += """
            <h3>Extra Items</h3>
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">Item No.</th>
                        <th style="width: 40%;">Description</th>
                        <th style="width: 10%;">Unit</th>
                        <th style="width: 13%;">Quantity</th>
                        <th style="width: 13%;">Rate</th>
                        <th style="width: 14%;">Amount</th>
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
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_certificate_ii(self) -> str:
        """Generate Professional Certificate II - Government Standard"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Certificate II - Work Completion Certificate</title>
            <style>
                @page {{ 
                    size: A4; 
                    margin: 15mm 20mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: 'Times New Roman', serif; 
                    margin: 0; 
                    padding: 0;
                    font-size: 14pt;
                    line-height: 1.6;
                    color: #000;
                }}
                .letterhead {{
                    text-align: center;
                    border-bottom: 3px double #000;
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                .dept-header {{
                    font-size: 18pt;
                    font-weight: bold;
                    color: #2d5f3f;
                    margin-bottom: 5px;
                }}
                .cert-title {{
                    text-align: center;
                    font-size: 20pt;
                    font-weight: bold;
                    text-decoration: underline;
                    margin: 25px 0;
                    color: #2d5f3f;
                }}
                .content {{
                    text-align: justify;
                    margin: 20px 0;
                    text-indent: 50px;
                }}
                .project-details {{
                    background: #f8f9fa;
                    padding: 15px;
                    border: 2px solid #2d5f3f;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .signatures {{
                    margin-top: 60px;
                    text-align: right;
                }}
                .signature-title {{
                    font-weight: bold;
                    font-size: 12pt;
                }}
            </style>
        </head>
        <body>
            <div class="letterhead">
                <div class="dept-header">PUBLIC WORKS DEPARTMENT</div>
                <div>GOVERNMENT OF RAJASTHAN</div>
            </div>
            
            <div class="cert-title">CERTIFICATE - II</div>
            <div style="text-align: center; font-size: 16pt; font-weight: bold; margin-bottom: 20px;">
                (WORK COMPLETION CERTIFICATE)
            </div>
            
            <div class="content">
                <p>This is to <strong>CERTIFY</strong> that the work described in the measurement book and bill has been executed according to the approved drawings, specifications, and technical standards prescribed for the work, and is <strong>COMPLETE IN ALL RESPECTS</strong>.</p>
            </div>
            
            <div class="project-details">
                <p><strong>Project Name:</strong> {self.title_data.get('Project Name', 'N/A')}</p>
                <p><strong>Contract No:</strong> {self.title_data.get('Contract No', 'N/A')}</p>
                <p><strong>Work Order No:</strong> {self.title_data.get('Work Order No', 'N/A')}</p>
            </div>
            
            <div class="signatures">
                <p>Date: {current_date}</p>
                <div style="margin-top: 60px;">
                    <p class="signature-title">Executive Engineer</p>
                    <p>PWD, Udaipur</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_certificate_iii(self) -> str:
        """Generate Professional Certificate III"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Certificate III - Measurement Certificate</title>
            <style>
                @page {{ 
                    size: A4; 
                    margin: 15mm 20mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: 'Times New Roman', serif; 
                    margin: 0; 
                    padding: 0;
                    font-size: 14pt;
                    line-height: 1.6;
                    color: #000;
                }}
                .letterhead {{
                    text-align: center;
                    border-bottom: 3px double #000;
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                .dept-header {{
                    font-size: 18pt;
                    font-weight: bold;
                    color: #2d5f3f;
                    margin-bottom: 5px;
                }}
                .cert-title {{
                    text-align: center;
                    font-size: 20pt;
                    font-weight: bold;
                    text-decoration: underline;
                    margin: 25px 0;
                    color: #2d5f3f;
                }}
                .content {{
                    text-align: justify;
                    margin: 20px 0;
                    text-indent: 50px;
                }}
                .project-details {{
                    background: #f8f9fa;
                    padding: 15px;
                    border: 2px solid #2d5f3f;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .signatures {{
                    margin-top: 60px;
                    text-align: right;
                }}
                .signature-title {{
                    font-weight: bold;
                    font-size: 12pt;
                }}
            </style>
        </head>
        <body>
            <div class="letterhead">
                <div class="dept-header">PUBLIC WORKS DEPARTMENT</div>
                <div>GOVERNMENT OF RAJASTHAN</div>
            </div>
            
            <div class="cert-title">CERTIFICATE - III</div>
            <div style="text-align: center; font-size: 16pt; font-weight: bold; margin-bottom: 20px;">
                (MEASUREMENT CERTIFICATE)
            </div>
            
            <div class="content">
                <p>This is to <strong>CERTIFY</strong> that I have satisfied myself that the rate/rates for the work has/have been correctly entered in the books and have been paid according to the Contract Agreement and as per the sanctioned rates.</p>
            </div>
            
            <div class="project-details">
                <p><strong>Project Name:</strong> {self.title_data.get('Project Name', 'N/A')}</p>
                <p><strong>Contract No:</strong> {self.title_data.get('Contract No', 'N/A')}</p>
                <p><strong>Work Order No:</strong> {self.title_data.get('Work Order No', 'N/A')}</p>
            </div>
            
            <div class="signatures">
                <p>Date: {current_date}</p>
                <div style="margin-top: 60px;">
                    <p class="signature-title">Executive Engineer</p>
                    <p>PWD, Udaipur</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content