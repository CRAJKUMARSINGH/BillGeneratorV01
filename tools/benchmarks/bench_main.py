#!/usr/bin/env python3
"""
Micro-benchmark harness for BillGeneratorV01.
Measures execution times of key paths using time.perf_counter().
"""

import time, statistics, importlib

def benchmark(func, *args, repeats=5):
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        func(*args)
        times.append(time.perf_counter() - t0)
    avg = statistics.mean(times)
    print(f"{func.__name__:<30} avg {avg*1000:.2f} ms  (±{statistics.stdev(times)*1000:.2f})")
    return avg

if __name__ == "__main__":
    try:
        app = importlib.import_module("batch_processor")
        funcs = [
            (app.process_batch, ["INPUT_FILES", "OUTPUT_FILES"]),
        ]
        print("Running BillGenerator micro-benchmarks…")
        for f, a in funcs:
            benchmark(f, *a)
    except Exception as e:
        print(f"Error running benchmarks: {e}")