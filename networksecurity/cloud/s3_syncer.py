import os
import logging
import subprocess

class S3Sync:
    def sync_folder_to_s3(self, folder, aws_bucket_url):
        try:
            logging.info(f"Starting sync from local folder '{folder}' to S3 bucket '{aws_bucket_url}'")
            
            # Check if folder exists
            if not os.path.exists(folder):
                logging.error(f"Local folder does not exist: {folder}")
                return False
                
            # List directory contents
            contents = os.listdir(folder)
            logging.info(f"Contents of folder to sync: {contents}")
            
            # Construct and execute AWS CLI command
            command = f"aws s3 sync {folder} {aws_bucket_url}"
            logging.info(f"Executing command: {command}")
            
            # Use subprocess instead of os.system for better error handling
            process = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if process.returncode == 0:
                logging.info(f"Successfully synced folder '{folder}' to '{aws_bucket_url}'")
                logging.info(f"Output: {process.stdout}")
                return True
            else:
                logging.error(f"Failed to sync folder. Error: {process.stderr}")
                return False
                
        except Exception as e:
            logging.error(f"Error during S3 sync: {str(e)}")
            return False
