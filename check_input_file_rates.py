#!/usr/bin/env python3
"""
Check input files for missing rates
"""

import pandas as pd
from pathlib import Path

def check_file_for_rates(file_path):
    """Check a specific file for rate issues"""
    try:
        print(f"Checking {file_path.name}...")
        df = pd.read_excel(file_path)
        
        print(f"  Columns: {list(df.columns)}")
        print(f"  Rows: {len(df)}")
        
        # Look for rate columns
        rate_cols = [col for col in df.columns if 'rate' in col.lower() or 'Rate' in col]
        print(f"  Potential rate columns: {rate_cols}")
        
        if rate_cols:
            for col in rate_cols:
                missing_rates = df[df[col].isna() | (df[col] == 0)]
                if len(missing_rates) > 0:
                    print(f"  ❌ Found {len(missing_rates)} items with missing/zero rates in '{col}'")
                    # Show first few rows with missing rates
                    print("  Sample rows with missing rates:")
                    for idx, row in missing_rates.head().iterrows():
                        desc_col = [c for c in df.columns if 'desc' in c.lower() or 'Desc' in c]
                        desc = row[desc_col[0]] if desc_col else "N/A"
                        print(f"    Row {idx}: '{desc}' - Rate: {row[col]}")
                else:
                    print(f"  ✅ All rates present in '{col}'")
        else:
            print("  ⚠️  No rate columns identified")
            
    except Exception as e:
        print(f"  Error reading file: {e}")

def main():
    """Main function to check input files"""
    input_dir = Path("INPUT_FILES")
    if not input_dir.exists():
        print("INPUT_FILES directory not found")
        return
    
    # Check a few sample files
    sample_files = [
        "3rdFinalNoExtra.xlsx",
        "3rdFinalVidExtra.xlsx", 
        "FirstFINALnoExtra.xlsx"
    ]
    
    for file_name in sample_files:
        file_path = input_dir / file_name
        if file_path.exists():
            check_file_for_rates(file_path)
            print()

if __name__ == "__main__":
    main()