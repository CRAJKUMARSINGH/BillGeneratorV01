import streamlit as st
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

# Add utils to path for imports
utils_path = Path(__file__).parent / "utils"
if str(utils_path) not in sys.path:
    sys.path.append(str(utils_path))

from utils.excel_processor import ExcelProcessor
from utils.document_generator import DocumentGenerator
from enhanced_document_generator_fixed import EnhancedDocumentGenerator
from utils.pdf_merger import PDFMerger
from batch_processor import HighPerformanceBatchProcessor, StreamlitBatchInterface
from optimized_pdf_converter import OptimizedPDFConverter

# Safe import for DataFrameSafetyUtils
try:
    from utils.dataframe_safety_utils import DataFrameSafetyUtils
except ImportError:
    # Fallback: Create minimal DataFrameSafetyUtils if not available
    class DataFrameSafetyUtils:
        @staticmethod
        def is_valid_dataframe(data):
            return isinstance(data, pd.DataFrame) and not data.empty
        
        @staticmethod
        def is_dataframe_or_data(data):
            if data is None:
                return False
            if isinstance(data, pd.DataFrame):
                return not data.empty
            return bool(data)
        
        @staticmethod
        def safe_dataframe_check(data, check_content=True):
            if data is None or not isinstance(data, pd.DataFrame):
                return False
            return not data.empty if check_content else True
        
        @staticmethod
        def get_safe_dataframe(data, default_columns=None):
            if isinstance(data, pd.DataFrame) and not data.empty:
                return data
            return pd.DataFrame(columns=list(default_columns) if default_columns else [])

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

    .header-professional {
        font-size: 1rem;
        text-align: center;
        color: #e8f5e9;
        opacity: 0.85;
        margin-bottom: 0.5rem;
        font-weight: 400;
        font-style: italic;
        letter-spacing: 0.8px;
    }

    .header-initiative {
        font-size: 0.9rem;
        text-align: center;
        color: #ffffff;
        opacity: 0.9;
        margin-bottom: 0;
        font-weight: 500;
        background: rgba(255,255,255,0.1);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.2);
        display: inline-block;
        margin: 0 auto;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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

    .mode-card.selected {
        border-color: #4CAF50;
        background: linear-gradient(135deg, #f8f9ff 0%, #e8f5e9 100%);
    }

    /* Upload card styling */
    .upload-card {
        background: #ffffff;
        border: 2px dashed #4CAF50;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }

    .upload-card:hover {
        border-color: #45a049;
        background: #f8fff8;
    }

    /* Progress indicator styles */
    .progress-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
    }

    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        flex: 1;
        position: relative;
    }

    .progress-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #e0e0e0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 0.9rem;
        z-index: 1;
        position: relative;
    }

    .progress-circle.completed {
        background: #28a745;
    }

    .progress-circle.current {
        background: #4CAF50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.3);
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

    /* Metrics styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-left: 4px solid #4CAF50;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
    }

    .metric-label {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    /* Enhanced work order table styles */
    .work-order-table-container {
        max-height: 600px;
        overflow-y: auto;
        border: 2px solid #e1e5e9;
        border-radius: 10px;
        background: #f8f9fa;
        margin: 20px 0;
    }
    .work-order-table {
        width: 100%;
        border-collapse: collapse;
        background: white;
    }
    .work-order-table th {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        color: white;
        padding: 12px 8px;
        text-align: left;
        font-weight: bold;
        position: sticky;
        top: 0;
        z-index: 10;
        border-bottom: 2px solid #45a049;
    }
    .work-order-table td {
        padding: 12px 8px;
        border-bottom: 1px solid #e2e8f0;
        vertical-align: top;
    }
    .work-order-table tr:hover {
        background-color: #f7fafc;
    }
    .item-row {
        border-left: 4px solid #4CAF50;
    }
    .item-description {
        font-weight: 500;
        color: #2d3748;
        line-height: 1.4;
    }
    .wo-qty-info {
        font-size: 0.85em;
        color: #718096;
        font-style: italic;
    }
    .rate-display {
        font-weight: bold;
        color: #2b6cb0;
        font-size: 1.05em;
    }
    .amount-cell {
        font-weight: bold;
        color: #28a745;
        font-size: 1.1em;
        text-align: right;
    }
    .qty-input-cell {
        width: 120px;
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

    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .mode-card {
            margin: 0.5rem 0;
            padding: 1.5rem;
        }

        .progress-container {
            flex-direction: column;
            gap: 1rem;
        }

        .form-section {
            padding: 1rem;
        }

        .header-title {
            font-size: 2rem;
        }

        .header-subtitle {
            font-size: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if 'mode' not in st.session_state:
        st.session_state.mode = None

    if 'step' not in st.session_state:
        st.session_state.step = 1

    if 'work_order_data' not in st.session_state:
        st.session_state.work_order_data = None

    if 'title_data' not in st.session_state:
        st.session_state.title_data = None

    if 'bill_quantities' not in st.session_state:
        st.session_state.bill_quantities = {}

    if 'extra_items' not in st.session_state:
        st.session_state.extra_items = []

    if 'generated_documents' not in st.session_state:
        st.session_state.generated_documents = []

def show_header():
    """Display the application header with government logo and professional design"""
    # Load and encode the government logo
    logo_path = Path(__file__).parent / "static" / "images" / "government_logo.svg"
    
    try:
        if logo_path.exists():
            with open(logo_path, "r", encoding="utf-8") as f:
                logo_svg = f.read()
        else:
            # Fallback to default icon if logo not found
            logo_svg = None
    except Exception:
        logo_svg = None
    
    st.markdown("""
    <div class="header-container">
        <div style="text-align: center;">
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                <div style="margin-right: 1rem;">
                    {logo_element}
                </div>
                <div style="font-size: 4rem; color: white;">🏛️</div>
            </div>
            <div class="header-title">Enhanced Infrastructure Billing System</div>
            <div class="header-subtitle">Professional Document Generation & Compliance Solution</div>
            <div class="header-professional">Advanced Multi-Format Document Processing with Election Commission Compliance</div>
            <div style="margin-top: 1.5rem;">
                <div class="header-initiative">
                    An Initiative by Mrs. Premlata Jain, Additional Administrative Officer, PWD, Udaipur
                </div>
            </div>
        </div>
    </div>
    """.format(
        logo_element=f'<div style="width: 60px; height: 60px;">{logo_svg}</div>' if logo_svg else ''
    ), unsafe_allow_html=True)

def show_progress_indicator(current_step: int, total_steps: int = 4):
    """Show progress indicator for online mode"""
    steps = ["Upload Work Order", "Fill Bill Quantities", "Add Extra Items", "Generate Documents"]

    progress_html = '<div class="progress-container">'

    for i, step_name in enumerate(steps[:total_steps], 1):
        if i < current_step:
            status = "completed"
        elif i == current_step:
            status = "current"
        else:
            status = ""

        progress_html += f"""
        <div class="progress-step {status}">
            <div class="progress-circle {status}">
                {"✓" if status == "completed" else str(i)}
            </div>
            <div class="progress-label">{step_name}</div>
        </div>
        """

    progress_html += '</div>'
    st.markdown(progress_html, unsafe_allow_html=True)

def show_mode_selection():
    """Display mode selection interface"""
    st.markdown("## Choose Your Workflow")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📁 Excel Upload Mode", key="excel_mode"):
            st.session_state.mode = "excel"
            st.session_state.step = 1
            st.rerun()

        st.markdown("""
        <div class="mode-card">
            <div style="font-size: 3rem; margin-bottom: 1rem; color: #667eea;">📁</div>
            <div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem; color: #2c3e50;">Excel Upload Mode</div>
            <div style="color: #7f8c8d; font-size: 0.9rem; line-height: 1.4;">
                Upload a complete Excel file with Title Sheet, Work Order, 
                and Bill Quantity data. Perfect for prepared datasets.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("💻 Online Entry Mode", key="online_mode"):
            st.session_state.mode = "online"
            st.session_state.step = 1
            st.rerun()

        st.markdown("""
        <div class="mode-card">
            <div style="font-size: 3rem; margin-bottom: 1rem; color: #667eea;">💻</div>
            <div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem; color: #2c3e50;">Online Entry Mode</div>
            <div style="color: #7f8c8d; font-size: 0.9rem; line-height: 1.4;">
                Enter bill quantities directly through web forms. 
                Upload work order and fill quantities step by step.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        if st.button("🚀 Batch Processing Mode", key="batch_mode"):
            st.session_state.mode = "batch"
            st.session_state.step = 1
            st.rerun()

        st.markdown("""
        <div class="mode-card">
            <div style="font-size: 3rem; margin-bottom: 1rem; color: #ff6b35;">🚀</div>
            <div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem; color: #2c3e50;">Batch Processing Mode</div>
            <div style="color: #7f8c8d; font-size: 0.9rem; line-height: 1.4;">
                Process multiple Excel files simultaneously. 
                High-performance processing with quality validation.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Mode comparison
    st.markdown("---")
    st.markdown("### 📊 Mode Comparison")

    comparison_df = pd.DataFrame({
        "Feature": [
            "Data Entry Method",
            "Setup Time", 
            "Flexibility",
            "Best For",
            "Technical Skill Required",
            "Performance"
        ],
        "Excel Upload Mode": [
            "Pre-prepared Excel files",
            "Quick (if Excel ready)",
            "Limited to Excel structure", 
            "Bulk data, recurring bills",
            "Excel knowledge",
            "Medium"
        ],
        "Online Entry Mode": [
            "Web forms and inputs",
            "Medium (step-by-step)",
            "High customization",
            "One-time bills, custom items",
            "Basic computer skills",
            "Medium"
        ],
        "Batch Processing Mode": [
            "Multiple Excel files",
            "Very Quick (automated)",
            "High (bulk processing)",
            "Large-scale operations",
            "Basic computer skills",
            "High"
        ]
    })

    st.dataframe(comparison_df, hide_index=True, use_container_width=True)

    # Feature highlights
    st.markdown("---")
    st.markdown("### ⭐ Key Features")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-radius: 10px; margin: 0.5rem 0; border: 1px solid #4CAF50;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem; color: #2E7D32;">📄</div>
            <h4 style="color: #1B5E20; margin-bottom: 0.5rem;">Multi-Format Output</h4>
            <p style="color: #2E7D32; font-size: 0.85rem; margin: 0;">PDF, HTML, Excel & more</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-radius: 10px; margin: 0.5rem 0; border: 1px solid #2196F3;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem; color: #1976D2;">⚡</div>
            <h4 style="color: #0D47A1; margin-bottom: 0.5rem;">Real-time Processing</h4>
            <p style="color: #1976D2; font-size: 0.85rem; margin: 0;">Instant calculations & updates</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); border-radius: 10px; margin: 0.5rem 0; border: 1px solid #FF9800;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem; color: #F57C00;">🔒</div>
            <h4 style="color: #E65100; margin-bottom: 0.5rem;">Compliance Ready</h4>
            <p style="color: #F57C00; font-size: 0.85rem; margin: 0;">Election Commission standards</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #fce4ec 0%, #f8bbd9 100%); border-radius: 10px; margin: 0.5rem 0; border: 1px solid #E91E63;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem; color: #C2185B;">📱</div>
            <h4 style="color: #880E4F; margin-bottom: 0.5rem;">Mobile Ready</h4>
            <p style="color: #C2185B; font-size: 0.85rem; margin: 0;">Works on any device</p>
        </div>
        """, unsafe_allow_html=True)

def show_excel_mode():
    """Handle Excel upload mode - existing functionality"""
    st.markdown("## 📁 Excel Upload Mode")
    show_progress_indicator(1, 3)

    st.markdown("""
    <div class="form-section">
        <h3>📤 Upload Excel File</h3>
        <p>Upload your Excel file containing Title Sheet, Work Order, and Bill Quantity data.</p>
    </div>
    """, unsafe_allow_html=True)

    # File upload
    uploaded_file = st.file_uploader(
        "Choose Excel file", 
        type=['xlsx', 'xls'],
        help="Upload Excel file with required sheets: Title, Work Order, Bill Quantity"
    )

    if uploaded_file is not None:
        try:
            with st.spinner("Processing Excel file..."):
                # Process Excel file using existing ExcelProcessor
                processor = ExcelProcessor(uploaded_file)

                # Process the Excel file directly
                result = processor.process_excel()

                if result and isinstance(result, dict):
                    st.success("✅ Excel file processed successfully!")

                    # Store processed data
                    st.session_state.title_data = result.get('title_data')
                    st.session_state.work_order_data = result.get('work_order_data')
                    st.session_state.bill_quantity_data = result.get('bill_quantity_data')
                    st.session_state.extra_items_data = result.get('extra_items_data', pd.DataFrame())

                    # Show data preview
                    show_data_preview(result)

                    # Generate documents
                    if st.button("🔄 Generate Documents", key="generate_excel"):
                        generate_documents_excel_mode(result)


        except Exception as e:
            st.error(f"❌ Failed to process Excel file: {str(e)}")
            logger.error(f"Excel processing error: {traceback.format_exc()}")

def show_data_preview(data: Dict):
    """Show preview of processed Excel data with editing capability"""
    st.markdown("### 📋 Data Preview & Modification")

    # Title data preview and editing
    if data.get('title_data'):
        with st.expander("📄 Title Information (Click to Edit)", expanded=True):
            st.markdown("**✏️ Edit project information below:**")
            
            # Create editable form for title data
            title_data = data['title_data'].copy()
            
            # Common title fields with user-friendly labels
            title_fields = {
                'Name of Work ;-': 'Project Name',
                'Agreement No.': 'Contract/Agreement Number', 
                'Reference to work order or Agreement :': 'Work Order Reference',
                'Name of Contractor or supplier :': 'Contractor Name',
                'Bill Number': 'Bill Number',
                'Running or Final': 'Bill Type (Running/Final)',
                'TENDER PREMIUM %': 'Tender Premium Percentage',
                'WORK ORDER AMOUNT RS.': 'Work Order Amount (Rs.)',
                'Date of written order to commence work :': 'Work Commencement Date',
                'St. date of Start :': 'Start Date',
                'St. date of completion :': 'Completion Date',
                'Date of actual completion of work :': 'Actual Completion Date',
                'Date of measurement :': 'Measurement Date'
            }
            
            # Display current values from Excel and allow editing
            col1, col2 = st.columns(2)
            
            modified_title_data = {}
            
            # Process known fields first
            field_count = 0
            for excel_key, friendly_label in title_fields.items():
                if excel_key in title_data:
                    current_value = str(title_data[excel_key]) if title_data[excel_key] is not None else ""
                    
                    # Alternate between columns
                    target_col = col1 if field_count % 2 == 0 else col2
                    
                    with target_col:
                        # Show original Excel value as help text
                        new_value = st.text_input(
                            friendly_label,
                            value=current_value,
                            help=f"Original Excel value: {current_value}",
                            key=f"title_{excel_key}"
                        )
                        modified_title_data[excel_key] = new_value
                    
                    field_count += 1
            
            # Handle any additional fields from Excel not in the predefined list
            other_fields = {k: v for k, v in title_data.items() if k not in title_fields}
            if other_fields:
                st.markdown("**📋 Additional Fields from Excel:**")
                col3, col4 = st.columns(2)
                
                additional_count = 0
                for key, value in other_fields.items():
                    current_value = str(value) if value is not None else ""
                    target_col = col3 if additional_count % 2 == 0 else col4
                    
                    with target_col:
                        new_value = st.text_input(
                            key,
                            value=current_value,
                            help=f"Additional field from Excel",
                            key=f"title_extra_{key}"
                        )
                        modified_title_data[key] = new_value
                    additional_count += 1
            
            # Update session state with modified data
            st.session_state.title_data = modified_title_data
            
            # Show preview of modified data
            if st.checkbox("📊 Show Current Title Data Summary", key="show_title_summary"):
                summary_df = pd.DataFrame([
                    {"Field": k, "Value": v} for k, v in modified_title_data.items() if v
                ])
                st.dataframe(summary_df, hide_index=True, use_container_width=True)

    # Work order preview
    work_order_data = data.get('work_order_data')
    if work_order_data is not None:
        # Safe DataFrame check
        if isinstance(work_order_data, pd.DataFrame):
            if not work_order_data.empty:
                with st.expander("📋 Work Order Summary"):
                    st.dataframe(work_order_data, hide_index=True, use_container_width=True)
        elif isinstance(work_order_data, (list, dict)) and len(work_order_data) > 0:
            with st.expander("📋 Work Order Summary"):
                work_order_df = pd.DataFrame(work_order_data)
                st.dataframe(work_order_df, hide_index=True, use_container_width=True)

    # Bill quantity preview
    bill_quantity_data = data.get('bill_quantity_data')
    if bill_quantity_data is not None:
        # Safe DataFrame check
        if isinstance(bill_quantity_data, pd.DataFrame):
            if not bill_quantity_data.empty:
                with st.expander("💰 Bill Quantities"):
                    st.dataframe(bill_quantity_data, hide_index=True, use_container_width=True)
        elif isinstance(bill_quantity_data, (list, dict)) and len(bill_quantity_data) > 0:
            with st.expander("💰 Bill Quantities"):
                bill_df = pd.DataFrame(bill_quantity_data)
                st.dataframe(bill_df, hide_index=True, use_container_width=True)

    # Extra items preview
    extra_items_data = data.get('extra_items_data')
    if extra_items_data is not None:
        # Safe DataFrame check
        if isinstance(extra_items_data, pd.DataFrame):
            if not extra_items_data.empty:
                with st.expander("➕ Extra Items"):
                    st.dataframe(extra_items_data, hide_index=True, use_container_width=True)
        elif isinstance(extra_items_data, (list, dict)) and len(extra_items_data) > 0:
            with st.expander("➕ Extra Items"):
                extra_df = pd.DataFrame(extra_items_data)
                st.dataframe(extra_df, hide_index=True, use_container_width=True)

def generate_documents_excel_mode(data: Dict):
    """Generate documents using processed Excel data with modified title information"""
    try:
        with st.spinner("Generating documents..."):
            # Use modified title data from session state if available
            if hasattr(st.session_state, 'title_data') and st.session_state.title_data:
                data['title_data'] = st.session_state.title_data
                st.info("📝 Using your modified title information for document generation")
            
            # Initialize EnhancedDocumentGenerator for robust HTML→PDF
            doc_generator = EnhancedDocumentGenerator(data)

            # Generate HTML documents
            html_documents = doc_generator.generate_all_documents()
            
            if html_documents:
                st.success(f"✅ Generated {len(html_documents)} HTML documents!")
                
                # Convert HTML to PDF
                with st.spinner("Converting to PDF..."):
                    pdf_documents = doc_generator.create_pdf_documents(html_documents)
                
                if pdf_documents:
                    st.success(f"✅ Successfully created {len(pdf_documents)} PDF documents!")
                    
                    # Save PDF files to temporary directory and collect file paths
                    generated_files = []
                    temp_dir = tempfile.mkdtemp()
                    
                    for filename, pdf_bytes in pdf_documents.items():
                        file_path = os.path.join(temp_dir, filename)
                        with open(file_path, 'wb') as f:
                            f.write(pdf_bytes)
                        generated_files.append(file_path)
                    
                    # Show individual download links
                    st.markdown("### 📥 Individual Downloads")
                    for i, file_path in enumerate(generated_files):
                        file_name = Path(file_path).name
                        provide_download_link(file_path, file_name, f"download_{i}")
                    
                    # Merge PDFs if multiple files
                    if len(generated_files) > 1:
                        try:
                            merger = PDFMerger()
                            merged_pdf_bytes = merger.merge_pdfs(pdf_documents)
                            if merged_pdf_bytes:
                                # Save merged PDF to temporary file
                                merged_file_path = os.path.join(temp_dir, "Merged_Bill_Documents.pdf")
                                with open(merged_file_path, 'wb') as f:
                                    f.write(merged_pdf_bytes)
                                st.success("📄 Documents merged successfully!")
                                provide_download_link(merged_file_path, "Merged_Bill_Documents.pdf", "merged_download")
                        except Exception as e:
                            st.warning(f"Could not merge PDFs: {str(e)}")
                            st.info("Individual downloads are still available above.")
                else:
                    st.error("❌ Failed to create PDF documents")
            else:
                st.error("❌ Failed to generate documents")

    except Exception as e:
        st.error(f"❌ Error generating documents: {str(e)}")
        logger.error(f"Document generation error: {traceback.format_exc()}")

def show_online_mode():
    """Handle online entry mode with step-by-step workflow"""
    st.markdown("## 💻 Online Entry Mode")

    # Show progress
    show_progress_indicator(st.session_state.step)

    if st.session_state.step == 1:
        show_work_order_upload()
    elif st.session_state.step == 2:
        show_bill_quantity_entry()
    elif st.session_state.step == 3:
        show_extra_items_entry()
    elif st.session_state.step == 4:
        show_document_generation()

def show_batch_mode():
    """Handle batch processing mode"""
    st.markdown("## 🚀 Batch Processing Mode")
    
    # Initialize batch interface
    if 'batch_interface' not in st.session_state:
        st.session_state.batch_interface = StreamlitBatchInterface()
    
    # Show batch processing interface
    st.session_state.batch_interface.show_batch_interface()

def show_work_order_upload():
    """Step 1: Upload work order and title information"""
    st.markdown("""
    <div class="form-section">
        <h3>📤 Step 1: Upload Work Order</h3>
        <p>Upload your work order Excel file or enter title information manually.</p>
    </div>
    """, unsafe_allow_html=True)

    # Option to upload work order or enter manually
    entry_method = st.radio(
        "Choose data entry method:",
        ["Upload Excel File", "Enter Manually"],
        horizontal=True
    )

    if entry_method == "Upload Excel File":
        uploaded_file = st.file_uploader(
            "Upload Work Order Excel File",
            type=['xlsx', 'xls'],
            help="Excel file containing Title sheet and Work Order data"
        )

        if uploaded_file is not None:
            try:
                with st.spinner("Processing work order..."):
                    processor = ExcelProcessor(uploaded_file)

                    # Process only title and work order sheets
                    result = processor.process_excel()

                    if result and isinstance(result, dict):
                        st.success("✅ Work order processed successfully!")

                        # Store data
                        st.session_state.title_data = result.get('title_data')
                        st.session_state.work_order_data = result.get('work_order_data')

                        # Show title editing interface
                        show_title_editing_interface(result.get('title_data', {}))

                        # Show preview
                        show_work_order_preview()

                        # Next step button
                        if st.button("➡️ Proceed to Bill Quantities", key="next_to_bill"):
                            st.session_state.step = 2
                            st.rerun()


            except Exception as e:
                st.error(f"❌ Failed to process file: {str(e)}")

    else:  # Manual entry
        show_manual_title_entry()

def show_title_editing_interface(title_data: Dict):
    """Show title editing interface for online mode"""
    if not title_data:
        return
        
    with st.expander("📝 Edit Project Information", expanded=False):
        st.markdown("**Modify the project information extracted from your Excel file:**")
        
        # Key fields for editing
        key_fields = {
            'Name of Work ;-': 'Project Name',
            'Agreement No.': 'Contract Number', 
            'Name of Contractor or supplier :': 'Contractor Name',
            'Bill Number': 'Bill Number',
            'Running or Final': 'Bill Type'
        }
        
        modified_data = {}
        col1, col2 = st.columns(2)
        
        field_count = 0
        for excel_key, label in key_fields.items():
            if excel_key in title_data:
                current_value = str(title_data[excel_key]) if title_data[excel_key] is not None else ""
                target_col = col1 if field_count % 2 == 0 else col2
                
                with target_col:
                    new_value = st.text_input(
                        label,
                        value=current_value,
                        key=f"online_title_{excel_key}"
                    )
                    modified_data[excel_key] = new_value
                field_count += 1
        
        # Update session state with any modifications
        if modified_data:
            if not hasattr(st.session_state, 'title_data'):
                st.session_state.title_data = {}
            st.session_state.title_data.update(modified_data)

def show_manual_title_entry():
    """Manual entry form for title and work order information"""
    st.markdown("### ✏️ Manual Entry")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📄 Title Information")

        title_data = {
            'project_name': st.text_input("Project Name", key="manual_project"),
            'contract_number': st.text_input("Contract Number", key="manual_contract"),
            'contractor_name': st.text_input("Contractor Name", key="manual_contractor"),
            'work_order': st.text_input("Work Order", key="manual_wo"),
            'bill_number': st.text_input("Bill Number", key="manual_bill_no"),
            'period_from': st.date_input("Period From", key="manual_from"),
            'period_to': st.date_input("Period To", key="manual_to")
        }

    with col2:
        st.markdown("#### 📋 Work Items")

        # Dynamic work items entry
        if 'work_items' not in st.session_state:
            st.session_state.work_items = [{"item_description": "", "unit": "", "rate": 0.0}]

        work_items = []
        for i, item in enumerate(st.session_state.work_items):
            st.markdown(f"**Item {i+1}:**")
            col_desc, col_unit, col_rate = st.columns([3, 1, 1])

            with col_desc:
                description = st.text_input("Description", value=item["item_description"], key=f"desc_{i}")
            with col_unit:
                unit = st.text_input("Unit", value=item["unit"], key=f"unit_{i}")
            with col_rate:
                rate = st.number_input("Rate", value=item["rate"], min_value=0.0, key=f"rate_{i}")

            work_items.append({
                "item_description": description,
                "unit": unit,
                "rate": rate
            })

        # Add/Remove buttons
        col_add, col_remove = st.columns(2)
        with col_add:
            if st.button("➕ Add Item"):
                st.session_state.work_items.append({"item_description": "", "unit": "", "rate": 0.0})
                st.rerun()

        with col_remove:
            if len(st.session_state.work_items) > 1 and st.button("➖ Remove Item"):
                st.session_state.work_items.pop()
                st.rerun()

    # Validate and proceed
    if st.button("💾 Save and Continue", key="save_manual"):
        # Validate required fields
        if not title_data['project_name'] or not title_data['work_order']:
            st.error("⚠️ Please fill in at least Project Name and Work Order")
            return

        # Store data
        st.session_state.title_data = title_data
        st.session_state.work_order_data = [item for item in work_items if item['item_description']]

        st.success("✅ Data saved successfully!")

        # Show preview
        show_work_order_preview()

        # Next step
        if st.button("➡️ Proceed to Bill Quantities", key="next_manual"):
            st.session_state.step = 2
            st.rerun()

def show_work_order_preview():
    """Show preview of work order data"""
    st.markdown("### 📋 Preview")

    if st.session_state.title_data:
        with st.expander("📄 Title Information", expanded=True):
            title_df = pd.DataFrame([st.session_state.title_data])
            st.dataframe(title_df, hide_index=True, use_container_width=True)

    if st.session_state.work_order_data is not None:
        # Safe check for DataFrame or list/dict
        if isinstance(st.session_state.work_order_data, pd.DataFrame):
            if not st.session_state.work_order_data.empty:
                with st.expander("📋 Work Items", expanded=True):
                    st.dataframe(st.session_state.work_order_data, hide_index=True, use_container_width=True)
        elif isinstance(st.session_state.work_order_data, (list, dict)) and len(st.session_state.work_order_data) > 0:
            with st.expander("📋 Work Items", expanded=True):
                work_df = pd.DataFrame(st.session_state.work_order_data)
                st.dataframe(work_df, hide_index=True, use_container_width=True)

def show_bill_quantity_entry():
    """Step 2: Enter bill quantities for work items - Scrollable table format"""
    st.markdown("""
    <div class="form-section">
        <h3>💰 Step 2: Fill Bill Quantities</h3>
        <p>Review work order items with rates below. Scroll through all items and fill quantities for your bill.</p>
    </div>
    """, unsafe_allow_html=True)

    # Safe check for work order data
    if st.session_state.work_order_data is None:
        st.error("⚠️ No work order data found. Please complete Step 1 first.")
        if st.button("⬅️ Go Back to Step 1"):
            st.session_state.step = 1
            st.rerun()
        return
    
    # Additional check for empty DataFrame
    if isinstance(st.session_state.work_order_data, pd.DataFrame) and st.session_state.work_order_data.empty:
        st.error("⚠️ Work order data is empty. Please complete Step 1 first.")
        if st.button("⬅️ Go Back to Step 1"):
            st.session_state.step = 1
            st.rerun()
        return
    
    # Check for empty list/dict
    if isinstance(st.session_state.work_order_data, (list, dict)) and len(st.session_state.work_order_data) == 0:
        st.error("⚠️ Work order data is empty. Please complete Step 1 first.")
        if st.button("⬅️ Go Back to Step 1"):
            st.session_state.step = 1
            st.rerun()
        return

    # Initialize quantities if not exists
    if 'bill_quantities' not in st.session_state:
        st.session_state.bill_quantities = {}

    # Convert work order data to DataFrame if it's a list or dict
    if isinstance(st.session_state.work_order_data, (list, dict)):
        work_df = pd.DataFrame(st.session_state.work_order_data)
    elif hasattr(st.session_state.work_order_data, 'copy'):
        work_df = st.session_state.work_order_data.copy()
    else:
        work_df = pd.DataFrame()

    # Removed filter to display all items including zero-rate items
    # This was causing issues where users couldn't enter quantities for zero-rate items
    pass

    # Calculate progress
    total_items = len(work_df) if hasattr(work_df, '__len__') else 0
    filled_items = len([k for k, v in st.session_state.bill_quantities.items() if v > 0])
    progress_percentage = (filled_items / total_items * 100) if total_items > 0 else 0
    
    # Progress indicator
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 15px; border-radius: 10px; margin: 15px 0; text-align: center;">
        📊 <strong>Bill Entry Progress:</strong> {filled_items}/{total_items} items filled ({progress_percentage:.1f}% complete)
    </div>
    """, unsafe_allow_html=True)

    # Enhanced scrollable work order items table
    st.markdown("### 📋 Work Order Items & Rates")
    st.markdown("**Instructions:** Scroll through the items below and enter quantities for billing.")
    
    total_amount = 0.0
    bill_data = []
    
    # Custom CSS for enhanced table styling
    st.markdown("""
    <style>
    .work-order-table-container {
        max-height: 600px;
        overflow-y: auto;
        border: 2px solid #e1e5e9;
        border-radius: 10px;
        background: #f8f9fa;
        margin: 20px 0;
    }
    .work-order-table {
        width: 100%;
        border-collapse: collapse;
        background: white;
    }
    .work-order-table th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 8px;
        text-align: left;
        font-weight: bold;
        position: sticky;
        top: 0;
        z-index: 10;
        border-bottom: 2px solid #5a67d8;
    }
    .work-order-table td {
        padding: 12px 8px;
        border-bottom: 1px solid #e2e8f0;
        vertical-align: top;
    }
    .work-order-table tr:hover {
        background-color: #f7fafc;
    }
    .item-row {
        border-left: 4px solid #667eea;
    }
    .item-description {
        font-weight: 500;
        color: #2d3748;
        line-height: 1.4;
    }
    .wo-qty-info {
        font-size: 0.85em;
        color: #718096;
        font-style: italic;
    }
    .rate-display {
        font-weight: bold;
        color: #2b6cb0;
        font-size: 1.05em;
    }
    .amount-cell {
        font-weight: bold;
        color: #28a745;
        font-size: 1.1em;
        text-align: right;
    }
    .qty-input-cell {
        width: 120px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create scrollable table
    st.markdown('<div class="work-order-table-container">', unsafe_allow_html=True)
    
    # Table header
    st.markdown("""
    <table class="work-order-table">
        <thead>
            <tr>
                <th style="width: 8%;">Item No.</th>
                <th style="width: 35%;">Description & WO Qty</th>
                <th style="width: 8%;">Unit</th>
                <th style="width: 12%;">Rate (₹)</th>
                <th style="width: 15%;">Bill Quantity</th>
                <th style="width: 12%;">Amount (₹)</th>
            </tr>
        </thead>
        <tbody>
    """, unsafe_allow_html=True)
    
    # Process each work order item in table rows
    # Ensure work_df is a DataFrame before iterating
    if not isinstance(work_df, pd.DataFrame):
        work_df = pd.DataFrame(work_df)
    
    for idx, (i, row) in enumerate(work_df.iterrows()):
        # Extract item details safely - FIXED to prevent 'str' object has no attribute 'get' error
        # First try to get 'Item No.', if not found try 'Item', if neither found use default
        item_no_value = row.get('Item No.')
        if item_no_value is None:
            item_no_value = row.get('Item', f'Item_{idx + 1}')
        item_no = '' if item_no_value is None else str(item_no_value)
        if item_no.strip().lower() in ['nan', 'none']:
            item_no = ''
        
        # First try to get 'Description', if not found try 'item_description', if neither found use default
        description_value = row.get('Description')
        if description_value is None:
            description_value = row.get('item_description', 'No description')
        description = '' if description_value is None else str(description_value)
        if description.strip().lower() in ['nan', 'none']:
            description = ''
        
        # First try to get 'Unit', if not found try 'unit', if neither found use default
        unit_value = row.get('Unit')
        if unit_value is None:
            unit_value = row.get('unit', 'Unit')
        unit = '' if unit_value is None else str(unit_value)
        if unit.strip().lower() in ['nan', 'none']:
            unit = ''
        
        # Safely convert to float
        # Parse rate safely; treat NaN/None/blank as missing (display blank)
        rate_display_str = ''
        try:
            rate_value = row.get('Rate', row.get('rate', row.get('RATE', 0)))
            if rate_value is None or (isinstance(rate_value, str) and rate_value.strip().lower() in ['nan', 'none', '']) or (hasattr(pd, 'isna') and pd.isna(rate_value)):
                rate = 0.0
                rate_display_str = ''
            else:
                rate = float(rate_value)
                rate_display_str = f"₹{rate:,.2f}"
        except (ValueError, TypeError):
            rate = 0.0
            rate_display_str = ''
            
        # Parse WO quantity safely; treat NaN/None/blank as missing (display blank)
        wo_qty_display_str = ''
        try:
            wo_qty_value = row.get('Quantity Since', row.get('Quantity', 0))
            if wo_qty_value is None or (isinstance(wo_qty_value, str) and wo_qty_value.strip().lower() in ['nan', 'none', '']) or (hasattr(pd, 'isna') and pd.isna(wo_qty_value)):
                work_order_qty = 0.0
                wo_qty_display_str = ''
            else:
                work_order_qty = float(wo_qty_value)
                wo_qty_display_str = f"{work_order_qty:,.2f}"
        except (ValueError, TypeError):
            work_order_qty = 0.0
            wo_qty_display_str = ''

        # Discipline: Only positive-rate rows should display/use WO quantity or accept Bill Qty
        is_positive_rate = (rate > 0.0)
        if not is_positive_rate:
            work_order_qty = 0.0
            wo_qty_display_str = ''
        
        # Quantity input key
        qty_key = f"bill_qty_{idx}_{item_no}"
        
        # Current quantity from session state
        current_qty = st.session_state.bill_quantities.get(qty_key, 0.0)
        
        # Create table row with embedded Streamlit components
        st.markdown(f"""
        <tr class="item-row">
            <td><strong>{item_no}</strong></td>
            <td>
                <div class="item-description">{description}</div>
                <div class="wo-qty-info">{('📋 WO Qty: ' + wo_qty_display_str + ' ' + unit) if is_positive_rate and wo_qty_display_str else ''}</div>
            </td>
            <td><strong>{unit}</strong></td>
            <td class="rate-display">{rate_display_str}</td>
            <td class="qty-input-cell">
        """, unsafe_allow_html=True)
        
        # Quantity input using Streamlit number_input in table cell
        col_qty, col_amount = st.columns([1, 1])
        
        with col_qty:
            bill_qty = st.number_input(
                label="Quantity",
                min_value=0.0,
                value=current_qty,
                step=0.01,
                key=qty_key,
                label_visibility="collapsed",
                help=f"Enter quantity to bill for {description[:30]}..." if is_positive_rate else "Bill quantity allowed only when rate > 0",
                disabled=not is_positive_rate
            )
            # Update session state
            st.session_state.bill_quantities[qty_key] = bill_qty
        
        # Calculate amount
        amount = bill_qty * rate
        total_amount += amount
        
        with col_amount:
            if bill_qty > 0:
                st.markdown(f'<div class="amount-cell">₹{amount:,.2f}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="amount-cell">₹0.00</div>', unsafe_allow_html=True)
        
        st.markdown("</td></tr>", unsafe_allow_html=True)
        
        # Add to bill data if quantity > 0
        if bill_qty > 0:
            bill_data.append({
                'item_no': item_no,
                'description': description,
                'unit': unit,
                'rate': rate,
                'work_order_qty': work_order_qty,
                'bill_qty': bill_qty,
                'amount': amount
            })
    
    # Close table
    st.markdown("""
        </tbody>
    </table>
    </div>
    """)
    
    # Summary section with enhanced styling
    st.markdown("### 📊 Bill Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        items_with_qty = len(bill_data)
        st.metric("Items to Bill", items_with_qty, help="Number of items with quantities entered")
    
    with col2:
        total_qty = sum(item['bill_qty'] for item in bill_data)
        st.metric("Total Quantity", f"{total_qty:,.2f}", help="Sum of all bill quantities")
    
    with col3:
        st.metric("Total Amount", f"₹{total_amount:,.2f}", help="Total bill amount", delta=None)

    # Show detailed bill table if there are items with quantities
    if bill_data:
        st.markdown("### 📄 Items to be Billed")
        
        # Create display dataframe
        display_df = pd.DataFrame(bill_data)
        display_df = display_df.rename(columns={
            'item_no': 'Item No.',
            'description': 'Description',
            'unit': 'Unit',
            'work_order_qty': 'WO Qty',
            'bill_qty': 'Bill Qty',
            'rate': 'Rate (₹)',
            'amount': 'Amount (₹)'
        })
        
        # Format numeric columns
        display_df['Rate (₹)'] = display_df['Rate (₹)'].apply(lambda x: f"₹{x:,.2f}")
        display_df['Amount (₹)'] = display_df['Amount (₹)'].apply(lambda x: f"₹{x:,.2f}")
        display_df['WO Qty'] = display_df['WO Qty'].apply(lambda x: f"{x:,.2f}")
        display_df['Bill Qty'] = display_df['Bill Qty'].apply(lambda x: f"{x:,.2f}")
        
        st.dataframe(display_df, hide_index=True, use_container_width=True)
        
        # Store processed bill data
        st.session_state.processed_bill_data = bill_data
        
        # Success message
        st.success(f"✅ Ready to proceed! {len(bill_data)} items prepared for billing.")
    else:
        st.info("💡 Enter quantities for work items above to see the bill summary.")

    # Summary section
    st.markdown("### 📊 Bill Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        items_with_qty = len(bill_data)
        st.metric("Items to Bill", items_with_qty)
    
    with col2:
        total_qty = sum(item['bill_qty'] for item in bill_data)
        st.metric("Total Quantity", f"{total_qty:,.2f}")
    
    with col3:
        st.metric("Total Amount", f"₹{total_amount:,.2f}")

    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Work Order", key="back_to_wo_2"):
            st.session_state.step = 1
            st.rerun()
    
    with col2:
        # Check if at least one item has a quantity entered, regardless of rate value
        has_quantities = any(item.get('bill_qty', 0) > 0 for item in bill_data)
        if has_quantities:
            if st.button("➡️ Proceed to Extra Items", key="proceed_to_extra_2"):
                st.session_state.step = 3
                st.rerun()
        else:
            st.warning("⚠️ Please enter quantities for at least one item to proceed")

def show_extra_items_entry():
    """Step 3: Add extra items (optional)"""
    st.markdown("""
    <div class="form-section">
        <h3>➕ Step 3: Add Extra Items (Optional)</h3>
        <p>Add any additional items not included in the work order.</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize extra items if not exists
    if 'extra_items_list' not in st.session_state:
        st.session_state.extra_items_list = []

    # Extra items entry form
    st.markdown("### ➕ Add Extra Items")

    with st.expander("Add New Extra Item", expanded=len(st.session_state.extra_items_list) == 0):
        col1, col2 = st.columns(2)

        with col1:
            extra_description = st.text_input("Item Description", key="extra_desc")
            extra_unit = st.text_input("Unit", key="extra_unit")

        with col2:
            extra_rate = st.number_input("Rate (₹)", min_value=0.0, key="extra_rate")
            extra_quantity = st.number_input("Quantity", min_value=0.0, key="extra_qty")

        if st.button("➕ Add Extra Item"):
            if extra_description and extra_quantity > 0:
                extra_item = {
                    'description': extra_description,
                    'unit': extra_unit,
                    'rate': extra_rate,
                    'quantity': extra_quantity,
                    'amount': extra_rate * extra_quantity
                }
                st.session_state.extra_items_list.append(extra_item)
                st.success(f"✅ Added: {extra_description}")
                st.rerun()
            else:
                st.error("⚠️ Please provide description and quantity")

    # Show current extra items
    if st.session_state.extra_items_list:
        st.markdown("### 📋 Current Extra Items")

        extra_df = pd.DataFrame(st.session_state.extra_items_list)

        # Format for display
        display_df = extra_df.copy()
        display_df['rate'] = display_df['rate'].apply(lambda x: f"₹{x:,.2f}")
        display_df['amount'] = display_df['amount'].apply(lambda x: f"₹{x:,.2f}")
        display_df['quantity'] = display_df['quantity'].apply(lambda x: f"{x:,.2f}")

        st.dataframe(display_df, hide_index=True, use_container_width=True)

        # Remove item functionality
        if len(st.session_state.extra_items_list) > 0:
            item_to_remove = st.selectbox(
                "Remove Item:",
                options=range(len(st.session_state.extra_items_list)),
                format_func=lambda x: st.session_state.extra_items_list[x]['description']
            )

            if st.button("🗑️ Remove Selected Item"):
                st.session_state.extra_items_list.pop(item_to_remove)
                st.success("Item removed!")
                st.rerun()

        # Extra items summary
        total_extra_amount = sum(item['amount'] for item in st.session_state.extra_items_list)
        st.markdown(f"**Total Extra Items Amount: ₹{total_extra_amount:,.2f}**")

    # Store extra items data
    st.session_state.extra_items = st.session_state.extra_items_list

    # Navigation
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Back to Bill Quantities"):
            st.session_state.step = 2
            st.rerun()

    with col2:
        if st.button("➡️ Generate Documents"):
            st.session_state.step = 4
            st.rerun()

def show_document_generation():
    """Step 4: Generate and download documents"""
    st.markdown("""
    <div class="form-section">
        <h3>📄 Step 4: Generate Documents</h3>
        <p>Review your data and generate the bill documents.</p>
    </div>
    """, unsafe_allow_html=True)

    # Final summary
    st.markdown("### 📊 Final Summary")

    # Calculate totals using structured processed data
    processed_items = st.session_state.get('processed_bill_data', []) or []
    extra_items_list = st.session_state.get('extra_items', []) or []

    try:
        bill_total = sum(float(item.get('amount', 0) or 0) for item in processed_items)
    except Exception:
        bill_total = 0.0
    try:
        extra_total = sum(float(item.get('amount', 0) or 0) for item in extra_items_list)
    except Exception:
        extra_total = 0.0
    grand_total = bill_total + extra_total

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len([item for item in st.session_state.bill_quantities.values() if isinstance(item, dict) and item.get('quantity', 0) > 0])}</div>
            <div class="metric-label">Bill Items</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.extra_items)}</div>
            <div class="metric-label">Extra Items</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{bill_total:,.2f}</div>
            <div class="metric-label">Bill Amount</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{grand_total:,.2f}</div>
            <div class="metric-label">Grand Total</div>
        </div>
        """, unsafe_allow_html=True)

    # Data preview tabs
    tab1, tab2, tab3 = st.tabs(["📄 Title Info", "💰 Bill Items", "➕ Extra Items"])

    with tab1:
        if st.session_state.title_data:
            title_df = pd.DataFrame([st.session_state.title_data])
            st.dataframe(title_df, hide_index=True, use_container_width=True)

    with tab2:
        bill_items = processed_items
        if bill_items:
            bill_df = pd.DataFrame(bill_items)
            st.dataframe(bill_df, hide_index=True, use_container_width=True)

    with tab3:
        if st.session_state.extra_items:
            extra_df = pd.DataFrame(st.session_state.extra_items)
            st.dataframe(extra_df, hide_index=True, use_container_width=True)

    # Document generation
    st.markdown("### 🔄 Generate Documents")

    if st.button("📄 Generate All Documents", type="primary"):
        generate_documents_online_mode()

    # Navigation
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Back to Extra Items"):
            st.session_state.step = 3
            st.rerun()

    with col2:
        if st.button("🔄 Start New Bill"):
            # Reset session state
            for key in ['mode', 'step', 'work_order_data', 'title_data', 'bill_quantities', 'extra_items']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

def generate_documents_online_mode():
    """Generate documents using online mode data"""
    try:
        with st.spinner("Generating documents..."):
            # Prepare data in the format expected by DocumentGenerator

            # Use processed items prepared in Step 2 (each is a dict with item_no, description, unit, bill_qty, rate, amount)
            processed_items = st.session_state.get('processed_bill_data', []) or []
            # Map to DocumentGenerator-friendly bill quantity structure
            # FIXED to prevent 'str' object has no attribute 'get' error
            bill_quantity_items = []
            for it in processed_items:
                # Safely extract values to prevent AttributeError
                item_no = it.get('item_no', '')
                description = it.get('description', '')
                unit = it.get('unit', '')
                bill_qty = it.get('bill_qty', 0)
                rate = it.get('rate', 0)
                amount = it.get('amount', 0)
                
                bill_quantity_items.append({
                    'Item No.': item_no,
                    'Description': description,
                    'Unit': unit,
                    'Quantity': bill_qty,
                    'Rate': rate,
                    'Amount': amount
                })
            
            # Convert list data to DataFrames as expected by DocumentGenerator
            if isinstance(st.session_state.get('work_order_data'), pd.DataFrame):
                work_order_df = st.session_state['work_order_data'].copy()
            elif st.session_state.get('work_order_data') is not None:
                work_order_df = pd.DataFrame(st.session_state['work_order_data'])
            else:
                work_order_df = pd.DataFrame()

            bill_quantity_df = pd.DataFrame(bill_quantity_items) if bill_quantity_items else pd.DataFrame()

            # CRITICAL: Reflect entered quantities into work_order_df so PDFs show correct amounts
            # DocumentGenerator uses work_order_data ('Quantity Since' * 'Rate') for main pages
            try:
                if not work_order_df.empty and len(bill_quantity_items) > 0:
                    # Normalize key column names for matching
                    wo_item_col = 'Item No.' if 'Item No.' in work_order_df.columns else ('Item' if 'Item' in work_order_df.columns else None)
                    if wo_item_col is not None:
                        # Build a quick lookup from bill items by item number
                        bq_lookup = {}
                        for bi in bill_quantity_items:
                            key = bi.get('Item No.', bi.get('Item', ''))
                            bq_lookup[str(key)] = bi
                        # Update rows in work_order_df
                        def _apply_billed(row):
                            key = str(row.get(wo_item_col, ''))
                            bi = bq_lookup.get(key)
                            if bi:
                                row['Quantity Since'] = bi.get('Quantity', 0)
                                row['Quantity Upto'] = bi.get('Quantity', 0)
                                # Prefer non-zero rate from bill item, else keep existing
                                rate_val = bi.get('Rate', row.get('Rate', 0))
                                row['Rate'] = rate_val
                            return row
                        work_order_df = work_order_df.apply(_apply_billed, axis=1)
                    else:
                        # If no item number column, best-effort alignment by index
                        for idx, bi in enumerate(bill_quantity_items):
                            if idx < len(work_order_df):
                                work_order_df.at[idx, 'Quantity Since'] = bi.get('Quantity', 0)
                                work_order_df.at[idx, 'Quantity Upto'] = bi.get('Quantity', 0)
                                work_order_df.at[idx, 'Rate'] = bi.get('Rate', work_order_df.at[idx, 'Rate'] if 'Rate' in work_order_df.columns else 0)
            except Exception:
                # If alignment fails, continue with original DataFrame; bill quantities will still be used in other docs
                pass
            # Normalize extra items columns
            # FIXED to prevent 'str' object has no attribute 'get' error
            extra_items_list = st.session_state.get('extra_items', []) or []
            extra_items_norm = []
            for ex in extra_items_list:
                # Safely extract values to prevent AttributeError
                item_no_value = ex.get('item_no')
                if item_no_value is None:
                    item_no_value = ex.get('Item No.', '')
                item_no = item_no_value
                
                description_value = ex.get('description')
                if description_value is None:
                    description_value = ex.get('Description', '')
                description = description_value
                
                unit_value = ex.get('unit')
                if unit_value is None:
                    unit_value = ex.get('Unit', '')
                unit = unit_value
                
                quantity_value = ex.get('quantity')
                if quantity_value is None:
                    quantity_value = ex.get('Quantity', 0)
                quantity = quantity_value
                
                rate_value = ex.get('rate')
                if rate_value is None:
                    rate_value = ex.get('Rate', 0)
                rate = rate_value
                
                amount_value = ex.get('amount')
                if amount_value is None:
                    amount_value = ex.get('Amount', 0)
                amount = amount_value
                
                extra_items_norm.append({
                    'Item No.': item_no,
                    'Description': description,
                    'Unit': unit,
                    'Quantity': quantity,
                    'Rate': rate,
                    'Amount': amount
                })
            extra_items_df = pd.DataFrame(extra_items_norm) if extra_items_norm else pd.DataFrame()

            # Prepare data in DocumentGenerator format with proper DataFrames
            online_data = {
                'title_data': st.session_state.title_data,
                'work_order_data': work_order_df,
                'bill_quantity_data': bill_quantity_df,
                'extra_items_data': extra_items_df
            }
            
            # Initialize EnhancedDocumentGenerator for robust HTML→PDF
            doc_generator = EnhancedDocumentGenerator(online_data)

            # Generate HTML documents
            html_documents = doc_generator.generate_all_documents()
            
            if html_documents:
                st.success(f"✅ Generated {len(html_documents)} HTML documents!")
                
                # Convert HTML to PDF
                with st.spinner("Converting to PDF..."):
                    pdf_documents = doc_generator.create_pdf_documents(html_documents)
                
                if pdf_documents:
                    st.success(f"✅ Successfully created {len(pdf_documents)} PDF documents!")
                    
                    # Save PDF files to temporary directory and collect file paths
                    generated_files = []
                    temp_dir = tempfile.mkdtemp()
                    
                    for filename, pdf_bytes in pdf_documents.items():
                        file_path = os.path.join(temp_dir, filename)
                        with open(file_path, 'wb') as f:
                            f.write(pdf_bytes)
                        generated_files.append(file_path)
                    
                    # Store generated files
                    st.session_state.generated_documents = generated_files

                    # Show individual download links
                    st.markdown("### 📥 Individual Downloads")
                    for i, file_path in enumerate(generated_files):
                        file_name = Path(file_path).name
                        provide_download_link(file_path, file_name, f"online_download_{i}")
                    
                    # Merge PDFs if multiple files
                    if len(generated_files) > 1:
                        try:
                            merger = PDFMerger()
                            merged_pdf_bytes = merger.merge_pdfs(pdf_documents)
                            if merged_pdf_bytes:
                                # Save merged PDF to temporary file
                                merged_file_path = os.path.join(temp_dir, "Merged_Bill_Documents.pdf")
                                with open(merged_file_path, 'wb') as f:
                                    f.write(merged_pdf_bytes)
                                st.success("📄 Documents merged successfully!")
                                provide_download_link(merged_file_path, "Merged_Bill_Documents.pdf", "online_merged")
                        except Exception as e:
                            st.warning(f"Could not merge PDFs: {str(e)}")
                            st.info("Individual downloads are still available above.")
                    else:
                        provide_download_link(generated_files[0], "Bill_Document.pdf", "online_single")

                    # Success message with summary
                    # FIXED to prevent 'str' object has no attribute 'get' error
                    total_bill_amount = 0
                    for item in bill_quantity_items:
                        amount_value = item.get('Amount', 0)
                        try:
                            total_bill_amount += float(amount_value or 0)
                        except (ValueError, TypeError):
                            pass
                    
                    total_extra_amount = 0
                    for item in extra_items_norm:
                        # Safely get amount value
                        amount_value = item.get('Amount')
                        if amount_value is None:
                            amount_value = item.get('amount', 0)
                        try:
                            total_extra_amount += float(amount_value or 0)
                        except (ValueError, TypeError):
                            pass
                    
                    total_amount = total_bill_amount + total_extra_amount

                    st.balloons()
                    st.success(f"""
                    🎉 **Documents Generated Successfully!**

                    - **Total Items:** {len(bill_quantity_items) + len(st.session_state.extra_items)}
                    - **Total Amount:** ₹{total_amount:,.2f}
                    - **Generated Files:** {len(generated_files)}
                    """)
                else:
                    st.error("❌ Failed to create PDF documents")
            else:
                st.error("❌ Failed to generate documents")

    except Exception as e:
        st.error(f"❌ Error generating documents: {str(e)}")
        logger.error(f"Online document generation error: {traceback.format_exc()}")

def provide_download_link(file_path: str, file_name: str, key: str = ""):
    """Provide download link for generated file"""
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                file_data = file.read()

            st.download_button(
                label=f"📥 Download {file_name}",
                data=file_data,
                file_name=file_name,
                mime="application/pdf" if file_name.endswith('.pdf') else "application/octet-stream",
                key=key
            )
        else:
            st.error(f"File not found: {file_name}")

    except Exception as e:
        st.error(f"Error providing download for {file_name}: {str(e)}")

def show_sidebar():
    """Show sidebar with application information and controls"""
    with st.sidebar:
        st.markdown("## 🔧 Application Controls")

        # Mode indicator
        if st.session_state.mode:
            mode_name = "Excel Upload" if st.session_state.mode == "excel" else "Online Entry"
            st.info(f"**Current Mode:** {mode_name}")

            if st.session_state.mode == "online":
                st.info(f"**Current Step:** {st.session_state.step}/4")

        # Reset button
        if st.button("🔄 Reset Application"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("---")

        # Application info
        st.markdown("""
        ## 📋 About This App

        **Enhanced Bill Generator** provides two modes for creating infrastructure billing documents:

        ### 📁 Excel Upload Mode
        - Upload complete Excel files
        - Automatic data processing
        - Quick generation for prepared data

        ### 💻 Online Entry Mode  
        - Step-by-step web forms
        - Real-time calculations
        - Custom item additions

        ### 🔧 Features
        - Professional PDF generation
        - Multiple document types
        - Data validation
        - Mobile responsive design
        """)

        st.markdown("---")

        # Performance metrics (if available)
        if hasattr(st.session_state, 'generated_documents'):
            st.markdown("## 📊 Session Stats")
            st.metric("Documents Generated", len(st.session_state.generated_documents))

        # Help section
        with st.expander("❓ Need Help?"):
            st.markdown("""
            **Excel Mode Requirements:**
            - Title sheet with project info
            - Work Order sheet with items
            - Bill Quantity sheet (optional)

            **Online Mode Steps:**
            1. Upload work order or enter manually
            2. Fill bill quantities for each item
            3. Add extra items (optional)
            4. Generate and download documents

            **Supported Formats:**
            - Input: Excel (.xlsx, .xls)
            - Output: PDF documents
            """)

def main():
    """Main application function"""
    # Load custom CSS
    load_custom_css()

    # Initialize session state
    initialize_session_state()

    # Show header
    show_header()

    # Show sidebar
    show_sidebar()

    # Main content area
    if st.session_state.mode is None:
        show_mode_selection()
    elif st.session_state.mode == "excel":
        show_excel_mode()
    elif st.session_state.mode == "online":
        show_online_mode()
    elif st.session_state.mode == "batch":
        show_batch_mode()

# Error handling wrapper
def run_app():
    """Run the application with error handling"""
    try:
        main()
    except Exception as e:
        st.error(f"❌ Application Error: {str(e)}")
        logger.error(f"Application error: {traceback.format_exc()}")

        # Provide reset option
        if st.button("🔄 Reset Application"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    run_app()
