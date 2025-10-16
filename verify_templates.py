#!/usr/bin/env python3
"""
Simple verification script to check that template files exist
"""

import os

def check_templates():
    """Check that all required template files exist"""
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    required_templates = [
        'first_page.html',
        'deviation_statement.html',
        'extra_items.html',
        'certificate_ii.html',
        'certificate_iii.html',
        'note_sheet.html'
    ]
    
    print(f"Checking templates in: {template_dir}")
    print("-" * 50)
    
    all_found = True
    for template in required_templates:
        template_path = os.path.join(template_dir, template)
        if os.path.exists(template_path):
            # Get file size
            size = os.path.getsize(template_path)
            print(f"✅ {template} - Found ({size} bytes)")
        else:
            print(f"❌ {template} - Missing")
            all_found = False
    
    print("-" * 50)
    if all_found:
        print("✅ All templates found!")
    else:
        print("❌ Some templates are missing!")
    
    return all_found

if __name__ == "__main__":
    check_templates()