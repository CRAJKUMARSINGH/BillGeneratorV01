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

# Add utils to path for imports
utils_path = Path(__file__).parent / "utils"
if str(utils_path) not in sys.path:
    sys.path.append(str(utils_path))

from utils.excel_processor import ExcelProcessor
from utils.document_generator import DocumentGenerator
from utils.pdf_merger import PDFMerger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Enhanced Bill Generator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
def load_custom_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 0;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }

    .mode-card.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, #f8f9ff 0%, #e8ebff 100%);
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
        background: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
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
        border-bottom: 2px solid #667eea;
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
        border-left: 4px solid #667eea;
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

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
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
    """Display the application header"""
    st.markdown("""
    <div class="main-header">
        <h1>📋 Enhanced Bill Generator</h1>
        <p>Professional infrastructure billing with Excel upload and online entry capabilities</p>
    </div>
    """, unsafe_allow_html=True)

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

    col1, col2 = st.columns(2)

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

    # Mode comparison
    st.markdown("---")
    st.markdown("### 📊 Mode Comparison")

    comparison_df = pd.DataFrame({
        "Feature": [
            "Data Entry Method",
            "Setup Time", 
            "Flexibility",
            "Best For",
            "Technical Skill Required"
        ],
        "Excel Upload Mode": [
            "Pre-prepared Excel files",
            "Quick (if Excel ready)",
            "Limited to Excel structure", 
            "Bulk data, recurring bills",
            "Excel knowledge"
        ],
        "Online Entry Mode": [
            "Web forms and inputs",
            "Medium (step-by-step)",
            "High customization",
            "One-time bills, custom items",
            "Basic computer skills"
        ]
    })

    st.dataframe(comparison_df, hide_index=True, use_container_width=True)

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
    """Show preview of processed Excel data"""
    st.markdown("### 📋 Data Preview")

    # Title data preview
    if data.get('title_data'):
        with st.expander("📄 Title Information", expanded=True):
            title_df = pd.DataFrame([data['title_data']])
            st.dataframe(title_df, hide_index=True, use_container_width=True)

    # Work order preview
    work_order_data = data.get('work_order_data')
    if work_order_data is not None and (isinstance(work_order_data, (list, dict)) or not work_order_data.empty if hasattr(work_order_data, 'empty') else True):
        with st.expander("📋 Work Order Summary"):
            if isinstance(work_order_data, pd.DataFrame):
                work_order_df = work_order_data
            else:
                work_order_df = pd.DataFrame(work_order_data)
            st.dataframe(work_order_df, hide_index=True, use_container_width=True)

    # Bill quantity preview
    bill_quantity_data = data.get('bill_quantity_data')
    if bill_quantity_data is not None and (isinstance(bill_quantity_data, (list, dict)) or not bill_quantity_data.empty if hasattr(bill_quantity_data, 'empty') else True):
        with st.expander("💰 Bill Quantities"):
            if isinstance(bill_quantity_data, pd.DataFrame):
                bill_df = bill_quantity_data
            else:
                bill_df = pd.DataFrame(bill_quantity_data)
            st.dataframe(bill_df, hide_index=True, use_container_width=True)

    # Extra items preview
    extra_items_data = data.get('extra_items_data')
    if extra_items_data is not None and (isinstance(extra_items_data, (list, dict)) or not extra_items_data.empty if hasattr(extra_items_data, 'empty') else True):
        with st.expander("➕ Extra Items"):
            if isinstance(extra_items_data, pd.DataFrame):
                extra_df = extra_items_data
            else:
                extra_df = pd.DataFrame(extra_items_data)
            st.dataframe(extra_df, hide_index=True, use_container_width=True)

def generate_documents_excel_mode(data: Dict):
    """Generate documents using processed Excel data"""
    try:
        with st.spinner("Generating documents..."):
            # Initialize DocumentGenerator with data
            doc_generator = DocumentGenerator(data)

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

    if st.session_state.work_order_data:
        with st.expander("📋 Work Items", expanded=True):
            work_df = pd.DataFrame(st.session_state.work_order_data)
            st.dataframe(work_df, hide_index=True, use_container_width=True)

def show_bill_quantity_entry():
    """Step 2: Enter bill quantities for work items"""
    st.markdown("""
    <div class="form-section">
        <h3>💰 Step 2: Enter Bill Quantities</h3>
        <p>Enter quantities for each work item in your order.</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.work_order_data:
        st.error("⚠️ No work order data found. Please complete Step 1 first.")
        if st.button("⬅️ Go Back to Step 1"):
            st.session_state.step = 1
            st.rerun()
        return

    # Initialize quantities if not exists
    if 'quantities' not in st.session_state:
        st.session_state.quantities = {}

    # Bill quantity entry form
    st.markdown("### 📊 Enter Quantities")

    total_amount = 0.0
    bill_data = []

    for i, item in enumerate(st.session_state.work_order_data):
        st.markdown(f"#### Item {i+1}: {item.get('item_description', 'Unknown Item')}")

        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

        with col1:
            st.markdown(f"**Description:** {item.get('item_description', 'N/A')}")

        with col2:
            st.markdown(f"**Unit:** {item.get('unit', 'N/A')}")

        with col3:
            st.markdown(f"**Rate:** ₹{item.get('rate', 0):,.2f}")

        with col4:
            quantity_key = f"qty_{i}"
            quantity = st.number_input(
                "Quantity",
                min_value=0.0,
                value=st.session_state.quantities.get(quantity_key, 0.0),
                step=0.01,
                key=quantity_key,
                help=f"Enter quantity for {item.get('item_description', 'item')}"
            )
            st.session_state.quantities[quantity_key] = quantity

        # Calculate amount
        rate = item.get('rate', 0)
        amount = quantity * rate
        total_amount += amount

        # Add to bill data
        bill_data.append({
            'item_description': item.get('item_description'),
            'unit': item.get('unit'),
            'rate': rate,
            'quantity': quantity,
            'amount': amount
        })

        # Show amount for this item
        if quantity > 0:
            st.markdown(f"💰 **Amount:** ₹{amount:,.2f}")

        st.markdown("---")

    # Summary
    st.markdown("### 📈 Bill Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_items = len([item for item in bill_data if item['quantity'] > 0])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_items}</div>
            <div class="metric-label">Items with Quantities</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        total_qty = sum(item['quantity'] for item in bill_data)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_qty:,.2f}</div>
            <div class="metric-label">Total Quantity</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{total_amount:,.2f}</div>
            <div class="metric-label">Total Amount</div>
        </div>
        """, unsafe_allow_html=True)

    # Store bill quantities
    st.session_state.bill_quantities = bill_data

    # Show detailed table
    if total_amount > 0:
        st.markdown("### 📋 Detailed Bill")
        bill_df = pd.DataFrame(bill_data)
        bill_df = bill_df[bill_df['quantity'] > 0]  # Show only items with quantities

        # Format the dataframe for display
        if len(bill_df) > 0:
            display_df = bill_df.copy()
            display_df['rate'] = display_df['rate'].apply(lambda x: f"₹{x:,.2f}")
            display_df['amount'] = display_df['amount'].apply(lambda x: f"₹{x:,.2f}")
            display_df['quantity'] = display_df['quantity'].apply(lambda x: f"{x:,.2f}")

            st.dataframe(display_df, hide_index=True, use_container_width=True)

    # Navigation buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Back to Work Order"):
            st.session_state.step = 1
            st.rerun()

    with col2:
        if total_amount > 0:
            if st.button("➡️ Proceed to Extra Items"):
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

    # Calculate totals
    bill_total = sum(item.get('amount', 0) for item in st.session_state.bill_quantities if item.get('quantity', 0) > 0)
    extra_total = sum(item.get('amount', 0) for item in st.session_state.extra_items)
    grand_total = bill_total + extra_total

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len([item for item in st.session_state.bill_quantities if item.get('quantity', 0) > 0])}</div>
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
        bill_items = [item for item in st.session_state.bill_quantities if item.get('quantity', 0) > 0]
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

            # Filter bill quantities to include only items with quantities > 0
            bill_quantity_data = [
                item for item in st.session_state.bill_quantities 
                if item.get('quantity', 0) > 0
            ]

            # Prepare data in DocumentGenerator format
            online_data = {
                'title_data': st.session_state.title_data,
                'work_order_data': st.session_state.work_order_data,
                'bill_quantity_data': bill_quantity_data,
                'extra_items_data': st.session_state.extra_items
            }
            
            # Initialize DocumentGenerator
            doc_generator = DocumentGenerator(online_data)

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
                    total_amount = sum(item.get('amount', 0) for item in bill_quantity_data) + sum(item.get('amount', 0) for item in st.session_state.extra_items)

                    st.balloons()
                    st.success(f"""
                    🎉 **Documents Generated Successfully!**

                    - **Total Items:** {len(bill_quantity_data) + len(st.session_state.extra_items)}
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

def provide_download_link(file_path: str, file_name: str, key: str = None):
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
