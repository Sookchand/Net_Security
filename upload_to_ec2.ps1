# PowerShell script to upload files to EC2 instance
# Usage: .\upload_to_ec2.ps1 -KeyPath "path\to\my-key-pair.pem" -EC2Address "ec2-3-87-239-199.compute-1.amazonaws.com"

param (
    [Parameter(Mandatory=$true)]
    [string]$KeyPath,
    
    [Parameter(Mandatory=$true)]
    [string]$EC2Address
)

# Ensure the key file exists
if (-not (Test-Path $KeyPath)) {
    Write-Error "Key file not found at $KeyPath"
    exit 1
}

# Function to upload a file using SCP
function Upload-File {
    param (
        [string]$SourceFile,
        [string]$DestinationPath
    )
    
    if (-not (Test-Path $SourceFile)) {
        Write-Warning "Source file not found: $SourceFile"
        return
    }
    
    Write-Host "Uploading $SourceFile to $DestinationPath..."
    
    # Use scp to upload the file
    # Note: This requires OpenSSH to be installed on Windows
    scp -i $KeyPath $SourceFile $DestinationPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully uploaded $SourceFile" -ForegroundColor Green
    } else {
        Write-Host "Failed to upload $SourceFile" -ForegroundColor Red
    }
}

# Files to upload
$files = @(
    "very_simple_app.py",
    "Dockerfile.very_simple",
    "requirements.very_simple.txt",
    "deploy_very_simple.sh",
    "sample_network_data.csv"
)

# Upload each file
foreach ($file in $files) {
    $destinationPath = "ec2-user@${EC2Address}:~/"
    Upload-File -SourceFile $file -DestinationPath $destinationPath
}

Write-Host "`nAll files uploaded. Now connect to your EC2 instance and run the deployment script:" -ForegroundColor Cyan
Write-Host "ssh -i $KeyPath ec2-user@$EC2Address" -ForegroundColor Yellow
Write-Host "chmod +x deploy_very_simple.sh" -ForegroundColor Yellow
Write-Host "./deploy_very_simple.sh" -ForegroundColor Yellow
