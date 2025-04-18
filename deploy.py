#!/usr/bin/env python3
"""
Automated deployment script for Network Security API
This script automates the process of uploading files to an EC2 instance and deploying the application.
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path

# Files to upload - Basic version
BASIC_FILES = [
    "very_simple_app.py",
    "Dockerfile.very_simple",
    "requirements.very_simple.txt",
    "deploy_very_simple.sh",
    "sample_network_data.csv"
]

# Files to upload - Enhanced version
ENHANCED_FILES = [
    "enhanced_very_simple_app.py",
    "Dockerfile.enhanced",
    "requirements.very_simple.txt",  # Same requirements file
    "deploy_enhanced.sh",
    "sample_network_data.csv"
]

# Files to upload - Templates version
TEMPLATES_FILES = [
    "enhanced_app_with_templates.py",
    "Dockerfile.templates",
    "requirements.templates.txt",
    "deploy_templates.sh",
    "sample_network_data.csv"
]

# Directory to upload - Templates version
TEMPLATES_DIRS = [
    "app"
]

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Deploy Network Security API to EC2")
    parser.add_argument("--key", "-k", required=True, help="Path to the EC2 key pair PEM file")
    parser.add_argument("--host", "-H", required=True, help="EC2 instance hostname or IP address")
    parser.add_argument("--user", "-u", default="ec2-user", help="EC2 instance username (default: ec2-user)")
    parser.add_argument("--port", "-p", default=22, type=int, help="SSH port (default: 22)")
    parser.add_argument("--skip-upload", action="store_true", help="Skip file upload and only run deployment")
    parser.add_argument("--enhanced", "-e", action="store_true", help="Deploy the enhanced version with advanced visualizations")
    parser.add_argument("--templates", "-t", action="store_true", help="Deploy the templates version with full web interface")
    return parser.parse_args()

def check_key_file(key_path):
    """Check if the key file exists and has correct permissions."""
    key_file = Path(key_path)
    if not key_file.exists():
        print(f"Error: Key file not found at {key_path}")
        return False

    # Check if the key file has the correct permissions (Windows doesn't care as much about this)
    if os.name != 'nt':  # Not Windows
        try:
            # Check if the key file has permissions that are too open
            stat_info = os.stat(key_path)
            if stat_info.st_mode & 0o077:
                print(f"Warning: Key file {key_path} has too open permissions.")
                print("Attempting to fix permissions...")
                os.chmod(key_path, 0o600)
                print("Permissions updated.")
        except Exception as e:
            print(f"Warning: Could not check/fix key file permissions: {e}")

    return True

def run_command(command, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except subprocess.CalledProcessError as e:
        return False, str(e)

def upload_files(args):
    """Upload files to the EC2 instance."""
    print("\n=== Uploading Files ===")

    # Determine which files to upload based on the flags
    if args.templates:
        files_to_upload = TEMPLATES_FILES
        print("Using templates version of the application with full web interface")
    elif args.enhanced:
        files_to_upload = ENHANCED_FILES
        print("Using enhanced version of the application")
    else:
        files_to_upload = BASIC_FILES
        print("Using basic version of the application")

    # Upload individual files
    for file_name in files_to_upload:
        if not os.path.exists(file_name):
            print(f"Warning: File {file_name} not found, skipping...")
            continue

        # Construct the scp command
        scp_command = f'scp -i "{args.key}" -P {args.port} {file_name} {args.user}@{args.host}:~/'

        # Run the command
        success, output = run_command(scp_command)
        if success:
            print(f"Successfully uploaded {file_name}")
        else:
            print(f"Failed to upload {file_name}: {output}")
            return False

    # Upload directories for templates version
    if args.templates:
        for dir_name in TEMPLATES_DIRS:
            if not os.path.exists(dir_name):
                print(f"Warning: Directory {dir_name} not found, skipping...")
                continue

            # Create the directory on the remote server
            mkdir_command = f'ssh -i "{args.key}" -p {args.port} {args.user}@{args.host} "mkdir -p ~/{dir_name}"'
            success, output = run_command(mkdir_command)
            if not success:
                print(f"Failed to create directory {dir_name} on remote server: {output}")
                return False

            # Construct the scp command to recursively copy the directory
            scp_command = f'scp -i "{args.key}" -P {args.port} -r {dir_name}/* {args.user}@{args.host}:~/{dir_name}/'

            # Run the command
            success, output = run_command(scp_command)
            if success:
                print(f"Successfully uploaded directory {dir_name}")
            else:
                print(f"Failed to upload directory {dir_name}: {output}")
                return False

    return True

def deploy_application(args):
    """Deploy the application on the EC2 instance."""
    print("\n=== Deploying Application ===")

    # Determine which deployment script to use based on the flags
    if args.templates:
        deploy_script = "deploy_templates.sh"
    elif args.enhanced:
        deploy_script = "deploy_enhanced.sh"
    else:
        deploy_script = "deploy_very_simple.sh"

    # Construct the SSH command to make the deployment script executable
    chmod_command = f'ssh -i "{args.key}" -p {args.port} {args.user}@{args.host} "chmod +x ~/{deploy_script}"'

    # Run the command
    success, output = run_command(chmod_command)
    if not success:
        print(f"Failed to make deployment script executable: {output}")
        return False

    # Construct the SSH command to run the deployment script
    deploy_command = f'ssh -i "{args.key}" -p {args.port} {args.user}@{args.host} "cd ~/ && ./{deploy_script}"'

    # Run the command
    success, output = run_command(deploy_command)
    if success:
        print("Deployment script executed successfully")
        print(output)
        return True
    else:
        print(f"Failed to run deployment script: {output}")
        return False

def check_application(args):
    """Check if the application is running."""
    print("\n=== Checking Application ===")

    # Wait a bit for the application to start
    print("Waiting for the application to start...")
    time.sleep(10)  # Increased wait time to ensure application is fully started

    # Construct the SSH command to check if the container is running
    check_command = f'ssh -i "{args.key}" -p {args.port} {args.user}@{args.host} "docker ps | grep netwroksecuritytrial"'

    # Run the command
    success, output = run_command(check_command, check=False)
    if success and output.strip():
        print("Container is running!")

        # Get the public IP address
        ip_command = f'ssh -i "{args.key}" -p {args.port} {args.user}@{args.host} "curl -s http://checkip.amazonaws.com"'
        success, ip_output = run_command(ip_command, check=False)

        public_ip = ip_output.strip() if success and ip_output.strip() else args.host

        # Check if the root endpoint is working
        root_check_command = f'ssh -i "{args.key}" -p {args.port} {args.user}@{args.host} "curl -s http://localhost:8000/"'
        success, root_output = run_command(root_check_command, check=False)

        if args.templates:
            # For templates version, check for HTML content
            if success and ("<html" in root_output or "Network Security AI" in root_output):
                print("✅ Root endpoint check passed")
            else:
                print("❌ Root endpoint check failed")
                print(f"Response: {root_output if success else 'No response'}")
                print("The application may not be fully initialized yet. Try accessing it manually.")
        else:
            # For basic and enhanced versions, check for API response
            if success and "Network Security API is running" in root_output:
                print("✅ Root endpoint check passed")
            else:
                print("❌ Root endpoint check failed")
                print(f"Response: {root_output if success else 'No response'}")
                print("The application may not be fully initialized yet. Try accessing it manually.")

        # Check if the health endpoint is working
        health_check_command = f'ssh -i "{args.key}" -p {args.port} {args.user}@{args.host} "curl -s http://localhost:8000/health"'
        success, health_output = run_command(health_check_command, check=False)

        if success and "healthy" in health_output:
            print("✅ Health endpoint check passed")
        else:
            print("❌ Health endpoint check failed")
            print(f"Response: {health_output if success else 'No response'}")

        print(f"\n=== Application Deployed Successfully ===")
        print(f"You can access the application at:")
        print(f"http://{public_ip}:8000")
        print(f"API documentation: http://{public_ip}:8000/docs")

        return True
    else:
        print("Container does not appear to be running.")
        print("Check the logs for more information:")
        print(f'ssh -i "{args.key}" -p {args.port} {args.user}@{args.host} "docker logs netwroksecuritytrial"')
        return False

def main():
    """Main function."""
    args = parse_arguments()

    # Check if the key file exists and has correct permissions
    if not check_key_file(args.key):
        sys.exit(1)

    # Upload files if not skipped
    if not args.skip_upload:
        if not upload_files(args):
            print("File upload failed. Aborting deployment.")
            sys.exit(1)
    else:
        print("Skipping file upload as requested.")

    # Deploy the application
    if not deploy_application(args):
        print("Deployment failed.")
        sys.exit(1)

    # Check if the application is running
    if not check_application(args):
        print("Application check failed.")
        sys.exit(1)

    # Print a message about the enhanced features if using the enhanced version
    if args.templates:
        print("\n=== Templates Features ===")
        print("The templates version includes:")
        print("  - Full web interface with multiple pages")
        print("  - Interactive visualizations (pie charts, bar charts, radar charts)")
        print("  - Email and text analysis for security threats")
        print("  - System architecture visualization")
        print("  - Responsive design with modern UI")
        print("\nExplore the different pages to see all the features!")
    elif args.enhanced:
        print("\n=== Enhanced Features ===")
        print("The enhanced version includes:")
        print("  - Interactive pie and bar charts")
        print("  - Filtering options for attack types")
        print("  - Export functionality (CSV and Print)")
        print("  - Improved styling and layout")
        print("\nTry uploading a CSV file to see the advanced visualizations!")

if __name__ == "__main__":
    main()
