import pandas as pd
import xlsxwriter
from typing import Dict, Any
import os
from pathlib import Path

class FirstPageGenerator:
    """Generate First Page sheet matching VBA behavior exactly"""
    
    def __init__(self):
        pass
    
    def generate_first_page(self, work_order_data: pd.DataFrame, extra_items_data: pd.DataFrame, 
                           title_data: Dict[str, Any], output_path: str):
        """
        Generate First Page sheet with VBA-like behavior for zero rates
        
        Args:
            work_order_data: DataFrame with work order items
            extra_items_data: DataFrame with extra items
            title_data: Dictionary with title information
            output_path: Path to save the Excel file
        """
        # Create Excel workbook
        workbook = xlsxwriter.Workbook(output_path)
        worksheet = workbook.add_worksheet('First Page')
        
        # Set up formatting
        self._setup_formatting(workbook, worksheet)
        
        # Copy header from title data (rows 1-19)
        self._copy_header_data(worksheet, title_data)
        
        # Process work order items starting from row 22 (0-indexed: row 21)
        current_row = 21  # Row 22 in 1-indexed (VBA style)
        
        # Process work order items
        for _, row in work_order_data.iterrows():
            self._process_work_order_item(worksheet, row, current_row)
            current_row += 1
        
        # Add extra items section header
        worksheet.write(current_row, 4, "Extra Items (With Premium)")  # Column E
        worksheet.set_row(current_row, None, self.bold_format)
        current_row += 1
        
        # Process extra items
        if extra_items_data is not None and not extra_items_data.empty:
            for _, row in extra_items_data.iterrows():
                self._process_extra_item(worksheet, row, current_row)
                current_row += 1
        
        # Apply column widths and formatting
        self._apply_column_formatting(worksheet)
        
        # Close workbook
        workbook.close()
    
    def _setup_formatting(self, workbook, worksheet):
        """Set up formatting styles"""
        # Font formatting
        self.normal_format = workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 9
        })
        
        # Bold formatting
        self.bold_format = workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 9,
            'bold': True
        })
        
        # Underline formatting
        self.underline_format = workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 9,
            'underline': True
        })
        
        # Border formatting
        self.border_format = workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 9,
            'border': 1
        })
        
        # Wrap text formatting for long descriptions
        self.wrap_text_format = workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 9,
            'text_wrap': True,
            'valign': 'top'
        })
    
    def _copy_header_data(self, worksheet, title_data):
        """Copy header data from title information"""
        # This would copy the header data from rows 1-19
        # For simplicity, we'll just add some basic header info
        worksheet.write('A2', 'WORK ORDER', self.bold_format)
        worksheet.write('A3', 'Date', self.normal_format)
        worksheet.write('B7', title_data.get('Name of Work ;-'), self.normal_format)
        worksheet.write('B9', title_data.get('Name of Contractor or supplier :'), self.normal_format)
        
        # Merge cells as in VBA
        worksheet.merge_range('B7:I7', title_data.get('Name of Work ;-'), self.normal_format)
        worksheet.merge_range('B9:I9', title_data.get('Name of Contractor or supplier :'), self.normal_format)
    
    def _process_work_order_item(self, worksheet, row, current_row):
        """
        Process a work order item with VBA-like behavior for zero rates
        
        Column mapping (VBA style):
        A: Unit
        B: Quantity Since (0 when Quantity Upto has value)
        C: Quantity Upto (actual quantity)
        D: Serial No.
        E: Description
        F: Rate
        G: Amount (Quantity Upto × Rate) - Rounded
        H: Amount (Quantity Since × Rate) - Rounded
        I: Remark
        """
        # Extract values
        unit = row.get('Unit', '')
        quantity_upto = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))  # Using Quantity Since as per data
        serial_no = row.get('Item No.', row.get('Item', ''))
        description = row.get('Description', '')
        rate = self._safe_float(row.get('Rate', 0))
        remark = row.get('Remark', row.get('Remark/ BSR Reference', ''))
        
        # CRITICAL: According to VBA specification, if Rate is blank or zero:
        # Only Serial Number (D) and Description (E) should be populated
        # All other columns should remain blank
        if rate == 0:
            # Only populate Serial No. and Description for zero rates
            worksheet.write(current_row, 3, serial_no)  # Column D: Serial No.
            worksheet.write(current_row, 4, description)  # Column E: Description
            # Leave all other columns blank
        else:
            # For non-zero rates, populate all columns
            quantity_since = 0 if quantity_upto > 0 else 0
            
            # Calculate amounts
            amount_upto = self._calculate_amount(quantity_upto, rate)
            amount_since = self._calculate_amount(quantity_since, rate)
            
            # Write to worksheet
            worksheet.write(current_row, 0, unit)  # Column A: Unit
            worksheet.write(current_row, 1, quantity_since)  # Column B: Quantity Since
            worksheet.write(current_row, 2, quantity_upto)  # Column C: Quantity Upto
            worksheet.write(current_row, 3, serial_no)  # Column D: Serial No.
            worksheet.write(current_row, 4, description)  # Column E: Description
            worksheet.write(current_row, 5, rate)  # Column F: Rate
            
            # Only populate amounts if rate is not zero (VBA behavior)
            if rate != 0:
                worksheet.write(current_row, 6, amount_upto)  # Column G: Amount Upto
                worksheet.write(current_row, 7, amount_since)  # Column H: Amount Since
            
            worksheet.write(current_row, 8, remark)  # Column I: Remark
    
    def _process_extra_item(self, worksheet, row, current_row):
        """
        Process an extra item with VBA-like behavior
        
        Same column mapping as work order items
        """
        # Extract values
        unit = row.get('Unit', '')
        quantity = self._safe_float(row.get('Quantity', 0))
        serial_no = row.get('Item No.', row.get('Item', ''))
        description = row.get('Description', '')
        rate = self._safe_float(row.get('Rate', 0))
        remark = row.get('Remark', '')
        
        # CRITICAL: According to VBA specification, if Rate is blank or zero:
        # Only Serial Number (D) and Description (E) should be populated
        # All other columns should remain blank
        if rate == 0:
            # Only populate Serial No. and Description for zero rates
            worksheet.write(current_row, 3, serial_no)  # Column D: Serial No.
            worksheet.write(current_row, 4, description)  # Column E: Description
            # Leave all other columns blank
        else:
            # For non-zero rates, populate all columns
            # For extra items, Quantity Since is typically 0
            quantity_since = 0
            quantity_upto = quantity
            
            # Calculate amounts
            amount_upto = self._calculate_amount(quantity_upto, rate)
            amount_since = self._calculate_amount(quantity_since, rate)
            
            # Write to worksheet
            worksheet.write(current_row, 0, unit)  # Column A: Unit
            worksheet.write(current_row, 1, quantity_since)  # Column B: Quantity Since
            worksheet.write(current_row, 2, quantity_upto)  # Column C: Quantity Upto
            worksheet.write(current_row, 3, serial_no)  # Column D: Serial No.
            worksheet.write(current_row, 4, description)  # Column E: Description
            worksheet.write(current_row, 5, rate)  # Column F: Rate
            
            # Only populate amounts if rate is not zero (VBA behavior)
            if rate != 0:
                worksheet.write(current_row, 6, amount_upto)  # Column G: Amount Upto
                worksheet.write(current_row, 7, amount_since)  # Column H: Amount Since
            
            worksheet.write(current_row, 8, remark)  # Column I: Remark
    
    def _safe_float(self, value):
        """Safely convert value to float"""
        try:
            if pd.isna(value) or value == '' or value is None:
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _calculate_amount(self, quantity, rate):
        """Calculate amount and round as per VBA behavior"""
        if quantity == 0 or rate == 0:
            return 0
        return round(quantity * rate, 0)
    
    def _apply_column_formatting(self, worksheet):
        """Apply column widths and formatting as in VBA"""
        # Set column widths
        column_widths = {
            0: 5.5,   # Column A
            1: 7.56,  # Column B
            2: 7.56,  # Column C
            3: 5.22,  # Column D
            4: 35,    # Column E
            5: 7.23,  # Column F
            6: 10.7,  # Column G
            7: 8.33,  # Column H
            8: 6.56   # Column I
        }
        
        for col, width in column_widths.items():
            worksheet.set_column(col, col, width)
        
        # Apply text wrapping to description column (E)
        worksheet.set_column(4, 4, 35, self.wrap_text_format)  # Column E