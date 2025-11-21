#!/bin/bash
set -e

cd /opt/ai-claims

# Clone repository
if [ -d ".git" ]; then
    git pull origin main
else
    git clone https://github.com/Abra7abra7/ai-claims-scaleway-python.git .
fi

# Setup environment
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env file with your credentials"
    exit 1
fi

# Pull and start services
docker compose pull
docker compose up -d

# Wait for services
sleep 10

# Run migrations
docker compose exec -T backend python scripts/migrate_db.py

echo "✅ Application deployed"
echo "Frontend: http://$(curl -s ifconfig.me):8501"
echo "Backend: http://$(curl -s ifconfig.me):8000"


