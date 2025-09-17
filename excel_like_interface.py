
'''
Enhanced Excel-like Quantity Entry Interface for Bill Generator
Provides scrollable, worksheet-like interface with rate modification capabilities
'''

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import json

class ExcelLikeQuantityEntry:
    '''Enhanced Excel-like interface for bill quantity entry with rate modification'''

    def __init__(self):
        self.css_styles = self._get_excel_styles()

    def _get_excel_styles(self) -> str:
        '''Return CSS styles for Excel-like appearance'''
        return '''
        <style>
        .excel-container {
            background: white;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 0;
            margin: 10px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .excel-header {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 15px 20px;
            border-bottom: 2px solid #cbd5e1;
            border-radius: 7px 7px 0 0;
        }

        .summary-container {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border: 1px solid #0284c7;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .summary-item {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #0284c7;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .summary-label {
            font-size: 12px;
            color: #64748b;
            font-weight: 500;
            margin-bottom: 5px;
        }

        .summary-value {
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
        }

        .validation-message {
            padding: 10px 15px;
            border-radius: 6px;
            margin: 10px 0;
            font-weight: 500;
        }

        .validation-error {
            background: #fee2e2;
            color: #dc2626;
            border: 1px solid #fecaca;
        }

        .validation-warning {
            background: #fef3c7;
            color: #d97706;
            border: 1px solid #fde68a;
        }

        .validation-success {
            background: #d1fae5;
            color: #059669;
            border: 1px solid #a7f3d0;
        }
        </style>
        '''

    def render_quantity_entry_interface(self, work_order_data: pd.DataFrame, 
                                      session_state_key: str = "enhanced_bill_quantities") -> Dict[str, Any]:
        '''
        Render the enhanced Excel-like quantity entry interface

        Args:
            work_order_data: DataFrame containing work order items
            session_state_key: Key for storing quantities in session state

        Returns:
            Dict containing entered quantities and validation results
        '''
        # Apply CSS styles
        st.markdown(self.css_styles, unsafe_allow_html=True)

        # Initialize session state if not exists
        if session_state_key not in st.session_state:
            st.session_state[session_state_key] = {}

        # Initialize rate modifications if not exists
        rate_key = f"{session_state_key}_rates"
        if rate_key not in st.session_state:
            st.session_state[rate_key] = {}

        # Header section
        st.markdown('''
        <div class="excel-header">
            <h3 style="margin: 0; color: #1e40af;">📊 Bill Quantity Entry - Excel-like Interface</h3>
            <p style="margin: 5px 0 0 0; color: #64748b;">Enter quantities and modify rates (cannot exceed work order rates)</p>
        </div>
        ''', unsafe_allow_html=True)

        # Create the Excel-like table
        self._render_excel_table(work_order_data, session_state_key, rate_key)

        # Render summary and validation
        summary_data = self._render_summary_and_validation(work_order_data, session_state_key, rate_key)

        return summary_data

    def _render_excel_table(self, work_order_data: pd.DataFrame, 
                           session_state_key: str, rate_key: str):
        '''Render the main Excel-like table with editable cells'''

        st.markdown("### 📋 Work Order Items")

        # Create scrollable container
        container = st.container()

        with container:
            # Create table headers
            header_cols = st.columns([0.5, 3, 0.8, 1.2, 1, 1.2])

            with header_cols[0]:
                st.markdown("**Item #**")
            with header_cols[1]:
                st.markdown("**Description & WO Quantity**")
            with header_cols[2]:
                st.markdown("**Unit**")
            with header_cols[3]:
                st.markdown("**Rate (₹)**")
            with header_cols[4]:
                st.markdown("**Bill Qty**")
            with header_cols[5]:
                st.markdown("**Amount (₹)**")

            st.markdown("---")

            # Create rows for each work order item
            for idx, row in work_order_data.iterrows():
                item_num = idx + 1
                description = str(row.get('Description', row.get('Item Description', 'N/A')))
                wo_quantity = float(row.get('Quantity', row.get('Work Order Quantity', 0)))
                unit = str(row.get('Unit', row.get('UOM', 'N/A')))
                original_rate = float(row.get('Rate', row.get('Unit Rate', 0)))

                # Create unique keys for this item
                qty_input_key = f"qty_{session_state_key}_{idx}"
                rate_input_key = f"rate_{session_state_key}_{idx}"

                # Get current values
                current_qty = st.session_state[session_state_key].get(qty_input_key, 0.0)
                current_rate = st.session_state[rate_key].get(rate_input_key, original_rate)

                # Create columns for input fields
                cols = st.columns([0.5, 3, 0.8, 1.2, 1, 1.2])

                with cols[0]:
                    st.markdown(f"**{item_num}**")

                with cols[1]:
                    # Description with work order quantity info
                    desc_text = f"{description[:60]}{'...' if len(description) > 60 else ''}"
                    wo_info = f"WO Qty: {wo_quantity:,.2f} {unit}"
                    st.markdown(f"**{desc_text}**")
                    st.caption(wo_info)

                with cols[2]:
                    st.markdown(unit)

                with cols[3]:
                    # Rate input with validation
                    new_rate = st.number_input(
                        f"Rate {idx+1}",
                        min_value=0.01,
                        max_value=original_rate,
                        value=current_rate,
                        step=0.01,
                        key=rate_input_key,
                        label_visibility="collapsed",
                        help=f"Original: ₹{original_rate:,.2f}"
                    )

                    # Update session state
                    st.session_state[rate_key][rate_input_key] = new_rate

                    # Add validation
                    if new_rate < original_rate * 0.9:
                        st.caption("⚠️ Reduced")

                with cols[4]:
                    # Quantity input
                    new_qty = st.number_input(
                        f"Quantity {idx+1}",
                        min_value=0.0,
                        max_value=wo_quantity * 1.2,
                        value=current_qty,
                        step=0.01,
                        key=qty_input_key,
                        label_visibility="collapsed",
                        help=f"Max: {wo_quantity * 1.2:,.2f}"
                    )

                    # Update session state
                    st.session_state[session_state_key][qty_input_key] = new_qty

                    # Validation for quantity
                    if new_qty > wo_quantity:
                        st.caption("⚠️ Exceeds WO")

                with cols[5]:
                    # Calculate and display amount
                    amount = new_qty * new_rate
                    st.markdown(f"₹**{amount:,.2f}**")

                # Add separator
                st.markdown("---")

    def _render_summary_and_validation(self, work_order_data: pd.DataFrame, 
                                     session_state_key: str, rate_key: str) -> Dict[str, Any]:
        '''Render summary metrics and validation messages'''

        # Calculate summary metrics
        total_items = len(work_order_data)
        items_with_qty = 0
        total_quantity = 0.0
        total_amount = 0.0
        rate_modifications = 0
        validation_issues = []

        for idx, row in work_order_data.iterrows():
            qty_key_item = f"qty_{session_state_key}_{idx}"
            rate_key_item = f"rate_{session_state_key}_{idx}"

            quantity = st.session_state[session_state_key].get(qty_key_item, 0.0)
            rate = st.session_state[rate_key].get(rate_key_item, float(row.get('Rate', 0)))
            original_rate = float(row.get('Rate', row.get('Unit Rate', 0)))

            if quantity > 0:
                items_with_qty += 1
                total_quantity += quantity
                total_amount += quantity * rate

                # Check for rate modifications
                if rate != original_rate:
                    rate_modifications += 1

                    if rate > original_rate:
                        validation_issues.append(f"Item {idx+1}: Rate exceeds original (₹{rate:,.2f} > ₹{original_rate:,.2f})")

        # Render summary container
        st.markdown('''
        <div class="summary-container">
            <h4 style="margin-top: 0; color: #0f172a;">📈 Summary & Calculations</h4>
        </div>
        ''', unsafe_allow_html=True)

        # Summary metrics in columns
        summary_cols = st.columns(3)

        with summary_cols[0]:
            st.metric("Total Items", total_items)
            st.metric("Items with Qty", items_with_qty)

        with summary_cols[1]:
            st.metric("Total Quantity", f"{total_quantity:,.2f}")
            st.metric("Total Amount", f"₹{total_amount:,.2f}")

        with summary_cols[2]:
            st.metric("Rate Changes", rate_modifications)
            completion = (items_with_qty/total_items*100) if total_items > 0 else 0
            st.metric("Completion", f"{completion:.1f}%")

        # Validation messages
        if validation_issues:
            st.error("⚠️ **Validation Issues Found:**")
            for issue in validation_issues:
                st.error(f"• {issue}")
        elif items_with_qty > 0:
            st.success("✅ **All validations passed!** Ready for document generation.")
        else:
            st.warning("⚠️ **No quantities entered yet.** Please enter bill quantities to proceed.")

        return {
            'total_items': total_items,
            'items_with_qty': items_with_qty,
            'total_quantity': total_quantity,
            'total_amount': total_amount,
            'rate_modifications': rate_modifications,
            'validation_issues': validation_issues,
            'completion_percentage': completion
        }
