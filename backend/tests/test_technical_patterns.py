"""
Test file for technical patterns implementation
Tests Factory, Decorator, Observer, and Strategy patterns
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# Add shared services to path
sys.path.append(str(Path(__file__).parent.parent.parent / "shared" / "services"))

from compliance_service import ComplianceRuleFactory, TradingStrategyFactory
from energy_trading import (
    BaseTradingStrategy, RiskManagementDecorator, ComplianceDecorator,
    MonitoringDecorator, PerformanceOptimizationDecorator,
    MarketEvent, MarketObserver, MarketSubject, MarketDataObserver,
    TradingSignalObserver, EnergyTradingService
)


class TestFactoryPattern:
    """Test Factory Pattern implementations"""
    
    def test_compliance_rule_factory_trading(self):
        """Test creating trading compliance rule"""
        from compliance_service import ComplianceRegion
        
        rule = ComplianceRuleFactory.create_rule("trading", ComplianceRegion.US_FERC)
        
        assert rule.rule_id.startswith("trading_us_ferc")
        assert rule.category == "trading"
        assert rule.requirements == ["Transaction reporting", "Price transparency", "Record keeping"]
        assert rule.status == "active"
    
    def test_compliance_rule_factory_environmental(self):
        """Test creating environmental compliance rule"""
        from compliance_service import ComplianceRegion
        
        rule = ComplianceRuleFactory.create_rule("environmental", ComplianceRegion.EU_ETS)
        
        assert rule.rule_id.startswith("environmental_eu_ets")
        assert rule.category == "environmental"
        assert "Emissions reporting" in rule.requirements
        assert "Carbon tracking" in rule.requirements
    
    def test_compliance_rule_factory_cybersecurity(self):
        """Test creating cybersecurity compliance rule"""
        from compliance_service import ComplianceRegion
        
        rule = ComplianceRuleFactory.create_rule("cybersecurity", ComplianceRegion.UK_ETS)
        
        assert rule.rule_id.startswith("cybersecurity_uk_ets")
        assert rule.category == "cybersecurity"
        assert "Data protection" in rule.requirements
        assert "Access controls" in rule.requirements
    
    def test_trading_strategy_factory_momentum(self):
        """Test creating momentum trading strategy"""
        market_conditions = {"volatility": "high"}
        strategy = TradingStrategyFactory.create_strategy("momentum", market_conditions, "conservative")
        
        assert strategy["strategy_id"].startswith("momentum_conservative")
        assert strategy["type"] == "momentum"
        assert strategy["risk_profile"] == "conservative"
        assert strategy["parameters"]["lookback_period"] == 5  # High volatility = shorter period
        assert strategy["parameters"]["position_size"] == 0.1  # Conservative = smaller position
    
    def test_trading_strategy_factory_mean_reversion(self):
        """Test creating mean reversion strategy"""
        market_conditions = {"volatility": "low"}
        strategy = TradingStrategyFactory.create_strategy("mean_reversion", market_conditions, "aggressive")
        
        assert strategy["strategy_id"].startswith("mean_reversion_aggressive")
        assert strategy["type"] == "mean_reversion"
        assert strategy["risk_profile"] == "aggressive"
        assert strategy["parameters"]["std_deviation"] == 1.5  # Aggressive = lower threshold
        assert strategy["parameters"]["position_size"] == 0.4  # Aggressive = larger position


class TestDecoratorPattern:
    """Test Decorator Pattern implementations"""
    
    def test_base_strategy(self):
        """Test base trading strategy"""
        strategy = BaseTradingStrategy("Test Strategy", 0.6)
        market_data = {"current_price": 100}
        
        result = strategy.execute(market_data)
        
        assert result["strategy"] == "Test Strategy"
        assert result["risk_level"] == 0.6
        assert result["status"] == "executed"
        assert strategy.get_risk_score() == 0.6
    
    def test_risk_management_decorator(self):
        """Test risk management decorator"""
        base_strategy = BaseTradingStrategy("Test Strategy", 0.6)
        risk_decorator = RiskManagementDecorator(base_strategy)
        market_data = {"current_price": 100, "volatility": 0.2}
        
        result = risk_decorator.execute(market_data)
        
        assert "risk_management" in result
        assert result["risk_management"]["risk_assessment"] == "medium"
        assert result["risk_management"]["stop_loss"] == 80.0  # 100 * (1 - 0.2)
        assert result["risk_management"]["position_size"] == 0.52  # 1.0 - 0.48 (0.6 * 0.8)
        assert risk_decorator.get_risk_score() == 0.48  # 0.6 * 0.8
    
    def test_compliance_decorator(self):
        """Test compliance decorator"""
        base_strategy = BaseTradingStrategy("Test Strategy", 0.6)
        compliance_decorator = ComplianceDecorator(base_strategy)
        market_data = {"market_hours": True, "position_size": 500}
        
        result = compliance_decorator.execute(market_data)
        
        assert "compliance" in result
        assert result["compliance"]["status"] == "compliant"
        assert "Market hours: PASS" in result["compliance"]["checks"]
        assert "Position limits: PASS" in result["compliance"]["checks"]
        assert compliance_decorator.get_risk_score() == 0.6  # Compliance doesn't change risk
    
    def test_monitoring_decorator(self):
        """Test monitoring decorator"""
        base_strategy = BaseTradingStrategy("Test Strategy", 0.6)
        monitoring_decorator = MonitoringDecorator(base_strategy)
        market_data = {"current_price": 100}
        
        result = monitoring_decorator.execute(market_data)
        
        assert "monitoring" in result
        assert "execution_time_ms" in result["monitoring"]
        assert "performance_metrics" in result["monitoring"]
        assert result["monitoring"]["performance_metrics"]["success_rate"] == 1.0
    
    def test_performance_optimization_decorator(self):
        """Test performance optimization decorator"""
        base_strategy = BaseTradingStrategy("Test Strategy", 0.6)
        optimization_decorator = PerformanceOptimizationDecorator(base_strategy)
        market_data = {"current_price": 100}
        
        # First execution
        result1 = optimization_decorator.execute(market_data)
        assert result1["performance_optimization"]["cached"] == False
        assert result1["performance_optimization"]["cache_hit"] == False
        
        # Second execution (should be cached)
        result2 = optimization_decorator.execute(market_data)
        assert result2["performance_optimization"]["cached"] == True
        assert result2["performance_optimization"]["cache_hit"] == True
    
    def test_decorator_chain(self):
        """Test multiple decorators chained together"""
        base_strategy = BaseTradingStrategy("Test Strategy", 0.6)
        
        # Chain multiple decorators
        decorated_strategy = ComplianceDecorator(
            RiskManagementDecorator(
                MonitoringDecorator(base_strategy)
            )
        )
        
        market_data = {"current_price": 100, "volatility": 0.2, "market_hours": True}
        result = decorated_strategy.execute(market_data)
        
        # Check all decorators are applied
        assert "risk_management" in result
        assert "compliance" in result
        assert "monitoring" in result
        assert result["compliance"]["status"] == "compliant"
        assert result["risk_management"]["risk_assessment"] == "medium"


class TestObserverPattern:
    """Test Observer Pattern implementations"""
    
    def test_market_event_creation(self):
        """Test market event creation"""
        data = {"symbol": "OIL", "price": 75.50}
        event = MarketEvent("price_change", data)
        
        assert event.event_type == "price_change"
        assert event.data == data
        assert event.event_id.startswith("price_change_")
        assert isinstance(event.timestamp, datetime)
    
    def test_market_subject_attach_detach(self):
        """Test attaching and detaching observers"""
        subject = MarketSubject()
        observer = Mock(spec=MarketObserver)
        
        # Attach observer
        subject.attach(observer)
        assert len(subject._observers) == 1
        assert observer in subject._observers
        
        # Detach observer
        subject.detach(observer)
        assert len(subject._observers) == 0
        assert observer not in subject._observers
    
    def test_market_subject_notify(self):
        """Test notifying observers"""
        subject = MarketSubject()
        observer1 = Mock(spec=MarketObserver)
        observer2 = Mock(spec=MarketObserver)
        
        subject.attach(observer1)
        subject.attach(observer2)
        
        event = MarketEvent("test", {"data": "test"})
        subject.notify(event)
        
        # Check both observers were notified
        observer1.update.assert_called_once_with(event)
        observer2.update.assert_called_once_with(event)
    
    def test_market_data_observer(self):
        """Test market data observer"""
        observer = MarketDataObserver("Test Market")
        event = MarketEvent("price_change", {
            "symbol": "OIL",
            "price_change": 2.50,
            "percentage_change": 3.4
        })
        
        observer.update(event)
        
        assert observer.last_update == event.timestamp
        assert observer.update_count == 1
    
    def test_trading_signal_observer(self):
        """Test trading signal observer"""
        observer = TradingSignalObserver("Test Strategy")
        event = MarketEvent("trading_signal", {
            "signal_type": "buy",
            "symbol": "OIL",
            "confidence": 0.8
        })
        
        observer.update(event)
        
        assert observer.signals_generated == 1
        assert observer.last_signal == event.timestamp


class TestEnergyTradingService:
    """Test the main energy trading service"""
    
    def test_service_initialization(self):
        """Test service initialization with decorators and observers"""
        service = EnergyTradingService()
        
        # Check strategies are initialized
        assert "basic" in service.strategies
        assert "risk_managed" in service.strategies
        assert "compliant" in service.strategies
        assert "monitored" in service.strategies
        assert "optimized" in service.strategies
        assert "full_featured" in service.strategies
        
        # Check observers are attached
        assert len(service._observers) == 2  # Market data and trading signal observers
    
    def test_strategy_execution(self):
        """Test strategy execution"""
        service = EnergyTradingService()
        market_data = {"current_price": 100, "volatility": 0.2, "market_hours": True}
        
        # Test basic strategy
        result = service.execute_strategy("basic", market_data)
        assert result["strategy"] == "Basic Energy Trading"
        assert result["status"] == "executed"
        
        # Test risk managed strategy
        result = service.execute_strategy("risk_managed", market_data)
        assert "risk_management" in result
        assert result["risk_management"]["risk_assessment"] == "medium"
    
    def test_market_event_publishing(self):
        """Test publishing market events"""
        service = EnergyTradingService()
        
        # Mock the notify method to verify it's called
        with patch.object(service, 'notify') as mock_notify:
            service.publish_market_event("price_change", {"symbol": "OIL", "price": 75.50})
            
            # Verify notify was called
            mock_notify.assert_called_once()
            event = mock_notify.call_args[0][0]
            assert event.event_type == "price_change"
            assert event.data["symbol"] == "OIL"
    
    def test_strategy_risk_scores(self):
        """Test risk scores for different strategies"""
        service = EnergyTradingService()
        
        # Basic strategy should have original risk score
        basic_score = service.get_strategy_risk_score("basic")
        assert basic_score == 0.5
        
        # Risk managed strategy should have reduced risk score
        risk_managed_score = service.get_strategy_risk_score("risk_managed")
        assert risk_managed_score == 0.4  # 0.5 * 0.8
        
        # Other strategies should maintain original risk score
        compliant_score = service.get_strategy_risk_score("compliant")
        assert compliant_score == 0.5
    
    def test_list_strategies(self):
        """Test listing available strategies"""
        service = EnergyTradingService()
        strategies = service.list_strategies()
        
        expected_strategies = [
            "basic", "risk_managed", "compliant", "monitored", 
            "optimized", "full_featured"
        ]
        
        for strategy in expected_strategies:
            assert strategy in strategies


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
