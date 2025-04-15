#!/bin/bash
# Script to deploy the application without DagsHub authentication

echo "Deploying Network Security API (No Auth Version)..."

# Stop and remove existing container if it exists
echo "Stopping existing container..."
docker stop netwroksecuritytrial 2>/dev/null || true
docker rm netwroksecuritytrial 2>/dev/null || true

# Build the Docker image
echo "Building Docker image..."
docker build -t netwroksecuritytrial:latest -f Dockerfile.no_auth .

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
# Use curl with -I to get headers and check for 307 redirect
ROOT_RESPONSE=$(curl -s -I --connect-timeout 5 http://localhost:8000/ || echo "Connection failed")
echo "Root endpoint response headers: $ROOT_RESPONSE"

# Check for either a 200 OK or a 307 redirect (both indicate the app is running)
if [[ "$ROOT_RESPONSE" == *"200 OK"* ]] || [[ "$ROOT_RESPONSE" == *"307 Temporary Redirect"* ]]; then
    echo "✅ Root endpoint check passed (received valid HTTP response)"
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

echo "Network Security API (No Auth Version) deployed! Access it at http://localhost:8000 or http://$(curl -s http://checkip.amazonaws.com):8000"
