#!/usr/bin/env python3
"""
High-Performance Batch Processor for Bill Generator
Addresses performance issues and enables efficient batch processing
"""

import os
import sys
import time
import gc
import asyncio
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import streamlit as st
from datetime import datetime
import tempfile
import shutil
import logging

# Add utils to path
utils_path = Path(__file__).parent / "utils"
if str(utils_path) not in sys.path:
    sys.path.append(str(utils_path))

from utils.excel_processor import ExcelProcessor
from enhanced_document_generator_fixed import EnhancedDocumentGenerator
from utils.pdf_merger import PDFMerger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HighPerformanceBatchProcessor:
    """High-performance batch processor for multiple Excel files"""
    
    def __init__(self, input_directory: str, output_directory: str = None):
        self.input_directory = Path(input_directory)
        self.output_directory = Path(output_directory) if output_directory else Path("batch_output")
        self.output_directory.mkdir(exist_ok=True)
        
        # Performance tracking
        self.processing_stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_time': 0,
            'file_times': [],
            'output_sizes': []
        }
        
        # Memory management
        self.max_memory_usage = 0
        self.gc_threshold = 10  # Run garbage collection every 10 files
        
    def discover_input_files(self) -> List[Path]:
        """Discover all Excel files in input directory"""
        excel_files = []
        for pattern in ['*.xlsx', '*.xls']:
            excel_files.extend(self.input_directory.glob(pattern))
        
        # Sort files for consistent processing order
        excel_files.sort()
        self.processing_stats['total_files'] = len(excel_files)
        
        logger.info(f"Discovered {len(excel_files)} Excel files for processing")
        return excel_files
    
    def process_single_file(self, file_path: Path, progress_callback=None) -> Dict[str, Any]:
        """Process a single Excel file with optimized performance"""
        start_time = time.time()
        file_stats = {
            'file_name': file_path.name,
            'success': False,
            'processing_time': 0,
            'output_size': 0,
            'error': None,
            'generated_files': []
        }
        
        try:
            if progress_callback:
                progress_callback(f"Processing {file_path.name}...")
            
            # Process Excel file
            processor = ExcelProcessor(file_path)
            result = processor.process_excel()
            
            if not result or not isinstance(result, dict):
                raise Exception("Invalid Excel processing result")
            
            # Generate documents with optimized generator
            doc_generator = EnhancedDocumentGenerator(result)
            html_documents = doc_generator.generate_all_documents()
            
            if not html_documents:
                raise Exception("No HTML documents generated")
            
            # Convert to PDF with memory optimization
            pdf_documents = self._convert_to_pdf_optimized(html_documents, file_path.stem)
            
            if not pdf_documents:
                raise Exception("No PDF documents generated")
            
            # Save files with proper naming
            file_output_dir = self.output_directory / file_path.stem
            file_output_dir.mkdir(exist_ok=True)
            
            generated_files = []
            total_size = 0
            
            for pdf_name, pdf_bytes in pdf_documents.items():
                output_path = file_output_dir / pdf_name
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                
                file_size = len(pdf_bytes)
                total_size += file_size
                generated_files.append(str(output_path))
                
                # Validate PDF size (should be > 10KB for proper documents)
                if file_size < 10240:  # 10KB
                    logger.warning(f"Small PDF file detected: {pdf_name} ({file_size} bytes)")
            
            # Create merged PDF if multiple documents
            if len(pdf_documents) > 1:
                try:
                    merger = PDFMerger()
                    merged_pdf_bytes = merger.merge_pdfs(pdf_documents)
                    if merged_pdf_bytes:
                        merged_path = file_output_dir / f"{file_path.stem}_Merged.pdf"
                        with open(merged_path, 'wb') as f:
                            f.write(merged_pdf_bytes)
                        generated_files.append(str(merged_path))
                        total_size += len(merged_pdf_bytes)
                except Exception as e:
                    logger.warning(f"Could not merge PDFs for {file_path.name}: {str(e)}")
            
            file_stats.update({
                'success': True,
                'output_size': total_size,
                'generated_files': generated_files
            })
            
            # Update global stats
            self.processing_stats['output_sizes'].append(total_size)
            
            if progress_callback:
                progress_callback(f"✅ Completed {file_path.name} ({total_size:,} bytes)")
                
        except Exception as e:
            file_stats['error'] = str(e)
            logger.error(f"Error processing {file_path.name}: {str(e)}")
            if progress_callback:
                progress_callback(f"❌ Failed {file_path.name}: {str(e)}")
        
        finally:
            file_stats['processing_time'] = time.time() - start_time
            self.processing_stats['file_times'].append(file_stats['processing_time'])
            
            # Memory management
            if self.processing_stats['processed_files'] % self.gc_threshold == 0:
                gc.collect()
        
        return file_stats
    
    def _convert_to_pdf_optimized(self, html_documents: Dict[str, str], base_name: str) -> Dict[str, bytes]:
        """Optimized PDF conversion with memory management"""
        pdf_documents = {}
        
        try:
            # Use the enhanced document generator's PDF conversion
            doc_generator = EnhancedDocumentGenerator({})
            pdf_documents = doc_generator.create_pdf_documents(html_documents)
            
            # Validate PDF sizes
            for name, pdf_bytes in pdf_documents.items():
                if len(pdf_bytes) < 1024:  # Less than 1KB indicates error
                    logger.warning(f"Small PDF detected: {name} ({len(pdf_bytes)} bytes)")
                    
        except Exception as e:
            logger.error(f"PDF conversion error: {str(e)}")
            # Create error PDFs
            for name in html_documents.keys():
                error_pdf = self._create_error_pdf(name, str(e))
                pdf_documents[f"{name}.pdf"] = error_pdf
        
        return pdf_documents
    
    def _create_error_pdf(self, doc_name: str, error_msg: str) -> bytes:
        """Create a simple error PDF"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from io import BytesIO
            
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            c.drawString(100, 750, f"Error generating {doc_name}")
            c.drawString(100, 700, f"Error: {error_msg[:100]}")
            c.save()
            
            return buffer.getvalue()
        except:
            # Fallback: return minimal PDF bytes
            return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF"
    
    def process_batch_sequential(self, progress_callback=None) -> Dict[str, Any]:
        """Process all files sequentially with progress tracking"""
        start_time = time.time()
        excel_files = self.discover_input_files()
        
        if not excel_files:
            return {
                'success': False,
                'message': 'No Excel files found in input directory',
                'stats': self.processing_stats
            }
        
        results = []
        
        for i, file_path in enumerate(excel_files, 1):
            if progress_callback:
                progress_callback(f"Processing file {i}/{len(excel_files)}: {file_path.name}")
            
            result = self.process_single_file(file_path, progress_callback)
            results.append(result)
            
            if result['success']:
                self.processing_stats['processed_files'] += 1
            else:
                self.processing_stats['failed_files'] += 1
        
        self.processing_stats['total_time'] = time.time() - start_time
        
        return {
            'success': True,
            'results': results,
            'stats': self.processing_stats,
            'output_directory': str(self.output_directory)
        }
    
    def process_batch_parallel(self, max_workers: int = 4, progress_callback=None) -> Dict[str, Any]:
        """Process files in parallel for better performance"""
        start_time = time.time()
        excel_files = self.discover_input_files()
        
        if not excel_files:
            return {
                'success': False,
                'message': 'No Excel files found in input directory',
                'stats': self.processing_stats
            }
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.process_single_file, file_path, progress_callback): file_path 
                for file_path in excel_files
            }
            
            # Process completed tasks
            for i, future in enumerate(concurrent.futures.as_completed(future_to_file), 1):
                file_path = future_to_file[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result['success']:
                        self.processing_stats['processed_files'] += 1
                    else:
                        self.processing_stats['failed_files'] += 1
                    
                    if progress_callback:
                        progress_callback(f"Completed {i}/{len(excel_files)}: {file_path.name}")
                        
                except Exception as e:
                    logger.error(f"Error processing {file_path.name}: {str(e)}")
                    self.processing_stats['failed_files'] += 1
        
        self.processing_stats['total_time'] = time.time() - start_time
        
        return {
            'success': True,
            'results': results,
            'stats': self.processing_stats,
            'output_directory': str(self.output_directory)
        }
    
    def generate_batch_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive batch processing report"""
        stats = results['stats']
        
        report = f"""
# Batch Processing Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Total Files:** {stats['total_files']}
- **Successfully Processed:** {stats['processed_files']}
- **Failed:** {stats['failed_files']}
- **Success Rate:** {(stats['processed_files'] / stats['total_files'] * 100):.1f}%
- **Total Processing Time:** {stats['total_time']:.2f} seconds
- **Average Time per File:** {(stats['total_time'] / stats['total_files']):.2f} seconds

## Performance Metrics
- **Fastest File:** {min(stats['file_times']):.2f} seconds
- **Slowest File:** {max(stats['file_times']):.2f} seconds
- **Total Output Size:** {sum(stats['output_sizes']):,} bytes
- **Average Output Size:** {sum(stats['output_sizes']) / len(stats['output_sizes']):,} bytes

## File Details
"""
        
        for result in results['results']:
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            report += f"- **{result['file_name']}**: {status} ({result['processing_time']:.2f}s, {result['output_size']:,} bytes)\n"
            if not result['success'] and result['error']:
                report += f"  - Error: {result['error']}\n"
        
        return report

class StreamlitBatchInterface:
    """Streamlit interface for batch processing"""
    
    def __init__(self):
        self.processor = None
        self.progress_bar = None
        self.status_text = None
    
    def show_batch_interface(self):
        """Display the batch processing interface"""
        st.markdown("## 🚀 High-Performance Batch Processing")
        
        # Input directory selection
        col1, col2 = st.columns(2)
        
        with col1:
            input_dir = st.text_input(
                "Input Directory",
                value="input_files",
                help="Directory containing Excel files to process"
            )
        
        with col2:
            output_dir = st.text_input(
                "Output Directory", 
                value="batch_output",
                help="Directory to save processed files"
            )
        
        # Processing options
        st.markdown("### ⚙️ Processing Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            processing_mode = st.selectbox(
                "Processing Mode",
                ["Sequential", "Parallel"],
                help="Sequential: Process files one by one. Parallel: Process multiple files simultaneously."
            )
        
        with col2:
            max_workers = st.number_input(
                "Max Workers (Parallel Mode)",
                min_value=1,
                max_value=8,
                value=4,
                help="Number of parallel workers (only for parallel mode)"
            )
        
        with col3:
            validate_outputs = st.checkbox(
                "Validate Output Quality",
                value=True,
                help="Check output file sizes and quality"
            )
        
        # Process button
        if st.button("🚀 Start Batch Processing", type="primary"):
            self._run_batch_processing(
                input_dir, 
                output_dir, 
                processing_mode, 
                max_workers,
                validate_outputs
            )
    
    def _run_batch_processing(self, input_dir: str, output_dir: str, mode: str, max_workers: int, validate: bool):
        """Run the batch processing with progress tracking"""
        
        # Initialize processor
        self.processor = HighPerformanceBatchProcessor(input_dir, output_dir)
        
        # Create progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(message: str):
            status_text.text(message)
        
        # Process files
        if mode == "Sequential":
            results = self.processor.process_batch_sequential(progress_callback)
        else:
            results = self.processor.process_batch_parallel(max_workers, progress_callback)
        
        # Update progress bar
        progress_bar.progress(1.0)
        
        # Display results
        self._display_results(results, validate)
    
    def _display_results(self, results: Dict[str, Any], validate: bool):
        """Display batch processing results"""
        
        if not results['success']:
            st.error(f"❌ Batch processing failed: {results['message']}")
            return
        
        stats = results['stats']
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Files", stats['total_files'])
        
        with col2:
            st.metric("Success Rate", f"{(stats['processed_files'] / stats['total_files'] * 100):.1f}%")
        
        with col3:
            st.metric("Processing Time", f"{stats['total_time']:.2f}s")
        
        with col4:
            avg_size = sum(stats['output_sizes']) / len(stats['output_sizes']) if stats['output_sizes'] else 0
            st.metric("Avg Output Size", f"{avg_size:,.0f} bytes")
        
        # Quality validation
        if validate:
            self._validate_output_quality(results)
        
        # Detailed results
        with st.expander("📊 Detailed Results", expanded=True):
            for result in results['results']:
                if result['success']:
                    st.success(f"✅ {result['file_name']}: {result['output_size']:,} bytes in {result['processing_time']:.2f}s")
                else:
                    st.error(f"❌ {result['file_name']}: {result['error']}")
        
        # Download report
        report = self.processor.generate_batch_report(results)
        
        st.download_button(
            label="📥 Download Processing Report",
            data=report,
            file_name=f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
    
    def _validate_output_quality(self, results: Dict[str, Any]):
        """Validate output file quality"""
        st.markdown("### 🔍 Output Quality Validation")
        
        quality_issues = []
        
        for result in results['results']:
            if result['success']:
                # Check file size (should be > 10KB for proper PDFs)
                if result['output_size'] < 10240:
                    quality_issues.append(f"{result['file_name']}: Small output size ({result['output_size']} bytes)")
                
                # Check processing time (should be reasonable)
                if result['processing_time'] > 30:
                    quality_issues.append(f"{result['file_name']}: Slow processing ({result['processing_time']:.2f}s)")
        
        if quality_issues:
            st.warning("⚠️ Quality Issues Detected:")
            for issue in quality_issues:
                st.text(f"• {issue}")
        else:
            st.success("✅ All outputs meet quality standards!")

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="High-Performance Batch Processor")
    parser.add_argument("input_dir", help="Input directory containing Excel files")
    parser.add_argument("-o", "--output", default="batch_output", help="Output directory")
    parser.add_argument("-m", "--mode", choices=["sequential", "parallel"], default="parallel", help="Processing mode")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Number of parallel workers")
    
    args = parser.parse_args()
    
    processor = HighPerformanceBatchProcessor(args.input_dir, args.output)
    
    if args.mode == "sequential":
        results = processor.process_batch_sequential()
    else:
        results = processor.process_batch_parallel(args.workers)
    
    # Print results
    print(processor.generate_batch_report(results))

if __name__ == "__main__":
    main()
