#!/bin/bash
# Script to check if the application is running properly on the EC2 instance

echo "Checking if the application is running properly..."

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

# Check if the container is running
CONTAINER_STATUS=$(docker ps | grep netwroksecuritytrial || echo "Container not running")
echo "Container status: $CONTAINER_STATUS"

if [[ "$CONTAINER_STATUS" == *"Container not running"* ]]; then
    echo "❌ Container is not running"
    echo "Checking if container exists but is stopped:"
    docker ps -a | grep netwroksecuritytrial || echo "Container does not exist"
    exit 1
else
    echo "✅ Container is running"
fi

# Check root endpoint
echo "Testing root endpoint..."
# Use GET request instead of HEAD
ROOT_RESPONSE=$(curl -s --connect-timeout 5 http://localhost:8000/ || echo "Connection failed")
echo "Root endpoint response: $ROOT_RESPONSE"

# Check if the response contains expected content
if [[ "$ROOT_RESPONSE" == *"healthy"* ]] || [[ "$ROOT_RESPONSE" == *"Network Security API is running"* ]]; then
    echo "✅ Root endpoint check passed (received valid response)"
else
    echo "❌ Root endpoint check failed"
    echo "Checking container logs:"
    docker logs netwroksecuritytrial
    exit 1
fi

# Check health endpoint
echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s --connect-timeout 5 http://localhost:8000/health || echo "Connection failed")
echo "Health endpoint response: $HEALTH_RESPONSE"

if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
    echo "✅ Health endpoint check passed"
else
    echo "❌ Health endpoint check failed"
    echo "Checking container logs:"
    docker logs netwroksecuritytrial
    exit 1
fi

# Get public IP
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com || echo "localhost")

# All checks passed
echo "✅ All checks passed! The application is running properly."
echo "Application is available at: http://$PUBLIC_IP:8000"
echo "API documentation: http://$PUBLIC_IP:8000/docs"
