#!/usr/bin/env python3
"""
Final Fix for Extra Items Template Alignment in V02 and V03
Run this script from V02 or V03 directory to fix the remaining alignment issue
"""

import os
import sys

def fix_extra_items_template():
    """Fix vertical alignment in extra_items.html template"""
    template_path = os.path.join('templates', 'extra_items.html')
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        print("💡 Make sure to run this script from the project root directory")
        return False
    
    try:
        # Read current content
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already fixed
        if 'vertical-align: top' in content:
            print(f"✅ {template_path} already has vertical alignment")
            return True
        
        # Apply the fix
        original_css = "th, td { border: 1px solid black; padding: 5px; text-align: left; word-wrap: break-word; }"
        fixed_css = "th, td { border: 1px solid black; padding: 5px; text-align: left; vertical-align: top; word-wrap: break-word; }"
        
        if original_css in content:
            content = content.replace(original_css, fixed_css)
            
            # Write back the fixed content
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Fixed vertical alignment in {template_path}")
            return True
        else:
            print(f"⚠️  Could not find expected CSS rule in {template_path}")
            return False
    
    except Exception as e:
        print(f"❌ Error fixing {template_path}: {str(e)}")
        return False

def main():
    """Main function"""
    print("🔧 EXTRA ITEMS TEMPLATE ALIGNMENT FIX")
    print("=" * 50)
    
    # Detect which project we're in
    cwd = os.getcwd()
    if 'BillGeneratorV02' in cwd:
        project_name = "BillGeneratorV02"
    elif 'BillGeneratorV03' in cwd:
        project_name = "BillGeneratorV03"
    else:
        print("❌ Please run this script from BillGeneratorV02 or BillGeneratorV03 directory")
        print("💡 Usage:")
        print("   cd C:\\Users\\Rajkumar\\BillGeneratorV02")
        print("   python fix_extra_items_alignment.py")
        return False
    
    print(f"📁 Working in: {project_name}")
    
    if fix_extra_items_template():
        print(f"\n🎉 SUCCESS: {project_name} extra_items.html template enhanced!")
        print("✅ Vertical alignment now consistent with V01 standards")
        print("📋 Template ready for production use")
        return True
    else:
        print(f"\n❌ FAILED: Could not enhance {project_name} template")
        print("📋 Manual verification may be required")
        return False

if __name__ == "__main__":
    main()