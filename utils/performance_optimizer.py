#!/usr/bin/env python3
"""
Performance optimization utilities for BillGeneratorV01
Provides memory management, caching, and performance monitoring
"""
import gc
try:
	import psutil  # type: ignore
except Exception:  # pragma: no cover
	psutil = None  # type: ignore
import pandas as pd
import hashlib
from functools import lru_cache, wraps
from typing import Any, Dict, Optional
import streamlit as st
from cachetools import TTLCache
import time

class PerformanceOptimizer:
	"""Handles performance optimization and monitoring"""
	
	def __init__(self):
		self.memory_cache = TTLCache(maxsize=100, ttl=1800)  # 30 minutes TTL
		self.process = psutil.Process() if psutil is not None else None
		
	def get_memory_usage(self) -> float:
		"""Get current memory usage in MB"""
		try:
			if self.process is not None:
				return self.process.memory_info().rss / 1024 / 1024
			return 0.0
		except:
			return 0.0
	
	def cleanup_memory(self):
		"""Force garbage collection and memory cleanup"""
		gc.collect()
		
	def monitor_performance(self, func):
		"""Decorator to monitor function performance"""
		@wraps(func)
		def wrapper(*args, **kwargs):
			start_time = time.time()
			start_memory = self.get_memory_usage()
			
			try:
				result = func(*args, **kwargs)
				
				end_time = time.time()
				end_memory = self.get_memory_usage()
				
				# Log performance metrics
				execution_time = end_time - start_time
				memory_used = end_memory - start_memory
				
				if hasattr(st, 'session_state'):
					if 'performance_metrics' not in st.session_state:
						st.session_state.performance_metrics = []
					
					st.session_state.performance_metrics.append({
						'function': func.__name__,
						'execution_time': execution_time,
						'memory_used': memory_used,
						'timestamp': time.time()
					})
				
				return result
				
			except Exception as e:
				self.cleanup_memory()
				raise e
				
		return wrapper
	
	def cache_result(self, key: str, data: Any, ttl: int = 1800):
		"""Cache data with TTL"""
		self.memory_cache[key] = data
		
	def get_cached_result(self, key: str) -> Optional[Any]:
		"""Get cached data"""
		return self.memory_cache.get(key)
		
	def clear_cache(self):
		"""Clear all cached data"""
		self.memory_cache.clear()
		gc.collect()
		
	def get_performance_report(self) -> Dict[str, Any]:
		"""Get performance metrics report"""
		if hasattr(st, 'session_state') and 'performance_metrics' in st.session_state:
			metrics = st.session_state.performance_metrics
			if metrics:
				total_time = sum(m['execution_time'] for m in metrics)
				total_memory = sum(m['memory_used'] for m in metrics)
				avg_time = total_time / len(metrics)
				
				return {
					'total_functions': len(metrics),
					'total_execution_time': total_time,
					'average_execution_time': avg_time,
					'total_memory_used': total_memory,
					'cache_size': len(self.memory_cache),
					'current_memory': self.get_memory_usage()
				}
		
		return {
			'cache_size': len(self.memory_cache),
			'current_memory': self.get_memory_usage()
		}

# Global optimizer instance
optimizer = PerformanceOptimizer()

def optimize_dataframe_memory(df):
	"""Optimize DataFrame memory usage"""
	if df is None or (isinstance(df, pd.DataFrame) and df.empty):
		return df
		
	# Convert object columns to category where appropriate
	for col in df.select_dtypes(include=['object']).columns:
		if df[col].nunique() / len(df) < 0.5:  # Less than 50% unique values
			df[col] = df[col].astype('category')
	
	# Optimize numeric columns
	for col in df.select_dtypes(include=['int64']).columns:
		df[col] = pd.to_numeric(df[col], downcast='integer')
		
	for col in df.select_dtypes(include=['float64']).columns:
		df[col] = pd.to_numeric(df[col], downcast='float')
	
	return df

@st.cache_data(ttl=3600, max_entries=50)
def cached_excel_processing(file_content_hash: str, file_content: bytes):
	"""Cache Excel processing results for repeated uploads"""
	# This will be called by the Excel processor
	pass

def create_file_hash(uploaded_file) -> str:
	"""Create hash for uploaded file for caching"""
	if hasattr(uploaded_file, 'getvalue'):
		content = uploaded_file.getvalue()
	elif hasattr(uploaded_file, 'read'):
		content = uploaded_file.read()
		uploaded_file.seek(0)  # Reset file pointer
	else:
		content = str(uploaded_file).encode()
	
	return hashlib.md5(content).hexdigest()

def memory_efficient_processing(data_processor_func):
	"""Decorator for memory-efficient data processing"""
	@wraps(data_processor_func)
	def wrapper(*args, **kwargs):
		initial_memory = optimizer.get_memory_usage()
		
		try:
			# Process data
			result = data_processor_func(*args, **kwargs)
			
			# Optimize result if it's a DataFrame
			if hasattr(result, 'get') and 'work_order_data' in result:
				for key in ['work_order_data', 'bill_quantity_data', 'extra_items_data']:
					if key in result and hasattr(result[key], 'memory_usage'):
						result[key] = optimize_dataframe_memory(result[key])
			
			# Clean up memory
			gc.collect()
			
			final_memory = optimizer.get_memory_usage()
			memory_saved = initial_memory - final_memory
			
			if memory_saved > 0:
				print(f"Memory optimization: Saved {memory_saved:.1f} MB")
			
			return result
			
		except Exception as e:
			gc.collect()
			raise e
			
	return wrapper

def batch_process_documents(documents, batch_size=3):
	"""Process documents in batches to reduce memory usage"""
	document_items = list(documents.items())
	batches = [document_items[i:i + batch_size] for i in range(0, len(document_items), batch_size)]
	
	processed_docs = {}
	for batch in batches:
		batch_docs = dict(batch)
		# Process batch
		for name, content in batch_docs.items():
			processed_docs[name] = content
		
		# Clean up memory after each batch
		gc.collect()
	
	return processed_docs

class StreamlitOptimizer:
	"""Streamlit-specific optimization utilities"""
	
	@staticmethod
	def optimize_session_state():
		"""Clean up old session state data"""
		if hasattr(st, 'session_state'):
			# Remove old performance metrics (keep only last 50)
			if 'performance_metrics' in st.session_state:
				metrics = st.session_state.performance_metrics
				if len(metrics) > 50:
					st.session_state.performance_metrics = metrics[-50:]
			
			# Clear temporary data
			temp_keys = [str(key) for key in st.session_state.keys() if str(key).startswith('temp_')]
			for key in temp_keys:
				del st.session_state[key]
	
	@staticmethod
	def setup_page_config():
		"""Optimize page configuration for performance"""
		if not hasattr(st, '_is_running_with_streamlit'):
			return
			
		try:
			st.set_page_config(
				page_title="Bill Generator",
				page_icon="🏛️",
				layout="wide",
				initial_sidebar_state="expanded",
				menu_items={
					'Get Help': None,
					'Report a bug': None,
					'About': "Bill Generator v2.1 - Optimized Edition"
				}
			)
		except:
			pass  # Already configured
	
	@staticmethod
	def add_performance_metrics_sidebar():
		"""Add performance metrics to sidebar"""
		with st.sidebar:
			st.markdown("### ⚡ Performance Monitor")
			
			report = optimizer.get_performance_report()
			
			col1, col2 = st.columns(2)
			with col1:
				st.metric(
					"Memory Usage", 
					f"{report.get('current_memory', 0):.1f} MB",
					help="Current application memory usage"
				)
			
			with col2:
				st.metric(
					"Cache Size", 
					report.get('cache_size', 0),
					help="Number of cached items"
				)
			
			if st.button("🧹 Clear Cache", help="Clear cached data to free memory"):
				optimizer.clear_cache()
				st.success("Cache cleared!")
				st.experimental_rerun()

# Export main functions
__all__ = [
	'PerformanceOptimizer', 
	'optimizer', 
	'optimize_dataframe_memory',
	'memory_efficient_processing',
	'batch_process_documents',
	'StreamlitOptimizer',
	'create_file_hash'
]
