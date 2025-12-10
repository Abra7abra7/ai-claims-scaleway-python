# ==============================================
# CHECK STATUS OF ALL SERVICES
# ==============================================

Write-Host ""
Write-Host "[STATUS] Container Status:" -ForegroundColor Cyan
Write-Host ""

docker compose ps

Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "  .\logs.ps1 frontend    - Frontend logs" -ForegroundColor Gray
Write-Host "  .\logs.ps1 backend     - Backend logs" -ForegroundColor Gray
Write-Host "  .\logs.ps1             - All logs" -ForegroundColor Gray
Write-Host ""
