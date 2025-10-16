#!/usr/bin/env python3
"""
Test script for cache module
"""

from tools.cache.cache_layer import cache_result
import time

@cache_result(ttl=10)
def expensive_function(x):
    """Simulate an expensive function"""
    time.sleep(1)  # Simulate work
    return x * 2

if __name__ == "__main__":
    print("Testing cache module...")
    
    # First call - should take about 1 second
    start = time.time()
    result1 = expensive_function(5)
    time1 = time.time() - start
    print(f"First call: {result1} (took {time1:.2f}s)")
    
    # Second call - should be fast (cached)
    start = time.time()
    result2 = expensive_function(5)
    time2 = time.time() - start
    print(f"Second call: {result2} (took {time2:.2f}s)")
    
    print("Cache test completed!")