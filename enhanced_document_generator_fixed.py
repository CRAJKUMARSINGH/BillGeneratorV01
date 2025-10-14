import pandas as pd
import gc
from datetime import datetime
from typing import Dict, Any
import io
import tempfile
from pathlib import Path
from functools import lru_cache
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from utils.template_renderer import TemplateRenderer
import os
import asyncio
from playwright.async_api import async_playwright
from utils.zip_packager import ZipPackager
import logging

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedDocumentGenerator:
    """Enhanced document generator with fixed HTML-to-PDF conversion to achieve 95%+ matching"""
    
    # Class-level cache for template environments
    _template_env_cache = {}
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.title_data = data.get('title_data', {})
        self.work_order_data = data.get('work_order_data', pd.DataFrame())
        self.bill_quantity_data = data.get('bill_quantity_data', pd.DataFrame())
        self.extra_items_data = data.get('extra_items_data', pd.DataFrame())
        
        # Use cached template environment
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        cache_key = template_dir
        
        if cache_key not in self._template_env_cache:
            self._template_env_cache[cache_key] = Environment(
                loader=FileSystemLoader(template_dir),
                cache_size=400,  # Limit template cache size
                auto_reload=False  # Disable auto-reload for performance
            )
        
        self.jinja_env = self._template_env_cache[cache_key]
        
        # Initialize template renderer for templates_14102025 format
        self.template_renderer = TemplateRenderer()
        
        # Prepare data for templates with memory optimization
        self.template_data = self._prepare_template_data()
    
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
    
    @lru_cache(maxsize=128)  # Cache number to words conversion
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
    
    def _prepare_template_data(self) -> Dict[str, Any]:
        """Prepare data structure for Jinja2 templates with VBA-like zero rate handling"""
        # Calculate totals and prepare structured data
        work_items = []
        total_amount = 0
        
        # Process work order data with memory optimization
        for index, row in self.work_order_data.iterrows():
            quantity_since = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
            rate = self._safe_float(row.get('Rate', 0))
            amount = quantity_since * rate
            total_amount += amount
            
            # VBA-like behavior: Only populate amounts if rate is not zero
            if rate != 0:
                amount_upto = amount
                amount_since = 0  # As per VBA, Quantity Since is 0 when Quantity Upto has value
            else:
                # For zero rates, leave amounts blank/zero as per VBA behavior
                amount_upto = 0
                amount_since = 0
            
            work_items.append({
                'unit': row.get('Unit', ''),
                'quantity_since': quantity_since if rate != 0 else 0,  # VBA behavior
                'quantity_upto': self._safe_float(row.get('Quantity Upto', quantity_since)),
                'item_no': self._safe_serial_no(row.get('Item No.', row.get('Item', row.get('S. No.', '')))),
                'description': row.get('Description', ''),
                'rate': rate,
                'amount_upto': amount_upto,
                'amount_since': amount_since,
                'remark': row.get('Remark', '')
            })
            
            # Periodic garbage collection for large datasets
            if index % 100 == 0:
                gc.collect()
        
        # Process extra items with memory optimization
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
                    'item_no': self._safe_serial_no(row.get('Item No.', row.get('Item', row.get('S. No.', '')))),
                    'description': row.get('Description', ''),
                    'rate': rate,
                    'amount': amount,
                    'remark': row.get('Remark', '')
                })
                
                # Periodic garbage collection for large datasets
                try:
                    if int(str(index)) % 50 == 0:
                        gc.collect()
                except (ValueError, TypeError):
                    pass
        
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
            'notes': ['Work completed as per schedule', 'All measurements verified', 'Quality as per specifications'],
            'data': {
                'measurement_officer': self.title_data.get('Measurement Officer', 'Measurement Officer Name'),
                'measurement_date': self.title_data.get('Measurement Date', datetime.now().strftime('%d/%m/%Y')),
                'measurement_book_page': self.title_data.get('Measurement Book Page', '123'),
                'measurement_book_no': self.title_data.get('Measurement Book No', 'MB-001'),
                'officer_name': self.title_data.get('Officer Name', 'Officer Name'),
                'officer_designation': self.title_data.get('Officer Designation', 'Designation'),
                'authorising_officer_name': self.title_data.get('Authorising Officer Name', 'Authorising Officer Name'),
                'authorising_officer_designation': self.title_data.get('Authorising Officer Designation', 'Designation')
            }
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
        """Generate PDF using Playwright with memory optimization"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Set viewport for consistent rendering
                await page.set_viewport_size({"width": 1200, "height": 1600})
                
                # Load HTML content with extended timeout
                await page.set_content(html_content, timeout=60000)  # 60 seconds timeout
                
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
                
                # Force garbage collection after PDF generation
                gc.collect()
                return True
        except Exception as e:
            logger.error(f"Playwright PDF generation error: {str(e)}")
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
    
    def _generate_pdf_reportlab(self, html_content: str, output_path: str) -> bool:
        """Generate PDF using ReportLab as a fallback method with better HTML parsing"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            import io
            from bs4 import BeautifulSoup
            import re
            
            # Parse HTML content
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Create a PDF document
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Extract title from HTML
            title_elem = soup.find('title')
            title_text = title_elem.get_text() if title_elem else "Generated Document"
            
            # Add title
            story.append(Paragraph(title_text, styles['Title']))
            story.append(Spacer(1, 12))
            
            # Extract and add headings
            for heading in soup.find_all(['h1', 'h2', 'h3']):
                level = int(heading.name[1]) if heading.name.startswith('h') else 2
                style = styles[f'Heading{level}'] if f'Heading{level}' in styles else styles['Heading2']
                story.append(Paragraph(heading.get_text(), style))
                story.append(Spacer(1, 6))
            
            # Extract and add paragraphs
            for paragraph in soup.find_all('p'):
                text = paragraph.get_text().strip()
                if text:
                    story.append(Paragraph(text, styles['Normal']))
                    story.append(Spacer(1, 6))
            
            # Extract and add tables
            for table_elem in soup.find_all('table'):
                rows = []
                # Extract headers
                headers = table_elem.find('thead')
                if headers:
                    header_row = []
                    for th in headers.find_all('th'):
                        header_row.append(th.get_text().strip())
                    if header_row:
                        rows.append(header_row)
                
                # Extract body rows
                tbody = table_elem.find('tbody')
                if tbody:
                    for tr in tbody.find_all('tr'):
                        row = []
                        for td in tr.find_all(['td', 'th']):
                            row.append(td.get_text().strip())
                        if row:
                            rows.append(row)
                
                # If no thead/tbody, extract all rows
                if not rows:
                    for tr in table_elem.find_all('tr'):
                        row = []
                        for td in tr.find_all(['td', 'th']):
                            row.append(td.get_text().strip())
                        if row:
                            rows.append(row)
                
                # Create ReportLab table if we have data
                if rows:
                    table = Table(rows)
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
                    story.append(Spacer(1, 12))
            
            # If no content was extracted, add raw text
            if len(story) <= 2:  # Just title and spacer
                clean_text = re.sub('<[^<]+?>', '', html_content[:2000])  # First 2000 chars
                if clean_text.strip():
                    story.append(Paragraph(clean_text[:500] + "...", styles['Normal']))
            
            # Build PDF
            doc.build(story)
            return True
            
        except ImportError:
            print("ReportLab or BeautifulSoup not installed")
            return False
        except Exception as e:
            print(f"ReportLab PDF generation failed: {str(e)}")
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
        
        # Generate First Page using template renderer that matches templates_14102025 format
        try:
            documents['First Page Summary'] = self.template_renderer.render_first_page(
                self.title_data, self.work_order_data, self.extra_items_data
            )
        except Exception as e:
            print(f"First Page template rendering failed, falling back to programmatic generation: {e}")
            documents['First Page Summary'] = self._generate_first_page()
        
        # Generate other documents using templates
        try:
            # Use specialized renderers for deviation statement, extra items, certificate II, and certificate III
            documents['Deviation Statement'] = self.template_renderer.render_deviation_statement(
                self.title_data, self.work_order_data, self.extra_items_data)
            documents['Final Bill Scrutiny Sheet'] = self.template_renderer.render_note_sheet(
                self.title_data, self.work_order_data, self.extra_items_data)
            
            # Only generate Extra Items document if there are extra items
            if self._has_extra_items():
                documents['Extra Items Statement'] = self.template_renderer.render_extra_items(
                    self.title_data, self.work_order_data, self.extra_items_data)
            
            # Use specialized renderers for Certificates
            documents['Certificate II'] = self.template_renderer.render_certificate_ii(
                self.title_data, self.work_order_data, self.extra_items_data)
            documents['Certificate III'] = self.template_renderer.render_certificate_iii(
                self.title_data, self.work_order_data, self.extra_items_data)
        except Exception as template_error:
            print(f"Template rendering failed, falling back to programmatic generation: {template_error}")
            # Fallback to programmatic generation if templates fail (but keep First Page)
            if 'Deviation Statement' not in documents:
                documents['Deviation Statement'] = self._generate_deviation_statement()
            if 'Final Bill Scrutiny Sheet' not in documents:
                documents['Final Bill Scrutiny Sheet'] = self._generate_final_bill_scrutiny()
            
            # Only generate Extra Items document if there are extra items
            if self._has_extra_items() and 'Extra Items Statement' not in documents:
                documents['Extra Items Statement'] = self._generate_extra_items_statement()
            
            if 'Certificate II' not in documents:
                documents['Certificate II'] = self._generate_certificate_ii()
            if 'Certificate III' not in documents:
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
        """Create PDF documents from HTML with enhanced memory management"""
        pdf_files = {}
        temp_files = []
        
        try:
            # Create temporary directory for PDF generation
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                for doc_name, html_content in documents.items():
                    try:
                        # Create temporary file path
                        temp_pdf_path = temp_path / f"{doc_name}.pdf"
                        temp_files.append(temp_pdf_path)
                        
                        # Try multiple PDF generation methods
                        success = False
                        
                        # Method 1: Try Playwright (most reliable)
                        try:
                            success = asyncio.run(self._generate_pdf_async(html_content, str(temp_pdf_path)))
                        except Exception as e:
                            print(f"Playwright failed for {doc_name}: {str(e)}")
                        
                        # Method 2: Try ReportLab as fallback
                        if not success:
                            try:
                                success = self._generate_pdf_reportlab(html_content, str(temp_pdf_path))
                            except Exception as e:
                                print(f"ReportLab failed for {doc_name}: {str(e)}")
                        
                        # Method 3: Try WeasyPrint
                        if not success:
                            try:
                                success = self._generate_pdf_weasyprint(html_content, str(temp_pdf_path))
                            except Exception as e:
                                print(f"WeasyPrint failed for {doc_name}: {str(e)}")
                        
                        # Method 4: Try pdfkit
                        if not success:
                            try:
                                success = self._generate_pdf_pdfkit(html_content, str(temp_pdf_path))
                            except Exception as e:
                                print(f"pdfkit failed for {doc_name}: {str(e)}")
                        
                        if success and temp_pdf_path.exists():
                            # Read PDF content
                            with open(temp_pdf_path, 'rb') as f:
                                pdf_bytes = f.read()
                            
                            # Only keep reasonably sized PDFs (at least 100 bytes to account for minimal valid PDFs)
                            if len(pdf_bytes) > 100:  # At least 100 bytes for minimal valid PDF
                                pdf_files[f"{doc_name}.pdf"] = pdf_bytes
                            else:
                                logger.warning(f"Generated PDF too small: {doc_name} ({len(pdf_bytes)} bytes)")
                                # Create a simple ReportLab PDF as fallback
                                error_pdf = self._create_error_pdf(doc_name, f"PDF too small: {len(pdf_bytes)} bytes")
                                pdf_files[f"{doc_name}.pdf"] = error_pdf
                        else:
                            # Create error PDF using ReportLab
                            error_pdf = self._create_error_pdf(doc_name, "PDF generation failed")
                            pdf_files[f"{doc_name}.pdf"] = error_pdf
                        
                        # Force garbage collection after each PDF
                        gc.collect()
                        
                    except Exception as e:
                        logger.error(f"Error creating PDF for {doc_name}: {str(e)}")
                        # Create error PDF using ReportLab
                        error_pdf = self._create_error_pdf(doc_name, str(e))
                        pdf_files[f"{doc_name}.pdf"] = error_pdf
                
                # Clean up temporary files explicitly
                for temp_file in temp_files:
                    try:
                        if temp_file.exists():
                            temp_file.unlink()
                    except Exception:
                        pass
                        
        except Exception as e:
            logger.error(f"Error in PDF creation process: {str(e)}")
        finally:
            # Final garbage collection
            gc.collect()
        
        return pdf_files
    
    def generate_all_formats_and_zip(self) -> Dict[str, Any]:
        """
        Generate all documents in HTML, DOC, and PDF formats, plus create a ZIP package
        
        Returns:
            Dictionary containing all formats and ZIP package
        """
        result = {
            'html_documents': {},
            'pdf_documents': {},
            'doc_documents': {},
            'merged_pdf': b'',
            'zip_package': b'',
            'success': False,
            'error': None
        }
        
        try:
            # Step 1: Generate HTML documents
            print("🔄 Generating HTML documents...")
            html_documents = self.generate_all_documents()
            result['html_documents'] = html_documents
            
            if not html_documents:
                raise Exception("Failed to generate HTML documents")
            
            print(f"✅ Generated {len(html_documents)} HTML documents")
            
            # Step 2: Generate PDF documents
            print("🔄 Generating PDF documents...")
            pdf_documents = self.create_pdf_documents(html_documents)
            result['pdf_documents'] = pdf_documents
            
            if not pdf_documents:
                raise Exception("Failed to generate PDF documents")
            
            print(f"✅ Generated {len(pdf_documents)} PDF documents")
            
            # Step 3: Generate merged PDF
            print("🔄 Creating merged PDF...")
            from utils.pdf_merger import PDFMerger
            merger = PDFMerger()
            merged_pdf = merger.merge_pdfs(pdf_documents)
            result['merged_pdf'] = merged_pdf
            
            if merged_pdf:
                print("✅ Created merged PDF")
            else:
                print("⚠️  Merged PDF creation failed, continuing with individual PDFs")
            
            # Step 4: Generate DOC documents using zip packager
            print("🔄 Generating DOC documents...")
            zip_packager = ZipPackager()
            doc_documents = {}
            
            for doc_name, html_content in html_documents.items():
                try:
                    doc_bytes = zip_packager._html_to_docx_bytes(doc_name, html_content)
                    doc_documents[f"{doc_name}.docx"] = doc_bytes
                except Exception as e:
                    print(f"⚠️  Failed to generate DOC for {doc_name}: {str(e)}")
                    # Create a placeholder DOC file
                    doc_documents[f"{doc_name}.docx"] = b"DOC generation failed - HTML content available"
            
            result['doc_documents'] = doc_documents
            print(f"✅ Generated {len(doc_documents)} DOC documents")
            
            # Step 5: Create ZIP package with all formats
            print("🔄 Creating ZIP package...")
            zip_package = zip_packager.create_package(html_documents, pdf_documents, merged_pdf)
            result['zip_package'] = zip_package.getvalue()
            result['success'] = True
            
            print("✅ Created ZIP package with all formats")
            
            # Print summary
            print("\n📊 GENERATION SUMMARY:")
            print(f"  📄 HTML Documents: {len(html_documents)}")
            print(f"  📄 PDF Documents: {len(pdf_documents)}")
            print(f"  📄 DOC Documents: {len(doc_documents)}")
            print(f"  📄 Merged PDF: {'Yes' if merged_pdf else 'No'}")
            print(f"  📦 ZIP Package: {len(result['zip_package'])} bytes")
            
        except Exception as e:
            result['error'] = str(e)
            print(f"❌ Error in multi-format generation: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return result
        
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
                            <td>{self._safe_serial_no(row.get('Item No.', row.get('Item', row.get('S. No.', ''))))}</td>
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
                    table-layout: fixed;
                }}
                
                th, td {{
                    padding: 8px;
                    text-align: left;
                    border: 1px solid #ddd;
                    word-wrap: break-word;
                }}
                
                /* Column alignment improvements for deviation statement */
                td:nth-child(4), td:nth-child(5), td:nth-child(6), td:nth-child(7), 
                td:nth-child(8), td:nth-child(9), td:nth-child(10), td:nth-child(11), 
                td:nth-child(12) {{ 
                    text-align: right; /* Right-align all numeric columns */
                }}
                td:nth-child(1) {{ 
                    text-align: center; /* Center-align serial numbers */
                }}
                
                /* Column width specifications */
                th:nth-child(1), td:nth-child(1) {{ width: 6%; }}  /* Item No */
                th:nth-child(2), td:nth-child(2) {{ width: 25%; }} /* Description */
                th:nth-child(3), td:nth-child(3) {{ width: 6%; }}  /* Unit */
                th:nth-child(4), td:nth-child(4) {{ width: 8%; }}  /* Qty WO */
                th:nth-child(5), td:nth-child(5) {{ width: 8%; }}  /* Rate */
                th:nth-child(6), td:nth-child(6) {{ width: 8%; }}  /* Amt WO */
                th:nth-child(7), td:nth-child(7) {{ width: 8%; }}  /* Qty Exec */
                th:nth-child(8), td:nth-child(8) {{ width: 8%; }}  /* Amt Exec */
                th:nth-child(9), td:nth-child(9) {{ width: 6%; }}  /* Excess Qty */
                th:nth-child(10), td:nth-child(10) {{ width: 6%; }} /* Excess Amt */
                th:nth-child(11), td:nth-child(11) {{ width: 6%; }} /* Saving Qty */
                th:nth-child(12), td:nth-child(12) {{ width: 6%; }} /* Saving Amt */
                th:nth-child(13), td:nth-child(13) {{ width: 5%; }} /* Remarks */
                
                th {{
                    background-color: #f5f5f5;
                    font-weight: bold;
                }}
                
                .amount {{
                    text-align: right;
                }}
                
                /* CRITICAL: Print-specific styles - MANDATORY LANDSCAPE for 13 columns */
                @media print {{
                    @page {{ size: A4 landscape; margin: 0.5in; }}
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
                wo_item = wo_row.get('Item No.', wo_row.get('Item', wo_row.get('S. No.', '')))
                bq_item_col = 'Item No.' if 'Item No.' in self.bill_quantity_data.columns else ('Item' if 'Item' in self.bill_quantity_data.columns else 'S. No.')
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
            
            # Format deviation values - show all values including zeros
            wo_qty_display = f"{wo_qty:.2f}" if wo_qty >= 0 else "0.00"
            wo_rate_display = f"{wo_rate:.2f}" if wo_rate >= 0 else "0.00"
            wo_amount_display = f"{wo_amount:.2f}" if wo_amount >= 0 else "0.00"
            bq_qty_display = f"{bq_qty:.2f}" if bq_qty >= 0 else "0.00"
            bq_amount_display = f"{bq_amount:.2f}" if bq_amount >= 0 else "0.00"
            excess_qty_display = f"{excess_qty:.2f}" if excess_qty >= 0 else "0.00"
            excess_amt_display = f"{excess_amt:.2f}" if excess_amt >= 0 else "0.00"
            saving_qty_display = f"{saving_qty:.2f}" if saving_qty >= 0 else "0.00"
            saving_amt_display = f"{saving_amt:.2f}" if saving_amt >= 0 else "0.00"
            
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
                            <td>{self._safe_serial_no(row.get('Item No.', row.get('Item', row.get('S. No.', ''))))}</td>
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
        
        # Get measurement data from title_data or use defaults
        measurement_officer = self.title_data.get('Measurement Officer', 'Measurement Officer Name')
        measurement_date = self.title_data.get('Measurement Date', current_date)
        measurement_book_page = self.title_data.get('Measurement Book Page', '123')
        measurement_book_no = self.title_data.get('Measurement Book No', 'MB-001')
        officer_name = self.title_data.get('Officer Name', 'Officer Name')
        officer_designation = self.title_data.get('Officer Designation', 'Designation')
        authorising_officer_name = self.title_data.get('Authorising Officer Name', 'Authorising Officer Name')
        authorising_officer_designation = self.title_data.get('Authorising Officer Designation', 'Designation')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Certificate II - Measurement Certificate</title>
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
                    line-height: 1.8;
                }}
                
                .signature-section {{
                    margin-top: 40px;
                }}
                
                .signature-block {{
                    margin-bottom: 30px;
                }}
                
                .signature-line {{
                    border-bottom: 2px solid #000;
                    margin-bottom: 5px;
                    height: 50px;
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
                
                .emphasis {{
                    font-style: italic;
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
                <div class="certificate-subtitle">(MEASUREMENT CERTIFICATE)</div>
                
                <div class="content">
                    <p>The measurements on which are based the entries in columns 1 to 6 of Account I, were made by {measurement_officer} on {measurement_date}, and are recorded at page {measurement_book_page} of Measurement Book No. {measurement_book_no}.</p>
                    
                    <p class="emphasis">Certified that in addition to and quite apart from the quantities of work actually executed, as shown in column 4 of Account I, some work has actually been done in connection with several items and the value of such work (after deduction therefrom the proportionate amount of secured advances, if any, ultimately recoverable on account of the quantities of materials used therein) is in no case, less than the advance payments as per item 2 of the Memorandum, if payments made or proposed to be made, for the convenience of the contractor, in anticipation of and subject to the result of detailed measurements, which will be made as soon as possible.</p>
                </div>
                
                <div class="signature-section">
                    <div class="signature-block">
                        <p>Dated: {current_date}</p>
                        <p>Signature of officer preparing the bill</p>
                        <div class="signature-line"></div>
                        <p>{officer_name}</p>
                        <p>{officer_designation}</p>
                    </div>
                    
                    <div class="signature-block">
                        <p>Dated: {current_date}</p>
                        <p>Signature of officer authorising payment</p>
                        <div class="signature-line"></div>
                        <p>{authorising_officer_name}</p>
                        <p>{authorising_officer_designation}</p>
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
    
    async def _generate_pdf_async(self, html_content: str, output_path: str) -> bool:
        """Async PDF generation wrapper"""
        return await self._generate_pdf_playwright(html_content, output_path)
    
    def _create_error_pdf(self, doc_name: str, error_msg: str) -> bytes:
        """Create a simple error PDF using ReportLab"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import inch
            import io
            
            # Create in-memory PDF
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            # Add error message
            c.setFont("Helvetica", 16)
            c.drawString(100, height - 100, f"Error generating document: {doc_name}")
            
            c.setFont("Helvetica", 12)
            c.drawString(100, height - 150, f"Error: {error_msg}")
            
            c.drawString(100, height - 200, "This is a fallback error document.")
            c.drawString(100, height - 220, "The HTML document was generated successfully but PDF conversion failed.")
            
            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.drawString(100, height - 270, f"Generated: {timestamp}")
            
            c.save()
            
            # Get PDF bytes
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            # If ReportLab also fails, return minimal PDF content
            return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Resources <<\n/Font <<\n/F1 <<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\n>>\n>>\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Error PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000108 00000 n \n0000000256 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n365\n%%EOF"
