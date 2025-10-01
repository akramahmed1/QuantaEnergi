@echo off
echo ========================================
echo QuantaEnergi - Fix and Test Script
echo ========================================

:: Ensure we're in the correct directory
cd /d D:\Documents\QuantaEnergi\backend
echo Current directory: %CD%

:: Verify fixes in geo_risk_service.py
echo.
echo Verifying geo_risk_service.py fixes...
findstr /n "from typing import.*Any" app\services\geo_risk_service.py
if %errorlevel% equ 0 (
    echo ✅ typing.Any import found in geo_risk_service.py
) else (
    echo ❌ typing.Any import NOT found in geo_risk_service.py
)

:: Verify fixes in validation_tests.py
echo.
echo Verifying validation_tests.py imports...
findstr /n "from app.services" tests\validation_tests.py
if %errorlevel% equ 0 (
    echo ✅ Correct imports found in validation_tests.py
) else (
    echo ❌ Correct imports NOT found in validation_tests.py
)

:: Stage modified files
echo.
echo Staging modified files...
git add app/services/geo_risk_service.py
git add tests/validation_tests.py
git add ../docs/

:: Commit changes
echo.
echo Committing changes...
git commit -m "Fix pytest NameError: add typing.Any to geo_risk_service, verify validation_tests imports, add docs/"

:: Set PYTHONPATH
echo.
echo Setting PYTHONPATH...
set PYTHONPATH=%CD%\..;%PYTHONPATH%
echo PYTHONPATH set to: %PYTHONPATH%

:: Run validation tests
echo.
echo Running validation tests...
pytest tests/validation_tests.py -v --tb=short

:: Push changes
echo.
echo Pushing changes to remote...
git push origin feature/ui-and-db-updates

echo.
echo ========================================
echo Script completed!
echo ========================================
pause
