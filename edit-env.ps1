# ==============================================
# EDIT ENVIRONMENT FILES
# ==============================================

param(
    [string]$Environment = "local"
)

if ($Environment -eq "local") {
    $file = ".env.local"
} elseif ($Environment -eq "prod" -or $Environment -eq "production") {
    $file = ".env.production"
} else {
    Write-Host "[ERROR] Invalid environment: $Environment" -ForegroundColor Red
    Write-Host "Usage: .\edit-env.ps1 [local|prod]" -ForegroundColor Yellow
    exit 1
}

if (Test-Path $file) {
    Write-Host ""
    Write-Host "[*] Opening $file in Notepad..." -ForegroundColor Cyan
    Write-Host ""
    notepad $file
} else {
    Write-Host ""
    Write-Host "[!] $file not found!" -ForegroundColor Yellow
    Write-Host "Creating from template..." -ForegroundColor Gray
    Copy-Item .env.example $file
    Write-Host "[OK] Created $file" -ForegroundColor Green
    Write-Host "Opening in Notepad..." -ForegroundColor Cyan
    Write-Host ""
    notepad $file
}
