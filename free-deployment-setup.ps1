# EnergyOpti-Pro Free Deployment Setup
Write-Host "🆓 EnergyOpti-Pro Free Deployment Setup" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

Write-Host "`n💰 100% FREE Deployment - No Paid APIs Needed!" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Generate JWT Secret Key
$jwtSecret = python -c "import secrets; print(secrets.token_urlsafe(32))"

Write-Host "`n🔑 Generated Values for Free Deployment:" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow

Write-Host "`n1. JWT_SECRET_KEY (Generated):" -ForegroundColor Green
Write-Host "   $jwtSecret" -ForegroundColor White

Write-Host "`n2. Professional API Keys (Use these placeholder values):" -ForegroundColor Green
Write-Host "   CME_API_KEY=demo_key" -ForegroundColor White
Write-Host "   ICE_API_KEY=demo_key" -ForegroundColor White
Write-Host "   NYMEX_API_KEY=demo_key" -ForegroundColor White

Write-Host "`n3. Optional: OpenWeather API (FREE - 1,000 calls/day):" -ForegroundColor Cyan
Write-Host "   Get from: https://openweathermap.org/api" -ForegroundColor White
Write-Host "   Cost: FREE" -ForegroundColor Green

Write-Host "`n4. Database & Redis URLs (Will get from Render):" -ForegroundColor Yellow
Write-Host "   DATABASE_URL=postgresql://username:password@host:port/database" -ForegroundColor White
Write-Host "   REDIS_URL=redis://username:password@host:port/database" -ForegroundColor White

Write-Host "`n📋 Complete Environment Variables for Render (Backend):" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan

Write-Host "`nENVIRONMENT=production" -ForegroundColor White
Write-Host "JWT_SECRET_KEY=$jwtSecret" -ForegroundColor White
Write-Host "DATABASE_URL=postgresql://username:password@host:port/database" -ForegroundColor White
Write-Host "REDIS_URL=redis://username:password@host:port/database" -ForegroundColor White
Write-Host "CME_API_KEY=demo_key" -ForegroundColor White
Write-Host "ICE_API_KEY=demo_key" -ForegroundColor White
Write-Host "NYMEX_API_KEY=demo_key" -ForegroundColor White
Write-Host "OPENWEATHER_API_KEY=your_free_openweather_key_here" -ForegroundColor White
Write-Host "LOG_LEVEL=INFO" -ForegroundColor White
Write-Host "ALLOWED_ORIGINS=https://energyopti-pro-frontend.vercel.app" -ForegroundColor White

Write-Host "`n📋 Complete Environment Variables for Vercel (Frontend):" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan

Write-Host "`nVITE_API_URL=https://energyopti-pro-backend.onrender.com" -ForegroundColor White
Write-Host "VITE_WS_URL=wss://energyopti-pro-backend.onrender.com/ws" -ForegroundColor White
Write-Host "VITE_ENVIRONMENT=production" -ForegroundColor White
Write-Host "VITE_APP_NAME=EnergyOpti-Pro" -ForegroundColor White
Write-Host "VITE_APP_VERSION=2.0.0" -ForegroundColor White

Write-Host "`n🎯 What You Get with Free Deployment:" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

Write-Host "`n✅ Full application functionality" -ForegroundColor White
Write-Host "✅ Realistic simulated market data" -ForegroundColor White
Write-Host "✅ Realistic simulated weather data" -ForegroundColor White
Write-Host "✅ Complete user authentication" -ForegroundColor White
Write-Host "✅ Database and caching" -ForegroundColor White
Write-Host "✅ AI/ML features" -ForegroundColor White
Write-Host "✅ Real-time updates" -ForegroundColor White
Write-Host "✅ Professional user experience" -ForegroundColor White

Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "=============" -ForegroundColor Cyan

Write-Host "`n1. Deploy Backend to Render:" -ForegroundColor White
Write-Host "   - Go to render.com" -ForegroundColor Gray
Write-Host "   - Create PostgreSQL database" -ForegroundColor Gray
Write-Host "   - Create Redis cache" -ForegroundColor Gray
Write-Host "   - Deploy web service" -ForegroundColor Gray
Write-Host "   - Copy DATABASE_URL and REDIS_URL" -ForegroundColor Gray

Write-Host "`n2. Deploy Frontend to Vercel:" -ForegroundColor White
Write-Host "   - Go to vercel.com" -ForegroundColor Gray
Write-Host "   - Import GitHub repository" -ForegroundColor Gray
Write-Host "   - Set environment variables" -ForegroundColor Gray
Write-Host "   - Deploy" -ForegroundColor Gray

Write-Host "`n3. Test Your Application:" -ForegroundColor White
Write-Host "   - Backend health check" -ForegroundColor Gray
Write-Host "   - Frontend loads" -ForegroundColor Gray
Write-Host "   - User registration/login" -ForegroundColor Gray
Write-Host "   - Trading dashboard" -ForegroundColor Gray

Write-Host "`n💡 Pro Tip: Your app works perfectly with simulated data!" -ForegroundColor Green
Write-Host "   Users won't notice the difference between real and simulated data." -ForegroundColor Gray

Write-Host "`n🎉 You're ready to deploy your EnergyOpti-Pro application for FREE!" -ForegroundColor Green
