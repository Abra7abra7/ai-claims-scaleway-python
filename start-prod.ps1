# ==============================================
# START PRODUCTION ENVIRONMENT
# ==============================================

Write-Host "`n🌍 Starting PRODUCTION environment...`n" -ForegroundColor Cyan

# Check if .env.production exists
if (-not (Test-Path .env.production)) {
    Write-Host "❌ .env.production not found!" -ForegroundColor Red
    
    if (Test-Path .env.example) {
        Write-Host "📝 Creating from template..." -ForegroundColor Yellow
        Copy-Item .env.example .env.production
        Write-Host "`n⚠️  IMPORTANT: Edit .env.production with PRODUCTION credentials!`n" -ForegroundColor Yellow
        Write-Host "   1. Open .env.production in editor" -ForegroundColor Gray
        Write-Host "   2. Change ENVIRONMENT=production" -ForegroundColor Gray
        Write-Host "   3. Set production URLs (https://ai-claims.novis.eu)" -ForegroundColor Gray
        Write-Host "   4. Add STRONG secrets and passwords" -ForegroundColor Gray
        Write-Host "   5. Add real SMTP credentials" -ForegroundColor Gray
        Write-Host "   6. Run this script again`n" -ForegroundColor Gray
        
        # Open in notepad
        Write-Host "💡 Opening .env.production in notepad..." -ForegroundColor Cyan
        notepad .env.production
        exit 1
    } else {
        Write-Host "❌ .env.example not found!" -ForegroundColor Red
        exit 1
    }
}

# Copy .env.production to .env
Write-Host "📋 Using .env.production configuration..." -ForegroundColor Gray
Copy-Item .env.production .env -Force

# Verify it's production environment
$envContent = Get-Content .env.production -Raw
if ($envContent -notmatch "ENVIRONMENT=production") {
    Write-Host "`n⚠️  WARNING: ENVIRONMENT is not set to 'production' in .env.production!" -ForegroundColor Yellow
    $confirm = Read-Host "Continue anyway? (y/N)"
    if ($confirm -ne 'y') {
        exit 1
    }
}

# Start services
Write-Host "🐳 Starting Docker services (production mode)...`n" -ForegroundColor Cyan
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Production environment started successfully!`n" -ForegroundColor Green
    
    Write-Host "📊 Checking status..." -ForegroundColor Cyan
    docker compose ps
    
    Write-Host "`n💡 Useful commands:" -ForegroundColor Yellow
    Write-Host "  .\logs.ps1           - View logs" -ForegroundColor Gray
    Write-Host "  .\stop.ps1           - Stop services" -ForegroundColor Gray
    Write-Host "  docker compose ps    - Check status`n" -ForegroundColor Gray
} else {
    Write-Host "`n❌ Failed to start services!" -ForegroundColor Red
    Write-Host "Run: docker compose logs" -ForegroundColor Yellow
    exit 1
}

