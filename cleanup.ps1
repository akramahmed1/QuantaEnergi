# QuantaEnergi Repository Cleanup Script
Write-Host "🚀 Starting comprehensive repository cleanup..." -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Yellow

# Backend duplicate files
$files = @(
    "backend/main.py.bak",
    "backend/main_simple.py",
    "backend/simple_main.py", 
    "backend/working_backend.py",
    "backend/energy_service.py",
    "backend/test_simple.py",
    "backend/minimal_test.py",
    "backend/test_phase1_stubs.py",
    "backend/test_phase2_stubs.py",
    "backend/test_phase3_stubs.py",
    "backend/test_phase1_etrm_features.py",
    "backend/test_phase2_advanced_features.py",
    "backend/test_phase2_complete_features.py",
    "backend/test_enhanced_features.py",
    "backend/test_redis.py",
    "backend/test_server.py",
    "backend/test_energyopti_pro.db",
    "backend/test_all_production_services.py",
    "backend/test_api_endpoints.py",
    "backend/test_pr2_frontend_security.py",
    "backend/test_production_ready.py",
    "backend/run_comprehensive_tests.py",
    "backend/run_grpc_test.py",
    "backend/FINAL_PHASE2_STATUS.md",
    "backend/POST_PHASE3_STATUS_REPORT.md",
    "backend/PR2_FRONTEND_SECURITY_STATUS_REPORT.md",
    "backend/PR3_GTM_COMPLIANCE_STATUS_REPORT.md",
    "backend/QUANTAENERGI_PRODUCTION_STATUS.md",
    "backend/PHASE2_IMPLEMENTATION_SUMMARY.md",
    "backend/PROJECT_STRUCTURE.md",
    "backend/PRODUCTION_DEPLOYMENT_GUIDE.md",
    "backend/audit.log",
    "backend/backend.log",
    "backend/bandit_report.json",
    "backend/bandit_report_new.json",
    "backend/energyopti_pro.db",
    "backend/users.db",
    "backend/AWSCLIV2.msi",
    "backend/wsl_update_x64.msi",
    "backend/flyctl_install.ps1",
    "backend/fix_warnings.py",
    "FINAL_STATUS.md",
    "FINAL_STATUS_REPORT.md",
    "FINAL_COMPLETION_STATUS.md",
    "COMPLETION_EXECUTION_SUMMARY.md",
    "COMPREHENSIVE_VALIDATION_REPORT.md",
    "DEPENDENCY_STATUS_REPORT.md",
    "FINAL_COMPLETION_REPORT.md",
    "FINAL_E2E_VALIDATION_REPORT.md",
    "FINAL_ENTERPRISE_COMPLETION_REPORT.md",
    "FINAL_IMPLEMENTATION_SUMMARY.md",
    "IMPLEMENTATION_SUMMARY.md",
    "INFRASTRUCTURE_DEPLOYMENT_STATUS.md",
    "PERFORMANCE_OPTIMIZATION_SUMMARY.md",
    "PHASE1_IMPLEMENTATION_SUMMARY.md",
    "PHASE2_COMPLETE_IMPLEMENTATION_SUMMARY.md",
    "PR1-PR4_COMPLETION_REPORT.md",
    "PR5-DEPLOYMENT-SUMMARY.md",
    "PROJECT_COMPLETION_SUMMARY.md",
    "temp_pr1.md",
    "MERMAID_11_4_1_SYNTAX_FIXES.md",
    "DEPLOYMENT.md",
    "DEPLOYMENT_STATUS.md",
    "DEPLOYMENT_GUIDE.md",
    "PRODUCTION_DEPLOYMENT_GUIDE.md",
    "README_INFRASTRUCTURE.md",
    "test_comprehensive.py",
    "test_e2e.py",
    "test-end-to-end.py",
    "test-local.py",
    "docs/beta_launch_plan.md",
    "docs/compliance_certifications.md",
    "docs/sales_pitch_deck.md",
    "docs/windows-redis-setup.md",
    "docker-compose.scale.yml",
    "scripts/complete-all.ps1",
    "scripts/complete-final.ps1",
    "scripts/complete-infrastructure.ps1",
    "scripts/execute-completion.ps1",
    "scripts/final-execution.ps1",
    "scripts/test-all-prs.py",
    "scripts/test-pr5.py",
    "scripts/verify-deployment.py",
    "scripts/fix-dependencies.py"
)

$removed = 0
$failed = 0

foreach ($file in $files) {
    if (Test-Path $file) {
        try {
            Remove-Item $file -Force
            Write-Host "✅ Removed: $file" -ForegroundColor Green
            $removed++
        }
        catch {
            Write-Host "❌ Failed: $file" -ForegroundColor Red
            $failed++
        }
    }
}

# Remove directories
$dirs = @(
    "backend/__pycache__",
    "backend/app/__pycache__",
    "backend/app/api/__pycache__",
    "backend/app/core/__pycache__",
    "backend/app/db/__pycache__",
    "backend/app/middleware/__pycache__",
    "backend/app/models/__pycache__",
    "backend/app/schemas/__pycache__",
    "backend/app/services/__pycache__",
    "backend/app/utils/__pycache__",
    "backend/tests/__pycache__",
    "backend/proto/__pycache__",
    "backend/build",
    "backend/awscli"
)

foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        try {
            Remove-Item $dir -Recurse -Force
            Write-Host "✅ Removed directory: $dir" -ForegroundColor Green
            $removed++
        }
        catch {
            Write-Host "❌ Failed directory: $dir" -ForegroundColor Red
            $failed++
        }
    }
}

Write-Host "=" * 60 -ForegroundColor Yellow
Write-Host "🎉 Cleanup completed!" -ForegroundColor Green
Write-Host "✅ Files/Directories removed: $removed" -ForegroundColor Green
Write-Host "❌ Failed removals: $failed" -ForegroundColor Red
Write-Host "=" * 60 -ForegroundColor Yellow
