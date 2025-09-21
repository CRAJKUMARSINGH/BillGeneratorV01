#!/usr/bin/env python3
"""
Streamlit Deployment Script for Bill Generator
Handles setup and configuration for cloud deployment
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_dependencies():
    """Install required dependencies for Streamlit deployment"""
    logger.info("Installing dependencies...")
    
    try:
        # Install core dependencies
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        logger.info("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install dependencies: {e}")
        return False
    
    return True

def setup_playwright():
    """Setup Playwright for PDF conversion"""
    logger.info("Setting up Playwright...")
    
    try:
        # Install Playwright browsers
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        logger.info("✅ Playwright setup completed")
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ Playwright setup failed (optional): {e}")
        # Continue without Playwright - other PDF engines will be used

def create_directories():
    """Create necessary directories for the application"""
    logger.info("Creating application directories...")
    
    directories = [
        "input_files",
        "output",
        "batch_output", 
        "logs",
        "cache",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"✅ Created directory: {directory}")

def verify_deployment():
    """Verify that the application is ready for deployment"""
    logger.info("Verifying deployment readiness...")
    
    # Check if main app file exists
    if not Path("app.py").exists():
        logger.error("❌ app.py not found")
        return False
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        logger.error("❌ requirements.txt not found")
        return False
    
    # Check if Streamlit config exists
    if not Path(".streamlit/config.toml").exists():
        logger.warning("⚠️ Streamlit config not found, using defaults")
    
    logger.info("✅ Deployment verification completed")
    return True

def main():
    """Main deployment setup function"""
    logger.info("🚀 Starting Streamlit deployment setup...")
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        logger.error("❌ Deployment setup failed")
        return False
    
    # Setup Playwright (optional)
    setup_playwright()
    
    # Verify deployment
    if not verify_deployment():
        logger.error("❌ Deployment verification failed")
        return False
    
    logger.info("🎉 Streamlit deployment setup completed successfully!")
    logger.info("📝 Next steps:")
    logger.info("   1. Push changes to GitHub repository")
    logger.info("   2. Deploy to Streamlit Cloud")
    logger.info("   3. Configure environment variables if needed")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
