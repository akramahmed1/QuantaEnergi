"""
Comprehensive tests for consolidated AI and Quantum services
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import numpy as np

from app.services.consolidated_ai_service import ConsolidatedAIService, ai_service
from app.services.consolidated_quantum_service import ConsolidatedQuantumService, quantum_service, PortfolioAsset
from app.core.secrets import VaultSecretsManager, secrets_manager


class TestConsolidatedAIService:
    """Test suite for Consolidated AI Service"""
    
    @pytest.fixture
    def ai_service_instance(self):
        return ConsolidatedAIService()
    
    @pytest.mark.asyncio
    async def test_predict_price_ensemble(self, ai_service_instance):
        """Test ensemble price prediction"""
        result = await ai_service_instance.predict_price(
            commodity='crude_oil',
            days_ahead=7,
            method='ensemble'
        )
        
        assert result['commodity'] == 'crude_oil'
        assert result['method'] == 'ensemble'
        assert 'predictions' in result
        assert 'esg_score' in result
        assert 'confidence' in result
        assert result['confidence'] > 0
    
    @pytest.mark.asyncio
    async def test_predict_price_lstm(self, ai_service_instance):
        """Test LSTM price prediction"""
        result = await ai_service_instance.predict_price(
            commodity='natural_gas',
            days_ahead=14,
            method='lstm'
        )
        
        assert result['commodity'] == 'natural_gas'
        assert result['method'] == 'lstm'
        assert 'predictions' in result
    
    @pytest.mark.asyncio
    async def test_predict_price_prophet(self, ai_service_instance):
        """Test Prophet price prediction"""
        result = await ai_service_instance.predict_price(
            commodity='coal',
            days_ahead=30,
            method='prophet'
        )
        
        assert result['commodity'] == 'coal'
        assert result['method'] == 'prophet'
        assert 'predictions' in result
    
    def test_calculate_esg_score(self, ai_service_instance):
        """Test ESG score calculation"""
        # Test crude oil
        esg_score = ai_service_instance._calculate_esg_score('crude_oil')
        assert esg_score['overall_score'] > 0
        assert esg_score['overall_score'] <= 100
        assert esg_score['rating'] in ['A', 'B', 'C', 'D']
        
        # Test renewables (should have higher score)
        esg_renewables = ai_service_instance._calculate_esg_score('renewables')
        assert esg_renewables['overall_score'] > esg_score['overall_score']
    
    def test_generate_historical_data(self, ai_service_instance):
        """Test historical data generation"""
        data = ai_service_instance._generate_historical_data('crude_oil', 100)
        
        assert len(data) == 100
        assert 'date' in data.columns
        assert 'price' in data.columns
        assert 'volume' in data.columns
        assert 'commodity' in data.columns
        assert data['commodity'].iloc[0] == 'crude_oil'
    
    def test_prepare_lstm_features(self, ai_service_instance):
        """Test LSTM feature preparation"""
        # Create sample data
        data = ai_service_instance._generate_historical_data('crude_oil', 50)
        features = ai_service_instance._prepare_lstm_features(data)
        
        assert features.shape[1] == 4  # price, volume, price_change, volume_change
        assert features.shape[0] == 50


class TestConsolidatedQuantumService:
    """Test suite for Consolidated Quantum Service"""
    
    @pytest.fixture
    def quantum_service_instance(self):
        return ConsolidatedQuantumService()
    
    @pytest.fixture
    def sample_assets(self):
        return [
            PortfolioAsset(
                symbol='WTI',
                expected_return=0.12,
                volatility=0.25,
                sector='energy',
                region='global',
                esg_score=65.0
            ),
            PortfolioAsset(
                symbol='BRENT',
                expected_return=0.10,
                volatility=0.22,
                sector='energy',
                region='global',
                esg_score=70.0
            ),
            PortfolioAsset(
                symbol='NATURAL_GAS',
                expected_return=0.08,
                volatility=0.30,
                sector='energy',
                region='global',
                esg_score=80.0
            )
        ]
    
    @pytest.mark.asyncio
    async def test_optimize_portfolio_quantum(self, quantum_service_instance, sample_assets):
        """Test quantum portfolio optimization"""
        result = await quantum_service_instance.optimize_portfolio_quantum(
            assets=sample_assets,
            target_return=0.10,
            risk_tolerance=0.5,
            max_iterations=50
        )
        
        assert 'optimization_method' in result
        assert 'selected_assets' in result
        assert 'optimal_weights' in result
        assert 'expected_return' in result
        assert 'risk_score' in result
        assert 'sharpe_ratio' in result
        assert result['expected_return'] > 0
    
    @pytest.mark.asyncio
    async def test_calculate_quantum_var(self, quantum_service_instance):
        """Test quantum VaR calculation"""
        portfolio = [
            {'symbol': 'WTI', 'value': 1000000, 'volatility': 0.25, 'weight': 0.5},
            {'symbol': 'BRENT', 'value': 800000, 'volatility': 0.22, 'weight': 0.3},
            {'symbol': 'NATURAL_GAS', 'value': 700000, 'volatility': 0.30, 'weight': 0.2}
        ]
        
        result = await quantum_service_instance.calculate_quantum_var(
            portfolio=portfolio,
            confidence_level=0.95,
            time_horizon=1
        )
        
        assert 'var_amount' in result
        assert 'confidence_level' in result
        assert 'time_horizon' in result
        assert 'quantum_advantage' in result
        assert result['confidence_level'] == 0.95
        assert result['time_horizon'] == 1
        assert result['var_amount'] > 0
    
    def test_calculate_portfolio_risk(self, quantum_service_instance, sample_assets):
        """Test portfolio risk calculation"""
        risk = quantum_service_instance._calculate_portfolio_risk(sample_assets)
        assert risk > 0
        assert risk <= 1.0  # Risk should be normalized
    
    def test_calculate_risk_level(self, quantum_service_instance):
        """Test risk level calculation"""
        # Test low risk
        risk_metrics = {'var_95': 50000, 'portfolio_value': 2500000}
        quantum_service_instance.riskMetrics = risk_metrics
        risk_level = quantum_service_instance._calculateRiskLevel()
        assert risk_level == 'Low'
        
        # Test medium risk
        risk_metrics = {'var_95': 100000, 'portfolio_value': 2500000}
        quantum_service_instance.riskMetrics = risk_metrics
        risk_level = quantum_service_instance._calculateRiskLevel()
        assert risk_level == 'Medium'
        
        # Test high risk
        risk_metrics = {'var_95': 150000, 'portfolio_value': 2500000}
        quantum_service_instance.riskMetrics = risk_metrics
        risk_level = quantum_service_instance._calculateRiskLevel()
        assert risk_level == 'High'


class TestVaultSecretsManager:
    """Test suite for Vault Secrets Manager"""
    
    @pytest.fixture
    def vault_manager(self):
        return VaultSecretsManager(vault_url="http://localhost:8200", vault_token="test-token")
    
    @pytest.mark.asyncio
    async def test_get_secret_with_vault(self, vault_manager):
        """Test getting secret from Vault"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "data": {
                    "data": {
                        "database_url": "postgresql://test:test@localhost:5432/test",
                        "password": "test-password"
                    }
                }
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await vault_manager.get_secret("database", "database_url")
            assert result == "postgresql://test:test@localhost:5432/test"
    
    @pytest.mark.asyncio
    async def test_get_secret_local_fallback(self, vault_manager):
        """Test local fallback when Vault is unavailable"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await vault_manager.get_secret("database", "database_url")
            # Should return default secret
            assert "postgresql://" in result
    
    @pytest.mark.asyncio
    async def test_set_secret(self, vault_manager):
        """Test setting secret in Vault"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_post.return_value.__aenter__.return_value = mock_response
            
            secrets = {"database_url": "postgresql://test:test@localhost:5432/test"}
            result = await vault_manager.set_secret("database", secrets)
            assert result is True
    
    @pytest.mark.asyncio
    async def test_rotate_secret(self, vault_manager):
        """Test secret rotation"""
        with patch.object(vault_manager, 'get_secret') as mock_get:
            with patch.object(vault_manager, 'set_secret') as mock_set:
                mock_get.return_value = "old-secret"
                mock_set.return_value = True
                
                result = await vault_manager.rotate_secret("database", "password")
                assert result is True
                mock_set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_database_config(self, vault_manager):
        """Test getting database configuration"""
        with patch.object(vault_manager, 'get_secret') as mock_get:
            mock_get.return_value = {
                "url": "postgresql://test:test@localhost:5432/test",
                "password": "test-password",
                "username": "test"
            }
            
            result = await vault_manager.get_database_config()
            assert "url" in result
            assert "password" in result
            assert "username" in result
    
    @pytest.mark.asyncio
    async def test_get_api_key(self, vault_manager):
        """Test getting API key"""
        with patch.object(vault_manager, 'get_secret') as mock_get:
            mock_get.return_value = {
                "openweathermap": "test-api-key",
                "ice": "test-ice-key"
            }
            
            result = await vault_manager.get_api_key("openweathermap")
            assert result == "test-api-key"
    
    @pytest.mark.asyncio
    async def test_health_check(self, vault_manager):
        """Test Vault health check"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"status": "ok"})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await vault_manager.health_check()
            assert result["status"] == "healthy"
            assert result["vault_available"] is True


class TestIntegration:
    """Integration tests for consolidated services"""
    
    @pytest.mark.asyncio
    async def test_ai_quantum_integration(self):
        """Test integration between AI and Quantum services"""
        # Create sample portfolio data
        portfolio = [
            {'symbol': 'WTI', 'value': 1000000, 'volatility': 0.25, 'weight': 0.5},
            {'symbol': 'BRENT', 'value': 800000, 'volatility': 0.22, 'weight': 0.3},
            {'symbol': 'NATURAL_GAS', 'value': 700000, 'volatility': 0.30, 'weight': 0.2}
        ]
        
        # Get AI price prediction
        ai_result = await ai_service.predict_price('crude_oil', days_ahead=7, method='ensemble')
        
        # Calculate quantum VaR
        var_result = await quantum_service.calculate_quantum_var(portfolio, 0.95, 1)
        
        # Verify both services work together
        assert ai_result['commodity'] == 'crude_oil'
        assert var_result['var_amount'] > 0
        assert ai_result['esg_score']['overall_score'] > 0
    
    @pytest.mark.asyncio
    async def test_secrets_integration(self):
        """Test integration with secrets management"""
        # Test getting database config
        db_config = await secrets_manager.get_database_config()
        assert 'url' in db_config
        
        # Test getting API key
        api_key = await secrets_manager.get_api_key('openweathermap')
        assert api_key is not None
        
        # Test health check
        health = await secrets_manager.health_check()
        assert 'status' in health


# Performance tests
class TestPerformance:
    """Performance tests for consolidated services"""
    
    @pytest.mark.asyncio
    async def test_ai_service_performance(self):
        """Test AI service performance"""
        start_time = datetime.now()
        
        result = await ai_service.predict_price('crude_oil', days_ahead=7, method='ensemble')
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should complete within 5 seconds
        assert duration < 5.0
        assert result['commodity'] == 'crude_oil'
    
    @pytest.mark.asyncio
    async def test_quantum_service_performance(self):
        """Test quantum service performance"""
        assets = [
            PortfolioAsset('WTI', 0.12, 0.25, 'energy', 'global', 65.0),
            PortfolioAsset('BRENT', 0.10, 0.22, 'energy', 'global', 70.0)
        ]
        
        start_time = datetime.now()
        
        result = await quantum_service.optimize_portfolio_quantum(assets, 0.10, 0.5, 50)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should complete within 10 seconds
        assert duration < 10.0
        assert result['expected_return'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
