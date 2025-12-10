# ==============================================
# CHECK STATUS OF ALL SERVICES
# ==============================================

Write-Host "`n📊 Container Status:`n" -ForegroundColor Cyan

docker compose ps

Write-Host "`n💡 Tips:" -ForegroundColor Yellow
Write-Host "  .\logs.ps1 frontend    - Frontend logs" -ForegroundColor Gray
Write-Host "  .\logs.ps1 backend     - Backend logs" -ForegroundColor Gray
Write-Host "  .\logs.ps1             - All logs`n" -ForegroundColor Gray

