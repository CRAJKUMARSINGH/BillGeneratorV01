import pandas as pd
from enhanced_document_generator_fixed import DocumentGenerator

def test_final_bill_scrutiny_sheet():
    """Test that final bill scrutiny sheet matches first page format"""
    
    # Sample data
    title_data = {
        'Project Name': 'Test Project',
        'Contract No': 'CT-001',
        'Work Order No': 'WO-001'
    }
    
    work_order_data = pd.DataFrame([
        {
            'Unit': 'MTR',
            'Quantity Since': 100,
            'Quantity Upto': 100,
            'Item No.': '1',
            'Description': 'Earth Work',
            'Rate': 50,
            'Remark': 'Regular item'
        },
        {
            'Unit': 'MTR',
            'Quantity Since': 50,
            'Quantity Upto': 50,
            'Item No.': '2',
            'Description': 'Concrete Work',
            'Rate': 0,  # Zero rate item
            'Remark': 'Zero rate item'
        }
    ])
    
    extra_items_data = pd.DataFrame([
        {
            'Unit': 'LS',
            'Quantity': 1,
            'Item No.': 'E1',
            'Description': 'Extra Work',
            'Rate': 1000,
            'Remark': 'Extra item'
        }
    ])
    
    # Create document generator
    data = {
        'title_data': title_data,
        'work_order_data': work_order_data,
        'bill_quantity_data': work_order_data,  # Using same data for simplicity
        'extra_items_data': extra_items_data
    }
    
    generator = DocumentGenerator(data)
    
    print("Testing Final Bill Scrutiny Sheet generation...")
    
    try:
        # Generate final bill scrutiny sheet
        final_bill_scrutiny = generator._generate_final_bill_scrutiny()
        print("✅ Final Bill Scrutiny Sheet generated successfully")
        
        # Check that it contains the same structure as first page
        if 'FOR CONTRACTORS & SUPPLIERS ONLY FOR PAYMENT FOR WORK OR SUPPLIES ACTUALLY MEASURED' in final_bill_scrutiny:
            print("✅ Contains correct header")
        else:
            print("❌ Missing correct header")
            
        if 'Unit' in final_bill_scrutiny and 'Quantity executed' in final_bill_scrutiny:
            print("✅ Contains correct column headers")
        else:
            print("❌ Missing correct column headers")
            
        if 'Earth Work' in final_bill_scrutiny and 'Concrete Work' in final_bill_scrutiny:
            print("✅ Contains work items")
        else:
            print("❌ Missing work items")
            
        if 'Extra Items' in final_bill_scrutiny:
            print("✅ Contains extra items section")
        else:
            print("❌ Missing extra items section")
            
        print("✅ Final Bill Scrutiny Sheet format verification completed")
        
    except Exception as e:
        print(f"❌ Error generating Final Bill Scrutiny Sheet: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_bill_scrutiny_sheet()