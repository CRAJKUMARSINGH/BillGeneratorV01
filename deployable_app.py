"""
Deployable Streamlit Bill Generator Application
Optimized for cloud deployment with minimal dependencies
"""

import streamlit as st
import pandas as pd
from streamlit.components.v1 import html
import numpy as np
from datetime import datetime
import io
import base64
import tempfile
import os
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure page
st.set_page_config(
    page_title="Bill Generator - Cloud Deployment",
    page_icon="🏛️",
    layout="wide"
)

# Custom CSS for deployment
def load_custom_css():
    st.markdown("""
    <style>
    /* Main styling */
    .main > div {
        padding: 1rem;
    }
    
    /* Header */
    .header {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
    }
    
    .header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Cards */
    .card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #45a049 0%, #5a9c5a 100%);
    }
    
    /* File uploader */
    .uploadedFile {
        border: 2px dashed #4CAF50;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Status indicators */
    .success {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid #4CAF50;
    }
    
    .error {
        background-color: #ffebee;
        color: #c62828;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid #f44336;
    }
    
    .info {
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid #2196F3;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .header h1 {
            font-size: 1.5rem;
        }
        
        .card {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def show_header():
    """Display application header"""
    st.markdown("""
    <div class="header">
        <h1>🏛️ Bill Generator</h1>
        <p>Professional Infrastructure Billing System</p>
    </div>
    """, unsafe_allow_html=True)

class SimpleExcelProcessor:
    """Simplified Excel processor for the deployable app"""
    
    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
    
    def process_excel(self):
        """Process uploaded Excel file"""
        try:
            # Read Excel file
            excel_data = pd.ExcelFile(self.uploaded_file)
            
            print(f"Available sheets: {excel_data.sheet_names}")
            
            # Initialize data dictionary
            data = {}
            
            # Process Title sheet
            if 'Title' in excel_data.sheet_names:
                data['title_data'] = self._process_title_sheet(excel_data)
            else:
                data['title_data'] = {}
            
            # Process Work Order sheet
            if 'Work Order' in excel_data.sheet_names:
                data['work_order_data'] = self._process_work_order_sheet(excel_data)
            else:
                raise Exception("Required 'Work Order' sheet not found in Excel file")
            
            # Process Bill Quantity sheet
            if 'Bill Quantity' in excel_data.sheet_names:
                data['bill_quantity_data'] = self._process_bill_quantity_sheet(excel_data)
            else:
                data['bill_quantity_data'] = pd.DataFrame()
            
            # Process Extra Items sheet (optional)
            if 'Extra Items' in excel_data.sheet_names:
                data['extra_items_data'] = self._process_extra_items_sheet(excel_data)
            else:
                data['extra_items_data'] = pd.DataFrame()
            
            return data
            
        except Exception as e:
            raise Exception(f"Error processing Excel file: {str(e)}")
    
    def _process_title_sheet(self, excel_data):
        """Extract metadata from Title sheet"""
        try:
            title_df = pd.read_excel(excel_data, sheet_name='Title', header=None)
            
            # Convert to dictionary - assuming key-value pairs in adjacent columns
            title_data = {}
            for index, row in title_df.iterrows():
                if pd.notna(row[0]) and pd.notna(row[1]):
                    key = str(row[0]).strip()
                    val = str(row[1]).strip()
                    if key and val and key != 'nan' and val != 'nan':
                        title_data[key] = val
            
            return title_data
            
        except Exception as e:
            raise Exception(f"Error processing Title sheet: {str(e)}")
    
    def _process_work_order_sheet(self, excel_data):
        """Extract work order data"""
        try:
            work_order_df = pd.read_excel(excel_data, sheet_name='Work Order', header=0)
            
            # Standardize column names
            column_mapping = {
                'Item': 'Item No.',
                'Description': 'Description',
                'Unit': 'Unit',
                'Quantity': 'Quantity Since',
                'Rate': 'Rate',
                'Amount': 'Amount Since'
            }
            
            # Rename columns if they exist
            for old_col, new_col in column_mapping.items():
                if old_col in work_order_df.columns:
                    work_order_df = work_order_df.rename(columns={old_col: new_col})
            
            # Add missing columns with default values
            if 'Quantity Upto' not in work_order_df.columns:
                work_order_df['Quantity Upto'] = work_order_df.get('Quantity Since', 0)
            
            return work_order_df
            
        except Exception as e:
            raise Exception(f"Error processing Work Order sheet: {str(e)}")
    
    def _process_bill_quantity_sheet(self, excel_data):
        """Extract bill quantity data"""
        try:
            return pd.read_excel(excel_data, sheet_name='Bill Quantity', header=0)
        except Exception as e:
            raise Exception(f"Error processing Bill Quantity sheet: {str(e)}")
    
    def _process_extra_items_sheet(self, excel_data):
        """Extract extra items data"""
        try:
            return pd.read_excel(excel_data, sheet_name='Extra Items', header=0)
        except Exception as e:
            raise Exception(f"Error processing Extra Items sheet: {str(e)}")

class SimpleDocumentGenerator:
    """Simplified document generator for the deployable app"""
    
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
    
    def generate_all_documents(self):
        """Generate all documents"""
        documents = {}
        
        documents['First Page Summary'] = self._generate_first_page()
        documents['Bill Summary'] = self._generate_bill_summary()
        documents['Work Order Details'] = self._generate_work_order_details()
        
        if not self.extra_items_data.empty:
            documents['Extra Items'] = self._generate_extra_items()
        
        return documents
    
    def _generate_first_page(self):
        """Generate first page summary"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        # Normalize common title fields for display
        project_name = (
            self.title_data.get('Project Name')
            or self.title_data.get('Name of Work ;-')
            or self.title_data.get('Name of Work :')
            or self.title_data.get('Name of Work')
            or 'Project Name'
        )
        
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
            item_no = row.get('Item No.', '')
            description = row.get('Description', '')
            unit = row.get('Unit', '')
            quantity = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
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
        # Accept premium provided as 10 or "10%"
        raw_premium = self.title_data.get('TENDER PREMIUM %', 0)
        if isinstance(raw_premium, str) and raw_premium.strip().endswith('%'):
            try:
                premium_percent = self._safe_float(raw_premium.strip().rstrip('%'))
            except Exception:
                premium_percent = 0.0
        else:
            premium_percent = self._safe_float(raw_premium)
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
            quantity = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
            rate = self._safe_float(row.get('Rate', 0))
            total_amount += quantity * rate
        
        raw_premium = self.title_data.get('TENDER PREMIUM %', 0)
        if isinstance(raw_premium, str) and raw_premium.strip().endswith('%'):
            try:
                premium_percent = self._safe_float(raw_premium.strip().rstrip('%'))
            except Exception:
                premium_percent = 0.0
        else:
            premium_percent = self._safe_float(raw_premium)
        premium_amount = total_amount * (premium_percent / 100)
        gross_total = total_amount + premium_amount
        
        # Calculate deductions
        sd_amount = gross_total * 0.10  # Security Deposit 10%
        it_amount = gross_total * 0.02  # Income Tax 2%
        gst_amount = gross_total * 0.02  # GST 2%
        lc_amount = gross_total * 0.01  # Labour Cess 1%
        total_deductions = sd_amount + it_amount + gst_amount + lc_amount
        net_payable = gross_total - total_deductions
        
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
                .total-row {{ background-color: #e8f5e9; font-weight: bold; }}
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
                <tr><td colspan="2" style="background-color: #f5f5f5; font-weight: bold;">Deductions</td></tr>
                <tr><td>Security Deposit (10%)</td><td class="amount">-{sd_amount:.2f}</td></tr>
                <tr><td>Income Tax (2%)</td><td class="amount">-{it_amount:.2f}</td></tr>
                <tr><td>GST (2%)</td><td class="amount">-{gst_amount:.2f}</td></tr>
                <tr><td>Labour Cess (1%)</td><td class="amount">-{lc_amount:.2f}</td></tr>
                <tr><td><strong>Total Deductions</strong></td><td class="amount"><strong>-{total_deductions:.2f}</strong></td></tr>
                <tr class="total-row"><td><strong>Net Payable Amount</strong></td><td class="amount"><strong>{net_payable:.2f}</strong></td></tr>
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
                th {{ background-color: #f0f0f0; font-weight: bold; font-size: 9px; }}
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
            item_no = row.get('Item No.', '')
            description = row.get('Description', '')[:50] + ('...' if len(str(row.get('Description', ''))) > 50 else '')
            unit = row.get('Unit', '')
            quantity = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
            rate = self._safe_float(row.get('Rate', 0))
            amount = quantity * rate
            remarks = row.get('Remark', row.get('Remarks', ''))
            
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
            item_no = row.get('Item No.', '')
            description = row.get('Description', '')
            unit = row.get('Unit', '')
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
        """Create PDF documents from HTML"""
        pdf_files = {}
        
        try:
            # Check if required dependencies are available
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import A4
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.enums import TA_CENTER
                from bs4 import BeautifulSoup
                from io import BytesIO
            except ImportError as e:
                st.error(f"Missing required dependency for PDF generation: {str(e)}")
                st.info("Please install missing dependencies: pip install beautifulsoup4")
                return {}
            
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
                    
                    # Add title
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
                    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'table']):
                        if element.name in ['h1', 'h2', 'h3']:
                            text = element.get_text()
                            story.append(Paragraph(text, styles[f'Heading{element.name[1]}']))
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
                                    cell_text = cell.get_text().strip()
                                    # Limit cell content length for PDF
                                    if len(cell_text) > 50:
                                        cell_text = cell_text[:47] + "..."
                                    row_data.append(cell_text)
                                if row_data:
                                    data.append(row_data)
                            
                            if data:
                                table = Table(data)
                                table.setStyle(TableStyle([
                                    ('BACKGROUND', (0, 0), (-1, 0), '#f0f0f0'),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                    ('BACKGROUND', (0, 1), (-1, -1), '#ffffff'),
                                    ('GRID', (0, 0), (-1, -1), 1, '#000000')
                                ]))
                                story.append(table)
                                story.append(Spacer(1, 12))
                    
                    # Build PDF
                    doc.build(story)
                    
                    # Get PDF bytes
                    pdf_bytes = buffer.getvalue()
                    buffer.close()
                    
                    if len(pdf_bytes) > 1024:  # At least 1KB
                        pdf_files[f"{doc_name}.pdf"] = pdf_bytes
                        logger.info(f"Generated PDF: {doc_name} ({len(pdf_bytes)} bytes)")
                    else:
                        logger.warning(f"Generated PDF too small: {doc_name} ({len(pdf_bytes)} bytes)")
                    
                except Exception as e:
                    logger.error(f"Error creating PDF for {doc_name}: {str(e)}")
                    st.warning(f"Could not create PDF for {doc_name}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error in PDF creation process: {str(e)}")
            st.error(f"PDF generation failed: {str(e)}")
        
        return pdf_files

def process_excel_file(uploaded_file):
    """Process uploaded Excel file"""
    try:
        processor = SimpleExcelProcessor(uploaded_file)
        result = processor.process_excel()
        return result
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def generate_documents(data):
    """Generate documents from processed data"""
    try:
        generator = SimpleDocumentGenerator(data)
        documents = generator.generate_all_documents()
        return documents
    except Exception as e:
        st.error(f"Error generating documents: {str(e)}")
        return None

def create_pdf_documents(documents):
    """Create PDF documents from HTML"""
    try:
        generator = SimpleDocumentGenerator({})  # Empty data for PDF generation
        pdf_files = generator.create_pdf_documents(documents)
        return pdf_files
    except Exception as e:
        st.error(f"Error creating PDFs: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return None

def main():
    """Main application function"""
    # Load custom CSS
    load_custom_css()
    
    # Show header
    show_header()
    
    # Initialize session state
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'documents' not in st.session_state:
        st.session_state.documents = None
    if 'pdf_files' not in st.session_state:
        st.session_state.pdf_files = None
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload", "📄 Preview", "📥 Download"])
    
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Upload Excel File")
        st.info("Upload an Excel file with Title, Work Order, and Bill Quantity sheets")
        
        uploaded_file = st.file_uploader(
            "Choose Excel file", 
            type=['xlsx', 'xls'],
            help="Upload Excel file with required sheets"
        )
        
        if uploaded_file is not None:
            with st.spinner("Processing Excel file..."):
                result = process_excel_file(uploaded_file)
                if result:
                    st.session_state.processed_data = result
                    st.success("✅ File processed successfully!")
                    
                    # Show summary
                    st.markdown('<div class="info">', unsafe_allow_html=True)
                    st.markdown("**File Summary:**")
                    if 'title_data' in result:
                        st.write(f"Title items: {len(result['title_data'])}")
                    if 'work_order_data' in result and hasattr(result['work_order_data'], '__len__'):
                        st.write(f"Work order items: {len(result['work_order_data'])}")
                    if 'bill_quantity_data' in result and hasattr(result['bill_quantity_data'], '__len__'):
                        st.write(f"Bill quantity items: {len(result['bill_quantity_data'])}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Generate documents button
                    if st.button("📄 Generate Documents", type="primary"):
                        with st.spinner("Generating documents..."):
                            documents = generate_documents(result)
                            if documents:
                                st.session_state.documents = documents
                                st.success(f"✅ Generated {len(documents)} documents!")
                                
                                # Generate PDFs
                                with st.spinner("Creating PDF documents..."):
                                    pdf_files = create_pdf_documents(documents)
                                    if pdf_files:
                                        st.session_state.pdf_files = pdf_files
                                        st.success(f"✅ Created {len(pdf_files)} PDF files!")
                                    else:
                                        st.warning("⚠️ Could not create PDF files. You can still view HTML documents in the Preview tab.")
                            else:
                                st.error("❌ Failed to generate documents")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Document Preview")
        
        if st.session_state.documents:
            doc_names = list(st.session_state.documents.keys())
            selected_doc = st.selectbox("Select document to preview", doc_names)
            
            if selected_doc:
                doc_content = st.session_state.documents[selected_doc]
                st.markdown("### Preview")
                html(doc_content, height=600, scrolling=True)
        else:
            st.info("📤 Please upload a file and generate documents first")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Download Documents")
        
        if st.session_state.pdf_files:
            st.success(f"✅ {len(st.session_state.pdf_files)} documents ready for download")
            
            # Show individual downloads
            st.markdown("### PDF Documents")
            cols = st.columns(2)
            col_idx = 0
            
            for filename, pdf_bytes in st.session_state.pdf_files.items():
                with cols[col_idx % 2]:
                    st.download_button(
                        label=f"📥 {filename}",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        key=f"download_{filename}"
                    )
                col_idx += 1
            
        elif st.session_state.documents:
            st.info("HTML documents generated but PDF creation failed. You can view documents in the Preview tab.")
            
            # Offer HTML downloads as fallback
            st.markdown("### HTML Documents (Fallback)")
            for doc_name, html_content in st.session_state.documents.items():
                st.download_button(
                    label=f"📄 {doc_name}.html",
                    data=html_content,
                    file_name=f"{doc_name}.html",
                    mime="text/html",
                    key=f"download_html_{doc_name}"
                )
        else:
            st.info("📤 Please upload a file and generate documents first")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.caption("🏛️ Bill Generator - Professional Infrastructure Billing System")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()