#!/usr/bin/env python3
"""
Script to inventory all .md files in the project and categorize them.
"""

import os
from pathlib import Path

def categorize_md_files():
    """Categorize all .md files in the project."""
    # Find all .md files
    md_files = list(Path('.').rglob('*.md'))
    
    # Categorize files
    project_docs = []
    backup_files = []
    test_files = []
    third_party = []
    output_files = []
    
    for file_path in md_files:
        path_str = str(file_path)
        
        # Skip virtual environment and git files
        if '.venv' in path_str or '.git' in path_str:
            third_party.append(file_path)
        elif 'test_suite' in path_str:
            test_files.append(file_path)
        elif 'backup_md_files' in path_str or 'backup_combined_md_files' in path_str:
            backup_files.append(file_path)
        elif 'OUTPUT_FILES' in path_str:
            output_files.append(file_path)
        elif 'Attached_Assets_Dont_Delete' in path_str:
            backup_files.append(file_path)
        else:
            project_docs.append(file_path)
    
    return {
        'project_docs': project_docs,
        'backup_files': backup_files,
        'test_files': test_files,
        'third_party': third_party,
        'output_files': output_files
    }

def main():
    """Main function to display the inventory."""
    print("=" * 60)
    print("BILL GENERATOR PROJECT - MARKDOWN FILE INVENTORY")
    print("=" * 60)
    
    categories = categorize_md_files()
    
    # Display project documentation files (main focus)
    print(f"\n📚 PROJECT DOCUMENTATION FILES ({len(categories['project_docs'])} files):")
    print("-" * 40)
    for file_path in sorted(categories['project_docs']):
        print(f"  • {file_path}")
    
    # Display test files
    print(f"\n🧪 TEST SUITE DOCUMENTATION ({len(categories['test_files'])} files):")
    print("-" * 40)
    for file_path in sorted(categories['test_files']):
        print(f"  • {file_path}")
    
    # Display backup files
    print(f"\n💾 BACKUP FILES ({len(categories['backup_files'])} files):")
    print("-" * 40)
    for file_path in sorted(categories['backup_files']):
        print(f"  • {file_path}")
    
    # Display output files
    print(f"\n📄 OUTPUT FILES ({len(categories['output_files'])} files):")
    print("-" * 40)
    for file_path in sorted(categories['output_files']):
        print(f"  • {file_path}")
    
    # Display third-party files count
    print(f"\n📦 THIRD-PARTY DOCUMENTATION ({len(categories['third_party'])} files in .venv)")
    print("-" * 40)
    print("  • Various README.md and LICENSE.md files in virtual environment")
    
    # Summary
    total_files = sum(len(files) for files in categories.values())
    print(f"\n" + "=" * 60)
    print(f"TOTAL MARKDOWN FILES: {total_files}")
    print(f"PROJECT-SPECIFIC FILES: {len(categories['project_docs']) + len(categories['test_files']) + len(categories['backup_files']) + len(categories['output_files'])}")
    print("=" * 60)

if __name__ == "__main__":
    main()