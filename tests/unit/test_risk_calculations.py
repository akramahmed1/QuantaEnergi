"""
Unit tests for Risk Calculation Tasks
Tests Celery-based risk calculation functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import numpy as np

from app.tasks.risk_calculations import (
    calculate_var_monte_carlo,
    calculate_portfolio_var,
    calculate_stress_test,
    calculate_daily_var,
    _monte_carlo_chunk,
    _get_portfolio_data,
    _get_tenant_portfolio_ids,
    _calculate_additional_risk_metrics
)


class TestMonteCarloVaR:
    """Test cases for Monte Carlo VaR calculation"""
    
    @pytest.fixture
    def sample_portfolio_data(self):
        """Sample portfolio data for testing"""
        return {
            "positions": [
                {
                    "commodity": "crude_oil",
                    "quantity": 1000,
                    "current_price": 85.50
                },
                {
                    "commodity": "natural_gas",
                    "quantity": 5000,
                    "current_price": 3.45
                }
            ],
            "market_data": {
                "crude_oil": {"volatility": 0.02},
                "natural_gas": {"volatility": 0.03}
            }
        }
    
    @pytest.mark.asyncio
    async def test_calculate_var_monte_carlo_success(self, sample_portfolio_data):
        """Test successful Monte Carlo VaR calculation"""
        with patch('app.tasks.risk_calculations.ProcessPoolExecutor') as mock_executor:
            with patch('app.tasks.risk_calculations.mp.cpu_count', return_value=4):
                # Mock executor context manager
                mock_executor_instance = Mock()
                mock_executor.return_value.__enter__.return_value = mock_executor_instance
                
                # Mock futures
                mock_futures = []
                for i in range(4):
                    mock_future = Mock()
                    mock_future.result.return_value = [100.0, -50.0, 200.0, -100.0]
                    mock_futures.append(mock_future)
                
                mock_executor_instance.submit.return_value = mock_futures[0]
                
                # Create a mock task
                mock_task = Mock()
                mock_task.request.id = "test-task-id"
                mock_task.retry = Mock()
                
                with patch('app.tasks.risk_calculations.current_task', mock_task):
                    result = calculate_var_monte_carlo(
                        sample_portfolio_data,
                        confidence_level=0.95,
                        num_simulations=1000,
                        tenant_id="test-tenant"
                    )
                
                assert result["var_value"] is not None
                assert result["confidence_level"] == 0.95
                assert result["tenant_id"] == "test-tenant"
                assert "calculation_time" in result
                assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_calculate_var_monte_carlo_invalid_data(self):
        """Test Monte Carlo VaR calculation with invalid data"""
        invalid_data = {"positions": [], "market_data": {}}
        
        mock_task = Mock()
        mock_task.request.id = "test-task-id"
        mock_task.retry = Mock()
        
        with patch('app.tasks.risk_calculations.current_task', mock_task):
            with pytest.raises(Exception):
                calculate_var_monte_carlo(invalid_data, tenant_id="test-tenant")
    
    @pytest.mark.asyncio
    async def test_calculate_var_monte_carlo_retry(self, sample_portfolio_data):
        """Test Monte Carlo VaR calculation with retry"""
        mock_task = Mock()
        mock_task.request.id = "test-task-id"
        mock_task.retry = Mock(side_effect=Exception("Retry"))
        
        with patch('app.tasks.risk_calculations.ProcessPoolExecutor') as mock_executor:
            mock_executor.side_effect = Exception("Processing error")
            
            with patch('app.tasks.risk_calculations.current_task', mock_task):
                with pytest.raises(Exception, match="Retry"):
                    calculate_var_monte_carlo(sample_portfolio_data, tenant_id="test-tenant")
    
    def test_monte_carlo_chunk(self, sample_portfolio_data):
        """Test Monte Carlo chunk calculation"""
        positions = sample_portfolio_data["positions"]
        market_data = sample_portfolio_data["market_data"]
        confidence_level = 0.95
        num_simulations = 100
        time_horizon = 1
        
        with patch('app.tasks.risk_calculations.np.random.normal') as mock_normal:
            with patch('app.tasks.risk_calculations.np.exp') as mock_exp:
                mock_normal.return_value = 0.01
                mock_exp.return_value = 1.01
                
                results = _monte_carlo_chunk(
                    positions, market_data, confidence_level, num_simulations, time_horizon
                )
                
                assert len(results) == num_simulations
                assert all(isinstance(result, float) for result in results)


class TestPortfolioVaR:
    """Test cases for portfolio VaR calculation"""
    
    @pytest.mark.asyncio
    async def test_calculate_portfolio_var_success(self):
        """Test successful portfolio VaR calculation"""
        portfolio_id = "test-portfolio"
        tenant_id = "test-tenant"
        
        mock_task = Mock()
        mock_task.request.id = "test-task-id"
        mock_task.retry = Mock()
        
        with patch('app.tasks.risk_calculations._get_portfolio_data') as mock_get_data:
            with patch('app.tasks.risk_calculations.calculate_var_monte_carlo') as mock_calculate_var:
                with patch('app.tasks.risk_calculations._calculate_additional_risk_metrics') as mock_risk_metrics:
                    mock_get_data.return_value = {"positions": [], "market_data": {}}
                    mock_calculate_var.delay.return_value.get.return_value = {
                        "var_95": 1000.0,
                        "var_99": 1500.0
                    }
                    mock_risk_metrics.return_value = {"portfolio_volatility": 0.02}
                    
                    with patch('app.tasks.risk_calculations.current_task', mock_task):
                        result = calculate_portfolio_var(portfolio_id, tenant_id)
                    
                    assert result["portfolio_id"] == portfolio_id
                    assert result["tenant_id"] == tenant_id
                    assert "var_results" in result
                    assert "risk_metrics" in result
                    assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_calculate_portfolio_var_failure(self):
        """Test portfolio VaR calculation failure"""
        portfolio_id = "test-portfolio"
        tenant_id = "test-tenant"
        
        mock_task = Mock()
        mock_task.request.id = "test-task-id"
        mock_task.retry = Mock(side_effect=Exception("Retry"))
        
        with patch('app.tasks.risk_calculations._get_portfolio_data') as mock_get_data:
            mock_get_data.side_effect = Exception("Data error")
            
            with patch('app.tasks.risk_calculations.current_task', mock_task):
                with pytest.raises(Exception, match="Retry"):
                    calculate_portfolio_var(portfolio_id, tenant_id)


class TestStressTest:
    """Test cases for stress test calculation"""
    
    @pytest.mark.asyncio
    async def test_calculate_stress_test_success(self):
        """Test successful stress test calculation"""
        portfolio_id = "test-portfolio"
        scenario_data = {
            "scenario_name": "market_crash",
            "market_shocks": {
                "crude_oil": -0.3,
                "natural_gas": -0.2
            }
        }
        tenant_id = "test-tenant"
        
        mock_task = Mock()
        mock_task.request.id = "test-task-id"
        mock_task.retry = Mock()
        
        with patch('app.tasks.risk_calculations._get_portfolio_data') as mock_get_data:
            mock_get_data.return_value = {
                "positions": [
                    {
                        "commodity": "crude_oil",
                        "quantity": 1000,
                        "current_price": 85.50
                    }
                ]
            }
            
            with patch('app.tasks.risk_calculations.current_task', mock_task):
                result = calculate_stress_test(portfolio_id, scenario_data, tenant_id)
            
            assert result["portfolio_id"] == portfolio_id
            assert result["scenario_name"] == "market_crash"
            assert result["portfolio_loss"] is not None
            assert "position_losses" in result
            assert "market_shocks" in result
            assert result["tenant_id"] == tenant_id
    
    @pytest.mark.asyncio
    async def test_calculate_stress_test_failure(self):
        """Test stress test calculation failure"""
        portfolio_id = "test-portfolio"
        scenario_data = {"scenario_name": "test"}
        tenant_id = "test-tenant"
        
        mock_task = Mock()
        mock_task.request.id = "test-task-id"
        mock_task.retry = Mock(side_effect=Exception("Retry"))
        
        with patch('app.tasks.risk_calculations._get_portfolio_data') as mock_get_data:
            mock_get_data.side_effect = Exception("Data error")
            
            with patch('app.tasks.risk_calculations.current_task', mock_task):
                with pytest.raises(Exception, match="Retry"):
                    calculate_stress_test(portfolio_id, scenario_data, tenant_id)


class TestDailyVaR:
    """Test cases for daily VaR calculation"""
    
    @pytest.mark.asyncio
    async def test_calculate_daily_var_success(self):
        """Test successful daily VaR calculation"""
        tenant_id = "test-tenant"
        
        mock_task = Mock()
        mock_task.request.id = "test-task-id"
        mock_task.retry = Mock()
        
        with patch('app.tasks.risk_calculations._get_tenant_portfolio_ids') as mock_get_portfolios:
            with patch('app.tasks.risk_calculations.calculate_portfolio_var') as mock_calculate_var:
                with patch('app.tasks.risk_calculations.ThreadPoolExecutor') as mock_executor:
                    mock_get_portfolios.return_value = ["portfolio1", "portfolio2", "portfolio3"]
                    
                    # Mock executor
                    mock_executor_instance = Mock()
                    mock_executor.return_value.__enter__.return_value = mock_executor_instance
                    
                    # Mock futures
                    mock_futures = []
                    for i in range(3):
                        mock_future = Mock()
                        mock_future.result.return_value = {"portfolio_id": f"portfolio{i+1}"}
                        mock_futures.append((f"portfolio{i+1}", mock_future))
                    
                    mock_executor_instance.submit.return_value = mock_futures[0][1]
                    
                    with patch('app.tasks.risk_calculations.current_task', mock_task):
                        result = calculate_daily_var(tenant_id)
                    
                    assert result["summary"]["total_portfolios"] == 3
                    assert result["summary"]["successful_calculations"] == 3
                    assert result["summary"]["failed_calculations"] == 0
                    assert result["summary"]["tenant_id"] == tenant_id
                    assert "portfolio_results" in result
    
    @pytest.mark.asyncio
    async def test_calculate_daily_var_with_failures(self):
        """Test daily VaR calculation with some failures"""
        tenant_id = "test-tenant"
        
        mock_task = Mock()
        mock_task.request.id = "test-task-id"
        mock_task.retry = Mock()
        
        with patch('app.tasks.risk_calculations._get_tenant_portfolio_ids') as mock_get_portfolios:
            with patch('app.tasks.risk_calculations.calculate_portfolio_var') as mock_calculate_var:
                with patch('app.tasks.risk_calculations.ThreadPoolExecutor') as mock_executor:
                    mock_get_portfolios.return_value = ["portfolio1", "portfolio2"]
                    
                    # Mock executor
                    mock_executor_instance = Mock()
                    mock_executor.return_value.__enter__.return_value = mock_executor_instance
                    
                    # Mock futures with one failure
                    mock_future1 = Mock()
                    mock_future1.result.return_value = {"portfolio_id": "portfolio1"}
                    
                    mock_future2 = Mock()
                    mock_future2.result.side_effect = Exception("Calculation failed")
                    
                    mock_executor_instance.submit.return_value = mock_future1
                    
                    with patch('app.tasks.risk_calculations.current_task', mock_task):
                        result = calculate_daily_var(tenant_id)
                    
                    assert result["summary"]["total_portfolios"] == 2
                    assert result["summary"]["successful_calculations"] == 1
                    assert result["summary"]["failed_calculations"] == 1
    
    @pytest.mark.asyncio
    async def test_calculate_daily_var_failure(self):
        """Test daily VaR calculation failure"""
        tenant_id = "test-tenant"
        
        mock_task = Mock()
        mock_task.request.id = "test-task-id"
        mock_task.retry = Mock(side_effect=Exception("Retry"))
        
        with patch('app.tasks.risk_calculations._get_tenant_portfolio_ids') as mock_get_portfolios:
            mock_get_portfolios.side_effect = Exception("Database error")
            
            with patch('app.tasks.risk_calculations.current_task', mock_task):
                with pytest.raises(Exception, match="Retry"):
                    calculate_daily_var(tenant_id)


class TestHelperFunctions:
    """Test cases for helper functions"""
    
    def test_get_portfolio_data(self):
        """Test getting portfolio data"""
        portfolio_id = "test-portfolio"
        tenant_id = "test-tenant"
        
        result = _get_portfolio_data(portfolio_id, tenant_id)
        
        assert result["portfolio_id"] == portfolio_id
        assert "positions" in result
        assert "market_data" in result
        assert len(result["positions"]) > 0
        assert len(result["market_data"]) > 0
    
    def test_get_tenant_portfolio_ids(self):
        """Test getting tenant portfolio IDs"""
        tenant_id = "test-tenant"
        
        result = _get_tenant_portfolio_ids(tenant_id)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(pid, str) for pid in result)
    
    def test_calculate_additional_risk_metrics(self):
        """Test calculating additional risk metrics"""
        portfolio_data = {
            "positions": [
                {
                    "commodity": "crude_oil",
                    "quantity": 1000,
                    "current_price": 85.50
                },
                {
                    "commodity": "natural_gas",
                    "quantity": 5000,
                    "current_price": 3.45
                }
            ]
        }
        
        result = _calculate_additional_risk_metrics(portfolio_data)
        
        assert "portfolio_volatility" in result
        assert "concentration" in result
        assert "total_value" in result
        assert result["total_value"] > 0
        assert len(result["concentration"]) == 2


if __name__ == "__main__":
    pytest.main([__file__])
