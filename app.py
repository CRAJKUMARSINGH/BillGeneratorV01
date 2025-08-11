import streamlit as st
import pandas as pd
import os
import zipfile
import tempfile
from datetime import datetime
import traceback
from utils.excel_processor import ExcelProcessor
from utils.document_generator import DocumentGenerator
from utils.pdf_merger import PDFMerger
from utils.zip_packager import ZipPackager

# Page configuration
st.set_page_config(
    page_title="Infrastructure Billing System",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance with green header from App2
def inject_custom_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main > div {
        padding: 2rem 1rem;
    }

    /* Header styling - Updated to match App2's green design */
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

    /* Card styling */
    .info-card {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    .upload-card {
        background: #ffffff;
        border: 2px dashed #007bff;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }

    .upload-card:hover {
        border-color: #0056b3;
        background: #f8f9ff;
    }

    /* Status indicators */
    .status-success {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }

    .status-error {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }

    .status-info {
        background: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }

    /* Progress styling */
    .progress-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    /* Download button styling */
    .download-section {
        background: #e8f5e9;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
        border: 1px solid #4caf50;
    }

    /* Feature list styling */
    .feature-list {
        background: #ffffff;
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid #e9ecef;
    }

    .feature-item {
        display: flex;
        align-items: center;
        margin-bottom: 0.8rem;
        padding: 0.5rem;
        background: #f8f9fa;
        border-radius: 5px;
    }

    .feature-icon {
        color: #28a745;
        font-weight: bold;
        margin-right: 0.8rem;
    }

    /* Document summary cards */
    .doc-summary-card {
        background: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .doc-summary-card h4 {
        color: #495057;
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }

    .doc-list-item {
        padding: 0.3rem 0;
        border-bottom: 1px solid #f8f9fa;
    }

    .doc-list-item:last-child {
        border-bottom: none;
    }

    /* Instructions styling - Enhanced and colorful */
    .instructions-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 3rem;
        margin-top: 3rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }

    .how-to-title {
        text-align: center;
        color: #2c3e50;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    .how-to-subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2.5rem;
        font-style: italic;
    }

    .instruction-step {
        display: flex;
        align-items: flex-start;
        margin-bottom: 2rem;
        padding: 1.5rem;
        background: #ffffff;
        border-radius: 15px;
        border: none;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .instruction-step:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }

    .instruction-step::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background: linear-gradient(45deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3, #54a0ff);
        background-size: 400% 400%;
        animation: gradientShift 3s ease infinite;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .step-number {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin-right: 1.5rem;
        flex-shrink: 0;
        box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
    }

    .step-content {
        flex: 1;
    }

    .step-title {
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.8rem;
        font-size: 1.3rem;
    }

    .step-description {
        color: #555;
        font-size: 1rem;
        line-height: 1.6;
    }

    .simple-steps {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }

    .simple-step-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease;
    }

    .simple-step-card:hover {
        transform: scale(1.05);
    }

    .simple-step-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }

    .simple-step-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .simple-step-desc {
        font-size: 0.9rem;
        opacity: 0.9;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2rem;
        }

        .header-subtitle {
            font-size: 1rem;
        }

        .upload-card {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Inject custom CSS
    inject_custom_css()

    # Sidebar with additional information and features
    with st.sidebar:
        st.markdown("### 🛠️ System Information")
        st.markdown("""
        **Version:** 2.0
        **Last Updated:** July 2025
        **Status:** ✅ Active
        """)

        st.markdown("### 📊 Supported Formats")
        st.markdown("""
        **Input:** Excel (.xlsx, .xls)
        **Output:** PDF, Word, HTML, ZIP
        """)

        st.markdown("### 🏛️ Document Types")
        st.markdown("""
        - First Page Summary
        - Deviation Statement
        - Final Bill Scrutiny Sheet
        - Extra Items Statement
        - Certificate II & III
        """)

        st.markdown("### 🎯 Key Features")
        st.markdown("""
        - Professional formatting
        - Statutory compliance
        - A4 specifications
        - Automatic calculations
        - Tender premium handling
        - Multi-format output
        """)

        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.markdown("""
        - Ensure all required sheets exist
        - Check data format consistency
        - Verify numerical values
        - Review generated documents
        """)

    # Header section - Updated to match App2's design exactly with crane logo
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🏗️ Infrastructure Billing System</h1>
        <p class="header-subtitle">Generate professional billing documents from Excel files automatically</p>
        <p class="header-professional">Streamlined infrastructure documentation with statutory compliance and automated calculations</p>
        <p class="header-initiative">An Initiative by Mrs. Premlata Jain, Additional Administrative Officer, PWD, Udaipur</p>
    </div>
    """, unsafe_allow_html=True)

    # Create columns for layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        <div class="upload-card">
            <h3 style="color: #007bff; margin-bottom: 1rem;">📁 Upload Excel File</h3>
            <p style="color: #666; margin-bottom: 1.5rem;">
                Upload your Excel file containing Title, Work Order, Bill Quantity, and Extra Items sheets
            </p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Choose Excel file",
            type=['xlsx', 'xls'],
            help="Select an Excel file with the required sheets: Title, Work Order, Bill Quantity, Extra Items (optional)"
        )

    with col2:
        st.markdown("""
        <div class="info-card">
            <h4 style="color: #495057; margin-bottom: 1rem;">📋 File Requirements</h4>
            <div class="feature-list">
                <div class="feature-item">
                    <span class="feature-icon">✓</span>
                    <span><strong>Title Sheet:</strong> Contains all metadata</span>
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✓</span>
                    <span><strong>Work Order:</strong> Original work items</span>
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✓</span>
                    <span><strong>Bill Quantity:</strong> Actual measurements</span>
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✓</span>
                    <span><strong>Extra Items:</strong> Additional work (optional)</span>
                </div>
            </div>
        </div>

        <div class="info-card">
            <h4 style="color: #495057; margin-bottom: 1rem;">📄 Output Formats</h4>
            <div class="feature-list">
                <div class="feature-item">
                    <span class="feature-icon">📄</span>
                    <span>Individual PDF, Word, HTML</span>
                </div>
                <div class="feature-item">
                    <span class="feature-icon">📑</span>
                    <span>Combined PDF document</span>
                </div>
                <div class="feature-item">
                    <span class="feature-icon">🗂️</span>
                    <span>Complete ZIP package</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if uploaded_file is not None:
        try:
            # Show processing status with enhanced styling
            st.markdown("""
            <div class="progress-container">
                <h4 style="color: #495057; margin-bottom: 1rem;">🔄 Processing Your File</h4>
                <p style="color: #666; margin-bottom: 1.5rem;">Please wait while we process your Excel file and generate all documents...</p>
            </div>
            """, unsafe_allow_html=True)

            progress_bar = st.progress(0)
            status_text = st.empty()
            start_time = datetime.now()

            # Process the Excel file with enhanced status
            status_text.markdown("**Step 1/5:** 📊 Analyzing Excel file structure...")
            progress_bar.progress(10)

            processor = ExcelProcessor(uploaded_file)
            data = processor.process_excel()
            progress_bar.progress(30)

            status_text.markdown("**Step 2/5:** 📝 Generating professional documents...")

            # Generate documents
            generator = DocumentGenerator(data)
            documents = generator.generate_all_documents()
            progress_bar.progress(60)

            status_text.markdown("**Step 3/5:** 📄 Converting to PDF format...")

            # Create individual PDFs
            pdf_files = generator.create_pdf_documents(documents)
            progress_bar.progress(80)

            status_text.markdown("**Step 4/5:** 📑 Combining all documents...")

            # Merge PDFs
            merger = PDFMerger()
            merged_pdf = merger.merge_pdfs(pdf_files)
            progress_bar.progress(90)

            status_text.markdown("**Step 5/5:** 📦 Creating download package...")

            # Package everything
            packager = ZipPackager()
            zip_buffer = packager.create_package(documents, pdf_files, merged_pdf)
            progress_bar.progress(100)

            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            status_text.markdown(f"**✅ Processing complete in {processing_time:.1f} seconds!**")

            # Display results with enhanced styling and metrics
            st.balloons()  # Celebration animation
            
            st.markdown("""
            <div class="status-success">
                <h4 style="margin-bottom: 0.5rem;">🎉 Success! All documents generated perfectly!</h4>
                <p style="margin: 0;">Your professional billing documents are ready for download.</p>
            </div>
            """, unsafe_allow_html=True)

            # Show metrics in an attractive way
            col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)
            
            with col_metrics1:
                st.metric(
                    label="📄 Documents Created", 
                    value=len(documents),
                    help="Individual billing documents generated"
                )
            
            with col_metrics2:
                total_data_rows = len(data.get('work_order_data', []))
                st.metric(
                    label="📊 Data Rows Processed", 
                    value=total_data_rows,
                    help="Work order items processed"
                )
            
            with col_metrics3:
                st.metric(
                    label="📁 Output Formats", 
                    value="3",
                    delta="PDF, Word, HTML",
                    help="Multiple format outputs available"
                )
            
            with col_metrics4:
                file_size_mb = round(len(zip_buffer.getvalue()) / (1024 * 1024), 2)
                st.metric(
                    label="💾 Package Size", 
                    value=f"{file_size_mb} MB",
                    help="Total size of download package"
                )

            # Enhanced document summary with tabs
            st.markdown("### 📋 Generated Documents Overview")
            
            tab1, tab2, tab3 = st.tabs(["📄 Documents", "📊 Data Summary", "📥 Download"])
            
            with tab1:
                for i, doc_name in enumerate(documents.keys(), 1):
                    st.markdown(f"""
                    <div style="padding: 1rem; margin: 0.5rem 0; background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 8px; border-left: 4px solid #28a745;">
                        <strong>{i}. {doc_name}</strong>
                        <div style="color: #666; font-size: 0.9rem; margin-top: 0.3rem;">
                            Ready in PDF, Word, and HTML formats
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with tab2:
                col_summary1, col_summary2 = st.columns(2)
                
                with col_summary1:
                    if 'title_data' in data:
                        st.markdown("#### 🏷️ Project Information")
                        key_info = {
                            'Project Name': data['title_data'].get('Project Name', 'N/A'),
                            'Contract No': data['title_data'].get('Contract No', 'N/A'),
                            'Work Order No': data['title_data'].get('Work Order No', 'N/A')
                        }
                        for key, value in key_info.items():
                            st.markdown(f"**{key}:** {value}")
                
                with col_summary2:
                    st.markdown("#### 📈 Processing Summary")
                    st.markdown(f"**Work Order Items:** {len(data.get('work_order_data', []))}")
                    st.markdown(f"**Bill Quantity Items:** {len(data.get('bill_quantity_data', []))}")
                    if not data.get('extra_items_data', pd.DataFrame()).empty:
                        st.markdown(f"**Extra Items:** {len(data.get('extra_items_data', []))}")
                    else:
                        st.markdown("**Extra Items:** None")
            
            with tab3:
                st.markdown("#### 📦 What's in your download package:")
                
                package_contents = [
                    "📁 **HTML Folder** - Web viewable documents",
                    "📄 **PDF Folder** - Print-ready individual files", 
                    "📑 **Word Folder** - Editable document versions",
                    "📋 **Combined PDF** - All documents in one file"
                ]
                
                for content in package_contents:
                    st.markdown(f"• {content}")
                
                st.info("💡 All documents follow government standards and are ready for official submission.")

            # Enhanced download section
            st.markdown("---")
            
            download_col1, download_col2 = st.columns([2, 1])
            
            with download_col1:
                st.markdown("""
                <div class="download-section">
                    <h3 style="color: #155724; margin-bottom: 1rem;">🎉 Ready for Download!</h3>
                    <p style="color: #155724; margin-bottom: 1.5rem;">
                        Your professional billing package is complete and ready. Contains all documents in multiple formats for immediate use.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Smart filename generation
                project_name = data.get('title_data', {}).get('Project Name', 'Project')
                clean_project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()[:20]
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{clean_project_name}_BillingDocs_{timestamp}.zip"

                # Download button with enhanced styling
                st.download_button(
                    label="📥 Download Complete Package",
                    data=zip_buffer.getvalue(),
                    file_name=filename,
                    mime="application/zip",
                    use_container_width=True,
                    help=f"Downloads: {filename}"
                )

                # Direct combined PDF download
                combined_pdf_name = f"{clean_project_name}_All_Documents_{timestamp}.pdf"
                st.download_button(
                    label="📑 Download Combined PDF",
                    data=merged_pdf,
                    file_name=combined_pdf_name,
                    mime="application/pdf",
                    use_container_width=True,
                    help=f"Downloads: {combined_pdf_name}"
                )
                
                # Additional download info
                st.success(f"✅ Package ready: **{filename}** ({file_size_mb} MB)")
            
            with download_col2:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 2rem; border-radius: 15px; text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🏆</div>
                    <h4 style="color: #2e7d32; margin-bottom: 1rem;">Professional Quality</h4>
                    <p style="color: #388e3c; margin: 0; font-size: 0.9rem;">
                        Government-standard documents ready for official submission
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # Show data preview with enhanced styling
            with st.expander("📊 Data Preview & Verification"):
                st.markdown("### 📋 Extracted Data Summary")

                # Title data
                if 'title_data' in data:
                    st.markdown("#### 🏷️ Title Sheet Data")
                    # Convert title_data dict to dataframe for better display
                    title_df = pd.DataFrame(list(data['title_data'].items()), columns=['Field', 'Value'])
                    st.dataframe(title_df, use_container_width=True)

                # Work order data
                if 'work_order_data' in data:
                    st.markdown("#### 📋 Work Order Summary")
                    st.dataframe(data['work_order_data'].head(10), use_container_width=True)
                    if len(data['work_order_data']) > 10:
                        st.info(f"Showing first 10 rows of {len(data['work_order_data'])} total work order items")

                # Bill quantity data
                if 'bill_quantity_data' in data:
                    st.markdown("#### 📊 Bill Quantity Summary")
                    st.dataframe(data['bill_quantity_data'].head(10), use_container_width=True)
                    if len(data['bill_quantity_data']) > 10:
                        st.info(f"Showing first 10 rows of {len(data['bill_quantity_data'])} total bill quantity items")

                # Extra items data
                if 'extra_items_data' in data and not data['extra_items_data'].empty:
                    st.markdown("#### ➕ Extra Items Summary")
                    st.dataframe(data['extra_items_data'].head(10), use_container_width=True)
                    if len(data['extra_items_data']) > 10:
                        st.info(f"Showing first 10 rows of {len(data['extra_items_data'])} total extra items")

        except Exception as e:
            error_msg = str(e)
            
            # Provide specific error guidance
            if "No such file or directory" in error_msg or "sheet_name" in error_msg:
                st.markdown("""
                <div class="status-error">
                    <h4 style="margin-bottom: 0.5rem;">❌ Missing Required Sheets</h4>
                    <p style="margin: 0;">Your Excel file is missing required sheets. Please ensure your file contains:</p>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        <li><strong>Title</strong> - Project information</li>
                        <li><strong>Work Order</strong> - Original work items</li>
                        <li><strong>Bill Quantity</strong> - Actual measurements</li>
                        <li><strong>Extra Items</strong> - Additional work (optional)</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            elif "column" in error_msg.lower() or "key" in error_msg.lower():
                st.markdown("""
                <div class="status-error">
                    <h4 style="margin-bottom: 0.5rem;">❌ Column Format Issue</h4>
                    <p style="margin: 0;">Your Excel file has missing or incorrectly named columns. Please check:</p>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        <li><strong>Work Order & Bill Quantity sheets</strong> should have: Item, Description, Unit, Quantity, Rate, Amount</li>
                        <li><strong>Title sheet</strong> should have project information in the first two columns</li>
                        <li>Column names should match exactly (case-sensitive)</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            elif "permission" in error_msg.lower() or "access" in error_msg.lower():
                st.markdown("""
                <div class="status-error">
                    <h4 style="margin-bottom: 0.5rem;">❌ File Access Issue</h4>
                    <p style="margin: 0;">Cannot access your Excel file. Please try:</p>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        <li>Close the Excel file if it's open in another program</li>
                        <li>Check if the file is corrupted</li>
                        <li>Try uploading a different Excel file</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="status-error">
                    <h4 style="margin-bottom: 0.5rem;">❌ Processing Error</h4>
                    <p style="margin: 0;">Error: {error_msg}</p>
                    <p style="margin: 0.5rem 0 0 0;">Please check your Excel file format and try again.</p>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("🔍 Technical Error Details"):
                st.code(traceback.format_exc())
                
            # Add helpful troubleshooting section
            st.markdown("""
            <div class="status-info">
                <h4 style="margin-bottom: 0.5rem;">💡 Troubleshooting Tips</h4>
                <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                    <li>Ensure your Excel file has all required sheets with correct names</li>
                    <li>Check that data starts from the first row (no empty rows at top)</li>
                    <li>Verify column headers match the expected format</li>
                    <li>Make sure numeric columns contain only numbers (no text like "Above")</li>
                    <li>Try using one of the test files that worked successfully</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # Enhanced instructions with better formatting
    st.markdown("""
    <div class="instructions-container">
        <h2 class="how-to-title">🎯 How to Use This System</h2>
        <p class="how-to-subtitle">Simple steps to generate your billing documents in minutes!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Three main steps using Streamlit columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin: 1rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📁</div>
            <h3>Step 1: Upload</h3>
            <p>Just drag & drop your Excel file or click to browse</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border-radius: 15px; margin: 1rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚡</div>
            <h3>Step 2: Wait</h3>
            <p>System automatically creates all your documents</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; border-radius: 15px; margin: 1rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📥</div>
            <h3>Step 3: Download</h3>
            <p>Get all documents in one convenient package</p>
        </div>
        """, unsafe_allow_html=True)

    # Detailed information in expandable sections
    with st.expander("📋 What Your Excel File Should Have"):
        st.markdown("""
        **Title Sheet:** Project details like name, contract number  
        **Work Order:** Original planned work items  
        **Bill Quantity:** Actual work completed  
        **Extra Items:** Any additional work (optional)
        """)

    with st.expander("📄 What Documents You'll Get"):
        st.markdown("""
        **Professional Documents:** First Page Summary, Deviation Statement, Bill Scrutiny, Certificates  
        **Multiple Formats:** PDF for printing, Word for editing, HTML for viewing  
        **Ready to Submit:** All documents follow government standards
        """)

    with st.expander("💡 Quick Tips"):
        st.markdown("""
        **File Size:** Works with files up to 10MB  
        **Format:** Excel files (.xlsx or .xls)  
        **Speed:** Processing takes 30-60 seconds  
        **Security:** All data stays secure on your device
        """)

if __name__ == "__main__":
    main()
