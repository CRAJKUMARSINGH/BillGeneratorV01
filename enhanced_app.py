#!/usr/bin/env python3
"""
Enhanced Infrastructure Billing System
Optimized for maximum performance and efficiency
"""

import streamlit as st
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import io
import base64
import asyncio
import time
from pathlib import Path
import os
import sys
import traceback
import json
import tempfile
from typing import Dict, List, Any, Optional, Union
import logging
import streamlit.components.v1 as components

import logging
import streamlit.components.v1 as components

# Add utils to path for imports
utils_path = Path(__file__).parent / "utils"
if str(utils_path) not in sys.path:
    sys.path.append(str(utils_path))

from utils.excel_processor import ExcelProcessor
from utils.document_generator import DocumentGenerator
from enhanced_document_generator_fixed import DocumentGenerator as EnhancedDocumentGenerator
from utils.pdf_merger import PDFMerger
from batch_processor import HighPerformanceBatchProcessor, StreamlitBatchInterface
from enhanced_batch_processor import EnhancedBatchProcessor
from optimized_pdf_converter import OptimizedPDFConverter

# Safe import for DataFrameSafetyUtils
try:
    from utils.dataframe_safety_utils import DataFrameSafetyUtils as UtilsDataFrameSafetyUtils
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

    # Performance optimization flags
    if 'use_enhanced_processor' not in st.session_state:
        st.session_state.use_enhanced_processor = True

def show_header():
    """Display the application header with government logo and professional design"""
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🏛️ Enhanced Infrastructure Billing System</h1>
        <p class="header-subtitle">Professional Government Billing and Documentation Solution</p>
        <p class="header-professional">Optimized for Performance and Accuracy</p>
        <p class="header-initiative">Rajasthan Public Works Department Initiative</p>
    </div>
    """, unsafe_allow_html=True)

# Performance optimization functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def cached_file_processing(uploaded_file):
    """Cache file processing results for better performance"""
    processor = ExcelProcessor(uploaded_file)
    return processor.process_excel()

async def async_document_generation(data):
    """Asynchronously generate documents for better performance"""
    generator = EnhancedDocumentGenerator(data)
    return await asyncio.get_event_loop().run_in_executor(None, generator.generate_all_documents)

def get_performance_metrics():
    """Get current performance metrics"""
    import psutil
    process = psutil.Process(os.getpid())
    return {
        'cpu_percent': process.cpu_percent(),
        'memory_mb': process.memory_info().rss / 1024 / 1024,
        'threads': process.num_threads()
    }

# Enhanced batch processing interface
class EnhancedStreamlitBatchInterface:
    """Enhanced Streamlit interface for batch processing with performance optimizations"""
    
    def __init__(self):
        self.processor = None
    
    def render_batch_interface(self):
        """Render the enhanced batch processing interface"""
        st.markdown("## 🚀 Enhanced Batch Processing")
        
        # Performance options
        st.markdown("### ⚙️ Performance Options")
        col1, col2 = st.columns(2)
        
        with col1:
            use_enhanced = st.checkbox("Use Enhanced Processor", value=True, 
                                     help="Enable enhanced batch processor with parallel processing")
            st.session_state.use_enhanced_processor = use_enhanced
            
        with col2:
            show_performance = st.checkbox("Show Performance Metrics", value=True)
        
        # Input directory selection
        st.markdown("### 📁 Input Configuration")
        input_dir = st.text_input("Input Directory", "INPUT_FILES", 
                                help="Directory containing Excel files to process")
        output_dir = st.text_input("Output Directory", "OUTPUT_FILES", 
                                 help="Directory where processed files will be saved")
        
        # Performance metrics display
        if show_performance:
            metrics = get_performance_metrics()
            st.markdown("### 📊 Real-time Performance Metrics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("CPU Usage", f"{metrics['cpu_percent']:.1f}%")
            
            with col2:
                st.metric("Memory Usage", f"{metrics['memory_mb']:.1f} MB")
            
            with col3:
                st.metric("Threads", metrics['threads'])
        
        # Process button
        if st.button("🚀 Process Batch Files", type="primary", use_container_width=True):
            if os.path.exists(input_dir):
                with st.spinner("Processing batch files..."):
                    try:
                        start_time = time.time()
                        
                        if st.session_state.use_enhanced_processor:
                            # Use enhanced processor
                            processor = EnhancedBatchProcessor(input_dir, output_dir)
                            results = asyncio.run(processor.process_batch_files(self._update_progress))
                        else:
                            # Use original processor
                            processor = HighPerformanceBatchProcessor(input_dir, output_dir)
                            results = processor.process_batch_files()
                        
                        # Ensure results is always a list
                        if isinstance(results, dict):
                            results = [results]
                        elif not isinstance(results, list):
                            results = []
                        
                        processing_time = time.time() - start_time
                        
                        # Show results
                        self._show_batch_results(results, processing_time)
                        
                    except Exception as e:
                        st.error(f"Error processing batch files: {str(e)}")
                        logger.error(f"Batch processing error: {str(e)}")
            else:
                st.error("Input directory does not exist!")
    
    def _update_progress(self, message):
        """Update progress callback"""
        st.info(message)
    
    def _show_batch_results(self, results: List[Dict[str, Any]], processing_time: float):
        """Show enhanced batch processing results"""
        st.markdown("### 📊 Batch Processing Results")
        
        # Summary statistics
        total_files = len(results)
        successful = sum(1 for r in results if r.get('success', False))
        failed = total_files - successful
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Files", total_files)
        
        with col2:
            st.metric("Successful", successful, f"+{successful}")
        
        with col3:
            st.metric("Failed", failed, f"-{failed}" if failed > 0 else None)
        
        with col4:
            st.metric("Time", f"{processing_time:.1f}s")
        
        # Performance improvements
        if st.session_state.use_enhanced_processor:
            st.success(f"✅ Using enhanced processor with parallel processing")
        
        # Detailed results
        if results:
            st.markdown("### 📋 Detailed Results")
            
            result_data = []
            for result in results:
                result_data.append({
                    "File": result.get('file_name', 'Unknown'),
                    "Status": "✅ Success" if result.get('success', False) else "❌ Failed",
                    "Processing Time": f"{result.get('processing_time', 0):.2f}s",
                    "Output Size": f"{result.get('output_size', 0):,} bytes" if result.get('output_size', 0) > 0 else "N/A",
                    "Memory Used": f"{result.get('memory_used', 0):.1f} MB" if result.get('memory_used', 0) > 0 else "N/A",
                    "Error": result.get('error', 'None')
                })
            
            results_df = pd.DataFrame(result_data)
            st.dataframe(results_df, hide_index=True, use_container_width=True)

# Main application
def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Load custom CSS
    load_custom_css()
    
    # Show header
    show_header()
    
    # Performance metrics in sidebar
    with st.sidebar:
        st.markdown("## 📊 Performance Dashboard")
        metrics = get_performance_metrics()
        st.metric("CPU Usage", f"{metrics['cpu_percent']:.1f}%")
        st.metric("Memory", f"{metrics['memory_mb']:.1f} MB")
        st.metric("Threads", metrics['threads'])
        
        # Performance options
        st.markdown("## ⚙️ Optimization")
        st.session_state.use_enhanced_processor = st.checkbox(
            "Use Enhanced Processor", 
            value=st.session_state.use_enhanced_processor,
            help="Enable enhanced batch processor with parallel processing"
        )
    
    # Enhanced batch processing interface
    batch_interface = EnhancedStreamlitBatchInterface()
    batch_interface.render_batch_interface()

if __name__ == "__main__":
    main()