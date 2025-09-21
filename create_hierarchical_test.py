import pandas as pd
import numpy as np
from datetime import datetime
import os

# Create hierarchical test structure
def create_hierarchical_test():
    # Title Sheet Data
    title_data = {
        'Name of Work ;-': 'Infrastructure Development Project - Hierarchical Test',
        'Agreement No.': 'AGREEMENT/2024/001',
        'Reference to work order or Agreement :': 'WO/2024/HD/001',
        'Name of Contractor or supplier :': 'ABC Construction Ltd.',
        'Bill Number': 'BILL/2024/001',
        'Running or Final': 'Running',
        'TENDER PREMIUM %': 5.0,
        'WORK ORDER AMOUNT RS.': 1500000.00,
        'Date of written order to commence work :': '01/01/2024',
        'St. date of Start :': '01/01/2024',
        'St. date of completion :': '31/12/2024',
        'Date of actual completion of work :': '',
        'Date of measurement :': '15/01/2024'
    }
    
    # Work Order Data - Hierarchical Structure
    work_order_items = []
    
    # Main Categories
    main_categories = [
        {'name': 'EARTHWORK', 'prefix': '1', 'base_rate': 100},
        {'name': 'CONCRETE WORK', 'prefix': '2', 'base_rate': 200},
        {'name': 'FINISHING WORK', 'prefix': '3', 'base_rate': 150}
    ]
    
    sub_categories = [
        {'name': 'EXCAVATION', 'suffix': 'A'},
        {'name': 'FILLING', 'suffix': 'B'},
        {'name': 'COMPACTION', 'suffix': 'C'}
    ]
    
    sub_sub_categories = [
        {'name': 'MANUAL', 'code': '1'},
        {'name': 'MECHANICAL', 'code': '2'},
        {'name': 'SPECIAL', 'code': '3'}
    ]
    
    item_counter = 1
    
    for main_cat in main_categories:
        for sub_cat in sub_categories:
            for sub_sub_cat in sub_sub_categories:
                # Create item number
                item_no = f"{main_cat['prefix']}.{sub_cat['suffix']}.{sub_sub_cat['code']}"
                
                # Create description
                description = f"{main_cat['name']} - {sub_cat['name']} - {sub_sub_cat['name']}"
                
                # Vary rates and quantities for testing
                base_rate = main_cat['base_rate'] + (item_counter * 10)
                
                # Some items have zero rates (for testing rate rules)
                if item_counter % 7 == 0:
                    rate = 0.0
                    unit = 'Nos'
                    wo_qty = 10.0
                elif item_counter % 5 == 0:
                    rate = base_rate
                    unit = ''  # Blank unit for testing
                    wo_qty = 0.0  # Blank quantity for testing
                else:
                    rate = base_rate
                    unit = 'Cum'
                    wo_qty = 5.0 + (item_counter % 3)
                
                # Some items have blank/NaN values for testing
                if item_counter % 11 == 0:
                    description = ''  # Blank description
                if item_counter % 13 == 0:
                    unit = None  # None unit
                
                work_order_items.append({
                    'Item No.': item_no,
                    'Description': description,
                    'Unit': unit,
                    'Quantity Since': wo_qty,
                    'Quantity Upto': wo_qty,
                    'Rate': rate,
                    'Amount Since': wo_qty * rate,
                    'Amount Upto': wo_qty * rate,
                    'Remark': f'Test item {item_counter}'
                })
                
                item_counter += 1
    
    # Bill Quantity Data (subset for testing)
    bill_quantity_items = []
    for i, item in enumerate(work_order_items[:15]):  # Only first 15 items
        if item['Rate'] > 0:  # Only for non-zero rate items
            bill_qty = item['Quantity Since'] * 0.8  # 80% of WO quantity
            bill_quantity_items.append({
                'Item No.': item['Item No.'],
                'Description': item['Description'],
                'Unit': item['Unit'],
                'Quantity': bill_qty,
                'Rate': item['Rate'],
                'Amount': bill_qty * item['Rate']
            })
    
    # Extra Items Data
    extra_items = [
        {
            'Item No.': 'EXT-001',
            'Description': 'Additional Safety Equipment',
            'Unit': 'Nos',
            'Quantity': 5.0,
            'Rate': 500.0,
            'Amount': 2500.0
        },
        {
            'Item No.': 'EXT-002', 
            'Description': 'Emergency Materials',
            'Unit': 'Ltr',
            'Quantity': 100.0,
            'Rate': 25.0,
            'Amount': 2500.0
        }
    ]
    
    return title_data, work_order_items, bill_quantity_items, extra_items

# Generate the test file
def create_test_excel():
    # Ensure directory exists
    os.makedirs('test_input_files', exist_ok=True)
    
    title_data, work_order_items, bill_quantity_items, extra_items = create_hierarchical_test()
    
    with pd.ExcelWriter('test_input_files/hierarchical_test_structure.xlsx', engine='openpyxl') as writer:
        # Title Sheet
        title_df = pd.DataFrame([title_data])
        title_df.to_excel(writer, sheet_name='Title', index=False)
        
        # Work Order Sheet
        work_order_df = pd.DataFrame(work_order_items)
        work_order_df.to_excel(writer, sheet_name='Work Order', index=False)
        
        # Bill Quantity Sheet
        bill_quantity_df = pd.DataFrame(bill_quantity_items)
        bill_quantity_df.to_excel(writer, sheet_name='Bill Quantity', index=False)
        
        # Extra Items Sheet
        extra_items_df = pd.DataFrame(extra_items)
        extra_items_df.to_excel(writer, sheet_name='Extra Items', index=False)
    
    print("✅ Hierarchical test file created successfully!")
    print(f"📊 Structure: {len(work_order_items)} total items")
    print(f"📋 Bill items: {len(bill_quantity_items)}")
    print(f"➕ Extra items: {len(extra_items)}")
    
    # Print structure summary
    print("\n📋 Structure Summary:")
    print("Main Categories: 3 (EARTHWORK, CONCRETE WORK, FINISHING WORK)")
    print("Sub Categories: 3 each (EXCAVATION, FILLING, COMPACTION)")
    print("Sub-Sub Categories: 3 each (MANUAL, MECHANICAL, SPECIAL)")
    print("Total Items: 3 × 3 × 3 = 27 items")
    
    # Print test scenarios
    print("\n🧪 Test Scenarios Included:")
    print("- Zero rate items (for rate rule testing)")
    print("- Blank units and quantities")
    print("- Blank descriptions")
    print("- None values")
    print("- Mixed rate structures")

if __name__ == "__main__":
    create_test_excel()
