#!/usr/bin/env python3
"""
Performance Benchmark for BillGenerator Application
Compares original and enhanced batch processors
"""

import time
import os
import sys
import psutil
import gc
from pathlib import Path
import pandas as pd
import asyncio

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from batch_processor import HighPerformanceBatchProcessor
from enhanced_batch_processor import EnhancedBatchProcessor

class PerformanceBenchmark:
    """Benchmark tool to compare batch processor performance"""
    
    def __init__(self, input_directory: str = "INPUT_FILES", test_output_directory: str = "benchmark_test_output"):
        self.input_directory = input_directory
        self.test_output_directory = test_output_directory
        self.results = {}
    
    def get_system_info(self):
        """Get system information for benchmarking"""
        return {
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total / (1024**3),  # GB
            'platform': sys.platform,
        }
    
    def measure_performance(self, processor_name: str, processor_func, *args) -> dict:
        """Measure performance of a processor function"""
        print(f"\n{'='*50}")
        print(f"Benchmarking {processor_name}")
        print(f"{'='*50}")
        
        # Clear cache and garbage collect
        gc.collect()
        
        # Get initial system stats
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = process.cpu_percent()
        
        # Measure time
        start_time = time.time()
        
        # Run the processor
        try:
            if asyncio.iscoroutinefunction(processor_func):
                results = asyncio.run(processor_func(*args))
            else:
                results = processor_func(*args)
        except Exception as e:
            print(f"Error running {processor_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'time': 0,
                'memory_used': 0,
                'cpu_used': 0,
                'files_processed': 0
            }
        
        end_time = time.time()
        
        # Get final system stats
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        final_cpu = process.cpu_percent()
        
        # Calculate metrics
        processing_time = end_time - start_time
        memory_used = final_memory - initial_memory
        cpu_used = final_cpu - initial_cpu
        files_processed = len(results) if isinstance(results, list) else 0
        
        print(f"Time: {processing_time:.2f} seconds")
        print(f"Memory used: {memory_used:.2f} MB")
        print(f"CPU usage: {cpu_used:.2f}%")
        print(f"Files processed: {files_processed}")
        
        return {
            'success': True,
            'time': processing_time,
            'memory_used': memory_used,
            'cpu_used': cpu_used,
            'files_processed': files_processed,
            'results': results
        }
    
    def run_benchmark(self, sample_size: int = 5) -> dict:
        """Run comprehensive benchmark comparison"""
        print("BillGenerator Performance Benchmark")
        print("=" * 40)
        
        # Get system info
        system_info = self.get_system_info()
        print(f"System: {system_info['cpu_count']} CPUs, {system_info['memory_total']:.1f}GB RAM")
        
        # Create output directories
        original_output = Path(self.test_output_directory) / "original"
        enhanced_output = Path(self.test_output_directory) / "enhanced"
        
        # Clean up previous test outputs
        for dir_path in [original_output, enhanced_output]:
            if dir_path.exists():
                import shutil
                shutil.rmtree(dir_path)
        
        # Benchmark original processor
        def run_original():
            processor = HighPerformanceBatchProcessor(self.input_directory, str(original_output))
            return processor.process_batch_files()
        
        original_results = self.measure_performance("Original Batch Processor", run_original)
        
        # Benchmark enhanced processor
        async def run_enhanced():
            processor = EnhancedBatchProcessor(self.input_directory, str(enhanced_output))
            return await processor.process_batch_files()
        
        enhanced_results = self.measure_performance("Enhanced Batch Processor", run_enhanced)
        
        # Calculate improvements
        comparison = {}
        if original_results['success'] and enhanced_results['success']:
            time_improvement = ((original_results['time'] - enhanced_results['time']) / original_results['time']) * 100
            memory_improvement = ((original_results['memory_used'] - enhanced_results['memory_used']) / original_results['memory_used']) * 100 if original_results['memory_used'] > 0 else 0
            
            comparison = {
                'time_improvement_percent': time_improvement,
                'memory_improvement_percent': memory_improvement,
                'files_per_second_original': original_results['files_processed'] / original_results['time'] if original_results['time'] > 0 else 0,
                'files_per_second_enhanced': enhanced_results['files_processed'] / enhanced_results['time'] if enhanced_results['time'] > 0 else 0,
            }
            
            print(f"\n{'='*50}")
            print("PERFORMANCE COMPARISON")
            print(f"{'='*50}")
            print(f"Time improvement: {time_improvement:.1f}%")
            print(f"Memory improvement: {memory_improvement:.1f}%")
            print(f"Throughput (Original): {comparison['files_per_second_original']:.2f} files/sec")
            print(f"Throughput (Enhanced): {comparison['files_per_second_enhanced']:.2f} files/sec")
        
        # Store results
        self.results = {
            'system_info': system_info,
            'original': original_results,
            'enhanced': enhanced_results,
            'comparison': comparison
        }
        
        # Clean up test outputs
        if Path(self.test_output_directory).exists():
            import shutil
            shutil.rmtree(self.test_output_directory)
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate a detailed performance report"""
        if not self.results:
            return "No benchmark results available"
        
        report = []
        report.append("# BillGenerator Performance Benchmark Report")
        report.append("=" * 50)
        report.append("")
        
        # System Information
        sys_info = self.results['system_info']
        report.append("## System Information")
        report.append(f"- CPUs: {sys_info['cpu_count']}")
        report.append(f"- Memory: {sys_info['memory_total']:.1f} GB")
        report.append(f"- Platform: {sys_info['platform']}")
        report.append("")
        
        # Original Processor Results
        orig = self.results['original']
        report.append("## Original Batch Processor")
        if orig['success']:
            report.append(f"- Processing Time: {orig['time']:.2f} seconds")
            report.append(f"- Memory Usage: {orig['memory_used']:.2f} MB")
            report.append(f"- CPU Usage: {orig['cpu_used']:.2f}%")
            report.append(f"- Files Processed: {orig['files_processed']}")
        else:
            report.append(f"- Error: {orig['error']}")
        report.append("")
        
        # Enhanced Processor Results
        enh = self.results['enhanced']
        report.append("## Enhanced Batch Processor")
        if enh['success']:
            report.append(f"- Processing Time: {enh['time']:.2f} seconds")
            report.append(f"- Memory Usage: {enh['memory_used']:.2f} MB")
            report.append(f"- CPU Usage: {enh['cpu_used']:.2f}%")
            report.append(f"- Files Processed: {enh['files_processed']}")
        else:
            report.append(f"- Error: {enh['error']}")
        report.append("")
        
        # Comparison
        if self.results['comparison']:
            comp = self.results['comparison']
            report.append("## Performance Comparison")
            report.append(f"- Time Improvement: {comp['time_improvement_percent']:.1f}%")
            report.append(f"- Memory Improvement: {comp['memory_improvement_percent']:.1f}%")
            report.append(f"- Throughput Improvement: {((comp['files_per_second_enhanced'] / comp['files_per_second_original']) - 1) * 100:.1f}%")
            report.append("")
        
        return "\n".join(report)

def main():
    """Main function to run the benchmark"""
    print("Starting BillGenerator Performance Benchmark...")
    
    # Initialize benchmark
    benchmark = PerformanceBenchmark()
    
    # Run benchmark
    results = benchmark.run_benchmark()
    
    # Generate and save report
    report = benchmark.generate_report()
    print("\n" + report)
    
    # Save report to file
    with open("PERFORMANCE_BENCHMARK_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\nDetailed report saved to PERFORMANCE_BENCHMARK_REPORT.md")

if __name__ == "__main__":
    main()