# EC2 Deployment Instructions

Follow these steps to deploy the updated Network Security API on your EC2 instance:

## 1. Upload the files to your EC2 instance
<!-- powershell -ExecutionPolicy Bypass -File .\upload_to_ec2.ps1 -KeyPath "my-key-pair.pem" -EC2Address "ec2-3-87-239-199.compute-1.amazonaws.com"
ssh -i my-key-pair.pem ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com
chmod +x deploy_very_simple.sh
./deploy_very_simple.sh -->

Upload the following files to your EC2 instance:
- `very_simple_app.py`
- `Dockerfile.very_simple`
- `requirements.very_simple.txt`
- `deploy_very_simple.sh`
- `sample_network_data.csv` (optional, for testing)

You can use SCP to upload the files:

```bash
scp -i my-key-pair.pem very_simple_app.py ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
scp -i my-key-pair.pem Dockerfile.very_simple ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
scp -i my-key-pair.pem requirements.very_simple.txt ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
scp -i my-key-pair.pem deploy_very_simple.sh ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
scp -i my-key-pair.pem sample_network_data.csv ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
```

## 2. SSH into your EC2 instance

```bash
ssh -i my-key-pair.pem ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com
```

## 3. Make the deployment script executable and run it

```bash
chmod +x deploy_very_simple.sh
./deploy_very_simple.sh
```

## 4. Access the application

After deployment, you can access the application at:
- http://ec2-3-87-239-199.compute-1.amazonaws.com:8000

## 5. Test the application

1. Visit the home page to see the UI with training and prediction options
2. Try the training endpoint by clicking "Start Training"
3. Upload a CSV file to test the prediction functionality
4. Check the API documentation at `/docs` endpoint

## Troubleshooting

If you encounter any issues:

1. Check the container logs:
```bash
docker logs netwroksecuritytrial
```

2. Check if the container is running:
```bash
docker ps | grep netwroksecuritytrial
```

3. If needed, restart the container:
```bash
docker restart netwroksecuritytrial
```

4. If you see any errors related to file permissions:
```bash
sudo chown -R ec2-user:ec2-user ~/templates
```

5. If the container fails to start, check for port conflicts:
```bash
sudo netstat -tulpn | grep 8000
```

6. If you need to rebuild the container:
```bash
docker build -t networksecurity-very-simple -f Dockerfile.very_simple .
docker stop netwroksecuritytrial
docker rm netwroksecuritytrial
docker run -d --name netwroksecuritytrial --restart always -p 8000:8000 networksecurity-very-simple
```
