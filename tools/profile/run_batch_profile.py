#!/usr/bin/env python3
"""
Profile the BillGenerator batch processing pipeline.
"""

import cProfile
import pstats
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Main function to profile batch processing"""
    print("Running BillGenerator batch processing profile...")
    
    try:
        # Import the batch processor
        import batch_processor
        
        # Create profiler
        profiler = cProfile.Profile()
        
        # Profile the batch processing function
        profiler.enable()
        result = batch_processor.process_batch("INPUT_FILES", "OUTPUT_FILES")
        profiler.disable()
        
        # Save stats
        PROFILE_DIR = Path(__file__).parent
        PROFILE_STATS = PROFILE_DIR / "profile.stats"
        PROFILE_SUMMARY = PROFILE_DIR / "profile_summary.txt"
        
        profiler.dump_stats(str(PROFILE_STATS))
        
        # Create summary
        with open(PROFILE_SUMMARY, "w") as fh:
            ps = pstats.Stats(profiler, stream=fh).sort_stats("cumtime")
            ps.print_stats(50)  # Show top 50 functions
        
        print(f"[✓] Batch processing profile completed")
        print(f"    Stats file: {PROFILE_STATS}")
        print(f"    Summary file: {PROFILE_SUMMARY}")
        print(f"    Result: {result['success'] if isinstance(result, dict) and 'success' in result else 'Success'}")
        
    except Exception as e:
        print(f"[✗] Error during profiling: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()