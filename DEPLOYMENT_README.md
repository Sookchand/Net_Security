# Network Security API Deployment

This repository contains files for deploying a simplified version of the Network Security API that includes training and prediction functionality.

## Files Included

- `very_simple_app.py`: The main FastAPI application with training and prediction endpoints
- `Dockerfile.very_simple`: Docker configuration for building the container
- `requirements.very_simple.txt`: Python dependencies for the application
- `deploy_very_simple.sh`: Bash script to build and deploy the Docker container
- `sample_network_data.csv`: Sample data for testing the prediction functionality
- `upload_to_ec2.ps1`: PowerShell script for Windows users to upload files to EC2
- `EC2_DEPLOYMENT_INSTRUCTIONS.md`: Detailed instructions for deploying on EC2

## Deployment Options

### Option 1: Deploy on EC2 (Recommended)

Follow the detailed instructions in `EC2_DEPLOYMENT_INSTRUCTIONS.md`.

#### For Windows Users:

1. Open PowerShell
2. Run the upload script:
   ```powershell
   .\upload_to_ec2.ps1 -KeyPath "path\to\my-key-pair.pem" -EC2Address "ec2-3-87-239-199.compute-1.amazonaws.com"
   ```
3. SSH into your EC2 instance:
   ```powershell
   ssh -i "path\to\my-key-pair.pem" ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com
   ```
4. Run the deployment script:
   ```bash
   chmod +x deploy_very_simple.sh
   ./deploy_very_simple.sh
   ```

#### For Linux/Mac Users:

1. Upload files using SCP:
   ```bash
   scp -i my-key-pair.pem very_simple_app.py ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
   scp -i my-key-pair.pem Dockerfile.very_simple ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
   scp -i my-key-pair.pem requirements.very_simple.txt ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
   scp -i my-key-pair.pem deploy_very_simple.sh ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
   scp -i my-key-pair.pem sample_network_data.csv ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
   ```
2. SSH into your EC2 instance:
   ```bash
   ssh -i my-key-pair.pem ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com
   ```
3. Run the deployment script:
   ```bash
   chmod +x deploy_very_simple.sh
   ./deploy_very_simple.sh
   ```

### Option 2: Deploy Locally with Docker

If you have Docker installed on your local machine, you can deploy the application locally:

```bash
# Build the Docker image
docker build -t networksecurity-very-simple -f Dockerfile.very_simple .

# Run the container
docker run -d --name netwroksecuritytrial --restart always -p 8000:8000 networksecurity-very-simple

# Check if the container is running
docker ps | grep netwroksecuritytrial
```

Access the application at http://localhost:8000

## Using the Application

1. Open the application in your web browser
2. Use the "Train Model" button to simulate training
3. Use the "Make Predictions" form to upload a CSV file and get predictions
4. View the API documentation at the `/docs` endpoint

## Troubleshooting

See the "Troubleshooting" section in `EC2_DEPLOYMENT_INSTRUCTIONS.md` for common issues and solutions.
