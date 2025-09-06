#!/usr/bin/env python3
"""
Comprehensive Test Suite for BillGenerator OPTIMIZED VERSION
Tests all functionality and validates bug fixes
"""

import os
import sys
import time
import pandas as pd
import tempfile
import traceback
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    try:
        import streamlit as st
        import pandas as pd
        import numpy as np
        from utils.excel_processor import ExcelProcessor
        from utils.document_generator import DocumentGenerator
        from utils.pdf_merger import PDFMerger
        from utils.zip_packager import ZipPackager
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_excel_processing():
    """Test Excel file processing functionality"""
    print("🧪 Testing Excel processing...")
    try:
        from utils.excel_processor import ExcelProcessor
        
        # Create a test Excel file
        test_data = {
            'Title': pd.DataFrame({
                'Field': ['Project Name', 'Contract No', 'Work Order No'],
                'Value': ['Test Project', 'TEST-001', 'WO-001']
            }),
            'Work Order': pd.DataFrame({
                'Item No.': [1, 2, 3],
                'Description': ['Item 1', 'Item 2', 'Item 3'],
                'Unit': ['Nos', 'Nos', 'Nos'],
                'Quantity Since': [10, 20, 30],
                'Rate': [100, 200, 300],
                'Amount Since': [1000, 4000, 9000]
            }),
            'Bill Quantity': pd.DataFrame({
                'Item No.': [1, 2, 3],
                'Description': ['Item 1', 'Item 2', 'Item 3'],
                'Unit': ['Nos', 'Nos', 'Nos'],
                'Quantity': [10, 20, 30],
                'Rate': [100, 200, 300],
                'Amount': [1000, 4000, 9000]
            }),
            'Extra Items': pd.DataFrame({
                'Item No.': [1],
                'Description': ['Extra Item'],
                'Unit': ['Nos'],
                'Quantity': [5],
                'Rate': [150],
                'Amount': [750]
            })
        }
        
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            with pd.ExcelWriter(tmp_file.name, engine='openpyxl') as writer:
                for sheet_name, df in test_data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Test processing
            processor = ExcelProcessor(tmp_file.name)
            result = processor.process_excel()
            
            # Validate results
            assert 'title_data' in result
            assert 'work_order_data' in result
            assert 'bill_quantity_data' in result
            assert 'extra_items_data' in result
            
            print("✅ Excel processing successful")
            
            # Clean up
            os.unlink(tmp_file.name)
            return True
            
    except Exception as e:
        print(f"❌ Excel processing error: {e}")
        traceback.print_exc()
        return False

def test_document_generation():
    """Test document generation functionality"""
    print("🧪 Testing document generation...")
    try:
        from utils.document_generator import DocumentGenerator
        
        # Create test data
        test_data = {
            'title_data': {
                'Project Name': 'Test Project',
                'Contract No': 'TEST-001',
                'Work Order No': 'WO-001'
            },
            'work_order_data': pd.DataFrame({
                'Item No.': [1, 2, 3],
                'Description': ['Item 1', 'Item 2', 'Item 3'],
                'Unit': ['Nos', 'Nos', 'Nos'],
                'Quantity Since': [10, 20, 30],
                'Rate': [100, 200, 300],
                'Amount Since': [1000, 4000, 9000]
            }),
            'bill_quantity_data': pd.DataFrame({
                'Item No.': [1, 2, 3],
                'Description': ['Item 1', 'Item 2', 'Item 3'],
                'Unit': ['Nos', 'Nos', 'Nos'],
                'Quantity': [10, 20, 30],
                'Rate': [100, 200, 300],
                'Amount': [1000, 4000, 9000]
            }),
            'extra_items_data': pd.DataFrame({
                'Item No.': [1],
                'Description': ['Extra Item'],
                'Unit': ['Nos'],
                'Quantity': [5],
                'Rate': [150],
                'Amount': [750]
            })
        }
        
        # Test document generation
        generator = DocumentGenerator(test_data)
        documents = generator.generate_all_documents()
        
        # Validate documents
        expected_docs = [
            'First Page Summary',
            'Deviation Statement',
            'Final Bill Scrutiny Sheet',
            'Extra Items Statement',
            'Certificate II',
            'Certificate III'
        ]
        
        for doc_name in expected_docs:
            assert doc_name in documents
            assert len(documents[doc_name]) > 0
        
        print("✅ Document generation successful")
        return True
        
    except Exception as e:
        print(f"❌ Document generation error: {e}")
        traceback.print_exc()
        return False

def test_performance():
    """Test performance metrics"""
    print("🧪 Testing performance...")
    try:
        from utils.document_generator import DocumentGenerator
        
        start_time = time.time()
        
        # Simulate processing
        test_data = {
            'title_data': {'Project Name': 'Test'},
            'work_order_data': pd.DataFrame({'Item': [1, 2, 3]}),
            'bill_quantity_data': pd.DataFrame({'Item': [1, 2, 3]}),
            'extra_items_data': pd.DataFrame()
        }
        
        generator = DocumentGenerator(test_data)
        documents = generator.generate_all_documents()
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Performance should be under 5 seconds for test data
        assert processing_time < 5.0, f"Processing too slow: {processing_time:.2f}s"
        
        print(f"✅ Performance test passed: {processing_time:.2f}s")
        return True
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

def test_memory_usage():
    """Test memory usage optimization"""
    print("🧪 Testing memory usage...")
    try:
        from utils.document_generator import DocumentGenerator
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simulate heavy processing
        test_data = {
            'title_data': {'Project Name': 'Test'},
            'work_order_data': pd.DataFrame({'Item': list(range(100))}),
            'bill_quantity_data': pd.DataFrame({'Item': list(range(100))}),
            'extra_items_data': pd.DataFrame()
        }
        
        generator = DocumentGenerator(test_data)
        documents = generator.generate_all_documents()
        
        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100, f"Memory usage too high: {memory_increase:.2f}MB"
        
        print(f"✅ Memory test passed: {memory_increase:.2f}MB increase")
        return True
        
    except Exception as e:
        print(f"❌ Memory test error: {e}")
        return False

def test_error_handling():
    """Test error handling capabilities"""
    print("🧪 Testing error handling...")
    try:
        from utils.document_generator import DocumentGenerator
        
        # Test with invalid data
        invalid_data = {
            'title_data': {},
            'work_order_data': pd.DataFrame(),
            'bill_quantity_data': pd.DataFrame(),
            'extra_items_data': pd.DataFrame()
        }
        
        generator = DocumentGenerator(invalid_data)
        documents = generator.generate_all_documents()
        
        # Should handle gracefully without crashing
        assert isinstance(documents, dict)
        
        print("✅ Error handling test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test error: {e}")
        return False

def run_comprehensive_tests():
    """Run all tests and generate report"""
    print("🚀 Starting Comprehensive Test Suite for BillGenerator OPTIMIZED VERSION")
    print("=" * 80)
    
    tests = [
        ("Import Test", test_imports),
        ("Excel Processing Test", test_excel_processing),
        ("Document Generation Test", test_document_generation),
        ("Performance Test", test_performance),
        ("Memory Usage Test", test_memory_usage),
        ("Error Handling Test", test_error_handling)
    ]
    
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"❌ {test_name} failed with exception: {e}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Generate report
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("="*80)
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Total Time: {total_time:.2f} seconds")
    
    print("\n📋 Detailed Results:")
    for test_name, result, error in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if error:
            print(f"    Error: {error}")
    
    print("\n🎯 Summary:")
    if success_rate == 100:
        print("🎉 ALL TESTS PASSED! The optimized version is working perfectly!")
        print("✅ Ready for production use!")
    elif success_rate >= 80:
        print("⚠️  Most tests passed. Minor issues detected.")
        print("🔧 Review failed tests and fix issues.")
    else:
        print("❌ Multiple test failures detected.")
        print("🚨 Major issues need to be addressed before production use.")
    
    print(f"\n📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    return success_rate == 100

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
