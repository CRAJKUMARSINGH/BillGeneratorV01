#!/usr/bin/env python3
"""
Performance test for BillGenerator application
"""

import time
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from batch_processor import HighPerformanceBatchProcessor

def test_performance():
    """Test the performance of the batch processor"""
    print("Performance Test for BillGenerator")
    print("=" * 35)
    
    # Initialize the batch processor
    start_time = time.time()
    processor = HighPerformanceBatchProcessor("INPUT_FILES", "performance_test_output")
    
    # Discover files
    discover_start = time.time()
    files = processor.discover_input_files()
    discover_time = time.time() - discover_start
    
    print(f"Discovered {len(files)} files in {discover_time:.2f} seconds")
    
    if not files:
        print("No files found to process")
        return
    
    # Process first file as a sample
    first_file = files[0]
    print(f"\nProcessing file: {first_file.name}")
    
    process_start = time.time()
    result = processor.process_single_file(first_file)
    process_time = time.time() - process_start
    
    print(f"Processing completed in {process_time:.2f} seconds")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Output size: {result['output_size']:,} bytes")
        print(f"Generated {len(result['generated_files'])} files")
    else:
        print(f"Error: {result['error']}")
    
    total_time = time.time() - start_time
    print(f"\nTotal test time: {total_time:.2f} seconds")
    
    # Clean up test output
    import shutil
    if os.path.exists("performance_test_output"):
        shutil.rmtree("performance_test_output")
        print("Cleaned up test output directory")

if __name__ == "__main__":
    test_performance()