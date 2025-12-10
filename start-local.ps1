# ==============================================
# START LOCAL DEVELOPMENT ENVIRONMENT
# ==============================================

Write-Host ""
Write-Host "[LOCAL] Starting LOCAL development environment..." -ForegroundColor Cyan
Write-Host ""

# Check if .env.local exists
if (-not (Test-Path .env.local)) {
    Write-Host "[!] .env.local not found!" -ForegroundColor Yellow
    
    if (Test-Path .env.example) {
        Write-Host "[*] Copying from .env.example..." -ForegroundColor Yellow
        Copy-Item .env.example .env.local
        Write-Host ""
        Write-Host "[OK] Created .env.local" -ForegroundColor Green
        Write-Host "[!] IMPORTANT: Edit .env.local with your API keys!" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   1. Open .env.local in editor" -ForegroundColor Gray
        Write-Host "   2. Add your MISTRAL_API_KEY (GDPR compliant)" -ForegroundColor Gray
        Write-Host "   3. Run this script again" -ForegroundColor Gray
        Write-Host ""
        exit 1
    } else {
        Write-Host "[ERROR] .env.example not found!" -ForegroundColor Red
        exit 1
    }
}

# Copy .env.local to .env
Write-Host "[*] Using .env.local configuration..." -ForegroundColor Gray
Copy-Item .env.local .env -Force

# Start services
Write-Host "[DOCKER] Starting Docker services..." -ForegroundColor Cyan
Write-Host ""
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[OK] Local environment started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "URLs:" -ForegroundColor Green
    Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
    Write-Host "  API Docs:  http://localhost:8000/api/v1/docs" -ForegroundColor White
    Write-Host "  pgAdmin:   http://localhost:5050 (admin@admin.com / admin123)" -ForegroundColor White
    Write-Host "  MinIO UI:  http://localhost:9001 (minioadmin / minioadmin123)" -ForegroundColor White
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor Yellow
    Write-Host "  .\logs.ps1           - View logs" -ForegroundColor Gray
    Write-Host "  .\stop.ps1           - Stop services" -ForegroundColor Gray
    Write-Host "  docker compose ps    - Check status" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] Failed to start services!" -ForegroundColor Red
    Write-Host "Run: docker compose logs" -ForegroundColor Yellow
    exit 1
}
