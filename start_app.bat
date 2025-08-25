@echo off
echo Starting EnergyOpti-Pro...
echo.

cd /d "D:\Documents\energyopti-pro"

echo Building and starting services...
docker-compose -f docker-compose.dev.yml up -d

echo.
echo Checking service status...
docker ps

echo.
echo Application should be running at:
echo - Frontend: http://localhost:3000
echo - Backend: http://localhost:8000
echo - Database: localhost:5432
echo.
echo Press any key to exit...
pause >nul
