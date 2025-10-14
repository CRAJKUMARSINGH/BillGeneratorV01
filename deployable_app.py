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

# Add utils to path for imports
utils_path = Path(__file__).parent / "utils"
if str(utils_path) not in sys.path:
    sys.path.append(str(utils_path))

# Import required modules
from utils.excel_processor import ExcelProcessor
from fixed_document_generator import FixedDocumentGenerator

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

def process_excel_file(uploaded_file):
    """Process uploaded Excel file"""
    try:
        # Process the Excel file
        processor = ExcelProcessor(uploaded_file)
        result = processor.process_excel()
        return result
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def generate_documents(data):
    """Generate documents from processed data"""
    try:
        # Generate documents
        generator = FixedDocumentGenerator(data)
        documents = generator.generate_all_documents()
        return documents
    except Exception as e:
        st.error(f"Error generating documents: {str(e)}")
        return None

def create_pdf_documents(documents):
    """Create PDF documents from HTML"""
    try:
        generator = FixedDocumentGenerator({})  # Empty data for PDF generation
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
                                        st.warning("⚠️ Could not create PDF files")
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
            st.markdown("### Individual Documents")
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
            
            # Create ZIP of all files
            st.markdown("### All Documents (ZIP)")
            if st.button("📦 Download All Documents as ZIP"):
                st.info("ZIP download feature requires additional dependencies. Please download individual files above.")
        else:
            st.info("📤 Please upload a file and generate documents first")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.caption("🏛️ Bill Generator - Professional Infrastructure Billing System")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()