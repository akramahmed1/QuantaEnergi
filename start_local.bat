@echo off
echo 🚀 Starting EnergyOpti-Pro Local Development...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -e .

REM Copy environment file if it doesn't exist
if not exist ".env" (
    echo ⚙️ Creating environment file...
    copy env.example .env
    echo ⚠️ Please edit .env file with your API keys
)

REM Check if Docker is available
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Docker not found. Starting with Python directly...
    echo 📝 Run these commands in separate terminals:
    echo.
    echo Terminal 1 (Backend):
    echo   cd backend
    echo   uvicorn main:app --reload --host 0.0.0.0 --port 8000
    echo.
    echo Terminal 2 (Frontend):
    echo   cd frontend
    echo   npm install
    echo   npm run dev
) else (
    echo 🐳 Starting with Docker Compose...
    docker-compose up -d
    echo ✅ Services started!
    echo 🌐 Backend API: http://localhost:8000
    echo 📊 Frontend: http://localhost:3000
    echo 📚 API Docs: http://localhost:8000/docs
)

echo 🎉 EnergyOpti-Pro is ready!
pause
