#!/usr/bin/env python3
"""
Deployment Script for BillGenerator OPTIMIZED VERSION
Handles deployment to Streamlit Cloud and Vercel
"""

import os
import subprocess
import sys
from pathlib import Path

def check_requirements():
    """Check if all requirements are met for deployment"""
    print("🔍 Checking deployment requirements...")
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found")
        return False
    
    # Check if main app exists
    if not Path("app.py").exists():
        print("❌ app.py not found")
        return False
    
    # Check if templates exist
    if not Path("templates").exists():
        print("❌ templates directory not found")
        return False
    
    print("✅ All requirements met")
    return True

def deploy_streamlit():
    """Deploy to Streamlit Cloud"""
    print("🚀 Deploying to Streamlit Cloud...")
    
    try:
        # Check if git is initialized
        if not Path(".git").exists():
            print("📦 Initializing Git repository...")
            subprocess.run(["git", "init"], check=True)
            
            # Add all files
            subprocess.run(["git", "add", "."], check=True)
            
            # Initial commit
            subprocess.run(["git", "commit", "-m", "Initial commit - BillGenerator OPTIMIZED"], check=True)
        
        print("✅ Git repository ready")
        print("📋 Next steps for Streamlit Cloud:")
        print("1. Push to GitHub repository")
        print("2. Connect to Streamlit Cloud")
        print("3. Deploy with one click")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git setup failed: {e}")
        return False

def deploy_vercel():
    """Deploy to Vercel"""
    print("🚀 Deploying to Vercel...")
    
    try:
        # Check if Vercel CLI is installed
        result = subprocess.run(["vercel", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Vercel CLI not installed. Install with: npm i -g vercel")
            return False
        
        print("✅ Vercel CLI found")
        print("📋 Next steps for Vercel:")
        print("1. Run: vercel login")
        print("2. Run: vercel --prod")
        print("3. Follow the prompts")
        
        return True
        
    except FileNotFoundError:
        print("❌ Vercel CLI not found. Install with: npm i -g vercel")
        return False

def create_deployment_guide():
    """Create a comprehensive deployment guide"""
    guide_content = """# 🚀 DEPLOYMENT GUIDE - BillGenerator OPTIMIZED

## 📋 Prerequisites
- Python 3.8+
- Git installed
- GitHub account (for Streamlit Cloud)
- Vercel account (for Vercel deployment)

## 🌐 Streamlit Cloud Deployment

### Step 1: Prepare Repository
```bash
# Initialize Git (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "BillGenerator OPTIMIZED - Ready for deployment"

# Add remote repository
git remote add origin https://github.com/yourusername/billgenerator-optimized.git

# Push to GitHub
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Select the repository and branch
5. Set main file path to `app.py`
6. Click "Deploy"

## ☁️ Vercel Deployment

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Deploy
```bash
# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

### Step 3: Configure
- Follow the prompts
- Set build command: `pip install -r requirements.txt`
- Set output directory: `.`
- Set install command: `pip install -r requirements.txt`

## 🖥️ Local Deployment

### Option 1: One-Click Launch (Windows)
```bash
# Double-click the batch file
🚀_LAUNCH_APP.bat
```

### Option 2: Manual Launch
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## 🔧 Configuration

### Environment Variables
- `STREAMLIT_SERVER_PORT`: Port for Streamlit (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: localhost)

### Customization
- Edit `app.py` for main application logic
- Edit `templates/` for document templates
- Edit `static/` for CSS and JavaScript
- Edit `requirements.txt` for dependencies

## 📊 Monitoring

### Performance Metrics
- Real-time dashboard in the app
- Efficiency scoring system
- Memory usage monitoring
- Processing time tracking

### Error Handling
- Comprehensive error logging
- User-friendly error messages
- Automatic recovery mechanisms

## 🆘 Troubleshooting

### Common Issues
1. **Import Errors**: Check Python version and dependencies
2. **Template Errors**: Verify template files exist
3. **Memory Issues**: Check system resources
4. **Deployment Errors**: Verify configuration files

### Support
- Check logs in the application
- Review error messages
- Contact: crajkumarsingh@hotmail.com

## ✅ Verification

### Test Deployment
1. Upload a test Excel file
2. Generate documents
3. Verify all outputs
4. Check performance metrics

### Production Checklist
- [ ] All dependencies installed
- [ ] Templates present
- [ ] Test files working
- [ ] Performance acceptable
- [ ] Error handling working
- [ ] Documentation complete

---

*Generated by BillGenerator OPTIMIZED V3.0*
*September 2025*
"""
    
    with open("DEPLOYMENT_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(guide_content)
    
    print("📖 Deployment guide created: DEPLOYMENT_GUIDE.md")

def main():
    """Main deployment function"""
    print("🚀 BillGenerator OPTIMIZED - Deployment Manager")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements not met. Please fix issues and try again.")
        return
    
    # Create deployment guide
    create_deployment_guide()
    
    # Show deployment options
    print("\n📋 Deployment Options:")
    print("1. Streamlit Cloud (Recommended)")
    print("2. Vercel")
    print("3. Local deployment")
    
    choice = input("\nSelect deployment option (1-3): ").strip()
    
    if choice == "1":
        deploy_streamlit()
    elif choice == "2":
        deploy_vercel()
    elif choice == "3":
        print("🖥️ For local deployment, run: streamlit run app.py")
    else:
        print("❌ Invalid choice")
    
    print("\n✅ Deployment setup complete!")
    print("📖 See DEPLOYMENT_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    main()
