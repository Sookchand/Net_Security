# PowerShell script to test deployment locally

Write-Host "Testing deployment to EC2..." -ForegroundColor Cyan

# Deploy using the deploy.py script
Write-Host "Running deployment script..." -ForegroundColor Yellow
python deploy.py --key my-key-pair.pem --host ec2-3-87-239-199.compute-1.amazonaws.com --enhanced

# Wait for the application to start
Write-Host "Waiting for application to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Test SSH connection
Write-Host "Testing SSH connection..." -ForegroundColor Yellow
ssh -i my-key-pair.pem ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com "echo SSH connection successful"

# Check if container is running
Write-Host "Checking if container is running..." -ForegroundColor Yellow
$containerStatus = ssh -i my-key-pair.pem ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com "docker ps | grep netwroksecuritytrial || echo 'Container not running'"
Write-Host "Container status: $containerStatus" -ForegroundColor Gray

if ($containerStatus -like "*Container not running*") {
    Write-Host "❌ Container is not running" -ForegroundColor Red
    Write-Host "Checking container logs:" -ForegroundColor Yellow
    ssh -i my-key-pair.pem ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com "docker logs netwroksecuritytrial 2>&1 || echo 'No logs available'"
    exit 1
} else {
    Write-Host "✅ Container is running" -ForegroundColor Green
}

# Test root endpoint
Write-Host "Testing root endpoint..." -ForegroundColor Yellow
$rootResponse = ssh -i my-key-pair.pem ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com "curl -s http://localhost:8000/ || echo 'Failed to connect'"
Write-Host "Root endpoint response: $rootResponse" -ForegroundColor Gray

if ($rootResponse -like "*Network Security API is running*") {
    Write-Host "✅ Root endpoint check passed" -ForegroundColor Green
} else {
    Write-Host "❌ Root endpoint check failed" -ForegroundColor Red
    Write-Host "Checking container logs:" -ForegroundColor Yellow
    ssh -i my-key-pair.pem ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com "docker logs netwroksecuritytrial 2>&1 || echo 'No logs available'"
    exit 1
}

# Test health endpoint
Write-Host "Testing health endpoint..." -ForegroundColor Yellow
$healthResponse = ssh -i my-key-pair.pem ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com "curl -s http://localhost:8000/health || echo 'Failed to connect'"
Write-Host "Health endpoint response: $healthResponse" -ForegroundColor Gray

if ($healthResponse -like "*healthy*") {
    Write-Host "✅ Health endpoint check passed" -ForegroundColor Green
} else {
    Write-Host "❌ Health endpoint check failed" -ForegroundColor Red
    Write-Host "Checking container logs:" -ForegroundColor Yellow
    ssh -i my-key-pair.pem ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com "docker logs netwroksecuritytrial 2>&1 || echo 'No logs available'"
    exit 1
}

# Get public IP
$publicIP = ssh -i my-key-pair.pem ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com "curl -s http://checkip.amazonaws.com || echo ec2-3-87-239-199.compute-1.amazonaws.com"

# Deployment successful
Write-Host "✅ Deployment successful!" -ForegroundColor Green
Write-Host "Application is available at: http://$publicIP`:8000" -ForegroundColor Cyan
Write-Host "API documentation: http://$publicIP`:8000/docs" -ForegroundColor Cyan
