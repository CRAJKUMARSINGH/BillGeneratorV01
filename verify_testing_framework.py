#!/usr/bin/env python3
"""
Verification Script for Testing Framework
Confirms that all components are ready for testing
"""

import os
import sys
from pathlib import Path

def check_directory_structure():
    """Check if required directories exist and have proper structure"""
    print("🔍 Checking Directory Structure...")
    
    # Check INPUT_FILES directory
    input_dir = Path("INPUT_FILES")
    if input_dir.exists():
        input_files = list(input_dir.glob("*.xlsx"))
        print(f"✅ INPUT_FILES directory exists with {len(input_files)} Excel files")
        if len(input_files) >= 36:
            print("✅ Sufficient input files available")
        else:
            print(f"⚠️  Only {len(input_files)} files found, expected 36+")
    else:
        print("❌ INPUT_FILES directory not found")
        return False
    
    # Check OUTPUT_FILES directory
    output_dir = Path("OUTPUT_FILES")
    if output_dir.exists():
        print("✅ OUTPUT_FILES directory exists")
    else:
        print("❌ OUTPUT_FILES directory not found")
        return False
    
    return True

def check_required_scripts():
    """Check if required test scripts exist"""
    print("\n🔍 Checking Required Scripts...")
    
    required_scripts = [
        "complete_app_tester.py",
        "online_mode_demo.py",
        "excel_upload_demo.py",
        "RUN_TESTS.bat"
    ]
    
    all_found = True
    for script in required_scripts:
        if Path(script).exists():
            print(f"✅ {script} found")
        else:
            print(f"❌ {script} not found")
            all_found = False
    
    return all_found

def check_python_environment():
    """Check Python environment and required packages"""
    print("\n🔍 Checking Python Environment...")
    
    # Check Python version
    print(f"✅ Python version: {sys.version}")
    
    # Check required packages
    required_packages = ['pandas', 'numpy', 'openpyxl']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} not available")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_test_inputs():
    """Check test input files structure"""
    print("\n🔍 Checking Test Input Files...")
    
    input_dir = Path("INPUT_FILES")
    if input_dir.exists():
        # Check a sample file
        sample_files = list(input_dir.glob("*.xlsx"))
        if sample_files:
            sample_file = sample_files[0]
            print(f"✅ Sample file found: {sample_file.name}")
            print(f"✅ File size: {sample_file.stat().st_size} bytes")
            return True
        else:
            print("❌ No Excel files found in INPUT_FILES")
            return False
    else:
        print("❌ INPUT_FILES directory not accessible")
        return False

def main():
    """Main verification function"""
    print("🚀 Testing Framework Verification")
    print("=" * 50)
    
    # Run all checks
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Required Scripts", check_required_scripts),
        ("Python Environment", check_python_environment),
        ("Test Inputs", check_test_inputs)
    ]
    
    results = []
    for check_name, check_function in checks:
        print(f"\n📋 {check_name}")
        print("-" * 30)
        result = check_function()
        results.append((check_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Testing framework is ready for use")
        print("\nTo run tests:")
        print("  Method 1: python complete_app_tester.py")
        print("  Method 2: Double-click RUN_TESTS.bat")
        print("\nOutput will be saved to OUTPUT_FILES/ directory")
    else:
        print("❌ SOME CHECKS FAILED!")
        print("Please review the output above and fix issues")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)