#!/usr/bin/env python3
"""
Debug script to identify validation errors related to missing rates in work order
"""

import pandas as pd
import json
from pathlib import Path

def check_for_missing_rates():
    """Check input files for missing rates"""
    input_dir = Path("INPUT_FILES")
    if not input_dir.exists():
        print("INPUT_FILES directory not found")
        return
    
    # Check all Excel files in INPUT_FILES
    excel_files = list(input_dir.glob("*.xlsx")) + list(input_dir.glob("*.xls"))
    
    print(f"Found {len(excel_files)} Excel files in INPUT_FILES")
    
    for file_path in excel_files:
        print(f"\nChecking {file_path.name}...")
        try:
            # Read the Excel file
            df = pd.read_excel(file_path)
            
            # Check for columns that might contain rates
            rate_columns = ['Rate', 'rate', 'Unit Rate', 'Unit rate', 'UnitRate', 'Work Rate']
            found_rate_column = None
            
            for col in rate_columns:
                if col in df.columns:
                    found_rate_column = col
                    break
            
            if found_rate_column:
                # Check for missing or zero rates
                missing_rates = df[df[found_rate_column].isna() | (df[found_rate_column] == 0)]
                if len(missing_rates) > 0:
                    print(f"  ❌ Found {len(missing_rates)} items with missing or zero rates in '{found_rate_column}' column")
                    print("  First few items with missing rates:")
                    print(missing_rates.head()[['Description', found_rate_column] if 'Description' in df.columns else missing_rates.head().columns[:2]])
                else:
                    print(f"  ✅ All rates present in '{found_rate_column}' column")
            else:
                print(f"  ⚠️  No rate column found. Available columns: {list(df.columns)}")
                
        except Exception as e:
            print(f"  Error reading {file_path.name}: {e}")

def check_validation_reports():
    """Check for existing validation reports"""
    validation_files = [
        "VBA_COMPLIANCE_VALIDATION_REPORT.md",
        "FINAL_VALIDATION_SUMMARY.md",
        "ZERO_RATE_ENHANCEMENT_REPORT.md",
        "VALIDATION_EVIDENCE.txt"
    ]
    
    for file_name in validation_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"\nFound validation report: {file_name}")
            # Show first few lines
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"  First 5 lines:")
                for i, line in enumerate(lines[:5]):
                    print(f"    {line.strip()}")
                    if i >= 4:
                        break

if __name__ == "__main__":
    print("Debugging validation errors...")
    print("=" * 50)
    
    check_for_missing_rates()
    check_validation_reports()
    
    print("\n" + "=" * 50)
    print("Debug complete")