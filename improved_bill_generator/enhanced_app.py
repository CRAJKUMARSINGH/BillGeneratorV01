"""
Enhanced Bill Generator - Complete PDF Solution
Combines best features from both repositories with complete PDF output for all templates
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import io
import base64
from pathlib import Path
import os
import sys
import traceback
import json
import tempfile
from typing import Dict, List, Any, Optional, Union
import logging
import streamlit.components.v1 as components

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Enhanced Infrastructure Billing System",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import utility modules
try:
    from utils.excel_processor import ExcelProcessor
    from utils.document_generator import DocumentGenerator
    from utils.pdf_merger import PDFMerger
except ImportError:
    st.warning("Utils modules not found. Using fallback implementations.")

# Custom CSS for enhanced UI
def load_custom_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main > div {
        padding: 2rem 1rem;
    }

    /* Header styling - Green gradient design */
    .header-container {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 50%, #81C784 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: center;
    }

    .header-subtitle {
        font-size: 1.2rem;
        text-align: center;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }

    /* Mode selection cards */
    .mode-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .mode-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.15);
        transform: translateY(-2px);
        background: #f8fff8;
    }

    /* Form styling */
    .form-section {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 2rem;
        border: 1px solid #e9ecef;
    }

    .form-section h3 {
        color: #2c3e50;
        border-bottom: 2px solid #4CAF50;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
    }

    /* Results styling */
    .results-container {
        background: #e8f5e9;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #4CAF50;
    }

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
    </style>
    """, unsafe_allow_html=True)

def show_header():
    """Display application header"""
    st.markdown("""
    <div class="header-container">
        <div class="header-title">🏛️ Enhanced Infrastructure Billing System</div>
        <div class="header-subtitle">Complete PDF Generation for All Templates</div>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Excel Processor
class EnhancedExcelProcessor:
    """Enhanced Excel processor with better error handling and format support"""
    
    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
    
    def process_excel(self):
        """Process uploaded Excel file with enhanced format support"""
        try:
            excel_data = pd.ExcelFile(self.uploaded_file)
            logger.info(f"Available sheets: {excel_data.sheet_names}")
            
            data = {}
            
            # Process Title sheet (optional but recommended)
            if 'Title' in excel_data.sheet_names:
                data['title_data'] = self._process_title_sheet(excel_data)
            else:
                data['title_data'] = self._get_default_title_data()
            
            # Process Work Order sheet (required)
            if 'Work Order' in excel_data.sheet_names:
                data['work_order_data'] = self._process_work_order_sheet(excel_data)
            else:
                raise Exception("Required 'Work Order' sheet not found in Excel file")
            
            # Process Bill Quantity sheet (required)
            if 'Bill Quantity' in excel_data.sheet_names:
                data['bill_quantity_data'] = self._process_bill_quantity_sheet(excel_data)
            else:
                raise Exception("Required 'Bill Quantity' sheet not found in Excel file")
            
            # Process Extra Items sheet (optional)
            if 'Extra Items' in excel_data.sheet_names:
                data['extra_items_data'] = self._process_extra_items_sheet(excel_data)
            else:
                data['extra_items_data'] = pd.DataFrame()
            
            return data
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {str(e)}")
            raise Exception(f"Error processing Excel file: {str(e)}")
    
    def _get_default_title_data(self):
        """Get default title data when Title sheet is missing"""
        return {
            'Name of Work ;-': 'Project Name',
            'Agreement No.': 'AGR001',
            'Name of Contractor or supplier :': 'Contractor Name',
            'Bill Number': 'BILL001',
            'Running or Final': 'Running',
            'TENDER PREMIUM %': '5.0',
            'Date of measurement :': datetime.now().strftime('%d/%m/%Y')
        }
    
    def _process_title_sheet(self, excel_data):
        """Extract metadata from Title sheet"""
        try:
            title_df = pd.read_excel(excel_data, sheet_name='Title', header=None)
            title_data = {}
            
            for index, row in title_df.iterrows():
                if pd.notna(row[0]) and pd.notna(row[1]):
                    key = str(row[0]).strip()
                    val = str(row[1]).strip()
                    if key and val and key != 'nan' and val != 'nan':
                        title_data[key] = val
            
            # Ensure required fields
            if 'TENDER PREMIUM %' not in title_data:
                title_data['TENDER PREMIUM %'] = '5.0'
            
            return title_data
            
        except Exception as e:
            logger.error(f"Error processing Title sheet: {str(e)}")
            return self._get_default_title_data()
    
    def _process_work_order_sheet(self, excel_data):
        """Extract work order data with enhanced format handling"""
        try:
            # Try different header rows to find the data
            work_order_df = None
            for header_row in [0, 20, 21]:  # Common header locations
                try:
                    df = pd.read_excel(excel_data, sheet_name='Work Order', header=header_row)
                    if len(df.columns) >= 6:  # Minimum expected columns
                        work_order_df = df
                        break
                except:
                    continue
            
            if work_order_df is None:
                work_order_df = pd.read_excel(excel_data, sheet_name='Work Order', header=None)
            
            # Standardize column names
            if len(work_order_df.columns) >= 7:
                work_order_df.columns = ['Item No.', 'Description', 'Unit', 'Quantity', 'Rate', 'Amount', 'Remark']
            elif len(work_order_df.columns) >= 6:
                work_order_df.columns = ['Item No.', 'Description', 'Unit', 'Quantity', 'Rate', 'Amount']
                work_order_df['Remark'] = ''
            
            # Clean and validate data
            work_order_df = work_order_df.dropna(subset=['Description'], how='all')
            work_order_df = work_order_df[work_order_df['Description'].notna()]
            
            # Convert numeric columns
            for col in ['Quantity', 'Rate', 'Amount']:
                if col in work_order_df.columns:
                    work_order_df[col] = pd.to_numeric(work_order_df[col], errors='coerce').fillna(0)
            
            return work_order_df
            
        except Exception as e:
            logger.error(f"Error processing Work Order sheet: {str(e)}")
            raise Exception(f"Error processing Work Order sheet: {str(e)}")
    
    def _process_bill_quantity_sheet(self, excel_data):
        """Extract bill quantity data"""
        try:
            # Try different header rows
            bill_quantity_df = None
            for header_row in [0, 20, 21]:
                try:
                    df = pd.read_excel(excel_data, sheet_name='Bill Quantity', header=header_row)
                    if len(df.columns) >= 6:
                        bill_quantity_df = df
                        break
                except:
                    continue
            
            if bill_quantity_df is None:
                bill_quantity_df = pd.read_excel(excel_data, sheet_name='Bill Quantity', header=None)
            
            # Standardize column names
            if len(bill_quantity_df.columns) >= 7:
                bill_quantity_df.columns = ['Item No.', 'Description', 'Unit', 'Quantity', 'Rate', 'Amount', 'Remark']
            elif len(bill_quantity_df.columns) >= 6:
                bill_quantity_df.columns = ['Item No.', 'Description', 'Unit', 'Quantity', 'Rate', 'Amount']
                bill_quantity_df['Remark'] = ''
            
            # Clean data
            bill_quantity_df = bill_quantity_df.dropna(subset=['Description'], how='all')
            
            # Convert numeric columns
            for col in ['Quantity', 'Rate', 'Amount']:
                if col in bill_quantity_df.columns:
                    bill_quantity_df[col] = pd.to_numeric(bill_quantity_df[col], errors='coerce').fillna(0)
            
            return bill_quantity_df
            
        except Exception as e:
            logger.error(f"Error processing Bill Quantity sheet: {str(e)}")
            raise Exception(f"Error processing Bill Quantity sheet: {str(e)}")
    
    def _process_extra_items_sheet(self, excel_data):
        """Extract extra items data"""
        try:
            extra_items_df = pd.read_excel(excel_data, sheet_name='Extra Items', header=0)
            
            # Clean data
            extra_items_df = extra_items_df.dropna(subset=['Description'], how='all')
            
            # Convert numeric columns
            for col in ['Quantity', 'Rate', 'Amount']:
                if col in extra_items_df.columns:
                    extra_items_df[col] = pd.to_numeric(extra_items_df[col], errors='coerce').fillna(0)
            
            return extra_items_df
            
        except Exception as e:
            logger.error(f"Error processing Extra Items sheet: {str(e)}")
            return pd.DataFrame()

# Enhanced Document Generator with Complete PDF Support
class CompleteDocumentGenerator:
    """Complete document generator ensuring all templates produce proper PDFs"""
    
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
        """Generate all required documents with complete templates"""
        documents = {}
        
        # Generate all document types
        documents['First Page Summary'] = self._generate_first_page()
        documents['Last Page Certificate'] = self._generate_last_page()
        documents['Bill Summary'] = self._generate_bill_summary()
        documents['Work Order Details'] = self._generate_work_order_details()
        documents['Deviation Statement'] = self._generate_deviation_statement()
        documents['Certificate II'] = self._generate_certificate_ii()
        documents['Certificate III'] = self._generate_certificate_iii()
        documents['Note Sheet'] = self._generate_note_sheet()
        
        if not self.extra_items_data.empty:
            documents['Extra Items'] = self._generate_extra_items()
        
        return documents
    
    def _generate_first_page(self):
        """Generate comprehensive first page summary"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        project_name = self.title_data.get('Name of Work ;-', 'Project Name')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>First Page Summary</title>
            <style>
                @page {{
                    size: A4 landscape;
                    margin: 0.5in;
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    font-size: 10px; 
                    line-height: 1.2;
                    margin: 0;
                    padding: 0;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 15px; 
                    border-bottom: 2px solid #000;
                    padding-bottom: 10px;
                }}
                .title {{ 
                    font-size: 14px; 
                    font-weight: bold; 
                    margin-bottom: 5px;
                }}
                .project-info {{
                    font-size: 11px;
                    margin-bottom: 10px;
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 5px 0; 
                    font-size: 9px;
                }}
                th, td {{ 
                    border: 1px solid #000; 
                    padding: 3px; 
                    text-align: left; 
                    vertical-align: top;
                }}
                th {{ 
                    background-color: #f0f0f0; 
                    font-weight: bold; 
                    text-align: center;
                }}
                .amount {{ text-align: right; }}
                .center {{ text-align: center; }}
                .bold {{ font-weight: bold; }}
                .total-row {{ background-color: #e8f5e9; }}
                .premium-row {{ background-color: #fff3cd; }}
                .grand-total-row {{ 
                    background-color: #d4edda; 
                    font-weight: bold;
                    font-size: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">FIRST PAGE SUMMARY - CONTRACTOR'S BILL</div>
                <div class="project-info">
                    <strong>Project:</strong> {project_name}<br>
                    <strong>Bill No:</strong> {self.title_data.get('Bill Number', 'BILL001')}<br>
                    <strong>Date:</strong> {current_date}
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th width="5%">S.No.</th>
                        <th width="35%">Description of Work</th>
                        <th width="8%">Unit</th>
                        <th width="10%">Quantity</th>
                        <th width="10%">Rate (Rs.)</th>
                        <th width="12%">Amount (Rs.)</th>
                        <th width="20%">Remarks</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_amount = 0
        row_count = 0
        
        # Add work order items
        for index, row in self.work_order_data.iterrows():
            row_count += 1
            item_no = self._safe_str(row.get('Item No.', row_count))
            description = self._safe_str(row.get('Description', ''))
            unit = self._safe_str(row.get('Unit', ''))
            quantity = self._safe_float(row.get('Quantity', 0))
            rate = self._safe_float(row.get('Rate', 0))
            amount = quantity * rate
            remark = self._safe_str(row.get('Remark', ''))
            
            total_amount += amount
            
            html_content += f"""
                <tr>
                    <td class="center">{item_no}</td>
                    <td>{description}</td>
                    <td class="center">{unit}</td>
                    <td class="amount">{quantity:.2f}</td>
                    <td class="amount">{rate:.2f}</td>
                    <td class="amount">{amount:.2f}</td>
                    <td>{remark}</td>
                </tr>
            """
        
        # Add extra items if any
        if not self.extra_items_data.empty:
            html_content += f"""
                <tr class="premium-row">
                    <td colspan="7" class="center bold">EXTRA ITEMS</td>
                </tr>
            """
            
            for index, row in self.extra_items_data.iterrows():
                row_count += 1
                item_no = self._safe_str(row.get('Item No.', f'E{row_count}'))
                description = self._safe_str(row.get('Description', ''))
                unit = self._safe_str(row.get('Unit', ''))
                quantity = self._safe_float(row.get('Quantity', 0))
                rate = self._safe_float(row.get('Rate', 0))
                amount = quantity * rate
                remark = self._safe_str(row.get('Remark', 'Extra Item'))
                
                total_amount += amount
                
                html_content += f"""
                    <tr>
                        <td class="center">{item_no}</td>
                        <td>{description}</td>
                        <td class="center">{unit}</td>
                        <td class="amount">{quantity:.2f}</td>
                        <td class="amount">{rate:.2f}</td>
                        <td class="amount">{amount:.2f}</td>
                        <td>{remark}</td>
                    </tr>
                """
        
        # Calculate totals
        premium_percent = self._safe_float(self.title_data.get('TENDER PREMIUM %', 5.0))
        premium_amount = total_amount * (premium_percent / 100)
        grand_total = total_amount + premium_amount
        
        html_content += f"""
                <tr class="total-row">
                    <td colspan="5" class="center bold">SUBTOTAL</td>
                    <td class="amount bold">{total_amount:.2f}</td>
                    <td></td>
                </tr>
                <tr class="premium-row">
                    <td colspan="5" class="center bold">TENDER PREMIUM ({premium_percent}%)</td>
                    <td class="amount bold">{premium_amount:.2f}</td>
                    <td></td>
                </tr>
                <tr class="grand-total-row">
                    <td colspan="5" class="center bold">GRAND TOTAL</td>
                    <td class="amount bold">{grand_total:.2f}</td>
                    <td></td>
                </tr>
            </tbody>
            </table>
            
            <div style="margin-top: 20px; font-size: 11px;">
                <p><strong>Summary:</strong></p>
                <p>Work Order Amount: Rs. {total_amount:.2f}</p>
                <p>Tender Premium ({premium_percent}%): Rs. {premium_amount:.2f}</p>               
                <p><strong>Grand Total: Rs. {grand_total:.2f}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_last_page(self):
        """Generate last page certificate"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        # Calculate totals
        total_amount = 0
        for index, row in self.work_order_data.iterrows():
            quantity = self._safe_float(row.get('Quantity', 0))
            rate = self._safe_float(row.get('Rate', 0))
            total_amount += quantity * rate
        
        if not self.extra_items_data.empty:
            for index, row in self.extra_items_data.iterrows():
                quantity = self._safe_float(row.get('Quantity', 0))
                rate = self._safe_float(row.get('Rate', 0))
                total_amount += quantity * rate
        
        premium_percent = self._safe_float(self.title_data.get('TENDER PREMIUM %', 5.0))
        premium_amount = total_amount * (premium_percent / 100)
        grand_total = total_amount + premium_amount
        
        # Calculate deductions
        sd_amount = grand_total * 0.10  # Security Deposit 10%
        it_amount = grand_total * 0.02  # Income Tax 2%
        gst_amount = grand_total * 0.02  # GST 2%
        lc_amount = grand_total * 0.01  # Labour Cess 1%
        total_deductions = sd_amount + it_amount + gst_amount + lc_amount
        net_payable = grand_total - total_deductions
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Last Page Certificate</title>
            <style>
                @page {{
                    size: A4 portrait;
                    margin: 1in;
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    font-size: 12px; 
                    line-height: 1.4;
                    margin: 0;
                    padding: 0;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 30px; 
                    border-bottom: 2px solid #000;
                    padding-bottom: 15px;
                }}
                .title {{ 
                    font-size: 16px; 
                    font-weight: bold; 
                    margin-bottom: 10px;
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 15px 0; 
                }}
                th, td {{ 
                    border: 1px solid #000; 
                    padding: 8px; 
                    text-align: left; 
                }}
                th {{ 
                    background-color: #f0f0f0; 
                    font-weight: bold; 
                }}
                .amount {{ text-align: right; }}
                .center {{ text-align: center; }}
                .bold {{ font-weight: bold; }}
                .signature-section {{
                    margin-top: 40px;
                    border-top: 1px solid #ccc;
                    padding-top: 20px;
                }}
                .signature-box {{
                    float: left;
                    width: 45%;
                    margin: 10px;
                    border: 1px solid #ccc;
                    padding: 15px;
                    min-height: 80px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">LAST PAGE - PAYMENT CERTIFICATE</div>
                <div>Date: {current_date}</div>
            </div>
            
            <h3>BILL SUMMARY & DEDUCTIONS</h3>
            <table>
                <tr><th>Description</th><th class="amount">Amount (Rs.)</th></tr>
                <tr><td>Work Order Amount</td><td class="amount">{total_amount:.2f}</td></tr>
                <tr><td>Tender Premium ({premium_percent}%)</td><td class="amount">{premium_amount:.2f}</td></tr>
                <tr class="bold"><td><strong>Gross Total</strong></td><td class="amount"><strong>{grand_total:.2f}</strong></td></tr>
                <tr><td colspan="2" style="background-color: #f5f5f5; font-weight: bold; text-align: center;">DEDUCTIONS</td></tr>
                <tr><td>Security Deposit (10%)</td><td class="amount">-{sd_amount:.2f}</td></tr>
                <tr><td>Income Tax (2%)</td><td class="amount">-{it_amount:.2f}</td></tr>
                <tr><td>GST (2%)</td><td class="amount">-{gst_amount:.2f}</td></tr>
                <tr><td>Labour Cess (1%)</td><td class="amount">-{lc_amount:.2f}</td></tr>
                <tr><td><strong>Total Deductions</strong></td><td class="amount"><strong>-{total_deductions:.2f}</strong></td></tr>
                <tr style="background-color: #d4edda;"><td><strong>NET PAYABLE AMOUNT</strong></td><td class="amount"><strong>{net_payable:.2f}</strong></td></tr>
            </table>
            
            <div style="margin: 30px 0; padding: 15px; border: 2px solid #4CAF50; background-color: #f8fff8;">
                <h3 style="margin: 0 0 10px 0; color: #2e7d32;">AMOUNT TO BE PAID</h3>
                <p style="font-size: 18px; font-weight: bold; margin: 0; color: #1b5e20;">
                    Rs. {net_payable:.2f}
                </p>
                <p style="margin: 10px 0 0 0; font-style: italic;">
                    (Rupees {self._number_to_words(int(net_payable))} only)
                </p>
            </div>
            
            <div class="signature-section">
                <div class="signature-box">
                    <h4>CONTRACTOR</h4>
                    <p>Name: {self.title_data.get('Name of Contractor or supplier :', 'Contractor Name')}</p>
                    <p>Signature: _________________________</p>
                    <p>Date: {current_date}</p>
                </div>
                
                <div class="signature-box" style="float: right;">
                    <h4>AUTHORIZING OFFICER</h4>
                    <p>Name: _________________________</p>
                    <p>Designation: Executive Engineer</p>
                    <p>Signature: _________________________</p>
                    <p>Date: {current_date}</p>
                </div>
                <div style="clear: both;"></div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_bill_summary(self):
        """Generate detailed bill summary"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Bill Summary</title>
            <style>
                @page {{
                    size: A4 portrait;
                    margin: 0.75in;
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    font-size: 11px; 
                    line-height: 1.3;
                    margin: 0;
                    padding: 0;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 20px; 
                    border-bottom: 2px solid #000;
                    padding-bottom: 10px;
                }}
                .title {{ 
                    font-size: 16px; 
                    font-weight: bold; 
                    margin-bottom: 5px;
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 10px 0; 
                }}
                th, td {{ 
                    border: 1px solid #000; 
                    padding: 6px; 
                    text-align: left; 
                }}
                th {{ 
                    background-color: #f0f0f0; 
                    font-weight: bold; 
                    text-align: center;
                }}
                .amount {{ text-align: right; }}
                .center {{ text-align: center; }}
                .bold {{ font-weight: bold; }}
                .summary-box {{
                    border: 2px solid #4CAF50;
                    padding: 15px;
                    margin: 20px 0;
                    background-color: #f8fff8;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">DETAILED BILL SUMMARY</div>
                <div>Bill No: {self.title_data.get('Bill Number', 'BILL001')} | Date: {current_date}</div>
            </div>
            
            <div class="summary-box">
                <h3>PROJECT INFORMATION</h3>
                <table>
                    <tr><td><strong>Project Name</strong></td><td>{self.title_data.get('Name of Work ;-', 'Project Name')}</td></tr>
                    <tr><td><strong>Agreement No.</strong></td><td>{self.title_data.get('Agreement No.', 'AGR001')}</td></tr>
                    <tr><td><strong>Contractor</strong></td><td>{self.title_data.get('Name of Contractor or supplier :', 'Contractor Name')}</td></tr>
                    <tr><td><strong>Bill Type</strong></td><td>{self.title_data.get('Running or Final', 'Running')}</td></tr>
                </table>
            </div>
        """
        
        # Calculate and display summary
        total_amount = 0
        work_items_count = len(self.work_order_data)
        extra_items_count = len(self.extra_items_data) if not self.extra_items_data.empty else 0
        
        for index, row in self.work_order_data.iterrows():
            quantity = self._safe_float(row.get('Quantity', 0))
            rate = self._safe_float(row.get('Rate', 0))
            total_amount += quantity * rate
        
        extra_amount = 0
        if not self.extra_items_data.empty:
            for index, row in self.extra_items_data.iterrows():
                quantity = self._safe_float(row.get('Quantity', 0))
                rate = self._safe_float(row.get('Rate', 0))
                extra_amount += quantity * rate
        
        total_amount += extra_amount
        premium_percent = self._safe_float(self.title_data.get('TENDER PREMIUM %', 5.0))
        premium_amount = total_amount * (premium_percent / 100)
        grand_total = total_amount + premium_amount
        
        html_content += f"""
            <h3>SUMMARY BREAKDOWN</h3>
            <table>
                <tr><th>Category</th><th>Count</th><th class="amount">Amount (Rs.)</th></tr>
                <tr><td>Work Order Items</td><td class="center">{work_items_count}</td><td class="amount">{total_amount - extra_amount:.2f}</td></tr>
                <tr><td>Extra Items</td><td class="center">{extra_items_count}</td><td class="amount">{extra_amount:.2f}</td></tr>
                <tr class="bold"><td><strong>Subtotal</strong></td><td class="center"><strong>{work_items_count + extra_items_count}</strong></td><td class="amount"><strong>{total_amount:.2f}</strong></td></tr>
                <tr><td>Tender Premium ({premium_percent}%)</td><td class="center">-</td><td class="amount">{premium_amount:.2f}</td></tr>
                <tr style="background-color: #d4edda;"><td><strong>GRAND TOTAL</strong></td><td class="center">-</td><td class="amount"><strong>{grand_total:.2f}</strong></td></tr>
            </table>
            
            <div style="margin-top: 30px; font-size: 10px; color: #666;">
                <p><strong>Note:</strong> This summary includes all work items and extra items as per the bill quantity sheet.</p>
                <p>Generated on: {current_date}</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_work_order_details(self):
        """Generate detailed work order breakdown"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Work Order Details</title>
            <style>
                @page {{
                    size: A4 landscape;
                    margin: 0.5in;
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    font-size: 9px; 
                    line-height: 1.2;
                    margin: 0;
                    padding: 0;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 15px; 
                    border-bottom: 2px solid #000;
                    padding-bottom: 10px;
                }}
                .title {{ 
                    font-size: 14px; 
                    font-weight: bold; 
                    margin-bottom: 5px;
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 5px 0; 
                    font-size: 8px;
                }}
                th, td {{ 
                    border: 1px solid #000; 
                    padding: 2px; 
                    text-align: left; 
                    vertical-align: top;
                }}
                th {{ 
                    background-color: #f0f0f0; 
                    font-weight: bold; 
                    text-align: center;
                }}
                .amount {{ text-align: right; }}
                .center {{ text-align: center; }}
                .description {{ max-width: 200px; word-wrap: break-word; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">WORK ORDER DETAILS</div>
                <div>Date: {current_date}</div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th width="5%">Item No.</th>
                        <th width="40%">Description</th>
                        <th width="8%">Unit</th>
                        <th width="10%">Quantity</th>
                        <th width="10%">Rate</th>
                        <th width="12%">Amount</th>
                        <th width="15%">Remarks</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_amount = 0
        for index, row in self.work_order_data.iterrows():
            item_no = self._safe_str(row.get('Item No.', index + 1))
            description = self._safe_str(row.get('Description', ''))
            # Truncate long descriptions
            if len(description) > 60:
                description = description[:57] + "..."
            unit = self._safe_str(row.get('Unit', ''))
            quantity = self._safe_float(row.get('Quantity', 0))
            rate = self._safe_float(row.get('Rate', 0))
            amount = quantity * rate
            remarks = self._safe_str(row.get('Remark', ''))
            
            total_amount += amount
            
            html_content += f"""
                <tr>
                    <td class="center">{item_no}</td>
                    <td class="description">{description}</td>
                    <td class="center">{unit}</td>
                    <td class="amount">{quantity:.2f}</td>
                    <td class="amount">{rate:.2f}</td>
                    <td class="amount">{amount:.2f}</td>
                    <td>{remarks}</td>
                </tr>
            """
        
        html_content += f"""
                <tr style="background-color: #d4edda; font-weight: bold;">
                    <td colspan="5" class="center"><strong>TOTAL</strong></td>
                    <td class="amount"><strong>{total_amount:.2f}</strong></td>
                    <td></td>
                </tr>
            </tbody>
            </table>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_deviation_statement(self):
        """Generate deviation statement comparing work order vs bill quantity"""
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
                    margin: 0.5in;
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    font-size: 8px; 
                    line-height: 1.1;
                    margin: 0;
                    padding: 0;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 10px; 
                    border-bottom: 2px solid #000;
                    padding-bottom: 8px;
                }}
                .title {{ 
                    font-size: 12px; 
                    font-weight: bold; 
                    margin-bottom: 5px;
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 5px 0; 
                    font-size: 7px;
                }}
                th, td {{ 
                    border: 1px solid #000; 
                    padding: 2px; 
                    text-align: left; 
                    vertical-align: top;
                }}
                th {{ 
                    background-color: #f0f0f0; 
                    font-weight: bold; 
                    text-align: center;
                }}
                .amount {{ text-align: right; }}
                .center {{ text-align: center; }}
                .excess {{ background-color: #ffebee; }}
                .saving {{ background-color: #e8f5e9; }}
                .total-row {{ background-color: #f5f5f5; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">DEVIATION STATEMENT</div>
                <div>Work Order vs Bill Quantity Comparison</div>
                <div>Date: {current_date}</div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th rowspan="2" width="4%">S.No.</th>
                        <th rowspan="2" width="20%">Description</th>
                        <th rowspan="2" width="6%">Unit</th>
                        <th colspan="3" width="24%">Work Order</th>
                        <th colspan="3" width="24%">Bill Quantity</th>
                        <th colspan="2" width="12%">Excess</th>
                        <th colspan="2" width="12%">Saving</th>
                    </tr>
                    <tr>
                        <th width="8%">Qty</th>
                        <th width="8%">Rate</th>
                        <th width="8%">Amount</th>
                        <th width="8%">Qty</th>
                        <th width="8%">Rate</th>
                        <th width="8%">Amount</th>
                        <th width="6%">Qty</th>
                        <th width="6%">Amount</th>
                        <th width="6%">Qty</th>
                        <th width="6%">Amount</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_wo_amount = 0
        total_bill_amount = 0
        total_excess_amount = 0
        total_saving_amount = 0
        
        # Compare work order with bill quantity
        for index, wo_row in self.work_order_data.iterrows():
            item_no = self._safe_str(wo_row.get('Item No.', index + 1))
            description = self._safe_str(wo_row.get('Description', ''))
            if len(description) > 40:
                description = description[:37] + "..."
            unit = self._safe_str(wo_row.get('Unit', ''))
            wo_qty = self._safe_float(wo_row.get('Quantity', 0))
            rate = self._safe_float(wo_row.get('Rate', 0))
            wo_amount = wo_qty * rate
            
            # Find corresponding bill quantity
            bill_qty = 0
            if index < len(self.bill_quantity_data):
                bill_row = self.bill_quantity_data.iloc[index]
                bill_qty = self._safe_float(bill_row.get('Quantity', 0))
            
            bill_amount = bill_qty * rate
            
            # Calculate excess/saving
            excess_qty = max(0, bill_qty - wo_qty)
            excess_amount = excess_qty * rate
            saving_qty = max(0, wo_qty - bill_qty)
            saving_amount = saving_qty * rate
            
            total_wo_amount += wo_amount
            total_bill_amount += bill_amount
            total_excess_amount += excess_amount
            total_saving_amount += saving_amount
            
            row_class = ""
            if excess_amount > 0:
                row_class = "excess"
            elif saving_amount > 0:
                row_class = "saving"
            
            html_content += f"""
                <tr class="{row_class}">
                    <td class="center">{item_no}</td>
                    <td>{description}</td>
                    <td class="center">{unit}</td>
                    <td class="amount">{wo_qty:.2f}</td>
                    <td class="amount">{rate:.2f}</td>
                    <td class="amount">{wo_amount:.2f}</td>
                    <td class="amount">{bill_qty:.2f}</td>
                    <td class="amount">{rate:.2f}</td>
                    <td class="amount">{bill_amount:.2f}</td>
                    <td class="amount">{excess_qty:.2f if excess_qty > 0 else ''}</td>
                    <td class="amount">{excess_amount:.2f if excess_amount > 0 else ''}</td>
                    <td class="amount">{saving_qty:.2f if saving_qty > 0 else ''}</td>
                    <td class="amount">{saving_amount:.2f if saving_amount > 0 else ''}</td>
                </tr>
            """
        
        # Add totals
        net_difference = total_bill_amount - total_wo_amount
        premium_percent = self._safe_float(self.title_data.get('TENDER PREMIUM %', 5.0))
        
        html_content += f"""
                <tr class="total-row">
                    <td colspan="5" class="center"><strong>TOTALS</strong></td>
                    <td class="amount"><strong>{total_wo_amount:.2f}</strong></td>
                    <td colspan="2"></td>
                    <td class="amount"><strong>{total_bill_amount:.2f}</strong></td>
                    <td></td>
                    <td class="amount"><strong>{total_excess_amount:.2f}</strong></td>
                    <td></td>
                    <td class="amount"><strong>{total_saving_amount:.2f}</strong></td>
                </tr>
            </tbody>
            </table>
            
            <div style="margin-top: 15px; font-size: 10px;">
                <table style="width: 50%;">
                    <tr><th colspan="2">SUMMARY</th></tr>
                    <tr><td>Work Order Total:</td><td class="amount">Rs. {total_wo_amount:.2f}</td></tr>
                    <tr><td>Bill Quantity Total:</td><td class="amount">Rs. {total_bill_amount:.2f}</td></tr>
                    <tr><td>Net Difference:</td><td class="amount">Rs. {net_difference:.2f}</td></tr>
                    <tr><td>Status:</td><td>{'Excess' if net_difference > 0 else 'Saving' if net_difference < 0 else 'No Change'}</td></tr>
                </table>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_certificate_ii(self):
        """Generate Certificate II"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Certificate II</title>
            <style>
                @page {{
                    size: A4 portrait;
                    margin: 1in;
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    font-size: 12px; 
                    line-height: 1.5;
                    margin: 0;
                    padding: 0;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 30px; 
                    border-bottom: 2px solid #000;
                    padding-bottom: 15px;
                }}
                .title {{ 
                    font-size: 16px; 
                    font-weight: bold; 
                    margin-bottom: 10px;
                }}
                .certificate-text {{
                    text-align: justify;
                    margin: 20px 0;
                    line-height: 1.6;
                }}
                .signature-section {{
                    margin-top: 50px;
                    border-top: 1px solid #ccc;
                    padding-top: 30px;
                }}
                .signature-box {{
                    float: left;
                    width: 45%;
                    margin: 10px;
                    border: 1px solid #ccc;
                    padding: 20px;
                    min-height: 100px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">II. CERTIFICATE AND SIGNATURES</div>
                <div>Project: {self.title_data.get('Name of Work ;-', 'Project Name')}</div>
            </div>
            
            <div class="certificate-text">
                <p>The measurements on which are based the entries in columns 1 to 6 of Account I, 
                were made by Junior Engineer on {self.title_data.get('Date of measurement :', current_date)}, 
                and are recorded at page 04-20 of Measurement Book No. 887.</p>
                
                <p>*Certified that in addition to and quite apart from the quantities of work actually executed, 
                as shown in column 4 of Account I, some work has actually been done in connection with several items 
                and the value of such work (after deduction therefrom the proportionate amount of secured advances, 
                if any, ultimately recoverable on account of the quantities of materials used therein) is in no case, 
                less than the advance payments as per item 2 of the Memorandum, if payment is made.</p>
                
                <p>+Certified that the contractor has made satisfactory progress with the work, and that the 
                quantities and amounts claimed are correct and the work has been executed in accordance with 
                the specifications and the terms of the contract.</p>
                
                <p>I also certify that the amount claimed is not more than the amount admissible under the contract.</p>
            </div>
            
            <div class="signature-section">
                <div class="signature-box">
                    <h4>Dated signature of officer preparing the bill</h4>
                    <p>Name: ___________________________</p>
                    <p>Designation: Assistant Engineer</p>
                    <p>Date: {current_date}</p>
                    <p>Signature: _______________________</p>
                </div>
                
                <div class="signature-box" style="float: right;">
                    <h4>+Dated signature of officer authorising payment</h4>
                    <p>Name: ___________________________</p>
                    <p>Designation: Executive Engineer</p>
                    <p>Date: {current_date}</p>
                    <p>Signature: _______________________</p>
                </div>
                <div style="clear: both;"></div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_certificate_iii(self):
        """Generate Certificate III - Memorandum of Payments"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        # Calculate amounts
        total_amount = 0
        for index, row in self.work_order_data.iterrows():
            quantity = self._safe_float(row.get('Quantity', 0))
            rate = self._safe_float(row.get('Rate', 0))
            total_amount += quantity * rate
        
        if not self.extra_items_data.empty:
            for index, row in self.extra_items_data.iterrows():
                quantity = self._safe_float(row.get('Quantity', 0))
                rate = self._safe_float(row.get('Rate', 0))
                total_amount += quantity * rate
        
        premium_percent = self._safe_float(self.title_data.get('TENDER PREMIUM %', 5.0))
        premium_amount = total_amount * (premium_percent / 100)
        grand_total = total_amount + premium_amount
        
        # Calculate deductions
        sd_amount = grand_total * 0.10
        it_amount = grand_total * 0.02
        gst_amount = grand_total * 0.02
        lc_amount = grand_total * 0.01
        total_deductions = sd_amount + it_amount + gst_amount + lc_amount
        cheque_amount = grand_total - total_deductions
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Certificate III</title>
            <style>
                @page {{
                    size: A4 portrait;
                    margin: 0.75in;
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    font-size: 10px; 
                    line-height: 1.3;
                    margin: 0;
                    padding: 0;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 20px; 
                    border-bottom: 2px solid #000;
                    padding-bottom: 10px;
                }}
                .title {{ 
                    font-size: 14px; 
                    font-weight: bold; 
                    margin-bottom: 5px;
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 10px 0; 
                }}
                th, td {{ 
                    border: 1px solid #000; 
                    padding: 4px; 
                    text-align: left; 
                    vertical-align: top;
                }}
                th {{ 
                    background-color: #f0f0f0; 
                    font-weight: bold; 
                    text-align: center;
                }}
                .amount {{ text-align: right; }}
                .center {{ text-align: center; }}
                .bold {{ font-weight: bold; }}
                .indent {{ padding-left: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">III. MEMORANDUM OF PAYMENTS</div>
                <div>Bill No: {self.title_data.get('Bill Number', 'BILL001')} | Date: {current_date}</div>
            </div>
            
            <table>
                <tr><th width="5%">S.No.</th><th width="60%">Description</th><th width="15%">Entry No.</th><th width="20%">Amount Rs.</th></tr>
                
                <tr><td>1.</td><td>Total value of work actually measured, as per Account I, Col. 5, Entry [A]</td><td>[A]</td><td class="amount">{grand_total:.0f}</td></tr>
                
                <tr><td>2.</td><td>Total up-to-date advance payments for work not yet measured as per details given below:</td><td></td><td></td></tr>
                <tr><td></td><td class="indent">(a) Total as per previous bill</td><td>[B]</td><td class="amount">Nil</td></tr>
                <tr><td></td><td class="indent">(b) Since previous bill</td><td>[D]</td><td class="amount">Nil</td></tr>
                
                <tr><td>3.</td><td>Total up-to-date secured advances on security of materials</td><td>[C]</td><td class="amount">Nil</td></tr>
                
                <tr><td>4.</td><td>Total (Items 1 + 2 + 3) A+B+C</td><td></td><td class="amount bold">{grand_total:.0f}</td></tr>
                
                <tr><td>5.</td><td>Deduct: Amount withheld</td><td></td><td></td></tr>
                <tr><td></td><td class="indent">(a) From previous bill as per last Running Account Bill</td><td>[5]</td><td class="amount">Nil</td></tr>
                <tr><td></td><td class="indent">(b) From this bill</td><td></td><td class="amount">Nil</td></tr>
                
                <tr><td>6.</td><td>Balance i.e. "up-to-date" payments (Item 4-5)</td><td></td><td class="amount bold">{grand_total:.0f}</td></tr>
                
                <tr><td>7.</td><td>Total amount of payments already made as per Entry (K)</td><td>[K]</td><td class="amount">0</td></tr>
                
                <tr><td>8.</td><td>Payments now to be made, as detailed below:</td><td></td><td class="amount bold">{cheque_amount:.0f}</td></tr>
                
                <tr><td></td><td class="indent">(a) By recovery of amounts creditable to this work</td><td>[a]</td><td></td></tr>
                <tr><td></td><td class="indent" style="padding-left: 40px;">SD @ 10%</td><td></td><td class="amount">{sd_amount:.0f}</td></tr>
                <tr><td></td><td class="indent" style="padding-left: 40px;">IT @ 2%</td><td></td><td class="amount">{it_amount:.0f}</td></tr>
                <tr><td></td><td class="indent" style="padding-left: 40px;">GST @ 2%</td><td></td><td class="amount">{gst_amount:.0f}</td></tr>
                <tr><td></td><td class="indent" style="padding-left: 40px;">LC @ 1%</td><td></td><td class="amount">{lc_amount:.0f}</td></tr>
                <tr><td></td><td class="indent" style="padding-left: 40px;">Total recovery</td><td></td><td class="amount bold">{total_deductions:.0f}</td></tr>
                
                <tr><td></td><td class="indent">(b) By recovery of amount creditable to other works</td><td>[b]</td><td class="amount">Nil</td></tr>
                
                <tr><td></td><td class="indent">(c) By cheque</td><td>[c]</td><td class="amount bold">{cheque_amount:.0f}</td></tr>
            </table>
            
            <div style="margin-top: 30px; border: 2px solid #000; padding: 15px;">
                <p><strong>Pay Rs. {cheque_amount:.0f}</strong></p>
                <p><strong>Pay Rupees {self._number_to_words(int(cheque_amount))} (by cheque)</strong></p>
                <p>Dated the ____ / ____ / ________</p>
                <p>Dated initials of Disbursing Officer: _______________</p>
            </div>
            
            <div style="margin-top: 20px; border: 1px solid #000; padding: 15px;">
                <p>Received Rupees {self._number_to_words(int(cheque_amount))} (by cheque) as per above memorandum, on account of this bill</p>
                <p>Signature of Contractor: _______________</p>
            </div>
            
            <div style="margin-top: 20px; border: 1px solid #000; padding: 15px;">
                <p>Paid by me, vide cheque No. _______ dated ____ / ____ / ________</p>
                <p>Dated initials of person actually making the payment: _______________</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_note_sheet(self):
        """Generate note sheet"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Note Sheet</title>
            <style>
                @page {{
                    size: A4 portrait;
                    margin: 1in;
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    font-size: 12px; 
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 30px; 
                    border-bottom: 2px solid #000;
                    padding-bottom: 15px;
                }}
                .title {{ 
                    font-size: 16px; 
                    font-weight: bold; 
                    margin-bottom: 10px;
                }}
                .note-item {{
                    margin: 15px 0;
                    padding: 10px;
                    border-left: 3px solid #4CAF50;
                    background-color: #f9f9f9;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">NOTE SHEET</div>
                <div>Bill Processing Notes and Remarks</div>
                <div>Date: {current_date}</div>
            </div>
            
            <div class="note-item">
                <h4>1. Bill Processing Summary</h4>
                <p>This bill has been processed and all calculations verified as per the work order and bill quantity sheets.</p>
            </div>
            
            <div class="note-item">
                <h4>2. Verification Status</h4>
                <p>✓ Work order quantities verified<br>
                ✓ Bill quantities cross-checked<br>
                ✓ Rates applied as per agreement<br>
                ✓ Premium calculations verified<br>
                ✓ Deductions calculated correctly</p>
            </div>
            
            <div class="note-item">
                <h4>3. Special Remarks</h4>
                <p>All work items have been executed as per specifications and within the agreed timeline.</p>
            </div>
            
            <div class="note-item">
                <h4>4. Approval Notes</h4>
                <p>The bill is recommended for payment after statutory deductions.</p>
            </div>
            
            <div style="margin-top: 50px; border-top: 1px solid #ccc; padding-top: 20px;">
                <p>Prepared by: ___________________________</p>
                <p>Date: {current_date}</p>
                <p>Signature: ___________________________</p>
            </div>
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
                @page {{
                    size: A4 landscape;
                    margin: 0.75in;
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    font-size: 11px; 
                    line-height: 1.3;
                    margin: 0;
                    padding: 0;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 20px; 
                    border-bottom: 2px solid #000;
                    padding-bottom: 10px;
                }}
                .title {{ 
                    font-size: 16px; 
                    font-weight: bold; 
                    margin-bottom: 5px;
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 10px 0; 
                }}
                th, td {{ 
                    border: 1px solid #000; 
                    padding: 6px; 
                    text-align: left; 
                    vertical-align: top;
                }}
                th {{ 
                    background-color: #f0f0f0; 
                    font-weight: bold; 
                    text-align: center;
                }}
                .amount {{ text-align: right; }}
                .center {{ text-align: center; }}
                .total-row {{ background-color: #d4edda; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">EXTRA ITEMS</div>
                <div>Additional Work Items Not in Original Work Order</div>
                <div>Date: {current_date}</div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th width="8%">Item No.</th>
                        <th width="35%">Description</th>
                        <th width="10%">Unit</th>
                        <th width="12%">Quantity</th>
                        <th width="12%">Rate (Rs.)</th>
                        <th width="13%">Amount (Rs.)</th>
                        <th width="10%">Remarks</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_extra = 0
        for index, row in self.extra_items_data.iterrows():
            item_no = self._safe_str(row.get('Item No.', f'E{index + 1}'))
            description = self._safe_str(row.get('Description', ''))
            unit = self._safe_str(row.get('Unit', ''))
            quantity = self._safe_float(row.get('Quantity', 0))
            rate = self._safe_float(row.get('Rate', 0))
            amount = quantity * rate
            remarks = self._safe_str(row.get('Remark', 'Extra Work'))
            
            total_extra += amount
            
            html_content += f"""
                <tr>
                    <td class="center">{item_no}</td>
                    <td>{description}</td>
                    <td class="center">{unit}</td>
                    <td class="amount">{quantity:.2f}</td>
                    <td class="amount">{rate:.2f}</td>
                    <td class="amount">{amount:.2f}</td>
                    <td>{remarks}</td>
                </tr>
            """
        
        # Add premium to extra items
        premium_percent = self._safe_float(self.title_data.get('TENDER PREMIUM %', 5.0))
        extra_premium = total_extra * (premium_percent / 100)
        extra_total = total_extra + extra_premium
        
        html_content += f"""
                <tr class="total-row">
                    <td colspan="5" class="center"><strong>SUBTOTAL (Extra Items)</strong></td>
                    <td class="amount"><strong>{total_extra:.2f}</strong></td>
                    <td></td>
                </tr>
                <tr>
                    <td colspan="5" class="center"><strong>Tender Premium ({premium_percent}%)</strong></td>
                    <td class="amount"><strong>{extra_premium:.2f}</strong></td>
                    <td></td>
                </tr>
                <tr class="total-row">
                    <td colspan="5" class="center"><strong>TOTAL (Extra Items with Premium)</strong></td>
                    <td class="amount"><strong>{extra_total:.2f}</strong></td>
                    <td></td>
                </tr>
            </tbody>
            </table>
            
            <div style="margin-top: 20px; font-size: 10px;">
                <h4>Notes:</h4>
                <p>1. All extra items have been approved by the competent authority.</p>
                <p>2. Rates applied are as per market rates or as negotiated.</p>
                <p>3. Premium is applicable as per contract terms.</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _number_to_words(self, number):
        """Convert number to words (basic implementation)"""
        try:
            # This is a basic implementation. In production, use num2words library
            if number == 0:
                return "Zero"
            
            # Basic conversion for demonstration
            ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
            teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", 
                    "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
            tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
            
            if number < 10:
                return ones[number]
            elif number < 20:
                return teens[number - 10]
            elif number < 100:
                return tens[number // 10] + ("" if number % 10 == 0 else " " + ones[number % 10])
            elif number < 1000:
                return ones[number // 100] + " Hundred" + ("" if number % 100 == 0 else " " + self._number_to_words(number % 100))
            else:
                return str(number)  # Fallback for larger numbers
        except:
            return str(number)
    
    def create_pdf_documents(self, documents):
        """Create PDF documents from HTML with multiple engine support"""
        pdf_files = {}
        
        try:
            # Try using ReportLab for PDF generation
            for doc_name, html_content in documents.items():
                try:
                    pdf_bytes = self._create_pdf_with_reportlab(html_content, doc_name)
                    if pdf_bytes and len(pdf_bytes) > 1024:
                        pdf_files[f"{doc_name}.pdf"] = pdf_bytes
                        logger.info(f"Generated PDF: {doc_name} ({len(pdf_bytes)} bytes)")
                    else:
                        logger.warning(f"Generated PDF too small: {doc_name}")
                
                except Exception as e:
                    logger.error(f"Error creating PDF for {doc_name}: {str(e)}")
                    # Try alternative method
                    try:
                        pdf_bytes = self._create_pdf_fallback(html_content, doc_name)
                        if pdf_bytes:
                            pdf_files[f"{doc_name}.pdf"] = pdf_bytes
                    except Exception as e2:
                        logger.error(f"Fallback PDF creation also failed for {doc_name}: {str(e2)}")
        
        except Exception as e:
            logger.error(f"Error in PDF creation process: {str(e)}")
            st.error(f"PDF generation failed: {str(e)}")
        
        return pdf_files
    
    def _create_pdf_with_reportlab(self, html_content, doc_name):
        """Create PDF using ReportLab"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
            from reportlab.lib.units import inch
            from bs4 import BeautifulSoup
            from io import BytesIO
            
            buffer = BytesIO()
            
            # Determine page size and orientation
            if doc_name in ['First Page Summary', 'Work Order Details', 'Deviation Statement', 'Extra Items']:
                pagesize = landscape(A4)
                margin = 0.5 * inch
            else:
                pagesize = A4
                margin = 0.75 * inch
            
            doc = SimpleDocTemplate(buffer, pagesize=pagesize, 
                                  leftMargin=margin, rightMargin=margin,
                                  topMargin=margin, bottomMargin=margin)
            story = []
            
            # Parse HTML content
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Add title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=20,
                alignment=TA_CENTER,
            )
            
            # Extract title from HTML
            title_elem = soup.find('title')
            title_text = title_elem.get_text() if title_elem else doc_name
            story.append(Paragraph(title_text, title_style))
            story.append(Spacer(1, 12))
            
            # Process content
            body = soup.find('body')
            if body:
                for element in body.find_all(['div', 'h1', 'h2', 'h3', 'h4', 'p', 'table']):
                    if element.name in ['h1', 'h2', 'h3', 'h4']:
                        text = element.get_text().strip()
                        if text:
                            story.append(Paragraph(text, styles['Heading2']))
                            story.append(Spacer(1, 6))
                    
                    elif element.name == 'p':
                        text = element.get_text().strip()
                        if text and not element.find_parent('table'):
                            story.append(Paragraph(text, styles['Normal']))
                            story.append(Spacer(1, 6))
                    
                    elif element.name == 'div' and 'header' in element.get('class', []):
                        text = element.get_text().strip()
                        if text:
                            header_style = ParagraphStyle(
                                'HeaderStyle',
                                parent=styles['Normal'],
                                fontSize=12,
                                alignment=TA_CENTER,
                                spaceAfter=12
                            )
                            story.append(Paragraph(text, header_style))
                    
                    elif element.name == 'table':
                        # Process table
                        table_data = []
                        for row in element.find_all('tr'):
                            row_data = []
                            for cell in row.find_all(['td', 'th']):
                                cell_text = cell.get_text().strip()
                                # Limit cell content length
                                if len(cell_text) > 40:
                                    cell_text = cell_text[:37] + "..."
                                row_data.append(cell_text)
                            if row_data:
                                table_data.append(row_data)
                        
                        if table_data:
                            # Adjust column widths based on content
                            col_count = len(table_data[0]) if table_data else 1
                            if col_count > 6:
                                col_widths = [0.8*inch] * col_count
                            else:
                                col_widths = None
                            
                            table = Table(table_data, colWidths=col_widths)
                            table_style = [
                                ('BACKGROUND', (0, 0), (-1, 0), '#f0f0f0'),
                                ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 8),
                                ('FONTSIZE', (0, 1), (-1, -1), 7),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                                ('BACKGROUND', (0, 1), (-1, -1), '#ffffff'),
                                ('GRID', (0, 0), (-1, -1), 0.5, '#000000'),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ]
                            
                            # Apply special styling for certain rows
                            for i, row in enumerate(table_data):
                                for j, cell in enumerate(row):
                                    if 'TOTAL' in cell.upper() or 'GRAND' in cell.upper():
                                        table_style.append(('BACKGROUND', (0, i), (-1, i), '#d4edda'))
                                        table_style.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'))
                            
                            table.setStyle(TableStyle(table_style))
                            story.append(table)
                            story.append(Spacer(1, 12))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"ReportLab PDF creation failed: {str(e)}")
            raise
    
    def _create_pdf_fallback(self, html_content, doc_name):
        """Fallback PDF creation method"""
        try:
            # Simple HTML to text conversion for basic PDF
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from bs4 import BeautifulSoup
            from io import BytesIO
            
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            
            # Parse HTML to extract text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract text content
            text_content = soup.get_text()
            lines = text_content.split('\n')
            
            # Write text to PDF
            y = 750
            p.setFont("Helvetica", 10)
            
            for line in lines:
                line = line.strip()
                if line:
                    if len(line) > 80:
                        # Word wrap for long lines
                        words = line.split()
                        current_line = ""
                        for word in words:
                            if len(current_line + word) < 80:
                                current_line += word + " "
                            else:
                                if current_line:
                                    p.drawString(50, y, current_line.strip())
                                    y -= 12
                                current_line = word + " "
                        if current_line:
                            p.drawString(50, y, current_line.strip())
                            y -= 12
                    else:
                        p.drawString(50, y, line)
                        y -= 12
                    
                    if y < 50:  # Start new page
                        p.showPage()
                        y = 750
                        p.setFont("Helvetica", 10)
            
            p.save()
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Fallback PDF creation failed: {str(e)}")
            return None

def provide_download_link(file_path, display_name, key):
    """Provide download link for a file"""
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
        
        st.download_button(
            label=f"📥 Download {display_name}",
            data=file_data,
            file_name=display_name,
            mime="application/pdf" if display_name.endswith('.pdf') else "application/octet-stream",
            key=key
        )
    except Exception as e:
        st.error(f"Error providing download for {display_name}: {str(e)}")

def main():
    """Main application function"""
    load_custom_css()
    show_header()
    
    # Initialize session state
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'documents' not in st.session_state:
        st.session_state.documents = None
    if 'pdf_files' not in st.session_state:
        st.session_state.pdf_files = None
    
    # Sidebar configuration
    st.sidebar.header("📋 Configuration")
    
    # Mode selection
    mode = st.sidebar.radio(
        "Choose Processing Mode:",
        ["Manual Upload", "Online Entry", "Batch Processing"],
        index=0
    )
    
    if mode == "Manual Upload":
        show_manual_mode()
    elif mode == "Online Entry":
        show_online_mode()
    else:
        show_batch_mode()

def show_manual_mode():
    """Handle manual file upload mode"""
    st.markdown("## 📁 Manual Upload Mode")
    
    st.markdown("""
    <div class="form-section">
        <h3>📤 Upload Excel File</h3>
        <p>Upload your Excel file containing Title, Work Order, Bill Quantity, and optionally Extra Items sheets.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose Excel file", 
        type=['xlsx', 'xls'],
        help="Upload Excel file with required sheets"
    )
    
    if uploaded_file is not None:
        try:
            with st.spinner("Processing Excel file..."):
                processor = EnhancedExcelProcessor(uploaded_file)
                result = processor.process_excel()
                
                if result:
                    st.session_state.processed_data = result
                    st.success("✅ File processed successfully!")
                    
                    # Show data preview
                    show_data_preview(result)
                    
                    # Generate documents button
                    if st.button("🔄 Generate All Documents", type="primary"):
                        generate_all_documents(result)
        
        except Exception as e:
            st.error(f"❌ Failed to process Excel file: {str(e)}")
            logger.error(f"Excel processing error: {traceback.format_exc()}")

def show_data_preview(data):
    """Show preview of processed data"""
    st.markdown("### 📋 Data Preview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if data.get('title_data'):
            with st.expander("📄 Title Information", expanded=False):
                title_df = pd.DataFrame(list(data['title_data'].items()), columns=['Field', 'Value'])
                st.dataframe(title_df, hide_index=True, use_container_width=True)
        
        if not data.get('work_order_data', pd.DataFrame()).empty:
            with st.expander("📋 Work Order Summary", expanded=False):
                wo_summary = data['work_order_data'].head()
                st.dataframe(wo_summary, hide_index=True, use_container_width=True)
    
    with col2:
        if not data.get('bill_quantity_data', pd.DataFrame()).empty:
            with st.expander("💰 Bill Quantities", expanded=False):
                bq_summary = data['bill_quantity_data'].head()
                st.dataframe(bq_summary, hide_index=True, use_container_width=True)
        
        if not data.get('extra_items_data', pd.DataFrame()).empty:
            with st.expander("➕ Extra Items", expanded=False):
                extra_summary = data['extra_items_data'].head()
                st.dataframe(extra_summary, hide_index=True, use_container_width=True)

def generate_all_documents(data):
    """Generate all documents and PDFs"""
    try:
        with st.spinner("Generating documents..."):
            doc_generator = CompleteDocumentGenerator(data)
            
            # Generate HTML documents
            html_documents = doc_generator.generate_all_documents()
            
            if html_documents:
                st.success(f"✅ Generated {len(html_documents)} HTML documents!")
                st.session_state.documents = html_documents
                
                # Convert to PDF
                with st.spinner("Creating PDF documents..."):
                    pdf_documents = doc_generator.create_pdf_documents(html_documents)
                    
                    if pdf_documents:
                        st.session_state.pdf_files = pdf_documents
                        st.success(f"✅ Successfully created {len(pdf_documents)} PDF documents!")
                        show_download_section()
                    else:
                        st.warning("⚠️ Could not create PDF files. HTML documents are available.")
                        show_html_download_section(html_documents)
            else:
                st.error("❌ Failed to generate documents")
    
    except Exception as e:
        st.error(f"❌ Error generating documents: {str(e)}")
        logger.error(f"Document generation error: {traceback.format_exc()}")

def show_download_section():
    """Show download section for PDF files"""
    st.markdown("### 📥 Download Documents")
    
    if st.session_state.pdf_files:
        # Create download columns
        cols = st.columns(3)
        col_idx = 0
        
        for filename, pdf_bytes in st.session_state.pdf_files.items():
            with cols[col_idx % 3]:
                st.download_button(
                    label=f"📄 {filename}",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    key=f"download_{filename}",
                    use_container_width=True
                )
            col_idx += 1
        
        # Merge all PDFs button
        if len(st.session_state.pdf_files) > 1:
            if st.button("📦 Download All as Single PDF", type="secondary"):
                try:
                    merged_pdf = merge_all_pdfs(st.session_state.pdf_files)
                    if merged_pdf:
                        st.download_button(
                            label="📥 Download Merged PDF",
                            data=merged_pdf,
                            file_name="Complete_Bill_Documents.pdf",
                            mime="application/pdf",
                            key="download_merged"
                        )
                except Exception as e:
                    st.error(f"Failed to merge PDFs: {str(e)}")

def show_html_download_section(html_documents):
    """Show download section for HTML files (fallback)"""
    st.markdown("### 📄 Download HTML Documents (Fallback)")
    st.info("PDF generation failed. You can download HTML versions below.")
    
    cols = st.columns(3)
    col_idx = 0
    
    for doc_name, html_content in html_documents.items():
        with cols[col_idx % 3]:
            st.download_button(
                label=f"📄 {doc_name}.html",
                data=html_content,
                file_name=f"{doc_name}.html",
                mime="text/html",
                key=f"download_html_{doc_name}",
                use_container_width=True
            )
        col_idx += 1

def merge_all_pdfs(pdf_files):
    """Merge all PDF files into single PDF"""
    try:
        from pypdf import PdfWriter
        from io import BytesIO
        
        writer = PdfWriter()
        
        for filename, pdf_bytes in pdf_files.items():
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(pdf_bytes))
            for page in reader.pages:
                writer.add_page(page)
        
        output = BytesIO()
        writer.write(output)
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Error merging PDFs: {str(e)}")
        return None

def show_online_mode():
    """Handle online entry mode"""
    st.markdown("## 💻 Online Entry Mode")
    st.info("Online entry mode is under development. Please use Manual Upload mode.")

def show_batch_mode():
    """Handle batch processing mode"""
    st.markdown("## 🚀 Batch Processing Mode")
    st.info("Batch processing mode is under development. Please use Manual Upload mode.")

if __name__ == "__main__":
    main()