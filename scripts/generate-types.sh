#!/bin/bash
# Generate TypeScript types from OpenAPI
# Run this script after modifying backend API schemas
#
# Usage: 
#   ./scripts/generate-types.sh
#   ./scripts/generate-types.sh --watch
#
# Or from frontend directory:
#   npm run generate-types

set -e

WATCH=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --watch|-w)
            WATCH=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🔄 Generating TypeScript types from OpenAPI..."

# Check if backend is running
if ! curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "❌ Backend is not running! Start it with: docker compose up -d backend"
    exit 1
fi

echo "✅ Backend is healthy"

# Generate types
cd frontend
npm run generate-types

if [ $? -eq 0 ]; then
    echo "✅ Types generated successfully!"
    echo "📁 Output: frontend/src/lib/api-types.ts"
else
    echo "❌ Type generation failed!"
    exit 1
fi

if [ "$WATCH" = true ]; then
    echo ""
    echo "👀 Watching for backend changes..."
    echo "Press Ctrl+C to stop"
    npm run types:watch
fi

