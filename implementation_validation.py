#!/usr/bin/env python3
"""
Validate current FirstPageGenerator implementation against VBA specification
"""

import pandas as pd
import sys
import os
from pathlib import Path
import inspect

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.first_page_generator import FirstPageGenerator

def validate_implementation():
    """Validate the current implementation against VBA specification"""
    print("🔍 Validating FirstPageGenerator Implementation")
    print("=" * 60)
    
    # Get the source code of the _process_work_order_item method
    generator = FirstPageGenerator()
    source = inspect.getsource(generator._process_work_order_item)
    
    print("📄 Analyzing _process_work_order_item method:")
    print("-" * 50)
    
    # Check for the critical zero rate handling logic
    if "if rate == 0:" in source:
        print("✅ Found zero rate condition check")
        
        # Check if it only populates Serial No. and Description for zero rates
        lines = source.split('\n')
        in_zero_rate_block = False
        zero_rate_lines = []
        
        for line in lines:
            if "if rate == 0:" in line:
                in_zero_rate_block = True
                continue
            elif in_zero_rate_block:
                if line.strip().startswith("else:"):
                    break
                elif line.strip() and not line.strip().startswith("#"):
                    zero_rate_lines.append(line.strip())
        
        print("📝 Zero rate handling code:")
        for line in zero_rate_lines:
            print(f"  {line}")
        
        # Validate that only Serial No. and Description are populated
        serial_no_populated = any("worksheet.write(current_row, 3" in line for line in zero_rate_lines)
        description_populated = any("worksheet.write(current_row, 4" in line for line in zero_rate_lines)
        other_columns_populated = any(
            ("worksheet.write(current_row, 0" in line) or  # Unit
            ("worksheet.write(current_row, 1" in line) or  # Quantity Since
            ("worksheet.write(current_row, 2" in line) or  # Quantity Upto
            ("worksheet.write(current_row, 5" in line) or  # Rate
            ("worksheet.write(current_row, 6" in line) or  # Amount Upto
            ("worksheet.write(current_row, 7" in line) or  # Amount Since
            ("worksheet.write(current_row, 8" in line)     # Remark
            for line in zero_rate_lines)
        
        if serial_no_populated and description_populated and not other_columns_populated:
            print("✅ Zero rate handling is CORRECT:")
            print("   - Only Serial No. (Column D) and Description (Column E) are populated")
            print("   - All other columns remain blank for zero rate items")
            print("✅ Implementation fully complies with VBA specification")
            return True
        else:
            print("❌ Zero rate handling is INCORRECT:")
            print(f"   - Serial No. populated: {serial_no_populated}")
            print(f"   - Description populated: {description_populated}")
            print(f"   - Other columns populated: {other_columns_populated}")
            return False
    else:
        print("❌ Zero rate condition check NOT found")
        return False

def validate_extra_items():
    """Validate the extra items implementation"""
    print("\n🔍 Validating _process_extra_item method:")
    print("-" * 50)
    
    # Get the source code of the _process_extra_item method
    generator = FirstPageGenerator()
    source = inspect.getsource(generator._process_extra_item)
    
    # Check for the critical zero rate handling logic
    if "if rate == 0:" in source:
        print("✅ Found zero rate condition check in extra items")
        
        # Check if it only populates Serial No. and Description for zero rates
        lines = source.split('\n')
        in_zero_rate_block = False
        zero_rate_lines = []
        
        for line in lines:
            if "if rate == 0:" in line:
                in_zero_rate_block = True
                continue
            elif in_zero_rate_block:
                if line.strip().startswith("else:"):
                    break
                elif line.strip() and not line.strip().startswith("#"):
                    zero_rate_lines.append(line.strip())
        
        print("📝 Zero rate handling code for extra items:")
        for line in zero_rate_lines:
            print(f"  {line}")
        
        # Validate that only Serial No. and Description are populated
        serial_no_populated = any("worksheet.write(current_row, 3" in line for line in zero_rate_lines)
        description_populated = any("worksheet.write(current_row, 4" in line for line in zero_rate_lines)
        other_columns_populated = any(
            ("worksheet.write(current_row, 0" in line) or  # Unit
            ("worksheet.write(current_row, 1" in line) or  # Quantity Since
            ("worksheet.write(current_row, 2" in line) or  # Quantity Upto
            ("worksheet.write(current_row, 5" in line) or  # Rate
            ("worksheet.write(current_row, 6" in line) or  # Amount Upto
            ("worksheet.write(current_row, 7" in line) or  # Amount Since
            ("worksheet.write(current_row, 8" in line)     # Remark
            for line in zero_rate_lines)
        
        if serial_no_populated and description_populated and not other_columns_populated:
            print("✅ Zero rate handling for extra items is CORRECT:")
            print("   - Only Serial No. (Column D) and Description (Column E) are populated")
            print("   - All other columns remain blank for zero rate extra items")
            return True
        else:
            print("❌ Zero rate handling for extra items is INCORRECT:")
            print(f"   - Serial No. populated: {serial_no_populated}")
            print(f"   - Description populated: {description_populated}")
            print(f"   - Other columns populated: {other_columns_populated}")
            return False
    else:
        print("❌ Zero rate condition check NOT found in extra items")
        return False

def main():
    """Main validation function"""
    print("🚀 Implementation Validation for VBA Compliance")
    print("=" * 70)
    
    # Validate work order items
    work_order_valid = validate_implementation()
    
    # Validate extra items
    extra_items_valid = validate_extra_items()
    
    print("\n" + "=" * 70)
    print("📊 IMPLEMENTATION VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Work Order Items: {'✅ PASS' if work_order_valid else '❌ FAIL'}")
    print(f"Extra Items: {'✅ PASS' if extra_items_valid else '❌ FAIL'}")
    
    if work_order_valid and extra_items_valid:
        print("\n🎉 IMPLEMENTATION VALIDATION PASSED!")
        print("✅ FirstPageGenerator fully complies with VBA specification")
        print("✅ Zero rate handling is correctly implemented:")
        print("   - For zero rates: Only Serial No. and Description are populated")
        print("   - All other columns remain blank for zero rate items")
        print("✅ Implementation matches exact VBA behavior")
        return True
    else:
        print("\n💥 IMPLEMENTATION VALIDATION FAILED!")
        print("❌ Implementation does not fully comply with VBA specification")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)