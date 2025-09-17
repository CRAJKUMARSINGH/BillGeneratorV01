import pandas as pd
import io
import pandas as pd
import hashlib
from typing import Dict, Any
from functools import lru_cache

class ExcelProcessor:
    """Handles Excel file processing and data extraction"""
    
    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
        self.workbook = None
    
    def _safe_read_excel(self):
        """
        Safely read Excel file with comprehensive error handling for common access issues
        """
        import time
        import os
        
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                # Read Excel file - handle both file paths and file-like objects
                if hasattr(self.uploaded_file, 'read'):
                    # It's a file-like object (like Streamlit uploaded file)
                    excel_data = pd.ExcelFile(self.uploaded_file)
                else:
                    # It's a file path - check if file exists and is accessible
                    if not os.path.exists(self.uploaded_file):
                        raise FileNotFoundError(f"File not found: {self.uploaded_file}")
                    
                    # Check file permissions
                    if not os.access(self.uploaded_file, os.R_OK):
                        raise PermissionError(f"No read permission for file: {self.uploaded_file}")
                    
                    excel_data = pd.ExcelFile(self.uploaded_file)
                
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
    
    def process_excel(self) -> Dict[str, Any]:
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
            if not data.get('work_order_data', pd.DataFrame()).empty and not data.get('bill_quantity_data', pd.DataFrame()).empty:
                print("SUCCESS: All required data extracted successfully")
                return data
            else:
                raise Exception("No valid data found in required sheets. Please check your Excel file format.")
            
        except Exception as e:
            print(f"ERROR in process_excel: {str(e)}")
            raise Exception(f"Error processing Excel file: {str(e)}")
    
    def _process_title_sheet(self, excel_data) -> Dict[str, str]:
        """Extract metadata from Title sheet"""
        try:
            title_df = pd.read_excel(excel_data, sheet_name='Title', header=None)
            print(f"Title sheet shape: {title_df.shape}")
            print(f"Title sheet columns: {list(title_df.columns)}")
            
            # Convert to dictionary - assuming key-value pairs in adjacent columns
            title_data = {}
            for index, row in title_df.iterrows():
                if pd.notna(row[0]) and pd.notna(row[1]):
                    key = str(row[0]).strip()
                    val = str(row[1]).strip()
                    if key and val and key != 'nan' and val != 'nan':
                        title_data[key] = val
            
            print(f"Title data extracted: {title_data}")
            return title_data
            
        except Exception as e:
            print(f"Error in _process_title_sheet: {str(e)}")
            raise Exception(f"Error processing Title sheet: {str(e)}")
    
    def _process_work_order_sheet(self, excel_data) -> pd.DataFrame:
        """Extract work order data"""
        try:
            work_order_df = pd.read_excel(excel_data, sheet_name='Work Order', header=0)
            print(f"Work Order sheet shape: {work_order_df.shape}")
            print(f"Work Order columns: {list(work_order_df.columns)}")
            print(f"First few rows:\n{work_order_df.head()}")
            
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
            if 'Amount Upto' not in work_order_df.columns:
                work_order_df['Amount Upto'] = work_order_df.get('Amount Since', 0)
            if 'Remark' not in work_order_df.columns:
                work_order_df['Remark'] = ''
            
            # Find quantity column with flexible naming
            qty_column = None
            for col in work_order_df.columns:
                if 'quantity' in str(col).lower() or 'qty' in str(col).lower():
                    qty_column = col
                    break
            
            print(f"Using quantity column: {qty_column}")
            
            if qty_column:
                # Preserve main specification items even with zero quantity
                # Only remove rows that are completely empty or have no description
                before_count = len(work_order_df)
                
                # Keep rows if they have:
                # 1. Non-zero quantity, OR
                # 2. A meaningful description (likely main specification), OR
                # 3. An item number (specification header)
                mask = (
                    (pd.notna(work_order_df[qty_column]) & (work_order_df[qty_column] != 0)) |  # Has quantity
                    (pd.notna(work_order_df.get('Description', pd.Series())) & 
                     work_order_df.get('Description', pd.Series()).astype(str).str.strip().str.len() > 0) |  # Has description
                    (pd.notna(work_order_df.get('Item No.', pd.Series())) & 
                     work_order_df.get('Item No.', pd.Series()).astype(str).str.strip().str.len() > 0)  # Has item number
                )
                
                work_order_df = work_order_df[mask]
                after_count = len(work_order_df)
                print(f"Smart filtered rows: {before_count} -> {after_count} (preserved main specifications)")
            
            print(f"Final Work Order data shape: {work_order_df.shape}")
            return work_order_df
            
        except Exception as e:
            print(f"Error in _process_work_order_sheet: {str(e)}")
            raise Exception(f"Error processing Work Order sheet: {str(e)}")
    
    def _process_bill_quantity_sheet(self, excel_data) -> pd.DataFrame:
        """Extract bill quantity data"""
        try:
            bill_qty_df = pd.read_excel(excel_data, sheet_name='Bill Quantity', header=0)
            
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
                if old_col in bill_qty_df.columns:
                    bill_qty_df = bill_qty_df.rename(columns={old_col: new_col})
            
            # Find quantity column with flexible naming
            qty_column = None
            for col in bill_qty_df.columns:
                if 'quantity' in str(col).lower() or 'qty' in str(col).lower():
                    qty_column = col
                    break
            
            if qty_column:
                # Preserve main specification items even with zero quantity
                # Keep rows if they have:
                # 1. Non-zero quantity, OR
                # 2. A meaningful description (likely main specification), OR
                # 3. An item number (specification header)
                mask = (
                    (pd.notna(bill_qty_df[qty_column]) & (bill_qty_df[qty_column] != 0)) |  # Has quantity
                    (pd.notna(bill_qty_df.get('Description', pd.Series())) & 
                     bill_qty_df.get('Description', pd.Series()).astype(str).str.strip().str.len() > 0) |  # Has description
                    (pd.notna(bill_qty_df.get('Item No.', pd.Series())) & 
                     bill_qty_df.get('Item No.', pd.Series()).astype(str).str.strip().str.len() > 0)  # Has item number
                )
                
                bill_qty_df = bill_qty_df[mask]
                print(f"Smart filtered bill quantity rows (preserved main specifications)")
            
            return bill_qty_df
            
        except Exception as e:
            raise Exception(f"Error processing Bill Quantity sheet: {str(e)}")
    
    def _process_extra_items_sheet(self, excel_data) -> pd.DataFrame:
        """Extract extra items data"""
        try:
            # Try to read with different header rows since the format is inconsistent
            extra_items_df = None
            
            # First try with header=0
            try:
                extra_items_df = pd.read_excel(excel_data, sheet_name='Extra Items', header=0)
                # Check if we have meaningful column names
                if all('Unnamed' in str(col) for col in extra_items_df.columns):
                    extra_items_df = None
            except:
                pass
            
            # If that didn't work, try with header=1 or 2
            if extra_items_df is None:
                for header_row in [1, 2, 3]:
                    try:
                        extra_items_df = pd.read_excel(excel_data, sheet_name='Extra Items', header=header_row)
                        # Check if we have meaningful column names
                        if not all('Unnamed' in str(col) for col in extra_items_df.columns):
                            break
                    except:
                        continue
            
            # If still no good data, return empty DataFrame
            if extra_items_df is None or extra_items_df.empty:
                return pd.DataFrame()
            
            # Standardize column names
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
            
            # Find quantity column with flexible naming
            qty_column = None
            for col in extra_items_df.columns:
                if 'quantity' in str(col).lower() or 'qty' in str(col).lower():
                    qty_column = col
                    break
            
            if qty_column:
                # Preserve main specification items even with zero quantity
                # Keep rows if they have:
                # 1. Non-zero quantity, OR
                # 2. A meaningful description (likely main specification), OR
                # 3. An item number (specification header)
                mask = (
                    (pd.notna(extra_items_df[qty_column]) & (extra_items_df[qty_column] != 0)) |  # Has quantity
                    (pd.notna(extra_items_df.get('Description', pd.Series())) & 
                     extra_items_df.get('Description', pd.Series()).astype(str).str.strip().str.len() > 0) |  # Has description
                    (pd.notna(extra_items_df.get('Item No.', pd.Series())) & 
                     extra_items_df.get('Item No.', pd.Series()).astype(str).str.strip().str.len() > 0)  # Has item number
                )
                
                extra_items_df = extra_items_df[mask]
                print(f"Smart filtered extra items rows (preserved main specifications)")
            
            return extra_items_df
            
        except Exception as e:
            # Return empty DataFrame instead of raising exception for optional sheet
            return pd.DataFrame()
