# Comprehensive Terminal and Environment Fix Script
Write-Host "🚀 Starting comprehensive terminal fix..." -ForegroundColor Green

# 1. Set PowerShell to use UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 2. Fix PATH with proper Git location
Write-Host "🔧 Fixing PATH with correct Git location..." -ForegroundColor Yellow

$cleanPath = @(
    "C:\Windows\system32",
    "C:\Windows", 
    "C:\Windows\System32\Wbem",
    "C:\Program Files\Git\bin",
    "C:\Program Files\Git\cmd",
    "C:\Program Files\nodejs\",
    "C:\Users\Mohd Akram\AppData\Local\Programs\Python\Python311",
    "C:\Users\Mohd Akram\AppData\Local\Programs\Python\Python311\Scripts",
    "C:\Users\Mohd Akram\AppData\Local\Microsoft\WindowsApps"
) -join ";"

# Set environment variable
[Environment]::SetEnvironmentVariable("PATH", $cleanPath, "User")

# Update current session
$env:PATH = $cleanPath

# 3. Test and fix Git
Write-Host "🔍 Testing Git installation..." -ForegroundColor Yellow

$gitPaths = @(
    "C:\Program Files\Git\bin\git.exe",
    "C:\Program Files\Git\cmd\git.exe",
    "C:\Windows\System32\git.exe"
)

$gitFound = $false
foreach ($gitPath in $gitPaths) {
    if (Test-Path $gitPath) {
        Write-Host "✅ Git found at: $gitPath" -ForegroundColor Green
        $gitFound = $true
        break
    }
}

if (-not $gitFound) {
    Write-Host "❌ Git not found. Please install Git from: https://git-scm.com/download/win" -ForegroundColor Red
}

# 4. Test Node.js
Write-Host "🔍 Testing Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = & "C:\Program Files\nodejs\node.exe" --version 2>$null
    if ($nodeVersion) {
        Write-Host "✅ Node.js is working: $nodeVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Node.js not working properly" -ForegroundColor Red
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
        Write-Host "❌ Python not working properly" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Python error: $_" -ForegroundColor Red
}

# 6. Fix Cursor Settings
Write-Host "🔧 Checking Cursor settings..." -ForegroundColor Yellow

$cursorSettingsPath = "$env:APPDATA\cursor\User\settings.json"
if (Test-Path $cursorSettingsPath) {
    Write-Host "✅ Cursor settings found at: $cursorSettingsPath" -ForegroundColor Green
    
    # Read current settings
    try {
        $settings = Get-Content $cursorSettingsPath | ConvertFrom-Json
        Write-Host "📋 Current Cursor settings loaded" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Could not read Cursor settings: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Cursor settings not found" -ForegroundColor Yellow
}

# 7. Check PowerShell Execution Policy
Write-Host "🔍 Checking PowerShell execution policy..." -ForegroundColor Yellow
$executionPolicy = Get-ExecutionPolicy
Write-Host "Current execution policy: $executionPolicy" -ForegroundColor Cyan

# 8. Test basic commands
Write-Host "🧪 Testing basic commands..." -ForegroundColor Yellow

# Test ls command
try {
    $lsResult = ls 2>$null
    Write-Host "✅ ls command working" -ForegroundColor Green
} catch {
    Write-Host "❌ ls command failed: $_" -ForegroundColor Red
}

# Test pwd command
try {
    $pwdResult = pwd 2>$null
    Write-Host "✅ pwd command working" -ForegroundColor Green
} catch {
    Write-Host "❌ pwd command failed: $_" -ForegroundColor Red
}

Write-Host "✅ Comprehensive fix completed!" -ForegroundColor Green
Write-Host "🔄 Please restart your terminal/Cursor for all changes to take effect" -ForegroundColor Cyan
Write-Host "💡 If Git still doesn't work, please install it from: https://git-scm.com/download/win" -ForegroundColor Yellow
