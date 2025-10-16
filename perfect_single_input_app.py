#!/usr/bin/env python3
"""
Perfect Single Input Bill Generator
Streamlined for optimal single file processing
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import base64
import tempfile
import os
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Add utils to path for imports
utils_path = Path(__file__).parent / "utils"
if str(utils_path) not in sys.path:
    sys.path.append(str(utils_path))

from utils.excel_processor import ExcelProcessor
from enhanced_document_generator_fixed import DocumentGenerator
from utils.pdf_merger import PDFMerger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Perfect Single Input Bill Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
def load_custom_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main > div {
        padding: 1.5rem;
    }

    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);
    }

    .header-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: center;
    }

    .header-subtitle {
        font-size: 1.1rem;
        text-align: center;
        opacity: 0.9;
        margin-bottom: 0;
    }

    /* Card styling */
    .feature-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }

    .feature-card:hover {
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.15);
        transform: translateY(-2px);
    }

    .feature-card h3 {
        color: #0ea5e9;
        margin-top: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Upload area */
    .upload-area {
        background: #f8fafc;
        border: 2px dashed #0ea5e9;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }

    .upload-area:hover {
        background: #f0f9ff;
        border-color: #0284c7;
    }

    .upload-icon {
        font-size: 3rem;
        color: #0ea5e9;
        margin-bottom: 1rem;
    }

    /* Status indicators */
    .status-success {
        background: #dcfce7;
        color: #166534;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }

    .status-error {
        background: #fee2e2;
        color: #991b1b;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }

    .status-info {
        background: #dbeafe;
        color: #1e40af;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
    }

    .stButton > button.secondary {
        background: linear-gradient(135deg, #64748b 0%, #94a3b8 100%);
    }

    /* Download section */
    .download-section {
        background: #f1f5f9;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .download-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem;
        border-bottom: 1px solid #e2e8f0;
    }

    .download-item:last-child {
        border-bottom: none;
    }

    /* Data preview */
    .data-preview {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .header-title {
            font-size: 1.5rem;
        }
        
        .feature-card {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    session_vars = [
        'uploaded_file',
        'processed_data',
        'html_documents',
        'pdf_documents',
        'doc_documents',
        'generated_files',
        'temp_dir'
    ]
    
    for var in session_vars:
        if var not in st.session_state:
            st.session_state[var] = None

def show_header():
    """Display the application header"""
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">📄 Perfect Single Input Bill Generator</h1>
        <p class="header-subtitle">Streamlined for optimal single file processing with all document formats</p>
    </div>
    """, unsafe_allow_html=True)

def process_excel_file(uploaded_file) -> Optional[Dict]:
    """Process uploaded Excel file with enhanced error handling"""
    try:
        with st.spinner("🔄 Processing Excel file..."):
            # Process Excel file using existing ExcelProcessor
            processor = ExcelProcessor(uploaded_file)
            result = processor.process_excel()
            
            if result and isinstance(result, dict):
                st.success("✅ Excel file processed successfully!")
                return result
            else:
                st.error("❌ Failed to process Excel file: Invalid data structure")
                return None
                
    except Exception as e:
        st.error(f"❌ Error processing Excel file: {str(e)}")
        logger.error(f"Excel processing error: {traceback.format_exc()}")
        return None

def generate_documents(data: Dict) -> bool:
    """Generate all document formats (HTML, PDF, DOC)"""
    try:
        with st.spinner("🔄 Generating all document formats..."):
            # Initialize DocumentGenerator
            doc_generator = DocumentGenerator(data)
            
            # Generate HTML documents
            st.info("📄 Generating HTML documents...")
            html_documents = doc_generator.generate_all_documents()
            
            if not html_documents:
                st.error("❌ Failed to generate HTML documents")
                return False
            
            st.success(f"✅ Generated {len(html_documents)} HTML documents!")
            st.session_state.html_documents = html_documents
            
            # Generate PDF documents
            st.info("🖨️ Converting HTML to PDF...")
            pdf_documents = doc_generator.create_pdf_documents(html_documents)
            
            if not pdf_documents:
                st.error("❌ Failed to generate PDF documents")
                return False
            
            st.success(f"✅ Generated {len(pdf_documents)} PDF documents!")
            st.session_state.pdf_documents = pdf_documents
            
            # Generate DOC documents (using the enhanced generator's method)
            st.info("📝 Generating DOC documents...")
            try:
                # Use the generate_all_formats_and_zip method to get DOC documents
                all_formats_result = doc_generator.generate_all_formats_and_zip()
                doc_documents = all_formats_result.get('doc_documents', {})
                
                if doc_documents:
                    st.success(f"✅ Generated {len(doc_documents)} DOC documents!")
                    st.session_state.doc_documents = doc_documents
                else:
                    st.warning("⚠️ No DOC documents generated")
            except Exception as e:
                st.warning(f"⚠️ Could not generate DOC documents: {str(e)}")
            
            return True
            
    except Exception as e:
        st.error(f"❌ Error generating documents: {str(e)}")
        logger.error(f"Document generation error: {traceback.format_exc()}")
        return False

def save_documents_to_temp() -> bool:
    """Save generated documents to temporary directory"""
    try:
        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp())
        st.session_state.temp_dir = temp_dir
        generated_files = []
        
        # Save HTML files
        if st.session_state.html_documents:
            html_dir = temp_dir / "html"
            html_dir.mkdir(exist_ok=True)
            
            for doc_name, html_content in st.session_state.html_documents.items():
                # Clean filename
                clean_name = "".join(c for c in doc_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                clean_name = clean_name.replace(' ', '_')
                filename = f"{clean_name}.html"
                file_path = html_dir / filename
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                generated_files.append({
                    'path': str(file_path),
                    'name': filename,
                    'type': 'HTML',
                    'size': len(html_content)
                })
        
        # Save PDF files
        if st.session_state.pdf_documents:
            pdf_dir = temp_dir / "pdf"
            pdf_dir.mkdir(exist_ok=True)
            
            for doc_name, pdf_bytes in st.session_state.pdf_documents.items():
                file_path = pdf_dir / doc_name
                with open(file_path, 'wb') as f:
                    f.write(pdf_bytes)
                generated_files.append({
                    'path': str(file_path),
                    'name': doc_name,
                    'type': 'PDF',
                    'size': len(pdf_bytes)
                })
        
        # Save DOC files
        if st.session_state.doc_documents:
            doc_dir = temp_dir / "doc"
            doc_dir.mkdir(exist_ok=True)
            
            for doc_name, doc_bytes in st.session_state.doc_documents.items():
                file_path = doc_dir / doc_name
                with open(file_path, 'wb') as f:
                    f.write(doc_bytes)
                generated_files.append({
                    'path': str(file_path),
                    'name': doc_name,
                    'type': 'DOC',
                    'size': len(doc_bytes)
                })
        
        # Create ZIP package if available
        if st.session_state.html_documents or st.session_state.pdf_documents or st.session_state.doc_documents:
            try:
                # Use the generator's ZIP creation method
                doc_generator = DocumentGenerator(st.session_state.processed_data)
                all_formats_result = doc_generator.generate_all_formats_and_zip()
                zip_bytes = all_formats_result.get('zip_package')
                
                if zip_bytes:
                    zip_path = temp_dir / "All_Documents.zip"
                    with open(zip_path, 'wb') as f:
                        f.write(zip_bytes)
                    generated_files.append({
                        'path': str(zip_path),
                        'name': "All_Documents.zip",
                        'type': 'ZIP',
                        'size': len(zip_bytes)
                    })
            except Exception as e:
                st.warning(f"⚠️ Could not create ZIP package: {str(e)}")
        
        st.session_state.generated_files = generated_files
        return True
        
    except Exception as e:
        st.error(f"❌ Error saving documents: {str(e)}")
        logger.error(f"Document saving error: {traceback.format_exc()}")
        return False

def show_download_section():
    """Show download section with all generated files"""
    if not st.session_state.generated_files:
        return
    
    st.markdown("### 📥 Download Generated Documents")
    
    # Group files by type
    file_groups = {}
    for file_info in st.session_state.generated_files:
        file_type = file_info['type']
        if file_type not in file_groups:
            file_groups[file_type] = []
        file_groups[file_type].append(file_info)
    
    # Show files by type
    for file_type, files in file_groups.items():
        with st.expander(f"📁 {file_type} Files ({len(files)})", expanded=True):
            for i, file_info in enumerate(files):
                file_path = file_info['path']
                file_name = file_info['name']
                file_size = file_info['size']
                
                # Read file content
                try:
                    if file_name.endswith('.zip'):
                        mime_type = "application/zip"
                    elif file_name.endswith('.pdf'):
                        mime_type = "application/pdf"
                    elif file_name.endswith('.docx'):
                        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    else:
                        mime_type = "text/html"
                    
                    with open(file_path, "rb") as file:
                        file_data = file.read()
                    
                    # Show file info and download button
                    col1, col2, col3 = st.columns([3, 1, 2])
                    with col1:
                        st.write(f"**{file_name}**")
                    with col2:
                        st.write(f"{file_size:,} bytes")
                    with col3:
                        st.download_button(
                            label="📥 Download",
                            data=file_data,
                            file_name=file_name,
                            mime=mime_type,
                            key=f"download_{file_type}_{i}"
                        )
                except Exception as e:
                    st.error(f"❌ Error reading {file_name}: {str(e)}")

def show_data_preview(data: Dict):
    """Show preview of processed data"""
    st.markdown("### 📋 Data Preview")
    
    # Title data
    if data.get('title_data'):
        with st.expander("📄 Project Information", expanded=True):
            title_df = pd.DataFrame([
                {"Field": k, "Value": v} for k, v in data['title_data'].items() if v
            ])
            st.dataframe(title_df, hide_index=True, use_container_width=True)
    
    # Work order data
    work_order_data = data.get('work_order_data')
    if work_order_data is not None and isinstance(work_order_data, pd.DataFrame) and not work_order_data.empty:
        with st.expander("📋 Work Order Items", expanded=False):
            st.dataframe(work_order_data, hide_index=True, use_container_width=True)
    
    # Bill quantity data
    bill_quantity_data = data.get('bill_quantity_data')
    if bill_quantity_data is not None and isinstance(bill_quantity_data, pd.DataFrame) and not bill_quantity_data.empty:
        with st.expander("💰 Bill Quantities", expanded=False):
            st.dataframe(bill_quantity_data, hide_index=True, use_container_width=True)
    
    # Extra items data
    extra_items_data = data.get('extra_items_data')
    if extra_items_data is not None and isinstance(extra_items_data, pd.DataFrame) and not extra_items_data.empty:
        with st.expander("➕ Extra Items", expanded=False):
            st.dataframe(extra_items_data, hide_index=True, use_container_width=True)

def show_performance_metrics():
    """Show performance metrics in sidebar"""
    with st.sidebar:
        st.markdown("## 📊 Performance")
        
        if st.session_state.processed_data:
            # Document counts
            html_count = len(st.session_state.html_documents) if st.session_state.html_documents else 0
            pdf_count = len(st.session_state.pdf_documents) if st.session_state.pdf_documents else 0
            doc_count = len(st.session_state.doc_documents) if st.session_state.doc_documents else 0
            
            st.metric("HTML Documents", html_count)
            st.metric("PDF Documents", pdf_count)
            st.metric("DOC Documents", doc_count)
            
            # File sizes
            if st.session_state.generated_files:
                total_size = sum(f['size'] for f in st.session_state.generated_files)
                st.metric("Total Size", f"{total_size:,} bytes")
        
        # Reset button
        if st.button("🔄 Reset Generator"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Load custom CSS
    load_custom_css()
    
    # Show header
    show_header()
    
    # Show performance metrics in sidebar
    show_performance_metrics()
    
    # Main content
    st.markdown("""
    <div class="feature-card">
        <h3>🚀 Perfect Single File Processing</h3>
        <p>Upload one Excel file and generate all document formats (HTML, PDF, DOC) with optimal performance.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload section
    st.markdown("""
    <div class="upload-area">
        <div class="upload-icon">📤</div>
        <h3>Upload Excel File</h3>
        <p>Supported formats: .xlsx, .xls</p>
        <p><small>File should contain Title, Work Order, and Bill Quantity sheets</small></p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose Excel file",
        type=['xlsx', 'xls'],
        label_visibility="collapsed",
        key="main_uploader"
    )
    
    # Process uploaded file
    if uploaded_file is not None:
        # Store uploaded file in session state
        st.session_state.uploaded_file = uploaded_file
        
        # Process file if not already processed
        if st.session_state.processed_data is None:
            processed_data = process_excel_file(uploaded_file)
            if processed_data:
                st.session_state.processed_data = processed_data
                show_data_preview(processed_data)
            else:
                st.session_state.processed_data = None
                return
        
        # Show data preview if we have processed data
        if st.session_state.processed_data:
            show_data_preview(st.session_state.processed_data)
            
            # Generate documents button
            if st.button("🎯 Generate All Documents", type="primary", use_container_width=True):
                # Generate documents
                if generate_documents(st.session_state.processed_data):
                    # Save documents to temporary directory
                    if save_documents_to_temp():
                        st.success("🎉 All documents generated and saved successfully!")
                    else:
                        st.error("❌ Failed to save documents")
                else:
                    st.error("❌ Failed to generate documents")
            
            # Show download section if we have generated files
            if st.session_state.generated_files:
                show_download_section()
                
                # Show summary
                st.markdown("### 📊 Generation Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    html_count = len([f for f in st.session_state.generated_files if f['type'] == 'HTML'])
                    st.metric("HTML Files", html_count)
                
                with col2:
                    pdf_count = len([f for f in st.session_state.generated_files if f['type'] == 'PDF'])
                    st.metric("PDF Files", pdf_count)
                
                with col3:
                    doc_count = len([f for f in st.session_state.generated_files if f['type'] == 'DOC'])
                    st.metric("DOC Files", doc_count)
                
                with col4:
                    total_size = sum(f['size'] for f in st.session_state.generated_files)
                    st.metric("Total Size", f"{total_size:,} bytes")

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