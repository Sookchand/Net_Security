import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from networksecurity.logging.logger import logging

class S3Sync:
    def sync_folder_to_s3(self, folder: str, aws_bucket_url: str):
        """
        Sync a local folder to an S3 bucket.

        Args:
            folder (str): Local folder path.
            aws_bucket_url (str): S3 bucket URL.

        Raises:
            Exception: If the sync fails.
        """
        try:
            logging.info(f"Starting S3 sync for folder: {folder} to bucket: {aws_bucket_url}")
            s3_client = boto3.client('s3')
            bucket_name = aws_bucket_url.split('/')[2]
            prefix = '/'.join(aws_bucket_url.split('/')[3:])

            for root, dirs, files in os.walk(folder):
                for file in files:
                    local_path = os.path.join(root, file)
                    s3_path = os.path.join(prefix, os.path.relpath(local_path, folder))
                    logging.info(f"Uploading {local_path} to s3://{bucket_name}/{s3_path}")
                    s3_client.upload_file(local_path, bucket_name, s3_path)

            logging.info("S3 sync completed successfully.")
        except NoCredentialsError:
            logging.error("AWS credentials not found.")
            raise
        except PartialCredentialsError:
            logging.error("Incomplete AWS credentials provided.")
            raise
        except Exception as e:
            logging.error(f"Error during S3 sync: {e}")
            raise

    def sync_folder_from_s3(self, folder, aws_bucket_url):
        command = f"aws s3 sync  {aws_bucket_url} {folder} "
        os.system(command)
