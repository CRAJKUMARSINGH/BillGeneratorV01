#!/usr/bin/env python3
"""
Asset-based Test Runner for BillGenerator
Tests all Excel files in the test_input_files directory programmatically
"""

import os
import sys
import time
import traceback
import pandas as pd
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_excel_file(file_path):
    """Test processing of a specific Excel file"""
    try:
        from utils.excel_processor import ExcelProcessor
        from utils.document_generator import DocumentGenerator
        
        print(f"📄 Testing: {os.path.basename(file_path)}")
        
        # Test Excel processing
        start_time = time.time()
        processor = ExcelProcessor(file_path)
        result = processor.process_excel()
        processing_time = time.time() - start_time
        
        # Validate basic structure
        required_keys = ['title_data', 'work_order_data', 'bill_quantity_data', 'extra_items_data']
        for key in required_keys:
            if key not in result:
                raise ValueError(f"Missing required key: {key}")
        
        # Test document generation
        start_time = time.time()
        generator = DocumentGenerator(result)
        documents = generator.generate_all_documents()
        doc_gen_time = time.time() - start_time
        
        # Validate documents
        expected_docs = [
            'First Page Summary',
            'Deviation Statement', 
            'Final Bill Scrutiny Sheet',
            'Extra Items Statement',
            'Certificate II',
            'Certificate III'
        ]
        
        generated_docs = []
        for doc_name in expected_docs:
            if doc_name in documents and len(documents[doc_name]) > 0:
                generated_docs.append(doc_name)
        
        # Count data rows
        work_order_rows = len(result['work_order_data']) if isinstance(result['work_order_data'], pd.DataFrame) else 0
        bill_quantity_rows = len(result['bill_quantity_data']) if isinstance(result['bill_quantity_data'], pd.DataFrame) else 0
        extra_items_rows = len(result['extra_items_data']) if isinstance(result['extra_items_data'], pd.DataFrame) else 0
        
        return {
            'success': True,
            'file_name': os.path.basename(file_path),
            'processing_time': processing_time,
            'doc_gen_time': doc_gen_time,
            'total_time': processing_time + doc_gen_time,
            'work_order_rows': work_order_rows,
            'bill_quantity_rows': bill_quantity_rows,
            'extra_items_rows': extra_items_rows,
            'documents_generated': len(generated_docs),
            'expected_documents': len(expected_docs),
            'generated_docs': generated_docs,
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'file_name': os.path.basename(file_path),
            'processing_time': 0,
            'doc_gen_time': 0,
            'total_time': 0,
            'work_order_rows': 0,
            'bill_quantity_rows': 0,
            'extra_items_rows': 0,
            'documents_generated': 0,
            'expected_documents': 6,
            'generated_docs': [],
            'error': str(e)
        }

def run_asset_tests():
    """Run tests on all Excel files in test_input_files directory"""
    print("🚀 Starting Asset-based Test Suite for BillGenerator")
    print("=" * 80)
    
    test_dir = "test_input_files"
    if not os.path.exists(test_dir):
        print(f"❌ Test directory '{test_dir}' not found!")
        return False
    
    # Get all Excel files
    excel_files = []
    for file in os.listdir(test_dir):
        if file.lower().endswith(('.xlsx', '.xls')):
            excel_files.append(os.path.join(test_dir, file))
    
    if not excel_files:
        print(f"❌ No Excel files found in '{test_dir}'!")
        return False
    
    print(f"📁 Found {len(excel_files)} Excel files to test")
    print("-" * 80)
    
    results = []
    total_start_time = time.time()
    
    # Test each file
    for i, file_path in enumerate(excel_files, 1):
        print(f"\n[{i}/{len(excel_files)}] Testing: {os.path.basename(file_path)}")
        print("-" * 50)
        
        try:
            result = test_excel_file(file_path)
            results.append(result)
            
            if result['success']:
                print(f"✅ SUCCESS - Processed in {result['total_time']:.2f}s")
                print(f"   📊 Data: {result['work_order_rows']} WO, {result['bill_quantity_rows']} BQ, {result['extra_items_rows']} EI rows")
                print(f"   📄 Documents: {result['documents_generated']}/{result['expected_documents']} generated")
            else:
                print(f"❌ FAILED - {result['error']}")
                
        except Exception as e:
            print(f"❌ CRITICAL ERROR: {e}")
            results.append({
                'success': False,
                'file_name': os.path.basename(file_path),
                'error': f"Critical error: {e}",
                'processing_time': 0,
                'doc_gen_time': 0,
                'total_time': 0,
                'work_order_rows': 0,
                'bill_quantity_rows': 0,
                'extra_items_rows': 0,
                'documents_generated': 0,
                'expected_documents': 6,
                'generated_docs': []
            })
    
    total_time = time.time() - total_start_time
    
    # Generate comprehensive report
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE ASSET TEST REPORT")
    print("=" * 80)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"📁 Total Files Tested: {len(results)}")
    print(f"✅ Successful: {len(successful_tests)}")
    print(f"❌ Failed: {len(failed_tests)}")
    print(f"📈 Success Rate: {(len(successful_tests) / len(results)) * 100:.1f}%")
    print(f"⏱️  Total Time: {total_time:.2f} seconds")
    
    if successful_tests:
        avg_processing_time = sum(r['processing_time'] for r in successful_tests) / len(successful_tests)
        avg_doc_gen_time = sum(r['doc_gen_time'] for r in successful_tests) / len(successful_tests)
        total_rows_processed = sum(r['work_order_rows'] + r['bill_quantity_rows'] + r['extra_items_rows'] for r in successful_tests)
        
        print(f"⚡ Avg Processing Time: {avg_processing_time:.2f}s")
        print(f"📄 Avg Doc Generation Time: {avg_doc_gen_time:.2f}s")
        print(f"📊 Total Rows Processed: {total_rows_processed}")
    
    # Detailed results
    print("\n📋 DETAILED RESULTS:")
    print("-" * 80)
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['file_name']}")
        
        if result['success']:
            print(f"    ⏱️  Time: {result['total_time']:.2f}s")
            print(f"    📊 Rows: WO({result['work_order_rows']}) BQ({result['bill_quantity_rows']}) EI({result['extra_items_rows']})")
            print(f"    📄 Docs: {result['documents_generated']}/{result['expected_documents']}")
        else:
            print(f"    ❌ Error: {result['error']}")
    
    # File type analysis
    print("\n📈 FILE TYPE ANALYSIS:")
    print("-" * 80)
    
    file_types = {}
    for result in results:
        file_name = result['file_name'].lower()
        if 'final' in file_name and 'extra' in file_name:
            file_type = "Final with Extra Items"
        elif 'final' in file_name:
            file_type = "Final Bills"
        elif 'running' in file_name:
            file_type = "Running Bills"
        else:
            file_type = "Other"
        
        if file_type not in file_types:
            file_types[file_type] = {'total': 0, 'success': 0}
        
        file_types[file_type]['total'] += 1
        if result['success']:
            file_types[file_type]['success'] += 1
    
    for file_type, stats in file_types.items():
        success_rate = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
        print(f"  📁 {file_type}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
    
    # Performance insights
    if successful_tests:
        print("\n⚡ PERFORMANCE INSIGHTS:")
        print("-" * 80)
        
        fastest = min(successful_tests, key=lambda x: x['total_time'])
        slowest = max(successful_tests, key=lambda x: x['total_time'])
        
        print(f"🚀 Fastest: {fastest['file_name']} ({fastest['total_time']:.2f}s)")
        print(f"🐌 Slowest: {slowest['file_name']} ({slowest['total_time']:.2f}s)")
        
        largest_dataset = max(successful_tests, key=lambda x: x['work_order_rows'] + x['bill_quantity_rows'] + x['extra_items_rows'])
        print(f"📊 Largest Dataset: {largest_dataset['file_name']} ({largest_dataset['work_order_rows'] + largest_dataset['bill_quantity_rows'] + largest_dataset['extra_items_rows']} rows)")
    
    # Summary
    print(f"\n🎯 SUMMARY:")
    print("-" * 80)
    
    if len(successful_tests) == len(results):
        print("🎉 ALL TESTS PASSED! All Excel assets processed successfully!")
        print("✅ Bill Generator is fully operational with all test assets!")
    elif len(successful_tests) >= len(results) * 0.8:
        print("⚠️  Most tests passed. Minor issues with some files.")
        print("🔧 Review failed files for potential data format issues.")
    else:
        print("❌ Multiple test failures detected.")
        print("🚨 Significant issues need to be addressed.")
    
    print(f"\n📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return len(successful_tests) == len(results)

if __name__ == "__main__":
    success = run_asset_tests()
    sys.exit(0 if success else 1)
