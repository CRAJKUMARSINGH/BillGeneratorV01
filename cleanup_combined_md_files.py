#!/usr/bin/env python3
"""
Script to clean up redundant .md files after combining them into a single comprehensive document.
"""

import os
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup_combined_md.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Files that should be preserved (essential files)
ESSENTIAL_MD_FILES = {
    'README.md',  # Main project documentation
    'ALL_TEMPLATES_IMPLEMENTATION.md',  # Implementation summary
    'COMBINED_PROJECT_DOCUMENTATION.md',  # Combined documentation
    'FINAL_COMBINED_DOCUMENTATION_SUMMARY.md',  # Final summary
    'REDUNDANT_MD_CLEANUP_REPORT.md',  # Cleanup report
}

# Directories to exclude from cleanup (we want to be more specific about what to clean)
EXCLUDED_DIRECTORIES = {
    '.venv',  # Virtual environment
    '.git',   # Git directory
    '__pycache__',  # Python cache
}

def is_essential_file(file_path: Path) -> bool:
    """
    Check if a file is essential and should not be removed.
    
    Args:
        file_path (Path): Path to the file
        
    Returns:
        bool: True if file is essential, False otherwise
    """
    file_name = file_path.name
    
    # Check if it's in the essential files list
    if file_name in ESSENTIAL_MD_FILES:
        return True
    
    # Check if it's in an excluded directory
    for excluded_dir in EXCLUDED_DIRECTORIES:
        if excluded_dir in file_path.parts:
            return True
    
    # Preserve files in test_suite directory
    if 'test_suite' in file_path.parts:
        return True
        
    # Preserve files in backup_md_files directory (they were already processed)
    if 'backup_md_files' in file_path.parts:
        return True
        
    # Preserve files in Attached_Assets_Dont_Delete directory
    if 'Attached_Assets_Dont_Delete' in file_path.parts:
        return True
        
    return False

def find_md_files(root_dir: str = '.') -> list:
    """
    Find all .md files in the project directory and subdirectories.
    
    Args:
        root_dir (str): Root directory to search
        
    Returns:
        list: List of paths to .md files
    """
    md_files = []
    root_path = Path(root_dir)
    
    try:
        for md_file in root_path.rglob("*.md"):
            # Skip excluded directories
            if not any(excluded_dir in md_file.parts for excluded_dir in EXCLUDED_DIRECTORIES):
                md_files.append(md_file)
    except Exception as e:
        logger.error(f"Error finding .md files: {e}")
    
    return md_files

def create_backup(file_path: Path, backup_dir: Path) -> bool:
    """
    Create a backup of a file before deletion.
    
    Args:
        file_path (Path): Path to the file to backup
        backup_dir (Path): Directory to store backups
        
    Returns:
        bool: True if backup successful, False otherwise
    """
    try:
        # Create backup directory if it doesn't exist
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create backup file path
        backup_path = backup_dir / file_path.name
        
        # Handle name conflicts
        counter = 1
        original_backup_path = backup_path
        while backup_path.exists():
            backup_path = original_backup_path.parent / f"{original_backup_path.stem}_{counter}{original_backup_path.suffix}"
            counter += 1
        
        # Copy file to backup location
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create backup for {file_path}: {e}")
        return False

def remove_redundant_files(md_files: list, create_backups: bool = True) -> bool:
    """
    Remove redundant .md files after creating backups.
    
    Args:
        md_files (list): List of .md files to evaluate
        create_backups (bool): Whether to create backups before deletion
        
    Returns:
        bool: True if operation successful, False otherwise
    """
    # Create backup directory
    backup_dir = Path('backup_combined_md_files')
    if create_backups:
        backup_dir.mkdir(exist_ok=True)
        logger.info(f"Created backup directory: {backup_dir}")
    
    # Identify redundant files (not essential)
    redundant_files = [f for f in md_files if not is_essential_file(f)]
    
    if not redundant_files:
        logger.info("No redundant files to remove")
        return True
    
    logger.info(f"Found {len(redundant_files)} redundant files to remove")
    
    # Remove files
    removed_count = 0
    failed_count = 0
    
    for file_path in redundant_files:
        try:
            # Create backup if requested
            if create_backups:
                if not create_backup(file_path, backup_dir):
                    logger.warning(f"Skipping deletion of {file_path} due to backup failure")
                    failed_count += 1
                    continue
            
            # Remove the file
            file_path.unlink()
            logger.info(f"Removed redundant file: {file_path}")
            removed_count += 1
        except Exception as e:
            logger.error(f"Failed to remove {file_path}: {e}")
            failed_count += 1
    
    logger.info(f"Removed {removed_count} redundant files, {failed_count} failed")
    return failed_count == 0

def main():
    """Main function to orchestrate the cleanup process."""
    logger.info("Starting combined .md files cleanup process")
    
    # Step 1: Find all .md files
    logger.info("Finding all .md files...")
    md_files = find_md_files()
    logger.info(f"Found {len(md_files)} .md files")
    
    # Log all files found
    essential_files = []
    redundant_files = []
    
    for file_path in md_files:
        if is_essential_file(file_path):
            essential_files.append(file_path)
            logger.info(f"  ESSENTIAL: {file_path}")
        else:
            redundant_files.append(file_path)
            logger.info(f"  REDUNDANT: {file_path}")
    
    logger.info(f"Essential files: {len(essential_files)}")
    logger.info(f"Redundant files: {len(redundant_files)}")
    
    # Step 2: Remove redundant files
    logger.info("Removing redundant files...")
    if not remove_redundant_files(md_files, create_backups=True):
        logger.error("Failed to remove some redundant files")
        return False
    
    logger.info("Cleanup process completed successfully")
    return True

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)