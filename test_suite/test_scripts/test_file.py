import pandas as pd

# Load the Excel file
file_path = 'test_input_files/3rdFinalNoExtra.xlsx'
excel_file = pd.ExcelFile(file_path)

print("Available sheets:", excel_file.sheet_names)

# Check Work Order sheet
if 'Work Order' in excel_file.sheet_names:
    print("\n--- Work Order Sheet ---")
    work_order_df = pd.read_excel(excel_file, 'Work Order')
    print("Shape:", work_order_df.shape)
    print("Columns:", list(work_order_df.columns))
    print("\nFirst 10 rows:")
    print(work_order_df.head(10))

# Check Title sheet
if 'Title' in excel_file.sheet_names:
    print("\n--- Title Sheet ---")
    title_df = pd.read_excel(excel_file, 'Title', header=None)
    print("Shape:", title_df.shape)
    print("First 10 rows:")
    print(title_df.head(10))
    
    # Convert to dictionary
    title_data = {}
    for index, row in title_df.iterrows():
        if len(row) >= 2 and pd.notna(row[0]) and pd.notna(row[1]):
            key = str(row[0]).strip()
            val = str(row[1]).strip()
            if key and val and key != 'nan' and val != 'nan':
                title_data[key] = val
    
    print("\nTitle data:", title_data)