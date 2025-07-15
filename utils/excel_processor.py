import pandas as pd
import io
from typing import Dict, Any

class ExcelProcessor:
    """Handles Excel file processing and data extraction"""
    
    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
        self.workbook = None
    
    def process_excel(self) -> Dict[str, Any]:
        """
        Process uploaded Excel file and extract data from all required sheets
        
        Returns:
            Dict containing extracted data from all sheets
        """
        try:
            # Read Excel file
            excel_data = pd.ExcelFile(self.uploaded_file)
            
            # Initialize data dictionary
            data = {}
            
            # Process Title sheet
            if 'Title' in excel_data.sheet_names:
                data['title_data'] = self._process_title_sheet(excel_data)
            
            # Process Work Order sheet
            if 'Work Order' in excel_data.sheet_names:
                data['work_order_data'] = self._process_work_order_sheet(excel_data)
            
            # Process Bill Quantity sheet
            if 'Bill Quantity' in excel_data.sheet_names:
                data['bill_quantity_data'] = self._process_bill_quantity_sheet(excel_data)
            
            # Process Extra Items sheet (optional)
            if 'Extra Items' in excel_data.sheet_names:
                data['extra_items_data'] = self._process_extra_items_sheet(excel_data)
            else:
                data['extra_items_data'] = pd.DataFrame()
            
            return data
            
        except Exception as e:
            raise Exception(f"Error processing Excel file: {str(e)}")
    
    def _process_title_sheet(self, excel_data) -> Dict[str, str]:
        """Extract metadata from Title sheet"""
        try:
            title_df = pd.read_excel(excel_data, sheet_name='Title', header=None)
            
            # Convert to dictionary - assuming key-value pairs in adjacent columns
            title_data = {}
            for index, row in title_df.iterrows():
                if pd.notna(row[0]) and pd.notna(row[1]):
                    title_data[str(row[0]).strip()] = str(row[1]).strip()
            
            return title_data
            
        except Exception as e:
            raise Exception(f"Error processing Title sheet: {str(e)}")
    
    def _process_work_order_sheet(self, excel_data) -> pd.DataFrame:
        """Extract work order data"""
        try:
            work_order_df = pd.read_excel(excel_data, sheet_name='Work Order', header=0)
            
            # Find quantity column with flexible naming
            qty_column = None
            for col in work_order_df.columns:
                if 'quantity' in str(col).lower() or 'qty' in str(col).lower():
                    qty_column = col
                    break
            
            if qty_column:
                # Filter out rows with zero or blank quantities
                work_order_df = work_order_df.dropna(subset=[qty_column])
                work_order_df = work_order_df[work_order_df[qty_column] != 0]
            
            return work_order_df
            
        except Exception as e:
            raise Exception(f"Error processing Work Order sheet: {str(e)}")
    
    def _process_bill_quantity_sheet(self, excel_data) -> pd.DataFrame:
        """Extract bill quantity data"""
        try:
            bill_qty_df = pd.read_excel(excel_data, sheet_name='Bill Quantity', header=0)
            
            # Find quantity column with flexible naming
            qty_column = None
            for col in bill_qty_df.columns:
                if 'quantity' in str(col).lower() or 'qty' in str(col).lower():
                    qty_column = col
                    break
            
            if qty_column:
                # Filter out rows with zero or blank quantities
                bill_qty_df = bill_qty_df.dropna(subset=[qty_column])
                bill_qty_df = bill_qty_df[bill_qty_df[qty_column] != 0]
            
            return bill_qty_df
            
        except Exception as e:
            raise Exception(f"Error processing Bill Quantity sheet: {str(e)}")
    
    def _process_extra_items_sheet(self, excel_data) -> pd.DataFrame:
        """Extract extra items data"""
        try:
            extra_items_df = pd.read_excel(excel_data, sheet_name='Extra Items', header=0)
            
            # Find quantity column with flexible naming
            qty_column = None
            for col in extra_items_df.columns:
                if 'quantity' in str(col).lower() or 'qty' in str(col).lower():
                    qty_column = col
                    break
            
            if qty_column:
                # Filter out rows with zero or blank quantities
                extra_items_df = extra_items_df.dropna(subset=[qty_column])
                extra_items_df = extra_items_df[extra_items_df[qty_column] != 0]
            
            return extra_items_df
            
        except Exception as e:
            raise Exception(f"Error processing Extra Items sheet: {str(e)}")
