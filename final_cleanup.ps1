# Final Repository Cleanup Script - ACTUAL REMOVAL
Write-Host "🚀 Executing final repository cleanup..." -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Yellow

# Files to actually remove
$files_to_remove = @(
    "backend/app/main_clean.py",
    "backend/app/main_simple.py", 
    "backend/app/main_refactored.py",
    "backend/main.py",
    "frontend/src/App.js",
    "frontend/src/App.jsx",
    "frontend/src/components/TradingDashboard.jsx",
    "frontend/src/components/MarketOverview.jsx",
    "frontend/src/components/ESGScore.jsx"
)

$removed = 0
$failed = 0

foreach ($file in $files_to_remove) {
    if (Test-Path $file) {
        try {
            Remove-Item $file -Force
            Write-Host "✅ Removed: $file" -ForegroundColor Green
            $removed++
        }
        catch {
            Write-Host "❌ Failed to remove: $file" -ForegroundColor Red
            $failed++
        }
    } else {
        Write-Host "⚠️  Not found: $file" -ForegroundColor Yellow
    }
}

Write-Host "=" * 60 -ForegroundColor Yellow
Write-Host "🎉 Final cleanup completed!" -ForegroundColor Green
Write-Host "✅ Files removed: $removed" -ForegroundColor Green
Write-Host "❌ Failed removals: $failed" -ForegroundColor Red
Write-Host "=" * 60 -ForegroundColor Yellow
