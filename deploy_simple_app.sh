#!/bin/bash

# Build the Docker image
docker build -t networksecurity-simple -f Dockerfile.simple .

# Stop and remove the existing container if it exists
docker stop netwroksecuritytrial || true
docker rm netwroksecuritytrial || true

# Run the new container
docker run -d \
  --name netwroksecuritytrial \
  --restart always \
  -p 8000:8000 \
  networksecurity-simple

# Check if the container is running
docker ps | grep netwroksecuritytrial

echo "Application deployed! Access it at http://localhost:8000 or http://$(curl -s http://checkip.amazonaws.com):8000"
