# ==============================================
# STOP ALL SERVICES
# ==============================================

Write-Host "`n🛑 Stopping all services...`n" -ForegroundColor Yellow

docker compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ All services stopped`n" -ForegroundColor Green
} else {
    Write-Host "`n❌ Error stopping services`n" -ForegroundColor Red
    exit 1
}

