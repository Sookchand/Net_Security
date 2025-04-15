# PowerShell script to test deployment locally

# Define your EC2 host and key file
$EC2_HOST = "ec2-3-87-239-199.compute-1.amazonaws.com"
$KEY_FILE = "my-key-pair.pem"

Write-Host "Testing deployment to EC2 ($EC2_HOST)..." -ForegroundColor Cyan

# Deploy using the deploy.py script
Write-Host "Running deployment script..." -ForegroundColor Yellow
python deploy.py --key $KEY_FILE --host $EC2_HOST --enhanced

# Wait for the application to start
Write-Host "Waiting for application to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Test SSH connection
Write-Host "Testing SSH connection..." -ForegroundColor Yellow
ssh -i $KEY_FILE ec2-user@$EC2_HOST "echo SSH connection successful"

# Check if container is running
Write-Host "Checking if container is running..." -ForegroundColor Yellow
$containerStatus = ssh -i $KEY_FILE ec2-user@$EC2_HOST "docker ps | grep netwroksecuritytrial || echo 'Container not running'"
Write-Host "Container status: $containerStatus" -ForegroundColor Gray

if ($containerStatus -like "*Container not running*") {
    Write-Host "❌ Container is not running" -ForegroundColor Red
    Write-Host "Checking container logs:" -ForegroundColor Yellow
    ssh -i $KEY_FILE ec2-user@$EC2_HOST "docker logs netwroksecuritytrial 2>&1 || echo 'No logs available'"
    exit 1
} else {
    Write-Host "✅ Container is running" -ForegroundColor Green
}

# Test root endpoint
Write-Host "Testing root endpoint..." -ForegroundColor Yellow
# Use GET request instead of HEAD
$rootResponse = ssh -i $KEY_FILE ec2-user@$EC2_HOST "curl -s http://localhost:8000/ || echo 'Failed to connect'"
Write-Host "Root endpoint response: $rootResponse" -ForegroundColor Gray

# Check if the response contains expected content
if (($rootResponse -like "*healthy*") -or ($rootResponse -like "*Network Security API is running*")) {
    Write-Host "✅ Root endpoint check passed (received valid HTTP response)" -ForegroundColor Green
} else {
    Write-Host "❌ Root endpoint check failed" -ForegroundColor Red
    Write-Host "Checking container logs:" -ForegroundColor Yellow
    ssh -i $KEY_FILE ec2-user@$EC2_HOST "docker logs netwroksecuritytrial 2>&1 || echo 'No logs available'"
    exit 1
}

# Test health endpoint
Write-Host "Testing health endpoint..." -ForegroundColor Yellow
$healthResponse = ssh -i $KEY_FILE ec2-user@$EC2_HOST "curl -s http://localhost:8000/health || echo 'Failed to connect'"
Write-Host "Health endpoint response: $healthResponse" -ForegroundColor Gray

if ($healthResponse -like "*healthy*") {
    Write-Host "✅ Health endpoint check passed" -ForegroundColor Green
} else {
    Write-Host "❌ Health endpoint check failed" -ForegroundColor Red
    Write-Host "Checking container logs:" -ForegroundColor Yellow
    ssh -i $KEY_FILE ec2-user@$EC2_HOST "docker logs netwroksecuritytrial 2>&1 || echo 'No logs available'"
    exit 1
}

# Get public IP
$publicIP = ssh -i $KEY_FILE ec2-user@$EC2_HOST "curl -s http://checkip.amazonaws.com || echo $EC2_HOST"

# Deployment successful
Write-Host "✅ Deployment successful!" -ForegroundColor Green
Write-Host "Application is available at: http://$publicIP`:8000" -ForegroundColor Cyan
Write-Host "API documentation: http://$publicIP`:8000/docs" -ForegroundColor Cyan
