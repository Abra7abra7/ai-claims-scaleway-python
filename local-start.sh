#!/bin/bash
# Local development startup script

set -e

echo "🚀 Starting AI Claims Processing System (Local Dev)"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file with required environment variables"
    exit 1
fi

# Stop existing containers
echo "📦 Stopping existing containers..."
docker compose down

# Build images
echo "🔨 Building Docker images..."
docker compose build --no-cache presidio

# Start services
echo "▶️  Starting services..."
docker compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check service health
echo ""
echo "🔍 Checking service health..."
echo "================================"

# Check Redis
if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: OK"
else
    echo "❌ Redis: FAILED"
fi

# Check Backend
if curl -f http://localhost:8000/claims/ > /dev/null 2>&1; then
    echo "✅ Backend: OK"
else
    echo "⚠️  Backend: Not responding (may still be starting)"
fi

# Check Presidio
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Presidio: OK"
else
    echo "⚠️  Presidio: Not responding (may still be starting)"
fi

echo ""
echo "================================"
echo "📊 Container Status:"
docker compose ps

echo ""
echo "================================"
echo "🌐 Access URLs:"
echo "Frontend:  http://localhost:8501"
echo "Backend:   http://localhost:8000"
echo "Presidio:  http://localhost:8001"
echo ""
echo "📝 View logs: docker compose logs -f"
echo "🛑 Stop all:  docker compose down"
echo "================================"

