#!/usr/bin/env python3
"""
Run the Streamlit app with debugging enabled
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting Streamlit app with debugging...")
    print("=" * 60)
    print("📋 Instructions:")
    print("1. The app will open in your browser")
    print("2. Upload one of the test Excel files")
    print("3. Check the debug information displayed")
    print("4. Look for any error messages")
    print("=" * 60)
    
    try:
        # Run Streamlit app
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"], check=True)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {e}")

if __name__ == "__main__":
    main()
