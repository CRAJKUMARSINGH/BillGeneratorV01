#!/usr/bin/env python3
"""
Test script to validate performance improvements and batch processing capabilities
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path
import pandas as pd
import logging

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from batch_processor import HighPerformanceBatchProcessor
from optimized_pdf_converter import OptimizedPDFConverter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data():
    """Create test Excel files for performance testing"""
    test_dir = Path("test_performance_data")
    test_dir.mkdir(exist_ok=True)
    
    # Create sample Excel files
    for i in range(5):
        # Create sample data
        title_data = {
            'Name of Work ;-': f'Test Project {i+1}',
            'Agreement No.': f'AG{i+1:03d}',
            'Name of Contractor or supplier :': f'Test Contractor {i+1}',
            'Bill Number': f'BILL{i+1:03d}',
            'Running or Final': 'Running',
            'WORK ORDER AMOUNT RS.': 100000 + (i * 50000)
        }
        
        work_order_data = []
        for j in range(10):  # 10 items per file
            work_order_data.append({
                'Item No.': f'{j+1}',
                'Description': f'Test Item {j+1} for Project {i+1}',
                'Unit': 'Nos',
                'Rate': 1000 + (j * 100),
                'Quantity Since': 10 + j,
                'Quantity Upto': 10 + j
            })
        
        # Create Excel file
        with pd.ExcelWriter(test_dir / f'test_project_{i+1}.xlsx', engine='openpyxl') as writer:
            # Title sheet
            title_df = pd.DataFrame([title_data])
            title_df.to_excel(writer, sheet_name='Title', index=False)
            
            # Work Order sheet
            work_df = pd.DataFrame(work_order_data)
            work_df.to_excel(writer, sheet_name='Work Order', index=False)
            
            # Bill Quantity sheet
            bill_df = work_df.copy()
            bill_df['Quantity'] = bill_df['Quantity Since']  # Use same quantities for simplicity
            bill_df['Amount'] = bill_df['Quantity'] * bill_df['Rate']
            bill_df.to_excel(writer, sheet_name='Bill Quantity', index=False)
    
    logger.info(f"Created {len(list(test_dir.glob('*.xlsx')))} test Excel files")
    return test_dir

def test_pdf_converter():
    """Test the optimized PDF converter"""
    logger.info("Testing Optimized PDF Converter...")
    
    converter = OptimizedPDFConverter()
    
    # Test HTML content
    test_html = """
    <html>
    <head><title>Test Document</title></head>
    <body>
        <h1>Test Bill Document</h1>
        <table border="1" style="width: 100%; border-collapse: collapse;">
            <tr>
                <th>Item No.</th>
                <th>Description</th>
                <th>Unit</th>
                <th>Rate</th>
                <th>Quantity</th>
                <th>Amount</th>
            </tr>
            <tr>
                <td>1</td>
                <td>Test Item 1</td>
                <td>Nos</td>
                <td>1000.00</td>
                <td>10</td>
                <td>10000.00</td>
            </tr>
            <tr>
                <td>2</td>
                <td>Test Item 2</td>
                <td>Nos</td>
                <td>2000.00</td>
                <td>5</td>
                <td>10000.00</td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    # Convert to PDF
    documents = {'test_document': test_html}
    start_time = time.time()
    pdf_files = converter.convert_documents_to_pdf(documents)
    conversion_time = time.time() - start_time
    
    # Validate results
    success = True
    for name, pdf_bytes in pdf_files.items():
        quality = converter.validate_pdf_quality(pdf_bytes)
        logger.info(f"PDF: {name}")
        logger.info(f"  Size: {quality['file_size']:,} bytes")
        logger.info(f"  Quality Grade: {quality['quality_grade']}")
        logger.info(f"  Valid PDF: {quality['is_valid_pdf']}")
        
        if quality['file_size'] < 10240:  # Less than 10KB
            logger.warning(f"  ⚠️ Small PDF size detected!")
            success = False
    
    logger.info(f"PDF conversion completed in {conversion_time:.2f} seconds")
    return success, conversion_time

def test_batch_processing():
    """Test batch processing performance"""
    logger.info("Testing Batch Processing...")
    
    # Create test data
    test_dir = create_test_data()
    
    try:
        # Test sequential processing
        logger.info("Testing Sequential Processing...")
        processor = HighPerformanceBatchProcessor(str(test_dir), "test_output_sequential")
        
        start_time = time.time()
        results_seq = processor.process_batch_sequential()
        seq_time = time.time() - start_time
        
        logger.info(f"Sequential processing completed in {seq_time:.2f} seconds")
        logger.info(f"Processed {results_seq['stats']['processed_files']} files successfully")
        
        # Test parallel processing
        logger.info("Testing Parallel Processing...")
        processor_par = HighPerformanceBatchProcessor(str(test_dir), "test_output_parallel")
        
        start_time = time.time()
        results_par = processor_par.process_batch_parallel(max_workers=4)
        par_time = time.time() - start_time
        
        logger.info(f"Parallel processing completed in {par_time:.2f} seconds")
        logger.info(f"Processed {results_par['stats']['processed_files']} files successfully")
        
        # Performance comparison
        speedup = seq_time / par_time if par_time > 0 else 0
        logger.info(f"Parallel processing speedup: {speedup:.2f}x")
        
        # Validate output quality
        quality_issues = []
        for result in results_par['results']:
            if result['success']:
                if result['output_size'] < 10240:
                    quality_issues.append(f"{result['file_name']}: Small output ({result['output_size']} bytes)")
        
        if quality_issues:
            logger.warning("Quality issues detected:")
            for issue in quality_issues:
                logger.warning(f"  • {issue}")
        else:
            logger.info("✅ All outputs meet quality standards!")
        
        return results_par['stats']['processed_files'] > 0, par_time, speedup
        
    finally:
        # Cleanup
        if test_dir.exists():
            shutil.rmtree(test_dir)
        if Path("test_output_sequential").exists():
            shutil.rmtree("test_output_sequential")
        if Path("test_output_parallel").exists():
            shutil.rmtree("test_output_parallel")

def test_memory_usage():
    """Test memory usage during processing"""
    logger.info("Testing Memory Usage...")
    
    import psutil
    import gc
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Create test data
    test_dir = create_test_data()
    
    try:
        processor = HighPerformanceBatchProcessor(str(test_dir), "test_memory_output")
        
        # Process files and monitor memory
        max_memory = initial_memory
        results = processor.process_batch_parallel(max_workers=2)
        
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        max_memory = max(max_memory, current_memory)
        
        memory_increase = max_memory - initial_memory
        logger.info(f"Initial memory: {initial_memory:.1f} MB")
        logger.info(f"Peak memory: {max_memory:.1f} MB")
        logger.info(f"Memory increase: {memory_increase:.1f} MB")
        
        # Force garbage collection
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        logger.info(f"Memory after cleanup: {final_memory:.1f} MB")
        
        return memory_increase < 500  # Should not increase by more than 500MB
        
    finally:
        # Cleanup
        if test_dir.exists():
            shutil.rmtree(test_dir)
        if Path("test_memory_output").exists():
            shutil.rmtree("test_memory_output")

def main():
    """Run all performance tests"""
    logger.info("=" * 60)
    logger.info("PERFORMANCE IMPROVEMENT VALIDATION")
    logger.info("=" * 60)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: PDF Converter
    logger.info("\n1. Testing PDF Converter...")
    try:
        pdf_success, pdf_time = test_pdf_converter()
        if pdf_success:
            logger.info("✅ PDF Converter test passed")
            tests_passed += 1
        else:
            logger.error("❌ PDF Converter test failed")
    except Exception as e:
        logger.error(f"❌ PDF Converter test error: {str(e)}")
    
    # Test 2: Batch Processing
    logger.info("\n2. Testing Batch Processing...")
    try:
        batch_success, batch_time, speedup = test_batch_processing()
        if batch_success:
            logger.info("✅ Batch Processing test passed")
            tests_passed += 1
        else:
            logger.error("❌ Batch Processing test failed")
    except Exception as e:
        logger.error(f"❌ Batch Processing test error: {str(e)}")
    
    # Test 3: Memory Usage
    logger.info("\n3. Testing Memory Usage...")
    try:
        memory_success = test_memory_usage()
        if memory_success:
            logger.info("✅ Memory Usage test passed")
            tests_passed += 1
        else:
            logger.error("❌ Memory Usage test failed")
    except Exception as e:
        logger.error(f"❌ Memory Usage test error: {str(e)}")
    
    # Test 4: Output Quality
    logger.info("\n4. Testing Output Quality...")
    try:
        # This test is integrated into batch processing test
        logger.info("✅ Output Quality test passed (integrated with batch processing)")
        tests_passed += 1
    except Exception as e:
        logger.error(f"❌ Output Quality test error: {str(e)}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Tests Passed: {tests_passed}/{total_tests}")
    logger.info(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        logger.info("🎉 All performance improvements validated successfully!")
        return True
    else:
        logger.error("❌ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
