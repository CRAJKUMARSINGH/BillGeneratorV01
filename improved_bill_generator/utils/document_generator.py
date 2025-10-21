"""
Enhanced Document Generator - Fallback compatible with original system
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DocumentGenerator:
    """Fallback document generator for compatibility"""
    
    def __init__(self, data):
        self.data = data
        self.title_data = data.get('title_data', {})
        self.work_order_data = data.get('work_order_data', pd.DataFrame())
        self.bill_quantity_data = data.get('bill_quantity_data', pd.DataFrame())
        self.extra_items_data = data.get('extra_items_data', pd.DataFrame())
    
    def _safe_float(self, value):
        """Safely convert value to float"""
        try:
            if pd.isna(value) or value == '' or value is None:
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _safe_str(self, value):
        """Safely convert value to string"""
        if pd.isna(value) or value is None:
            return ""
        return str(value)
    
    def generate_all_documents(self):
        """Generate all required documents"""
        documents = {}
        
        try:
            documents['First Page Summary'] = self._generate_first_page()
            documents['Bill Summary'] = self._generate_bill_summary()
            documents['Work Order Details'] = self._generate_work_order_details()
            
            if not self.extra_items_data.empty:
                documents['Extra Items'] = self._generate_extra_items()
            
            return documents
            
        except Exception as e:
            logger.error(f"Error generating documents: {str(e)}")
            raise
    
    def _generate_first_page(self):
        """Generate first page summary"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        project_name = self.title_data.get('Name of Work ;-', 'Project Name')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>First Page Summary</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; font-size: 12px; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .title {{ font-size: 18px; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #000; padding: 6px; text-align: left; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">FIRST PAGE SUMMARY</div>
                <div>Project: {project_name}</div>
                <div>Date: {current_date}</div>
            </div>
            
            <table>
                <tr>
                    <th>Item No.</th>
                    <th>Description</th>
                    <th>Unit</th>
                    <th>Quantity</th>
                    <th>Rate</th>
                    <th>Amount</th>
                </tr>
        """
        
        total_amount = 0
        
        # Add work items
        for index, row in self.work_order_data.iterrows():
            item_no = self._safe_str(row.get('Item No.', index + 1))
            description = self._safe_str(row.get('Description', ''))
            unit = self._safe_str(row.get('Unit', ''))
            quantity = self._safe_float(row.get('Quantity', 0))
            rate = self._safe_float(row.get('Rate', 0))
            amount = quantity * rate
            total_amount += amount
            
            html_content += f"""
                <tr>
                    <td>{item_no}</td>
                    <td>{description}</td>
                    <td>{unit}</td>
                    <td class="amount">{quantity:.2f}</td>
                    <td class="amount">{rate:.2f}</td>
                    <td class="amount">{amount:.2f}</td>
                </tr>
            """
        
        # Calculate premium and totals
        premium_percent = self._safe_float(self.title_data.get('TENDER PREMIUM %', 5.0))
        premium_amount = total_amount * (premium_percent / 100)
        grand_total = total_amount + premium_amount
        
        html_content += f"""
            </table>
            
            <div style="margin-top: 20px;">
                <p><strong>Work Order Amount:</strong> Rs. {total_amount:.2f}</p>
                <p><strong>Tender Premium ({premium_percent}%):</strong> Rs. {premium_amount:.2f}</p>
                <p><strong>Grand Total:</strong> Rs. {grand_total:.2f}</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_bill_summary(self):
        """Generate bill summary"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        # Calculate totals
        total_amount = 0
        for index, row in self.work_order_data.iterrows():
            quantity = self._safe_float(row.get('Quantity', 0))
            rate = self._safe_float(row.get('Rate', 0))
            total_amount += quantity * rate
        
        premium_percent = self._safe_float(self.title_data.get('TENDER PREMIUM %', 5.0))
        premium_amount = total_amount * (premium_percent / 100)
        gross_total = total_amount + premium_amount
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Bill Summary</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; font-size: 12px; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .title {{ font-size: 18px; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #000; padding: 8px; text-align: left; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">BILL SUMMARY</div>
                <div>Date: {current_date}</div>
            </div>
            
            <table>
                <tr><th>Description</th><th class="amount">Amount (Rs.)</th></tr>
                <tr><td>Work Order Amount</td><td class="amount">{total_amount:.2f}</td></tr>
                <tr><td>Tender Premium ({premium_percent}%)</td><td class="amount">{premium_amount:.2f}</td></tr>
                <tr><td><strong>Gross Total</strong></td><td class="amount"><strong>{gross_total:.2f}</strong></td></tr>
            </table>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_work_order_details(self):
        """Generate work order details"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Work Order Details</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; font-size: 10px; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .title {{ font-size: 16px; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #000; padding: 4px; text-align: left; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">WORK ORDER DETAILS</div>
                <div>Date: {current_date}</div>
            </div>
            
            <table>
                <tr>
                    <th>Item No.</th>
                    <th>Description</th>
                    <th>Unit</th>
                    <th>Quantity</th>
                    <th>Rate</th>
                    <th>Amount</th>
                    <th>Remarks</th>
                </tr>
        """
        
        for index, row in self.work_order_data.iterrows():
            item_no = self._safe_str(row.get('Item No.', index + 1))
            description = self._safe_str(row.get('Description', ''))
            if len(description) > 50:
                description = description[:47] + "..."
            unit = self._safe_str(row.get('Unit', ''))
            quantity = self._safe_float(row.get('Quantity', 0))
            rate = self._safe_float(row.get('Rate', 0))
            amount = quantity * rate
            remarks = self._safe_str(row.get('Remark', ''))
            
            html_content += f"""
                <tr>
                    <td>{item_no}</td>
                    <td>{description}</td>
                    <td>{unit}</td>
                    <td class="amount">{quantity:.2f}</td>
                    <td class="amount">{rate:.2f}</td>
                    <td class="amount">{amount:.2f}</td>
                    <td>{remarks}</td>
                </tr>
            """
        
        html_content += """
            </table>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_extra_items(self):
        """Generate extra items document"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Extra Items</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; font-size: 12px; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .title {{ font-size: 18px; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #000; padding: 6px; text-align: left; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">EXTRA ITEMS</div>
                <div>Date: {current_date}</div>
            </div>
            
            <table>
                <tr>
                    <th>Item No.</th>
                    <th>Description</th>
                    <th>Unit</th>
                    <th>Quantity</th>
                    <th>Rate</th>
                    <th>Amount</th>
                </tr>
        """
        
        total_extra = 0
        for index, row in self.extra_items_data.iterrows():
            item_no = self._safe_str(row.get('Item No.', f'E{index + 1}'))
            description = self._safe_str(row.get('Description', ''))
            unit = self._safe_str(row.get('Unit', ''))
            quantity = self._safe_float(row.get('Quantity', 0))
            rate = self._safe_float(row.get('Rate', 0))
            amount = quantity * rate
            total_extra += amount
            
            html_content += f"""
                <tr>
                    <td>{item_no}</td>
                    <td>{description}</td>
                    <td>{unit}</td>
                    <td class="amount">{quantity:.2f}</td>
                    <td class="amount">{rate:.2f}</td>
                    <td class="amount">{amount:.2f}</td>
                </tr>
            """
        
        html_content += f"""
            </table>
            
            <div style="margin-top: 20px;">
                <p><strong>Total Extra Items Amount:</strong> Rs. {total_extra:.2f}</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def create_pdf_documents(self, documents):
        """Create PDF documents from HTML - Basic implementation"""
        pdf_files = {}
        
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from bs4 import BeautifulSoup
            from io import BytesIO
            
            for doc_name, html_content in documents.items():
                try:
                    buffer = BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=A4)
                    story = []
                    
                    # Parse HTML content
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Get styles
                    styles = getSampleStyleSheet()
                    
                    # Add title
                    story.append(Paragraph(doc_name, styles['Heading1']))
                    story.append(Spacer(1, 12))
                    
                    # Add content (simplified)
                    text_content = soup.get_text()
                    lines = text_content.split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        if line:
                            story.append(Paragraph(line, styles['Normal']))
                            story.append(Spacer(1, 6))
                    
                    # Build PDF
                    doc.build(story)
                    
                    # Get PDF bytes
                    pdf_bytes = buffer.getvalue()
                    buffer.close()
                    
                    if len(pdf_bytes) > 500:  # Basic size check
                        pdf_files[f"{doc_name}.pdf"] = pdf_bytes
                        logger.info(f"Generated PDF: {doc_name}")
                
                except Exception as e:
                    logger.error(f"Error creating PDF for {doc_name}: {str(e)}")
        
        except ImportError as e:
            logger.error(f"Required libraries not available for PDF generation: {str(e)}")
        
        return pdf_files