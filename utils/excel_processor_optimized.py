import pandas as pd
import io
import hashlib
from typing import Dict, Any, Optional, List
from functools import lru_cache
import gc
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelProcessorOptimized:
    """Enhanced Excel processor with performance optimizations and better error handling"""
    
    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
        self.workbook = None
        self._cached_data = {}
        
    def _get_file_hash(self) -> str:
        """Generate hash for file caching"""
        try:
            if hasattr(self.uploaded_file, 'getbuffer'):
                content = self.uploaded_file.getbuffer()
            elif hasattr(self.uploaded_file, 'read'):
                content = self.uploaded_file.read()
                # Reset file pointer if possible
                if hasattr(self.uploaded_file, 'seek'):
                    self.uploaded_file.seek(0)
            else:
                # File path
                with open(self.uploaded_file, 'rb') as f:
                    content = f.read()
            
            return hashlib.md5(content).hexdigest()
        except Exception:
            return str(hash(str(self.uploaded_file)))
    
    @lru_cache(maxsize=10)
    def _get_excel_file_cached(self, file_hash: str) -> pd.ExcelFile:
        """Cached Excel file reading"""
        try:
            if hasattr(self.uploaded_file, 'read'):
                return pd.ExcelFile(self.uploaded_file)
            else:
                return pd.ExcelFile(self.uploaded_file)
        except Exception as e:
            logger.error(f"Failed to read Excel file: {str(e)}")
            raise Exception(f"Cannot read Excel file: {str(e)}")
    
    def process_excel(self) -> Dict[str, Any]:
        """
        Enhanced Excel processing with performance optimizations
        
        Returns:
            Dict containing extracted data from all sheets
        """
        try:
            file_hash = self._get_file_hash()
            
            # Check cache first
            if file_hash in self._cached_data:
                logger.info("Using cached Excel data")
                return self._cached_data[file_hash]
            
            # Read Excel file
            excel_data = self._get_excel_file_cached(file_hash)
            
            # Initialize data dictionary
            data = {}
            
            # Process sheets in parallel-friendly order
            sheet_processors = {
                'Title': self._process_title_sheet_optimized,
                'Work Order': self._process_work_order_sheet_optimized,
                'Bill Quantity': self._process_bill_quantity_sheet_optimized,
                'Extra Items': self._process_extra_items_sheet_optimized
            }
            
            for sheet_name, processor in sheet_processors.items():
                if sheet_name in excel_data.sheet_names:
                    try:
                        data[f"{sheet_name.lower().replace(' ', '_')}_data"] = processor(excel_data, sheet_name)
                        logger.info(f"Processed {sheet_name} sheet successfully")
                    except Exception as e:
                        logger.warning(f"Failed to process {sheet_name} sheet: {str(e)}")
                        if sheet_name == 'Extra Items':
                            data['extra_items_data'] = pd.DataFrame()
                        else:
                            # For critical sheets, re-raise the error
                            raise Exception(f"Critical sheet '{sheet_name}' processing failed: {str(e)}")
                else:
                    if sheet_name == 'Extra Items':
                        data['extra_items_data'] = pd.DataFrame()
                    else:
                        logger.warning(f"Required sheet '{sheet_name}' not found")
            
            # Cache the result
            self._cached_data[file_hash] = data
            
            # Memory cleanup
            gc.collect()
            
            return data
            
        except Exception as e:
            logger.error(f"Excel processing failed: {str(e)}")
            raise Exception(f"Error processing Excel file: {str(e)}")
    
    def _process_title_sheet_optimized(self, excel_data: pd.ExcelFile, sheet_name: str) -> Dict[str, str]:
        """Optimized title sheet processing with better error handling"""
        try:
            # Try different configurations for robustness
            for header_config in [None, 0]:
                try:
                    title_df = pd.read_excel(excel_data, sheet_name=sheet_name, header=header_config)
                    
                    # Skip empty rows
                    title_df = title_df.dropna(how='all')
                    
                    if title_df.empty or len(title_df.columns) < 2:
                        continue
                    
                    # Convert to dictionary with improved key-value extraction
                    title_data = {}
                    
                    for index, row in title_df.iterrows():
                        try:
                            # Check multiple column combinations
                            key_col = row.iloc[0] if not pd.isna(row.iloc[0]) else None
                            val_col = row.iloc[1] if len(row) > 1 and not pd.isna(row.iloc[1]) else None
                            
                            if key_col is not None and val_col is not None:
                                key = str(key_col).strip()
                                val = str(val_col).strip()
                                
                                # Skip empty or invalid entries
                                if key and val and key != 'nan' and val != 'nan':
                                    title_data[key] = val
                        except Exception:
                            continue
                    
                    if title_data:  # If we got some data, return it
                        return title_data
                        
                except Exception:
                    continue
            
            # If all attempts failed, return minimal data structure
            logger.warning("Could not extract title data, returning empty structure")
            return {}
            
        except Exception as e:
            logger.error(f"Title sheet processing error: {str(e)}")
            return {}
    
    def _process_work_order_sheet_optimized(self, excel_data: pd.ExcelFile, sheet_name: str) -> pd.DataFrame:
        """Optimized work order processing with flexible column mapping"""
        try:
            # Try different header configurations
            for header_row in [0, 1, 2]:
                try:
                    df = pd.read_excel(excel_data, sheet_name=sheet_name, header=header_row)
                    
                    # Check if we have meaningful columns
                    if df.empty or all('Unnamed' in str(col) for col in df.columns):
                        continue
                    
                    # Flexible column mapping
                    column_map = self._create_flexible_column_mapping(df.columns)
                    
                    if not column_map:  # No recognizable columns
                        continue
                    
                    # Apply column mapping
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
                    
                    # Add missing columns with default values
                    required_columns = ['Item No.', 'Description', 'Unit', 'Quantity Since', 'Rate', 'Amount Since']
                    for col in required_columns:
                        if col not in df.columns:
                            if 'Quantity' in col:
                                df[col] = 0.0
                            elif 'Rate' in col or 'Amount' in col:
                                df[col] = 0.0
                            else:
                                df[col] = ''
                    
                    # Add derived columns
                    if 'Quantity Upto' not in df.columns:
                        df['Quantity Upto'] = df.get('Quantity Since', 0)
                    if 'Amount Upto' not in df.columns:
                        df['Amount Upto'] = df.get('Amount Since', 0)
                    if 'Remark' not in df.columns:
                        df['Remark'] = ''
                    
                    # Data cleaning and filtering
                    df = self._clean_dataframe(df)
                    
                    if not df.empty:
                        return df
                        
                except Exception as e:
                    logger.warning(f"Failed header row {header_row} for {sheet_name}: {str(e)}")
                    continue
            
            raise Exception(f"Could not process {sheet_name} sheet with any header configuration")
            
        except Exception as e:
            logger.error(f"Work order processing error: {str(e)}")
            raise Exception(f"Error processing {sheet_name} sheet: {str(e)}")
    
    def _process_bill_quantity_sheet_optimized(self, excel_data: pd.ExcelFile, sheet_name: str) -> pd.DataFrame:
        """Optimized bill quantity processing"""
        try:
            # Similar approach to work order but with bill quantity specific logic
            for header_row in [0, 1, 2]:
                try:
                    df = pd.read_excel(excel_data, sheet_name=sheet_name, header=header_row)
                    
                    if df.empty or all('Unnamed' in str(col) for col in df.columns):
                        continue
                    
                    # Flexible column mapping
                    column_map = self._create_flexible_column_mapping(df.columns)
                    
                    if not column_map:
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
                        if old_col in df.columns and old_col != new_col:
                            df = df.rename(columns={old_col: new_col})
                    
                    # Ensure required columns exist
                    required_columns = ['Item No.', 'Description', 'Unit', 'Quantity', 'Rate', 'Amount']
                    for col in required_columns:
                        if col not in df.columns:
                            if col in ['Quantity', 'Rate', 'Amount']:
                                df[col] = 0.0
                            else:
                                df[col] = ''
                    
                    # Clean data
                    df = self._clean_dataframe(df)
                    
                    if not df.empty:
                        return df
                        
                except Exception as e:
                    logger.warning(f"Failed header row {header_row} for {sheet_name}: {str(e)}")
                    continue
            
            raise Exception(f"Could not process {sheet_name} sheet")
            
        except Exception as e:
            logger.error(f"Bill quantity processing error: {str(e)}")
            raise Exception(f"Error processing {sheet_name} sheet: {str(e)}")
    
    def _process_extra_items_sheet_optimized(self, excel_data: pd.ExcelFile, sheet_name: str) -> pd.DataFrame:
        """Optimized extra items processing with multiple fallback strategies"""
        try:
            # Extra items sheet can have very different formats
            for header_row in range(0, 5):  # Try more header positions
                try:
                    df = pd.read_excel(excel_data, sheet_name=sheet_name, header=header_row)
                    
                    if df.empty:
                        continue
                    
                    # Check if this looks like a data row (not header/title)
                    first_row = df.iloc[0] if not df.empty else None
                    if first_row is not None:
                        # Look for numeric or recognizable data in first row
                        numeric_cols = sum(1 for val in first_row if pd.api.types.is_numeric_dtype(type(val)) or 
                                         (isinstance(val, str) and val.replace('.', '').replace('-', '').isdigit()))
                        
                        if numeric_cols < 2:  # Not enough numeric data, probably header/title row
                            continue
                    
                    # Try to identify meaningful columns
                    column_map = self._create_flexible_column_mapping(df.columns, include_extra_patterns=True)
                    
                    if column_map:
                        df = df.rename(columns=column_map)
                        df = self._clean_dataframe(df, min_rows=1)  # More lenient for extra items
                        
                        if not df.empty:
                            return df
                    
                except Exception:
                    continue
            
            # If all attempts failed, return empty DataFrame (extra items are optional)
            logger.info("No valid extra items data found, returning empty DataFrame")
            return pd.DataFrame()
            
        except Exception as e:
            logger.warning(f"Extra items processing warning: {str(e)}")
            return pd.DataFrame()
    
    def _create_flexible_column_mapping(self, columns: List[str], include_extra_patterns: bool = False) -> Dict[str, str]:
        """Create flexible column mapping based on column names"""
        mapping = {}
        
        # Normalize column names for comparison
        normalized_cols = {str(col).lower().strip(): col for col in columns}
        
        # Define pattern mappings
        patterns = {
            'Item': ['item', 'item no', 'item number', 'sl no', 'sr no', 'serial'],
            'Description': ['description', 'desc', 'work', 'item of work', 'particulars'],
            'Unit': ['unit', 'units', 'uom', 'unit of measurement'],
            'Quantity': ['quantity', 'qty', 'quantities', 'nos', 'number'],
            'Rate': ['rate', 'rates', 'price', 'unit rate', 'cost'],
            'Amount': ['amount', 'amounts', 'total', 'cost', 'value']
        }
        
        # Additional patterns for extra items
        if include_extra_patterns:
            patterns.update({
                'Extra Item': ['extra', 'additional', 'addon'],
                'Remarks': ['remark', 'remarks', 'note', 'notes', 'comment']
            })
        
        # Match patterns to actual column names
        for standard_name, pattern_list in patterns.items():
            for pattern in pattern_list:
                for norm_col, orig_col in normalized_cols.items():
                    if pattern in norm_col:
                        mapping[orig_col] = standard_name
                        break
                if standard_name in mapping.values():
                    break
        
        return {v: k for k, v in mapping.items()}  # Reverse for rename operation
    
    def _clean_dataframe(self, df: pd.DataFrame, min_rows: int = 5) -> pd.DataFrame:
        """Clean and validate DataFrame"""
        try:
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Find quantity column for filtering
            qty_columns = [col for col in df.columns if 'quantity' in str(col).lower() or 'qty' in str(col).lower()]
            
            if qty_columns:
                qty_col = qty_columns[0]
                # Filter out rows with zero, negative, or invalid quantities
                df = df[df[qty_col].notna()]
                df = df[pd.to_numeric(df[qty_col], errors='coerce') > 0]
            
            # Remove rows where key columns are all empty
            key_columns = ['Item No.', 'Item', 'Description']
            existing_key_cols = [col for col in key_columns if col in df.columns]
            
            if existing_key_cols:
                df = df.dropna(subset=existing_key_cols, how='all')
            
            # Ensure minimum data quality
            if len(df) < min_rows and min_rows > 1:
                logger.warning(f"DataFrame has only {len(df)} rows, below minimum of {min_rows}")
            
            return df
            
        except Exception as e:
            logger.error(f"DataFrame cleaning error: {str(e)}")
            return df  # Return uncleaned data rather than failing
