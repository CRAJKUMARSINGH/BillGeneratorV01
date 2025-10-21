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
    
    def __init__(self, input_directory: str, output_directory: Optional[str] = None):
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
        self.gc_threshold = 5  # Run garbage collection every 5 files (reduced from 10)
        self.max_concurrent_files = 3  # Limit concurrent processing to prevent memory issues
        
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
            
            # Process Excel file with memory optimization
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
            
            # Memory management - force garbage collection more frequently
            if self.processing_stats['processed_files'] % self.gc_threshold == 0:
                collected = gc.collect()
                logger.info(f"Garbage collection: {collected} objects collected")
        
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
            c.drawString(100, 730, error_msg)
            c.save()
            
            pdf_bytes = buffer.getvalue()
            buffer.close()
            return pdf_bytes
        except Exception as e:
            logger.error(f"Error creating error PDF: {str(e)}")
            return b"Error PDF generation failed"
    
    def process_batch_files(self, progress_callback=None) -> Dict[str, Any]:
        """Process all files in batch with enhanced memory management"""
        start_time = time.time()
        all_stats = []
        
        try:
            # Discover files
            excel_files = self.discover_input_files()
            
            if not excel_files:
                logger.warning("No Excel files found for processing")
                return {
                    'success': False,
                    'message': 'No Excel files found in input directory',
                    'stats': []
                }
            
            # Process files with limited concurrency to manage memory
            for i, file_path in enumerate(excel_files):
                try:
                    # Process single file
                    file_stats = self.process_single_file(file_path, progress_callback)
                    all_stats.append(file_stats)
                    
                    # Update counters
                    if file_stats['success']:
                        self.processing_stats['processed_files'] += 1
                    else:
                        self.processing_stats['failed_files'] += 1
                    
                    # Memory optimization: Force garbage collection after each file
                    gc.collect()
                    
                    # Optional: Add small delay to prevent system overload
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Critical error processing {file_path.name}: {str(e)}")
                    self.processing_stats['failed_files'] += 1
                    if progress_callback:
                        progress_callback(f"❌ Critical error with {file_path.name}: {str(e)}")
                
                # Periodic memory cleanup
                if i % self.gc_threshold == 0:
                    collected = gc.collect()
                    logger.info(f"Periodic garbage collection: {collected} objects collected")
            
            # Calculate final statistics
            total_time = time.time() - start_time
            self.processing_stats['total_time'] = total_time
            
            success_rate = (self.processing_stats['processed_files'] / 
                          max(self.processing_stats['total_files'], 1)) * 100
            
            # Memory cleanup
            gc.collect()
            
            return {
                'success': True,
                'message': f'Processed {self.processing_stats["processed_files"]} of {self.processing_stats["total_files"]} files ({success_rate:.1f}% success rate)',
                'processing_time': total_time,
                'stats': all_stats,
                'summary': self.processing_stats
            }
            
        except Exception as e:
            logger.error(f"Batch processing error: {str(e)}")
            return {
                'success': False,
                'message': f'Batch processing failed: {str(e)}',
                'processing_time': time.time() - start_time,
                'stats': all_stats,
                'summary': self.processing_stats
            }
    
    def process_batch_sequential(self, progress_callback=None) -> Dict[str, Any]:
        """Process files sequentially (wrapper for process_batch_files)"""
        return self.process_batch_files(progress_callback)
    
    def process_batch_parallel(self, max_workers: int = 4, progress_callback=None) -> Dict[str, Any]:
        """Process files in parallel with memory management"""
        # For memory safety, we'll limit parallel processing
        max_workers = min(max_workers, self.max_concurrent_files)
        
        start_time = time.time()
        all_stats = []
        
        try:
            # Discover files
            excel_files = self.discover_input_files()
            
            if not excel_files:
                logger.warning("No Excel files found for processing")
                return {
                    'success': False,
                    'message': 'No Excel files found in input directory',
                    'stats': []
                }
            
            # Process files in parallel with executor
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_file = {
                    executor.submit(self._process_file_wrapper, file_path): file_path 
                    for file_path in excel_files
                }
                
                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        file_stats = future.result()
                        all_stats.append(file_stats)
                        
                        # Update counters
                        if file_stats['success']:
                            self.processing_stats['processed_files'] += 1
                        else:
                            self.processing_stats['failed_files'] += 1
                        
                        # Call progress callback if provided
                        if progress_callback:
                            if file_stats['success']:
                                progress_callback(f"✅ Completed {file_stats['file_name']} ({file_stats['output_size']:,} bytes)")
                            else:
                                progress_callback(f"❌ Failed {file_stats['file_name']}: {file_stats['error']}")
                    
                    except Exception as e:
                        logger.error(f"Error processing {file_path.name}: {str(e)}")
                        self.processing_stats['failed_files'] += 1
                        if progress_callback:
                            progress_callback(f"❌ Error with {file_path.name}: {str(e)}")
                    
                    # Memory cleanup after each completion
                    gc.collect()
            
            # Calculate final statistics
            total_time = time.time() - start_time
            self.processing_stats['total_time'] = total_time
            
            success_rate = (self.processing_stats['processed_files'] / 
                          max(self.processing_stats['total_files'], 1)) * 100
            
            # Memory cleanup
            gc.collect()
            
            return {
                'success': True,
                'message': f'Processed {self.processing_stats["processed_files"]} of {self.processing_stats["total_files"]} files ({success_rate:.1f}% success rate)',
                'processing_time': total_time,
                'stats': all_stats,
                'summary': self.processing_stats
            }
            
        except Exception as e:
            logger.error(f"Parallel batch processing error: {str(e)}")
            return {
                'success': False,
                'message': f'Parallel batch processing failed: {str(e)}',
                'processing_time': time.time() - start_time,
                'stats': all_stats,
                'summary': self.processing_stats
            }
    
    def _process_file_wrapper(self, file_path: Path) -> Dict[str, Any]:
        """Wrapper method for parallel processing"""
        return self.process_single_file(file_path)
    
    def generate_batch_report(self, results: Dict[str, Any]) -> str:
        """Generate a batch processing report"""
        if not results or 'summary' not in results:
            return "No results to report"
        
        summary = results['summary']
        report = []
        report.append("BATCH PROCESSING REPORT")
        report.append("=" * 50)
        report.append(f"Total Files: {summary['total_files']}")
        report.append(f"Processed Files: {summary['processed_files']}")
        report.append(f"Failed Files: {summary['failed_files']}")
        report.append(f"Success Rate: {(summary['processed_files'] / max(summary['total_files'], 1)) * 100:.1f}%")
        report.append(f"Total Processing Time: {summary['total_time']:.2f} seconds")
        
        if summary['file_times']:
            avg_time = sum(summary['file_times']) / len(summary['file_times'])
            report.append(f"Average Time per File: {avg_time:.2f} seconds")
        
        if summary['output_sizes']:
            total_output = sum(summary['output_sizes'])
            avg_output = total_output / len(summary['output_sizes'])
            report.append(f"Total Output Size: {total_output:,} bytes")
            report.append(f"Average Output Size: {avg_output:,.0f} bytes")
        
        return "\n".join(report)

class CLIBatchInterface:
    """Command-line interface for batch processing (replaces Streamlit UI)"""

    def __init__(self) -> None:
        self.processor: Optional[HighPerformanceBatchProcessor] = None
        self.results: List[Dict[str, Any]] = []

    def run(self, input_dir: str = "input_files", output_dir: str = "OUTPUT_FILES", max_workers: int = 3) -> Dict[str, Any]:
        self.processor = HighPerformanceBatchProcessor(input_dir, output_dir)
        self.processor.max_concurrent_files = max_workers
        files = self.processor.discover_input_files()
        if not files:
            return {
                'success': False,
                'message': 'No Excel files found in input directory',
                'stats': []
            }
        results: List[Dict[str, Any]] = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Processing {file_path.name}... ({i}/{len(files)})")
            result = self.processor.process_single_file(file_path)
            results.append(result)
        summary = self.processor.generate_batch_report({
            'summary': self.processor.processing_stats
        })
        logger.info("\n" + summary)
        return {
            'success': True,
            'message': f'Processed {len([r for r in results if r.get("success")])} of {len(results)} files',
            'stats': results,
            'summary_text': summary,
        }

def main_cli():
    """Entrypoint for CLI usage"""
    import argparse
    parser = argparse.ArgumentParser(description="Batch process Excel files into billing PDFs")
    parser.add_argument("--input", default="input_files", help="Input directory containing Excel files")
    parser.add_argument("--output", default="OUTPUT_FILES", help="Output directory for generated files")
    parser.add_argument("--workers", type=int, default=3, help="Maximum concurrent files to process")
    args = parser.parse_args()

    interface = CLIBatchInterface()
    result = interface.run(args.input, args.output, args.workers)
    if not result.get('success'):
        logger.error(result.get('message', 'Batch processing failed'))
        raise SystemExit(1)
    print(result.get('summary_text', ''))

if __name__ == "__main__":
    main_cli()
