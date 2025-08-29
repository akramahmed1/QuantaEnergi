@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM EnergyOpti-Pro Deployment Script for Windows
REM This script automates the deployment process for local verification and cloud deployment

echo 🚀 EnergyOpti-Pro Deployment Script
echo ==================================

REM Check if Docker is running
echo [INFO] Checking if Docker is running...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo [SUCCESS] Docker is running

:menu
echo.
echo Choose deployment option:
echo 1) Local verification with Docker Compose
echo 2) Deploy backend to Render
echo 3) Deploy frontend to Vercel
echo 4) Full deployment (local + cloud)
echo 5) Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto local_verification
if "%choice%"=="2" goto deploy_render
if "%choice%"=="3" goto deploy_vercel
if "%choice%"=="4" goto full_deployment
if "%choice%"=="5" goto exit_script
echo [ERROR] Invalid choice. Please enter 1-5
goto menu

:local_verification
echo [INFO] Starting local verification with Docker Compose...
docker-compose up --build -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Docker Compose services
    pause
    goto menu
)

echo [INFO] Waiting for services to be ready...
timeout /t 30 /nobreak >nul

echo [INFO] Checking if backend is responding...
curl -f http://localhost:8000/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Backend is not responding. Check logs with: docker-compose logs backend
    pause
    goto menu
)
echo [SUCCESS] Backend is responding at http://localhost:8000

echo [SUCCESS] Local verification completed successfully!
echo [INFO] Services available at:
echo   - Backend API: http://localhost:8000
echo   - Database: localhost:5432
echo   - Redis: localhost:6379
echo.
echo [INFO] View logs with: docker-compose logs -f
echo [INFO] Stop services with: docker-compose down
pause
goto menu

:deploy_render
echo [INFO] Deploying to Render...
echo [INFO] Please ensure you have:
echo   1. Render CLI installed and authenticated
echo   2. A Render account with a service created
echo   3. Environment variables configured in Render dashboard
echo.
pause

REM Check if render CLI is available
render --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Render CLI is not installed. Please install it first:
    echo   https://render.com/docs/install-cli
    pause
    goto menu
)

render deploy
if %errorlevel% neq 0 (
    echo [ERROR] Deployment to Render failed
    pause
    goto menu
)

echo [SUCCESS] Deployment to Render completed!
pause
goto menu

:deploy_vercel
echo [INFO] Deploying frontend to Vercel...
echo [INFO] Please ensure you have:
echo   1. Vercel CLI installed and authenticated
echo   2. A Vercel account with a project created
echo   3. Environment variables configured in Vercel dashboard
echo.
pause

REM Check if vercel CLI is available
vercel --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Vercel CLI is not installed. Please install it first:
    echo   npm i -g vercel
    pause
    goto menu
)

cd frontend
vercel --prod
if %errorlevel% neq 0 (
    echo [ERROR] Frontend deployment to Vercel failed
    cd ..
    pause
    goto menu
)
cd ..

echo [SUCCESS] Frontend deployment to Vercel completed!
pause
goto menu

:full_deployment
echo [INFO] Starting full deployment process...
call :local_verification
echo.
call :deploy_render
echo.
call :deploy_vercel
echo.
echo [SUCCESS] Full deployment completed!
pause
goto menu

:exit_script
echo [INFO] Exiting deployment script
exit /b 0
