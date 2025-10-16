#!/usr/bin/env python3
"""
Verbose test to capture detailed document generation output
"""

import pandas as pd
import sys
from pathlib import Path
import logging

# Set up logging to capture detailed output
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

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
    """Main function to run verbose test"""
    print("🔍 Verbose Document Generation Test")
    print("=" * 40)
    
    # Create sample data
    print("🔄 Creating sample data...")
    sample_data = create_sample_data()
    print("✅ Sample data created successfully")
    
    # Initialize the document generator
    print("\n🔄 Initializing DocumentGenerator...")
    generator = DocumentGenerator(sample_data)
    print("✅ DocumentGenerator initialized successfully")
    
    # Test document generation
    print("\n📄 Generating HTML documents...")
    documents = generator.generate_all_documents()
    print(f"✅ Generated {len(documents)} HTML documents")
    
    # Print document names
    for name in documents.keys():
        print(f"  - {name}")
    
    # Test PDF generation
    print("\n🖨️  Generating PDF documents...")
    pdf_docs = generator.create_pdf_documents(documents)
    
    # Print detailed PDF generation info
    for name, content in pdf_docs.items():
        print(f"✅ Successfully generated {name} ({len(content)} bytes)")
    
    # Test saving all formats
    print("\n💾 Saving all document formats...")
    success = generator.save_all_formats("verbose_test_output")
    print(f"Save result: {success}")
    
    if success:
        print("\n🎉 All tests completed successfully!")
        return True
    else:
        print("\n❌ Tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)