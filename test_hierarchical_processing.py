#!/usr/bin/env python3
"""
Test script for hierarchical Excel processing
Tests the app's ability to handle complex nested item structures
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

def test_hierarchical_excel_processing():
    """Test Excel processing with hierarchical structure"""
    print("🧪 Testing Hierarchical Excel Processing")
    print("=" * 50)
    
    # Test file path
    test_file = "test_input_files/hierarchical_test_structure.xlsx"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        # Process Excel file
        print(f"📁 Processing: {test_file}")
        processor = ExcelProcessor(test_file)
        result = processor.process_excel()
        
        if not result:
            print("❌ Excel processing failed")
            return False
        
        print("✅ Excel processing successful!")
        
        # Validate structure
        print("\n📊 Data Structure Validation:")
        
        # Title data
        title_data = result.get('title_data', {})
        print(f"  📄 Title fields: {len(title_data)}")
        print(f"  📄 Project: {title_data.get('Name of Work ;-', 'N/A')}")
        
        # Work order data
        work_order_data = result.get('work_order_data')
        if isinstance(work_order_data, pd.DataFrame):
            print(f"  📋 Work Order items: {len(work_order_data)}")
            print(f"  📋 Columns: {list(work_order_data.columns)}")
            
            # Check for hierarchical structure
            item_nos = work_order_data['Item No.'].tolist() if 'Item No.' in work_order_data.columns else []
            print(f"  📋 Item numbers: {item_nos[:5]}... (showing first 5)")
            
            # Check rate distribution
            rates = work_order_data['Rate'].tolist() if 'Rate' in work_order_data.columns else []
            zero_rates = [r for r in rates if r == 0.0]
            non_zero_rates = [r for r in rates if r > 0.0]
            print(f"  📋 Zero rate items: {len(zero_rates)}")
            print(f"  📋 Non-zero rate items: {len(non_zero_rates)}")
            
            # Check for blank/NaN values
            blank_units = work_order_data['Unit'].isna().sum() if 'Unit' in work_order_data.columns else 0
            blank_descriptions = work_order_data['Description'].isna().sum() if 'Description' in work_order_data.columns else 0
            print(f"  📋 Blank units: {blank_units}")
            print(f"  📋 Blank descriptions: {blank_descriptions}")
        
        # Bill quantity data
        bill_quantity_data = result.get('bill_quantity_data')
        if isinstance(bill_quantity_data, pd.DataFrame):
            print(f"  💰 Bill items: {len(bill_quantity_data)}")
        
        # Extra items data
        extra_items_data = result.get('extra_items_data')
        if isinstance(extra_items_data, pd.DataFrame):
            print(f"  ➕ Extra items: {len(extra_items_data)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing Excel: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_document_generation():
    """Test document generation with hierarchical data"""
    print("\n🧪 Testing Document Generation")
    print("=" * 50)
    
    try:
        # Process Excel file first
        test_file = "test_input_files/hierarchical_test_structure.xlsx"
        processor = ExcelProcessor(test_file)
        result = processor.process_excel()
        
        if not result:
            print("❌ Excel processing failed")
            return False
        
        # Generate documents
        print("📄 Generating documents...")
        doc_generator = EnhancedDocumentGenerator(result)
        html_documents = doc_generator.generate_all_documents()
        
        if not html_documents:
            print("❌ HTML generation failed")
            return False
        
        print(f"✅ Generated {len(html_documents)} HTML documents:")
        for doc_name in html_documents.keys():
            print(f"  📄 {doc_name}")
        
        # Test PDF generation
        print("\n🔄 Testing PDF generation...")
        pdf_documents = doc_generator.create_pdf_documents(html_documents)
        
        if not pdf_documents:
            print("❌ PDF generation failed")
            return False
        
        print(f"✅ Generated {len(pdf_documents)} PDF documents:")
        for pdf_name in pdf_documents.keys():
            pdf_size = len(pdf_documents[pdf_name])
            print(f"  📄 {pdf_name} ({pdf_size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating documents: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_blank_handling():
    """Test blank/NaN handling in hierarchical structure"""
    print("\n🧪 Testing Blank/NaN Handling")
    print("=" * 50)
    
    try:
        # Process Excel file
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
        
        print("🔍 Checking blank/NaN handling:")
        
        # Check units
        unit_col = work_order_data['Unit'] if 'Unit' in work_order_data.columns else pd.Series()
        blank_units = unit_col.isna().sum()
        empty_units = (unit_col == '').sum()
        print(f"  📋 Blank units (NaN): {blank_units}")
        print(f"  📋 Empty units (''): {empty_units}")
        
        # Check descriptions
        desc_col = work_order_data['Description'] if 'Description' in work_order_data.columns else pd.Series()
        blank_descriptions = desc_col.isna().sum()
        empty_descriptions = (desc_col == '').sum()
        print(f"  📋 Blank descriptions (NaN): {blank_descriptions}")
        print(f"  📋 Empty descriptions (''): {empty_descriptions}")
        
        # Check rates
        rate_col = work_order_data['Rate'] if 'Rate' in work_order_data.columns else pd.Series()
        zero_rates = (rate_col == 0.0).sum()
        print(f"  📋 Zero rates: {zero_rates}")
        
        # Check quantities
        qty_col = work_order_data['Quantity Since'] if 'Quantity Since' in work_order_data.columns else pd.Series()
        zero_quantities = (qty_col == 0.0).sum()
        print(f"  📋 Zero quantities: {zero_quantities}")
        
        print("✅ Blank/NaN handling validation complete")
        return True
        
    except Exception as e:
        print(f"❌ Error testing blank handling: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all hierarchical tests"""
    print("🚀 Starting Hierarchical Test Suite")
    print("=" * 60)
    
    tests = [
        ("Excel Processing", test_hierarchical_excel_processing),
        ("Document Generation", test_document_generation),
        ("Blank/NaN Handling", test_blank_handling)
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
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! App is robust for hierarchical structures.")
    else:
        print("⚠️ Some tests failed. Review and fix issues.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
