"""
Enhanced Excel Processor with better format support and error handling
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ExcelProcessor:
    """Enhanced Excel processor compatible with both repository formats"""
    
    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
    
    def process_excel(self, allow_missing_bill_quantity=False):
        """
        Process Excel file with enhanced format support
        
        Args:
            allow_missing_bill_quantity: Allow processing without Bill Quantity sheet
        
        Returns:
            dict: Processed data containing all sheets
        """
        try:
            excel_data = pd.ExcelFile(self.uploaded_file)
            logger.info(f"Available sheets: {excel_data.sheet_names}")
            
            data = {}
            
            # Process Title sheet (optional but recommended)
            if 'Title' in excel_data.sheet_names:
                data['title_data'] = self._process_title_sheet(excel_data)
            else:
                data['title_data'] = self._get_default_title_data()
                logger.warning("Title sheet not found, using defaults")
            
            # Process Work Order sheet (required)
            if 'Work Order' in excel_data.sheet_names:
                data['work_order_data'] = self._process_work_order_sheet(excel_data)
            else:
                raise Exception("Required 'Work Order' sheet not found in Excel file")
            
            # Process Bill Quantity sheet
            if 'Bill Quantity' in excel_data.sheet_names:
                data['bill_quantity_data'] = self._process_bill_quantity_sheet(excel_data)
            elif not allow_missing_bill_quantity:
                raise Exception("Required 'Bill Quantity' sheet not found in Excel file")
            else:
                # Create bill quantity from work order if missing
                data['bill_quantity_data'] = data['work_order_data'].copy()
                logger.info("Created bill quantity data from work order")
            
            # Process Extra Items sheet (optional)
            if 'Extra Items' in excel_data.sheet_names:
                data['extra_items_data'] = self._process_extra_items_sheet(excel_data)
            else:
                data['extra_items_data'] = pd.DataFrame()
            
            return data
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {str(e)}")
            raise Exception(f"Error processing Excel file: {str(e)}")
    
    def _get_default_title_data(self):
        """Get default title data when Title sheet is missing"""
        return {
            'Name of Work ;-': 'Project Name',
            'Agreement No.': 'AGR001',
            'Name of Contractor or supplier :': 'Contractor Name',
            'Bill Number': 'BILL001',
            'Running or Final': 'Running',
            'TENDER PREMIUM %': '5.0',
            'Date of measurement :': datetime.now().strftime('%d/%m/%Y'),
            'Date of written order to commence work :': datetime.now().strftime('%d/%m/%Y'),
            'St. date of Start :': datetime.now().strftime('%d/%m/%Y'),
            'St. date of completion :': datetime.now().strftime('%d/%m/%Y')
        }
    
    def _process_title_sheet(self, excel_data):
        """Extract metadata from Title sheet with enhanced parsing"""
        try:
            title_df = pd.read_excel(excel_data, sheet_name='Title', header=None)
            title_data = {}
            
            # Try different parsing strategies
            for index, row in title_df.iterrows():
                # Strategy 1: Key-Value pairs in adjacent columns
                if len(row) >= 2 and pd.notna(row[0]) and pd.notna(row[1]):
                    key = str(row[0]).strip()
                    val = str(row[1]).strip()
                    if key and val and key != 'nan' and val != 'nan':
                        title_data[key] = val
                
                # Strategy 2: Single column with colon separation
                elif len(row) >= 1 and pd.notna(row[0]):
                    text = str(row[0]).strip()
                    if ':' in text:
                        parts = text.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            val = parts[1].strip()
                            if key and val:
                                title_data[key] = val
            
            # Ensure required fields with defaults
            required_fields = {
                'TENDER PREMIUM %': '5.0',
                'Bill Number': 'BILL001',
                'Name of Work ;-': 'Project Name',
                'Name of Contractor or supplier :': 'Contractor Name'
            }
            
            for field, default_value in required_fields.items():
                if field not in title_data:
                    title_data[field] = default_value
            
            return title_data
            
        except Exception as e:
            logger.error(f"Error processing Title sheet: {str(e)}")
            return self._get_default_title_data()
    
    def _process_work_order_sheet(self, excel_data):
        """Extract work order data with enhanced format handling"""
        try:
            # Try different header strategies for different formats
            work_order_df = None
            
            # Strategy 1: Try common header rows (0, 20, 21)
            for header_row in [0, 20, 21]:
                try:
                    df = pd.read_excel(excel_data, sheet_name='Work Order', header=header_row)
                    if len(df.columns) >= 5:  # Minimum expected columns
                        # Check if this looks like actual data
                        if not df.empty and not df.iloc[0].isna().all():
                            work_order_df = df
                            break
                except:
                    continue
            
            # Strategy 2: No header, identify data rows
            if work_order_df is None:
                df = pd.read_excel(excel_data, sheet_name='Work Order', header=None)
                # Find the row that looks like headers
                for i in range(min(25, len(df))):
                    row = df.iloc[i]
                    if any(str(cell).lower() in ['description', 'item', 'quantity', 'rate'] 
                          for cell in row if pd.notna(cell)):
                        work_order_df = pd.read_excel(excel_data, sheet_name='Work Order', header=i)
                        break
                
                if work_order_df is None:
                    work_order_df = df
            
            # Standardize column names
            if len(work_order_df.columns) >= 7:
                work_order_df.columns = ['Item No.', 'Description', 'Unit', 'Quantity', 'Rate', 'Amount', 'Remark']
            elif len(work_order_df.columns) >= 6:
                work_order_df.columns = ['Item No.', 'Description', 'Unit', 'Quantity', 'Rate', 'Amount']
                work_order_df['Remark'] = ''
            elif len(work_order_df.columns) >= 5:
                work_order_df.columns = ['Item No.', 'Description', 'Unit', 'Quantity', 'Rate']
                work_order_df['Amount'] = work_order_df['Quantity'] * work_order_df['Rate']
                work_order_df['Remark'] = ''
            else:
                # Try to infer columns
                cols = ['Col_' + str(i) for i in range(len(work_order_df.columns))]
                work_order_df.columns = cols
            
            # Clean and validate data
            work_order_df = work_order_df.dropna(subset=['Description'], how='all')
            work_order_df = work_order_df[work_order_df['Description'].notna()]
            work_order_df = work_order_df[work_order_df['Description'] != '']
            
            # Convert numeric columns
            for col in ['Quantity', 'Rate', 'Amount']:
                if col in work_order_df.columns:
                    work_order_df[col] = pd.to_numeric(work_order_df[col], errors='coerce').fillna(0)
            
            # Calculate Amount if missing
            if 'Amount' in work_order_df.columns and 'Quantity' in work_order_df.columns and 'Rate' in work_order_df.columns:
                work_order_df['Amount'] = work_order_df['Quantity'] * work_order_df['Rate']
            
            return work_order_df
            
        except Exception as e:
            logger.error(f"Error processing Work Order sheet: {str(e)}")
            raise Exception(f"Error processing Work Order sheet: {str(e)}")
    
    def _process_bill_quantity_sheet(self, excel_data):
        """Extract bill quantity data with format flexibility"""
        try:
            # Similar strategy as work order
            bill_quantity_df = None
            
            for header_row in [0, 20, 21]:
                try:
                    df = pd.read_excel(excel_data, sheet_name='Bill Quantity', header=header_row)
                    if len(df.columns) >= 5:
                        if not df.empty and not df.iloc[0].isna().all():
                            bill_quantity_df = df
                            break
                except:
                    continue
            
            if bill_quantity_df is None:
                df = pd.read_excel(excel_data, sheet_name='Bill Quantity', header=None)
                # Try to find header row
                for i in range(min(25, len(df))):
                    row = df.iloc[i]
                    if any(str(cell).lower() in ['description', 'item', 'quantity', 'rate'] 
                          for cell in row if pd.notna(cell)):
                        bill_quantity_df = pd.read_excel(excel_data, sheet_name='Bill Quantity', header=i)
                        break
                
                if bill_quantity_df is None:
                    bill_quantity_df = df
            
            # Standardize columns similar to work order
            if len(bill_quantity_df.columns) >= 7:
                bill_quantity_df.columns = ['Item No.', 'Description', 'Unit', 'Quantity', 'Rate', 'Amount', 'Remark']
            elif len(bill_quantity_df.columns) >= 6:
                bill_quantity_df.columns = ['Item No.', 'Description', 'Unit', 'Quantity', 'Rate', 'Amount']
                bill_quantity_df['Remark'] = ''
            elif len(bill_quantity_df.columns) >= 5:
                bill_quantity_df.columns = ['Item No.', 'Description', 'Unit', 'Quantity', 'Rate']
                bill_quantity_df['Amount'] = 0
                bill_quantity_df['Remark'] = ''
            
            # Clean data
            bill_quantity_df = bill_quantity_df.dropna(subset=['Description'], how='all')
            
            # Convert numeric columns
            for col in ['Quantity', 'Rate', 'Amount']:
                if col in bill_quantity_df.columns:
                    bill_quantity_df[col] = pd.to_numeric(bill_quantity_df[col], errors='coerce').fillna(0)
            
            # Calculate Amount
            if 'Quantity' in bill_quantity_df.columns and 'Rate' in bill_quantity_df.columns:
                bill_quantity_df['Amount'] = bill_quantity_df['Quantity'] * bill_quantity_df['Rate']
            
            return bill_quantity_df
            
        except Exception as e:
            logger.error(f"Error processing Bill Quantity sheet: {str(e)}")
            raise Exception(f"Error processing Bill Quantity sheet: {str(e)}")
    
    def _process_extra_items_sheet(self, excel_data):
        """Extract extra items data"""
        try:
            extra_items_df = pd.read_excel(excel_data, sheet_name='Extra Items', header=0)
            
            # Try alternative header positions if first attempt fails
            if extra_items_df.empty or extra_items_df.columns[0] == 'Unnamed: 0':
                for header_row in [1, 2, 3, 5, 6]:
                    try:
                        df = pd.read_excel(excel_data, sheet_name='Extra Items', header=header_row)
                        if not df.empty and len([col for col in df.columns if 'Unnamed' not in str(col)]) > 2:
                            extra_items_df = df
                            break
                    except:
                        continue
            
            # Standardize columns if needed
            if len(extra_items_df.columns) >= 6:
                expected_cols = ['Item No.', 'Remark', 'Description', 'Quantity', 'Unit', 'Rate']
                if len(extra_items_df.columns) >= len(expected_cols):
                    extra_items_df.columns = expected_cols + list(extra_items_df.columns[len(expected_cols):])
            
            # Clean data
            extra_items_df = extra_items_df.dropna(subset=['Description'], how='all')
            
            # Convert numeric columns
            for col in ['Quantity', 'Rate']:
                if col in extra_items_df.columns:
                    extra_items_df[col] = pd.to_numeric(extra_items_df[col], errors='coerce').fillna(0)
            
            # Calculate Amount
            if 'Quantity' in extra_items_df.columns and 'Rate' in extra_items_df.columns:
                extra_items_df['Amount'] = extra_items_df['Quantity'] * extra_items_df['Rate']
            
            return extra_items_df
            
        except Exception as e:
            logger.error(f"Error processing Extra Items sheet: {str(e)}")
            return pd.DataFrame()
    
    def validate_processed_data(self, data):
        """Validate processed data for completeness"""
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check title data
        if not data.get('title_data'):
            validation_results['warnings'].append("Title data is missing or empty")
        
        # Check work order data
        work_order = data.get('work_order_data')
        if work_order is None or (isinstance(work_order, pd.DataFrame) and work_order.empty):
            validation_results['errors'].append("Work order data is missing or empty")
            validation_results['valid'] = False
        
        # Check bill quantity data
        bill_quantity = data.get('bill_quantity_data')
        if bill_quantity is None or (isinstance(bill_quantity, pd.DataFrame) and bill_quantity.empty):
            validation_results['warnings'].append("Bill quantity data is missing")
        
        # Check for required columns
        if isinstance(work_order, pd.DataFrame):
            required_cols = ['Description', 'Quantity', 'Rate']
            missing_cols = [col for col in required_cols if col not in work_order.columns]
            if missing_cols:
                validation_results['errors'].append(f"Missing required columns in work order: {missing_cols}")
                validation_results['valid'] = False
        
        return validation_results