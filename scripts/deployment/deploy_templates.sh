#!/bin/bash
# Script to deploy the application with templates

echo "Deploying Network Security AI Platform with Templates..."

# Stop and remove existing container if it exists
echo "Stopping existing container..."
docker stop netwroksecuritytrial 2>/dev/null || true
docker rm netwroksecuritytrial 2>/dev/null || true

# Build the Docker image
echo "Building Docker image..."
docker build -t netwroksecuritytrial:latest -f Dockerfile.templates .

# Run the container
echo "Starting container..."
docker run -d --name netwroksecuritytrial -p 8000:8000 netwroksecuritytrial:latest

# Check if the container is running
docker ps | grep netwroksecuritytrial

# Wait for the application to start
echo "Waiting for the application to start..."
sleep 10

# Check if the application is responding
echo "Checking if the application is responding..."
# Use GET request instead of HEAD
ROOT_RESPONSE=$(curl -s --connect-timeout 5 http://localhost:8000/ || echo "Connection failed")
echo "Root endpoint response: $ROOT_RESPONSE"

# Check if the response contains expected content
if [[ "$ROOT_RESPONSE" == *"Network Security AI"* ]]; then
    echo "✅ Root endpoint check passed (received valid response)"
else
    echo "❌ Root endpoint check failed"
    echo "The application may still be starting up. Check the logs:"
    docker logs netwroksecuritytrial
fi

# Check health endpoint
echo "Checking health endpoint..."
HEALTH_RESPONSE=$(curl -s --connect-timeout 5 http://localhost:8000/health || echo "Connection failed")
echo "Health endpoint response: $HEALTH_RESPONSE"

if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
    echo "✅ Health endpoint check passed"
else
    echo "❌ Health endpoint check failed"
    echo "The application may still be starting up. Check the logs:"
    docker logs netwroksecuritytrial
fi

echo "Network Security AI Platform deployed! Access it at http://localhost:8000 or http://$(curl -s http://checkip.amazonaws.com):8000"
