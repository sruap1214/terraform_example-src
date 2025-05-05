#!/bin/bash
yum update -y

# Install Git
yum install git -y

# Install curl
yum install curl -y

# Install uv 
sudo -u ec2-user -i -- bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'

# Clone repository
git clone https://github.com/sruap1214/terraform_example-src.git
cd terraform_example-src/
uv sync