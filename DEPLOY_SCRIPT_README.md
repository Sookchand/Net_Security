# Network Security API Deployment Script

This repository includes a Python script (`deploy.py`) that automates the deployment of the Network Security API to an EC2 instance.

## Prerequisites

- Python 3.6 or higher
- SSH client installed on your machine
- EC2 instance with Docker installed
- EC2 key pair (.pem file)

## Usage

### Basic Usage

```bash
python deploy.py --key my-key-pair.pem --host ec2-3-87-239-199.compute-1.amazonaws.com
```

### All Options

```bash
python deploy.py --key my-key-pair.pem --host ec2-3-87-239-199.compute-1.amazonaws.com --user ec2-user --port 22 --skip-upload
```

### Parameters

- `--key` or `-k`: Path to your EC2 key pair PEM file (required)
- `--host` or `-H`: EC2 instance hostname or IP address (required)
- `--user` or `-u`: EC2 instance username (default: ec2-user)
- `--port` or `-p`: SSH port (default: 22)
- `--skip-upload`: Skip file upload and only run deployment

## What the Script Does

1. **Validates** the key file and fixes permissions if needed
2. **Uploads** the necessary files to your EC2 instance:
   - very_simple_app.py
   - Dockerfile.very_simple
   - requirements.very_simple.txt
   - deploy_very_simple.sh
   - sample_network_data.csv
3. **Deploys** the application by:
   - Making the deployment script executable
   - Running the deployment script
4. **Verifies** the deployment by:
   - Checking if the container is running
   - Providing the URL to access the application

## Example Output

```
=== Uploading Files ===
Running: scp -i "my-key-pair.pem" -P 22 very_simple_app.py ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
Successfully uploaded very_simple_app.py
Running: scp -i "my-key-pair.pem" -P 22 Dockerfile.very_simple ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
Successfully uploaded Dockerfile.very_simple
Running: scp -i "my-key-pair.pem" -P 22 requirements.very_simple.txt ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
Successfully uploaded requirements.very_simple.txt
Running: scp -i "my-key-pair.pem" -P 22 deploy_very_simple.sh ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
Successfully uploaded deploy_very_simple.sh
Running: scp -i "my-key-pair.pem" -P 22 sample_network_data.csv ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
Successfully uploaded sample_network_data.csv

=== Deploying Application ===
Running: ssh -i "my-key-pair.pem" -p 22 ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com "chmod +x ~/deploy_very_simple.sh"
Running: ssh -i "my-key-pair.pem" -p 22 ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com "cd ~/ && ./deploy_very_simple.sh"
Deployment script executed successfully

=== Checking Application ===
Waiting for the application to start...
Container is running!

=== Application Deployed Successfully ===
You can access the application at:
http://3.87.239.199:8000
API documentation: http://3.87.239.199:8000/docs
```

## Troubleshooting

If you encounter any issues:

1. **Permission denied errors**:
   - Make sure your key file has the correct permissions (chmod 600 my-key-pair.pem)
   - Verify that you're using the correct username for your EC2 instance

2. **Connection timeout**:
   - Check that your EC2 instance is running
   - Verify that your security group allows SSH connections on port 22

3. **Deployment failures**:
   - SSH into your EC2 instance and check the Docker logs:
     ```bash
     ssh -i my-key-pair.pem ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com
     docker logs netwroksecuritytrial
     ```
