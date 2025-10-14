#!/usr/bin/env python3
"""
Verification script for the deployable Bill Generator application
"""

import sys
import os
import importlib.util
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    if os.path.exists(filepath):
        print(f"✅ {description} - FOUND")
        return True
    else:
        print(f"❌ {description} - MISSING")
        return False

def check_import(module_name, description):
    """Try to import a module and print status"""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is not None and spec.loader is not None:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"✅ {description} - IMPORT SUCCESS")
            return True
        else:
            print(f"❌ {description} - NOT FOUND")
            return False
    except Exception as e:
        print(f"❌ {description} - IMPORT FAILED: {str(e)}")
        return False

def main():
    """Main verification function"""
    print("Bill Generator Deployment Verification")
    print("=" * 40)
    
    # Check core files
    print("\n📁 Checking core files...")
    files_check = [
        ("deployable_app.py", "Deployable Streamlit App"),
        ("requirements-deploy.txt", "Deployment Requirements"),
        ("fixed_document_generator.py", "Fixed Document Generator"),
        ("process_with_fixed_generator.py", "Process Script"),
        ("DEPLOYMENT_INSTRUCTIONS.md", "Deployment Instructions"),
        ("TROUBLESHOOTING.md", "Troubleshooting Guide")
    ]
    
    files_ok = True
    for filename, description in files_check:
        if not check_file_exists(filename, description):
            files_ok = False
    
    # Check template files
    print("\n📄 Checking template files...")
    template_dir = Path("templates")
    templates = [
        "first_page.html",
        "deviation_statement.html",
        "extra_items.html",
        "certificate_ii.html",
        "certificate_iii.html",
        "note_sheet.html"
    ]
    
    templates_ok = True
    for template in templates:
        template_path = template_dir / template
        if not check_file_exists(str(template_path), f"Template: {template}"):
            templates_ok = False
    
    # Check utils files
    print("\n⚙️  Checking utility files...")
    utils_ok = check_file_exists("utils/excel_processor.py", "Excel Processor")
    
    # Check imports
    print("\n📦 Checking imports...")
    imports_check = [
        ("streamlit", "Streamlit Framework"),
        ("pandas", "Pandas Library"),
        ("openpyxl", "OpenPyXL Library"),
        ("reportlab", "ReportLab Library"),
        ("jinja2", "Jinja2 Library")
    ]
    
    imports_ok = True
    for module, description in imports_check:
        if not check_import(module, description):
            imports_ok = False
    
    # Check local imports
    print("\n🔧 Checking local imports...")
    local_imports = [
        ("utils.excel_processor", "Excel Processor Module"),
        ("fixed_document_generator", "Fixed Document Generator Module")
    ]
    
    local_imports_ok = True
    for module, description in local_imports:
        if not check_import(module, description):
            local_imports_ok = False
    
    # Summary
    print("\n" + "=" * 40)
    print("VERIFICATION SUMMARY:")
    print(f"  Core Files: {'✅ PASS' if files_ok else '❌ FAIL'}")
    print(f"  Templates: {'✅ PASS' if templates_ok else '❌ FAIL'}")
    print(f"  Utilities: {'✅ PASS' if utils_ok else '❌ FAIL'}")
    print(f"  Dependencies: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"  Local Modules: {'✅ PASS' if local_imports_ok else '❌ FAIL'}")
    
    overall_ok = files_ok and templates_ok and utils_ok and imports_ok and local_imports_ok
    
    if overall_ok:
        print("\n🎉 ALL CHECKS PASSED!")
        print("The deployable Bill Generator is ready for deployment.")
        print("\nTo deploy:")
        print("1. Install dependencies: pip install -r requirements-deploy.txt")
        print("2. Run the app: streamlit run deployable_app.py")
        return True
    else:
        print("\n❌ SOME CHECKS FAILED!")
        print("Please check the errors above and resolve them before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)