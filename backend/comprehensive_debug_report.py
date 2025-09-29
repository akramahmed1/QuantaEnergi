#!/usr/bin/env python3
"""
Comprehensive Debug Report for QuantaEnergi Project
Identifies and documents all potential issues
"""

import sys
import os
import traceback
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class DebugReporter:
    """Comprehensive debug reporter for the QuantaEnergi project"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []
        self.report_time = datetime.now()
    
    def add_issue(self, category, description, severity="HIGH"):
        """Add an issue to the report"""
        self.issues.append({
            "category": category,
            "description": description,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_warning(self, category, description):
        """Add a warning to the report"""
        self.warnings.append({
            "category": category,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_success(self, category, description):
        """Add a success to the report"""
        self.successes.append({
            "category": category,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_basic_imports(self):
        """Test basic Python imports"""
        try:
            import logging
            import uuid
            import json
            from datetime import datetime
            from typing import Dict, List, Any, Optional
            from enum import Enum
            from dataclasses import dataclass
            self.add_success("Imports", "Basic Python imports successful")
            return True
        except Exception as e:
            self.add_issue("Imports", f"Basic imports failed: {e}")
            return False
    
    def test_fastapi_imports(self):
        """Test FastAPI imports"""
        try:
            from fastapi import APIRouter, HTTPException, Depends, Query
            from pydantic import BaseModel
            self.add_success("Imports", "FastAPI imports successful")
            return True
        except Exception as e:
            self.add_issue("Imports", f"FastAPI imports failed: {e}")
            return False
    
    def test_database_imports(self):
        """Test database imports"""
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker, Session
            from sqlalchemy.pool import StaticPool
            self.add_success("Database", "SQLAlchemy imports successful")
            return True
        except Exception as e:
            self.add_issue("Database", f"SQLAlchemy imports failed: {e}")
            return False
    
    def test_app_config(self):
        """Test app configuration"""
        try:
            from app.core.config import settings
            if hasattr(settings, 'DATABASE_URL'):
                self.add_success("Config", "App configuration loaded successfully")
                return True
            else:
                self.add_warning("Config", "App configuration missing DATABASE_URL")
                return False
        except Exception as e:
            self.add_issue("Config", f"App configuration failed: {e}")
            return False
    
    def test_models_imports(self):
        """Test model imports"""
        try:
            from app.models import Base, Trade, ESG, User
            self.add_success("Models", "Model imports successful")
            return True
        except Exception as e:
            self.add_issue("Models", f"Model imports failed: {e}")
            return False
    
    def test_services_imports(self):
        """Test service imports"""
        try:
            from app.services.advanced_etrm_features import AdvancedETRMService
            from app.services.advanced_risk_management import AdvancedRiskManager
            from app.services.advanced_trading_engine import AdvancedTradingEngine
            from app.services.comprehensive_compliance import ComprehensiveComplianceEngine
            self.add_success("Services", "Service imports successful")
            return True
        except Exception as e:
            self.add_issue("Services", f"Service imports failed: {e}")
            return False
    
    def test_schemas_imports(self):
        """Test schema imports"""
        try:
            from app.schemas.trade import ApiResponse
            self.add_success("Schemas", "Schema imports successful")
            return True
        except Exception as e:
            self.add_issue("Schemas", f"Schema imports failed: {e}")
            return False
    
    def test_api_imports(self):
        """Test API imports"""
        try:
            from app.api.v1.advanced_etrm import router
            self.add_success("API", "API router imports successful")
            return True
        except Exception as e:
            self.add_issue("API", f"API router imports failed: {e}")
            return False
    
    def test_database_connection(self):
        """Test database connection"""
        try:
            from app.db.session import engine, SessionLocal
            # Test connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            self.add_success("Database", "Database connection successful")
            return True
        except Exception as e:
            self.add_issue("Database", f"Database connection failed: {e}")
            return False
    
    def test_service_initialization(self):
        """Test service initialization"""
        try:
            from app.services.advanced_etrm_features import AdvancedETRMService
            service = AdvancedETRMService()
            instruments = service.get_available_instruments('US')
            if len(instruments) > 0:
                self.add_success("Services", "ETRM service initialization successful")
                return True
            else:
                self.add_warning("Services", "ETRM service returned no instruments")
                return False
        except Exception as e:
            self.add_issue("Services", f"ETRM service initialization failed: {e}")
            return False
    
    def test_api_routing(self):
        """Test API routing"""
        try:
            from app.api.v1.advanced_etrm import router
            if hasattr(router, 'routes') and len(router.routes) > 0:
                self.add_success("API", f"API router has {len(router.routes)} routes")
                return True
            else:
                self.add_warning("API", "API router has no routes")
                return False
        except Exception as e:
            self.add_issue("API", f"API routing test failed: {e}")
            return False
    
    def generate_report(self):
        """Generate comprehensive debug report"""
        print("🔍 QuantaEnergi Comprehensive Debug Report")
        print("=" * 60)
        print(f"Report Generated: {self.report_time.isoformat()}")
        print()
        
        # Test all components
        print("🧪 Running Diagnostic Tests...")
        print("-" * 40)
        
        tests = [
            ("Basic Imports", self.test_basic_imports),
            ("FastAPI Imports", self.test_fastapi_imports),
            ("Database Imports", self.test_database_imports),
            ("App Configuration", self.test_app_config),
            ("Model Imports", self.test_models_imports),
            ("Service Imports", self.test_services_imports),
            ("Schema Imports", self.test_schemas_imports),
            ("API Imports", self.test_api_imports),
            ("Database Connection", self.test_database_connection),
            ("Service Initialization", self.test_service_initialization),
            ("API Routing", self.test_api_routing),
        ]
        
        passed = 0
        total = len(tests)
        
        for name, test_func in tests:
            print(f"Testing {name}...", end=" ")
            try:
                if test_func():
                    print("✅ PASS")
                    passed += 1
                else:
                    print("⚠️ WARN")
            except Exception as e:
                print(f"❌ FAIL - {e}")
        
        print()
        print("📊 Test Results Summary")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Issues: {len(self.issues)}")
        
        if self.successes:
            print(f"\n✅ Successes ({len(self.successes)}):")
            for success in self.successes:
                print(f"  • {success['category']}: {success['description']}")
        
        if self.warnings:
            print(f"\n⚠️ Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning['category']}: {warning['description']}")
        
        if self.issues:
            print(f"\n❌ Issues ({len(self.issues)}):")
            for issue in self.issues:
                print(f"  • {issue['category']} ({issue['severity']}): {issue['description']}")
        
        print()
        print("🔧 Recommended Actions:")
        print("-" * 40)
        
        if len(self.issues) == 0:
            print("🎉 No critical issues found! The project appears to be working correctly.")
        else:
            print("1. Fix critical issues listed above")
            print("2. Address warnings for optimal performance")
            print("3. Run tests again to verify fixes")
        
        if len(self.issues) == 0 and len(self.warnings) == 0:
            print("\n🚀 Project Status: READY FOR PRODUCTION")
        elif len(self.issues) == 0:
            print("\n⚠️ Project Status: READY WITH WARNINGS")
        else:
            print("\n🔧 Project Status: NEEDS ATTENTION")
        
        return len(self.issues) == 0

def main():
    """Main debug function"""
    reporter = DebugReporter()
    success = reporter.generate_report()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
