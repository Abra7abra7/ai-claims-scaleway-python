# ==============================================
# STOP ALL SERVICES
# ==============================================

Write-Host ""
Write-Host "[STOP] Stopping all services..." -ForegroundColor Yellow
Write-Host ""

docker compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[OK] All services stopped" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] Error stopping services" -ForegroundColor Red
    Write-Host ""
    exit 1
}
