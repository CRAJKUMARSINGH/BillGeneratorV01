import pandas as pd
import io
import hashlib
from typing import Dict, Any
from functools import lru_cache
import sys
import os
import gc

from .dataframe_safety_utils import DataFrameSafetyUtils
# Add import for FirstPageGenerator
from .first_page_generator import FirstPageGenerator

class ExcelProcessor:
    """Handles Excel file processing and data extraction"""
    
    # Class-level cache for processed files
    _file_cache = {}
    _cache_max_size = 75  # Limit cache size to prevent memory issues
    
    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
        self.workbook = None
        self._file_hash = None
    
    def _get_file_hash(self):
        """Generate hash for file caching"""
        if self._file_hash is None:
            if hasattr(self.uploaded_file, 'read'):
                # For file-like objects, we can't reliably hash without consuming
                # So we'll use a combination of size and name if available
                if hasattr(self.uploaded_file, 'name'):
                    self._file_hash = f"{getattr(self.uploaded_file, 'name', 'unknown')}_{hash(str(self.uploaded_file))}"
                else:
                    self._file_hash = str(id(self.uploaded_file))
            else:
                # For file paths, we can hash the file content
                try:
                    hash_md5 = hashlib.md5()
                    with open(self.uploaded_file, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_md5.update(chunk)
                    self._file_hash = hash_md5.hexdigest()
                except:
                    self._file_hash = str(self.uploaded_file)
        return self._file_hash
    
    def process_excel_file(self, uploaded_file) -> Dict[str, Any]:
        """Process Excel file - compatibility method for enhanced_app.py"""
        # Update the uploaded file and process it
        self.uploaded_file = uploaded_file
        return self.process_excel()
    
    def _safe_read_excel(self):
        """
        Safely read Excel file with comprehensive error handling for common access issues
        """
        import time
        import os
        
        max_retries = 3
        retry_delay = 1  # seconds
        
        # Check cache first
        file_hash = self._get_file_hash()
        if file_hash in self._file_cache:
            print("Using cached Excel data")
            return self._file_cache[file_hash]
        
        for attempt in range(max_retries):
            try:
                # Read Excel file - handle both file paths and file-like objects
                if hasattr(self.uploaded_file, 'read'):
                    # It's a file-like object (like Streamlit uploaded file)
                    # Reset file pointer to beginning
                    if hasattr(self.uploaded_file, 'seek'):
                        self.uploaded_file.seek(0)
                    excel_data = pd.ExcelFile(self.uploaded_file)
                else:
                    # It's a file path - check if file exists and is accessible
                    if not os.path.exists(self.uploaded_file):
                        raise FileNotFoundError(f"File not found: {self.uploaded_file}")
                    
                    # Check file permissions
                    if not os.access(self.uploaded_file, os.R_OK):
                        raise PermissionError(f"No read permission for file: {self.uploaded_file}")
                    
                    excel_data = pd.ExcelFile(self.uploaded_file)
                
                # Cache the result if we have space
                if len(self._file_cache) < self._cache_max_size:
                    self._file_cache[file_hash] = excel_data
                
                return excel_data
                
            except PermissionError as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise Exception(f"File access denied. Please close the Excel file if it's open in another program. Error: {str(e)}")
            
            except FileNotFoundError as e:
                raise Exception(f"File not found. Please check the file path. Error: {str(e)}")
            
            except pd.errors.EmptyDataError:
                raise Exception("The Excel file appears to be empty or corrupted. Please check the file and try again.")
            
            except Exception as excel_error:
                # Handle various Excel-related errors
                error_message = str(excel_error).lower()
                if "permission denied" in error_message or "access" in error_message:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    raise Exception(f"File access issue. Please close the Excel file if it's open in another program. Error: {str(excel_error)}")
                elif "not a valid excel" in error_message or "unsupported format" in error_message:
                    raise Exception(f"Excel file format error. Please ensure the file is a valid Excel file (.xlsx or .xls). Error: {str(excel_error)}")
                elif "permission" in error_message or "locked" in error_message:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    raise Exception(f"File access issue. Please close the Excel file if it's open in another program. Error: {str(excel_error)}")
                else:
                    raise Exception(f"Error reading Excel file: {str(excel_error)}")
        
        raise Exception("Failed to read Excel file after multiple attempts. Please check file permissions and ensure it's not open in another program.")
    
    def process_excel(self, allow_missing_bill_quantity: bool = False) -> Dict[str, Any]:
        """
        Process uploaded Excel file and extract data from all required sheets
        
        Returns:
            Dict containing extracted data from all sheets
        """
        try:
            # Enhanced file access with better error handling
            excel_data = self._safe_read_excel()
            
            # Debug: Print available sheet names
            print(f"Available sheets: {excel_data.sheet_names}")
            
            # Initialize data dictionary
            data = {}
            
            # Process Title sheet
            if 'Title' in excel_data.sheet_names:
                print("Processing Title sheet...")
                data['title_data'] = self._process_title_sheet(excel_data)
                print(f"Title data extracted: {len(data['title_data'])} items")
            else:
                print("WARNING: Title sheet not found")
                data['title_data'] = {}
            
            # Process Work Order sheet
            if 'Work Order' in excel_data.sheet_names:
                print("Processing Work Order sheet...")
                data['work_order_data'] = self._process_work_order_sheet(excel_data)
                print(f"Work Order data extracted: {len(data['work_order_data'])} rows")
            else:
                print("ERROR: Work Order sheet not found - this is required!")
                raise Exception("Required 'Work Order' sheet not found in Excel file")
            
            # Process Bill Quantity sheet
            if 'Bill Quantity' in excel_data.sheet_names:
                print("Processing Bill Quantity sheet...")
                data['bill_quantity_data'] = self._process_bill_quantity_sheet(excel_data)
                print(f"Bill Quantity data extracted: {len(data['bill_quantity_data'])} rows")
            else:
                if allow_missing_bill_quantity:
                    print("INFO: Bill Quantity sheet not found - allowed for partial processing")
                    data['bill_quantity_data'] = pd.DataFrame()
                else:
                    print("ERROR: Bill Quantity sheet not found - this is required!")
                    raise Exception("Required 'Bill Quantity' sheet not found in Excel file")
            
            # Process Extra Items sheet (optional)
            if 'Extra Items' in excel_data.sheet_names:
                print("Processing Extra Items sheet...")
                data['extra_items_data'] = self._process_extra_items_sheet(excel_data)
                print(f"Extra Items data extracted: {len(data['extra_items_data'])} rows")
            else:
                print("INFO: Extra Items sheet not found - this is optional")
                data['extra_items_data'] = pd.DataFrame()
            
            # Validate that we have essential data
            if allow_missing_bill_quantity:
                # Only require work order data when partial processing
                if DataFrameSafetyUtils.is_valid_dataframe(data.get('work_order_data')):
                    print("SUCCESS: Work Order data extracted successfully (partial mode)")
                    gc.collect()
                    return data
                else:
                    raise Exception("No valid Work Order data found. Please check your Excel file format.")
            elif (DataFrameSafetyUtils.is_valid_dataframe(data.get('work_order_data')) and 
                  DataFrameSafetyUtils.is_valid_dataframe(data.get('bill_quantity_data'))):
                print("SUCCESS: All required data extracted successfully")
                
                # Force garbage collection after processing
                gc.collect()
                return data
            else:
                raise Exception("No valid data found in required sheets. Please check your Excel file format.")
            
        except Exception as e:
            print(f"ERROR in process_excel: {str(e)}")
            raise Exception(f"Error processing Excel file: {str(e)}")
        finally:
            # Clean up workbook reference
            if hasattr(self, 'workbook'):
                del self.workbook
                self.workbook = None
            gc.collect()
    
    def _process_title_sheet(self, excel_data) -> Dict[str, str]:
        """Extract metadata from Title sheet"""
        try:
            title_df = pd.read_excel(excel_data, sheet_name='Title', header=None)
            print(f"Title sheet shape: {title_df.shape}")
            print(f"Title sheet columns: {list(title_df.columns)}")
            
            # Convert to dictionary - assuming key-value pairs in adjacent columns
            title_data = {}
            for index, row in title_df.iterrows():
                # Fix linter error by using scalar boolean check
                if row[0] is not None and row[0] is not pd.NaT and row[0] is not pd.NA and \
                   row[1] is not None and row[1] is not pd.NaT and row[1] is not pd.NA:
                    key = str(row[0]).strip()
                    val = str(row[1]).strip()
                    if key and val and key != 'nan' and val != 'nan':
                        title_data[key] = val
            
            print(f"Title data extracted: {title_data}")
            
            # Force garbage collection
            gc.collect()
            return title_data
            
        except Exception as e:
            print(f"Error in _process_title_sheet: {str(e)}")
            raise Exception(f"Error processing Title sheet: {str(e)}")
    
    def _process_work_order_sheet(self, excel_data) -> pd.DataFrame:
        """Extract work order data with memory optimization"""
        try:
            # Read with chunking for large files and optimize data types
            work_order_df = pd.read_excel(
                excel_data, 
                sheet_name='Work Order', 
                header=0,
                dtype_backend='numpy_nullable'  # Use more memory-efficient data types
            )
            
            print(f"Work Order sheet shape: {work_order_df.shape}")
            print(f"Work Order columns: {list(work_order_df.columns)}")
            print(f"First few rows:\n{work_order_df.head()}")
            
            # Optimize memory usage by converting data types
            for col in work_order_df.columns:
                if work_order_df[col].dtype == 'object':
                    # Try to convert to category if there are repeated values
                    unique_vals = work_order_df[col].nunique()
                    if unique_vals > 0 and unique_vals / len(work_order_df) < 0.5:
                        work_order_df[col] = work_order_df[col].astype('category')
                elif work_order_df[col].dtype == 'float64':
                    # Downcast floats if possible
                    work_order_df[col] = pd.to_numeric(work_order_df[col], downcast='float')
                elif work_order_df[col].dtype == 'int64':
                    # Downcast integers if possible
                    work_order_df[col] = pd.to_numeric(work_order_df[col], downcast='integer')
            
            # Standardize column names to match expected format
            column_mapping = {
                'Item': 'Item No.',
                'Description': 'Description',
                'Unit': 'Unit',
                'Quantity': 'Quantity Since',  # Map to expected column
                'Rate': 'Rate',
                'Amount': 'Amount Since'  # Map to expected column
            }
            
            # Rename columns if they exist
            for old_col, new_col in column_mapping.items():
                if old_col in work_order_df.columns:
                    work_order_df = work_order_df.rename(columns={old_col: new_col})
                    print(f"Renamed column: {old_col} -> {new_col}")
            
            # Add missing columns with default values
            if 'Quantity Upto' not in work_order_df.columns:
                work_order_df['Quantity Upto'] = work_order_df.get('Quantity Since', 0)
            
            # Force garbage collection
            gc.collect()
            return work_order_df
            
        except Exception as e:
            print(f"Error in _process_work_order_sheet: {str(e)}")
            raise Exception(f"Error processing Work Order sheet: {str(e)}")
    
    def _process_bill_quantity_sheet(self, excel_data) -> pd.DataFrame:
        """Extract bill quantity data with memory optimization"""
        try:
            # Read with optimized data types
            bill_quantity_df = pd.read_excel(
                excel_data, 
                sheet_name='Bill Quantity', 
                header=0,
                dtype_backend='numpy_nullable'  # Use more memory-efficient data types
            )
            
            print(f"Bill Quantity sheet shape: {bill_quantity_df.shape}")
            print(f"Bill Quantity columns: {list(bill_quantity_df.columns)}")
            
            # Optimize memory usage by converting data types
            for col in bill_quantity_df.columns:
                if bill_quantity_df[col].dtype == 'object':
                    # Try to convert to category if there are repeated values
                    unique_vals = bill_quantity_df[col].nunique()
                    if unique_vals > 0 and unique_vals / len(bill_quantity_df) < 0.5:
                        bill_quantity_df[col] = bill_quantity_df[col].astype('category')
                elif bill_quantity_df[col].dtype == 'float64':
                    # Downcast floats if possible
                    bill_quantity_df[col] = pd.to_numeric(bill_quantity_df[col], downcast='float')
                elif bill_quantity_df[col].dtype == 'int64':
                    # Downcast integers if possible
                    bill_quantity_df[col] = pd.to_numeric(bill_quantity_df[col], downcast='integer')
            
            # Standardize column names to match expected format
            column_mapping = {
                'Item': 'Item No.',
                'Description': 'Description',
                'Unit': 'Unit',
                'Quantity': 'Quantity',  # Keep as is for bill quantity
                'Rate': 'Rate',
                'Amount': 'Amount'
            }
            
            # Rename columns if they exist
            for old_col, new_col in column_mapping.items():
                if old_col in bill_quantity_df.columns:
                    bill_quantity_df = bill_quantity_df.rename(columns={old_col: new_col})
                    print(f"Renamed column: {old_col} -> {new_col}")
            
            # Force garbage collection
            gc.collect()
            return bill_quantity_df
            
        except Exception as e:
            print(f"Error in _process_bill_quantity_sheet: {str(e)}")
            raise Exception(f"Error processing Bill Quantity sheet: {str(e)}")
    
    def _process_extra_items_sheet(self, excel_data) -> pd.DataFrame:
        """Extract extra items data with memory optimization"""
        try:
            # Read with optimized data types
            extra_items_df = pd.read_excel(
                excel_data, 
                sheet_name='Extra Items', 
                header=0,
                dtype_backend='numpy_nullable'  # Use more memory-efficient data types
            )
            
            print(f"Extra Items sheet shape: {extra_items_df.shape}")
            print(f"Extra Items columns: {list(extra_items_df.columns)}")
            
            # Optimize memory usage by converting data types
            for col in extra_items_df.columns:
                if extra_items_df[col].dtype == 'object':
                    # Try to convert to category if there are repeated values
                    unique_vals = extra_items_df[col].nunique()
                    if unique_vals > 0 and unique_vals / len(extra_items_df) < 0.5:
                        extra_items_df[col] = extra_items_df[col].astype('category')
                elif extra_items_df[col].dtype == 'float64':
                    # Downcast floats if possible
                    extra_items_df[col] = pd.to_numeric(extra_items_df[col], downcast='float')
                elif extra_items_df[col].dtype == 'int64':
                    # Downcast integers if possible
                    extra_items_df[col] = pd.to_numeric(extra_items_df[col], downcast='integer')
            
            # Standardize column names to match expected format
            column_mapping = {
                'Item': 'Item No.',
                'Description': 'Description',
                'Unit': 'Unit',
                'Quantity': 'Quantity',
                'Rate': 'Rate',
                'Amount': 'Amount'
            }
            
            # Rename columns if they exist
            for old_col, new_col in column_mapping.items():
                if old_col in extra_items_df.columns:
                    extra_items_df = extra_items_df.rename(columns={old_col: new_col})
                    print(f"Renamed column: {old_col} -> {new_col}")
            
            # Force garbage collection
            gc.collect()
            return extra_items_df
            
        except Exception as e:
            print(f"Error in _process_extra_items_sheet: {str(e)}")
            raise Exception(f"Error processing Extra Items sheet: {str(e)}")