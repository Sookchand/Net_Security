"""
Cleanup script for the Net_Security project.

This script helps organize the project by moving files to their appropriate locations
and removing unnecessary files.
"""

import os
import shutil
import glob
import re

def create_directory(directory):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def move_file(source, destination):
    """Move a file from source to destination."""
    if os.path.exists(source):
        # Create the destination directory if it doesn't exist
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        # Move the file
        shutil.copy2(source, destination)
        print(f"Moved: {source} -> {destination}")
        return True
    else:
        print(f"File not found: {source}")
        return False

def main():
    """Main function to clean up the project."""
    print("Starting project cleanup...")
    
    # Create the new directory structure
    directories = [
        "data/raw",
        "data/processed",
        "models/baseline",
        "models/current",
        "scripts/deployment",
        "scripts/testing",
        "docs",
        "tests"
    ]
    
    for directory in directories:
        create_directory(directory)
    
    # Move data files
    data_files = glob.glob("Network_Data/*")
    for file in data_files:
        move_file(file, f"data/raw/{os.path.basename(file)}")
    
    valid_data_files = glob.glob("valid_data/*")
    for file in valid_data_files:
        move_file(file, f"data/processed/{os.path.basename(file)}")
    
    # Move model files
    model_files = glob.glob("final_model/*")
    for file in model_files:
        move_file(file, f"models/baseline/{os.path.basename(file)}")
    
    # Move deployment scripts
    deployment_scripts = [
        "deploy.py",
        "deploy_templates.sh",
        "check_app.sh"
    ]
    
    for script in deployment_scripts:
        move_file(script, f"scripts/deployment/{script}")
    
    # Move testing scripts
    testing_scripts = [
        "test_deployment.ps1"
    ]
    
    for script in testing_scripts:
        move_file(script, f"scripts/testing/{script}")
    
    print("\nCleanup completed successfully!")
    print("\nNext steps:")
    print("1. Review the new directory structure")
    print("2. Update import paths in Python files")
    print("3. Test the application with the new structure")
    print("4. Remove unnecessary files")

if __name__ == "__main__":
    main()
