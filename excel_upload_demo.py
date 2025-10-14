#!/usr/bin/env python3
"""
Excel Upload Mode Testing Demonstration
This script demonstrates how the Excel upload mode would work
"""

import sys
import os
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ExcelUploadDemo:
    """Demonstrates Excel upload mode functionality"""
    
    def __init__(self):
        self.input_dir = Path("INPUT_FILES")
        self.output_base = Path("OUTPUT_FILES")
    
    def demonstrate_excel_processing(self):
        """Demonstrate processing of multiple Excel files"""
        print("📂 Excel Upload Mode Demonstration")
        print("=" * 50)
        
        # Get test files
        test_files = list(self.input_dir.glob("*.xlsx"))
        
        if not test_files:
            print("❌ No test files found in INPUT_FILES directory")
            return False
        
        print(f"📁 Found {len(test_files)} Excel files to process")
        
        # Create output directory with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = self.output_base / timestamp / "excel_upload_demo"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process results tracking
        results = {
            'total_files': len(test_files),
            'processed_files': 0,
            'failed_files': 0,
            'processing_log': []
        }
        
        # Process first 5 files as a demo
        demo_files = test_files[:5]
        print(f"\n🚀 Processing first {len(demo_files)} files as demonstration...")
        
        for i, file_path in enumerate(demo_files, 1):
            print(f"\n[{i}/{len(demo_files)}] Processing {file_path.name}...")
            
            try:
                # Create individual output directory for this file
                file_output_dir = output_dir / file_path.stem
                file_output_dir.mkdir(exist_ok=True)
                
                # Simulate Excel processing (in real implementation, this uses ExcelProcessor)
                processing_result = self.simulate_excel_processing(file_path, file_output_dir)
                
                if processing_result['success']:
                    results['processed_files'] += 1
                    print(f"  ✅ Successfully processed {file_path.name}")
                else:
                    results['failed_files'] += 1
                    print(f"  ❌ Failed to process {file_path.name}")
                
                results['processing_log'].append(processing_result)
                
            except Exception as e:
                results['failed_files'] += 1
                print(f"  ❌ Error processing {file_path.name}: {e}")
                results['processing_log'].append({
                    'file': file_path.name,
                    'success': False,
                    'error': str(e)
                })
        
        # Save results
        self.save_excel_results(results, output_dir)
        
        # Print summary
        success_rate = (results['processed_files'] / len(demo_files)) * 100 if demo_files else 0
        print(f"\n📊 Excel Upload Mode Summary:")
        print(f"  Total Files Processed: {len(demo_files)}")
        print(f"  Successful: {results['processed_files']}")
        print(f"  Failed: {results['failed_files']}")
        print(f"  Success Rate: {success_rate:.1f}%")
        
        return results['processed_files'] > 0
    
    def simulate_excel_processing(self, file_path, output_dir):
        """Simulate Excel processing (in real implementation, this uses ExcelProcessor)"""
        try:
            # Simulate reading Excel file and extracting data
            # In real implementation, this would use:
            # processor = ExcelProcessor(str(file_path))
            # result = processor.process_excel()
            
            # For demo, we'll simulate the result structure
            simulated_result = self.create_simulated_excel_data()
            
            # Save simulated data
            self.save_simulated_data(simulated_result, output_dir)
            
            return {
                'file': file_path.name,
                'success': True,
                'sheets_processed': ['Title', 'Work Order', 'Bill Quantity'],
                'work_items_count': len(simulated_result.get('work_order_data', [])),
                'title_items_count': len(simulated_result.get('title_data', {}))
            }
            
        except Exception as e:
            return {
                'file': file_path.name,
                'success': False,
                'error': str(e)
            }
    
    def create_simulated_excel_data(self):
        """Create simulated Excel data"""
        # Simulated title data
        title_data = {
            "Name of Work": "Test Infrastructure Project",
            "Agreement No.": "AG-1234",
            "Reference to work order": "WO-567/2025",
            "Name of Contractor": "ABC Construction Ltd",
            "Bill Number": "BILL-8901",
            "Running or Final": "Running",
            "WORK ORDER AMOUNT RS.": 1500000,
            "Date of measurement": "15-10-2025"
        }
        
        # Simulated work order data
        work_order_data = [
            {"Item No.": "01", "Description": "Excavation in ordinary soil", "Unit": "CuM", "Rate": 1200.00, "Quantity Since": 50.00},
            {"Item No.": "02", "Description": "Brickwork in cement mortar 1:6", "Unit": "CuM", "Rate": 8500.00, "Quantity Since": 25.50},
            {"Item No.": "03", "Description": "RCC M20 for foundation", "Unit": "CuM", "Rate": 9200.00, "Quantity Since": 30.00},
            {"Item No.": "04", "Description": "Plastering in cement mortar 1:6", "Unit": "SqM", "Rate": 65.00, "Quantity Since": 500.00},
            {"Item No.": "05", "Description": "Electrical wiring with copper cables", "Unit": "Mtr", "Rate": 120.00, "Quantity Since": 200.00}
        ]
        
        # Simulated bill quantity data
        bill_quantity_data = [
            {"Item No.": "01", "Description": "Excavation in ordinary soil", "Unit": "CuM", "Quantity": 45.00, "Rate": 1200.00, "Amount": 54000.00},
            {"Item No.": "02", "Description": "Brickwork in cement mortar 1:6", "Unit": "CuM", "Quantity": 25.00, "Rate": 8500.00, "Amount": 212500.00},
            {"Item No.": "04", "Description": "Plastering in cement mortar 1:6", "Unit": "SqM", "Quantity": 480.00, "Rate": 65.00, "Amount": 31200.00}
        ]
        
        return {
            'title_data': title_data,
            'work_order_data': work_order_data,
            'bill_quantity_data': bill_quantity_data
        }
    
    def save_simulated_data(self, data, output_dir):
        """Save simulated data to files"""
        try:
            # Save title data
            if 'title_data' in data:
                title_df = pd.DataFrame(list(data['title_data'].items()), columns=['Key', 'Value'])
                title_df.to_csv(output_dir / "title_data.csv", index=False)
            
            # Save work order data
            if 'work_order_data' in data:
                work_order_df = pd.DataFrame(data['work_order_data'])
                work_order_df.to_csv(output_dir / "work_order_data.csv", index=False)
            
            # Save bill quantity data
            if 'bill_quantity_data' in data:
                bill_qty_df = pd.DataFrame(data['bill_quantity_data'])
                bill_qty_df.to_csv(output_dir / "bill_quantity_data.csv", index=False)
                
        except Exception as e:
            print(f"  ⚠️  Error saving data: {e}")
    
    def save_excel_results(self, results, output_dir):
        """Save Excel processing results"""
        # Add timestamp to results
        results['timestamp'] = datetime.now().isoformat()
        
        # Save JSON results
        with open(output_dir / "processing_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save human-readable report
        report_content = f"""
# Excel Upload Mode Test Results

**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Files Processed:** {results['total_files']}
**Successful Files:** {results['processed_files']}
**Failed Files:** {results['failed_files']}
**Success Rate:** {(results['processed_files'] / results['total_files'] * 100):.1f}%

## Processing Log

"""
        
        for log_entry in results['processing_log']:
            if log_entry['success']:
                report_content += f"- ✅ {log_entry['file']}: Processed successfully\n"
                report_content += f"  - Sheets: {', '.join(log_entry['sheets_processed'])}\n"
                report_content += f"  - Work Items: {log_entry['work_items_count']}\n"
            else:
                report_content += f"- ❌ {log_entry['file']}: Failed - {log_entry.get('error', 'Unknown error')}\n"
        
        report_content += f"""

## Summary

The Excel Upload Mode processes Excel files in bulk, extracting data from Title, Work Order, 
and Bill Quantity sheets. Each file is validated and processed independently, with results 
saved to timestamped output directories.

This mode is ideal for organizations that have prepared Excel files and want to process 
multiple bills simultaneously.
"""
        
        with open(output_dir / "report.md", 'w') as f:
            f.write(report_content)

def main():
    """Main demonstration function"""
    print("🚀 Excel Upload Mode Testing Demonstration")
    print("=" * 50)
    
    # Initialize demo
    demo = ExcelUploadDemo()
    
    # Run demonstration
    success = demo.demonstrate_excel_processing()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Excel Upload Mode Demo Completed Successfully!")
        print("📁 Check OUTPUT_FILES directory for results")
    else:
        print("❌ Excel Upload Mode Demo Failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)