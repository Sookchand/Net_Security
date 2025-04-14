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

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Deploy Network Security API to EC2")
    parser.add_argument("--key", "-k", required=True, help="Path to the EC2 key pair PEM file")
    parser.add_argument("--host", "-H", required=True, help="EC2 instance hostname or IP address")
    parser.add_argument("--user", "-u", default="ec2-user", help="EC2 instance username (default: ec2-user)")
    parser.add_argument("--port", "-p", default=22, type=int, help="SSH port (default: 22)")
    parser.add_argument("--skip-upload", action="store_true", help="Skip file upload and only run deployment")
    parser.add_argument("--enhanced", "-e", action="store_true", help="Deploy the enhanced version with advanced visualizations")
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

    # Determine which files to upload based on the --enhanced flag
    files_to_upload = ENHANCED_FILES if args.enhanced else BASIC_FILES
    print(f"Using {'enhanced' if args.enhanced else 'basic'} version of the application")

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

    return True

def deploy_application(args):
    """Deploy the application on the EC2 instance."""
    print("\n=== Deploying Application ===")

    # Determine which deployment script to use based on the --enhanced flag
    deploy_script = "deploy_enhanced.sh" if args.enhanced else "deploy_very_simple.sh"

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
    time.sleep(5)

    # Construct the SSH command to check if the container is running
    check_command = f'ssh -i "{args.key}" -p {args.port} {args.user}@{args.host} "docker ps | grep netwroksecuritytrial"'

    # Run the command
    success, output = run_command(check_command, check=False)
    if success and output.strip():
        print("Container is running!")

        # Get the public IP address
        ip_command = f'ssh -i "{args.key}" -p {args.port} {args.user}@{args.host} "curl -s http://checkip.amazonaws.com"'
        success, ip_output = run_command(ip_command, check=False)

        if success and ip_output.strip():
            public_ip = ip_output.strip()
            print(f"\n=== Application Deployed Successfully ===")
            print(f"You can access the application at:")
            print(f"http://{public_ip}:8000")
            print(f"API documentation: http://{public_ip}:8000/docs")
        else:
            print(f"\n=== Application Deployed Successfully ===")
            print(f"You can access the application at:")
            print(f"http://{args.host}:8000")
            print(f"API documentation: http://{args.host}:8000/docs")

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
    check_application(args)

    # Print a message about the enhanced features if using the enhanced version
    if args.enhanced:
        print("\n=== Enhanced Features ===")
        print("The enhanced version includes:")
        print("  - Interactive pie and bar charts")
        print("  - Filtering options for attack types")
        print("  - Export functionality (CSV and Print)")
        print("  - Improved styling and layout")
        print("\nTry uploading a CSV file to see the advanced visualizations!")

if __name__ == "__main__":
    main()
