import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader
import os

class TemplateRenderer:
    """Render HTML templates with data structure matching templates_14102025 format"""
    
    def __init__(self, template_dir: str = ""):
        if not template_dir:
            # Try the nested templates_14102025 directory
            nested_template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates_14102025', 'templates_14102025')
            if os.path.exists(nested_template_dir):
                template_dir = nested_template_dir
            else:
                # Try the main templates_14102025 directory
                main_template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates_14102025')
                if os.path.exists(main_template_dir):
                    template_dir = main_template_dir
                else:
                    # Fallback to main templates directory
                    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            cache_size=400,
            auto_reload=False
        )
    
    def _prepare_first_page_data(self, title_data: Dict[str, Any], work_order_data: pd.DataFrame, 
                                extra_items_data = None) -> Dict[str, Any]:
        """Prepare data structure for first_page.html template"""
        
        # Prepare header data - convert title_data to rows format
        header_rows = []
        if title_data:
            # Convert title_data to rows format expected by template
            header_data = []
            for key, value in title_data.items():
                if value:
                    header_data.append(f"{key}: {value}")
            
            # Split into rows (simplified approach)
            current_row = []
            for i, item in enumerate(header_data):
                current_row.append(item)
                # Create a new row every 3 items (adjust as needed)
                if (i + 1) % 3 == 0:
                    header_rows.append(current_row)
                    current_row = []
            
            # Add remaining items
            if current_row:
                header_rows.append(current_row)
        
        # Prepare items data
        items = []
        
        # Process work order items
        if isinstance(work_order_data, pd.DataFrame):
            for _, row in work_order_data.iterrows():
                # Extract values with safe defaults
                unit = str(row.get('Unit', ''))
                quantity_since = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
                quantity_upto = self._safe_float(row.get('Quantity Upto', quantity_since))
                serial_no = str(row.get('Item No.', row.get('Item', row.get('S. No.', ''))))
                description = str(row.get('Description', ''))
                rate = self._safe_float(row.get('Rate', 0))
                amount = self._safe_float(row.get('Amount', quantity_upto * rate))
                remark = str(row.get('Remark', ''))
                
                # Apply VBA-like behavior for zero rates
                if rate == 0:
                    # Only populate Serial No. and Description for zero rates
                    item_data = {
                        'unit': '',
                        'quantity_since_last': '',
                        'quantity_upto_date': '',
                        'serial_no': serial_no,
                        'description': description,
                        'rate': '',
                        'amount': '',
                        'amount_previous': '',
                        'remark': ''
                    }
                else:
                    # For non-zero rates, populate all columns
                    item_data = {
                        'unit': unit,
                        'quantity_since_last': f"{quantity_since:.2f}" if quantity_since > 0 else "",
                        'quantity_upto_date': f"{quantity_upto:.2f}" if quantity_upto > 0 else "",
                        'serial_no': serial_no,
                        'description': description,
                        'rate': f"{rate:.2f}" if rate > 0 else "",
                        'amount': f"{amount:.2f}" if amount > 0 else "",
                        'amount_previous': "",  # As per VBA behavior
                        'remark': remark
                    }
                
                items.append(item_data)
        
        # Process extra items
        if isinstance(extra_items_data, pd.DataFrame) and not extra_items_data.empty:
            for _, row in extra_items_data.iterrows():
                unit = str(row.get('Unit', ''))
                quantity = self._safe_float(row.get('Quantity', 0))
                serial_no = str(row.get('Item No.', row.get('Item', '')))
                description = str(row.get('Description', ''))
                rate = self._safe_float(row.get('Rate', 0))
                amount = self._safe_float(row.get('Amount', quantity * rate))
                remark = str(row.get('Remark', ''))
                
                # Apply VBA-like behavior for zero rates
                if rate == 0:
                    # Only populate Serial No. and Description for zero rates
                    item_data = {
                        'unit': '',
                        'quantity_since_last': '',
                        'quantity_upto_date': '',
                        'serial_no': serial_no,
                        'description': description,
                        'rate': '',
                        'amount': '',
                        'amount_previous': '',
                        'remark': ''
                    }
                else:
                    # For non-zero rates, populate all columns
                    item_data = {
                        'unit': unit,
                        'quantity_since_last': "",
                        'quantity_upto_date': f"{quantity:.2f}" if quantity > 0 else "",
                        'serial_no': serial_no,
                        'description': description,
                        'rate': f"{rate:.2f}" if rate > 0 else "",
                        'amount': f"{amount:.2f}" if amount > 0 else "",
                        'amount_previous': "",
                        'remark': remark
                    }
                
                items.append(item_data)
        
        # Calculate totals
        total_amount = 0
        if isinstance(work_order_data, pd.DataFrame):
            for _, row in work_order_data.iterrows():
                quantity = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
                rate = self._safe_float(row.get('Rate', 0))
                if rate != 0:  # Only count non-zero rate items
                    total_amount += quantity * rate
        
        # Calculate premium (typically 10%)
        premium_percent = 0.10
        premium_amount = total_amount * premium_percent
        payable_amount = total_amount + premium_amount
        
        return {
            'data': {
                'header': header_rows,
                'items': items,
                'totals': {
                    'grand_total': f"{total_amount:.2f}",
                    'premium': {
                        'percent': premium_percent,
                        'amount': f"{premium_amount:.2f}"
                    },
                    'payable': f"{payable_amount:.2f}"
                }
            }
        }
    
    def _safe_float(self, value) -> float:
        """Safely convert value to float"""
        try:
            if pd.isna(value) or value == '' or value is None:
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def render_first_page(self, title_data: Dict[str, Any], work_order_data: pd.DataFrame,
                         extra_items_data = None) -> str:
        """Render first_page.html template"""
        try:
            # Prepare data in the format expected by the template
            template_data = self._prepare_first_page_data(title_data, work_order_data, extra_items_data)
            
            # Render template
            template = self.jinja_env.get_template('first_page.html')
            return template.render(**template_data)
        except Exception as e:
            print(f"Failed to render first_page.html template: {e}")
            raise
    
    def render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Render any template with provided data"""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**data)
        except Exception as e:
            print(f"Failed to render template {template_name}: {e}")
            raise