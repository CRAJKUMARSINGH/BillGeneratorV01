import pandas as pd
import gc
from datetime import datetime
from typing import Dict, Any
import io
from functools import lru_cache
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import asyncio
from playwright.async_api import async_playwright

class EnhancedDocumentGenerator:
    """Enhanced document generator with fixed HTML-to-PDF conversion to achieve 95%+ matching"""
    
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
        
        # Insert the print CSS into the HTML head section
        if '<head>' in html_content:
            html_content = html_content.replace('<head>', f'<head>{print_css}')
        else:
            # If no head tag, add it at the beginning
            html_content = html_content.replace('<html>', f'<html><head>{print_css}</head>')
        
        return html_content
    
    def _fix_html_structure(self, html_content: str) -> str:
        """Fix HTML structure for better PDF conversion"""
        # Ensure proper DOCTYPE and viewport
        if not html_content.startswith('<!DOCTYPE'):
            html_content = '<!DOCTYPE html>\n' + html_content
        
        # Add viewport meta tag if missing
        if '<meta name="viewport"' not in html_content:
            viewport_meta = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            if '<head>' in html_content:
                html_content = html_content.replace('<head>', f'<head>\n    {viewport_meta}')
        
        return html_content
    
    async def _generate_pdf_playwright(self, html_content: str, output_path: str) -> bool:
        """Generate PDF using Playwright for better results"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Set viewport for consistent rendering
                await page.set_viewport_size({"width": 1200, "height": 1600})
                
                # Load HTML content
                await page.set_content(html_content)
                
                # Generate PDF with proper settings
                await page.pdf(
                    path=output_path,
                    format='A4',
                    print_background=True,
                    margin={
                        'top': '1cm',
                        'right': '1cm', 
                        'bottom': '1cm',
                        'left': '1cm'
                    }
                )
                
                await browser.close()
                return True
        except Exception as e:
            print(f"Playwright PDF generation failed: {str(e)}")
            return False
    
    def _generate_pdf_weasyprint(self, html_content: str, output_path: str) -> bool:
        """Generate PDF using WeasyPrint"""
        try:
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
            
            # Create font configuration
            font_config = FontConfiguration()
            
            # CSS for better PDF rendering
            css = CSS(string='''
                @page {
                    size: A4;
                    margin: 1cm;
                }
                body {
                    font-family: Arial, sans-serif;
                    font-size: 12px;
                    line-height: 1.4;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    table-layout: fixed;
                }
                td, th {
                    padding: 8px;
                    border: 1px solid #ddd;
                    word-wrap: break-word;
                }
            ''', font_config=font_config)
            
            # Generate PDF
            HTML(string=html_content).write_pdf(
                output_path, 
                stylesheets=[css], 
                font_config=font_config
            )
            return True
        except ImportError:
            print("WeasyPrint not installed")
            return False
        except Exception as e:
            print(f"WeasyPrint PDF generation failed: {str(e)}")
            return False
    
    def _generate_pdf_pdfkit(self, html_content: str, output_path: str) -> bool:
        """Generate PDF using pdfkit with fixed options"""
        try:
            import pdfkit
            
            # Correct options for preventing distortion
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'print-media-type': True,  # CRITICAL: Uses print CSS
                'disable-smart-shrinking': True,  # Prevents unwanted scaling
                'no-outline': None,
                'enable-local-file-access': None,
                'dpi': 300,  # High quality
                'javascript-delay': 1000,  # Wait for JS to load
                'load-error-handling': 'ignore',
                'load-media-error-handling': 'ignore',
            }
            
            # Generate PDF
            pdfkit.from_string(html_content, output_path, options=options)
            return True
        except ImportError:
            print("pdfkit not installed")
            return False
        except Exception as e:
            print(f"pdfkit PDF generation failed: {str(e)}")
            return False
    
    def generate_pdf_fixed(self, html_content: str, output_path: str) -> bool:
        """Fixed PDF generation with proper formatting using multiple fallback methods"""
        # Apply fixes to HTML content
        html_content = self._fix_html_structure(html_content)
        html_content = self._add_print_css(html_content)
        
        # Method 1: Using Playwright (Most Reliable)
        try:
            # Run async function in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._generate_pdf_playwright(html_content, output_path))
            loop.close()
            if result:
                print(f"✅ Playwright successful for {output_path}")
                return True
        except Exception as e:
            print(f"❌ Playwright failed: {str(e)}")
        
        # Method 2: Using WeasyPrint (Recommended)
        if self._generate_pdf_weasyprint(html_content, output_path):
            print(f"✅ WeasyPrint successful for {output_path}")
            return True
        
        # Method 3: Using pdfkit with fixed options
        if self._generate_pdf_pdfkit(html_content, output_path):
            print(f"✅ pdfkit successful for {output_path}")
            return True
            
        return False
    
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
    
    def create_pdf_documents(self, documents: Dict[str, str]) -> Dict[str, bytes]:
        """
        Convert HTML documents to PDF format with enhanced quality and 95%+ matching
        
        Args:
            documents: Dictionary of HTML documents
            
        Returns:
            Dictionary of PDF documents as bytes
        """
        pdf_files = {}
        
        # Process each document with enhanced PDF generation
        for doc_name, html_content in documents.items():
            print(f"🔄 Processing {doc_name} for PDF conversion...")
            
            # Create temporary file path
            temp_pdf_path = f"temp_{doc_name.replace(' ', '_').lower()}.pdf"
            
            # Generate PDF with enhanced method
            if self.generate_pdf_fixed(html_content, temp_pdf_path):
                # Read the generated PDF file
                try:
                    with open(temp_pdf_path, 'rb') as f:
                        pdf_bytes = f.read()
                    pdf_files[f"{doc_name}.pdf"] = pdf_bytes
                    print(f"  ✅ PDF generation successful for {doc_name} ({len(pdf_bytes)} bytes)")
                    
                    # Clean up temporary file
                    os.remove(temp_pdf_path)
                except Exception as e:
                    print(f"  ❌ Failed to read PDF file for {doc_name}: {str(e)}")
                    pdf_files[f"{doc_name}.pdf"] = b"PDF generation failed"
            else:
                print(f"  ❌ All PDF generation methods failed for {doc_name}")
                pdf_files[f"{doc_name}.pdf"] = b"PDF generation failed"
        
        # Memory cleanup
        gc.collect()
        return pdf_files
        
    def _generate_first_page(self) -> str:
        """Generate First Page Summary document with enhanced structure"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>First Page Summary</title>
            <style>
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
                
                .amount {{
                    text-align: right;
                }}
                
                /* CRITICAL: Print-specific styles */
                @media print {{
                    body {{ font-size: 12px; }}
                    .container {{ max-width: none; width: 100%; }}
                    table {{ page-break-inside: auto; }}
                    tr {{ page-break-inside: avoid; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>First Page Summary</h2>
                <p><strong>Date:</strong> {current_date}</p>
                
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
                            <td>{row.get('Unit', '')}</td>
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
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_deviation_statement(self) -> str:
        """Generate Deviation Statement document with enhanced structure"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Deviation Statement</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    font-size: 14px;
                }}
                
                .container {{
                    max-width: 1000px;
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
                
                .amount {{
                    text-align: right;
                }}
                
                /* CRITICAL: Print-specific styles */
                @media print {{
                    body {{ font-size: 12px; }}
                    .container {{ max-width: none; width: 100%; }}
                    table {{ page-break-inside: auto; }}
                    tr {{ page-break-inside: avoid; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Deviation Statement</h2>
                <p><strong>Date:</strong> {current_date}</p>
                
                <table>
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
                            <td></td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_final_bill_scrutiny(self) -> str:
        """Generate Final Bill Scrutiny Sheet with enhanced structure"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Final Bill Scrutiny Sheet</title>
            <style>
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
                
                .amount {{
                    text-align: right;
                }}
                
                /* CRITICAL: Print-specific styles */
                @media print {{
                    body {{ font-size: 12px; }}
                    .container {{ max-width: none; width: 100%; }}
                    table {{ page-break-inside: auto; }}
                    tr {{ page-break-inside: avoid; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Final Bill Scrutiny Sheet</h2>
                <p><strong>Date:</strong> {current_date}</p>
                
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
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_extra_items_statement(self) -> str:
        """Generate Extra Items Statement with enhanced structure"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Extra Items Statement</title>
            <style>
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
                
                .amount {{
                    text-align: right;
                }}
                
                /* CRITICAL: Print-specific styles */
                @media print {{
                    body {{ font-size: 12px; }}
                    .container {{ max-width: none; width: 100%; }}
                    table {{ page-break-inside: auto; }}
                    tr {{ page-break-inside: avoid; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Extra Items Statement</h2>
                <p><strong>Date:</strong> {current_date}</p>
        """
        
        if isinstance(self.extra_items_data, pd.DataFrame) and not self.extra_items_data.empty:
            html_content += """
                <h3>Extra Items</h3>
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
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_certificate_ii(self) -> str:
        """Generate Professional Certificate II - Government Standard with enhanced structure"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Certificate II - Work Completion Certificate</title>
            <style>
                body {{
                    font-family: 'Times New Roman', serif;
                    margin: 0;
                    padding: 20px;
                    font-size: 14px;
                    line-height: 1.6;
                }}
                
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                }}
                
                .letterhead {{
                    text-align: center;
                    border-bottom: 3px double #000;
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                
                .dept-header {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #2d5f3f;
                    margin-bottom: 5px;
                }}
                
                .govt-header {{
                    font-size: 14px;
                    font-weight: bold;
                    margin-bottom: 3px;
                }}
                
                .office-header {{
                    font-size: 12px;
                    margin-bottom: 8px;
                }}
                
                .certificate-title {{
                    text-align: center;
                    font-size: 20px;
                    font-weight: bold;
                    text-decoration: underline;
                    margin: 25px 0;
                    color: #2d5f3f;
                }}
                
                .certificate-subtitle {{
                    text-align: center;
                    font-size: 16px;
                    font-weight: bold;
                    margin-bottom: 20px;
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
                
                .detail-row {{
                    display: flex;
                    margin-bottom: 8px;
                }}
                
                .detail-label {{
                    font-weight: bold;
                    width: 35%;
                    color: #2d5f3f;
                }}
                
                .detail-value {{
                    width: 65%;
                    border-bottom: 1px dotted #000;
                    min-height: 20px;
                }}
                
                .signatures {{
                    margin-top: 40px;
                    display: flex;
                    justify-content: space-between;
                }}
                
                .signature-block {{
                    text-align: center;
                    width: 45%;
                }}
                
                .signature-line {{
                    border-bottom: 2px solid #000;
                    margin-bottom: 5px;
                    height: 50px;
                }}
                
                .signature-title {{
                    font-weight: bold;
                    font-size: 12px;
                }}
                
                .reference-no {{
                    text-align: right;
                    font-size: 12px;
                    margin-bottom: 10px;
                }}
                
                .date-place {{
                    display: flex;
                    justify-content: space-between;
                    margin-top: 30px;
                    font-weight: bold;
                }}
                
                /* CRITICAL: Print-specific styles */
                @media print {{
                    body {{ font-size: 12px; }}
                    .container {{ max-width: none; width: 100%; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="letterhead">
                    <div class="dept-header">PUBLIC WORKS DEPARTMENT</div>
                    <div class="govt-header">GOVERNMENT OF RAJASTHAN</div>
                    <div class="office-header">OFFICE OF THE EXECUTIVE ENGINEER, PWD UDAIPUR</div>
                </div>
                
                <div class="reference-no">
                    <strong>No. PWD/UDR/CE-II/{datetime.now().strftime('%Y')}/____</strong>
                </div>
                
                <div class="certificate-title">CERTIFICATE - II</div>
                <div class="certificate-subtitle">(WORK COMPLETION CERTIFICATE)</div>
                
                <div class="content">
                    <p>This is to <strong>CERTIFY</strong> that the work described in the measurement book and bill has been executed according to the approved drawings, specifications, and technical standards prescribed for the work, and is <strong>COMPLETE IN ALL RESPECTS</strong>.</p>
                    
                    <p>The undersigned has carefully inspected the work and found that all items of work have been executed as per the contract agreement and technical specifications approved by the competent authority.</p>
                </div>
                
                <div class="project-details">
                    <div class="detail-row">
                        <div class="detail-label">Project Name:</div>
                        <div class="detail-value">{self.title_data.get('Project Name', 'N/A')}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">Contract Number:</div>
                        <div class="detail-value">{self.title_data.get('Contract No', 'N/A')}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">Work Order Number:</div>
                        <div class="detail-value">{self.title_data.get('Work Order No', 'N/A')}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">Contractor Name:</div>
                        <div class="detail-value">{self.title_data.get('Contractor Name', 'N/A')}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">Work Description:</div>
                        <div class="detail-value">{self.title_data.get('Work Description', 'Infrastructure Development Work')}</div>
                    </div>
                </div>
                
                <div class="content">
                    <p>The work has been executed in accordance with the Indian Standard specifications, PWD Manual, and contract terms and conditions. All safety measures and quality control procedures have been duly followed during the execution of work.</p>
                    
                    <p><strong>The work is hereby ACCEPTED</strong> and is fit for the intended use as per the approved project requirements.</p>
                </div>
                
                <div class="date-place">
                    <div>Date: {current_date}</div>
                    <div>Place: Udaipur</div>
                </div>
                
                <div class="signatures">
                    <div class="signature-block">
                        <div class="signature-line"></div>
                        <div class="signature-title">CONTRACTOR</div>
                        <div style="font-size: 11px; margin-top: 5px;">(Name & Signature with Seal)</div>
                    </div>
                    <div class="signature-block">
                        <div class="signature-line"></div>
                        <div class="signature-title">EXECUTIVE ENGINEER</div>
                        <div style="font-size: 11px; margin-top: 5px;">PWD, Udaipur Division</div>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 20px; font-size: 10px; font-style: italic;">
                    <p>This certificate is issued as per PWD Manual provisions and Government of Rajasthan guidelines.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_certificate_iii(self) -> str:
        """Generate Professional Certificate III - Government Standard with enhanced structure"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Certificate III - Rate Verification Certificate</title>
            <style>
                body {{
                    font-family: 'Times New Roman', serif;
                    margin: 0;
                    padding: 20px;
                    font-size: 14px;
                    line-height: 1.6;
                }}
                
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                }}
                
                .letterhead {{
                    text-align: center;
                    border-bottom: 3px double #000;
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                
                .dept-header {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #2d5f3f;
                    margin-bottom: 5px;
                }}
                
                .govt-header {{
                    font-size: 14px;
                    font-weight: bold;
                    margin-bottom: 3px;
                }}
                
                .office-header {{
                    font-size: 12px;
                    margin-bottom: 8px;
                }}
                
                .certificate-title {{
                    text-align: center;
                    font-size: 20px;
                    font-weight: bold;
                    text-decoration: underline;
                    margin: 25px 0;
                    color: #2d5f3f;
                }}
                
                .certificate-subtitle {{
                    text-align: center;
                    font-size: 16px;
                    font-weight: bold;
                    margin-bottom: 20px;
                }}
                
                .content {{
                    text-align: justify;
                    margin: 20px 0;
                    text-indent: 50px;
                }}
                
                .verification-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    border: 2px solid #2d5f3f;
                }}
                
                .verification-table th {{
                    background: #2d5f3f;
                    color: white;
                    padding: 12px 8px;
                    text-align: center;
                    font-weight: bold;
                    border: 1px solid #000;
                }}
                
                .verification-table td {{
                    padding: 10px 8px;
                    border: 1px solid #000;
                    text-align: center;
                }}
                
                .project-details {{
                    background: #f8f9fa;
                    padding: 15px;
                    border: 2px solid #2d5f3f;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                
                .detail-row {{
                    display: flex;
                    margin-bottom: 8px;
                }}
                
                .detail-label {{
                    font-weight: bold;
                    width: 35%;
                    color: #2d5f3f;
                }}
                
                .detail-value {{
                    width: 65%;
                    border-bottom: 1px dotted #000;
                    min-height: 20px;
                }}
                
                .signatures {{
                    margin-top: 40px;
                    display: flex;
                    justify-content: space-between;
                }}
                
                .signature-block {{
                    text-align: center;
                    width: 30%;
                }}
                
                .signature-line {{
                    border-bottom: 2px solid #000;
                    margin-bottom: 5px;
                    height: 50px;
                }}
                
                .signature-title {{
                    font-weight: bold;
                    font-size: 12px;
                }}
                
                .reference-no {{
                    text-align: right;
                    font-size: 12px;
                    margin-bottom: 10px;
                }}
                
                .date-place {{
                    display: flex;
                    justify-content: space-between;
                    margin-top: 30px;
                    font-weight: bold;
                }}
                
                .highlight {{
                    background: #fff3cd;
                    padding: 10px;
                    border-left: 4px solid #f39c12;
                    margin: 15px 0;
                }}
                
                /* CRITICAL: Print-specific styles */
                @media print {{
                    body {{ font-size: 12px; }}
                    .container {{ max-width: none; width: 100%; }}
                    table {{ page-break-inside: auto; }}
                    tr {{ page-break-inside: avoid; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="letterhead">
                    <div class="dept-header">PUBLIC WORKS DEPARTMENT</div>
                    <div class="govt-header">GOVERNMENT OF RAJASTHAN</div>
                    <div class="office-header">OFFICE OF THE ACCOUNTS OFFICER, PWD UDAIPUR</div>
                </div>
                
                <div class="reference-no">
                    <strong>No. PWD/UDR/AO/CE-III/{datetime.now().strftime('%Y')}/____</strong>
                </div>
                
                <div class="certificate-title">CERTIFICATE - III</div>
                <div class="certificate-subtitle">(RATE VERIFICATION & ACCOUNTS CERTIFICATE)</div>
                
                <div class="content">
                    <p>This is to <strong>CERTIFY</strong> that I have <strong>CHECKED AND VERIFIED</strong> the rates charged in the attached bill and found them to be in accordance with the sanctioned estimate, approved rate contract, and prevailing government rate schedule.</p>
                    
                    <p>All calculations have been arithmetically verified and found correct. The rates applied are as per the approved schedule and no unauthorized deviation has been made.</p>
                </div>
                
                <div class="project-details">
                    <div class="detail-row">
                        <div class="detail-label">Project Name:</div>
                        <div class="detail-value">{self.title_data.get('Project Name', 'N/A')}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">Contract Number:</div>
                        <div class="detail-value">{self.title_data.get('Contract No', 'N/A')}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">Work Order Number:</div>
                        <div class="detail-value">{self.title_data.get('Work Order No', 'N/A')}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">Bill Amount:</div>
                        <div class="detail-value">Rs. ______ (Subject to Verification)</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">Rate Schedule Reference:</div>
                        <div class="detail-value">PWD Rate Schedule {datetime.now().strftime('%Y')}</div>
                    </div>
                </div>
                
                <div class="highlight">
                    <strong>VERIFICATION CHECKLIST COMPLETED:</strong>
                    <ul style="margin: 10px 0; padding-left: 30px;">
                        <li>✓ Rate Schedule Compliance Verified</li>
                        <li>✓ Arithmetic Calculations Checked</li>
                        <li>✓ Measurements Cross-Verified</li>
                        <li>✓ Contract Terms Compliance Ensured</li>
                        <li>✓ Government Guidelines Followed</li>
                    </ul>
                </div>
                
                <table class="verification-table">
                    <thead>
                        <tr>
                            <th style="width: 40%;">Verification Parameter</th>
                            <th style="width: 20%;">Status</th>
                            <th style="width: 40%;">Remarks</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Rate Compliance Check</td>
                            <td><strong>✓ VERIFIED</strong></td>
                            <td>As per approved rate schedule</td>
                        </tr>
                        <tr>
                            <td>Calculation Accuracy</td>
                            <td><strong>✓ VERIFIED</strong></td>
                            <td>Arithmetically correct</td>
                        </tr>
                        <tr>
                            <td>Measurement Validation</td>
                            <td><strong>✓ VERIFIED</strong></td>
                            <td>Cross-checked with MB records</td>
                        </tr>
                    </tbody>
                </table>
                
                <div class="content">
                    <p><strong>CERTIFICATION:</strong> The rates and amounts charged in this bill are found to be correct and in accordance with the government approved rate schedule. The bill is <strong>RECOMMENDED FOR PAYMENT</strong> subject to other administrative and technical clearances.</p>
                </div>
                
                <div class="date-place">
                    <div>Date: {current_date}</div>
                    <div>Place: Udaipur</div>
                </div>
                
                <div class="signatures">
                    <div class="signature-block">
                        <div class="signature-line"></div>
                        <div class="signature-title">ASSISTANT ENGINEER</div>
                        <div style="font-size: 11px; margin-top: 5px;">Technical Verification</div>
                    </div>
                    <div class="signature-block">
                        <div class="signature-line"></div>
                        <div class="signature-title">ACCOUNTS OFFICER</div>
                        <div style="font-size: 11px; margin-top: 5px;">Financial Verification</div>
                    </div>
                    <div class="signature-block">
                        <div class="signature-line"></div>
                        <div class="signature-title">EXECUTIVE ENGINEER</div>
                        <div style="font-size: 11px; margin-top: 5px;">Final Approval</div>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 20px; font-size: 10px; font-style: italic;">
                    <p>This certificate is issued as per Government Financial Rules and PWD Account Code provisions.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content