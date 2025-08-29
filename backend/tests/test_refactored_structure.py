"""
Test suite for EnergyOpti-Pro refactored structure.

This test file verifies that the new organized module structure works correctly
and all imports and dependencies are properly configured.
"""

import pytest
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

class TestRefactoredStructure:
    """Test the refactored project structure"""
    
    def test_core_module_imports(self):
        """Test that core module imports work correctly"""
        try:
            from app.core import (
                settings,
                get_current_user,
                create_access_token,
                verify_token,
                SecurityAuditor,
                SecurityMiddleware
            )
            assert True, "Core module imports successful"
        except ImportError as e:
            pytest.fail(f"Core module import failed: {e}")
    
    def test_services_module_imports(self):
        """Test that services module imports work correctly"""
        try:
            from app.services import (
                forecasting_service,
                quantum_optimization_service,
                blockchain_service,
                iot_integration_service,
                compliance_service
            )
            assert True, "Services module imports successful"
        except ImportError as e:
            pytest.fail(f"Services module import failed: {e}")
    
    def test_api_module_imports(self):
        """Test that API module imports work correctly"""
        try:
            from app.api import (
                auth_router,
                disruptive_router,
                admin_router,
                energy_data_router
            )
            assert True, "API module imports successful"
        except ImportError as e:
            pytest.fail(f"API module import failed: {e}")
    
    def test_utils_module_imports(self):
        """Test that utils module imports work correctly"""
        try:
            from app.utils import (
                validate_email,
                format_currency,
                generate_uuid
            )
            assert True, "Utils module imports successful"
        except ImportError as e:
            pytest.fail(f"Utils module import failed: {e}")
    
    def test_schemas_module_imports(self):
        """Test that schemas module imports work correctly"""
        try:
            from app.schemas.disruptive import (
                ForecastRequest,
                PortfolioAsset,
                ComplianceRegion
            )
            assert True, "Schemas module imports successful"
        except ImportError as e:
            pytest.fail(f"Schemas module import failed: {e}")

class TestRefactoredMainApp:
    """Test the refactored main application"""
    
    def test_main_app_import(self):
        """Test that the refactored main app can be imported"""
        try:
            from app.main_refactored import app
            assert app is not None, "Main app imported successfully"
            assert hasattr(app, 'title'), "App has title attribute"
            assert hasattr(app, 'version'), "App has version attribute"
        except ImportError as e:
            pytest.fail(f"Main app import failed: {e}")
    
    def test_app_configuration(self):
        """Test that the app is properly configured"""
        try:
            from app.main_refactored import app
            
            # Check app metadata
            assert app.title == "EnergyOpti-Pro: Disruptive Energy Trading SaaS"
            assert app.version == "2.0.0"
            
            # Check that routers are included
            routes = [route.path for route in app.routes]
            assert "/api/auth" in str(routes), "Auth router included"
            assert "/api/disruptive" in str(routes), "Disruptive features router included"
            assert "/api/admin" in str(routes), "Admin router included"
            assert "/api/energy" in str(routes), "Energy data router included"
            
        except ImportError as e:
            pytest.fail(f"App configuration test failed: {e}")

class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_validation_functions(self):
        """Test validation utility functions"""
        from app.utils.validators import (
            validate_email,
            validate_phone,
            validate_currency,
            validate_timestamp
        )
        
        # Test email validation
        assert validate_email("test@example.com") == True
        assert validate_email("invalid-email") == False
        assert validate_email("") == False
        
        # Test phone validation
        assert validate_phone("+1-555-123-4567") == True
        assert validate_phone("123") == False
        assert validate_phone("") == False
        
        # Test currency validation
        assert validate_currency("USD") == True
        assert validate_currency("EUR") == True
        assert validate_currency("123") == False
        
        # Test timestamp validation
        from datetime import datetime
        now = datetime.now().isoformat()
        assert validate_timestamp(now) == True
        assert validate_timestamp("invalid-timestamp") == False
    
    def test_formatting_functions(self):
        """Test formatting utility functions"""
        from app.utils.formatters import (
            format_currency,
            format_percentage,
            format_timestamp
        )
        
        # Test currency formatting
        formatted = format_currency(1234.56, "USD")
        assert "1234.56" in formatted or "1,234.56" in formatted
        
        # Test percentage formatting
        formatted = format_percentage(25.5)
        assert formatted == "25.50%"
        
        # Test timestamp formatting
        from datetime import datetime
        now = datetime.now()
        formatted = format_timestamp(now, "human")
        assert str(now.year) in formatted
    
    def test_helper_functions(self):
        """Test helper utility functions"""
        from app.utils.helpers import (
            generate_uuid,
            calculate_hash,
            sanitize_input
        )
        
        # Test UUID generation
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        assert uuid1 != uuid2
        assert len(uuid1) == 36
        
        # Test hash calculation
        hash1 = calculate_hash("test", "sha256")
        hash2 = calculate_hash("test", "sha256")
        assert hash1 == hash2
        
        # Test input sanitization
        sanitized = sanitize_input("<script>alert('xss')</script>")
        assert "<script>" not in sanitized
        assert sanitized == "scriptalertxss/script"  # Expected sanitized output

class TestSchemaValidation:
    """Test Pydantic schema validation"""
    
    def test_forecast_schemas(self):
        """Test forecast-related schemas"""
        from app.schemas.disruptive import (
            ForecastRequest,
            ForecastModelType,
            HistoricalDataPoint
        )
        from datetime import datetime
        
        # Test valid forecast request
        valid_request = ForecastRequest(
            commodity="crude_oil",
            days=7,
            use_prophet=False,
            model_type=ForecastModelType.ENSEMBLE
        )
        assert valid_request.commodity == "crude_oil"
        assert valid_request.days == 7
        
        # Test valid historical data point
        valid_data = HistoricalDataPoint(
            timestamp=datetime.now(),
            price=80.0,
            volume=1000.0
        )
        assert valid_data.price == 80.0
        assert valid_data.volume == 1000.0
    
    def test_portfolio_schemas(self):
        """Test portfolio optimization schemas"""
        from app.schemas.disruptive import (
            PortfolioAsset,
            PortfolioOptimizationRequest
        )
        
        # Test valid portfolio asset
        asset = PortfolioAsset(
            symbol="OIL",
            weight=0.5,
            expected_return=0.08,
            volatility=0.15,
            sector="energy",
            region="global",
            esg_score=75.0
        )
        assert asset.symbol == "OIL"
        assert asset.weight == 0.5
        assert asset.esg_score == 75.0
        
        # Test portfolio optimization request
        request = PortfolioOptimizationRequest(
            assets=[asset, asset],  # Need at least 2 assets
            target_return=0.08,
            risk_tolerance=0.5
        )
        assert len(request.assets) == 2
        assert request.risk_tolerance == 0.5
    
    def test_compliance_schemas(self):
        """Test compliance schemas"""
        from app.schemas.disruptive import (
            ComplianceRegion,
            ComplianceStatus,
            ComplianceRequest
        )
        
        # Test compliance regions
        assert ComplianceRegion.US_FERC == "US_FERC"
        assert ComplianceRegion.EU_REMIT == "EU_REMIT"
        
        # Test compliance statuses
        assert ComplianceStatus.COMPLIANT == "compliant"
        assert ComplianceStatus.NON_COMPLIANT == "non_compliant"
        
        # Test compliance request
        request = ComplianceRequest(
            trading_data={"transaction_reporting": True},
            regions=[ComplianceRegion.US_FERC]
        )
        assert request.regions[0] == ComplianceRegion.US_FERC

class TestServiceIntegration:
    """Test service integration with new structure"""
    
    def test_forecasting_service_integration(self):
        """Test forecasting service works with new structure"""
        from app.services import forecasting_service
        
        assert hasattr(forecasting_service, 'train_model')
        assert hasattr(forecasting_service, 'forecast_future_consumption')
        assert hasattr(forecasting_service, 'calculate_esg_score')
    
    def test_quantum_service_integration(self):
        """Test quantum optimization service works with new structure"""
        from app.services import quantum_optimization_service
        
        assert hasattr(quantum_optimization_service, 'optimize_portfolio_quantum')
        assert hasattr(quantum_optimization_service, 'quantum_risk_assessment')
        assert hasattr(quantum_optimization_service, 'get_quantum_status')
    
    def test_blockchain_service_integration(self):
        """Test blockchain service works with new structure"""
        from app.services import blockchain_service
        
        assert hasattr(blockchain_service, 'deploy_energy_trade_contract')
        assert hasattr(blockchain_service, 'execute_energy_trade')
        assert hasattr(blockchain_service, 'get_blockchain_status')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
