@echo off
echo 🚀 Starting EnergyOpti-Pro Frontend...

REM Check if port 3000 is busy and kill process
echo 🔍 Checking port 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    if not "%%a"=="0" (
        echo ⚠️  Port 3000 is busy. Killing process %%a...
        taskkill /PID %%a /F
        timeout /t 2 /nobreak >nul
    )
)

REM Navigate to frontend directory
cd frontend

REM Install dependencies if needed
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
)

REM Start development server
echo 🌐 Starting development server on port 3000...
npm run dev
