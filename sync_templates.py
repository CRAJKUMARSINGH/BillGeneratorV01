#!/usr/bin/env python3
"""
Template Synchronization Script

This script synchronizes HTML templates across multiple directories to avoid
having multiple copies of the same templates in different locations.
"""

import os
import shutil
import glob
from pathlib import Path

def sync_templates():
    """Synchronize templates across all template directories"""
    
    # Define the main template directory (source of truth)
    main_template_dir = Path("templates")
    
    # Define backup template directories
    backup_dirs = [
        Path("templates_14102025"),
        Path("templates_14102025/templates_14102025"),
        Path("templates_14102025/templates_14102025/tested templates")
    ]
    
    # Get all HTML templates from the main directory
    main_templates = list(main_template_dir.glob("*.html"))
    print(f"Found {len(main_templates)} templates in main directory")
    
    # Sync templates to all backup directories
    for backup_dir in backup_dirs:
        if backup_dir.exists():
            print(f"\nSyncing to {backup_dir}")
            
            # Remove existing HTML templates in backup directory
            existing_templates = list(backup_dir.glob("*.html"))
            for template in existing_templates:
                # Don't remove the tested templates in the separate tested directory
                if "tested templates" not in str(template):
                    print(f"  Removing {template.name}")
                    template.unlink()
            
            # Copy all templates from main directory to backup directory
            for template in main_templates:
                destination = backup_dir / template.name
                print(f"  Copying {template.name}")
                shutil.copy2(template, destination)
        else:
            print(f"\nSkipping {backup_dir} (does not exist)")
    
    print("\n✅ Template synchronization completed!")

def verify_sync():
    """Verify that all template directories have the same templates"""
    
    # Define all template directories
    template_dirs = [
        Path("templates"),
        Path("templates_14102025"),
        Path("templates_14102025/templates_14102025")
    ]
    
    print("Verifying template synchronization...")
    
    # Get templates from main directory (source of truth)
    main_templates = set([f.name for f in Path("templates").glob("*.html")])
    print(f"Main directory templates: {sorted(main_templates)}")
    
    # Check each backup directory
    for template_dir in template_dirs[1:]:  # Skip main directory
        if template_dir.exists():
            backup_templates = set([f.name for f in template_dir.glob("*.html")])
            print(f"{template_dir} templates: {sorted(backup_templates)}")
            
            # Check for differences
            missing_in_backup = main_templates - backup_templates
            extra_in_backup = backup_templates - main_templates
            
            if missing_in_backup:
                print(f"  ❌ Missing in {template_dir}: {missing_in_backup}")
            if extra_in_backup:
                print(f"  ❌ Extra in {template_dir}: {extra_in_backup}")
            
            if not missing_in_backup and not extra_in_backup:
                print(f"  ✅ {template_dir} is synchronized")
    
    print("\nVerification completed!")

def cleanup_redundant_templates():
    """Clean up redundant template copies"""
    
    # Define directories with redundant templates
    redundant_dirs = [
        Path("templates_14102025/tested templates")
    ]
    
    print("Cleaning up redundant template copies...")
    
    for redundant_dir in redundant_dirs:
        if redundant_dir.exists():
            templates = list(redundant_dir.glob("*.html"))
            print(f"\nFound {len(templates)} templates in {redundant_dir}")
            
            for template in templates:
                print(f"  Removing {template.name}")
                template.unlink()
            
            print(f"✅ Cleaned up {redundant_dir}")
    
    print("Redundant template cleanup completed!")

if __name__ == "__main__":
    print("Template Synchronization Tool")
    print("=" * 30)
    
    # Sync templates
    sync_templates()
    
    # Verify synchronization
    verify_sync()
    
    # Clean up redundant templates
    cleanup_redundant_templates()
    
    print("\n🎉 All template synchronization tasks completed!")