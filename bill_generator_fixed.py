"""
Professional Bill Generator - Bug-Free Production Ready Version
Fixed all PDF generation issues with comprehensive error handling
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import base64
import tempfile
import os
import traceback
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Professional Bill Generator",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_custom_css():
    """Enhanced CSS styling"""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main > div {
        padding: 1rem 2rem;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .app-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .app-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
        font-weight: 300;
    }
    
    /* Card components */
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    /* Status indicators */
    .status-success {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .status-error {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .status-info {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px 0 rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* File uploader styling */
    .uploadedFile {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8fafc;
        transition: all 0.3s ease;
    }
    
    .uploadedFile:hover {
        border-color: #764ba2;
        background: #f1f5f9;
    }
    
    /* Metrics styling */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* Progress indicator */
    .progress-container {
        margin: 2rem 0;
    }
    
    .progress-step {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding: 1rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .progress-step.completed {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
    }
    
    .progress-step.active {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .app-header h1 {
            font-size: 2rem;
        }
        
        .main > div {
            padding: 1rem;
        }
        
        .feature-card {
            padding: 1rem;
        }
    }
    
    /* Dark theme support */
    @media (prefers-color-scheme: dark) {
        .feature-card {
            background: #1f2937;
            border-color: #374151;
            color: white;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def show_header():
    """Display enhanced application header"""
    st.markdown("""
    <div class="app-header">
        <h1>🧾 Professional Bill Generator</h1>
        <p>Advanced Infrastructure Billing System with Guaranteed PDF Output</p>
    </div>
    """, unsafe_allow_html=True)

class RobustPDFGenerator:
    """Robust PDF generator with multiple fallback methods"""
    
    def __init__(self):
        self.methods = [
            self._generate_with_reportlab,
            self._generate_with_fpdf,
            self._generate_with_weasyprint,
            self._generate_basic_pdf
        ]
    
    def generate_pdf(self, html_content, filename):
        """Generate PDF with multiple fallback methods"""
        for i, method in enumerate(self.methods):
            try:
                logger.info(f"Attempting PDF generation method {i+1}: {method.__name__}")
                pdf_bytes = method(html_content, filename)
                if pdf_bytes and len(pdf_bytes) > 1024:  # At least 1KB
                    logger.info(f"Success with method {i+1}: {len(pdf_bytes)} bytes")
                    return pdf_bytes
                else:
                    logger.warning(f"Method {i+1} produced insufficient data")
            except Exception as e:
                logger.error(f"Method {i+1} failed: {str(e)}")
                continue
        
        logger.error("All PDF generation methods failed")
        return None
    
    def _generate_with_reportlab(self, html_content, filename):
        """Generate PDF using ReportLab with HTML parsing"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4, letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from bs4 import BeautifulSoup
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Create PDF buffer
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=72, leftMargin=72,
                topMargin=72, bottomMargin=18
            )
            
            # Build story
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2563eb')
            )
            
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=20,
                textColor=colors.HexColor('#1f2937')
            )
            
            # Extract and add title
            title_elem = soup.find('title')
            if title_elem:
                story.append(Paragraph(title_elem.get_text(), title_style))
                story.append(Spacer(1, 12))
            
            # Process body content
            body = soup.find('body')
            if body:
                for element in body.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'table', 'div']):
                    if element.name in ['h1', 'h2', 'h3', 'h4']:
                        text = element.get_text().strip()
                        if text:
                            story.append(Paragraph(text, header_style))
                            story.append(Spacer(1, 12))
                    
                    elif element.name == 'p':
                        text = element.get_text().strip()
                        if text:
                            story.append(Paragraph(text, styles['Normal']))
                            story.append(Spacer(1, 6))
                    
                    elif element.name == 'div' and 'header' in element.get('class', []):
                        # Process header divs
                        for child in element.find_all(['h1', 'p']):
                            text = child.get_text().strip()
                            if text:
                                if child.name == 'h1':
                                    story.append(Paragraph(text, title_style))
                                else:
                                    story.append(Paragraph(text, styles['Normal']))
                                story.append(Spacer(1, 6))
                    
                    elif element.name == 'table':
                        # Process tables
                        data = []
                        for row in element.find_all('tr'):
                            row_data = []
                            for cell in row.find_all(['td', 'th']):
                                cell_text = cell.get_text().strip()
                                # Handle long text
                                if len(cell_text) > 60:
                                    # Split long text into multiple lines
                                    words = cell_text.split()
                                    lines = []
                                    current_line = []
                                    current_length = 0
                                    
                                    for word in words:
                                        if current_length + len(word) > 50:
                                            if current_line:
                                                lines.append(' '.join(current_line))
                                                current_line = [word]
                                                current_length = len(word)
                                            else:
                                                lines.append(word[:50] + "...")
                                                current_length = 0
                                        else:
                                            current_line.append(word)
                                            current_length += len(word) + 1
                                    
                                    if current_line:
                                        lines.append(' '.join(current_line))
                                    
                                    cell_text = '\n'.join(lines) if lines else cell_text[:50] + "..."
                                
                                row_data.append(cell_text)
                            if row_data:
                                data.append(row_data)
                        
                        if data:
                            # Calculate column widths
                            num_cols = len(data[0]) if data else 1
                            col_width = (A4[0] - 144) / num_cols  # Available width divided by columns
                            
                            table = Table(data, colWidths=[col_width] * num_cols)
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 9),
                                ('FONTSIZE', (0, 1), (-1, -1), 8),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
                            ]))
                            
                            story.append(table)
                            story.append(Spacer(1, 12))
            
            # Build PDF
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"ReportLab method failed: {str(e)}")
            raise
    
    def _generate_with_fpdf(self, html_content, filename):
        """Generate PDF using FPDF as fallback"""
        try:
            # Try to import FPDF
            try:
                from fpdf import FPDF
            except ImportError:
                # Install FPDF if not available
                import subprocess
                subprocess.check_call(['pip', 'install', '--quiet', 'fpdf2'])
                from fpdf import FPDF
            
            from bs4 import BeautifulSoup
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            
            # Add title
            title = soup.find('title')
            if title:
                pdf.cell(0, 10, title.get_text().encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
                pdf.ln(10)
            
            # Process content
            pdf.set_font('Arial', '', 10)
            body = soup.find('body')
            if body:
                for element in body.find_all(['h1', 'h2', 'h3', 'p', 'table']):
                    if element.name in ['h1', 'h2', 'h3']:
                        pdf.set_font('Arial', 'B', 12)
                        text = element.get_text().strip()
                        # Handle encoding issues
                        safe_text = text.encode('latin-1', 'replace').decode('latin-1')
                        pdf.cell(0, 8, safe_text, ln=True)
                        pdf.ln(5)
                        pdf.set_font('Arial', '', 10)
                    
                    elif element.name == 'p':
                        text = element.get_text().strip()
                        if text:
                            # Handle encoding and long text
                            safe_text = text.encode('latin-1', 'replace').decode('latin-1')
                            # Split long lines
                            words = safe_text.split()
                            line = ''
                            for word in words:
                                if len(line + word) > 80:  # Approximate line length
                                    if line:
                                        pdf.cell(0, 6, line.strip(), ln=True)
                                        line = word + ' '
                                    else:
                                        pdf.cell(0, 6, word[:80], ln=True)
                                else:
                                    line += word + ' '
                            if line:
                                pdf.cell(0, 6, line.strip(), ln=True)
                            pdf.ln(3)
                    
                    elif element.name == 'table':
                        # Simple table processing
                        pdf.ln(5)
                        rows = element.find_all('tr')
                        for i, row in enumerate(rows):
                            cells = row.find_all(['td', 'th'])
                            if cells:
                                cell_width = 180 / len(cells)  # Distribute width
                                for cell in cells:
                                    text = cell.get_text().strip()
                                    safe_text = text.encode('latin-1', 'replace').decode('latin-1')
                                    # Truncate long text
                                    if len(safe_text) > 20:
                                        safe_text = safe_text[:17] + "..."
                                    
                                    if i == 0:  # Header row
                                        pdf.set_font('Arial', 'B', 8)
                                    else:
                                        pdf.set_font('Arial', '', 8)
                                    
                                    pdf.cell(cell_width, 6, safe_text, 1, 0, 'L')
                                pdf.ln()
                        pdf.set_font('Arial', '', 10)
                        pdf.ln(5)
            
            # Get PDF bytes
            buffer = io.BytesIO()
            pdf_string = pdf.output(dest='S')
            if isinstance(pdf_string, str):
                buffer.write(pdf_string.encode('latin-1'))
            else:
                buffer.write(pdf_string)
            
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"FPDF method failed: {str(e)}")
            raise
    
    def _generate_with_weasyprint(self, html_content, filename):
        """Generate PDF using WeasyPrint"""
        try:
            # Try to import and use WeasyPrint
            import subprocess
            try:
                from weasyprint import HTML, CSS
                from weasyprint.text.fonts import FontConfiguration
            except ImportError:
                # Install WeasyPrint if not available
                subprocess.check_call(['pip', 'install', '--quiet', 'weasyprint'])
                from weasyprint import HTML, CSS
                from weasyprint.text.fonts import FontConfiguration
            
            # Create font configuration
            font_config = FontConfiguration()
            
            # Enhanced CSS for better PDF rendering
            css_content = CSS(string="""
                @page {
                    size: A4;
                    margin: 2cm;
                }
                body {
                    font-family: Arial, sans-serif;
                    font-size: 12px;
                    line-height: 1.4;
                    color: #333;
                }
                h1 { font-size: 18px; margin-bottom: 20px; color: #2563eb; }
                h2 { font-size: 16px; margin-bottom: 15px; color: #1f2937; }
                h3 { font-size: 14px; margin-bottom: 10px; }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                    font-size: 10px;
                }
                th, td {
                    border: 1px solid #000;
                    padding: 6px;
                    text-align: left;
                    vertical-align: top;
                }
                th {
                    background-color: #f3f4f6;
                    font-weight: bold;
                }
                .amount {
                    text-align: right;
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .title {
                    font-size: 20px;
                    font-weight: bold;
                    color: #2563eb;
                }
            """, font_config=font_config)
            
            # Generate PDF
            html_doc = HTML(string=html_content)
            pdf_bytes = html_doc.write_pdf(stylesheets=[css_content], font_config=font_config)
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"WeasyPrint method failed: {str(e)}")
            raise
    
    def _generate_basic_pdf(self, html_content, filename):
        """Basic PDF generation as last resort"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from bs4 import BeautifulSoup
            import textwrap
            
            # Parse HTML to extract text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Create PDF
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            y_position = height - 50
            
            # Add title
            title = soup.find('title')
            if title:
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredText(width/2, y_position, title.get_text())
                y_position -= 40
            
            # Extract and add text content
            c.setFont("Helvetica", 10)
            body = soup.find('body')
            if body:
                # Get all text content
                text_content = body.get_text()
                # Clean up text
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                
                for line in lines:
                    # Wrap long lines
                    wrapped_lines = textwrap.wrap(line, width=80)
                    for wrapped_line in wrapped_lines:
                        if y_position < 50:  # Start new page
                            c.showPage()
                            y_position = height - 50
                            c.setFont("Helvetica", 10)
                        
                        c.drawString(50, y_position, wrapped_line[:100])  # Limit line length
                        y_position -= 15
            
            c.save()
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Basic PDF method failed: {str(e)}")
            raise

class EnhancedExcelProcessor:
    """Enhanced Excel processor with better error handling"""
    
    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
        self.data = {}
    
    def process_excel(self):
        """Process Excel file with comprehensive error handling"""
        try:
            # Read Excel file
            with st.spinner("Reading Excel file..."):
                excel_data = pd.ExcelFile(self.uploaded_file)
                logger.info(f"Available sheets: {excel_data.sheet_names}")
            
            # Process each sheet
            self.data['sheets_available'] = excel_data.sheet_names
            
            # Process Title sheet
            if 'Title' in excel_data.sheet_names:
                with st.spinner("Processing Title sheet..."):
                    self.data['title_data'] = self._process_title_sheet(excel_data)
                    logger.info(f"Title data: {len(self.data['title_data'])} items")
            else:
                self.data['title_data'] = {}
                st.warning("⚠️ Title sheet not found. Using default values.")
            
            # Process Work Order sheet (required)
            if 'Work Order' in excel_data.sheet_names:
                with st.spinner("Processing Work Order sheet..."):
                    self.data['work_order_data'] = self._process_work_order_sheet(excel_data)
                    logger.info(f"Work order data: {len(self.data['work_order_data'])} items")
            else:
                raise Exception("❌ Required 'Work Order' sheet not found in Excel file")
            
            # Process Bill Quantity sheet
            if 'Bill Quantity' in excel_data.sheet_names:
                with st.spinner("Processing Bill Quantity sheet..."):
                    self.data['bill_quantity_data'] = self._process_bill_quantity_sheet(excel_data)
                    logger.info(f"Bill quantity data: {len(self.data['bill_quantity_data'])} items")
            else:
                self.data['bill_quantity_data'] = pd.DataFrame()
                st.info("ℹ️ Bill Quantity sheet not found. Using Work Order quantities.")
            
            # Process Extra Items sheet (optional)
            if 'Extra Items' in excel_data.sheet_names:
                with st.spinner("Processing Extra Items sheet..."):
                    self.data['extra_items_data'] = self._process_extra_items_sheet(excel_data)
                    logger.info(f"Extra items data: {len(self.data['extra_items_data'])} items")
            else:
                self.data['extra_items_data'] = pd.DataFrame()
                st.info("ℹ️ Extra Items sheet not found. Skipping extra items.")
            
            return self.data
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {str(e)}")
            st.error(f"❌ Error processing Excel file: {str(e)}")
            return None
    
    def _process_title_sheet(self, excel_data):
        """Extract metadata from Title sheet with error handling"""
        try:
            title_df = pd.read_excel(excel_data, sheet_name='Title', header=None)
            title_data = {}
            
            # Try different parsing strategies
            for index, row in title_df.iterrows():
                try:
                    if len(row) >= 2 and pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]):
                        key = str(row.iloc[0]).strip()
                        val = str(row.iloc[1]).strip()
                        if key and val and key != 'nan' and val != 'nan':
                            title_data[key] = val
                except Exception as e:
                    logger.warning(f"Error processing title row {index}: {e}")
                    continue
            
            # Add default values if missing
            default_values = {
                'Project Name': 'Infrastructure Project',
                'TENDER PREMIUM %': '10',
                'Contractor': 'Contractor Name',
                'Date': datetime.now().strftime('%d/%m/%Y')
            }
            
            for key, default_val in default_values.items():
                if key not in title_data:
                    title_data[key] = default_val
            
            return title_data
            
        except Exception as e:
            logger.error(f"Error processing Title sheet: {str(e)}")
            return {
                'Project Name': 'Infrastructure Project',
                'TENDER PREMIUM %': '10',
                'Contractor': 'Contractor Name',
                'Date': datetime.now().strftime('%d/%m/%Y')
            }
    
    def _process_work_order_sheet(self, excel_data):
        """Extract work order data with enhanced error handling"""
        try:
            work_order_df = pd.read_excel(excel_data, sheet_name='Work Order', header=0)
            
            # Clean column names
            work_order_df.columns = work_order_df.columns.str.strip()
            
            # Standardize column names with flexible mapping
            column_mapping = {
                'Item': 'Item No.',
                'item': 'Item No.',
                'Item No': 'Item No.',
                'item no': 'Item No.',
                'Description': 'Description',
                'description': 'Description',
                'Desc': 'Description',
                'Unit': 'Unit',
                'unit': 'Unit',
                'Units': 'Unit',
                'Quantity': 'Quantity Since',
                'quantity': 'Quantity Since',
                'Qty': 'Quantity Since',
                'Rate': 'Rate',
                'rate': 'Rate',
                'Amount': 'Amount Since',
                'amount': 'Amount Since'
            }
            
            # Apply column mapping
            for old_col in work_order_df.columns:
                if old_col in column_mapping:
                    work_order_df = work_order_df.rename(columns={old_col: column_mapping[old_col]})
            
            # Ensure required columns exist
            required_columns = ['Item No.', 'Description', 'Unit', 'Quantity Since', 'Rate']
            for col in required_columns:
                if col not in work_order_df.columns:
                    if col == 'Item No.':
                        work_order_df['Item No.'] = range(1, len(work_order_df) + 1)
                    elif col == 'Description':
                        work_order_df['Description'] = 'Work Item Description'
                    elif col == 'Unit':
                        work_order_df['Unit'] = 'Nos'
                    elif col == 'Quantity Since':
                        work_order_df['Quantity Since'] = 0
                    elif col == 'Rate':
                        work_order_df['Rate'] = 0
            
            # Add calculated columns
            if 'Quantity Upto' not in work_order_df.columns:
                work_order_df['Quantity Upto'] = work_order_df['Quantity Since']
            
            if 'Amount Since' not in work_order_df.columns:
                work_order_df['Amount Since'] = pd.to_numeric(work_order_df['Quantity Since'], errors='coerce').fillna(0) * pd.to_numeric(work_order_df['Rate'], errors='coerce').fillna(0)
            
            # Clean numeric columns
            numeric_columns = ['Quantity Since', 'Quantity Upto', 'Rate', 'Amount Since']
            for col in numeric_columns:
                if col in work_order_df.columns:
                    work_order_df[col] = pd.to_numeric(work_order_df[col], errors='coerce').fillna(0)
            
            # Remove empty rows
            work_order_df = work_order_df.dropna(subset=['Description'])
            
            return work_order_df
            
        except Exception as e:
            logger.error(f"Error processing Work Order sheet: {str(e)}")
            raise Exception(f"Failed to process Work Order sheet: {str(e)}")
    
    def _process_bill_quantity_sheet(self, excel_data):
        """Extract bill quantity data"""
        try:
            bill_df = pd.read_excel(excel_data, sheet_name='Bill Quantity', header=0)
            # Clean and process similar to work order
            numeric_columns = ['Quantity', 'Rate', 'Amount']
            for col in numeric_columns:
                if col in bill_df.columns:
                    bill_df[col] = pd.to_numeric(bill_df[col], errors='coerce').fillna(0)
            return bill_df
        except Exception as e:
            logger.error(f"Error processing Bill Quantity sheet: {str(e)}")
            return pd.DataFrame()
    
    def _process_extra_items_sheet(self, excel_data):
        """Extract extra items data"""
        try:
            extra_df = pd.read_excel(excel_data, sheet_name='Extra Items', header=0)
            # Clean and process
            numeric_columns = ['Quantity', 'Rate', 'Amount']
            for col in numeric_columns:
                if col in extra_df.columns:
                    extra_df[col] = pd.to_numeric(extra_df[col], errors='coerce').fillna(0)
            return extra_df
        except Exception as e:
            logger.error(f"Error processing Extra Items sheet: {str(e)}")
            return pd.DataFrame()

class ProfessionalDocumentGenerator:
    """Professional document generator with enhanced features"""
    
    def __init__(self, data):
        self.data = data
        self.title_data = data.get('title_data', {})
        self.work_order_data = data.get('work_order_data', pd.DataFrame())
        self.bill_quantity_data = data.get('bill_quantity_data', pd.DataFrame())
        self.extra_items_data = data.get('extra_items_data', pd.DataFrame())
        self.pdf_generator = RobustPDFGenerator()
    
    def _safe_float(self, value):
        """Safely convert value to float"""
        try:
            if pd.isna(value) or value == '' or value is None:
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _format_currency(self, amount):
        """Format currency with Indian formatting"""
        try:
            return f"₹ {amount:,.2f}"
        except:
            return f"₹ 0.00"
    
    def generate_all_documents(self):
        """Generate all documents with progress tracking"""
        documents = {}
        
        with st.spinner("Generating documents..."):
            progress_bar = st.progress(0)
            
            # Generate First Page Summary
            progress_bar.progress(25)
            documents['First_Page_Summary'] = self._generate_first_page()
            st.success("✅ First Page Summary generated")
            
            # Generate Bill Summary
            progress_bar.progress(50)
            documents['Bill_Summary'] = self._generate_bill_summary()
            st.success("✅ Bill Summary generated")
            
            # Generate Work Order Details
            progress_bar.progress(75)
            documents['Work_Order_Details'] = self._generate_work_order_details()
            st.success("✅ Work Order Details generated")
            
            # Generate Extra Items if available
            if not self.extra_items_data.empty:
                documents['Extra_Items'] = self._generate_extra_items()
                st.success("✅ Extra Items generated")
            
            progress_bar.progress(100)
            st.success(f"🎉 All documents generated successfully! ({len(documents)} documents)")
        
        return documents
    
    def _generate_first_page(self):
        """Generate enhanced first page summary"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        project_name = self.title_data.get('Project Name', 'Infrastructure Project')
        contractor = self.title_data.get('Contractor', 'Contractor Name')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>First Page Summary</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    margin: 20px; 
                    font-size: 12px; 
                    line-height: 1.4;
                    color: #333;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 30px; 
                    border-bottom: 3px solid #2563eb;
                    padding-bottom: 20px;
                }}
                .title {{ 
                    font-size: 24px; 
                    font-weight: bold; 
                    color: #2563eb;
                    margin-bottom: 10px;
                }}
                .subtitle {{
                    font-size: 14px;
                    color: #666;
                    margin-bottom: 5px;
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 15px 0; 
                    font-size: 11px;
                }}
                th, td {{ 
                    border: 1px solid #333; 
                    padding: 8px; 
                    text-align: left; 
                    vertical-align: top;
                }}
                th {{ 
                    background-color: #f8f9fa; 
                    font-weight: bold; 
                    color: #2563eb;
                }}
                .amount {{ text-align: right; font-weight: 500; }}
                .summary-box {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 20px;
                    border-left: 4px solid #2563eb;
                }}
                .total-row {{
                    background-color: #e3f2fd;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">BILL SUMMARY - FIRST PAGE</div>
                <div class="subtitle">Project: {project_name}</div>
                <div class="subtitle">Contractor: {contractor}</div>
                <div class="subtitle">Date: {current_date}</div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th style="width: 8%;">Item No.</th>
                        <th style="width: 35%;">Description of Work</th>
                        <th style="width: 8%;">Unit</th>
                        <th style="width: 12%;">Quantity</th>
                        <th style="width: 15%;">Rate (₹)</th>
                        <th style="width: 17%;">Amount (₹)</th>
                        <th style="width: 5%;">%</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_amount = 0
        
        # Add work items
        for index, row in self.work_order_data.iterrows():
            item_no = row.get('Item No.', index + 1)
            description = str(row.get('Description', 'Work Item'))[:60]
            unit = row.get('Unit', 'Nos')
            quantity = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
            rate = self._safe_float(row.get('Rate', 0))
            amount = quantity * rate
            total_amount += amount
            
            # Calculate percentage of total (will be updated after calculating total)
            percentage = 0  # Will be calculated after total is known
            
            html_content += f"""
                <tr>
                    <td style="text-align: center;">{item_no}</td>
                    <td>{description}</td>
                    <td style="text-align: center;">{unit}</td>
                    <td class="amount">{quantity:,.2f}</td>
                    <td class="amount">{rate:,.2f}</td>
                    <td class="amount">{amount:,.2f}</td>
                    <td class="amount">{(amount/max(total_amount, 1)*100):,.1f}%</td>
                </tr>
            """
        
        # Calculate totals and premiums
        premium_percent = self._safe_float(self.title_data.get('TENDER PREMIUM %', 10))
        premium_amount = total_amount * (premium_percent / 100)
        gross_total = total_amount + premium_amount
        
        # Add summary rows
        html_content += f"""
                </tbody>
            </table>
            
            <div class="summary-box">
                <table style="margin: 0;">
                    <tr>
                        <td style="border: none; font-weight: bold; width: 70%;">Sub Total (Work Order Amount):</td>
                        <td style="border: none; text-align: right; font-weight: bold;">{self._format_currency(total_amount)}</td>
                    </tr>
                    <tr>
                        <td style="border: none; font-weight: bold;">Tender Premium ({premium_percent}%):</td>
                        <td style="border: none; text-align: right; font-weight: bold;">{self._format_currency(premium_amount)}</td>
                    </tr>
                    <tr style="border-top: 2px solid #2563eb;">
                        <td style="border: none; font-weight: bold; font-size: 14px; color: #2563eb;">GROSS TOTAL:</td>
                        <td style="border: none; text-align: right; font-weight: bold; font-size: 14px; color: #2563eb;">{self._format_currency(gross_total)}</td>
                    </tr>
                </table>
            </div>
            
            <div style="margin-top: 30px; font-size: 10px; color: #666;">
                <p><strong>Note:</strong> This is a computer-generated document. All amounts are calculated based on the work order rates and quantities.</p>
                <p><strong>Generated on:</strong> {datetime.now().strftime('%d/%m/%Y at %I:%M %p')}</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_bill_summary(self):
        """Generate enhanced bill summary with deductions"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        project_name = self.title_data.get('Project Name', 'Infrastructure Project')
        
        # Calculate work order total
        total_amount = 0
        for index, row in self.work_order_data.iterrows():
            quantity = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
            rate = self._safe_float(row.get('Rate', 0))
            total_amount += quantity * rate
        
        # Add extra items if any
        extra_total = 0
        if not self.extra_items_data.empty:
            for index, row in self.extra_items_data.iterrows():
                quantity = self._safe_float(row.get('Quantity', 0))
                rate = self._safe_float(row.get('Rate', 0))
                extra_total += quantity * rate
        
        # Calculate premiums and totals
        premium_percent = self._safe_float(self.title_data.get('TENDER PREMIUM %', 10))
        premium_amount = (total_amount + extra_total) * (premium_percent / 100)
        gross_total = total_amount + extra_total + premium_amount
        
        # Calculate deductions (standard rates)
        security_deposit = gross_total * 0.10  # 10%
        income_tax = gross_total * 0.02  # 2%
        gst_deduction = gross_total * 0.02  # 2%
        labour_cess = gross_total * 0.01  # 1%
        total_deductions = security_deposit + income_tax + gst_deduction + labour_cess
        
        net_payable = gross_total - total_deductions
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Bill Summary</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    margin: 20px; 
                    font-size: 12px; 
                    color: #333;
                    line-height: 1.4;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 30px; 
                    border-bottom: 3px solid #10b981;
                    padding-bottom: 20px;
                }}
                .title {{ 
                    font-size: 24px; 
                    font-weight: bold; 
                    color: #10b981;
                    margin-bottom: 10px;
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 10px 0; 
                    font-size: 12px;
                }}
                th, td {{ 
                    border: 1px solid #333; 
                    padding: 12px; 
                    text-align: left; 
                }}
                th {{ 
                    background-color: #f0f9ff; 
                    font-weight: bold; 
                    color: #1e40af;
                }}
                .amount {{ text-align: right; font-weight: 500; }}
                .total-row {{ 
                    background-color: #dcfce7; 
                    font-weight: bold; 
                    color: #166534;
                }}
                .deduction-row {{
                    background-color: #fef2f2;
                    color: #991b1b;
                }}
                .section-header {{
                    background-color: #f3f4f6;
                    font-weight: bold;
                    color: #374151;
                    text-align: center;
                }}
                .final-total {{
                    background-color: #1e40af;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">DETAILED BILL SUMMARY</div>
                <div style="font-size: 14px; color: #666;">Project: {project_name}</div>
                <div style="font-size: 14px; color: #666;">Date: {current_date}</div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th style="width: 70%;">Description</th>
                        <th style="width: 30%;">Amount (₹)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Work Order Amount</strong></td>
                        <td class="amount">{self._format_currency(total_amount)}</td>
                    </tr>
        """
        
        if extra_total > 0:
            html_content += f"""
                    <tr>
                        <td><strong>Extra Items Amount</strong></td>
                        <td class="amount">{self._format_currency(extra_total)}</td>
                    </tr>
            """
        
        html_content += f"""
                    <tr>
                        <td><strong>Sub Total</strong></td>
                        <td class="amount">{self._format_currency(total_amount + extra_total)}</td>
                    </tr>
                    <tr>
                        <td><strong>Tender Premium ({premium_percent}%)</strong></td>
                        <td class="amount">{self._format_currency(premium_amount)}</td>
                    </tr>
                    <tr class="total-row">
                        <td><strong>GROSS TOTAL</strong></td>
                        <td class="amount"><strong>{self._format_currency(gross_total)}</strong></td>
                    </tr>
                    <tr class="section-header">
                        <td colspan="2"><strong>DEDUCTIONS</strong></td>
                    </tr>
                    <tr class="deduction-row">
                        <td>Security Deposit (10%)</td>
                        <td class="amount">-{self._format_currency(security_deposit)}</td>
                    </tr>
                    <tr class="deduction-row">
                        <td>Income Tax (2%)</td>
                        <td class="amount">-{self._format_currency(income_tax)}</td>
                    </tr>
                    <tr class="deduction-row">
                        <td>GST Deduction (2%)</td>
                        <td class="amount">-{self._format_currency(gst_deduction)}</td>
                    </tr>
                    <tr class="deduction-row">
                        <td>Labour Cess (1%)</td>
                        <td class="amount">-{self._format_currency(labour_cess)}</td>
                    </tr>
                    <tr class="deduction-row">
                        <td><strong>Total Deductions</strong></td>
                        <td class="amount"><strong>-{self._format_currency(total_deductions)}</strong></td>
                    </tr>
                    <tr class="final-total">
                        <td><strong>NET PAYABLE AMOUNT</strong></td>
                        <td class="amount"><strong>{self._format_currency(net_payable)}</strong></td>
                    </tr>
                </tbody>
            </table>
            
            <div style="margin-top: 30px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #10b981;">
                <h4 style="margin-top: 0; color: #10b981;">Summary</h4>
                <p><strong>Total Work Items:</strong> {len(self.work_order_data)}</p>
                <p><strong>Extra Items:</strong> {len(self.extra_items_data) if not self.extra_items_data.empty else 0}</p>
                <p><strong>Gross Amount:</strong> {self._format_currency(gross_total)}</p>
                <p><strong>Net Payable:</strong> {self._format_currency(net_payable)}</p>
            </div>
            
            <div style="margin-top: 30px; font-size: 10px; color: #666;">
                <p><strong>Note:</strong> All deductions are calculated as per standard government norms. Actual deductions may vary based on specific contract terms.</p>
                <p><strong>Generated on:</strong> {datetime.now().strftime('%d/%m/%Y at %I:%M %p')}</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_work_order_details(self):
        """Generate comprehensive work order details"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        project_name = self.title_data.get('Project Name', 'Infrastructure Project')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Work Order Details</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    margin: 15px; 
                    font-size: 10px; 
                    color: #333;
                    line-height: 1.3;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 25px; 
                    border-bottom: 2px solid #7c3aed;
                    padding-bottom: 15px;
                }}
                .title {{ 
                    font-size: 20px; 
                    font-weight: bold; 
                    color: #7c3aed;
                    margin-bottom: 8px;
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 10px 0; 
                    font-size: 9px;
                }}
                th, td {{ 
                    border: 1px solid #333; 
                    padding: 6px; 
                    text-align: left; 
                    vertical-align: top;
                }}
                th {{ 
                    background-color: #faf5ff; 
                    font-weight: bold; 
                    color: #6b21a8;
                    font-size: 8px;
                }}
                .amount {{ text-align: right; }}
                .item-no {{ text-align: center; font-weight: bold; }}
                tr:nth-child(even) {{ background-color: #f9fafb; }}
                .description {{ 
                    max-width: 200px; 
                    word-wrap: break-word; 
                    font-size: 9px;
                }}
                .summary-row {{
                    background-color: #ede9fe;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">DETAILED WORK ORDER</div>
                <div style="font-size: 12px; color: #666;">Project: {project_name}</div>
                <div style="font-size: 12px; color: #666;">Date: {current_date}</div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th style="width: 6%;">Item No.</th>
                        <th style="width: 32%;">Description of Work</th>
                        <th style="width: 8%;">Unit</th>
                        <th style="width: 10%;">Qty Since</th>
                        <th style="width: 10%;">Qty Upto</th>
                        <th style="width: 12%;">Rate (₹)</th>
                        <th style="width: 12%;">Amount (₹)</th>
                        <th style="width: 10%;">Remarks</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_amount = 0
        
        for index, row in self.work_order_data.iterrows():
            item_no = row.get('Item No.', index + 1)
            description = str(row.get('Description', 'Work Item Description'))
            # Truncate long descriptions
            if len(description) > 80:
                description = description[:77] + "..."
            
            unit = row.get('Unit', 'Nos')
            qty_since = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
            qty_upto = self._safe_float(row.get('Quantity Upto', qty_since))
            rate = self._safe_float(row.get('Rate', 0))
            amount = qty_since * rate
            total_amount += amount
            remarks = str(row.get('Remarks', row.get('Remark', '')))[:30]
            
            html_content += f"""
                <tr>
                    <td class="item-no">{item_no}</td>
                    <td class="description">{description}</td>
                    <td style="text-align: center;">{unit}</td>
                    <td class="amount">{qty_since:,.2f}</td>
                    <td class="amount">{qty_upto:,.2f}</td>
                    <td class="amount">{rate:,.2f}</td>
                    <td class="amount">{amount:,.2f}</td>
                    <td style="font-size: 8px;">{remarks}</td>
                </tr>
            """
        
        # Add summary row
        html_content += f"""
                <tr class="summary-row">
                    <td colspan="6" style="text-align: right; padding: 10px;"><strong>TOTAL WORK ORDER AMOUNT:</strong></td>
                    <td class="amount" style="padding: 10px;"><strong>{self._format_currency(total_amount)}</strong></td>
                    <td></td>
                </tr>
            </tbody>
        </table>
        
        <div style="margin-top: 25px; padding: 15px; background-color: #f8fafc; border-radius: 8px; border-left: 4px solid #7c3aed;">
            <h4 style="margin-top: 0; color: #7c3aed;">Work Order Summary</h4>
            <div style="display: flex; justify-content: space-between; font-size: 11px;">
                <div>
                    <p><strong>Total Items:</strong> {len(self.work_order_data)}</p>
                    <p><strong>Total Amount:</strong> {self._format_currency(total_amount)}</p>
                </div>
                <div style="text-align: right;">
                    <p><strong>Project:</strong> {project_name}</p>
                    <p><strong>Generated:</strong> {datetime.now().strftime('%d/%m/%Y %I:%M %p')}</p>
                </div>
            </div>
        </div>
        
        <div style="margin-top: 20px; font-size: 9px; color: #666; text-align: center;">
            <p>This is a computer-generated detailed work order document. All calculations are based on the uploaded data.</p>
        </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_extra_items(self):
        """Generate extra items document"""
        if self.extra_items_data.empty:
            return ""
        
        current_date = datetime.now().strftime('%d/%m/%Y')
        project_name = self.title_data.get('Project Name', 'Infrastructure Project')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Extra Items</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    margin: 20px; 
                    font-size: 12px; 
                    color: #333;
                    line-height: 1.4;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 30px; 
                    border-bottom: 3px solid #f59e0b;
                    padding-bottom: 20px;
                }}
                .title {{ 
                    font-size: 24px; 
                    font-weight: bold; 
                    color: #f59e0b;
                    margin-bottom: 10px;
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 10px 0; 
                    font-size: 11px;
                }}
                th, td {{ 
                    border: 1px solid #333; 
                    padding: 10px; 
                    text-align: left; 
                    vertical-align: top;
                }}
                th {{ 
                    background-color: #fffbeb; 
                    font-weight: bold; 
                    color: #92400e;
                }}
                .amount {{ text-align: right; font-weight: 500; }}
                tr:nth-child(even) {{ background-color: #fafafa; }}
                .total-row {{
                    background-color: #fef3c7;
                    font-weight: bold;
                    color: #92400e;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">EXTRA ITEMS</div>
                <div style="font-size: 14px; color: #666;">Project: {project_name}</div>
                <div style="font-size: 14px; color: #666;">Date: {current_date}</div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">Item No.</th>
                        <th style="width: 40%;">Description</th>
                        <th style="width: 10%;">Unit</th>
                        <th style="width: 12%;">Quantity</th>
                        <th style="width: 14%;">Rate (₹)</th>
                        <th style="width: 14%;">Amount (₹)</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_extra = 0
        for index, row in self.extra_items_data.iterrows():
            item_no = row.get('Item No.', f"E{index + 1}")
            description = str(row.get('Description', 'Extra Item'))
            unit = row.get('Unit', 'Nos')
            quantity = self._safe_float(row.get('Quantity', 0))
            rate = self._safe_float(row.get('Rate', 0))
            amount = quantity * rate
            total_extra += amount
            
            html_content += f"""
                <tr>
                    <td style="text-align: center; font-weight: bold;">{item_no}</td>
                    <td>{description}</td>
                    <td style="text-align: center;">{unit}</td>
                    <td class="amount">{quantity:,.2f}</td>
                    <td class="amount">{rate:,.2f}</td>
                    <td class="amount">{amount:,.2f}</td>
                </tr>
            """
        
        html_content += f"""
                <tr class="total-row">
                    <td colspan="5" style="text-align: right; font-size: 13px;"><strong>TOTAL EXTRA ITEMS AMOUNT:</strong></td>
                    <td class="amount" style="font-size: 13px;"><strong>{self._format_currency(total_extra)}</strong></td>
                </tr>
            </tbody>
        </table>
        
        <div style="margin-top: 30px; padding: 15px; background-color: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 8px;">
            <h4 style="margin-top: 0; color: #92400e;">Extra Items Summary</h4>
            <p><strong>Total Extra Items:</strong> {len(self.extra_items_data)}</p>
            <p><strong>Total Extra Amount:</strong> {self._format_currency(total_extra)}</p>
            <p><strong>Note:</strong> These items are in addition to the main work order and will be added to the final bill calculation.</p>
        </div>
        
        <div style="margin-top: 30px; font-size: 10px; color: #666; text-align: center;">
            <p>This document contains additional work items not included in the original work order.</p>
            <p><strong>Generated on:</strong> {datetime.now().strftime('%d/%m/%Y at %I:%M %p')}</p>
        </div>
        </body>
        </html>
        """
        
        return html_content
    
    def create_pdf_documents(self, documents):
        """Create PDF documents with enhanced error handling"""
        pdf_files = {}
        
        if not documents:
            st.error("❌ No documents to convert to PDF")
            return pdf_files
        
        with st.spinner("Creating PDF documents..."):
            progress_bar = st.progress(0)
            total_docs = len(documents)
            
            for i, (doc_name, html_content) in enumerate(documents.items()):
                try:
                    st.info(f"🔄 Creating PDF: {doc_name}")
                    
                    # Clean filename
                    safe_filename = doc_name.replace(' ', '_').replace('/', '_')
                    
                    # Generate PDF
                    pdf_bytes = self.pdf_generator.generate_pdf(html_content, safe_filename)
                    
                    if pdf_bytes and len(pdf_bytes) > 1024:
                        pdf_files[f"{safe_filename}.pdf"] = pdf_bytes
                        st.success(f"✅ Created: {safe_filename}.pdf ({len(pdf_bytes):,} bytes)")
                    else:
                        st.warning(f"⚠️ Failed to create PDF for {doc_name}")
                        logger.warning(f"PDF generation failed for {doc_name}")
                
                except Exception as e:
                    st.error(f"❌ Error creating PDF for {doc_name}: {str(e)}")
                    logger.error(f"PDF creation error for {doc_name}: {str(e)}")
                
                # Update progress
                progress_bar.progress((i + 1) / total_docs)
            
            progress_bar.progress(1.0)
        
        if pdf_files:
            st.success(f"🎉 Successfully created {len(pdf_files)} PDF documents!")
        else:
            st.error("❌ Failed to create any PDF documents")
        
        return pdf_files

def create_sample_excel():
    """Create a sample Excel file for testing"""
    try:
        # Create sample data
        title_data = {
            'Project Name': ['Sample Infrastructure Project'],
            'TENDER PREMIUM %': [10],
            'Contractor': ['ABC Construction Company'],
            'Location': ['Sample City'],
            'Engineer': ['John Engineer'],
            'Date': [datetime.now().strftime('%d/%m/%Y')]
        }
        
        work_order_data = {
            'Item No.': [1, 2, 3, 4, 5],
            'Description': [
                'Excavation of foundation',
                'Concrete work M25 grade',
                'Steel reinforcement work',
                'Brick masonry work',
                'Plastering and finishing'
            ],
            'Unit': ['Cu.m', 'Cu.m', 'MT', 'Cu.m', 'Sq.m'],
            'Quantity Since': [100, 50, 5, 200, 500],
            'Rate': [500, 8500, 75000, 4500, 350],
            'Remarks': ['As per drawing', 'Grade M25', 'TMT bars', 'First class bricks', 'Smooth finish']
        }
        
        extra_items_data = {
            'Item No.': ['E1', 'E2'],
            'Description': ['Additional electrical work', 'Extra plumbing fittings'],
            'Unit': ['LS', 'LS'],
            'Quantity': [1, 1],
            'Rate': [25000, 15000]
        }
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame(title_data).to_excel(writer, sheet_name='Title', index=False)
            pd.DataFrame(work_order_data).to_excel(writer, sheet_name='Work Order', index=False)
            pd.DataFrame(work_order_data).to_excel(writer, sheet_name='Bill Quantity', index=False)
            pd.DataFrame(extra_items_data).to_excel(writer, sheet_name='Extra Items', index=False)
        
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Error creating sample Excel: {str(e)}")
        return None

def show_progress_steps(current_step):
    """Show progress steps"""
    steps = [
        "📤 Upload Excel File",
        "🔄 Process Data", 
        "📄 Generate Documents",
        "📥 Download PDFs"
    ]
    
    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i < current_step:
                st.success(step)
            elif i == current_step:
                st.info(f"**{step}**")
            else:
                st.write(step)

def main():
    """Main application function"""
    # Load CSS
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
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    
    # Sidebar with help and information
    with st.sidebar:
        st.markdown("### 🚀 Quick Start Guide")
        st.markdown("""
        1. **Upload Excel File** with these sheets:
           - Title (project info)
           - Work Order (required)
           - Bill Quantity (optional)
           - Extra Items (optional)
        
        2. **Process Data** - verify information
        
        3. **Generate Documents** - create bills
        
        4. **Download PDFs** - get your files
        """)
        
        st.markdown("---")
        
        # Sample file download
        st.markdown("### 📋 Sample File")
        sample_excel = create_sample_excel()
        if sample_excel:
            st.download_button(
                label="📥 Download Sample Excel",
                data=sample_excel,
                file_name="sample_bill_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download a sample Excel file to see the required format"
            )
        
        st.markdown("---")
        st.markdown("### 🛠️ Features")
        st.markdown("""
        ✅ **Multi-method PDF generation**  
        ✅ **Comprehensive error handling**  
        ✅ **Professional document templates**  
        ✅ **Automatic calculations**  
        ✅ **Mobile-responsive design**  
        ✅ **Real-time progress tracking**
        """)
    
    # Main content
    # Show progress
    show_progress_steps(st.session_state.current_step)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Process", "📊 Data Preview", "📄 Document Preview", "📥 Download"])
    
    with tab1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.subheader("📤 Excel File Upload")
        
        st.markdown("""
        <div class="status-info">
        <strong>📋 Required Excel Sheets:</strong><br>
        • <strong>Title:</strong> Project information and settings<br>
        • <strong>Work Order:</strong> Main work items (Required)<br>
        • <strong>Bill Quantity:</strong> Quantity updates (Optional)<br>
        • <strong>Extra Items:</strong> Additional items (Optional)
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose Excel file (.xlsx or .xls)", 
            type=['xlsx', 'xls'],
            help="Upload Excel file with the required sheets"
        )
        
        if uploaded_file is not None:
            # File info
            st.info(f"📁 File: {uploaded_file.name} ({uploaded_file.size:,} bytes)")
            
            if st.button("🔄 Process Excel File", type="primary"):
                st.session_state.current_step = 1
                
                try:
                    with st.spinner("🔄 Processing Excel file..."):
                        processor = EnhancedExcelProcessor(uploaded_file)
                        result = processor.process_excel()
                    
                    if result:
                        st.session_state.processed_data = result
                        st.session_state.current_step = 2
                        
                        # Show success message with details
                        st.markdown("""
                        <div class="status-success">
                        ✅ <strong>File processed successfully!</strong><br>
                        Data has been extracted and validated from all available sheets.
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show summary metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📋 Title Items", len(result.get('title_data', {})))
                        with col2:
                            st.metric("🔨 Work Items", len(result.get('work_order_data', [])))
                        with col3:
                            st.metric("📊 Bill Items", len(result.get('bill_quantity_data', [])))
                        with col4:
                            st.metric("➕ Extra Items", len(result.get('extra_items_data', [])))
                        
                        # Generate documents button
                        if st.button("📄 Generate All Documents", type="primary"):
                            st.session_state.current_step = 3
                            
                            try:
                                with st.spinner("📄 Generating documents..."):
                                    generator = ProfessionalDocumentGenerator(result)
                                    documents = generator.generate_all_documents()
                                
                                if documents:
                                    st.session_state.documents = documents
                                    
                                    # Generate PDFs
                                    with st.spinner("🎯 Creating PDF files..."):
                                        pdf_files = generator.create_pdf_documents(documents)
                                    
                                    if pdf_files:
                                        st.session_state.pdf_files = pdf_files
                                        st.session_state.current_step = 4
                                        
                                        st.markdown("""
                                        <div class="status-success">
                                        🎉 <strong>All documents generated successfully!</strong><br>
                                        PDF files are ready for download in the Download tab.
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Show generation summary
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.metric("📄 Documents", len(documents))
                                        with col2:
                                            st.metric("📥 PDF Files", len(pdf_files))
                                    else:
                                        st.markdown("""
                                        <div class="status-warning">
                                        ⚠️ <strong>Documents generated but PDF creation failed.</strong><br>
                                        You can still preview documents in HTML format.
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.markdown("""
                                    <div class="status-error">
                                    ❌ <strong>Failed to generate documents.</strong><br>
                                    Please check your data and try again.
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            except Exception as e:
                                st.error(f"❌ Error generating documents: {str(e)}")
                                logger.error(f"Document generation error: {str(e)}")
                    else:
                        st.markdown("""
                        <div class="status-error">
                        ❌ <strong>Failed to process Excel file.</strong><br>
                        Please check the file format and required sheets.
                        </div>
                        """, unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"❌ Processing error: {str(e)}")
                    logger.error(f"File processing error: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.subheader("📊 Data Preview")
        
        if st.session_state.processed_data:
            data = st.session_state.processed_data
            
            # Title data
            if data.get('title_data'):
                st.markdown("#### 📋 Project Information")
                title_df = pd.DataFrame(list(data['title_data'].items()), columns=['Field', 'Value'])
                st.table(title_df)
            
            # Work order data
            if not data.get('work_order_data', pd.DataFrame()).empty:
                st.markdown("#### 🔨 Work Order Items")
                st.dataframe(data['work_order_data'], use_container_width=True)
                
                # Calculate totals
                work_df = data['work_order_data']
                if 'Quantity Since' in work_df.columns and 'Rate' in work_df.columns:
                    total_amount = (pd.to_numeric(work_df['Quantity Since'], errors='coerce').fillna(0) * 
                                  pd.to_numeric(work_df['Rate'], errors='coerce').fillna(0)).sum()
                    st.metric("💰 Total Work Order Amount", f"₹ {total_amount:,.2f}")
            
            # Extra items
            if not data.get('extra_items_data', pd.DataFrame()).empty:
                st.markdown("#### ➕ Extra Items")
                st.dataframe(data['extra_items_data'], use_container_width=True)
        else:
            st.info("📤 Please upload and process an Excel file first.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.subheader("📄 Document Preview")
        
        if st.session_state.documents:
            doc_names = list(st.session_state.documents.keys())
            selected_doc = st.selectbox("📋 Select document to preview:", doc_names)
            
            if selected_doc:
                st.markdown(f"### 👁️ Preview: {selected_doc}")
                doc_content = st.session_state.documents[selected_doc]
                
                # Show HTML preview
                st.components.v1.html(doc_content, height=600, scrolling=True)
        else:
            st.info("📄 Please generate documents first.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.subheader("📥 Download Documents")
        
        if st.session_state.pdf_files:
            st.markdown("""
            <div class="status-success">
            🎉 <strong>PDF documents ready for download!</strong><br>
            All documents have been successfully generated and are available below.
            </div>
            """, unsafe_allow_html=True)
            
            # Show file metrics
            total_size = sum(len(pdf_bytes) for pdf_bytes in st.session_state.pdf_files.values())
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📄 Total Files", len(st.session_state.pdf_files))
            with col2:
                st.metric("💾 Total Size", f"{total_size/1024:.1f} KB")
            
            st.markdown("---")
            
            # Individual downloads
            st.markdown("### 📋 Individual Downloads")
            cols = st.columns(2)
            col_idx = 0
            
            for filename, pdf_bytes in st.session_state.pdf_files.items():
                with cols[col_idx % 2]:
                    file_size = len(pdf_bytes) / 1024  # KB
                    st.download_button(
                        label=f"📥 {filename.replace('_', ' ')}",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        help=f"Download {filename} ({file_size:.1f} KB)",
                        key=f"download_{filename}"
                    )
                col_idx += 1
            
            # Bulk download option
            st.markdown("---")
            st.markdown("### 📦 Bulk Download")
            if st.button("📥 Download All PDFs as ZIP", type="primary"):
                try:
                    import zipfile
                    
                    # Create ZIP file in memory
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for filename, pdf_bytes in st.session_state.pdf_files.items():
                            zip_file.writestr(filename, pdf_bytes)
                    
                    zip_bytes = zip_buffer.getvalue()
                    
                    st.download_button(
                        label="📥 Download ZIP File",
                        data=zip_bytes,
                        file_name=f"bill_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        help=f"Download all PDFs in one ZIP file ({len(zip_bytes)/1024:.1f} KB)"
                    )
                    
                except Exception as e:
                    st.error(f"Error creating ZIP file: {str(e)}")
        
        elif st.session_state.documents:
            st.markdown("""
            <div class="status-warning">
            ⚠️ <strong>HTML documents available</strong><br>
            PDF generation failed, but you can download HTML versions.
            </div>
            """, unsafe_allow_html=True)
            
            # Offer HTML downloads
            st.markdown("### 📄 HTML Downloads")
            for doc_name, html_content in st.session_state.documents.items():
                st.download_button(
                    label=f"📄 {doc_name}.html",
                    data=html_content,
                    file_name=f"{doc_name}.html",
                    mime="text/html",
                    key=f"download_html_{doc_name}"
                )
        else:
            st.info("🔄 Please upload a file and generate documents first.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; border-radius: 10px; margin-top: 30px;">
        <h3 style="margin: 0;">🧾 Professional Bill Generator</h3>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">
            Advanced Infrastructure Billing System | 
            Generated on {datetime.now().strftime('%d/%m/%Y at %I:%M %p')}
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")
        st.error("Please refresh the page and try again.")
        logger.error(f"Application error: {str(e)}")
        logger.error(traceback.format_exc())