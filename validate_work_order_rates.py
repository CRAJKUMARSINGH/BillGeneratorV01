#!/usr/bin/env python3
"""
Validate work order files for missing rates
"""

import pandas as pd
from pathlib import Path
import sys

def validate_work_order_rates(file_path):
    """Validate that all work order items have rates"""
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Look for rate columns
        rate_columns = [col for col in df.columns if 'rate' in col.lower() or 'Rate' in col]
        
        if not rate_columns:
            return False, f"No rate column found in {file_path.name}. Available columns: {list(df.columns)}"
        
        # Check the first rate column found
        rate_col = rate_columns[0]
        
        # Check for missing or zero rates
        missing_rates = df[df[rate_col].isna() | (df[rate_col] == 0) | (df[rate_col] == '')]
        
        if len(missing_rates) > 0:
            # Get description column for context
            desc_columns = [col for col in df.columns if 'desc' in col.lower() or 'Desc' in col or 'Item' in col]
            desc_col = desc_columns[0] if desc_columns else df.columns[0]
            
            missing_items = []
            for idx, row in missing_rates.iterrows():
                desc = row.get(desc_col, "Unknown item")
                rate = row.get(rate_col, "N/A")
                missing_items.append(f"  - '{desc}' (Rate: {rate})")
            
            error_msg = f"Missing rates in work order: {len(missing_rates)} items found without valid rates\n"
            error_msg += "\n".join(missing_items[:10])  # Show first 10 items
            if len(missing_items) > 10:
                error_msg += f"\n  ... and {len(missing_items) - 10} more items"
                
            return False, error_msg
        else:
            return True, f"All {len(df)} items have valid rates in column '{rate_col}'"
            
    except Exception as e:
        return False, f"Error reading {file_path.name}: {str(e)}"

def main():
    """Main function to validate all input files"""
    input_dir = Path("INPUT_FILES")
    if not input_dir.exists():
        print("INPUT_FILES directory not found")
        return
    
    # Check all Excel files
    excel_files = list(input_dir.glob("*.xlsx")) + list(input_dir.glob("*.xls"))
    
    if not excel_files:
        print("No Excel files found in INPUT_FILES directory")
        return
    
    print("Validating work order files for missing rates...")
    print("=" * 60)
    
    validation_errors = []
    
    for file_path in excel_files:
        is_valid, message = validate_work_order_rates(file_path)
        status = "✅" if is_valid else "❌"
        print(f"{status} {file_path.name}: {message}")
        
        if not is_valid:
            validation_errors.append(f"{file_path.name}: {message}")
    
    print("\n" + "=" * 60)
    if validation_errors:
        print(f"❌ Found {len(validation_errors)} files with validation errors:")
        for error in validation_errors:
            print(f"  - {error}")
        return 1
    else:
        print("✅ All files passed validation - no missing rates found")
        return 0

if __name__ == "__main__":
    sys.exit(main())