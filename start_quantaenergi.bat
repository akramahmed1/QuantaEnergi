@echo off
echo ========================================
echo QuantaEnergi ETRM/CTRM Platform
echo ========================================

echo.
echo Starting Backend Server...
start "QuantaEnergi Backend" cmd /k "cd apps\backend && python main.py"

echo.
echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo Starting Frontend Server...
start "QuantaEnergi Frontend" cmd /k "cd apps\frontend && npm run dev"

echo.
echo ========================================
echo APPLICATION STARTED SUCCESSFULLY!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo Swagger: http://localhost:8000/docs
echo.
echo LOGIN CREDENTIALS:
echo Administrator: admin / QuantaEnergi2024!
echo Trader: trader / trader123
echo.
echo Press any key to close this window...
pause >nul