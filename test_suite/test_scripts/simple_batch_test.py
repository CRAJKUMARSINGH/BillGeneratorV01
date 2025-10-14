#!/usr/bin/env python3
"""
Simple Batch Performance Test for Bill Generator V01
Tests response time with three batch runs
"""

import time
import os
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def create_test_data(batch_size=5):
    """Create test data for batch processing"""
    # Ensure all arrays have the same length
    units = ['Cum', 'Sqm', 'Kg', 'Nos', 'Mtr', 'Ltr', 'Ton', 'Pcs']
    remarks = ['Completed', 'In Progress', 'Pending', 'Approved', 'Rejected', 'Under Review', 'Draft', 'Final']
    
    test_data = {
        'title_data': {
            'work_order_no': f'WO/2025/BATCH/{batch_size}',
            'contractor_name': 'RAJKUMAR SINGH CHAUHAN',
            'project_title': f'Batch Test Project - {batch_size} items',
            'location': 'Test Location, City',
            'date': datetime.now().strftime('%d-%m-%Y'),
            'client_name': 'Government Department',
            'client_address': 'Government Office, City'
        },
        'work_order_data': pd.DataFrame({
            'S. No.': list(range(1, batch_size + 1)),
            'Description': [f'Test work item {i}' for i in range(1, batch_size + 1)],
            'Unit': [units[i % len(units)] for i in range(batch_size)],
            'Quantity Since': [10.5 + i for i in range(batch_size)],
            'Quantity Upto': [12.0 + i for i in range(batch_size)],
            'Rate': [500.0 + (i * 100) for i in range(batch_size)],
            'Amount Upto': [6000.0 + (i * 1000) for i in range(batch_size)],
            'Amount Since': [5250.0 + (i * 900) for i in range(batch_size)],
            'Remarks': [remarks[i % len(remarks)] for i in range(batch_size)]
        }),
        'bill_quantity_data': pd.DataFrame({
            'S. No.': list(range(1, batch_size + 1)),
            'Description': [f'Test work item {i}' for i in range(1, batch_size + 1)],
            'Unit': [units[i % len(units)] for i in range(batch_size)],
            'Quantity Since': [10.5 + i for i in range(batch_size)],
            'Quantity Upto': [12.0 + i for i in range(batch_size)],
            'Rate': [500.0 + (i * 100) for i in range(batch_size)],
            'Amount Upto': [6000.0 + (i * 1000) for i in range(batch_size)],
            'Amount Since': [5250.0 + (i * 900) for i in range(batch_size)],
            'Remarks': [remarks[i % len(remarks)] for i in range(batch_size)]
        }),
        'extra_items_data': pd.DataFrame({
            'S. No.': list(range(1, min(3, batch_size) + 1)),
            'Description': [f'Extra work item {i}' for i in range(1, min(3, batch_size) + 1)],
            'Unit': [units[i % len(units)] for i in range(min(3, batch_size))],
            'Quantity': [2.0 + i for i in range(min(3, batch_size))],
            'Rate': [600.0 + (i * 50) for i in range(min(3, batch_size))],
            'Amount': [1200.0 + (i * 200) for i in range(min(3, batch_size))],
            'Remarks': ['Extra work'] * min(3, batch_size)
        })
    }
    return test_data

def run_single_batch(batch_number, batch_size):
    """Run a single batch test"""
    print(f"Starting Batch {batch_number} (Size: {batch_size} items)")
    start_time = time.time()
    
    # Create test data
    test_data = create_test_data(batch_size)
    
    # Create output folder
    output_dir = Path("outputs") / datetime.now().strftime("%Y-%m-%d")
    output_dir.mkdir(parents=True, exist_ok=True)
    batch_folder = output_dir / f"batch_test_{batch_number}_size_{batch_size}"
    batch_folder.mkdir(exist_ok=True)
    (batch_folder / "pdf").mkdir(exist_ok=True)
    (batch_folder / "html").mkdir(exist_ok=True)
    
    # Initialize generator
    generator = EnhancedDocumentGenerator(test_data)
    
    # Test all templates
    templates = ['first_page', 'extra_items', 'deviation_statement', 
                'certificate_ii', 'certificate_iii', 'note_sheet']
    
    successful_templates = 0
    template_times = {}
    
    for template in templates:
        template_start = time.time()
        
        try:
            # Generate HTML
            if template == 'first_page':
                html_content = generator._generate_first_page()
            elif template == 'extra_items':
                html_content = generator._generate_extra_items_statement()
            elif template == 'deviation_statement':
                html_content = generator._generate_deviation_statement()
            elif template == 'certificate_ii':
                html_content = generator._generate_certificate_ii()
            elif template == 'certificate_iii':
                html_content = generator._generate_certificate_iii()
            elif template == 'note_sheet':
                html_content = generator._generate_final_bill_scrutiny()
            
            if html_content:
                # Save HTML
                html_file = batch_folder / "html" / f"{template}.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Generate PDF
                pdf_file = batch_folder / "pdf" / f"{template}.pdf"
                
                if generator.generate_pdf_fixed(html_content, str(pdf_file)):
                    successful_templates += 1
                    print(f"  SUCCESS: {template} - HTML + PDF generated")
                else:
                    print(f"  PARTIAL: {template} - HTML generated, PDF failed")
            else:
                print(f"  FAILED: {template} - HTML generation failed")
                
        except Exception as e:
            print(f"  ERROR: {template} - {e}")
        
        template_end = time.time()
        template_times[template] = template_end - template_start
    
    total_time = time.time() - start_time
    success_rate = (successful_templates / len(templates)) * 100
    
    print(f"Batch {batch_number} completed in {total_time:.2f} seconds")
    print(f"Success rate: {success_rate:.1f}% ({successful_templates}/{len(templates)})")
    print(f"Output folder: {batch_folder}")
    print("-" * 50)
    
    return {
        'batch_number': batch_number,
        'batch_size': batch_size,
        'total_time': total_time,
        'successful_templates': successful_templates,
        'total_templates': len(templates),
        'success_rate': success_rate,
        'template_times': template_times,
        'output_folder': str(batch_folder)
    }

def main():
    """Run three batch tests"""
    print("=" * 60)
    print("BILL GENERATOR V01 - BATCH PERFORMANCE TEST")
    print("=" * 60)
    
    batch_configs = [
        {'batch_number': 1, 'batch_size': 3},   # Small batch
        {'batch_number': 2, 'batch_size': 5},   # Medium batch  
        {'batch_number': 3, 'batch_size': 8}    # Large batch
    ]
    
    results = []
    
    for config in batch_configs:
        result = run_single_batch(**config)
        results.append(result)
    
    # Calculate overall statistics
    total_time = sum(r['total_time'] for r in results)
    avg_time = total_time / len(results)
    avg_success_rate = sum(r['success_rate'] for r in results) / len(results)
    
    # Find fastest and slowest
    fastest = min(results, key=lambda x: x['total_time'])
    slowest = max(results, key=lambda x: x['total_time'])
    
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"Total Execution Time: {total_time:.2f} seconds")
    print(f"Average Batch Time: {avg_time:.2f} seconds")
    print(f"Average Success Rate: {avg_success_rate:.1f}%")
    print(f"Fastest Batch: Batch {fastest['batch_number']} ({fastest['total_time']:.2f}s)")
    print(f"Slowest Batch: Batch {slowest['batch_number']} ({slowest['total_time']:.2f}s)")
    
    print("\nDETAILED RESULTS:")
    for result in results:
        print(f"Batch {result['batch_number']} ({result['batch_size']} items): {result['total_time']:.2f}s - {result['success_rate']:.1f}% success")
    
    # Performance assessment
    print("\n" + "=" * 60)
    print("PERFORMANCE ASSESSMENT")
    print("=" * 60)
    
    if avg_success_rate >= 95:
        print("SUCCESS RATE: EXCELLENT (95%+)")
    elif avg_success_rate >= 90:
        print("SUCCESS RATE: GOOD (90-94%)")
    else:
        print("SUCCESS RATE: NEEDS IMPROVEMENT (<90%)")
    
    if avg_time <= 5:
        print("RESPONSE TIME: EXCELLENT (≤5s per batch)")
    elif avg_time <= 10:
        print("RESPONSE TIME: GOOD (5-10s per batch)")
    else:
        print("RESPONSE TIME: ACCEPTABLE (>10s per batch)")
    
    # Scalability analysis
    time_per_item = avg_time / sum(r['batch_size'] for r in results) * len(results)
    print(f"TIME PER ITEM: {time_per_item:.2f} seconds")
    
    if time_per_item <= 1:
        print("SCALABILITY: EXCELLENT (≤1s per item)")
    elif time_per_item <= 2:
        print("SCALABILITY: GOOD (1-2s per item)")
    else:
        print("SCALABILITY: ACCEPTABLE (>2s per item)")
    
    print("\n" + "=" * 60)
    if avg_success_rate >= 95 and avg_time <= 10:
        print("OVERALL STATUS: SATISFACTORY - READY FOR PRODUCTION")
    else:
        print("OVERALL STATUS: NEEDS OPTIMIZATION")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    main()
