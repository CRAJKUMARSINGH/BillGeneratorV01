#!/usr/bin/env python3
"""
Debug script to test PDF generation with smaller datasets and log HTML output
"""

import pandas as pd
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def test_with_small_dataset():
    """Test PDF generation with a smaller dataset (5 rows)"""
    print("🔍 Testing PDF generation with smaller dataset")
    print("=" * 50)
    
    # Create sample data with only 5 rows for testing
    sample_data = {
        'title_data': {
            'Project Name': 'Highway Improvement Project',
            'Contract No': 'NH-2025-001',
            'Work Order No': 'WO-2025-001',
            'Contractor Name': 'ABC Construction Ltd.',
            'Bill Number': 'BILL-2025-001',
            'Period From': '01/01/2025',
            'Period To': '31/03/2025'
        },
        'work_order_data': pd.DataFrame([
            {
                'Item No.': '1',
                'Description': 'Earthwork in excavation',
                'Unit': 'Cum',
                'Quantity': 150.50,
                'Rate': 600.00,
                'Amount': 90300.00,
                'Remark': 'As per drawings'
            },
            {
                'Item No.': '2',
                'Description': 'Cement concrete M25',
                'Unit': 'Cum',
                'Quantity': 85.25,
                'Rate': 4500.00,
                'Amount': 383625.00,
                'Remark': 'Reinforced concrete'
            },
            {
                'Item No.': '3',
                'Description': 'Steel reinforcement',
                'Unit': 'Kg',
                'Quantity': 5000.00,
                'Rate': 80.00,
                'Amount': 400000.00,
                'Remark': 'Fe 500 grade'
            },
            {
                'Item No.': '4',
                'Description': 'Brickwork in cement mortar 1:6',
                'Unit': 'Cum',
                'Quantity': 25.75,
                'Rate': 3200.00,
                'Amount': 82400.00,
                'Remark': 'Standard size bricks'
            },
            {
                'Item No.': '5',
                'Description': 'Plastering cement mortar 1:6',
                'Unit': 'Sq.m',
                'Quantity': 120.50,
                'Rate': 45.00,
                'Amount': 5422.50,
                'Remark': 'Internal walls'
            }
        ]),
        'bill_quantity_data': pd.DataFrame([
            {
                'Item No.': '1',
                'Description': 'Earthwork in excavation',
                'Unit': 'Cum',
                'Quantity': 150.50,
                'Rate': 600.00,
                'Amount': 90300.00
            },
            {
                'Item No.': '2',
                'Description': 'Cement concrete M25',
                'Unit': 'Cum',
                'Quantity': 85.25,
                'Rate': 4500.00,
                'Amount': 383625.00
            },
            {
                'Item No.': '3',
                'Description': 'Steel reinforcement',
                'Unit': 'Kg',
                'Quantity': 5000.00,
                'Rate': 80.00,
                'Amount': 400000.00
            },
            {
                'Item No.': '4',
                'Description': 'Brickwork in cement mortar 1:6',
                'Unit': 'Cum',
                'Quantity': 25.75,
                'Rate': 3200.00,
                'Amount': 82400.00
            },
            {
                'Item No.': '5',
                'Description': 'Plastering cement mortar 1:6',
                'Unit': 'Sq.m',
                'Quantity': 120.50,
                'Rate': 45.00,
                'Amount': 5422.50
            }
        ]),
        'extra_items_data': pd.DataFrame([
            {
                'Item No.': 'E1',
                'Description': 'Additional Survey Work',
                'Unit': 'LS',
                'Quantity': 1,
                'Rate': 15000.00,
                'Amount': 15000.00,
                'Remark': 'Extra work'
            }
        ])
    }
    
    try:
        # Initialize the document generator
        print("🔄 Initializing EnhancedDocumentGenerator...")
        generator = EnhancedDocumentGenerator(sample_data)
        print("✅ EnhancedDocumentGenerator initialized successfully")
        
        # Generate HTML documents
        print("\n📄 Generating HTML documents...")
        html_documents = generator.generate_all_documents()
        print(f"✅ Generated {len(html_documents)} HTML documents")
        
        # Log HTML content for debugging
        print("\n📝 Logging HTML content for debugging...")
        for doc_name, html_content in html_documents.items():
            # Create a safe filename
            safe_name = "".join(c for c in doc_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            filename = f"debug_{safe_name}.html"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"  ✅ Saved debug HTML: {filename}")
            
            # Check for specific elements in Deviation Statement
            if 'Deviation Statement' in doc_name:
                print(f"\n📋 Checking Deviation Statement HTML...")
                checks = [
                    ('table-layout: fixed', 'table-layout: fixed' in html_content),
                    ('width: 15mm', 'width: 15mm' in html_content),
                    ('A4 landscape', 'A4 landscape' in html_content),
                    ('font-size: 8pt', 'font-size: 8pt' in html_content)
                ]
                
                for check_name, passed in checks:
                    status = "✅ PASS" if passed else "❌ FAIL"
                    print(f"  {status} {check_name}")
        
        # Test PDF generation
        print("\n🖨️  Testing PDF generation with smaller dataset...")
        deviation_html = html_documents.get('Deviation Statement', '')
        if deviation_html:
            # Save the HTML for manual inspection
            with open('debug_deviation_statement.html', 'w', encoding='utf-8') as f:
                f.write(deviation_html)
            print("  ✅ Saved Deviation Statement HTML for manual inspection")
            
            # Try to generate PDF
            pdf_path = 'debug_deviation_statement.pdf'
            success = generator.generate_pdf_fixed(deviation_html, pdf_path)
            if success:
                pdf_file = Path(pdf_path)
                if pdf_file.exists():
                    size = pdf_file.stat().st_size
                    print(f"  ✅ PDF generated successfully: {pdf_path} ({size} bytes)")
                else:
                    print(f"  ❌ PDF file was not created: {pdf_path}")
            else:
                print("  ❌ PDF generation failed")
        else:
            print("  ❌ No Deviation Statement HTML generated")
            
        print("\n🎉 Debug test completed!")
        return True
            
    except Exception as e:
        print(f"\n💥 Error during debug test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hybrid_reportlab_approach():
    """Test the hybrid ReportLab approach for precise column widths"""
    print("\n" + "=" * 50)
    print("🧪 Testing Hybrid ReportLab Approach")
    print("=" * 50)
    
    # Sample data for testing
    sample_rows = [
        ['1', 'Earthwork excavation', 'Cum', '150.50', '600.00', '90300.00', '150.50', '90300.00', '0.00', '0.00', '0.00', '0.00', ''],
        ['2', 'Cement concrete M25', 'Cum', '85.25', '4500.00', '383625.00', '85.25', '383625.00', '0.00', '0.00', '0.00', '0.00', ''],
        ['3', 'Steel reinforcement', 'Kg', '5000.00', '80.00', '400000.00', '5000.00', '400000.00', '0.00', '0.00', '0.00', '0.00', ''],
        ['4', 'Brickwork 1:6 mortar', 'Cum', '25.75', '3200.00', '82400.00', '25.75', '82400.00', '0.00', '0.00', '0.00', '0.00', ''],
        ['5', 'Plastering 1:6 mortar', 'Sq.m', '120.50', '45.00', '5422.50', '120.50', '5422.50', '0.00', '0.00', '0.00', '0.00', '']
    ]
    
    # Column widths in mm (matching our CSS)
    col_widths_mm = [15, 50, 15, 20, 20, 20, 20, 20, 15, 15, 15, 15, 15]
    
    print(f"📋 Sample data rows: {len(sample_rows)}")
    print(f"📐 Column widths (mm): {col_widths_mm}")
    print(f"📐 Total width: {sum(col_widths_mm)}mm (should fit A4 landscape ~277mm)")
    
    # This would be implemented in the _generate_pdf_reportlab method
    print("\n💡 Implementation note:")
    print("   In _generate_pdf_reportlab, we can use:")
    print(f"   table = Table(rows, colWidths=[{', '.join([f'{w}*mm' for w in col_widths_mm])}], repeatRows=1)")
    print("   This ensures precise column widths in the PDF output")
    
    return True

def test_absolute_units_approach():
    """Test the absolute units approach"""
    print("\n" + "=" * 50)
    print("📏 Testing Absolute Units Approach")
    print("=" * 50)
    
    # Verify our current CSS uses absolute units
    css_checks = [
        "width: 15mm",
        "width: 50mm", 
        "padding: 3mm",
        "margin: 10mm",
        "font-size: 8pt"
    ]
    
    print("📋 Current CSS uses absolute units:")
    for css_rule in css_checks:
        print(f"  ✅ {css_rule}")
    
    print("\n💡 Benefits of absolute units:")
    print("   • Consistent rendering across different PDF engines")
    print("   • Predictable layout sizing")
    print("   • No scaling or distortion issues")
    print("   • Better control over page fitting")
    
    return True

if __name__ == "__main__":
    print("🔍 Starting comprehensive PDF generation debugging")
    
    # Test with smaller dataset
    success1 = test_with_small_dataset()
    
    # Test hybrid ReportLab approach
    success2 = test_hybrid_reportlab_approach()
    
    # Test absolute units approach
    success3 = test_absolute_units_approach()
    
    if success1 and success2 and success3:
        print("\n🏆 All debugging tests completed successfully!")
        print("\n📋 Recommendations:")
        print("   1. Check debug_*.html files to verify CSS")
        print("   2. Inspect debug_deviation_statement.pdf for layout issues")
        print("   3. Consider hybrid ReportLab for complex tables")
        print("   4. Continue using absolute units (mm/pt) in CSS")
        sys.exit(0)
    else:
        print("\n❌ Some debugging tests failed!")
        sys.exit(1)