# EnergyOpti-Pro API Keys Setup Guide
Write-Host "🔑 EnergyOpti-Pro API Keys Setup Guide" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

Write-Host "`n📋 Required API Keys and Values:" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Generate JWT Secret Key
$jwtSecret = python -c "import secrets; print(secrets.token_urlsafe(32))"
Write-Host "`n1. JWT_SECRET_KEY (Generated):" -ForegroundColor Yellow
Write-Host "   Value: $jwtSecret" -ForegroundColor White
Write-Host "   Status: ✅ READY TO USE" -ForegroundColor Green

Write-Host "`n2. DATABASE_URL (Render PostgreSQL):" -ForegroundColor Yellow
Write-Host "   Format: postgresql://username:password@host:port/database" -ForegroundColor White
Write-Host "   How to get: Create PostgreSQL service on Render" -ForegroundColor Gray
Write-Host "   Status: ⏳ WILL GET FROM RENDER" -ForegroundColor Yellow

Write-Host "`n3. REDIS_URL (Render Redis):" -ForegroundColor Yellow
Write-Host "   Format: redis://username:password@host:port/database" -ForegroundColor White
Write-Host "   How to get: Create Redis service on Render" -ForegroundColor Gray
Write-Host "   Status: ⏳ WILL GET FROM RENDER" -ForegroundColor Yellow

Write-Host "`n4. OPENWEATHER_API_KEY (Weather Data):" -ForegroundColor Yellow
Write-Host "   Website: https://openweathermap.org/api" -ForegroundColor White
Write-Host "   Cost: FREE (1,000 calls/day)" -ForegroundColor Green
Write-Host "   Time to get: 2 minutes" -ForegroundColor Green
Write-Host "   Status: 🔗 GET NOW" -ForegroundColor Cyan

Write-Host "`n5. CME_API_KEY (Energy Trading):" -ForegroundColor Yellow
Write-Host "   Website: https://www.cmegroup.com/api/" -ForegroundColor White
Write-Host "   Cost: Varies (Professional)" -ForegroundColor Yellow
Write-Host "   Time to get: 1-2 weeks (approval required)" -ForegroundColor Yellow
Write-Host "   Status: ⚠️ OPTIONAL (app has fallbacks)" -ForegroundColor Yellow

Write-Host "`n6. ICE_API_KEY (Intercontinental Exchange):" -ForegroundColor Yellow
Write-Host "   Website: https://www.theice.com/api" -ForegroundColor White
Write-Host "   Cost: Varies (Professional)" -ForegroundColor Yellow
Write-Host "   Time to get: 1-2 weeks (approval required)" -ForegroundColor Yellow
Write-Host "   Status: ⚠️ OPTIONAL (app has fallbacks)" -ForegroundColor Yellow

Write-Host "`n7. NYMEX_API_KEY (Natural Gas & Oil):" -ForegroundColor Yellow
Write-Host "   Website: https://www.cmegroup.com/markets/energy/" -ForegroundColor White
Write-Host "   Cost: Varies (Professional)" -ForegroundColor Yellow
Write-Host "   Time to get: 1-2 weeks (approval required)" -ForegroundColor Yellow
Write-Host "   Status: ⚠️ OPTIONAL (app has fallbacks)" -ForegroundColor Yellow

Write-Host "`n🎯 Quick Start Recommendations:" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

Write-Host "`n✅ IMMEDIATE (Required for deployment):" -ForegroundColor Green
Write-Host "   - JWT_SECRET_KEY: $jwtSecret" -ForegroundColor White
Write-Host "   - DATABASE_URL: Get from Render" -ForegroundColor White
Write-Host "   - REDIS_URL: Get from Render" -ForegroundColor White

Write-Host "`n🔗 EASY (Get in 2 minutes):" -ForegroundColor Cyan
Write-Host "   - OPENWEATHER_API_KEY: https://openweathermap.org/api" -ForegroundColor White

Write-Host "`n⚠️ OPTIONAL (Professional APIs):" -ForegroundColor Yellow
Write-Host "   - CME_API_KEY, ICE_API_KEY, NYMEX_API_KEY" -ForegroundColor White
Write-Host "   - Your app works without these (uses simulated data)" -ForegroundColor Gray

Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "=============" -ForegroundColor Cyan
Write-Host "1. Deploy to Render (get DATABASE_URL and REDIS_URL)" -ForegroundColor White
Write-Host "2. Get OpenWeather API key (optional but recommended)" -ForegroundColor White
Write-Host "3. Professional API keys (optional, for real market data)" -ForegroundColor White

Write-Host "`n💡 Pro Tip: Your app works perfectly with simulated data!" -ForegroundColor Green
Write-Host "   You can deploy and test everything without professional API keys." -ForegroundColor Gray
