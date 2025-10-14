import pandas as pd
from enhanced_document_generator_fixed import EnhancedDocumentGenerator

def debug_template_rendering():
    """Debug template rendering issues"""
    print("🐛 Debugging Template Rendering")
    print("=" * 30)
    
    # Create minimal test data
    title_data = {
        'agreement_no': 'TEST-2025-001',
        'name_of_work': 'Test Work',
        'name_of_firm': 'Test Firm',
        'work_order_amount': '1000000.00'
    }
    
    work_order_data = pd.DataFrame([
        {
            'Item No.': '1',
            'Description': 'Test Item',
            'Unit': 'Nos',
            'Quantity Since': 100,
            'Rate': 1000,
            'Amount': 100000
        }
    ])
    
    test_data = {
        'title_data': title_data,
        'work_order_data': work_order_data,
        'bill_quantity_data': work_order_data.copy(),
        'extra_items_data': pd.DataFrame()
    }
    
    # Initialize document generator
    print("🔄 Initializing EnhancedDocumentGenerator...")
    generator = EnhancedDocumentGenerator(test_data)
    
    # Check template environment
    print(f"Template directory: {generator.jinja_env.loader.searchpath}")
    
    # Try to render note_sheet.html directly
    print("\n📄 Testing direct template rendering...")
    try:
        template = generator.jinja_env.get_template('note_sheet.html')
        print("✅ note_sheet.html template loaded")
        
        # Render with template data
        rendered = template.render(**generator.template_data)
        print("✅ note_sheet.html rendered successfully")
        print(f"   Content length: {len(rendered)} characters")
        
        if '________ BILL SCRUTINY SHEET' in rendered:
            print("✅ Correct title found")
        else:
            print("❌ Correct title not found")
            
    except Exception as e:
        print(f"❌ Direct template rendering failed: {e}")
    
    # Test the full document generation
    print("\n📄 Testing full document generation...")
    try:
        documents = generator.generate_all_documents()
        if 'Final Bill Scrutiny Sheet' in documents:
            content = documents['Final Bill Scrutiny Sheet']
            print("✅ Final Bill Scrutiny Sheet generated")
            print(f"   Content length: {len(content)} characters")
            
            # Check for key elements
            checks = [
                '<!DOCTYPE html>',
                '<title>Note Sheet</title>',
                '________ BILL SCRUTINY SHEET',
                'TEST-2025-001'
            ]
            
            for check in checks:
                if check in content:
                    print(f"✅ Found: {check}")
                else:
                    print(f"❌ Missing: {check}")
        else:
            print("❌ Final Bill Scrutiny Sheet not in generated documents")
            print("Available documents:")
            for doc_name in documents.keys():
                print(f"  - {doc_name}")
                
    except Exception as e:
        print(f"❌ Full document generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_template_rendering()