#!/usr/bin/env python3
"""
Simple test script to verify profiling tools work correctly
"""

import cProfile
import pstats
from pathlib import Path
import sys

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def simple_test_function():
    """A simple function to profile"""
    total = 0
    for i in range(100000):
        total += i
    return total

def main():
    """Main function to run the test"""
    print("Running simple profiling test...")
    
    # Create profiler
    profiler = cProfile.Profile()
    
    # Profile the function
    profiler.enable()
    result = simple_test_function()
    profiler.disable()
    
    # Save stats
    PROFILE_DIR = Path(__file__).parent
    PROFILE_STATS = PROFILE_DIR / "test_profile.stats"
    PROFILE_SUMMARY = PROFILE_DIR / "test_profile_summary.txt"
    
    profiler.dump_stats(str(PROFILE_STATS))
    
    # Create summary
    with open(PROFILE_SUMMARY, "w") as fh:
        ps = pstats.Stats(profiler, stream=fh).sort_stats("cumtime")
        ps.print_stats(20)  # Only show top 20 functions
    
    print(f"[✓] Test profile completed")
    print(f"    Stats file: {PROFILE_STATS}")
    print(f"    Summary file: {PROFILE_SUMMARY}")
    print(f"    Result: {result}")

if __name__ == "__main__":
    main()