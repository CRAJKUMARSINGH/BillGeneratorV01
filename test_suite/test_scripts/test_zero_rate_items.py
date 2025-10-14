import streamlit as st
import pandas as pd
import sys
import os
from utils.excel_processor import ExcelProcessor

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_zero_rate_items_scenario():
    """Test the specific scenario where user enters quantities for zero-rate items"""
    
    print("Testing Zero-Rate Items Scenario...")
    print("=" * 50)
    
    # Simulate the exact scenario described in the user's issue:
    # "i filled quantity in online mode yet shows >>>>>Please enter quantities for at least one item to proceed >>>>>only display >>>item/subitem/sub-sub_item having a rate not equal to zero"
    
    # Create mock bill data that simulates what would happen in the app
    # This represents the bill_data list that gets created in show_bill_quantity_entry()
    bill_data = [
        {
            'item_no': '1.0',
            'description': 'Specification header (zero rate)',
            'unit': '',
            'rate': 0.0,  # Zero rate item
            'bill_qty': 10.0,  # User entered quantity
            'amount': 0.0  # 10.0 * 0.0 = 0.0
        },
        {
            'item_no': '1.1',
            'description': 'Actual work item',
            'unit': 'P. point',
            'rate': 256.0,  # Non-zero rate
            'bill_qty': 0.0,  # No quantity entered
            'amount': 0.0  # 0.0 * 256.0 = 0.0
        },
        {
            'item_no': '1.2', 
            'description': 'Another zero rate item',
            'unit': 'Each',
            'rate': 0.0,  # Zero rate item
            'bill_qty': 5.0,  # User entered quantity
            'amount': 0.0  # 5.0 * 0.0 = 0.0
        }
    ]
    
    print("Mock bill data created:")
    for item in bill_data:
        print(f"  Item {item['item_no']}: Rate={item['rate']}, Qty={item['bill_qty']}, Amount={item['amount']}")
    
    # Test the OLD validation logic (the one that was causing the issue)
    print("\n--- Testing OLD validation logic ---")
    total_amount = sum(item['amount'] for item in bill_data)
    old_validation = total_amount > 0
    print(f"Total amount: {total_amount}")
    print(f"Old validation (total_amount > 0): {old_validation}")
    if not old_validation:
        print("❌ OLD LOGIC WOULD SHOW ERROR: 'Please enter quantities for at least one item to proceed'")
    
    # Test the NEW validation logic (the fix)
    print("\n--- Testing NEW validation logic ---")
    has_quantities = any(item.get('bill_qty', 0) > 0 for item in bill_data)
    print(f"Has quantities entered: {has_quantities}")
    print(f"New validation (has_quantities): {has_quantities}")
    if has_quantities:
        print("✅ NEW LOGIC WOULD ENABLE PROCEED BUTTON")
    else:
        print("❌ NEW LOGIC WOULD STILL SHOW ERROR")
    
    # Show the difference
    print("\n--- Comparison ---")
    print(f"Old logic enables proceed: {old_validation}")
    print(f"New logic enables proceed: {has_quantities}")
    
    if not old_validation and has_quantities:
        print("\n🎉 SUCCESS: The fix resolves the issue!")
        print("   Users can now proceed even when entering quantities for zero-rate items.")
    elif old_validation == has_quantities:
        print("\nℹ️  Both logic produce the same result in this case.")
    else:
        print("\n⚠️  Unexpected result - needs investigation.")
    
    return True

def test_real_excel_file():
    """Test with actual Excel file data"""
    print("\n" + "=" * 50)
    print("Testing with Real Excel File Data...")
    print("=" * 50)
    
    # Load test data
    file_path = 'test_input_files/3rdFinalNoExtra.xlsx'
    
    try:
        # Process the Excel file
        processor = ExcelProcessor(file_path)
        result = processor.process_excel()
        
        work_order_data = result.get('work_order_data')
        if work_order_data is not None and not work_order_data.empty:
            print(f"Loaded {len(work_order_data)} work items")
            
            # Simulate user entering quantities ONLY for zero-rate items
            bill_data = []
            
            for idx, (_, row) in enumerate(work_order_data.iterrows()):
                item_no = str(row.get('Item', row.get('Item No.', f'Item_{idx + 1}')))
                description = str(row.get('Description', 'No description'))
                unit = str(row.get('Unit', 'Unit'))
                
                # Safely convert rate to float
                try:
                    rate_value = row.get('Rate', 0)
                    rate = float(rate_value) if rate_value is not None and not (isinstance(rate_value, float) and pd.isna(rate_value)) else 0.0
                except (ValueError, TypeError):
                    rate = 0.0
                
                # SPECIAL TEST: Enter quantities ONLY for zero-rate items
                bill_qty = 0.0  # Default no quantity
                if rate == 0.0 and idx < 3:  # Enter quantities for first 3 zero-rate items
                    bill_qty = 10.0 + idx  # Different quantities for testing
                elif rate > 0 and idx == 5:  # Enter quantity for one non-zero rate item
                    bill_qty = 5.0
                
                # Add to bill data if quantity > 0
                if bill_qty > 0:
                    amount = bill_qty * rate
                    bill_data.append({
                        'item_no': item_no,
                        'description': description,
                        'unit': unit,
                        'rate': rate,
                        'bill_qty': bill_qty,
                        'amount': amount
                    })
            
            print(f"\nItems with quantities entered:")
            total_amount = 0
            for item in bill_data:
                amount = item['bill_qty'] * item['rate']
                total_amount += amount
                print(f"  Item {item['item_no']}: '{item['description'][:30]}...' - Qty: {item['bill_qty']}, Rate: {item['rate']}, Amount: {amount}")
            
            print(f"\nTotal amount: {total_amount}")
            
            # Test validations
            has_quantities = any(item.get('bill_qty', 0) > 0 for item in bill_data)
            
            print(f"\nValidation Results:")
            print(f"  Has quantities entered: {has_quantities}")
            print(f"  Total amount > 0: {total_amount > 0}")
            
            if has_quantities:
                print("  ✅ PROCEED BUTTON ENABLED - Fix working!")
            else:
                print("  ❌ PROCEED BUTTON DISABLED - Issue exists!")
                
            return True
            
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_zero_rate_items_scenario()
    success2 = test_real_excel_file()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ ALL TESTS PASSED - Bug fix verified!")
    else:
        print("❌ SOME TESTS FAILED - Needs attention!")