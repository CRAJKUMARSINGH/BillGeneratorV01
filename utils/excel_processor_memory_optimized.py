import pandas as pd
import io
import hashlib
import gc
import logging
import weakref
from typing import Dict, Any, Optional, List, Tuple
from functools import lru_cache, wraps
from datetime import datetime, timedelta
import psutil
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryManager:
    """Advanced memory management and monitoring"""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get detailed memory usage statistics"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
                'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                'percent': process.memory_percent(),
                'available_mb': psutil.virtual_memory().available / 1024 / 1024
            }
        except Exception:
            return {'rss_mb': 0, 'vms_mb': 0, 'percent': 0, 'available_mb': 0}
    
    @staticmethod
    def force_gc():
        """Force garbage collection and return freed memory"""
        before = MemoryManager.get_memory_usage()['rss_mb']
        gc.collect()
        after = MemoryManager.get_memory_usage()['rss_mb']
        return before - after
    
    @staticmethod
    def memory_monitor(func):
        """Decorator to monitor memory usage of functions"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_mem = MemoryManager.get_memory_usage()
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_mem = MemoryManager.get_memory_usage()
                end_time = datetime.now()
                
                memory_delta = end_mem['rss_mb'] - start_mem['rss_mb']
                time_delta = (end_time - start_time).total_seconds()
                
                logger.info(f"{func.__name__}: {time_delta:.2f}s, Memory: {memory_delta:+.1f}MB")
                
                # Auto cleanup if memory usage is high
                if end_mem['percent'] > 80:
                    freed = MemoryManager.force_gc()
                    logger.info(f"Auto cleanup freed {freed:.1f}MB")
        
        return wrapper

class IntelligentCache:
    """Multi-level intelligent caching system"""
    
    def __init__(self, max_items: int = 50, ttl_seconds: int = 3600):
        self.max_items = max_items
        self.ttl_seconds = ttl_seconds
        self._cache = {}
        self._access_times = {}
        self._creation_times = {}
        
    def _cleanup_expired(self):
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = []
        
        for key, created_time in self._creation_times.items():
            if (now - created_time).total_seconds() > self.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_key(key)
    
    def _remove_key(self, key: str):
        """Remove a key from all cache structures"""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_times:
            del self._access_times[key]
        if key in self._creation_times:
            del self._creation_times[key]
    
    def _evict_lru(self):
        """Evict least recently used items if cache is full"""
        while len(self._cache) >= self.max_items:
            # Find least recently used key
            lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
            self._remove_key(lru_key)
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        self._cleanup_expired()
        
        if key in self._cache:
            self._access_times[key] = datetime.now()
            return self._cache[key]
        
        return None
    
    def set(self, key: str, value: Any):
        """Set item in cache"""
        self._cleanup_expired()
        self._evict_lru()
        
        now = datetime.now()
        self._cache[key] = value
        self._access_times[key] = now
        self._creation_times[key] = now
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._access_times.clear()
        self._creation_times.clear()
        
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'items': len(self._cache),
            'max_items': self.max_items,
            'hit_rate': getattr(self, '_hit_rate', 0.0)
        }

class ChunkedDataProcessor:
    """Process large DataFrames in chunks to optimize memory"""
    
    @staticmethod
    def process_dataframe_chunked(df: pd.DataFrame, chunk_size: int = 1000) -> pd.DataFrame:
        """Process DataFrame in chunks for memory efficiency"""
        if len(df) <= chunk_size:
            return ChunkedDataProcessor._clean_dataframe(df)
        
        processed_chunks = []
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i+chunk_size].copy()
            processed_chunk = ChunkedDataProcessor._clean_dataframe(chunk)
            processed_chunks.append(processed_chunk)
            
            # Force cleanup after each chunk
            del chunk
            gc.collect()
        
        # Combine all chunks
        result = pd.concat(processed_chunks, ignore_index=True)
        
        # Cleanup chunks
        for chunk in processed_chunks:
            del chunk
        del processed_chunks
        gc.collect()
        
        return result
    
    @staticmethod
    def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and optimize DataFrame"""
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Convert string columns to category for memory efficiency
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) < 0.5:  # If less than 50% unique values
                df[col] = df[col].astype('category')
        
        # Optimize numeric columns
        for col in df.select_dtypes(include=['int64', 'float64']).columns:
            # Try to downcast to smaller types
            if df[col].dtype == 'int64':
                df[col] = pd.to_numeric(df[col], downcast='integer')
            elif df[col].dtype == 'float64':
                df[col] = pd.to_numeric(df[col], downcast='float')
        
        return df

class ExcelProcessorMemoryOptimized:
    """Memory-optimized Excel processor with intelligent caching and chunked processing"""
    
    def __init__(self, uploaded_file, cache_size: int = 50):
        self.uploaded_file = uploaded_file
        self.cache = IntelligentCache(max_items=cache_size, ttl_seconds=1800)  # 30 min TTL
        self._file_hash = None
        self._memory_threshold = 80  # Percent
        
    def _get_file_hash(self) -> str:
        """Generate hash for file caching with memory optimization"""
        if self._file_hash:
            return self._file_hash
            
        try:
            if hasattr(self.uploaded_file, 'getbuffer'):
                content = bytes(self.uploaded_file.getbuffer())
            elif hasattr(self.uploaded_file, 'read'):
                # Save current position
                pos = getattr(self.uploaded_file, 'tell', lambda: 0)()
                content = self.uploaded_file.read()
                # Reset file pointer if possible
                if hasattr(self.uploaded_file, 'seek'):
                    self.uploaded_file.seek(pos)
            else:
                # File path
                with open(self.uploaded_file, 'rb') as f:
                    content = f.read()
            
            # Use first 1KB + file size for faster hashing
            if len(content) > 1024:
                hash_content = content[:1024] + str(len(content)).encode()
            else:
                hash_content = content
            
            self._file_hash = hashlib.md5(hash_content).hexdigest()
            return self._file_hash
            
        except Exception as e:
            logger.warning(f"Could not generate file hash: {e}")
            return str(hash(str(self.uploaded_file)))

    @MemoryManager.memory_monitor
    def _read_excel_optimized(self) -> pd.ExcelFile:
        """Read Excel file with memory optimization"""
        file_hash = self._get_file_hash()
        cache_key = f"excel_file_{file_hash}"
        
        # Check cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info("Using cached Excel file")
            return cached_data
        
        try:
            # Read Excel file with optimizations
            excel_file = pd.ExcelFile(self.uploaded_file, engine='openpyxl')
            
            # Cache the Excel file object (but not the data)
            # Store only sheet names and file reference
            cached_info = {
                'sheet_names': excel_file.sheet_names,
                'file_ref': weakref.ref(excel_file)  # Weak reference to prevent memory leaks
            }
            
            self.cache.set(cache_key, excel_file)
            return excel_file
            
        except Exception as e:
            logger.error(f"Failed to read Excel file: {str(e)}")
            raise Exception(f"Cannot read Excel file: {str(e)}")

    @MemoryManager.memory_monitor
    def process_excel(self) -> Dict[str, Any]:
        """
        Memory-optimized Excel processing with intelligent caching
        
        Returns:
            Dict containing extracted data from all sheets
        """
        file_hash = self._get_file_hash()
        cache_key = f"processed_data_{file_hash}"
        
        # Check cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info("Using cached processed data")
            return cached_data
        
        try:
            # Monitor memory at start
            initial_memory = MemoryManager.get_memory_usage()
            logger.info(f"Starting Excel processing. Memory: {initial_memory['rss_mb']:.1f}MB ({initial_memory['percent']:.1f}%)")
            
            # Read Excel file
            excel_data = self._read_excel_optimized()
            
            # Initialize data dictionary
            data = {}
            
            # Process sheets with memory monitoring
            sheet_processors = {
                'Title': ('title_data', self._process_title_sheet_optimized),
                'Work Order': ('work_order_data', self._process_work_order_sheet_optimized),
                'Bill Quantity': ('bill_quantity_data', self._process_bill_quantity_sheet_optimized),
                'Extra Items': ('extra_items_data', self._process_extra_items_sheet_optimized)
            }
            
            for sheet_name, (data_key, processor) in sheet_processors.items():
                if sheet_name in excel_data.sheet_names:
                    try:
                        logger.info(f"Processing {sheet_name} sheet...")
                        sheet_data = processor(excel_data, sheet_name)
                        data[data_key] = sheet_data
                        
                        # Memory check after each sheet
                        current_memory = MemoryManager.get_memory_usage()
                        if current_memory['percent'] > self._memory_threshold:
                            freed = MemoryManager.force_gc()
                            logger.warning(f"Memory cleanup freed {freed:.1f}MB after processing {sheet_name}")
                        
                    except Exception as e:
                        if sheet_name == 'Extra Items':
                            logger.warning(f"Optional sheet {sheet_name} processing failed: {str(e)}")
                            data['extra_items_data'] = pd.DataFrame()
                        else:
                            logger.error(f"Critical sheet {sheet_name} processing failed: {str(e)}")
                            raise Exception(f"Critical sheet '{sheet_name}' processing failed: {str(e)}")
                else:
                    if sheet_name == 'Extra Items':
                        data['extra_items_data'] = pd.DataFrame()
                    else:
                        logger.warning(f"Required sheet '{sheet_name}' not found")
            
            # Cache the processed data
            self.cache.set(cache_key, data)
            
            # Final memory cleanup
            final_memory = MemoryManager.get_memory_usage()
            memory_used = final_memory['rss_mb'] - initial_memory['rss_mb']
            logger.info(f"Excel processing complete. Memory used: {memory_used:+.1f}MB, Final: {final_memory['rss_mb']:.1f}MB")
            
            return data
            
        except Exception as e:
            # Cleanup on error
            MemoryManager.force_gc()
            logger.error(f"Excel processing failed: {str(e)}")
            raise Exception(f"Error processing Excel file: {str(e)}")

    def _create_flexible_column_mapping(self, columns: List[str]) -> Dict[str, str]:
        """Create flexible column mapping for various naming conventions"""
        column_patterns = {
            'Item': ['item', 'sl', 'serial', 'no', 'number', 'item no', 'item number', 'sl no'],
            'Description': ['description', 'desc', 'particular', 'work', 'item description'],
            'Unit': ['unit', 'uom', 'unit of measure', 'measurement'],
            'Quantity': ['quantity', 'qty', 'amount', 'count'],
            'Rate': ['rate', 'unit rate', 'price', 'cost'],
            'Amount': ['amount', 'total', 'value', 'sum']
        }
        
        mapping = {}
        columns_lower = [str(col).lower().strip() for col in columns]
        
        for standard_name, patterns in column_patterns.items():
            for col, col_lower in zip(columns, columns_lower):
                if any(pattern in col_lower for pattern in patterns):
                    mapping[col] = standard_name
                    break
        
        return mapping

    @MemoryManager.memory_monitor
    def _process_title_sheet_optimized(self, excel_data: pd.ExcelFile, sheet_name: str) -> Dict[str, str]:
        """Memory-optimized title sheet processing"""
        try:
            # Try different configurations for robustness
            for header_config in [None, 0, 1]:
                try:
                    # Read with minimal memory footprint
                    title_df = pd.read_excel(excel_data, sheet_name=sheet_name, header=header_config, nrows=50)
                    
                    # Skip empty rows
                    title_df = title_df.dropna(how='all')
                    
                    if title_df.empty or len(title_df.columns) < 2:
                        continue
                    
                    # Convert to dictionary with optimized processing
                    title_data = {}
                    
                    # Process only first two columns for key-value pairs
                    for index, row in title_df.iterrows():
                        try:
                            key_val = row.iloc[0] if not pd.isna(row.iloc[0]) else None
                            val_val = row.iloc[1] if len(row) > 1 and not pd.isna(row.iloc[1]) else None
                            
                            if key_val is not None and val_val is not None:
                                key = str(key_val).strip()
                                val = str(val_val).strip()
                                
                                if key and val and key != 'nan' and val != 'nan':
                                    title_data[key] = val
                        except Exception:
                            continue
                    
                    # Cleanup DataFrame immediately
                    del title_df
                    gc.collect()
                    
                    if title_data:
                        return title_data
                        
                except Exception:
                    continue
            
            logger.warning("Could not extract title data, returning empty structure")
            return {}
            
        except Exception as e:
            logger.error(f"Title sheet processing error: {str(e)}")
            return {}

    @MemoryManager.memory_monitor
    def _process_work_order_sheet_optimized(self, excel_data: pd.ExcelFile, sheet_name: str) -> pd.DataFrame:
        """Memory-optimized work order processing with chunked processing"""
        try:
            df_result = None
            
            # Try different header configurations
            for header_row in [0, 1, 2]:
                try:
                    # Read with memory optimization
                    df = pd.read_excel(excel_data, sheet_name=sheet_name, header=header_row)
                    
                    # Basic validation
                    if df.empty or all('Unnamed' in str(col) for col in df.columns):
                        del df
                        continue
                    
                    # Apply flexible column mapping
                    column_map = self._create_flexible_column_mapping(df.columns)
                    if not column_map:
                        del df
                        continue
                    
                    df = df.rename(columns=column_map)
                    
                    # Standardize column names
                    final_columns = {
                        'Item': 'Item No.',
                        'Description': 'Description',
                        'Unit': 'Unit',
                        'Quantity': 'Quantity Since',
                        'Rate': 'Rate',
                        'Amount': 'Amount Since'
                    }
                    
                    for old_col, new_col in final_columns.items():
                        if old_col in df.columns and old_col != new_col:
                            df = df.rename(columns={old_col: new_col})
                    
                    # Add missing columns with memory-efficient defaults
                    required_columns = ['Item No.', 'Description', 'Unit', 'Quantity Since', 'Rate', 'Amount Since']
                    for col in required_columns:
                        if col not in df.columns:
                            if any(x in col for x in ['Quantity', 'Rate', 'Amount']):
                                df[col] = 0.0
                            else:
                                df[col] = ''
                    
                    # Add derived columns
                    df['Quantity Upto'] = df.get('Quantity Since', 0)
                    df['Amount Upto'] = df.get('Amount Since', 0)
                    df['Remark'] = ''
                    
                    # Process in chunks for large datasets
                    df_result = ChunkedDataProcessor.process_dataframe_chunked(df)
                    
                    # Cleanup original DataFrame
                    del df
                    gc.collect()
                    
                    if not df_result.empty:
                        return df_result
                        
                except Exception as e:
                    logger.warning(f"Failed header row {header_row} for {sheet_name}: {str(e)}")
                    continue
            
            raise Exception(f"Could not process {sheet_name} sheet with any header configuration")
            
        except Exception as e:
            logger.error(f"Work order processing error: {str(e)}")
            raise Exception(f"Error processing {sheet_name} sheet: {str(e)}")

    @MemoryManager.memory_monitor
    def _process_bill_quantity_sheet_optimized(self, excel_data: pd.ExcelFile, sheet_name: str) -> pd.DataFrame:
        """Memory-optimized bill quantity processing"""
        try:
            # Similar approach to work order but with bill quantity specific logic
            for header_row in [0, 1, 2]:
                try:
                    df = pd.read_excel(excel_data, sheet_name=sheet_name, header=header_row)
                    
                    if df.empty or all('Unnamed' in str(col) for col in df.columns):
                        del df
                        continue
                    
                    # Flexible column mapping
                    column_map = self._create_flexible_column_mapping(df.columns)
                    if not column_map:
                        del df
                        continue
                    
                    df = df.rename(columns=column_map)
                    
                    # Standard column mapping for bill quantity
                    standard_columns = {
                        'Item': 'Item No.',
                        'Description': 'Description',
                        'Unit': 'Unit',
                        'Quantity': 'Quantity',
                        'Rate': 'Rate',
                        'Amount': 'Amount'
                    }
                    
                    for old_col, new_col in standard_columns.items():
                        if old_col in df.columns:
                            df = df.rename(columns={old_col: new_col})
                    
                    # Add missing required columns
                    for col in ['Item No.', 'Description', 'Unit', 'Quantity', 'Rate', 'Amount']:
                        if col not in df.columns:
                            if col in ['Quantity', 'Rate', 'Amount']:
                                df[col] = 0.0
                            else:
                                df[col] = ''
                    
                    # Process with chunked method for memory efficiency
                    result = ChunkedDataProcessor.process_dataframe_chunked(df)
                    
                    # Cleanup
                    del df
                    gc.collect()
                    
                    if not result.empty:
                        return result
                        
                except Exception as e:
                    logger.warning(f"Failed header row {header_row} for {sheet_name}: {str(e)}")
                    continue
            
            raise Exception(f"Could not process {sheet_name} sheet")
            
        except Exception as e:
            logger.error(f"Bill quantity processing error: {str(e)}")
            raise Exception(f"Error processing {sheet_name} sheet: {str(e)}")

    @MemoryManager.memory_monitor
    def _process_extra_items_sheet_optimized(self, excel_data: pd.ExcelFile, sheet_name: str) -> pd.DataFrame:
        """Memory-optimized extra items processing"""
        try:
            # Try different header configurations for robustness
            for header_row in [0, 1, 2, 3]:
                try:
                    df = pd.read_excel(excel_data, sheet_name=sheet_name, header=header_row, nrows=100)
                    
                    # Check if we have meaningful columns
                    if df.empty or all('Unnamed' in str(col) for col in df.columns):
                        del df
                        continue
                    
                    # Flexible column mapping
                    column_map = self._create_flexible_column_mapping(df.columns)
                    if column_map:
                        df = df.rename(columns=column_map)
                        
                        # Standard column names
                        for old_col, new_col in {'Item': 'Item No.', 'Quantity': 'Quantity'}.items():
                            if old_col in df.columns:
                                df = df.rename(columns={old_col: new_col})
                        
                        # Process with memory optimization
                        result = ChunkedDataProcessor.process_dataframe_chunked(df)
                        
                        # Cleanup
                        del df
                        gc.collect()
                        
                        if not result.empty:
                            return result
                    
                    del df
                    
                except Exception:
                    continue
            
            # If all attempts failed, return empty DataFrame
            logger.info("No valid extra items data found, returning empty DataFrame")
            return pd.DataFrame()
            
        except Exception as e:
            logger.warning(f"Extra items processing error: {str(e)}")
            return pd.DataFrame()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get caching statistics"""
        return self.cache.get_stats()
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        MemoryManager.force_gc()

# Utility functions for backwards compatibility
def create_optimized_processor(uploaded_file, cache_size: int = 50):
    """Factory function to create optimized Excel processor"""
    return ExcelProcessorMemoryOptimized(uploaded_file, cache_size)
