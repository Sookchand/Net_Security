### Network Security Projects For Phising Data

Setup github secrets:
AWS_ACCESS_KEY_ID=

AWS_SECRET_ACCESS_KEY=

AWS_REGION = us-east-1

AWS_ECR_LOGIN_URI = 
ECR_REPOSITORY_NAME =


check for runner = ls -ld actions-runner
clear runner = rm -rf actions-runner
clear = ./config.sh remove --token AIGA35237WYC2N5ZYGWDW6LH6W2YE


key pair:
name = 
type = 
format = 

istance_url = 44.202.38.160


Docker Setup In EC2 commands to be Executed
#optinal

sudo apt-get update -y

sudo apt-get upgrade

#required

curl -fsSL https://get.docker.com -o get-docker.sh

sudo sh get-docker.sh

sudo usermod -aG docker ubuntu

newgrp docker