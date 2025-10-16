#!/usr/bin/env python3
"""
Simple test to verify batch processor works
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Main function to test batch processing"""
    print("Testing BillGenerator batch processing...")
    
    try:
        # Import the batch processor
        import batch_processor
        
        print("Creating processor...")
        processor = batch_processor.HighPerformanceBatchProcessor("INPUT_FILES", "test_output")
        
        print("Discovering files...")
        files = processor.discover_input_files()
        print(f"Found {len(files)} files")
        
        if files:
            print("Processing first file...")
            result = processor.process_single_file(files[0])
            print(f"Result: {result}")
        else:
            print("No files found")
        
    except Exception as e:
        print(f"[✗] Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()