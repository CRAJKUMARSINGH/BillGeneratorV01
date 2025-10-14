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
    
    def render_note_sheet(self, title_data: Dict[str, Any], work_order_data: pd.DataFrame,
                         extra_items_data = None) -> str:
        """Render note_sheet.html template with proper data structure"""
        try:
            # Prepare data in the format expected by the note_sheet template
            template_data = {
                'data': {
                    'agreement_no': title_data.get('agreement_no', title_data.get('Contract No', '')),
                    'name_of_work': title_data.get('name_of_work', title_data.get('Project Name', '')),
                    'name_of_firm': title_data.get('name_of_firm', title_data.get('Contractor Name', '')),
                    'date_commencement': title_data.get('date_commencement', ''),
                    'date_completion': title_data.get('date_completion', ''),
                    'actual_completion': title_data.get('actual_completion', ''),
                    'work_order_amount': title_data.get('work_order_amount', '0.00'),
                    'totals': {
                        'payable': title_data.get('net_payable', '0.00'),
                        'extra_items_sum': title_data.get('extra_items_sum', 0.0)
                    }
                },
                'notes': title_data.get('notes', ['Work completed as per schedule'])
            }
            
            # Render template
            template = self.jinja_env.get_template('note_sheet.html')
            return template.render(**template_data)
        except Exception as e:
            print(f"Failed to render note_sheet.html template: {e}")
            raise

    def render_deviation_statement(self, title_data: Dict[str, Any], work_order_data: pd.DataFrame,
                                  extra_items_data = None) -> str:
        """Render deviation_statement.html template with proper data structure"""
        try:
            # Prepare header data in the format expected by the deviation statement template
            header_data = []
            if title_data:
                # Convert title_data to a 2D array format expected by the template
                # This is a simplified approach - in a real implementation, you might need
                # to structure this more precisely based on your actual data
                header_data = [[], [], [], [], [], [], [], [], [], [], [], [], []]  # 13 rows
                
                # Populate specific positions based on template expectations
                if 'agreement_no' in title_data:
                    if len(header_data) > 12:
                        if len(header_data[12]) <= 4:
                            # Extend the row if needed
                            while len(header_data[12]) <= 4:
                                header_data[12].append('')
                        header_data[12][4] = title_data['agreement_no']
                
                if 'name_of_work' in title_data:
                    if len(header_data) > 8:
                        if len(header_data[8]) <= 1:
                            # Extend the row if needed
                            while len(header_data[8]) <= 1:
                                header_data[8].append('')
                        header_data[8][1] = title_data['name_of_work']
            
            # Prepare items data
            items = []
            
            # Process work order items for deviation calculation
            if isinstance(work_order_data, pd.DataFrame):
                for _, row in work_order_data.iterrows():
                    # Extract values with safe defaults
                    unit = str(row.get('Unit', ''))
                    qty_wo = self._safe_float(row.get('Quantity', 0))
                    qty_bill = self._safe_float(row.get('Quantity Billed', qty_wo))  # Default to same as WO
                    serial_no = str(row.get('Item No.', row.get('Item', row.get('S. No.', ''))))
                    description = str(row.get('Description', ''))
                    rate = self._safe_float(row.get('Rate', 0))
                    
                    # Calculate amounts
                    amt_wo = qty_wo * rate
                    amt_bill = qty_bill * rate
                    
                    # Calculate deviations
                    excess_qty = max(0, qty_bill - qty_wo)
                    saving_qty = max(0, qty_wo - qty_bill)
                    excess_amt = excess_qty * rate
                    saving_amt = saving_qty * rate
                    
                    item_data = {
                        'serial_no': serial_no,
                        'description': description,
                        'unit': unit,
                        'qty_wo': f"{qty_wo:.2f}" if qty_wo > 0 else "",
                        'rate': f"{rate:.2f}" if rate > 0 else "",
                        'amt_wo': f"{amt_wo:.2f}" if amt_wo > 0 else "",
                        'qty_bill': f"{qty_bill:.2f}" if qty_bill > 0 else "",
                        'amt_bill': f"{amt_bill:.2f}" if amt_bill > 0 else "",
                        'excess_qty': f"{excess_qty:.2f}" if excess_qty > 0 else "",
                        'excess_amt': f"{excess_amt:.2f}" if excess_amt > 0 else "",
                        'saving_qty': f"{saving_qty:.2f}" if saving_qty > 0 else "",
                        'saving_amt': f"{saving_amt:.2f}" if saving_amt > 0 else "",
                        'remark': str(row.get('Remark', ''))
                    }
                    
                    items.append(item_data)
            
            # Calculate summary data
            work_order_total = sum(self._safe_float(item.get('amt_wo', 0)) for item in items)
            executed_total = sum(self._safe_float(item.get('amt_bill', 0)) for item in items)
            overall_excess = max(0, executed_total - work_order_total)
            overall_saving = max(0, work_order_total - executed_total)
            
            # Calculate tender premium (typically 10%)
            premium_percent = 0.10
            tender_premium_f = work_order_total * premium_percent
            tender_premium_h = executed_total * premium_percent
            tender_premium_j = overall_excess * premium_percent if overall_excess > 0 else 0
            tender_premium_l = overall_saving * premium_percent if overall_saving > 0 else 0
            
            # Calculate grand totals including premium
            grand_total_f = work_order_total + tender_premium_f
            grand_total_h = executed_total + tender_premium_h
            grand_total_j = overall_excess + tender_premium_j
            grand_total_l = overall_saving + tender_premium_l
            
            # Net difference
            net_difference = executed_total - work_order_total
            
            summary_data = {
                'work_order_total': f"{work_order_total:.2f}",
                'executed_total': f"{executed_total:.2f}",
                'overall_excess': f"{overall_excess:.2f}",
                'overall_saving': f"{overall_saving:.2f}",
                'premium': {
                    'percent': premium_percent
                },
                'tender_premium_f': f"{tender_premium_f:.2f}",
                'tender_premium_h': f"{tender_premium_h:.2f}",
                'tender_premium_j': f"{tender_premium_j:.2f}",
                'tender_premium_l': f"{tender_premium_l:.2f}",
                'grand_total_f': f"{grand_total_f:.2f}",
                'grand_total_h': f"{grand_total_h:.2f}",
                'grand_total_j': f"{grand_total_j:.2f}",
                'grand_total_l': f"{grand_total_l:.2f}",
                'net_difference': f"{net_difference:.2f}"
            }
            
            # Prepare data in the format expected by the deviation statement template
            template_data = {
                'header_data': header_data,
                'data': {
                    'items': items,
                    'summary': summary_data
                }
            }
            
            # Render template
            template = self.jinja_env.get_template('deviation_statement.html')
            return template.render(**template_data)
        except Exception as e:
            print(f"Failed to render deviation_statement.html template: {e}")
            raise

    def render_extra_items(self, title_data: Dict[str, Any], work_order_data: pd.DataFrame,
                          extra_items_data = None) -> str:
        """Render extra_items.html template with proper data structure"""
        try:
            # Prepare items data
            items = []
            
            # Process extra items data
            if isinstance(extra_items_data, pd.DataFrame) and not extra_items_data.empty:
                for _, row in extra_items_data.iterrows():
                    # Extract values with safe defaults
                    serial_no = str(row.get('Item No.', row.get('Item', row.get('S. No.', ''))))
                    remark = str(row.get('Remark', ''))
                    description = str(row.get('Description', ''))
                    quantity = self._safe_float(row.get('Quantity', 0))
                    unit = str(row.get('Unit', ''))
                    rate = self._safe_float(row.get('Rate', 0))
                    amount = quantity * rate
                    
                    item_data = {
                        'serial_no': serial_no,
                        'remark': remark,
                        'description': description,
                        'quantity': f"{quantity:.2f}" if quantity > 0 else "",
                        'unit': unit,
                        'rate': f"{rate:.2f}" if rate > 0 else "",
                        'amount': f"{amount:.2f}" if amount > 0 else ""
                    }
                    
                    items.append(item_data)
            
            # Prepare data in the format expected by the extra items template
            template_data = {
                'data': {
                    'item_list': items
                }
            }
            
            # Render template
            template = self.jinja_env.get_template('extra_items.html')
            return template.render(**template_data)
        except Exception as e:
            print(f"Failed to render extra_items.html template: {e}")
            raise

    def render_certificate_ii(self, title_data: Dict[str, Any], work_order_data: pd.DataFrame,
                             extra_items_data = None) -> str:
        """Render certificate_ii.html template with proper data structure"""
        try:
            # Prepare data in the format expected by the certificate_ii template
            template_data = {
                'data': {
                    'measurement_officer': title_data.get('Measurement Officer', 'Measurement Officer Name'),
                    'measurement_date': title_data.get('Measurement Date', '30/04/2025'),
                    'measurement_book_page': title_data.get('Measurement Book Page', '123'),
                    'measurement_book_no': title_data.get('Measurement Book No', 'MB-001'),
                    'officer_name': title_data.get('Officer Name', 'Officer Name'),
                    'officer_designation': title_data.get('Officer Designation', 'Designation'),
                    'authorising_officer_name': title_data.get('Authorising Officer Name', 'Authorising Officer Name'),
                    'authorising_officer_designation': title_data.get('Authorising Officer Designation', 'Designation')
                }
            }
            
            # Render template
            template = self.jinja_env.get_template('certificate_ii.html')
            return template.render(**template_data)
        except Exception as e:
            print(f"Failed to render certificate_ii.html template: {e}")
            raise

    def _number_to_words(self, num):
        """Convert number to words (simplified version)"""
        if num == 0:
            return "Zero"
        
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
        teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        def convert_hundreds(n):
            result = ''
            if n >= 100:
                result += ones[n // 100] + ' Hundred '
                n %= 100
            if n >= 20:
                result += tens[n // 10] + ' '
                n %= 10
            elif n >= 10:
                result += teens[n - 10] + ' '
                n = 0
            if n > 0:
                result += ones[n] + ' '
            return result.strip()
        
        if num < 1000:
            return convert_hundreds(num)
        elif num < 100000:
            thousands = num // 1000
            remainder = num % 1000
            result = convert_hundreds(thousands) + ' Thousand '
            if remainder > 0:
                result += convert_hundreds(remainder)
            return result.strip()
        else:
            lakhs = num // 100000
            remainder = num % 100000
            result = convert_hundreds(lakhs) + ' Lakh '
            if remainder > 0:
                if remainder >= 1000:
                    result += convert_hundreds(remainder // 1000) + ' Thousand '
                    remainder %= 1000
                if remainder > 0:
                    result += convert_hundreds(remainder)
            return result.strip()

    def render_certificate_iii(self, title_data: Dict[str, Any], work_order_data: pd.DataFrame,
                              extra_items_data = None) -> str:
        """Render certificate_iii.html template with proper data structure"""
        try:
            # Calculate totals from work order data
            total_amount = 0
            if isinstance(work_order_data, pd.DataFrame):
                for _, row in work_order_data.iterrows():
                    quantity = self._safe_float(row.get('Quantity', 0))
                    rate = self._safe_float(row.get('Rate', 0))
                    total_amount += quantity * rate
            
            # Calculate premium (typically 10%)
            premium_percent = 0.10
            premium_amount = total_amount * premium_percent
            payable_amount = total_amount + premium_amount
            
            # Calculate deductions
            sd_amount = payable_amount * 0.10  # Security Deposit 10%
            it_amount = payable_amount * 0.02  # Income Tax 2%
            gst_amount = payable_amount * 0.02  # GST 2%
            lc_amount = payable_amount * 0.01  # Labour Cess 1%
            total_deductions = sd_amount + it_amount + gst_amount + lc_amount
            
            # Calculate amounts for template
            total_123 = total_amount  # Items 1 + 2 + 3 (simplified)
            balance_4_minus_5 = total_123  # Balance (Item 4 - 5)
            total_recovery = sd_amount + it_amount + gst_amount + lc_amount
            by_cheque = payable_amount - total_recovery
            
            # Convert amount to words (simplified)
            amount_words = self._number_to_words(int(payable_amount))
            
            # Prepare data in the format expected by the certificate_iii template
            # Pass both numeric values (for calculations) and string values (for display)
            template_data = {
                'data': {
                    'totals': {
                        'grand_total': f"{total_amount:.0f}",
                        'payable_amount': f"{payable_amount:.0f}",
                        # Numeric values for calculations in template
                        'grand_total_numeric': total_amount,
                        'payable_amount_numeric': payable_amount
                    },
                    'total_123': f"{total_123:.0f}",
                    'balance_4_minus_5': f"{balance_4_minus_5:.0f}",
                    'payable_amount': f"{payable_amount:.0f}",
                    'total_recovery': f"{total_recovery:.0f}",
                    'by_cheque': f"{by_cheque:.0f}",
                    'amount_words': amount_words,
                    # Numeric values for calculations
                    'payable_amount_numeric': payable_amount,
                    'sd_amount': sd_amount,
                    'it_amount': it_amount,
                    'gst_amount': gst_amount,
                    'lc_amount': lc_amount
                }
            }
            
            # Render template
            template = self.jinja_env.get_template('certificate_iii.html')
            return template.render(**template_data)
        except Exception as e:
            print(f"Failed to render certificate_iii.html template: {e}")
            raise
