#!/usr/bin/env python3
"""
Script to generate all document formats (HTML, PDF, DOC) and save them in organized directories
"""

import pandas as pd
import sys
from pathlib import Path
import os

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from enhanced_document_generator_fixed import DocumentGenerator

def create_sample_data():
    """Create sample data for document generation"""
    return {
        'title_data': {
            'Project Name': 'NH-XX Highway Improvement Project',
            'Contract No': 'NH-2025-789',
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
                'Description': 'Providing and laying in position cement concrete M25',
                'Unit': 'Cum',
                'Quantity': 85.25,
                'Rate': 4500.00,
                'Amount': 383625.00,
                'Remark': 'Reinforced concrete'
            },
            {
                'Item No.': '3',
                'Description': 'Providing and fixing MS railing',
                'Unit': 'Meter',
                'Quantity': 120.00,
                'Rate': 1200.00,
                'Amount': 144000.00,
                'Remark': 'MS 40x20x1.5 mm'
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
                'Description': 'Providing and laying in position cement concrete M25',
                'Unit': 'Cum',
                'Quantity': 85.25,
                'Rate': 4500.00,
                'Amount': 383625.00
            },
            {
                'Item No.': '3',
                'Description': 'Providing and fixing MS railing',
                'Unit': 'Meter',
                'Quantity': 120.00,
                'Rate': 1200.00,
                'Amount': 144000.00
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

def main():
    """Main function to generate all document formats"""
    print("🔍 Document Generation - All Formats")
    print("=" * 40)
    
    try:
        # Create sample data
        print("🔄 Creating sample data...")
        sample_data = create_sample_data()
        print("✅ Sample data created successfully")
        
        # Initialize the document generator
        print("\n🔄 Initializing DocumentGenerator...")
        generator = DocumentGenerator(sample_data)
        print("✅ DocumentGenerator initialized successfully")
        
        # Generate and save all formats
        print("\n💾 Generating and saving all document formats...")
        output_dir = "output"
        success = generator.save_all_formats(output_dir)
        
        if success:
            print(f"\n🎉 All documents generated and saved successfully to '{output_dir}' directory!")
            print("\n📁 Directory structure:")
            print(f"   {output_dir}/")
            print(f"   ├── html/ (HTML files)")
            print(f"   ├── pdf/ (PDF files)")
            print(f"   ├── doc/ (DOC files)")
            print(f"   ├── All_Documents.zip (Complete package)")
            
            # Show what files were created
            html_dir = Path(output_dir) / "html"
            pdf_dir = Path(output_dir) / "pdf"
            doc_dir = Path(output_dir) / "doc"
            
            if html_dir.exists():
                html_files = list(html_dir.glob("*.html"))
                print(f"\n📄 HTML files generated: {len(html_files)}")
                for file in html_files:
                    print(f"   - {file.name}")
            
            if pdf_dir.exists():
                pdf_files = list(pdf_dir.glob("*.pdf"))
                print(f"\n🖨️  PDF files generated: {len(pdf_files)}")
                for file in pdf_files:
                    print(f"   - {file.name}")
            
            if doc_dir.exists():
                doc_files = list(doc_dir.glob("*.docx"))
                print(f"\n📝 DOC files generated: {len(doc_files)}")
                for file in doc_files:
                    print(f"   - {file.name}")
            
            # Check for ZIP file
            zip_file = Path(output_dir) / "All_Documents.zip"
            if zip_file.exists():
                size = zip_file.stat().st_size
                print(f"\n📦 ZIP package created: {zip_file.name} ({size:,} bytes)")
            
            print(f"\n✨ You can now find all generated documents in the '{output_dir}' folder!")
            return True
        else:
            print("\n❌ Failed to generate documents!")
            return False
            
    except Exception as e:
        print(f"\n💥 Error during document generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)