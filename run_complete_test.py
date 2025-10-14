#!/usr/bin/env python3
"""
Complete Test Runner
Runs both Excel Upload Mode and Online Mode tests
"""

import subprocess
import sys
import os
from pathlib import Path

def run_test(script_name, description):
    """Run a test script and return the result"""
    print(f"\n🚀 Running {description}...")
    print("=" * 50)
    
    try:
        # Run the script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            if result.stdout:
                print("Output:")
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} failed!")
            if result.stdout:
                print("Output:")
                print(result.stdout)
            if result.stderr:
                print("Error:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out!")
        return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def main():
    """Run complete test suite"""
    print("🧪 Complete Bill Generator Testing Suite")
    print("=" * 60)
    
    # Check if required files exist
    required_files = [
        "online_mode_demo.py",
        "excel_upload_demo.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    # Run tests
    tests = [
        ("online_mode_demo.py", "Online Mode Demonstration"),
        ("excel_upload_demo.py", "Excel Upload Mode Demonstration")
    ]
    
    results = []
    for script, description in tests:
        success = run_test(script, description)
        results.append((description, success))
    
    # Print final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{description}: {status}")
        if not success:
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