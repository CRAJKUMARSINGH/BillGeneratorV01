#!/usr/bin/env python3
"""
Test script to process Excel files and organize output in test_outputs directory
- All output in one folder test_outputs
- Separate subfolders for different input file results
- Multiple results with same input separated by timestamped subfolders
"""

import pandas as pd
import sys
from pathlib import Path
import os
from datetime import datetime
import traceback

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def process_excel_file(file_path: Path):
    """Process an Excel file and return sheet information"""
    try:
        print(f"Processing file: {file_path.name}")
        
        # Load Excel file
        xl = pd.ExcelFile(file_path)
        
        # Get sheet names
        sheet_names = xl.sheet_names
        print(f"  Sheets: {sheet_names}")
        
        # Process each sheet
        sheet_data = {}
        for sheet_name in sheet_names:
            try:
                # Parse sheet
                df = xl.parse(sheet_name, header=None)
                # Ensure df is a DataFrame
                if isinstance(df, pd.DataFrame):
                    sheet_data[sheet_name] = {
                        'shape': df.shape,
                        'rows': df.shape[0],
                        'columns': df.shape[1]
                    }
                    print(f"  Sheet '{sheet_name}' shape: {df.shape}")
                else:
                    sheet_data[sheet_name] = {
                        'error': 'Parsed data is not a DataFrame'
                    }
                    print(f"  Sheet '{sheet_name}': Parsed data is not a DataFrame")
            except Exception as e:
                print(f"  Error processing sheet '{sheet_name}': {e}")
                sheet_data[sheet_name] = {
                    'error': str(e)
                }
        
        return {
            'success': True,
            'file_name': file_path.name,
            'sheets': sheet_names,
            'sheet_data': sheet_data
        }
    except Exception as e:
        print(f"Error processing file {file_path.name}: {e}")
        return {
            'success': False,
            'file_name': file_path.name,
            'error': str(e)
        }

def create_output_structure(input_files, base_output_dir="test_outputs"):
    """Create organized output structure for test results"""
    # Create base output directory
    output_root = Path(base_output_dir)
    output_root.mkdir(exist_ok=True)
    
    # Create timestamp for this test run
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    results = []
    
    # Process each input file
    for file_path in input_files:
        try:
            print(f"\n{'='*50}")
            print(f"Processing: {file_path.name}")
            print(f"{'='*50}")
            
            # Process the Excel file
            result = process_excel_file(file_path)
            results.append(result)
            
            # Create output directory structure:
            # test_outputs/
            #   ├── filename_without_extension/
            #   │   ├── timestamp/
            #   │   │   └── results.txt
            #   │   └── latest/  (symlink or copy of latest)
            
            file_stem = file_path.stem  # filename without extension
            file_output_dir = output_root / file_stem
            file_output_dir.mkdir(exist_ok=True)
            
            # Create timestamped subdirectory
            timestamp_dir = file_output_dir / timestamp
            timestamp_dir.mkdir(exist_ok=True)
            
            # Create latest directory (or update symlink)
            latest_dir = file_output_dir / "latest"
            if latest_dir.exists():
                # Remove existing latest directory
                import shutil
                shutil.rmtree(latest_dir)
            # Create new latest directory with results
            latest_dir.mkdir(exist_ok=True)
            
            # Write results to files
            result_file = timestamp_dir / "results.txt"
            latest_result_file = latest_dir / "results.txt"
            
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(f"Excel File Processing Results\n")
                f.write(f"============================\n")
                f.write(f"File: {result['file_name']}\n")
                f.write(f"Processed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Success: {result['success']}\n\n")
                
                if result['success']:
                    f.write(f"Sheet Names: {', '.join(result['sheets'])}\n\n")
                    f.write("Sheet Details:\n")
                    f.write("--------------\n")
                    for sheet_name, data in result['sheet_data'].items():
                        if 'error' in data:
                            f.write(f"  {sheet_name}: ERROR - {data['error']}\n")
                        else:
                            f.write(f"  {sheet_name}: {data['rows']} rows × {data['columns']} columns\n")
                else:
                    f.write(f"Error: {result['error']}\n")
            
            # Copy to latest directory
            import shutil
            shutil.copy2(result_file, latest_result_file)
            
            print(f"  Results saved to: {result_file}")
            print(f"  Latest results updated: {latest_result_file}")
            
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            traceback.print_exc()
    
    # Create summary file
    summary_file = output_root / f"summary_{timestamp}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"Excel Processing Summary\n")
        f.write(f"=======================\n")
        f.write(f"Test Run: {timestamp}\n")
        f.write(f"Files Processed: {len(results)}\n\n")
        
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        f.write(f"Successful: {successful}\n")
        f.write(f"Failed: {failed}\n\n")
        
        f.write("Details:\n")
        f.write("--------\n")
        for result in results:
            status = "✓" if result['success'] else "✗"
            f.write(f"  {status} {result['file_name']}\n")
    
    print(f"\n{'='*50}")
    print(f"Test Summary:")
    print(f"  Total files processed: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Summary saved to: {summary_file}")
    print(f"  Output directory: {output_root}")
    print(f"{'='*50}")
    
    return results

def main():
    """Main function to run the test"""
    print("Excel File Processing Test")
    print("=" * 30)
    
    # Define input directory
    input_dir = Path("INPUT_FILES")
    
    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' not found!")
        return False
    
    # Get list of Excel files
    excel_files = list(input_dir.glob("*.xlsx"))
    
    if not excel_files:
        print(f"No Excel files found in '{input_dir}'")
        return False
    
    print(f"Found {len(excel_files)} Excel files in '{input_dir}'")
    
    # Select a few sample files for testing (first 5)
    sample_files = excel_files[:5]
    print(f"Processing first {len(sample_files)} files as samples:")
    for file in sample_files:
        print(f"  - {file.name}")
    
    # Process files and create output structure
    results = create_output_structure(sample_files)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)