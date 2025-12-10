# ==============================================
# VIEW LOGS
# ==============================================

param(
    [string]$Service = ""
)

Write-Host "`n📋 Viewing logs...`n" -ForegroundColor Cyan

if ($Service -eq "") {
    Write-Host "Showing ALL services (Ctrl+C to exit)" -ForegroundColor Gray
    docker compose logs -f
} else {
    Write-Host "Showing $Service logs (Ctrl+C to exit)" -ForegroundColor Gray
    docker compose logs -f $Service
}

