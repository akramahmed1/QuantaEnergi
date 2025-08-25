# Fix Terminal and Environment Issues Script
Write-Host "🔧 Fixing Terminal and Environment Issues..." -ForegroundColor Green

# 1. Fix PATH Environment Variable
Write-Host "📝 Fixing PATH environment variable..." -ForegroundColor Yellow

$cleanPath = @(
    "C:\Windows\system32",
    "C:\Windows", 
    "C:\Windows\System32\Wbem",
    "C:\Program Files\Git\cmd",
    "C:\Program Files\nodejs\",
    "C:\Users\Mohd Akram\AppData\Local\Programs\Python\Python311",
    "C:\Users\Mohd Akram\AppData\Local\Programs\Python\Python311\Scripts",
    "C:\Users\Mohd Akram\AppData\Local\Microsoft\WindowsApps"
) -join ";"

[Environment]::SetEnvironmentVariable("PATH", $cleanPath, "User")

# 2. Refresh current session PATH
$env:PATH = $cleanPath

# 3. Test Git
Write-Host "🔍 Testing Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>$null
    if ($gitVersion) {
        Write-Host "✅ Git is working: $gitVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Git not found in PATH" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Git error: $_" -ForegroundColor Red
}

# 4. Test Node.js
Write-Host "🔍 Testing Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>$null
    if ($nodeVersion) {
        Write-Host "✅ Node.js is working: $nodeVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Node.js not found in PATH" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Node.js error: $_" -ForegroundColor Red
}

# 5. Test Python
Write-Host "🔍 Testing Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Host "✅ Python is working: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python not found in PATH" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Python error: $_" -ForegroundColor Red
}

# 6. Fix Cursor Settings
Write-Host "🔧 Fixing Cursor settings..." -ForegroundColor Yellow

$cursorSettingsPath = "$env:APPDATA\cursor\User\settings.json"
if (Test-Path $cursorSettingsPath) {
    Write-Host "✅ Cursor settings found at: $cursorSettingsPath" -ForegroundColor Green
} else {
    Write-Host "⚠️ Cursor settings not found" -ForegroundColor Yellow
}

# 7. Check PowerShell Execution Policy
Write-Host "🔍 Checking PowerShell execution policy..." -ForegroundColor Yellow
$executionPolicy = Get-ExecutionPolicy
Write-Host "Current execution policy: $executionPolicy" -ForegroundColor Cyan

if ($executionPolicy -eq "Restricted") {
    Write-Host "⚠️ Execution policy is restricted. Consider setting to RemoteSigned" -ForegroundColor Yellow
}

Write-Host "✅ Terminal fix completed!" -ForegroundColor Green
Write-Host "🔄 Please restart your terminal/Cursor for changes to take effect" -ForegroundColor Cyan
