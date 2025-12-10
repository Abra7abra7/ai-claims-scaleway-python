# ==============================================
# START PRODUCTION ENVIRONMENT
# ==============================================

Write-Host ""
Write-Host "[PROD] Starting PRODUCTION environment..." -ForegroundColor Cyan
Write-Host ""

# Check if .env.production exists
if (-not (Test-Path .env.production)) {
    Write-Host "[ERROR] .env.production not found!" -ForegroundColor Red
    
    if (Test-Path .env.example) {
        Write-Host "[*] Creating from template..." -ForegroundColor Yellow
        Copy-Item .env.example .env.production
        Write-Host ""
        Write-Host "[!] IMPORTANT: Edit .env.production with PRODUCTION credentials!" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   1. Open .env.production in editor" -ForegroundColor Gray
        Write-Host "   2. Change ENVIRONMENT=production" -ForegroundColor Gray
        Write-Host "   3. Set production URLs (https://ai-claims.novis.eu)" -ForegroundColor Gray
        Write-Host "   4. Add STRONG secrets and passwords" -ForegroundColor Gray
        Write-Host "   5. Add real SMTP credentials" -ForegroundColor Gray
        Write-Host "   6. Run this script again" -ForegroundColor Gray
        Write-Host ""
        
        # Open in notepad
        Write-Host "[*] Opening .env.production in notepad..." -ForegroundColor Cyan
        notepad .env.production
        exit 1
    } else {
        Write-Host "[ERROR] .env.example not found!" -ForegroundColor Red
        exit 1
    }
}

# Copy .env.production to .env
Write-Host "[*] Using .env.production configuration..." -ForegroundColor Gray
Copy-Item .env.production .env -Force

# Verify it's production environment
$envContent = Get-Content .env.production -Raw
if ($envContent -notmatch "ENVIRONMENT=production") {
    Write-Host ""
    Write-Host "[!] WARNING: ENVIRONMENT is not set to 'production' in .env.production!" -ForegroundColor Yellow
    $confirm = Read-Host "Continue anyway? (y/N)"
    if ($confirm -ne 'y') {
        exit 1
    }
}

# Start services
Write-Host "[DOCKER] Starting Docker services (production mode)..." -ForegroundColor Cyan
Write-Host ""
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[OK] Production environment started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "[*] Checking status..." -ForegroundColor Cyan
    docker compose ps
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
