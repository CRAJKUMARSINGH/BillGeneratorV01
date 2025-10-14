from jinja2 import Environment, FileSystemLoader
import os

def test_template_loading():
    """Test if templates can be loaded correctly"""
    print("🔍 Testing Template Loading")
    print("=" * 25)
    
    # Test main templates directory
    main_template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    print(f"Main template directory: {main_template_dir}")
    print(f"Exists: {os.path.exists(main_template_dir)}")
    
    if os.path.exists(main_template_dir):
        main_env = Environment(loader=FileSystemLoader(main_template_dir))
        try:
            template = main_env.get_template('note_sheet.html')
            print("✅ Main templates/note_sheet.html loaded successfully")
        except Exception as e:
            print(f"❌ Main templates/note_sheet.html failed to load: {e}")
    
    # Test templates_14102025 directory
    template_14102025_dir = os.path.join(os.path.dirname(__file__), 'templates_14102025', 'templates_14102025')
    print(f"\n14102025 template directory: {template_14102025_dir}")
    print(f"Exists: {os.path.exists(template_14102025_dir)}")
    
    if os.path.exists(template_14102025_dir):
        env_14102025 = Environment(loader=FileSystemLoader(template_14102025_dir))
        try:
            template = env_14102025.get_template('note_sheet.html')
            print("✅ templates_14102025/note_sheet.html loaded successfully")
            
            # Test rendering with sample data
            sample_data = {
                'data': {
                    'agreement_no': 'TEST-2025-001',
                    'name_of_work': 'Test Work',
                    'name_of_firm': 'Test Firm',
                    'date_commencement': '01/01/2025',
                    'date_completion': '31/12/2025',
                    'actual_completion': '25/11/2025',
                    'work_order_amount': '1000000.00',
                    'totals': {
                        'payable': '950000.00',
                        'extra_items_sum': 50000.00
                    }
                },
                'notes': ['Test note 1', 'Test note 2']
            }
            
            rendered = template.render(**sample_data)
            print("✅ Template rendered successfully")
            print(f"   Rendered content length: {len(rendered)} characters")
            
            # Check for key elements
            if '________ BILL SCRUTINY SHEET' in rendered:
                print("✅ Correct title found")
            else:
                print("❌ Correct title not found")
                
            if 'TEST-2025-001' in rendered:
                print("✅ Agreement number rendered")
            else:
                print("❌ Agreement number not rendered")
                
        except Exception as e:
            print(f"❌ templates_14102025/note_sheet.html failed to load: {e}")
    
    print("\n🔍 Testing TemplateRenderer")
    try:
        from utils.template_renderer import TemplateRenderer
        renderer = TemplateRenderer()
        print("✅ TemplateRenderer initialized successfully")
    except Exception as e:
        print(f"❌ TemplateRenderer failed to initialize: {e}")

if __name__ == "__main__":
    test_template_loading()