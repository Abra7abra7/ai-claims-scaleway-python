#!/bin/bash
set -e

cd /opt/ai-claims
git pull origin main
docker compose pull
docker compose up -d --build

echo "✅ Application updated"


