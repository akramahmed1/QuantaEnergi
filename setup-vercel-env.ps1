# EnergyOpti-Pro Vercel Environment Variables Setup
Write-Host "🔧 Setting up Vercel Environment Variables..." -ForegroundColor Green

Write-Host "`n📋 Required Environment Variables for Vercel:" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

$envVars = @{
    "VITE_API_URL" = "https://energyopti-pro-backend.onrender.com"
    "VITE_WS_URL" = "wss://energyopti-pro-backend.onrender.com/ws"
    "VITE_ENVIRONMENT" = "production"
    "VITE_APP_NAME" = "EnergyOpti-Pro"
    "VITE_APP_VERSION" = "2.0.0"
}

Write-Host "`n🔑 Copy and paste these into your Vercel Environment Variables:" -ForegroundColor Yellow
Write-Host "===============================================================" -ForegroundColor Yellow

foreach ($key in $envVars.Keys) {
    Write-Host "`nVariable Name: $key" -ForegroundColor Green
    Write-Host "Value: $($envVars[$key])" -ForegroundColor White
    Write-Host "---" -ForegroundColor Gray
}

Write-Host "`n📝 Instructions:" -ForegroundColor Cyan
Write-Host "1. Go to your Vercel project dashboard" -ForegroundColor White
Write-Host "2. Click 'Settings' tab" -ForegroundColor White
Write-Host "3. Click 'Environment Variables' in left sidebar" -ForegroundColor White
Write-Host "4. Click 'Add New' for each variable above" -ForegroundColor White
Write-Host "5. Select all environments (Production, Preview, Development)" -ForegroundColor White
Write-Host "6. Click 'Save' after each variable" -ForegroundColor White

Write-Host "`n🌐 After setting variables, redeploy your project:" -ForegroundColor Yellow
Write-Host "1. Go to 'Deployments' tab" -ForegroundColor White
Write-Host "2. Click 'Redeploy' on your latest deployment" -ForegroundColor White

Write-Host "`n✅ Your Vercel frontend will then connect to your backend!" -ForegroundColor Green
