#!/usr/bin/env python3
"""
Asset Manager for BillGenerator OPTIMIZED VERSION
Manages all assets including templates, test files, and static resources
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any

class AssetManager:
    """Manages all assets for the BillGenerator application"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.assets = {
            'templates': self.base_dir / 'templates',
            'test_files': self.base_dir / 'test_input_files',
            'static': self.base_dir / 'static',
            'latex': self.base_dir / 'LaTeX_Templates',
            'images': self.base_dir
        }
    
    def validate_assets(self) -> Dict[str, Any]:
        """Validate that all required assets are present"""
        validation_results = {
            'templates': self._validate_templates(),
            'test_files': self._validate_test_files(),
            'static': self._validate_static_assets(),
            'latex': self._validate_latex_templates(),
            'images': self._validate_images()
        }
        
        return validation_results
    
    def _validate_templates(self) -> Dict[str, Any]:
        """Validate HTML templates"""
        required_templates = [
            'first_page.html',
            'deviation_statement.html',
            'extra_items.html',
            'certificate_ii.html',
            'certificate_iii.html',
            'note_sheet.html'
        ]
        
        found_templates = []
        missing_templates = []
        
        for template in required_templates:
            template_path = self.assets['templates'] / template
            if template_path.exists():
                found_templates.append(template)
            else:
                missing_templates.append(template)
        
        return {
            'found': found_templates,
            'missing': missing_templates,
            'total_required': len(required_templates),
            'total_found': len(found_templates),
            'status': 'complete' if len(missing_templates) == 0 else 'incomplete'
        }
    
    def _validate_test_files(self) -> Dict[str, Any]:
        """Validate test Excel files"""
        test_files = list(self.assets['test_files'].glob('*.xlsx'))
        
        return {
            'files': [f.name for f in test_files],
            'count': len(test_files),
            'status': 'complete' if len(test_files) > 0 else 'incomplete'
        }
    
    def _validate_static_assets(self) -> Dict[str, Any]:
        """Validate static assets (CSS, JS)"""
        css_files = list(self.assets['static'].glob('*.css'))
        js_files = list(self.assets['static'].glob('*.js'))
        
        return {
            'css_files': [f.name for f in css_files],
            'js_files': [f.name for f in js_files],
            'total_assets': len(css_files) + len(js_files),
            'status': 'complete' if len(css_files) > 0 or len(js_files) > 0 else 'incomplete'
        }
    
    def _validate_latex_templates(self) -> Dict[str, Any]:
        """Validate LaTeX templates"""
        latex_files = list(self.assets['latex'].glob('*.TeX'))
        
        return {
            'files': [f.name for f in latex_files],
            'count': len(latex_files),
            'status': 'complete' if len(latex_files) > 0 else 'incomplete'
        }
    
    def _validate_images(self) -> Dict[str, Any]:
        """Validate image assets"""
        image_files = list(self.assets['images'].glob('*.png')) + list(self.assets['images'].glob('*.jpg'))
        
        return {
            'files': [f.name for f in image_files],
            'count': len(image_files),
            'status': 'complete' if len(image_files) > 0 else 'incomplete'
        }
    
    def get_asset_summary(self) -> str:
        """Get a summary of all assets"""
        validation = self.validate_assets()
        
        summary = "📁 ASSET SUMMARY\n"
        summary += "=" * 50 + "\n\n"
        
        for category, results in validation.items():
            status_icon = "✅" if results['status'] == 'complete' else "❌"
            summary += f"{status_icon} {category.upper()}\n"
            
            if 'found' in results:
                summary += f"   Found: {results['total_found']}/{results['total_required']}\n"
                if results['missing']:
                    summary += f"   Missing: {', '.join(results['missing'])}\n"
            elif 'count' in results:
                summary += f"   Files: {results['count']}\n"
            elif 'total_assets' in results:
                summary += f"   Assets: {results['total_assets']}\n"
            
            summary += "\n"
        
        return summary
    
    def list_all_assets(self) -> List[str]:
        """List all asset files"""
        all_assets = []
        
        for category, path in self.assets.items():
            if path.exists():
                for file_path in path.rglob('*'):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(self.base_dir)
                        all_assets.append(str(relative_path))
        
        return sorted(all_assets)

def main():
    """Main function to validate and report on assets"""
    print("🔍 BillGenerator OPTIMIZED - Asset Validation")
    print("=" * 60)
    
    manager = AssetManager()
    
    # Validate all assets
    validation_results = manager.validate_assets()
    
    # Print summary
    print(manager.get_asset_summary())
    
    # List all assets
    print("📋 ALL ASSETS:")
    print("-" * 30)
    all_assets = manager.list_all_assets()
    for asset in all_assets:
        print(f"  📄 {asset}")
    
    print(f"\n📊 Total Assets: {len(all_assets)}")
    
    # Check if all critical assets are present
    critical_assets_complete = all(
        results['status'] == 'complete' 
        for results in validation_results.values()
    )
    
    if critical_assets_complete:
        print("\n🎉 All critical assets are present and ready!")
    else:
        print("\n⚠️  Some assets are missing. Please check the validation results above.")

if __name__ == "__main__":
    main()
