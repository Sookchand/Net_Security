# Simple script to check EC2 application status

# Define your EC2 host and key file
$EC2_HOST = "ec2-3-87-239-199.compute-1.amazonaws.com"
$KEY_FILE = "my-key-pair.pem"

Write-Host "Checking application on $EC2_HOST..." -ForegroundColor Cyan

# Test SSH connection
Write-Host "Testing SSH connection..." -ForegroundColor Yellow
try {
    $sshResult = ssh -i $KEY_FILE ec2-user@$EC2_HOST "echo SSH connection successful"
    Write-Host $sshResult -ForegroundColor Green
} catch {
    Write-Host "SSH connection failed: $_" -ForegroundColor Red
    exit 1
}

# Check if container is running
Write-Host "Checking if container is running..." -ForegroundColor Yellow
try {
    $containerStatus = ssh -i $KEY_FILE ec2-user@$EC2_HOST "docker ps | grep netwroksecuritytrial || echo 'Container not running'"
    Write-Host "Container status: $containerStatus" -ForegroundColor Gray
    
    if ($containerStatus -like "*Container not running*") {
        Write-Host "❌ Container is not running" -ForegroundColor Red
        exit 1
    } else {
        Write-Host "✅ Container is running" -ForegroundColor Green
    }
} catch {
    Write-Host "Failed to check container status: $_" -ForegroundColor Red
    exit 1
}

# Test health endpoint
Write-Host "Testing health endpoint..." -ForegroundColor Yellow
try {
    $healthResponse = ssh -i $KEY_FILE ec2-user@$EC2_HOST "curl -s http://localhost:8000/health || echo 'Failed to connect'"
    Write-Host "Health endpoint response: $healthResponse" -ForegroundColor Gray
    
    if ($healthResponse -like "*healthy*") {
        Write-Host "✅ Health endpoint check passed" -ForegroundColor Green
    } else {
        Write-Host "❌ Health endpoint check failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Failed to check health endpoint: $_" -ForegroundColor Red
    exit 1
}

# Get public IP
try {
    $publicIP = ssh -i $KEY_FILE ec2-user@$EC2_HOST "curl -s http://checkip.amazonaws.com || echo $EC2_HOST"
    
    # Deployment successful
    Write-Host "✅ Application is running successfully!" -ForegroundColor Green
    Write-Host "Application is available at: http://$publicIP`:8000" -ForegroundColor Cyan
    Write-Host "API documentation: http://$publicIP`:8000/docs" -ForegroundColor Cyan
} catch {
    Write-Host "Failed to get public IP: $_" -ForegroundColor Red
    exit 1
}
