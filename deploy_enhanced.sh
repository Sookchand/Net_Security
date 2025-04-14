#!/bin/bash

# Build the Docker image
docker build -t networksecurity-enhanced -f Dockerfile.enhanced .

# Stop and remove the existing container if it exists
docker stop netwroksecuritytrial || true
docker rm netwroksecuritytrial || true

# Run the new container
docker run -d \
  --name netwroksecuritytrial \
  --restart always \
  -p 8000:8000 \
  networksecurity-enhanced

# Check if the container is running
docker ps | grep netwroksecuritytrial

echo "Enhanced application deployed! Access it at http://localhost:8000 or http://$(curl -s http://checkip.amazonaws.com):8000"


# python deploy.py --key my-key-pair.pem --host ec2-3-87-239-199.compute-1.amazonaws.com --enhanced