#!/usr/bin/env python3
"""
Enhanced High-Performance Batch Processor for Bill Generator
Optimized for maximum efficiency and parallel processing
"""

import os
import sys
import time
import gc
import asyncio
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import streamlit as st
from datetime import datetime
import tempfile
import shutil
import logging
from functools import lru_cache
import psutil
import threading
from queue import Queue

# Add utils to path
utils_path = Path(__file__).parent / "utils"
if str(utils_path) not in sys.path:
    sys.path.append(str(utils_path))

from utils.excel_processor import ExcelProcessor
from enhanced_document_generator_fixed import DocumentGenerator
from utils.pdf_merger import PDFMerger
from optimized_pdf_converter import OptimizedPDFConverter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedBatchProcessor:
    """Enhanced high-performance batch processor with optimized parallel processing"""
    
    def __init__(self, input_directory: str, output_directory: Optional[str] = None):
        self.input_directory = Path(input_directory)
        self.output_directory = Path(output_directory) if output_directory else Path("enhanced_batch_output")
        self.output_directory.mkdir(exist_ok=True)
        
        # Dynamic worker count based on system resources
        self.cpu_count = multiprocessing.cpu_count()
        self.max_workers = min(8, self.cpu_count * 2)  # Cap at 8 workers
        self.max_concurrent_files = min(10, self.max_workers * 2)  # Up to 10 concurrent files
        
        # Performance tracking
        self.processing_stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_time': 0,
            'file_times': [],
            'output_sizes': [],
            'peak_memory': 0,
            'avg_cpu_usage': 0
        }
        
        # Memory management
        self.max_memory_usage = 0
        self.gc_threshold = 3  # Run garbage collection every 3 files
        self.memory_check_interval = 5  # Check memory every 5 files
        
        # Thread-safe queue for results
        self.result_queue = Queue()
        
        # Cache for processed files
        self.file_cache = {}
        self.cache_max_size = 100  # Increased cache size
        
    def discover_input_files(self) -> List[Path]:
        """Discover all Excel files in input directory with enhanced filtering"""
        excel_files = []
        valid_extensions = {'.xlsx', '.xls'}
        
        # Use glob for better performance
        for ext in valid_extensions:
            excel_files.extend(self.input_directory.glob(f"*{ext}"))
        
        # Sort files for consistent processing order
        excel_files.sort()
        self.processing_stats['total_files'] = len(excel_files)
        
        logger.info(f"Discovered {len(excel_files)} Excel files for processing")
        return excel_files
    
    async def process_single_file_async(self, file_path: Path, progress_callback=None) -> Dict[str, Any]:
        """Process a single Excel file asynchronously with optimized performance"""
        start_time = time.time()
        file_stats = {
            'file_name': file_path.name,
            'success': False,
            'processing_time': 0,
            'output_size': 0,
            'error': None,
            'generated_files': [],
            'memory_used': 0,
            'cpu_time': 0
        }
        
        # Monitor resources
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = process.cpu_percent()
        
        try:
            if progress_callback:
                await progress_callback(f"Processing {file_path.name}...")
            
            # Check cache first
            file_hash = self._get_file_hash(file_path)
            if file_hash in self.file_cache:
                logger.info(f"Using cached data for {file_path.name}")
                result = self.file_cache[file_hash]
            else:
                # Process Excel file with memory optimization
                processor = ExcelProcessor(file_path)
                result = processor.process_excel()
                
                # Cache result if we have space
                if len(self.file_cache) < self.cache_max_size:
                    self.file_cache[file_hash] = result
            
            if not result or not isinstance(result, dict):
                raise Exception("Invalid Excel processing result")
            
            # Generate documents with optimized generator
            doc_generator = DocumentGenerator(result)
            html_documents = doc_generator.generate_all_documents()
            
            if not html_documents:
                raise Exception("No HTML documents generated")
            
            # Convert to PDF with enhanced optimization
            pdf_documents = await self._convert_to_pdf_enhanced(html_documents, file_path.stem)
            
            if not pdf_documents:
                raise Exception("No PDF documents generated")
            
            # Save files with proper naming
            file_output_dir = self.output_directory / file_path.stem
            file_output_dir.mkdir(exist_ok=True)
            
            generated_files = []
            total_size = 0
            
            # Parallel file writing
            write_tasks = []
            for pdf_name, pdf_bytes in pdf_documents.items():
                output_path = file_output_dir / pdf_name
                write_tasks.append(self._write_file_async(output_path, pdf_bytes))
                file_size = len(pdf_bytes)
                total_size += file_size
                generated_files.append(str(output_path))
                
                # Validate PDF size (should be > 10KB for proper documents)
                if file_size < 10240:  # 10KB
                    logger.warning(f"Small PDF file detected: {pdf_name} ({file_size} bytes)")
            
            # Execute all write tasks
            await asyncio.gather(*write_tasks)
            
            # Create merged PDF if multiple documents
            if len(pdf_documents) > 1:
                try:
                    merger = PDFMerger()
                    merged_pdf_bytes = merger.merge_pdfs(pdf_documents)
                    if merged_pdf_bytes:
                        merged_path = file_output_dir / f"{file_path.stem}_Merged.pdf"
                        await self._write_file_async(merged_path, merged_pdf_bytes)
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
                await progress_callback(f"✅ Completed {file_path.name} ({total_size:,} bytes)")
                
        except Exception as e:
            file_stats['error'] = str(e)
            logger.error(f"Error processing {file_path.name}: {str(e)}")
            if progress_callback:
                await progress_callback(f"❌ Failed {file_path.name}: {str(e)}")
        
        finally:
            # Resource monitoring
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            end_cpu = process.cpu_percent()
            
            file_stats['processing_time'] = time.time() - start_time
            file_stats['memory_used'] = end_memory - start_memory
            file_stats['cpu_time'] = end_cpu - start_cpu
            self.processing_stats['file_times'].append(file_stats['processing_time'])
            
            # Memory management - force garbage collection more frequently
            if self.processing_stats['processed_files'] % self.gc_threshold == 0:
                collected = gc.collect()
                logger.info(f"Garbage collection: {collected} objects collected")
            
            # Update peak memory usage
            if end_memory > self.processing_stats['peak_memory']:
                self.processing_stats['peak_memory'] = end_memory
        
        return file_stats
    
    async def _convert_to_pdf_enhanced(self, html_documents: Dict[str, str], base_name: str) -> Dict[str, bytes]:
        """Enhanced PDF conversion with parallel engine testing"""
        pdf_documents = {}
        
        try:
            # Use the optimized PDF converter
            converter = OptimizedPDFConverter()
            pdf_documents = converter.convert_documents_to_pdf(html_documents)
            
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
    
    async def _write_file_async(self, file_path: Path, data: bytes):
        """Asynchronously write file with buffered I/O"""
        loop = asyncio.get_event_loop()
        with open(file_path, 'wb') as f:
            await loop.run_in_executor(None, f.write, data)
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Generate hash for file caching"""
        try:
            import hashlib
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return str(file_path)
    
    def _create_error_pdf(self, doc_name: str, error_msg: str) -> bytes:
        """Create a simple error PDF"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from io import BytesIO
            
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            c.setFont("Helvetica", 16)
            c.drawString(50, height - 100, f"PDF Generation Error: {doc_name}")
            
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 150, f"Error: {error_msg}")
            
            c.save()
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating error PDF: {str(e)}")
            return f"PDF generation failed: {error_msg}".encode()
    
    async def process_batch_files(self, progress_callback=None) -> List[Dict[str, Any]]:
        """
        Process all Excel files in the input directory with enhanced performance
        
        Args:
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of processing results for each file
        """
        start_time = time.time()
        logger.info("Starting enhanced batch processing...")
        
        # Discover input files
        excel_files = self.discover_input_files()
        
        if not excel_files:
            logger.warning("No Excel files found in input directory")
            return []
        
        results = []
        
        # Process files in batches to control memory usage
        batch_size = self.max_concurrent_files
        for i in range(0, len(excel_files), batch_size):
            batch = excel_files[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(excel_files)-1)//batch_size + 1} ({len(batch)} files)")
            
            # Process batch concurrently
            batch_tasks = [
                self.process_single_file_async(file_path, progress_callback) 
                for file_path in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle results and exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error: {str(result)}")
                else:
                    results.append(result)
                    self.processing_stats['processed_files'] += 1
            
            # Memory cleanup between batches
            gc.collect()
            
            # Check system resources
            if self.processing_stats['processed_files'] % self.memory_check_interval == 0:
                process = psutil.Process(os.getpid())
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                if current_memory > self.max_memory_usage:
                    self.max_memory_usage = current_memory
        
        # Calculate total processing time
        self.processing_stats['total_time'] = time.time() - start_time
        
        # Calculate average CPU usage
        process = psutil.Process(os.getpid())
        self.processing_stats['avg_cpu_usage'] = process.cpu_percent()
        
        logger.info(f"Enhanced batch processing completed in {self.processing_stats['total_time']:.2f} seconds")
        logger.info(f"Processed {self.processing_stats['processed_files']} files")
        logger.info(f"Peak memory usage: {self.processing_stats['peak_memory']:.2f} MB")
        
        return results

# Convenience function for backward compatibility
def process_batch_enhanced(input_directory: str = "INPUT_FILES", output_directory: str = "OUTPUT_FILES"):
    """
    Process a batch of Excel files with enhanced performance.
    
    Args:
        input_directory (str): Directory containing Excel files to process
        output_directory (str): Directory where processed files will be saved
    """
    async def run_async():
        processor = EnhancedBatchProcessor(input_directory, output_directory)
        results = await processor.process_batch_files()
        return results
    
    # Run the async function
    return asyncio.run(run_async())

if __name__ == "__main__":
    # Allow command line arguments for input and output directories
    import sys
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "INPUT_FILES"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "OUTPUT_FILES"
    results = process_batch_enhanced(input_dir, output_dir)
    print(f"Processed {len(results)} files")