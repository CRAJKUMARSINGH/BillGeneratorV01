"""
Enhanced Bill Generator Application with Excel-like Quantity Entry
Fixed DataFrame ambiguity errors and enhanced user interface
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import io
import zipfile
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Union
import os
import sys

# Add utils to path
if 'utils' not in sys.path:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

try:
    from utils.excel_processor import ExcelProcessor
    from utils.document_generator import DocumentGenerator
    from utils.pdf_merger import PDFMerger
    from utils.enhanced_config import EnhancedConfig
except ImportError as e:
    st.error(f"Import error: {e}. Please ensure utils modules are available.")

# Import our custom utilities
from dataframe_safety_utils import DataFrameSafetyUtils
from excel_like_interface import ExcelLikeQuantityEntry

# Page configuration
st.set_page_config(
    page_title="Enhanced Bill Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class EnhancedBillGenerator:
    """Enhanced Bill Generator with DataFrame safety and Excel-like interface"""

    def __init__(self):
        self.config = EnhancedConfig()
        self.excel_processor = ExcelProcessor(self.config)
        self.df_utils = DataFrameSafetyUtils()
        self.excel_interface = ExcelLikeQuantityEntry()
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize session state variables safely"""
        default_states = {
            'mode': 'selection',
            'step': 1,
            'work_order_data': None,
            'bill_quantities': {},
            'extra_items': [],
            'title_data': None,
            'processing_status': 'ready',
            'validation_results': {},
            'enhanced_bill_quantities': {},
            'enhanced_bill_quantities_rates': {}
        }

        for key, default_value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

    def render_header(self):
        """Render the application header"""
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 10px; margin-bottom: 2rem; color: white;">
            <h1 style="margin: 0; text-align: center;">🏗️ Enhanced Bill Generator</h1>
            <p style="margin: 0.5rem 0 0 0; text-align: center; opacity: 0.9;">
                Professional infrastructure billing with Excel-like quantity entry
            </p>
        </div>
        """, unsafe_allow_html=True)

    def render_mode_selection(self):
        """Render mode selection interface"""
        st.markdown("## 🚀 Choose Your Working Mode")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📄 Excel Upload Mode", use_container_width=True):
                st.session_state.mode = 'excel_upload'
                st.rerun()

            st.markdown("""
            **Features:**
            - Upload complete Excel files
            - Automatic data extraction
            - Quick processing
            - Best for prepared data
            """)

        with col2:
            if st.button("🌐 Online Entry Mode", use_container_width=True):
                st.session_state.mode = 'online_entry'
                st.session_state.step = 1
                st.rerun()

            st.markdown("""
            **Features:**
            - Step-by-step data entry
            - Excel-like quantity interface
            - Rate modification controls
            - Real-time validation
            """)

    def render_excel_upload_mode(self):
        """Render Excel upload mode interface"""
        st.markdown("## 📄 Excel Upload Mode")

        if st.button("← Back to Mode Selection"):
            st.session_state.mode = 'selection'
            st.rerun()

        uploaded_file = st.file_uploader(
            "Upload Excel File",
            type=['xlsx', 'xls'],
            help="Upload Excel file containing Title, Work Order, and Bill Quantity sheets"
        )

        if uploaded_file:
            try:
                with st.spinner("Processing Excel file..."):
                    # Use safe DataFrame processing
                    data = self.excel_processor.process_excel_file(uploaded_file)

                    # Safely check and store data
                    if self.df_utils.is_dataframe_or_data(data.get('work_order_data')):
                        st.session_state.work_order_data = data['work_order_data']

                    if self.df_utils.is_dataframe_or_data(data.get('title_data')):
                        st.session_state.title_data = data['title_data']

                    if self.df_utils.is_dataframe_or_data(data.get('bill_quantity_data')):
                        st.session_state.bill_quantity_data = data['bill_quantity_data']

                st.success("✅ Excel file processed successfully!")
                self._show_data_preview(data)

                if st.button("Generate Documents", type="primary"):
                    self._generate_documents(data)

            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")

    def render_online_entry_mode(self):
        """Render online entry mode with step-by-step interface"""
        st.markdown("## 🌐 Online Entry Mode")

        # Progress indicator
        progress_cols = st.columns(4)
        steps = [
            ("1", "Work Order", st.session_state.step >= 1),
            ("2", "Bill Quantities", st.session_state.step >= 2),
            ("3", "Extra Items", st.session_state.step >= 3),
            ("4", "Generate", st.session_state.step >= 4)
        ]

        for i, (step_num, step_name, is_active) in enumerate(steps):
            with progress_cols[i]:
                status = "🟢" if is_active else "⚪"
                st.markdown(f"{status} **Step {step_num}:** {step_name}")

        st.markdown("---")

        # Navigation buttons
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])

        with nav_col1:
            if st.button("← Back to Selection"):
                st.session_state.mode = 'selection'
                st.rerun()

        with nav_col3:
            if st.session_state.step > 1:
                if st.button("← Previous Step"):
                    st.session_state.step -= 1
                    st.rerun()

        # Render current step
        if st.session_state.step == 1:
            self._render_step1_work_order()
        elif st.session_state.step == 2:
            self._render_step2_bill_quantities()
        elif st.session_state.step == 3:
            self._render_step3_extra_items()
        elif st.session_state.step == 4:
            self._render_step4_generate()

    def _render_step1_work_order(self):
        """Step 1: Work Order Upload/Entry"""
        st.markdown("### Step 1: Work Order Data")

        tab1, tab2 = st.tabs(["📁 Upload Excel", "✏️ Manual Entry"])

        with tab1:
            uploaded_file = st.file_uploader(
                "Upload Work Order Excel File",
                type=['xlsx', 'xls'],
                key="wo_upload"
            )

            if uploaded_file:
                try:
                    # Process work order file safely
                    data = self.excel_processor.process_excel_file(uploaded_file)

                    if self.df_utils.is_valid_dataframe(data.get('work_order_data')):
                        st.session_state.work_order_data = data['work_order_data']
                        st.success("✅ Work order data loaded successfully!")

                        # Show preview
                        st.markdown("#### 📋 Work Order Preview")
                        st.dataframe(st.session_state.work_order_data.head(), use_container_width=True)

                        if st.button("Continue to Bill Quantities →", type="primary"):
                            st.session_state.step = 2
                            st.rerun()
                    else:
                        st.error("❌ No valid work order data found in the file")

                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")

        with tab2:
            st.markdown("#### Manual Work Order Entry")
            st.info("🚧 Manual entry feature coming soon. Please use Excel upload for now.")

    def _render_step2_bill_quantities(self):
        """Step 2: Enhanced Excel-like Bill Quantity Entry"""
        st.markdown("### Step 2: Bill Quantity Entry")

        # Check if we have work order data
        if not self.df_utils.is_valid_dataframe(st.session_state.work_order_data):
            st.warning("⚠️ No work order data available. Please complete Step 1 first.")
            return

        # Render the enhanced Excel-like interface
        summary_data = self.excel_interface.render_quantity_entry_interface(
            st.session_state.work_order_data,
            "enhanced_bill_quantities"
        )

        # Navigation based on completion
        if summary_data['items_with_qty'] > 0 and not summary_data['validation_issues']:
            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button("Continue to Extra Items →", type="primary"):
                    st.session_state.step = 3
                    st.rerun()

            with col2:
                if st.button("Skip to Generate →"):
                    st.session_state.step = 4
                    st.rerun()

        # Store summary for later use
        st.session_state.validation_results = summary_data

    def _render_step3_extra_items(self):
        """Step 3: Extra Items Management"""
        st.markdown("### Step 3: Extra Items (Optional)")

        st.markdown("#### ➕ Add Extra Items")

        # Initialize extra items if not exists
        if 'extra_items' not in st.session_state:
            st.session_state.extra_items = []

        with st.form("add_extra_item"):
            col1, col2, col3, col4 = st.columns([3, 1, 1.5, 1.5])

            with col1:
                description = st.text_input("Item Description")
            with col2:
                unit = st.text_input("Unit", value="No")
            with col3:
                rate = st.number_input("Rate (₹)", min_value=0.01, step=0.01)
            with col4:
                quantity = st.number_input("Quantity", min_value=0.01, step=0.01)

            if st.form_submit_button("Add Item"):
                if description and rate > 0 and quantity > 0:
                    extra_item = {
                        'description': description,
                        'unit': unit,
                        'rate': rate,
                        'quantity': quantity,
                        'amount': rate * quantity
                    }
                    st.session_state.extra_items.append(extra_item)
                    st.success(f"✅ Added: {description}")
                    st.rerun()

        # Show existing extra items
        if st.session_state.extra_items:
            st.markdown("#### 📋 Extra Items")

            for i, item in enumerate(st.session_state.extra_items):
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"**{item['description']}** - {item['quantity']} {item['unit']} @ ₹{item['rate']} = ₹{item['amount']:.2f}")

                with col2:
                    if st.button(f"Remove", key=f"remove_extra_{i}"):
                        st.session_state.extra_items.pop(i)
                        st.rerun()

        # Navigation
        if st.button("Continue to Generate →", type="primary"):
            st.session_state.step = 4
            st.rerun()

    def _render_step4_generate(self):
        """Step 4: Document Generation"""
        st.markdown("### Step 4: Generate Documents")

        # Final summary
        st.markdown("#### 📊 Final Summary")

        # Check data availability
        has_work_order = self.df_utils.is_valid_dataframe(st.session_state.work_order_data)
        has_quantities = bool(st.session_state.get('enhanced_bill_quantities', {}))
        has_extra_items = bool(st.session_state.get('extra_items', []))

        summary_cols = st.columns(3)

        with summary_cols[0]:
            status = "✅" if has_work_order else "❌"
            st.markdown(f"{status} **Work Order Data**")
            if has_work_order:
                st.caption(f"{len(st.session_state.work_order_data)} items")

        with summary_cols[1]:
            status = "✅" if has_quantities else "❌"
            st.markdown(f"{status} **Bill Quantities**")
            if has_quantities:
                qty_count = sum(1 for v in st.session_state.enhanced_bill_quantities.values() if v > 0)
                st.caption(f"{qty_count} items with quantities")

        with summary_cols[2]:
            status = "✅" if has_extra_items else "ℹ️"
            st.markdown(f"{status} **Extra Items**")
            if has_extra_items:
                st.caption(f"{len(st.session_state.extra_items)} extra items")

        # Generate button
        if has_work_order and has_quantities:
            if st.button("🎯 Generate Documents", type="primary", use_container_width=True):
                self._generate_documents_online()
        else:
            st.warning("⚠️ Please complete work order data and bill quantities to generate documents.")

    def _show_data_preview(self, data: Dict):
        """Show preview of processed data with safe DataFrame checks"""
        st.markdown("#### 📋 Data Preview")

        # Work Order Data Preview
        work_order_data = data.get('work_order_data')
        if self.df_utils.is_valid_dataframe(work_order_data):
            with st.expander("📋 Work Order Summary", expanded=True):
                st.dataframe(work_order_data, use_container_width=True, hide_index=True)

        # Bill Quantity Data Preview
        bill_quantity_data = data.get('bill_quantity_data')
        if self.df_utils.is_valid_dataframe(bill_quantity_data):
            with st.expander("📊 Bill Quantity Summary"):
                st.dataframe(bill_quantity_data, use_container_width=True, hide_index=True)

        # Extra Items Data Preview
        extra_items_data = data.get('extra_items_data')
        if self.df_utils.is_valid_dataframe(extra_items_data):
            with st.expander("➕ Extra Items Summary"):
                st.dataframe(extra_items_data, use_container_width=True, hide_index=True)

    def _generate_documents(self, data: Dict):
        """Generate documents from Excel mode data"""
        try:
            with st.spinner("Generating documents..."):
                # Initialize document generator
                doc_generator = DocumentGenerator(self.config)

                # Generate documents
                results = doc_generator.generate_all_documents(data)

                if results.get('success'):
                    st.success("✅ Documents generated successfully!")

                    # Provide download options
                    self._show_download_options(results.get('files', []))
                else:
                    st.error(f"❌ Document generation failed: {results.get('error')}")

        except Exception as e:
            st.error(f"❌ Error generating documents: {str(e)}")

    def _generate_documents_online(self):
        """Generate documents from online entry mode data"""
        try:
            with st.spinner("Preparing data and generating documents..."):
                # Prepare data from session state
                data = self._prepare_online_data()

                # Generate documents
                doc_generator = DocumentGenerator(self.config)
                results = doc_generator.generate_all_documents(data)

                if results.get('success'):
                    st.success("✅ Documents generated successfully!")
                    self._show_download_options(results.get('files', []))
                else:
                    st.error(f"❌ Document generation failed: {results.get('error')}")

        except Exception as e:
            st.error(f"❌ Error generating documents: {str(e)}")

    def _prepare_online_data(self) -> Dict:
        """Prepare data from online entry for document generation"""
        # Convert session state data to the format expected by document generator
        work_order_data = st.session_state.work_order_data.copy()

        # Create bill quantity data from enhanced quantities
        bill_quantity_rows = []
        enhanced_quantities = st.session_state.get('enhanced_bill_quantities', {})
        enhanced_rates = st.session_state.get('enhanced_bill_quantities_rates', {})

        for idx, row in work_order_data.iterrows():
            qty_key = f"qty_enhanced_bill_quantities_{idx}"
            rate_key = f"rate_enhanced_bill_quantities_{idx}"

            quantity = enhanced_quantities.get(qty_key, 0.0)
            rate = enhanced_rates.get(rate_key, float(row.get('Rate', 0)))

            if quantity > 0:  # Only include items with quantities
                bill_row = {
                    'Description': row.get('Description', row.get('Item Description', '')),
                    'Unit': row.get('Unit', row.get('UOM', '')),
                    'Quantity': quantity,
                    'Rate': rate,
                    'Amount': quantity * rate
                }
                bill_quantity_rows.append(bill_row)

        bill_quantity_data = pd.DataFrame(bill_quantity_rows)

        # Add extra items if any
        extra_items_data = None
        if st.session_state.get('extra_items'):
            extra_items_data = pd.DataFrame(st.session_state.extra_items)

        return {
            'work_order_data': work_order_data,
            'bill_quantity_data': bill_quantity_data,
            'extra_items_data': extra_items_data,
            'title_data': st.session_state.get('title_data')
        }

    def _show_download_options(self, files: List[str]):
        """Show download options for generated files"""
        st.markdown("#### 📥 Download Generated Documents")

        for file_path in files:
            if os.path.exists(file_path):
                file_name = os.path.basename(file_path)

                with open(file_path, 'rb') as f:
                    st.download_button(
                        label=f"📄 Download {file_name}",
                        data=f.read(),
                        file_name=file_name,
                        mime="application/pdf" if file_name.endswith('.pdf') else "application/octet-stream"
                    )

    def run(self):
        """Main application runner"""
        self.render_header()

        # Route to appropriate mode
        if st.session_state.mode == 'selection':
            self.render_mode_selection()
        elif st.session_state.mode == 'excel_upload':
            self.render_excel_upload_mode()
        elif st.session_state.mode == 'online_entry':
            self.render_online_entry_mode()

        # Sidebar with app info
        with st.sidebar:
            st.markdown("### 📊 App Status")

            mode_status = {
                'selection': '🎯 Mode Selection',
                'excel_upload': '📄 Excel Upload Mode',
                'online_entry': f'🌐 Online Entry (Step {st.session_state.step})'
            }

            st.info(f"**Current Mode:** {mode_status.get(st.session_state.mode, 'Unknown')}")

            if st.button("🔄 Reset Application"):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

            st.markdown("---")
            st.markdown("### 🛠️ Features")
            st.markdown("""
            - ✅ DataFrame error fixes
            - 📊 Excel-like quantity entry
            - 🎛️ Rate modification controls
            - 🔄 Real-time validation
            - 📱 Mobile-responsive design
            """)

# Main application entry point
if __name__ == "__main__":
    app = EnhancedBillGenerator()
    app.run()
