#!/usr/bin/env python3
import os
import shutil

def remove_file_or_dir(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
            print(f"✅ Removed file: {path}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"✅ Removed directory: {path}")
    except Exception as e:
        print(f"❌ Failed to remove {path}: {e}")

def cleanup_backend():
    print("🧹 Cleaning up backend directory...")
    backup_files = ["main.py.bak", "main_simple.py", "main_refactored.py", "main_clean.py", "working_backend.py", "simple_main.py", "energy_service.py"]
    test_files = ["test_simple.py", "minimal_test.py", "test_phase1_stubs.py", "test_phase2_stubs.py", "test_phase3_stubs.py", "test_phase1_etrm_features.py", "test_phase2_advanced_features.py", "test_phase2_complete_features.py", "test_enhanced_features.py", "test_redis.py", "test_server.py"]
    artifacts = ["__pycache__", "app/__pycache__", "api/__pycache__", "core/__pycache__", "db/__pycache__", "middleware/__pycache__", "models/__pycache__", "schemas/__pycache__", "services/__pycache__", "utils/__pycache__", "tests/__pycache__", "proto/__pycache__", "build", "audit.log", "backend.log", "bandit_report.json", "bandit_report_new.json", "energyopti_pro.db", "users.db", "AWSCLIV2.msi", "wsl_update_x64.msi"]
    for file in backup_files + test_files:
        if os.path.exists(f"backend/{file}"):
            remove_file_or_dir(f"backend/{file}")
    for artifact in artifacts:
        if os.path.exists(f"backend/{artifact}"):
            remove_file_or_dir(f"backend/{artifact}")
    if os.path.exists("backend/awscli"):
        remove_file_or_dir("backend/awscli")

def cleanup_root():
    print("🧹 Cleaning up root directory...")
    status_files = ["BETA_LAUNCH_CHECKLIST.md", "COMPLETION_EXECUTION_SUMMARY.md", "COMPREHENSIVE_VALIDATION_REPORT.md", "DEPENDENCY_STATUS_REPORT.md", "FINAL_COMPLETION_REPORT.md", "FINAL_COMPLETION_STATUS.md", "FINAL_E2E_VALIDATION_REPORT.md", "FINAL_ENTERPRISE_COMPLETION_REPORT.md", "FINAL_IMPLEMENTATION_SUMMARY.md", "FINAL_STATUS_REPORT.md", "FINAL_STATUS.md", "IMPLEMENTATION_SUMMARY.md", "INFRASTRUCTURE_DEPLOYMENT_STATUS.md", "PERFORMANCE_OPTIMIZATION_SUMMARY.md", "PHASE1_IMPLEMENTATION_SUMMARY.md", "PHASE2_COMPLETE_IMPLEMENTATION_SUMMARY.md", "PR1-PR4_COMPLETION_REPORT.md", "PR5-DEPLOYMENT-SUMMARY.md", "PROJECT_COMPLETION_SUMMARY.md", "temp_pr1.md", "MERMAID_11_4_1_SYNTAX_FIXES.md"]
    duplicate_files = ["DEPLOYMENT.md", "DEPLOYMENT_STATUS.md", "DEPLOYMENT_GUIDE.md", "PRODUCTION_DEPLOYMENT_GUIDE.md", "README_INFRASTRUCTURE.md"]
    test_files = ["test_comprehensive.py", "test_e2e.py", "test-end-to-end.py", "test-local.py"]
    for file in status_files + duplicate_files + test_files:
        if os.path.exists(file):
            remove_file_or_dir(file)

def cleanup_scripts():
    print("🧹 Cleaning up scripts directory...")
    redundant_scripts = ["complete-all.ps1", "complete-final.ps1", "complete-infrastructure.ps1", "execute-completion.ps1", "final-execution.ps1", "test-all-prs.py", "test-pr5.py", "verify-deployment.py", "fix-dependencies.py"]
    for script in redundant_scripts:
        if os.path.exists(f"scripts/{script}"):
            remove_file_or_dir(f"scripts/{script}")

def cleanup_docs():
    print("🧹 Cleaning up documentation...")
    redundant_docs = ["beta_launch_plan.md", "compliance_certifications.md", "sales_pitch_deck.md", "windows-redis-setup.md"]
    for doc in redundant_docs:
        if os.path.exists(f"docs/{doc}"):
            remove_file_or_dir(f"docs/{doc}")

def cleanup_docker():
    print("🧹 Cleaning up Docker files...")
    docker_files = ["docker-compose.scale.yml"]
    for file in docker_files:
        if os.path.exists(file):
            remove_file_or_dir(file)

def consolidate_configs():
    print("🔧 Consolidating configuration files...")
    essential_configs = ["docker-compose.yml", "docker-compose.prod.yml", "Dockerfile", "requirements.txt", "pyproject.toml", "pytest.ini", "alembic.ini", "env.example", "Procfile", "render.yaml", "deploy.sh", "deploy.bat", "quick-start.sh", "start_backend.bat", "start_frontend.bat", ".gitignore", ".dockerignore", ".gitattributes", ".pre-commit-config.yaml", ".ruff.toml"]
    print("✅ Essential config files retained")

def create_clean_readme():
    print("📝 Creating clean README...")
    readme_content = """# 🚀 QuantaEnergi - AI-Powered Energy Trading Platform
    ## 🌟 Overview
    QuantaEnergi is a next-generation Energy Trading and Risk Management (ETRM/CTRM) platform.
    ## ✨ Key Features
    - Trade Lifecycle Management
    - Risk Analytics
    - Islamic Finance Compliance
    - Multi-Regional Regulatory Support
    ## 🏗️ Architecture
    - Backend: FastAPI, PostgreSQL, Redis
    - Frontend: React, TypeScript
    - Infrastructure: Kubernetes, Docker
    ## 🚀 Quick Start
    ### Backend Setup
    ```bash
    cd backend
    venv\\Scripts\\activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload