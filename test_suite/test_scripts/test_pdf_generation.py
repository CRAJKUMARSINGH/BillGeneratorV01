#!/usr/bin/env python3
"""
Test PDF Generation and Check Table Formatting
"""

import pandas as pd
import sys
import os
from datetime import datetime
import tempfile
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.excel_processor import ExcelProcessor
from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def test_pdf_generation():
    """Test PDF generation and examine table formatting"""
    print("🔍 Testing PDF Generation and Table Formatting")
    print("=" * 60)
    
    # Load test data
    file_path = 'test_input_files/3rdFinalNoExtra.xlsx'
    
    try:
        # Process the Excel file
        processor = ExcelProcessor(file_path)
        result = processor.process_excel()
        
        if not result:
            print("❌ Failed to process Excel file")
            return
        
        print("✅ Excel file processed successfully!")
        
        # Simulate user input with quantities
        work_order_data = result.get('work_order_data')
        if work_order_data is None or work_order_data.empty:
            print("❌ No work order data found")
            return
        
        # Convert to list if it's a DataFrame
        if hasattr(work_order_data, 'to_dict'):
            work_items = work_order_data.to_dict('records')
        else:
            work_items = work_order_data if isinstance(work_order_data, list) else []
        
        # Simulate user entering quantities for some items
        bill_quantity_items = []
        for idx, item in enumerate(work_items[:10]):  # Test first 10 items
            item_no = str(item.get('Item', item.get('Item No.', f'Item_{idx + 1}')))
            description = str(item.get('Description', 'No description'))
            unit = str(item.get('Unit', 'Unit'))
            
            # Safely convert rate to float
            try:
                rate_value = item.get('Rate', 0)
                rate = float(rate_value) if rate_value is not None and not (isinstance(rate_value, float) and pd.isna(rate_value)) else 0.0
            except (ValueError, TypeError):
                rate = 0.0
            
            # Enter some quantities for testing
            if idx < 5:  # First 5 items get quantities
                bill_qty = 10.0 + idx
            else:
                bill_qty = 0.0
            
            if bill_qty > 0:
                bill_quantity_items.append({
                    'Item No.': item_no,
                    'Description': description,
                    'Unit': unit,
                    'Quantity': bill_qty,
                    'Rate': rate,
                    'Amount': bill_qty * rate
                })
        
        print(f"📊 Created {len(bill_quantity_items)} bill quantity items")
        
        # Create updated data structure
        updated_data = {
            'title_data': result.get('title_data', {}),
            'work_order_data': work_order_data,
            'bill_quantity_data': pd.DataFrame(bill_quantity_items),
            'extra_items_data': result.get('extra_items_data', pd.DataFrame())
        }
        
        # Generate documents
        print("🔄 Generating documents...")
        doc_generator = EnhancedDocumentGenerator(updated_data)
        
        # Generate HTML documents
        html_documents = doc_generator.generate_all_documents()
        
        if html_documents:
            print(f"✅ Generated {len(html_documents)} HTML documents!")
            
            # Save HTML files for inspection
            html_dir = Path("test_html_output")
            html_dir.mkdir(exist_ok=True)
            
            for filename, html_content in html_documents.items():
                html_file = html_dir / filename
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"📄 Saved HTML: {html_file}")
            
            # Convert HTML to PDF
            print("🔄 Converting to PDF...")
            pdf_documents = doc_generator.create_pdf_documents(html_documents)
            
            if pdf_documents:
                print(f"✅ Generated {len(pdf_documents)} PDF documents!")
                
                # Save PDF files
                pdf_dir = Path("test_pdf_output")
                pdf_dir.mkdir(exist_ok=True)
                
                for filename, pdf_bytes in pdf_documents.items():
                    pdf_file = pdf_dir / filename
                    with open(pdf_file, 'wb') as f:
                        f.write(pdf_bytes)
                    print(f"📄 Saved PDF: {pdf_file}")
                
                # Analyze the HTML content for table formatting issues
                print("\n🔍 Analyzing Table Formatting...")
                analyze_table_formatting(html_documents)
                
            else:
                print("❌ Failed to create PDF documents")
        else:
            print("❌ Failed to generate HTML documents")
            
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        import traceback
        traceback.print_exc()

def analyze_table_formatting(html_documents):
    """Analyze HTML content for table formatting issues"""
    print("\n" + "=" * 60)
    print("📊 TABLE FORMATTING ANALYSIS")
    print("=" * 60)
    
    for filename, html_content in html_documents.items():
        print(f"\n📄 Analyzing: {filename}")
        print("-" * 40)
        
        # Check for table elements
        if '<table' in html_content:
            print("✅ Contains table elements")
            
            # Check for table width specifications
            if 'width=' in html_content or 'style="width' in html_content:
                print("✅ Contains width specifications")
            else:
                print("❌ Missing width specifications")
            
            # Check for table cell content
            if '<td' in html_content:
                print("✅ Contains table cells")
                
                # Count empty cells
                empty_cells = html_content.count('<td></td>') + html_content.count('<td> </td>') + html_content.count('<td>&nbsp;</td>')
                total_cells = html_content.count('<td')
                print(f"📊 Total cells: {total_cells}")
                print(f"📊 Empty cells: {empty_cells}")
                print(f"📊 Empty cell percentage: {(empty_cells/total_cells)*100:.1f}%")
                
                if empty_cells > total_cells * 0.5:
                    print("⚠️  High percentage of empty cells - potential formatting issue")
                else:
                    print("✅ Reasonable cell content distribution")
            else:
                print("❌ No table cells found")
            
            # Check for specific table structure
            if 'Item No.' in html_content:
                print("✅ Contains Item No. column")
            if 'Description' in html_content:
                print("✅ Contains Description column")
            if 'Rate' in html_content:
                print("✅ Contains Rate column")
            if 'Amount' in html_content:
                print("✅ Contains Amount column")
            
            # Check for CSS styling
            if 'class=' in html_content:
                print("✅ Contains CSS classes")
            if 'style=' in html_content:
                print("✅ Contains inline styles")
            
            # Look for table width issues
            if 'table-layout' in html_content:
                print("✅ Contains table-layout specification")
            else:
                print("⚠️  Missing table-layout specification")
            
            # Check for column width specifications
            if 'colgroup' in html_content:
                print("✅ Contains column group specifications")
            else:
                print("⚠️  Missing column group specifications")
                
        else:
            print("❌ No table elements found")
        
        # Show a sample of the HTML content
        print(f"\n📋 Sample HTML Content (first 500 chars):")
        print(html_content[:500] + "...")

if __name__ == "__main__":
    test_pdf_generation()
