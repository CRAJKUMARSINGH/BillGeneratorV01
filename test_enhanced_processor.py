#!/usr/bin/env python3
"""
Test script for enhanced batch processor
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from enhanced_batch_processor import EnhancedBatchProcessor

def test_enhanced_processor():
    """Test the enhanced batch processor"""
    print("Testing Enhanced Batch Processor")
    print("=" * 35)
    
    # Initialize processor
    processor = EnhancedBatchProcessor("INPUT_FILES", "test_enhanced_output")
    
    print(f"CPU Count: {processor.cpu_count}")
    print(f"Max Workers: {processor.max_workers}")
    print(f"Max Concurrent Files: {processor.max_concurrent_files}")
    
    # Discover files
    files = processor.discover_input_files()
    print(f"Discovered {len(files)} files")
    
    if files:
        print(f"First file: {files[0].name}")
    
    print("✅ Enhanced batch processor test completed successfully")

if __name__ == "__main__":
    test_enhanced_processor()