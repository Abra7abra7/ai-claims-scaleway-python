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
    Write-Host "❌ Invalid environment: $Environment" -ForegroundColor Red
    Write-Host "Usage: .\edit-env.ps1 [local|prod]" -ForegroundColor Yellow
    exit 1
}

if (Test-Path $file) {
    Write-Host "📝 Opening $file in Notepad...`n" -ForegroundColor Cyan
    notepad $file
} else {
    Write-Host "⚠️  $file not found!" -ForegroundColor Yellow
    Write-Host "Creating from template...`n" -ForegroundColor Gray
    Copy-Item .env.example $file
    Write-Host "✅ Created $file" -ForegroundColor Green
    Write-Host "Opening in Notepad...`n" -ForegroundColor Cyan
    notepad $file
}

