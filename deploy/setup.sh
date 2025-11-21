#!/bin/bash
set -e

echo "🚀 AI Claims Scaleway Deployment Setup"

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
apt-get install -y docker-compose-plugin

# Install Git
apt-get install -y git curl

# Create app directory
mkdir -p /opt/ai-claims
cd /opt/ai-claims

echo "✅ System setup complete"


