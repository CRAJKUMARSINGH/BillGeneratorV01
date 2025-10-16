#!/usr/bin/env python3
"""
Test script to verify the batch_processor.process_batch function works correctly
"""

import batch_processor
import tempfile
import os

def test_process_batch():
    """Test the process_batch function with string arguments"""
    # Create temporary directories
    input_dir = tempfile.mkdtemp()
    output_dir = tempfile.mkdtemp()
    
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    try:
        # Test the function
        result = batch_processor.process_batch(input_dir, output_dir)
        print("Process batch function executed successfully")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        # Clean up
        os.rmdir(input_dir)
        os.rmdir(output_dir)

if __name__ == "__main__":
    test_process_batch()