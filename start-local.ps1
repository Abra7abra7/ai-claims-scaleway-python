# ==============================================
# START LOCAL DEVELOPMENT ENVIRONMENT
# ==============================================

Write-Host "`n🏠 Starting LOCAL development environment...`n" -ForegroundColor Cyan

# Check if .env.local exists
if (-not (Test-Path .env.local)) {
    Write-Host "⚠️  .env.local not found!" -ForegroundColor Yellow
    
    if (Test-Path .env.example) {
        Write-Host "📝 Copying from .env.example..." -ForegroundColor Yellow
        Copy-Item .env.example .env.local
        Write-Host "`n✅ Created .env.local" -ForegroundColor Green
        Write-Host "⚠️  IMPORTANT: Edit .env.local with your API keys!`n" -ForegroundColor Yellow
        Write-Host "   1. Open .env.local in editor" -ForegroundColor Gray
        Write-Host "   2. Add your GEMINI_API_KEY or MISTRAL_API_KEY" -ForegroundColor Gray
        Write-Host "   3. Run this script again`n" -ForegroundColor Gray
        exit 1
    } else {
        Write-Host "❌ .env.example not found!" -ForegroundColor Red
        exit 1
    }
}

# Copy .env.local to .env
Write-Host "📋 Using .env.local configuration..." -ForegroundColor Gray
Copy-Item .env.local .env -Force

# Start services
Write-Host "🐳 Starting Docker services...`n" -ForegroundColor Cyan
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Local environment started successfully!`n" -ForegroundColor Green
    
    Write-Host "🌐 URLs:" -ForegroundColor Green
    Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
    Write-Host "  API Docs:  http://localhost:8000/api/v1/docs" -ForegroundColor White
    Write-Host "  MinIO UI:  http://localhost:9001 (admin/minioadmin123)`n" -ForegroundColor White
    
    Write-Host "💡 Useful commands:" -ForegroundColor Yellow
    Write-Host "  .\logs.ps1           - View logs" -ForegroundColor Gray
    Write-Host "  .\stop.ps1           - Stop services" -ForegroundColor Gray
    Write-Host "  docker compose ps    - Check status`n" -ForegroundColor Gray
} else {
    Write-Host "`n❌ Failed to start services!" -ForegroundColor Red
    Write-Host "Run: docker compose logs" -ForegroundColor Yellow
    exit 1
}
