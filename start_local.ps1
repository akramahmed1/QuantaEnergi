# EnergyOpti-Pro Local Development Startup Script
Write-Host "🚀 Starting EnergyOpti-Pro Local Development..." -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = py --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Check if Docker is available
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Docker not found. Will use direct Python startup" -ForegroundColor Yellow
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Blue
    py -m venv venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Blue
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Blue
pip install -e .

# Copy environment file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "⚙️  Creating environment file..." -ForegroundColor Blue
    Copy-Item "env.example" ".env"
    Write-Host "⚠️  Please edit .env file with your API keys" -ForegroundColor Yellow
}

# Check if Docker is available and start with Docker
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "🐳 Starting with Docker Compose..." -ForegroundColor Blue
    docker-compose up -d
    
    Write-Host "✅ Services started!" -ForegroundColor Green
    Write-Host "🌐 Backend API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "📊 Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    
} else {
    Write-Host "🐍 Starting with Python directly..." -ForegroundColor Blue
    Write-Host "📝 Run these commands in separate terminals:" -ForegroundColor Yellow
    
    Write-Host "Terminal 1 (Backend):" -ForegroundColor Cyan
    Write-Host "  cd backend" -ForegroundColor White
    Write-Host "  uvicorn main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
    
    Write-Host "Terminal 2 (Frontend):" -ForegroundColor Cyan
    Write-Host "  cd frontend" -ForegroundColor White
    Write-Host "  npm install" -ForegroundColor White
    Write-Host "  npm run dev" -ForegroundColor White
}

Write-Host "🎉 EnergyOpti-Pro is ready!" -ForegroundColor Green
