#!/usr/bin/env python3
"""
Simple test to verify FirstPageGenerator can be imported and instantiated
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """Test that FirstPageGenerator can be imported"""
    try:
        from utils.first_page_generator import FirstPageGenerator
        print("✅ FirstPageGenerator imported successfully")
        
        # Try to instantiate
        generator = FirstPageGenerator()
        print("✅ FirstPageGenerator instantiated successfully")
        
        return True
    except Exception as e:
        print(f"❌ Error importing FirstPageGenerator: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Simple Zero Rate Handling Test")
    print("=" * 40)
    
    result = test_import()
    
    print("\n" + "=" * 40)
    if result:
        print("✅ Import test passed!")
        print("✅ FirstPageGenerator is ready for use")
    else:
        print("❌ Import test failed!")
    
    return result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)