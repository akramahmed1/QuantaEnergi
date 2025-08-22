"""
Unit tests for EnergyOpti-Pro services.

This module tests all the core services including market data, trading, risk management,
compliance, and AI/ML services.
"""

import pytest
import asyncio
from decimal import Decimal
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone

from energyopti_pro.services.market_data_service import MarketDataService
from energyopti_pro.services.trading_service import TradingService, OrderSide, OrderType, OrderStatus
from energyopti_pro.services.risk_management_service import RiskManagementService
from energyopti_pro.services.compliance_service import ComplianceService, ComplianceRegion, ComplianceStatus
from energyopti_pro.services.ai_ml_service import AIMLService


class TestMarketDataService:
    """Test cases for MarketDataService."""
    
    @pytest.mark.asyncio
    async def test_fetch_cme_prices_success(self, market_data_service):
        """Test successful CME price fetching."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"last": 75.50})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await market_data_service.fetch_cme_prices("crude_oil")
            
            assert result["source"] == "cme"
            assert result["data"] == 75.50
            assert "timestamp" in result
            assert result["exchange"] == "CME"
    
    @pytest.mark.asyncio
    async def test_fetch_cme_prices_fallback(self, market_data_service):
        """Test CME price fetching with fallback to simulated data."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await market_data_service.fetch_cme_prices("crude_oil")
            
            assert result["source"] == "simulated_cme"
            assert "data" in result
            assert result["exchange"] == "CME"
    
    @pytest.mark.asyncio
    async def test_get_market_overview(self, market_data_service):
        """Test market overview generation."""
        result = await market_data_service.get_market_overview("global")
        
        assert "region" in result
        assert result["region"] == "global"
        assert "timestamp" in result
        assert "market_status" in result
        assert "data_sources" in result
    
    @pytest.mark.asyncio
    async def test_get_commodity_prices(self, market_data_service):
        """Test commodity price fetching for multiple commodities."""
        commodities = ["crude_oil", "natural_gas", "brent_crude"]
        result = await market_data_service.get_commodity_prices(commodities)
        
        assert "commodities" in result
        assert "timestamp" in result
        assert "total_commodities" in result
        assert result["total_commodities"] == 3


class TestTradingService:
    """Test cases for TradingService."""
    
    def test_create_order_success(self, trading_service):
        """Test successful order creation."""
        order = asyncio.run(trading_service.create_order(
            user_id="test_user",
            commodity="crude_oil",
            exchange="CME",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("1000"),
            price=Decimal("75.50")
        ))
        
        assert order.id is not None
        assert order.user_id == "test_user"
        assert order.commodity == "crude_oil"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.LIMIT
        assert order.quantity == Decimal("1000")
        assert order.price == Decimal("75.50")
        assert order.status == OrderStatus.PENDING
    
    def test_create_order_validation(self, trading_service):
        """Test order creation validation."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            asyncio.run(trading_service.create_order(
                user_id="test_user",
                commodity="crude_oil",
                exchange="CME",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal("-1000"),
                price=Decimal("75.50")
            ))
    
    @pytest.mark.asyncio
    async def test_submit_order(self, trading_service):
        """Test order submission."""
        # Create order first
        order = await trading_service.create_order(
            user_id="test_user",
            commodity="crude_oil",
            exchange="CME",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("1000")
        )
        
        # Submit order
        submitted_order = await trading_service.submit_order(order.id)
        
        assert submitted_order.status in [OrderStatus.FILLED, OrderStatus.PARTIALLY_FILLED]
        assert submitted_order.updated_at > order.created_at
    
    @pytest.mark.asyncio
    async def test_cancel_order(self, trading_service):
        """Test order cancellation."""
        # Create and submit order
        order = await trading_service.create_order(
            user_id="test_user",
            commodity="crude_oil",
            exchange="CME",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("1000")
        )
        
        # Cancel order
        cancelled_order = await trading_service.cancel_order(order.id, "test_user")
        
        assert cancelled_order.status == OrderStatus.CANCELLED
    
    @pytest.mark.asyncio
    async def test_get_user_orders(self, trading_service):
        """Test retrieving user orders."""
        # Create multiple orders
        await trading_service.create_order(
            user_id="user1",
            commodity="crude_oil",
            exchange="CME",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("1000")
        )
        
        await trading_service.create_order(
            user_id="user2",
            commodity="natural_gas",
            exchange="NYMEX",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=Decimal("5000")
        )
        
        # Get orders for user1
        user1_orders = await trading_service.get_user_orders("user1")
        assert len(user1_orders) == 1
        assert user1_orders[0].commodity == "crude_oil"
        
        # Get orders for user2
        user2_orders = await trading_service.get_user_orders("user2")
        assert len(user2_orders) == 1
        assert user2_orders[0].commodity == "natural_gas"
    
    @pytest.mark.asyncio
    async def test_get_trading_summary(self, trading_service):
        """Test trading summary generation."""
        # Create some orders and positions
        await trading_service.create_order(
            user_id="test_user",
            commodity="crude_oil",
            exchange="CME",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("1000")
        )
        
        summary = await trading_service.get_trading_summary("test_user")
        
        assert "user_id" in summary
        assert "orders_summary" in summary
        assert "positions_summary" in summary
        assert "pnl_summary" in summary
        assert "timestamp" in summary


class TestRiskManagementService:
    """Test cases for RiskManagementService."""
    
    @pytest.mark.asyncio
    async def test_calculate_var(self, risk_management_service, mock_positions):
        """Test VaR calculation."""
        risk_metrics = await risk_management_service.calculate_var(mock_positions)
        
        assert risk_metrics.var_95 > 0
        assert risk_metrics.var_99 > 0
        assert risk_metrics.expected_shortfall > 0
        assert risk_metrics.volatility > 0
        assert risk_metrics.sharpe_ratio is not None
        assert risk_metrics.concentration_risk > 0
    
    @pytest.mark.asyncio
    async def test_check_position_limits(self, risk_management_service, mock_positions):
        """Test position limit checking."""
        compliance_check = await risk_management_service.check_position_limits(
            "test_user", mock_positions
        )
        
        assert "compliant" in compliance_check
        assert "violations" in compliance_check
        assert "warnings" in compliance_check
        assert "risk_metrics" in compliance_check
        assert "timestamp" in compliance_check
    
    @pytest.mark.asyncio
    async def test_perform_stress_test(self, risk_management_service, mock_positions, mock_stress_scenarios):
        """Test stress testing."""
        stress_results = await risk_management_service.perform_stress_test(
            mock_positions, mock_stress_scenarios
        )
        
        assert "scenarios" in stress_results
        assert "summary" in stress_results
        assert "timestamp" in stress_results
        assert len(stress_results["scenarios"]) == 3
    
    @pytest.mark.asyncio
    async def test_generate_risk_report(self, risk_management_service, mock_positions):
        """Test risk report generation."""
        risk_report = await risk_management_service.generate_risk_report(
            "test_user", mock_positions
        )
        
        assert "user_id" in risk_report
        assert "risk_score" in risk_report
        assert "risk_level" in risk_report
        assert "risk_metrics" in risk_report
        assert "compliance_status" in risk_report
        assert "stress_test_results" in risk_report
        assert "recommendations" in risk_report
        assert "timestamp" in risk_report


class TestComplianceService:
    """Test cases for ComplianceService."""
    
    @pytest.mark.asyncio
    async def test_check_compliance_success(self, compliance_service, mock_transaction_data, mock_user_profile, mock_compliance_region):
        """Test successful compliance check."""
        compliance_result = await compliance_service.check_compliance(
            "test_user",
            mock_compliance_region,
            mock_transaction_data,
            mock_user_profile
        )
        
        assert "user_id" in compliance_result
        assert "region" in compliance_result
        assert "overall_status" in compliance_result
        assert "rule_checks" in compliance_result
        assert "violations" in compliance_result
        assert "warnings" in compliance_result
        assert "timestamp" in compliance_result
    
    @pytest.mark.asyncio
    async def test_islamic_finance_compliance(self, compliance_service, mock_transaction_data):
        """Test Islamic finance compliance checking."""
        islamic_compliance = await compliance_service._check_islamic_finance_compliance(
            mock_transaction_data
        )
        
        assert "overall_status" in islamic_compliance
        assert "rule_checks" in islamic_compliance
        assert "violations" in islamic_compliance
        assert "warnings" in islamic_compliance
        assert "timestamp" in islamic_compliance
    
    @pytest.mark.asyncio
    async def test_get_compliance_history(self, compliance_service):
        """Test compliance history retrieval."""
        # First create some compliance checks
        await compliance_service.check_compliance(
            "test_user",
            ComplianceRegion.MIDDLE_EAST,
            {"test": "data"},
            {"test": "profile"}
        )
        
        history = await compliance_service.get_compliance_history()
        
        assert len(history) > 0
        assert all(hasattr(check, 'timestamp') for check in history)
    
    @pytest.mark.asyncio
    async def test_generate_compliance_report(self, compliance_service, mock_compliance_region):
        """Test compliance report generation."""
        report = await compliance_service.generate_compliance_report(
            "test_user",
            mock_compliance_region,
            30
        )
        
        assert "user_id" in report
        assert "region" in report
        assert "period" in report
        assert "statistics" in report
        assert "compliance_history" in report
        assert "recommendations" in report
        assert "timestamp" in report


class TestAIMLService:
    """Test cases for AIMLService."""
    
    @pytest.mark.asyncio
    async def test_forecast_energy_prices(self, ai_ml_service):
        """Test energy price forecasting."""
        forecast_results = await ai_ml_service.forecast_energy_prices(
            "crude_oil", forecast_horizon=7
        )
        
        assert len(forecast_results) == 7
        for result in forecast_results:
            assert hasattr(result, 'timestamp')
            assert hasattr(result, 'forecast_value')
            assert hasattr(result, 'lower_bound')
            assert hasattr(result, 'upper_bound')
            assert hasattr(result, 'confidence_level')
            assert hasattr(result, 'model_used')
            assert hasattr(result, 'accuracy_metrics')
    
    @pytest.mark.asyncio
    async def test_generate_trading_signals(self, ai_ml_service, mock_market_data, mock_user_profile):
        """Test trading signal generation."""
        signals = await ai_ml_service.generate_trading_signals(
            mock_market_data, mock_user_profile
        )
        
        assert len(signals) > 0
        for signal in signals:
            assert hasattr(signal, 'timestamp')
            assert hasattr(signal, 'commodity')
            assert hasattr(signal, 'signal_type')
            assert hasattr(signal, 'confidence')
            assert hasattr(signal, 'price_target')
            assert hasattr(signal, 'stop_loss')
            assert hasattr(signal, 'take_profit')
            assert hasattr(signal, 'reasoning')
            assert hasattr(signal, 'model_used')
    
    @pytest.mark.asyncio
    async def test_optimize_portfolio(self, ai_ml_service, mock_positions):
        """Test portfolio optimization."""
        optimization = await ai_ml_service.optimize_portfolio(
            mock_positions, risk_tolerance=0.5
        )
        
        assert hasattr(optimization, 'timestamp')
        assert hasattr(optimization, 'optimal_weights')
        assert hasattr(optimization, 'expected_return')
        assert hasattr(optimization, 'expected_volatility')
        assert hasattr(optimization, 'sharpe_ratio')
        assert hasattr(optimization, 'risk_metrics')
        assert hasattr(optimization, 'constraints_satisfied')
    
    @pytest.mark.asyncio
    async def test_run_quantum_optimization(self, ai_ml_service):
        """Test quantum optimization."""
        result = await ai_ml_service.run_quantum_optimization(
            "portfolio_optimization", {"test": "params"}
        )
        
        assert "optimal_weights" in result
        assert "quantum_advantage" in result
        assert "circuit_depth" in result
        assert "shots" in result
        assert "execution_time" in result
    
    @pytest.mark.asyncio
    async def test_train_rl_agent(self, ai_ml_service):
        """Test RL agent training."""
        training_data = {"episodes": 100, "rewards": [1, 2, 3]}
        hyperparameters = {"learning_rate": 0.001, "batch_size": 32}
        
        result = await ai_ml_service.train_rl_agent(
            "portfolio_optimization", training_data, hyperparameters
        )
        
        assert "agent_type" in result
        assert "training_episodes" in result
        assert "final_reward" in result
        assert "training_loss" in result
        assert "convergence_episode" in result
        assert "hyperparameters" in result
        assert "model_performance" in result
    
    @pytest.mark.asyncio
    async def test_get_ai_insights(self, ai_ml_service, mock_market_data, mock_user_profile):
        """Test AI insights generation."""
        insights = await ai_ml_service.get_ai_insights(
            mock_market_data, mock_user_profile
        )
        
        assert "timestamp" in insights
        assert "market_analysis" in insights
        assert "trading_recommendations" in insights
        assert "risk_assessment" in insights
        assert "portfolio_optimization" in insights
        assert "quantum_insights" in insights


# Integration tests
class TestServiceIntegration:
    """Integration tests for service interactions."""
    
    @pytest.mark.asyncio
    async def test_market_data_to_trading_flow(self, market_data_service, trading_service):
        """Test flow from market data to trading."""
        # Get market data
        market_overview = await market_data_service.get_market_overview()
        
        # Create trading order based on market data
        if "cme_crude" in market_overview:
            order = await trading_service.create_order(
                user_id="test_user",
                commodity="crude_oil",
                exchange="CME",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=Decimal("1000")
            )
            
            assert order is not None
            assert order.commodity == "crude_oil"
    
    @pytest.mark.asyncio
    async def test_trading_to_risk_management_flow(self, trading_service, risk_management_service):
        """Test flow from trading to risk management."""
        # Create and submit order
        order = await trading_service.create_order(
            user_id="test_user",
            commodity="crude_oil",
            exchange="CME",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("1000")
        )
        
        await trading_service.submit_order(order.id)
        
        # Get positions
        positions = await trading_service.get_user_positions("test_user")
        
        # Check risk
        if positions:
            risk_report = await risk_management_service.generate_risk_report(
                "test_user", positions
            )
            
            assert risk_report is not None
            assert "risk_score" in risk_report
    
    @pytest.mark.asyncio
    async def test_compliance_integration(self, compliance_service, trading_service, mock_compliance_region):
        """Test compliance integration with trading."""
        # Create order
        order = await trading_service.create_order(
            user_id="test_user",
            commodity="crude_oil",
            exchange="CME",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("1000")
        )
        
        # Check compliance
        transaction_data = {
            "transaction_id": order.id,
            "commodity": order.commodity,
            "quantity": float(order.quantity),
            "exchange": order.exchange,
            "user_id": order.user_id,
            "adnoc_certification": True,
            "data_consent": True
        }
        
        user_profile = {"islamic_finance_enabled": True}
        
        compliance_result = await compliance_service.check_compliance(
            order.user_id,
            mock_compliance_region,
            transaction_data,
            user_profile
        )
        
        assert compliance_result is not None
        assert "overall_status" in compliance_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
