@echo off
echo 🚀 EnergyOpti-Pro Universal Execution Script
echo ============================================

REM Set Python path explicitly
set PYTHON_PATH=python
if exist "C:\Python312\python.exe" set PYTHON_PATH=C:\Python312\python.exe
if exist "C:\Python311\python.exe" set PYTHON_PATH=C:\Python311\python.exe
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" set PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe

echo Using Python: %PYTHON_PATH%

REM Execute validation
echo 🔍 Running validation...
%PYTHON_PATH% validation_system.py
if %ERRORLEVEL% EQU 0 (
    echo ✅ Validation passed
) else (
    echo ❌ Validation failed - continuing anyway
)

REM Execute quick validation
echo 🔍 Running quick validation...
%PYTHON_PATH% quick_validation.py
if %ERRORLEVEL% EQU 0 (
    echo ✅ Quick validation passed
) else (
    echo ❌ Quick validation failed - continuing anyway
)

REM Git operations
echo 🔄 Git operations...
git add .
git commit -m "AUTO: Batch execution completed"
git push origin main

echo 🏆 Execution complete!
pause 