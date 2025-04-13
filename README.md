# Network Security Project For Phishing Data

## AWS Configuration

### GitHub Secrets
```bash
AWS_ACCESS_KEY_ID=<your_access_key>
AWS_SECRET_ACCESS_KEY=<your_secret_key>
AWS_REGION=us-east-1
AWS_ECR_LOGIN_URI=<your_ecr_uri>
ECR_REPOSITORY_NAME=<your_repository_name>
```

### EC2 Instance Details
```yaml
Instance ID: i-09fdca77840b2442a
Public DNS: ec2-3-87-239-199.compute-1.amazonaws.com
Status: running
Availability Zone: us-east-1b
Access URL: http://ec2-3-87-239-199.compute-1.amazonaws.com:8000/docs
```

### GitHub Runner Management
```bash
# Check existing runner
ls -ld actions-runner

# Remove runner
rm -rf actions-runner

# Remove runner configuration
./config.sh remove --token AIGA35237WYC2N5ZYGWDW6LH6W2YE
```

### EC2 SSH Key Details
```yaml
Key Pair:
  Name: my-key-pair
  Type: RSA
  Format: PEM
```

## Docker Setup on EC2

### Optional Updates
```bash
# Update package list
sudo apt-get update -y

# Upgrade installed packages
sudo apt-get upgrade
```

### Required Docker Installation
```bash
# Download Docker installation script
curl -fsSL https://get.docker.com -o get-docker.sh

# Install Docker
sudo sh get-docker.sh

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Activate new group membership
newgrp docker
```

## Instance Status Commands
```bash
# List EC2 instances
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,PublicDnsName,State.Name]' --output table

# Check instance status
aws ec2 describe-instance-status --instance-ids i-09fdca77840b2442a
```

<!-- check for runner = ls -ld actions-runner
clear runner = rm -rf actions-runner
clear = ./config.sh remove --token AIGA35237WYC2N5ZYGWDW6LH6W2YE


key pair:
name = 
type = 
format = 


Docker Setup In EC2 commands to be Executed
#optinal

sudo apt-get update -y

sudo apt-get upgrade

#required

curl -fsSL https://get.docker.com -o get-docker.sh

sudo sh get-docker.sh

sudo usermod -aG docker ubuntu

newgrp docker -->