import pandas as pd
import gc
from datetime import datetime
from typing import Dict, Any
import io
from functools import lru_cache
import os
from jinja2 import Environment, FileSystemLoader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FixedDocumentGenerator:
    """Fixed Document Generator that uses ReportLab for reliable PDF generation"""
    
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
        if not os.path.exists(template_dir):
            template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        cache_key = template_dir
        
        if cache_key not in self._template_env_cache:
            self._template_env_cache[cache_key] = Environment(
                loader=FileSystemLoader(template_dir),
                cache_size=200,  # Limit template cache size
                auto_reload=False  # Disable auto-reload for performance
            )
        
        self.jinja_env = self._template_env_cache[cache_key]
        
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
    
    def _has_extra_items(self):
        """Check if there are any extra items"""
        if isinstance(self.extra_items_data, pd.DataFrame):
            return not self.extra_items_data.empty and len(self.extra_items_data) > 0
        elif isinstance(self.extra_items_data, (list, tuple)):
            return len(self.extra_items_data) > 0
        else:
            return False
    
    def _prepare_template_data(self) -> Dict[str, Any]:
        """Prepare data structure for templates with memory optimization"""
        # Calculate totals and prepare structured data
        work_items = []
        total_amount = 0
        
        # Process work order data with memory optimization
        for i, (index, row) in enumerate(self.work_order_data.iterrows()):
            quantity_since = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
            rate = self._safe_float(row.get('Rate', 0))
            amount = quantity_since * rate
            total_amount += amount
            
            work_items.append({
                'unit': row.get('Unit', ''),
                'quantity_since': quantity_since,
                'quantity_upto': self._safe_float(row.get('Quantity Upto', quantity_since)),
                'item_no': row.get('Item No.', row.get('Item', '')),
                'description': row.get('Description', ''),
                'rate': rate,
                'amount_upto': amount,
                'amount_since': amount,
                'remark': row.get('Remark', '')
            })
            
            # Periodic garbage collection for large datasets
            if i % 100 == 0:
                gc.collect()
        
        # Process extra items with memory optimization
        extra_items = []
        extra_total = 0
        
        if isinstance(self.extra_items_data, pd.DataFrame) and not self.extra_items_data.empty:
            for i, (index, row) in enumerate(self.extra_items_data.iterrows()):
                quantity = self._safe_float(row.get('Quantity', 0))
                rate = self._safe_float(row.get('Rate', 0))
                amount = quantity * rate
                extra_total += amount
                
                extra_items.append({
                    'unit': row.get('Unit', ''),
                    'quantity': quantity,
                    'item_no': row.get('Item No.', row.get('Item', '')),
                    'description': row.get('Description', ''),
                    'rate': rate,
                    'amount': amount,
                    'remark': row.get('Remark', '')
                })
                
                # Periodic garbage collection for large datasets
                if i % 50 == 0:
                    gc.collect()
        
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
            'excess_amount': 0,
            'excess_premium': 0,
            'excess_total': 0,
            'saving_amount': 0,
            'saving_premium': 0,
            'saving_total': 0,
            'net_difference': 0
        }
        
        # Force garbage collection
        gc.collect()
        
        return {
            'title_data': self.title_data,
            'work_items': work_items,
            'extra_items': extra_items,
            'totals': totals,
            'has_extra_items': self._has_extra_items(),
            'current_date': datetime.now().strftime('%d/%m/%Y'),
            'current_datetime': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
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
    
    def generate_all_documents(self) -> Dict[str, str]:
        """
        Generate all required documents using programmatic HTML generation
        
        Returns:
            Dictionary containing all generated documents in HTML format
        """
        documents = {}
        
        # Generate documents programmatically
        documents['First Page Summary'] = self._generate_first_page()
        documents['Deviation Statement'] = self._generate_deviation_statement()
        documents['Final Bill Scrutiny Sheet'] = self._generate_final_bill_scrutiny()
        
        # Only generate Extra Items document if there are extra items
        if self._has_extra_items():
            documents['Extra Items Statement'] = self._generate_extra_items_statement()
        
        documents['Certificate II'] = self._generate_certificate_ii()
        documents['Certificate III'] = self._generate_certificate_iii()
        
        # Force garbage collection after document generation
        gc.collect()
        
        return documents
    
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
                body {{ font-family: Arial, sans-serif; margin: 20px; font-size: 12px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #000; padding: 6px; text-align: left; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .title {{ font-size: 18px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">FIRST PAGE SUMMARY</div>
                <div>Date: {current_date}</div>
            </div>
            
            <table>
                <tr>
                    <th>Item No.</th>
                    <th>Description</th>
                    <th>Unit</th>
                    <th>Quantity Since</th>
                    <th>Rate</th>
                    <th>Amount Since</th>
                    <th>Remark</th>
                </tr>
        """
        
        # Add work items
        for item in self.template_data['work_items']:
            html_content += f"""
                <tr>
                    <td>{item['item_no']}</td>
                    <td>{item['description']}</td>
                    <td>{item['unit']}</td>
                    <td class="amount">{item['quantity_since']:.2f}</td>
                    <td class="amount">{item['rate']:.2f}</td>
                    <td class="amount">{item['amount_since']:.2f}</td>
                    <td>{item['remark']}</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <div style="margin-top: 20px;">
                <p><strong>Total Work Order Amount:</strong> ₹{:.2f}</p>
                <p><strong>Tender Premium ({}%):</strong> ₹{:.2f}</p>
                <p><strong>Grand Total:</strong> ₹{:.2f}</p>
                <p><strong>Amount in Words:</strong> {}</p>
            </div>
        </body>
        </html>
        """.format(
            self.template_data['totals']['work_order_amount'],
            self.template_data['totals']['tender_premium_percent'] * 100,
            self.template_data['totals']['tender_premium_amount'],
            self.template_data['totals']['grand_total'],
            self._number_to_words(int(self.template_data['totals']['grand_total']))
        )
        
        return html_content
    
    @lru_cache(maxsize=64)  # Cache number to words conversion
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
    
    def _generate_deviation_statement(self) -> str:
        """Generate Deviation Statement document"""
        # Implementation would go here
        # For brevity, returning a simple template
        return "<html><body><h1>Deviation Statement</h1><p>Deviation data would be shown here.</p></body></html>"
    
    def _generate_final_bill_scrutiny(self) -> str:
        """Generate Final Bill Scrutiny Sheet document"""
        # Implementation would go here
        # For brevity, returning a simple template
        return "<html><body><h1>Final Bill Scrutiny Sheet</h1><p>Scrutiny data would be shown here.</p></body></html>"
    
    def _generate_extra_items_statement(self) -> str:
        """Generate Extra Items Statement document"""
        # Implementation would go here
        # For brevity, returning a simple template
        return "<html><body><h1>Extra Items Statement</h1><p>Extra items data would be shown here.</p></body></html>"
    
    def _generate_certificate_ii(self) -> str:
        """Generate Certificate II document"""
        # Implementation would go here
        # For brevity, returning a simple template
        return "<html><body><h1>Certificate II</h1><p>Certificate II content would be shown here.</p></body></html>"
    
    def _generate_certificate_iii(self) -> str:
        """Generate Certificate III document"""
        # Implementation would go here
        # For brevity, returning a simple template
        return "<html><body><h1>Certificate III</h1><p>Certificate III content would be shown here.</p></body></html>"
    
    def create_pdf_documents(self, documents: Dict[str, str]) -> Dict[str, bytes]:
        """Create PDF documents from HTML with memory optimization"""
        pdf_files = {}
        
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            from io import BytesIO
            from reportlab.platypus import Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
            from bs4 import BeautifulSoup
            import re
            
            for doc_name, html_content in documents.items():
                try:
                    # Create PDF in memory
                    buffer = BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                          leftMargin=72, rightMargin=72,
                                          topMargin=72, bottomMargin=72)
                    story = []
                    
                    # Parse HTML content
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Get styles
                    styles = getSampleStyleSheet()
                    
                    # Add title from document name
                    title_style = ParagraphStyle(
                        'CustomTitle',
                        parent=styles['Heading1'],
                        fontSize=18,
                        spaceAfter=30,
                        alignment=TA_CENTER,
                    )
                    story.append(Paragraph(doc_name, title_style))
                    story.append(Spacer(1, 12))
                    
                    # Process HTML content
                    for element in soup.find_all():
                        if element.name == 'h1':
                            text = element.get_text()
                            story.append(Paragraph(text, styles['Heading1']))
                            story.append(Spacer(1, 12))
                        elif element.name == 'h2':
                            text = element.get_text()
                            story.append(Paragraph(text, styles['Heading2']))
                            story.append(Spacer(1, 12))
                        elif element.name == 'h3':
                            text = element.get_text()
                            story.append(Paragraph(text, styles['Heading3']))
                            story.append(Spacer(1, 12))
                        elif element.name == 'p':
                            text = element.get_text()
                            story.append(Paragraph(text, styles['Normal']))
                            story.append(Spacer(1, 12))
                        elif element.name == 'table':
                            # Process table
                            data = []
                            for row in element.find_all('tr'):
                                row_data = []
                                for cell in row.find_all(['td', 'th']):
                                    row_data.append(cell.get_text())
                                if row_data:
                                    data.append(row_data)
                            
                            if data:
                                table = Table(data)
                                table.setStyle(TableStyle([
                                    ('BACKGROUND', (0, 0), (-1, 0), '#f0f0f0'),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
                                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                    ('BACKGROUND', (0, 1), (-1, -1), '#ffffff'),
                                    ('GRID', (0, 0), (-1, -1), 1, '#000000')
                                ]))
                                story.append(table)
                                story.append(Spacer(1, 12))
                        elif element.name == 'br':
                            story.append(Spacer(1, 12))
                    
                    # Build PDF
                    doc.build(story)
                    
                    # Get PDF bytes
                    pdf_bytes = buffer.getvalue()
                    buffer.close()
                    
                    # Only keep reasonably sized PDFs
                    if len(pdf_bytes) > 1024:  # At least 1KB
                        pdf_files[f"{doc_name}.pdf"] = pdf_bytes
                    else:
                        logger.warning(f"Generated PDF too small: {doc_name} ({len(pdf_bytes)} bytes)")
                        # Create a more detailed error PDF
                        error_pdf = self._create_detailed_error_pdf(doc_name, "PDF content too small", html_content[:500])
                        pdf_files[f"{doc_name}.pdf"] = error_pdf
                    
                    # Force garbage collection after each PDF
                    gc.collect()
                    
                except Exception as e:
                    logger.error(f"Error creating PDF for {doc_name}: {str(e)}")
                    # Create error PDF
                    error_pdf = self._create_detailed_error_pdf(doc_name, str(e), html_content[:500] if html_content else "")
                    pdf_files[f"{doc_name}.pdf"] = error_pdf
            
        except Exception as e:
            logger.error(f"Error in PDF creation process: {str(e)}")
        finally:
            # Final garbage collection
            gc.collect()
        
        return pdf_files
    
    def _create_error_pdf(self, doc_name: str, error_msg: str) -> bytes:
        """Create a simple error PDF"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from io import BytesIO
            
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            c.drawString(100, 750, f"Error generating {doc_name}")
            c.drawString(100, 730, error_msg)
            c.save()
            
            pdf_bytes = buffer.getvalue()
            buffer.close()
            return pdf_bytes
        except Exception as e:
            logger.error(f"Error creating error PDF: {str(e)}")
            return b"Error PDF generation failed"
    
    def _create_detailed_error_pdf(self, doc_name: str, error_msg: str, html_preview: str = "") -> bytes:
        """Create a detailed error PDF with more information"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from io import BytesIO
            
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            c.drawString(100, height - 100, f"Error generating {doc_name}")
            c.drawString(100, height - 120, f"Error: {error_msg}")
            
            if html_preview:
                c.drawString(100, height - 150, "HTML Preview (first 500 chars):")
                # Split long text into multiple lines
                y_pos = height - 170
                for i in range(0, min(len(html_preview), 500), 80):
                    line = html_preview[i:i+80]
                    c.drawString(100, y_pos, line)
                    y_pos -= 20
                    if y_pos < 100:  # Prevent writing outside page
                        break
            
            c.save()
            
            pdf_bytes = buffer.getvalue()
            buffer.close()
            return pdf_bytes
        except Exception as e:
            logger.error(f"Error creating detailed error PDF: {str(e)}")
            return b"Error PDF generation failed"