"""
Advanced Performance Monitor for BillGenerator ENHANCED
Real-time performance tracking, system monitoring, and optimization
Integrated from Priyanka_TenderV02's superior monitoring system
"""

import time
import psutil
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from contextlib import contextmanager
from collections import defaultdict, deque
import gc
import sys
import os

class PerformanceMonitor:
    """
    Advanced performance monitoring with real-time tracking and analytics
    """
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.session_start = datetime.now()
        self.operations_count = 0
        self.errors_count = 0
        self.function_calls = defaultdict(int)
        self.execution_times = defaultdict(list)
        self.memory_snapshots = deque(maxlen=1000)
        self.cpu_snapshots = deque(maxlen=1000)
        self.is_monitoring = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        # Performance thresholds
        self.THRESHOLDS = {
            'memory_warning': 80,  # %
            'memory_critical': 90,  # %
            'cpu_warning': 75,     # %
            'cpu_critical': 90,    # %
            'execution_warning': 5.0,  # seconds
            'execution_critical': 10.0  # seconds
        }
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def start_session(self):
        """Start monitoring session"""
        self.session_start = datetime.now()
        self.operations_count = 0
        self.errors_count = 0
        self.start_monitoring()
        self.logger.info("Performance monitoring session started")
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._background_monitor, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
    
    def _background_monitor(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                with self.lock:
                    memory_info = psutil.virtual_memory()
                    cpu_percent = psutil.cpu_percent(interval=1)
                    
                    self.memory_snapshots.append({
                        'timestamp': datetime.now(),
                        'percent': memory_info.percent,
                        'available': memory_info.available,
                        'used': memory_info.used
                    })
                    
                    self.cpu_snapshots.append({
                        'timestamp': datetime.now(),
                        'percent': cpu_percent
                    })
                    
                    # Check thresholds and log warnings
                    self._check_thresholds(memory_info.percent, cpu_percent)
                
                time.sleep(2)  # Monitor every 2 seconds
                
            except Exception as e:
                self.logger.error(f"Error in background monitoring: {e}")
                break
    
    def _check_thresholds(self, memory_percent: float, cpu_percent: float):
        """Check performance thresholds and log warnings"""
        if memory_percent >= self.THRESHOLDS['memory_critical']:
            self.logger.critical(f"Memory usage critical: {memory_percent:.1f}%")
        elif memory_percent >= self.THRESHOLDS['memory_warning']:
            self.logger.warning(f"Memory usage high: {memory_percent:.1f}%")
        
        if cpu_percent >= self.THRESHOLDS['cpu_critical']:
            self.logger.critical(f"CPU usage critical: {cpu_percent:.1f}%")
        elif cpu_percent >= self.THRESHOLDS['cpu_warning']:
            self.logger.warning(f"CPU usage high: {cpu_percent:.1f}%")
    
    @contextmanager
    def performance_monitor(self, operation_name: str):
        """Context manager for monitoring operations"""
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        try:
            self.operations_count += 1
            self.function_calls[operation_name] += 1
            yield
            
        except Exception as e:
            self.errors_count += 1
            self.logger.error(f"Error in {operation_name}: {e}")
            raise
            
        finally:
            end_time = time.time()
            end_memory = self.get_memory_usage()
            execution_time = end_time - start_time
            memory_delta = end_memory - start_memory
            
            # Record metrics
            with self.lock:
                self.execution_times[operation_name].append(execution_time)
                self.metrics[operation_name].append({
                    'timestamp': datetime.now(),
                    'execution_time': execution_time,
                    'memory_delta': memory_delta,
                    'start_memory': start_memory,
                    'end_memory': end_memory
                })
            
            # Check execution time thresholds
            if execution_time >= self.THRESHOLDS['execution_critical']:
                self.logger.critical(f"{operation_name} took {execution_time:.2f}s (CRITICAL)")
            elif execution_time >= self.THRESHOLDS['execution_warning']:
                self.logger.warning(f"{operation_name} took {execution_time:.2f}s (WARNING)")
            
            # Log detailed metrics for slow operations
            if execution_time > 1.0:
                self.logger.info(f"{operation_name}: {execution_time:.2f}s, Memory: {memory_delta:+.1f}MB")
    
    def monitor_function(self, func_name: str = None):
        """Decorator for monitoring function performance"""
        def decorator(func: Callable):
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.performance_monitor(name):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': memory.available / 1024 / 1024,
                'memory_used_mb': memory.used / 1024 / 1024,
                'disk_free_gb': disk.free / 1024 / 1024 / 1024,
                'process_memory_mb': self.get_memory_usage()
            }
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        with self.lock:
            stats = {
                'session_duration': (datetime.now() - self.session_start).total_seconds(),
                'operations_count': self.operations_count,
                'errors_count': self.errors_count,
                'error_rate': (self.errors_count / max(self.operations_count, 1)) * 100,
                'function_calls': dict(self.function_calls),
                'system_metrics': self.get_system_metrics()
            }
            
            # Calculate average execution times
            avg_execution_times = {}
            for func_name, times in self.execution_times.items():
                if times:
                    avg_execution_times[func_name] = {
                        'avg': sum(times) / len(times),
                        'min': min(times),
                        'max': max(times),
                        'count': len(times)
                    }
            
            stats['execution_times'] = avg_execution_times
            
            # Get recent system snapshots
            if self.memory_snapshots:
                recent_memory = list(self.memory_snapshots)[-10:]  # Last 10 snapshots
                stats['memory_trend'] = [snap['percent'] for snap in recent_memory]
            
            if self.cpu_snapshots:
                recent_cpu = list(self.cpu_snapshots)[-10:]  # Last 10 snapshots
                stats['cpu_trend'] = [snap['percent'] for snap in recent_cpu]
            
            return stats
    
    def get_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on metrics"""
        recommendations = []
        stats = self.get_performance_stats()
        
        # Memory recommendations
        memory_percent = stats['system_metrics'].get('memory_percent', 0)
        if memory_percent > 80:
            recommendations.append("🔧 Memory usage is high. Consider enabling garbage collection optimization.")
            recommendations.append("🗑️ Clear unnecessary cached data to free memory.")
        
        # CPU recommendations
        cpu_percent = stats['system_metrics'].get('cpu_percent', 0)
        if cpu_percent > 75:
            recommendations.append("⚡ CPU usage is high. Consider enabling multiprocessing for large operations.")
            recommendations.append("🔄 Implement batch processing to reduce CPU load.")
        
        # Error rate recommendations
        if stats['error_rate'] > 5:
            recommendations.append("❌ High error rate detected. Review error logs and implement better validation.")
        
        # Slow function recommendations
        for func_name, times in stats['execution_times'].items():
            if times['avg'] > 5:
                recommendations.append(f"⏰ {func_name} is slow (avg: {times['avg']:.2f}s). Consider optimization.")
        
        return recommendations
    
    def optimize_memory(self) -> float:
        """Perform memory optimization and return freed memory"""
        start_memory = self.get_memory_usage()
        
        # Force garbage collection
        gc.collect()
        
        # Clear metrics if they're too large
        with self.lock:
            if len(self.metrics) > 1000:
                # Keep only recent metrics
                for key in self.metrics:
                    if len(self.metrics[key]) > 100:
                        self.metrics[key] = self.metrics[key][-100:]
        
        end_memory = self.get_memory_usage()
        freed_memory = start_memory - end_memory
        
        if freed_memory > 0:
            self.logger.info(f"Memory optimization freed {freed_memory:.1f}MB")
        
        return freed_memory
    
    def reset_metrics(self):
        """Reset all performance metrics"""
        with self.lock:
            self.metrics.clear()
            self.function_calls.clear()
            self.execution_times.clear()
            self.memory_snapshots.clear()
            self.cpu_snapshots.clear()
            self.operations_count = 0
            self.errors_count = 0
        
        self.logger.info("Performance metrics reset")
    
    def export_metrics(self, filepath: Optional[str] = None) -> str:
        """Export performance metrics to JSON file"""
        import json
        
        stats = self.get_performance_stats()
        
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"performance_metrics_{timestamp}.json"
        
        try:
            with open(filepath, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            
            self.logger.info(f"Performance metrics exported to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            return ""
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data formatted for dashboard display"""
        stats = self.get_performance_stats()
        
        dashboard_data = {
            'overview': {
                'session_duration': f"{stats['session_duration']:.0f}s",
                'operations_total': stats['operations_count'],
                'errors_total': stats['errors_count'],
                'success_rate': f"{100 - stats['error_rate']:.1f}%"
            },
            'system': {
                'memory_usage': f"{stats['system_metrics'].get('memory_percent', 0):.1f}%",
                'cpu_usage': f"{stats['system_metrics'].get('cpu_percent', 0):.1f}%",
                'process_memory': f"{stats['system_metrics'].get('process_memory_mb', 0):.1f}MB",
                'disk_free': f"{stats['system_metrics'].get('disk_free_gb', 0):.1f}GB"
            },
            'performance': {
                'memory_trend': stats.get('memory_trend', []),
                'cpu_trend': stats.get('cpu_trend', []),
                'top_functions': self._get_top_functions(stats),
                'recommendations': self.get_optimization_recommendations()
            }
        }
        
        return dashboard_data
    
    def _get_top_functions(self, stats: Dict) -> List[Dict]:
        """Get top functions by execution time"""
        functions = []
        for func_name, times in stats['execution_times'].items():
            functions.append({
                'name': func_name,
                'avg_time': times['avg'],
                'call_count': times['count'],
                'total_time': times['avg'] * times['count']
            })
        
        # Sort by total time descending
        functions.sort(key=lambda x: x['total_time'], reverse=True)
        return functions[:10]  # Top 10 functions


# Global performance monitor instance
perf_monitor = PerformanceMonitor()

# Convenience decorators
def monitor_performance(operation_name: str = None):
    """Decorator shortcut for performance monitoring"""
    return perf_monitor.monitor_function(operation_name)

def performance_context(operation_name: str):
    """Context manager shortcut for performance monitoring"""
    return perf_monitor.performance_monitor(operation_name)

# Export main functions
__all__ = [
    'PerformanceMonitor', 
    'perf_monitor', 
    'monitor_performance', 
    'performance_context'
]
