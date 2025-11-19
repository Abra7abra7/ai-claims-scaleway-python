#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Scaleway AI Claims Setup ===${NC}"

# Check if scw is installed
if ! command -v scw &> /dev/null; then
    echo "Scaleway CLI (scw) is not installed."
    echo "Please install it: https://github.com/scaleway/scaleway-cli"
    echo "Or configure your .env file manually."
    exit 1
fi

# Check if logged in
scw account project list &> /dev/null
if [ $? -ne 0 ]; then
    echo "Please run 'scw init' to login first."
    exit 1
fi

# 1. Create Object Storage Bucket
BUCKET_NAME="ai-claims-$(date +%s)"
REGION="fr-par"

echo -e "\n${GREEN}1. Creating Object Storage Bucket: $BUCKET_NAME ($REGION)...${NC}"
scw s3 bucket create name=$BUCKET_NAME region=$REGION

# 2. Get Credentials (User needs to provide these or we guide them)
echo -e "\n${BLUE}=== Configuration ===${NC}"
echo "We have created the bucket: $BUCKET_NAME"
echo ""
echo "To finish setup, you need your Scaleway Access Key and Secret Key."
echo "You can generate them here: https://console.scaleway.com/iam/api-keys"
echo ""

# 3. Update .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

# Ask for keys
read -p "Enter Scaleway Access Key: " SCW_ACCESS_KEY
read -p "Enter Scaleway Secret Key: " SCW_SECRET_KEY
read -p "Enter Mistral API Key: " MISTRAL_API_KEY

# Update .env file (using sed for simplicity, careful with special chars)
# MacOS sed requires '' after -i
sed -i '' "s/S3_BUCKET_NAME=.*/S3_BUCKET_NAME=$BUCKET_NAME/" .env
sed -i '' "s/S3_ACCESS_KEY=.*/S3_ACCESS_KEY=$SCW_ACCESS_KEY/" .env
sed -i '' "s/S3_SECRET_KEY=.*/S3_SECRET_KEY=$SCW_SECRET_KEY/" .env
sed -i '' "s/MISTRAL_API_KEY=.*/MISTRAL_API_KEY=$MISTRAL_API_KEY/" .env

echo -e "\n${GREEN}Success! .env file updated.${NC}"
echo "You can now run 'make up' to start the application."
