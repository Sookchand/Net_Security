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

echo "Enhanced application deployed! Access it at http://localhost:8000 or http://$(curl -s http://checkip.amazonaws.com):8000"


# python deploy.py --key my-key-pair.pem --host ec2-3-87-239-199.compute-1.amazonaws.com --enhanced