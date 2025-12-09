# Generate TypeScript types from OpenAPI
# Run this script after modifying backend API schemas
#
# Usage: 
#   .\scripts\generate-types.ps1
#
# Or from frontend directory:
#   npm run generate-types

param(
    [switch]$Watch = $false
)

$ErrorActionPreference = "Stop"

Write-Host "🔄 Generating TypeScript types from OpenAPI..." -ForegroundColor Cyan

# Check if backend is running
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" -Method Get -ErrorAction Stop
    Write-Host "✅ Backend is healthy: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend is not running! Start it with: docker compose up -d backend" -ForegroundColor Red
    exit 1
}

# Generate types
Push-Location .\frontend
try {
    npm run generate-types
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Types generated successfully!" -ForegroundColor Green
        Write-Host "📁 Output: frontend/src/lib/api-types.ts" -ForegroundColor Gray
    } else {
        Write-Host "❌ Type generation failed!" -ForegroundColor Red
        exit 1
    }
} finally {
    Pop-Location
}

if ($Watch) {
    Write-Host "`n👀 Watching for backend changes..." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
    
    Push-Location .\frontend
    try {
        npm run types:watch
    } finally {
        Pop-Location
    }
}

