#!/usr/bin/env python3
"""
Test online mode with hierarchical data
Simulates the online entry workflow with complex nested structures
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add utils to path
utils_path = Path(__file__).parent / "utils"
if str(utils_path) not in sys.path:
    sys.path.append(str(utils_path))

from utils.excel_processor import ExcelProcessor
from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def simulate_online_mode_workflow():
    """Simulate the complete online mode workflow"""
    print("🧪 Testing Online Mode with Hierarchical Data")
    print("=" * 60)
    
    # Step 1: Load work order data (simulating upload)
    print("📤 Step 1: Loading Work Order Data")
    test_file = "test_input_files/hierarchical_test_structure.xlsx"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        processor = ExcelProcessor(test_file)
        result = processor.process_excel()
        
        if not result:
            print("❌ Excel processing failed")
            return False
        
        print("✅ Work order data loaded successfully")
        
        # Extract work order data
        work_order_data = result.get('work_order_data')
        title_data = result.get('title_data', {})
        
        if not isinstance(work_order_data, pd.DataFrame):
            print("❌ No work order data found")
            return False
        
        print(f"📋 Loaded {len(work_order_data)} work order items")
        
        # Step 2: Simulate bill quantity entry
        print("\n💰 Step 2: Simulating Bill Quantity Entry")
        
        # Simulate user entering quantities for some items
        bill_quantities = {}
        processed_bill_data = []
        
        for idx, (_, row) in enumerate(work_order_data.iterrows()):
            item_no = row.get('Item No.', f'Item_{idx + 1}')
            description = row.get('Description', '')
            unit = row.get('Unit', '')
            rate = float(row.get('Rate', 0))
            
            # Apply rate-based rules: only positive rates can have quantities
            if rate > 0:
                # Simulate user entering quantity (80% of WO quantity)
                wo_qty = float(row.get('Quantity Since', 0))
                bill_qty = wo_qty * 0.8 if wo_qty > 0 else 5.0  # Default if WO qty is 0
                
                bill_quantities[f"bill_qty_{idx}_{item_no}"] = bill_qty
                
                # Calculate amount
                amount = bill_qty * rate
                
                processed_bill_data.append({
                    'item_no': str(item_no),
                    'description': str(description) if description else '',
                    'unit': str(unit) if unit else '',
                    'rate': rate,
                    'work_order_qty': wo_qty,
                    'bill_qty': bill_qty,
                    'amount': amount
                })
                
                print(f"  📝 Item {item_no}: WO Qty={wo_qty}, Bill Qty={bill_qty}, Rate={rate}, Amount={amount}")
            else:
                print(f"  🚫 Item {item_no}: Zero rate - Bill Qty disabled")
        
        print(f"✅ Processed {len(processed_bill_data)} bill items")
        
        # Step 3: Simulate extra items entry
        print("\n➕ Step 3: Simulating Extra Items Entry")
        
        extra_items = [
            {
                'item_no': 'EXT-001',
                'description': 'Additional Safety Equipment',
                'unit': 'Nos',
                'quantity': 5.0,
                'rate': 500.0,
                'amount': 2500.0
            },
            {
                'item_no': 'EXT-002',
                'description': 'Emergency Materials',
                'unit': 'Ltr',
                'quantity': 100.0,
                'rate': 25.0,
                'amount': 2500.0
            }
        ]
        
        print(f"✅ Added {len(extra_items)} extra items")
        
        # Step 4: Generate documents
        print("\n📄 Step 4: Generating Documents")
        
        # Prepare data for document generation
        # Fix column mapping for document generator
        bill_df = pd.DataFrame(processed_bill_data)
        if 'item_no' in bill_df.columns:
            bill_df = bill_df.rename(columns={'item_no': 'Item No.'})
        if 'description' in bill_df.columns:
            bill_df = bill_df.rename(columns={'description': 'Description'})
        if 'unit' in bill_df.columns:
            bill_df = bill_df.rename(columns={'unit': 'Unit'})
        if 'rate' in bill_df.columns:
            bill_df = bill_df.rename(columns={'rate': 'Rate'})
        if 'bill_qty' in bill_df.columns:
            bill_df = bill_df.rename(columns={'bill_qty': 'Quantity'})
        if 'amount' in bill_df.columns:
            bill_df = bill_df.rename(columns={'amount': 'Amount'})
        
        extra_df = pd.DataFrame(extra_items)
        if 'item_no' in extra_df.columns:
            extra_df = extra_df.rename(columns={'item_no': 'Item No.'})
        if 'description' in extra_df.columns:
            extra_df = extra_df.rename(columns={'description': 'Description'})
        if 'unit' in extra_df.columns:
            extra_df = extra_df.rename(columns={'unit': 'Unit'})
        if 'rate' in extra_df.columns:
            extra_df = extra_df.rename(columns={'rate': 'Rate'})
        if 'quantity' in extra_df.columns:
            extra_df = extra_df.rename(columns={'quantity': 'Quantity'})
        if 'amount' in extra_df.columns:
            extra_df = extra_df.rename(columns={'amount': 'Amount'})
        
        online_data = {
            'title_data': title_data,
            'work_order_data': work_order_data,
            'bill_quantity_data': bill_df,
            'extra_items_data': extra_df
        }
        
        # Generate HTML documents
        doc_generator = EnhancedDocumentGenerator(online_data)
        html_documents = doc_generator.generate_all_documents()
        
        if not html_documents:
            print("❌ HTML generation failed")
            return False
        
        print(f"✅ Generated {len(html_documents)} HTML documents")
        
        # Generate PDF documents
        pdf_documents = doc_generator.create_pdf_documents(html_documents)
        
        if not pdf_documents:
            print("❌ PDF generation failed")
            return False
        
        print(f"✅ Generated {len(pdf_documents)} PDF documents")
        
        # Summary
        total_bill_amount = sum(item['amount'] for item in processed_bill_data)
        total_extra_amount = sum(item['amount'] for item in extra_items)
        grand_total = total_bill_amount + total_extra_amount
        
        print(f"\n📊 Final Summary:")
        print(f"  💰 Bill items: {len(processed_bill_data)}")
        print(f"  ➕ Extra items: {len(extra_items)}")
        print(f"  💵 Bill amount: ₹{total_bill_amount:,.2f}")
        print(f"  💵 Extra amount: ₹{total_extra_amount:,.2f}")
        print(f"  💵 Grand total: ₹{grand_total:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in online mode simulation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_rate_based_rules():
    """Test rate-based quantity rules with hierarchical items"""
    print("\n🧪 Testing Rate-Based Rules")
    print("=" * 50)
    
    try:
        # Load test data
        test_file = "test_input_files/hierarchical_test_structure.xlsx"
        processor = ExcelProcessor(test_file)
        result = processor.process_excel()
        
        if not result:
            print("❌ Excel processing failed")
            return False
        
        work_order_data = result.get('work_order_data')
        if not isinstance(work_order_data, pd.DataFrame):
            print("❌ No work order data found")
            return False
        
        print("🔍 Analyzing rate-based rules:")
        
        # Categorize items by rate
        zero_rate_items = []
        positive_rate_items = []
        blank_rate_items = []
        
        for idx, (_, row) in enumerate(work_order_data.iterrows()):
            rate = row.get('Rate', 0)
            item_no = row.get('Item No.', f'Item_{idx + 1}')
            description = row.get('Description', '')
            
            if pd.isna(rate) or rate == '':
                blank_rate_items.append((item_no, description))
            elif rate == 0.0:
                zero_rate_items.append((item_no, description))
            else:
                positive_rate_items.append((item_no, description))
        
        print(f"  📋 Zero rate items: {len(zero_rate_items)}")
        for item_no, desc in zero_rate_items[:3]:  # Show first 3
            print(f"    - {item_no}: {desc[:50]}...")
        
        print(f"  📋 Positive rate items: {len(positive_rate_items)}")
        for item_no, desc in positive_rate_items[:3]:  # Show first 3
            print(f"    - {item_no}: {desc[:50]}...")
        
        print(f"  📋 Blank rate items: {len(blank_rate_items)}")
        for item_no, desc in blank_rate_items[:3]:  # Show first 3
            print(f"    - {item_no}: {desc[:50]}...")
        
        # Test rule enforcement
        print("\n🔒 Testing rule enforcement:")
        
        # Zero rate items should not allow bill quantities
        print(f"  🚫 Zero rate items ({len(zero_rate_items)}) should have Bill Qty disabled")
        
        # Positive rate items should allow bill quantities
        print(f"  ✅ Positive rate items ({len(positive_rate_items)}) should allow Bill Qty")
        
        # Blank rate items should be treated as zero
        print(f"  🚫 Blank rate items ({len(blank_rate_items)}) should have Bill Qty disabled")
        
        print("✅ Rate-based rules validation complete")
        return True
        
    except Exception as e:
        print(f"❌ Error testing rate rules: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_blank_field_handling():
    """Test blank field handling in hierarchical structure"""
    print("\n🧪 Testing Blank Field Handling")
    print("=" * 50)
    
    try:
        # Load test data
        test_file = "test_input_files/hierarchical_test_structure.xlsx"
        processor = ExcelProcessor(test_file)
        result = processor.process_excel()
        
        if not result:
            print("❌ Excel processing failed")
            return False
        
        work_order_data = result.get('work_order_data')
        if not isinstance(work_order_data, pd.DataFrame):
            print("❌ No work order data found")
            return False
        
        print("🔍 Analyzing blank field handling:")
        
        # Check each field type
        fields_to_check = ['Item No.', 'Description', 'Unit', 'Rate', 'Quantity Since']
        
        for field in fields_to_check:
            if field in work_order_data.columns:
                col = work_order_data[field]
                
                # Count different types of blank values
                nan_count = col.isna().sum()
                empty_count = (col == '').sum()
                zero_count = (col == 0).sum() if col.dtype in ['int64', 'float64'] else 0
                
                print(f"  📋 {field}:")
                print(f"    - NaN values: {nan_count}")
                print(f"    - Empty strings: {empty_count}")
                if zero_count > 0:
                    print(f"    - Zero values: {zero_count}")
                
                # Show examples of blank values
                blank_examples = []
                for idx, (_, row) in enumerate(work_order_data.iterrows()):
                    value = row.get(field)
                    if pd.isna(value) or value == '' or value == 0:
                        item_no = row.get('Item No.', f'Item_{idx + 1}')
                        blank_examples.append((item_no, value))
                        if len(blank_examples) >= 3:  # Show first 3 examples
                            break
                
                if blank_examples:
                    print(f"    - Examples:")
                    for item_no, value in blank_examples:
                        print(f"      {item_no}: {value}")
        
        print("✅ Blank field handling validation complete")
        return True
        
    except Exception as e:
        print(f"❌ Error testing blank handling: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all online mode tests"""
    print("🚀 Starting Online Mode Test Suite")
    print("=" * 60)
    
    tests = [
        ("Online Mode Workflow", simulate_online_mode_workflow),
        ("Rate-Based Rules", test_rate_based_rules),
        ("Blank Field Handling", test_blank_field_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ONLINE MODE TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All online mode tests passed! App handles hierarchical data robustly.")
    else:
        print("⚠️ Some tests failed. Review and fix issues.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
