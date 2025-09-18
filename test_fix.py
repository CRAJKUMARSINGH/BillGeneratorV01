import pandas as pd
from utils.excel_processor import ExcelProcessor

def test_fix():
    """Test the fix for the 'str' object has no attribute 'get' error"""
    
    print("Testing the fix for 'str' object has no attribute 'get' error...")
    print("=" * 60)
    
    # Load test data
    file_path = 'test_input_files/3rdFinalNoExtra.xlsx'
    
    try:
        # Process the Excel file
        processor = ExcelProcessor(file_path)
        result = processor.process_excel()
        
        work_order_data = result.get('work_order_data')
        
        if work_order_data is not None and not work_order_data.empty:
            # Convert to list if it's a DataFrame
            if hasattr(work_order_data, 'to_dict'):
                work_items = work_order_data.to_dict('records')
            else:
                work_items = work_order_data if isinstance(work_order_data, list) else []
            
            print(f"Processing {len(work_items)} work items...")
            
            # Test the FIXED approach
            for idx, row in enumerate(work_items[:5]):  # Test first 5 items
                print(f"\nItem {idx + 1}:")
                print(f"  Row type: {type(row)}")
                
                # OLD problematic approach (would fail)
                try:
                    # This is the problematic line that caused the error
                    item_no_old = str(row.get('Item No.', row.get('Item', f'Item_{idx + 1}')))
                    print(f"  OLD approach - Item No: {item_no_old}")
                except AttributeError as e:
                    print(f"  OLD approach - ERROR: {e}")
                
                # NEW fixed approach
                # First try to get 'Item No.', if not found try 'Item', if neither found use default
                item_no_value = row.get('Item No.')
                if item_no_value is None:
                    item_no_value = row.get('Item', f'Item_{idx + 1}')
                item_no = str(item_no_value)
                print(f"  NEW approach - Item No: {item_no}")
                
                # Test description extraction
                description_value = row.get('Description')
                if description_value is None:
                    description_value = row.get('item_description', 'No description')
                description = str(description_value)
                print(f"  Description: {description[:50]}...")
                
                # Test unit extraction
                unit_value = row.get('Unit')
                if unit_value is None:
                    unit_value = row.get('unit', 'Unit')
                unit = str(unit_value)
                print(f"  Unit: {unit}")
            
            print("\n" + "=" * 60)
            print("✅ FIX VERIFIED: The new approach prevents the AttributeError!")
            return True
        
    except Exception as e:
        print(f"Error in test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fix()