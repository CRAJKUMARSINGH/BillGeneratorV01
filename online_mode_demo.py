#!/usr/bin/env python3
"""
Online Mode Testing Demonstration
This script demonstrates how the online mode would work with simulated user input
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import required modules
try:
    from utils.excel_processor import ExcelProcessor
    print("✅ Required modules imported successfully")
except ImportError as e:
    print(f"⚠️  Some modules could not be imported: {e}")
    print("    This is expected in a demonstration environment")

class OnlineModeDemo:
    """Demonstrates online mode functionality"""
    
    def __init__(self):
        self.input_dir = Path("INPUT_FILES")
        self.output_base = Path("OUTPUT_FILES")
    
    def simulate_user_workflow(self, file_path):
        """Simulate the complete online user workflow"""
        print(f"\n🤖 Simulating Online Mode Workflow for: {file_path.name}")
        print("-" * 50)
        
        try:
            # Step 1: Process Excel file to get work order data
            print("📋 Step 1: Loading Work Order Data...")
            if os.path.exists(file_path):
                print("  ✅ File found, processing...")
                # In real implementation, this would use ExcelProcessor
                # For demo, we'll simulate the data structure
                work_order_data = self.simulate_work_order_data()
                print(f"  📊 Loaded {len(work_order_data)} work items")
            else:
                print("  ⚠️  File not found, using sample data")
                work_order_data = self.create_sample_work_order()
            
            # Step 2: Simulate user entering bill quantities (60-75% of items)
            print("\n💰 Step 2: Entering Bill Quantities...")
            bill_data = self.simulate_bill_quantity_entry(work_order_data)
            print(f"  ✅ Entered quantities for {len(bill_data)} items")
            
            # Step 3: Add extra items (1-10 items)
            print("\n➕ Step 3: Adding Extra Items...")
            extra_items = self.simulate_extra_items()
            print(f"  ✅ Added {len(extra_items)} extra items")
            
            # Step 4: Calculate totals and generate summary
            print("\n📊 Step 4: Calculating Totals...")
            summary = self.calculate_summary(bill_data, extra_items)
            print(f"  💰 Total Bill Amount: ₹{summary['bill_total']:,.2f}")
            print(f"  💰 Extra Items Total: ₹{summary['extra_total']:,.2f}")
            print(f"  💰 Grand Total: ₹{summary['grand_total']:,.2f}")
            
            # Step 5: Save results
            print("\n💾 Step 5: Saving Results...")
            self.save_online_mode_results(file_path.name, bill_data, extra_items, summary)
            print("  ✅ Results saved successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in workflow simulation: {e}")
            return False
    
    def simulate_work_order_data(self):
        """Simulate work order data (in real implementation, this comes from ExcelProcessor)"""
        # Sample work items
        work_items = [
            {"Item No.": "01", "Description": "Excavation in ordinary soil", "Unit": "CuM", "Rate": 1200.00, "Quantity Since": 50.00},
            {"Item No.": "02", "Description": "Brickwork in cement mortar 1:6", "Unit": "CuM", "Rate": 8500.00, "Quantity Since": 25.50},
            {"Item No.": "03", "Description": "RCC M20 for foundation", "Unit": "CuM", "Rate": 9200.00, "Quantity Since": 30.00},
            {"Item No.": "04", "Description": "Plastering in cement mortar 1:6", "Unit": "SqM", "Rate": 65.00, "Quantity Since": 500.00},
            {"Item No.": "05", "Description": "Electrical wiring with copper cables", "Unit": "Mtr", "Rate": 120.00, "Quantity Since": 200.00},
            {"Item No.": "06", "Description": "Installation of LED lights", "Unit": "No", "Rate": 850.00, "Quantity Since": 25.00},
            {"Item No.": "07", "Description": "Waterproofing treatment", "Unit": "SqM", "Rate": 85.00, "Quantity Since": 150.00},
            {"Item No.": "08", "Description": "Painting with emulsion paint", "Unit": "SqM", "Rate": 45.00, "Quantity Since": 800.00},
        ]
        return work_items
    
    def create_sample_work_order(self):
        """Create sample work order data when file is not available"""
        return self.simulate_work_order_data()
    
    def simulate_bill_quantity_entry(self, work_order_data):
        """Simulate user entering bill quantities (60-75% of items)"""
        print("  🎯 Filling quantities for 60-75% of items...")
        
        # Determine how many items to fill (60-75%)
        fill_percentage = np.random.uniform(0.6, 0.75)
        items_to_fill = int(len(work_order_data) * fill_percentage)
        
        # Randomly select items to fill
        indices_to_fill = np.random.choice(len(work_order_data), items_to_fill, replace=False)
        
        bill_data = []
        for idx, item in enumerate(work_order_data):
            if idx in indices_to_fill:
                # Assign quantity within 10-125% of original Work Order quantity
                try:
                    wo_qty = float(item.get('Quantity Since', 1))
                    bill_qty = wo_qty * np.random.uniform(0.1, 1.25)
                    bill_qty = round(bill_qty, 2)
                except (ValueError, TypeError):
                    wo_qty = 1.0
                    bill_qty = np.random.uniform(1, 20)  # Default quantity
                
                # Calculate amount
                try:
                    rate = float(item.get('Rate', 0))
                except (ValueError, TypeError):
                    rate = 0.0
                
                amount = bill_qty * rate
                
                bill_item = {
                    'item_no': item.get('Item No.', f'Item_{idx+1}'),
                    'description': item.get('Description', 'No description'),
                    'unit': item.get('Unit', 'Unit'),
                    'rate': rate,
                    'work_order_qty': wo_qty,
                    'bill_qty': bill_qty,
                    'amount': amount
                }
                bill_data.append(bill_item)
        
        return bill_data
    
    def simulate_extra_items(self):
        """Simulate adding 1-10 extra items"""
        extra_count = np.random.randint(1, 11)  # 1-10 items
        print(f"  ➕ Adding {extra_count} extra items...")
        
        extra_items = []
        for i in range(extra_count):
            extra_item = {
                'item_no': f"EX{i+1:02d}",
                'description': f"Extra Work Item {i+1} - Additional Services",
                'unit': np.random.choice(['No', 'SqM', 'Mtr', 'CuM']),
                'rate': round(np.random.uniform(100, 2000), 2),
                'bill_qty': round(np.random.uniform(1, 20), 2)
            }
            extra_item['amount'] = extra_item['rate'] * extra_item['bill_qty']
            extra_items.append(extra_item)
        
        return extra_items
    
    def calculate_summary(self, bill_data, extra_items):
        """Calculate totals and summary"""
        bill_total = sum(item['amount'] for item in bill_data)
        extra_total = sum(item['amount'] for item in extra_items)
        grand_total = bill_total + extra_total
        
        return {
            'items_count': len(bill_data),
            'extra_items_count': len(extra_items),
            'bill_total': bill_total,
            'extra_total': extra_total,
            'grand_total': grand_total
        }
    
    def save_online_mode_results(self, file_name, bill_data, extra_items, summary):
        """Save online mode results to output directory"""
        # Create output directory with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = self.output_base / timestamp / "online_mode_demo"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save bill data
        if bill_data:
            bill_df = pd.DataFrame(bill_data)
            bill_df.to_csv(output_dir / "bill_quantities.csv", index=False)
        
        # Save extra items
        if extra_items:
            extra_df = pd.DataFrame(extra_items)
            extra_df.to_csv(output_dir / "extra_items.csv", index=False)
        
        # Save summary
        summary['file_name'] = file_name
        summary['timestamp'] = datetime.now().isoformat()
        
        with open(output_dir / "summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save human-readable report
        report_content = f"""
# Online Mode Test Results

**File Tested:** {file_name}
**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Items with Quantities:** {summary['items_count']}
- **Extra Items Added:** {summary['extra_items_count']}
- **Total Bill Amount:** ₹{summary['bill_total']:,.2f}
- **Extra Items Total:** ₹{summary['extra_total']:,.2f}
- **Grand Total:** ₹{summary['grand_total']:,.2f}

## Details

This simulation demonstrates the online mode workflow where:
1. Work order data is loaded
2. Users enter quantities for 60-75% of items
3. Quantities are assigned within 10-125% of original values
4. 1-10 extra items are added
5. Totals are calculated and results saved

The online mode provides an interactive interface for custom bill creation.
"""
        
        with open(output_dir / "report.md", 'w') as f:
            f.write(report_content)

def main():
    """Main demonstration function"""
    print("🚀 Online Mode Testing Demonstration")
    print("=" * 50)
    
    # Initialize demo
    demo = OnlineModeDemo()
    
    # Get test files
    input_dir = Path("INPUT_FILES")
    if input_dir.exists():
        test_files = list(input_dir.glob("*.xlsx"))
        if test_files:
            # Test with first file
            success = demo.simulate_user_workflow(test_files[0])
        else:
            # Use sample data
            print("⚠️  No test files found, using sample data")
            success = demo.simulate_user_workflow(Path("sample_data.xlsx"))
    else:
        # Use sample data
        print("⚠️  INPUT_FILES directory not found, using sample data")
        success = demo.simulate_user_workflow(Path("sample_data.xlsx"))
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Online Mode Demo Completed Successfully!")
        print("📁 Check OUTPUT_FILES directory for results")
    else:
        print("❌ Online Mode Demo Failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)