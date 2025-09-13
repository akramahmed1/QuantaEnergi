# QuantaEnergi Repository Backup Script (PowerShell)
# Creates a timestamped backup of the entire repository
param(
    [string]$BackupLocation = "D:\Backups"
)

# Get current timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupName = "energyopti-pro_backup_$timestamp"
$backupDir = Join-Path $BackupLocation $backupName
Write-Host "🚀 Starting backup process: $backupName" -ForegroundColor Green
Write-Host "=" * 60

# Create backup directory
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# Files and directories to exclude
$excludePatterns = @(
    "__pycache__",
    "*.pyc",
    "venv",
    "env",
    ".venv",
    "node_modules",
    ".vscode",
    ".idea",
    ".cursor",
    "*.log",
    "*.db",
    "*.sqlite",
    "temp_*.md",
    "*.tmp",
    "*.msi",
    "*.exe",
    "bandit_report*.json",
    "awscli",
    "AWSCLIV2.msi",
    "wsl_update_x64.msi"
)

# Important directories to backup
$includeDirectories = @(
    "backend/app",
    "backend/tests",
    "backend/models",
    "backend/proto",
    "frontend/src",
    "frontend/public",
    "docs",
    "scripts",
    "k8s",
    "kubernetes",
    "monitoring",
    "nginx",
    "shared",
    "infrastructure",
    "mobile"
)

# Important files to backup
$includeFiles = @(
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    "pytest.ini",
    "alembic.ini",
    "docker-compose.yml",
    "docker-compose.prod.yml",
    "Dockerfile",
    "Procfile",
    "render.yaml",
    "deploy.sh",
    "deploy.bat",
    "quick-start.sh",
    "start_backend.bat",
    "start_frontend.bat",
    "env.example",
    "security.md",
    "api_documentation.md",
    ".gitignore",
    "backend/requirements.txt",
    "backend/Dockerfile",
    "backend/main.py"
)

Write-Host "📁 Copying important directories..." -ForegroundColor Yellow
$filesBackedUp = 0
$totalSize = 0
foreach ($dir in $includeDirectories) {
    if (Test-Path $dir) {
        $destPath = Join-Path $backupDir $dir
        try {
            Copy-Item -Path $dir -Destination $destPath -Recurse -Force -Exclude $excludePatterns
            Write-Host "✅ Copied directory: $dir" -ForegroundColor Green
            # Count files and size
            $files = Get-ChildItem -Path $destPath -Recurse -File -Exclude $excludePatterns
            $filesBackedUp += $files.Count
            $totalSize += ($files | Measure-Object -Property Length -Sum).Sum
        }
        catch {
            Write-Host "❌ Failed to copy $dir : $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host "`n📄 Copying important files..." -ForegroundColor Yellow
foreach ($file in $includeFiles) {
    if (Test-Path $file) {
        $destPath = Join-Path $backupDir $file
        $destDir = Split-Path $destPath -Parent
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        try {
            Copy-Item -Path $file -Destination $destPath -Force
            Write-Host "✅ Copied file: $file" -ForegroundColor Green
            $filesBackedUp++
            $totalSize += (Get-Item $file).Length
        }
        catch {
            Write-Host "❌ Failed to copy $file : $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# Create backup manifest
$manifest = @{
    backup_name = $backupName
    timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
    source_directory = (Get-Location).Path
    backup_directory = $backupDir
    excluded_patterns = $excludePatterns
    included_directories = $includeDirectories
    included_files = $includeFiles
    total_files_backed_up = $filesBackedUp
    total_size_bytes = $totalSize
    total_size_mb = [math]::Round($totalSize / 1MB, 2)
} | ConvertTo-Json -Depth 3

$manifestPath = Join-Path $backupDir "backup_manifest.json"
$manifest | Out-File -FilePath $manifestPath -Encoding UTF8
Write-Host "`n📋 Backup manifest saved: $manifestPath" -ForegroundColor Green

# Create ZIP archive
Write-Host "`n📦 Creating ZIP archive..." -ForegroundColor Yellow
$zipPath = Join-Path $BackupLocation "$backupName.zip"
try {
    Compress-Archive -Path $backupDir -DestinationPath $zipPath -Force
    Write-Host "✅ ZIP archive created: $zipPath" -ForegroundColor Green
}
catch {
    Write-Host "❌ Failed to create ZIP archive: $($_.Exception.Message)" -ForegroundColor Red
}

# Final summary
Write-Host "`n" + "=" * 60 -ForegroundColor Green
Write-Host "🎉 BACKUP COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "📁 Backup Name: $backupName" -ForegroundColor Cyan
Write-Host "📄 Files Backed Up: $filesBackedUp" -ForegroundColor Cyan
Write-Host "💾 Total Size: $([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor Cyan
Write-Host "📋 Manifest: $manifestPath" -ForegroundColor Cyan
Write-Host "📦 ZIP Archive: $zipPath" -ForegroundColor Cyan
Write-Host "`n🚀 Your repository is safely backed up!" -ForegroundColor Green
Write-Host " You can now proceed with refactoring safely." -ForegroundColor Yellow

return @{
    backup_name = $backupName
    manifest_path = $manifestPath
    zip_archive = $zipPath
    files_count = $filesBackedUp
    size_mb = [math]::Round($totalSize / 1MB, 2)
}