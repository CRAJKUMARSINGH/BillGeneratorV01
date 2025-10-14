#!/usr/bin/env python3
"""
Test runner script for the Bill Generator test suite
"""

import os
import sys
import subprocess
from pathlib import Path

def run_test_script(script_name):
    """Run a single test script and return the result"""
    try:
        print(f"Running {script_name}...")
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ {script_name} PASSED")
            return True
        else:
            print(f"❌ {script_name} FAILED")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {script_name} TIMED OUT")
        return False
    except Exception as e:
        print(f"❌ {script_name} ERROR: {e}")
        return False

def main():
    """Run all test scripts in the test_scripts directory"""
    # Change to the test_scripts directory
    test_scripts_dir = Path(__file__).parent / "test_scripts"
    os.chdir(test_scripts_dir)
    
    print("Bill Generator Test Suite Runner")
    print("=" * 40)
    
    # List all test scripts
    test_scripts = list(test_scripts_dir.glob("test_*.py"))
    test_scripts.extend(test_scripts_dir.glob("*_test.py"))
    test_scripts.extend(test_scripts_dir.glob("*_test_*.py"))
    test_scripts.extend(test_scripts_dir.glob("batch_*.py"))
    test_scripts.extend(test_scripts_dir.glob("comprehensive_*.py"))
    test_scripts.extend(test_scripts_dir.glob("simple_*.py"))
    
    # Remove duplicates and sort
    test_scripts = sorted(list(set(test_scripts)))
    
    print(f"Found {len(test_scripts)} test scripts")
    print()
    
    # Run each test script
    passed = 0
    failed = 0
    
    for script_path in test_scripts:
        if run_test_script(script_path.name):
            passed += 1
        else:
            failed += 1
        print()
    
    # Summary
    print("=" * 40)
    print("TEST SUMMARY:")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Total:  {len(test_scripts)}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n❌ {failed} tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)