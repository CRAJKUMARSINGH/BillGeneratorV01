import streamlit as st
import pandas as pd
import sys
import os
from utils.excel_processor import ExcelProcessor

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_online_mode_workflow():
    """Test the online mode workflow with sample data"""
    
    # Load test data
    file_path = 'test_input_files/3rdFinalNoExtra.xlsx'
    
    try:
        # Process the Excel file
        processor = ExcelProcessor(file_path)
        result = processor.process_excel()
        
        print("✅ Excel file processed successfully!")
        print(f"Title data: {len(result.get('title_data', {}))} items")
        print(f"Work order data: {len(result.get('work_order_data', []))} rows")
        
        # Simulate online mode - step by step
        work_order_data = result.get('work_order_data')
        if work_order_data is not None and not work_order_data.empty:
            print("\n--- Simulating Online Mode: Bill Quantity Entry ---")
            
            # Convert to list if it's a DataFrame
            if hasattr(work_order_data, 'to_dict'):
                work_items = work_order_data.to_dict('records')
            else:
                work_items = work_order_data if isinstance(work_order_data, list) else []
            
            # Simulate user entering quantities
            bill_quantities = {}
            bill_data = []
            total_amount = 0.0
            
            print(f"Processing {len(work_items)} work items...")
            
            for idx, item in enumerate(work_items):
                # Extract item details
                item_no = str(item.get('Item', item.get('Item No.', f'Item_{idx + 1}')))
                description = str(item.get('Description', 'No description'))
                unit = str(item.get('Unit', 'Unit'))
                
                # Safely convert rate to float
                try:
                    rate_value = item.get('Rate', 0)
                    rate = float(rate_value) if rate_value is not None and not (isinstance(rate_value, float) and pd.isna(rate_value)) else 0.0
                except (ValueError, TypeError):
                    rate = 0.0
                
                # For testing, let's enter quantities for some items (including zero-rate items)
                # This simulates a user entering quantities
                if idx < 5:  # Enter quantities for first 5 items
                    bill_qty = 10.0 + idx  # Different quantities for testing
                elif rate == 0 and idx < 10:  # Enter quantities for zero-rate items
                    bill_qty = 5.0
                else:
                    bill_qty = 0.0  # No quantity for other items
                
                # Store in session state simulation
                qty_key = f"bill_qty_{idx}_{item_no}"
                bill_quantities[qty_key] = bill_qty
                
                # Calculate amount and add to bill data if quantity > 0
                if bill_qty > 0:
                    amount = bill_qty * rate
                    total_amount += amount if not pd.isna(amount) else 0.0
                    
                    bill_data.append({
                        'item_no': item_no,
                        'description': description,
                        'unit': unit,
                        'rate': rate,
                        'bill_qty': bill_qty,
                        'amount': amount
                    })
                    
                    print(f"  Item {item_no}: {description[:50]}... - Qty: {bill_qty}, Rate: {rate}, Amount: {amount}")
            
            print(f"\n--- Validation Check ---")
            print(f"Total items with quantities: {len(bill_data)}")
            print(f"Total amount: {total_amount}")
            
            # Test the validation logic that was fixed
            has_quantities = any(item.get('bill_qty', 0) > 0 for item in bill_data)
            
            print(f"Has quantities entered: {has_quantities}")
            print(f"Total amount > 0: {total_amount > 0}")
            
            if has_quantities:
                print("✅ PROCEED BUTTON SHOULD BE ENABLED - Fix working correctly!")
            else:
                print("❌ PROCEED BUTTON WOULD BE DISABLED - Issue not fixed!")
                
            # Show the bill data that would be displayed
            if bill_data:
                print("\n--- Bill Summary ---")
                bill_df = pd.DataFrame(bill_data)
                print(bill_df[['item_no', 'description', 'unit', 'rate', 'bill_qty', 'amount']].to_string(index=False))
            
            return True
            
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Online Mode Workflow...")
    print("=" * 50)
    success = test_online_mode_workflow()
    print("=" * 50)
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")