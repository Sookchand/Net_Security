"""
File listing script for the Net_Security project.

This script lists all files in the project and categorizes them by type.
"""

import os
import glob
import re
from collections import defaultdict

def get_file_extension(filename):
    """Get the file extension."""
    _, ext = os.path.splitext(filename)
    return ext.lower()

def categorize_file(filename):
    """Categorize a file based on its name and extension."""
    ext = get_file_extension(filename)
    basename = os.path.basename(filename)
    
    # Python files
    if ext == '.py':
        if basename.startswith('test_'):
            return 'Test Files'
        elif 'deploy' in basename:
            return 'Deployment Scripts'
        else:
            return 'Python Files'
    
    # Docker files
    elif basename.startswith('Dockerfile'):
        return 'Docker Files'
    
    # Requirements files
    elif basename.startswith('requirements'):
        return 'Requirements Files'
    
    # Shell scripts
    elif ext in ['.sh', '.bat', '.ps1']:
        return 'Shell Scripts'
    
    # Data files
    elif ext in ['.csv', '.json', '.yaml', '.yml']:
        return 'Data Files'
    
    # HTML/CSS/JS files
    elif ext in ['.html', '.css', '.js']:
        return 'Web Files'
    
    # Documentation
    elif ext in ['.md', '.txt', '.rst']:
        return 'Documentation'
    
    # Images
    elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
        return 'Images'
    
    # Other
    else:
        return 'Other Files'

def list_files(directory='.', ignore_dirs=None):
    """List all files in the directory and categorize them."""
    if ignore_dirs is None:
        ignore_dirs = ['.git', '__pycache__', 'venv', 'env', '.venv', '.env']
    
    categories = defaultdict(list)
    
    for root, dirs, files in os.walk(directory):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            filepath = os.path.join(root, file)
            category = categorize_file(filepath)
            categories[category].append(filepath)
    
    return categories

def main():
    """Main function to list files."""
    print("Listing files in the project...")
    
    categories = list_files()
    
    print("\nFile Categories:")
    print("=" * 80)
    
    for category, files in sorted(categories.items()):
        print(f"\n{category} ({len(files)}):")
        print("-" * 80)
        for file in sorted(files):
            print(f"  {file}")
    
    print("\nSummary:")
    print("=" * 80)
    total_files = sum(len(files) for files in categories.values())
    print(f"Total files: {total_files}")
    
    for category, files in sorted(categories.items()):
        print(f"{category}: {len(files)} files")

if __name__ == "__main__":
    main()
