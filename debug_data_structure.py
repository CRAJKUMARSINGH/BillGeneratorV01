import pandas as pd
from utils.excel_processor import ExcelProcessor

def debug_data_structure():
    """Debug the data structure to understand the error"""
    
    print("Debugging data structure...")
    print("=" * 50)
    
    # Load test data
    file_path = 'test_input_files/3rdFinalNoExtra.xlsx'
    
    try:
        # Process the Excel file
        processor = ExcelProcessor(file_path)
        result = processor.process_excel()
        
        work_order_data = result.get('work_order_data')
        print(f"Work order data type: {type(work_order_data)}")
        print(f"Work order data is DataFrame: {isinstance(work_order_data, pd.DataFrame)}")
        
        if work_order_data is not None and not work_order_data.empty:
            print(f"Work order shape: {work_order_data.shape}")
            print(f"Work order columns: {list(work_order_data.columns)}")
            print("\nFirst few rows:")
            print(work_order_data.head())
            
            # Convert to list if it's a DataFrame
            if hasattr(work_order_data, 'to_dict'):
                work_items = work_order_data.to_dict('records')
            else:
                work_items = work_order_data if isinstance(work_order_data, list) else []
            
            print(f"\nWork items type: {type(work_items)}")
            print(f"Work items length: {len(work_items)}")
            
            if work_items:
                first_item = work_items[0]
                print(f"First item type: {type(first_item)}")
                print(f"First item: {first_item}")
                
                # Test the problematic operation
                print("\n--- Testing row.get operations ---")
                if isinstance(first_item, dict):
                    print("First item is a dictionary")
                    item_no = first_item.get('Item No.', first_item.get('Item', 'Default'))
                    print(f"Item No: {item_no} (type: {type(item_no)})")
                    
                    # This is the problematic line - what if first_item.get('Item', 'Default') returns a string?
                    try:
                        # This would fail if first_item.get('Item', 'Default') returns a string
                        result = first_item.get('Item No.', first_item.get('Item', 'Default').get('nested', 'fallback'))
                        print(f"Nested get result: {result}")
                    except AttributeError as e:
                        print(f"AttributeError as expected: {e}")
                else:
                    print("First item is NOT a dictionary")
                    
        return True
        
    except Exception as e:
        print(f"Error in debug: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_data_structure()