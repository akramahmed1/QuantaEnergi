# EnergyOpti-Pro Vercel Deployment Script
Write-Host "🚀 Deploying EnergyOpti-Pro Frontend to Vercel..." -ForegroundColor Green

# Check if Node.js is available
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Check if npm is available
try {
    $npmVersion = npm --version
    Write-Host "✅ npm found: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not found. Please install npm" -ForegroundColor Red
    exit 1
}

# Check if Vercel CLI is installed
try {
    $vercelVersion = vercel --version
    Write-Host "✅ Vercel CLI found: $vercelVersion" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing Vercel CLI..." -ForegroundColor Blue
    npm install -g vercel
}

# Navigate to frontend directory
Write-Host "📁 Navigating to frontend directory..." -ForegroundColor Blue
Set-Location "frontend"

# Install dependencies
Write-Host "📥 Installing frontend dependencies..." -ForegroundColor Blue
npm install

# Build the project
Write-Host "🔨 Building frontend..." -ForegroundColor Blue
npm run build

# Deploy to Vercel
Write-Host "🚀 Deploying to Vercel..." -ForegroundColor Blue
vercel --prod

Write-Host "✅ Vercel deployment completed!" -ForegroundColor Green
Write-Host "🌐 Your frontend is now live on Vercel!" -ForegroundColor Cyan
