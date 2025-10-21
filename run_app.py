#!/usr/bin/env python3
"""
Simple deployment script for the Professional Bill Generator
This script ensures all dependencies are installed and runs the application
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    try:
        print("📦 Installing requirements...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--quiet", "--no-input",
            "-r", "requirements_fixed.txt"
        ])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
    except FileNotFoundError:
        print("❌ requirements_fixed.txt not found")
        return False

def run_streamlit_app():
    """Run the Streamlit application"""
    try:
        print("🚀 Starting Professional Bill Generator...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "bill_generator_fixed.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

def main():
    """Main deployment function"""
    print("🧾 Professional Bill Generator - Deployment Script")
    print("=" * 50)
    
    # Check if files exist
    if not os.path.exists("bill_generator_fixed.py"):
        print("❌ bill_generator_fixed.py not found in current directory")
        return
    
    if not os.path.exists("requirements_fixed.txt"):
        print("❌ requirements_fixed.txt not found in current directory")
        return
    
    # Install requirements
    if install_requirements():
        print("\n🚀 Starting application...")
        run_streamlit_app()
    else:
        print("❌ Failed to install requirements. Please check your environment.")

if __name__ == "__main__":
    main()