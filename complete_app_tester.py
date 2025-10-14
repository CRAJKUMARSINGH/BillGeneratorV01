#!/usr/bin/env python3
"""
Complete App Tester
Runs comprehensive tests for both Excel Upload Mode and Online Mode
"""

import subprocess
import sys
import os
from pathlib import Path
import time

def run_test_script(script_name, description):
    """Run a test script and capture output"""
    print(f"\n{'='*60}")
    print(f"🏃 Running {description}")
    print(f"{'='*60}")
    
    try:
        # Run the script and capture output
        result = subprocess.run(
            [sys.executable, script_name], 
            capture_output=True, 
            text=True, 
            timeout=300,
            cwd=os.getcwd()
        )
        
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        else:
            print("No stdout output")
            
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        else:
            print("No stderr output")
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            return True
        else:
            print(f"❌ {description} failed!")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out!")
        return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def main():
    """Main test runner"""
    print("🚀 Complete App Testing Suite")
    print("=" * 60)
    print("This script will test both Excel Upload Mode and Online Mode")
    print("=" * 60)
    
    # Check if required files exist
    required_scripts = [
        "online_mode_demo.py",
        "excel_upload_demo.py"
    ]
    
    missing_scripts = []
    for script in required_scripts:
        if not Path(script).exists():
            missing_scripts.append(script)
    
    if missing_scripts:
        print(f"❌ Missing required scripts: {missing_scripts}")
        return False
    
    # Run tests
    test_results = []
    
    # Test 1: Online Mode
    result1 = run_test_script("online_mode_demo.py", "Online Mode Test")
    test_results.append(("Online Mode Test", result1))
    
    # Small delay between tests
    time.sleep(2)
    
    # Test 2: Excel Upload Mode
    result2 = run_test_script("excel_upload_demo.py", "Excel Upload Mode Test")
    test_results.append(("Excel Upload Mode Test", result2))
    
    # Print final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("📁 Check OUTPUT_FILES directory for detailed results")
        print("📝 Review FINAL_TESTING_SUMMARY.md for complete report")
    else:
        print("💥 SOME TESTS FAILED!")
        print("Please check the output above for details.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)