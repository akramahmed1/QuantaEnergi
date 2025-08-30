from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import structlog

logger = structlog.get_logger()

class TradingStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    @abstractmethod
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the trading strategy"""
        pass
    
    @abstractmethod
    def get_risk_score(self) -> float:
        """Get the risk score for this strategy"""
        pass

class BaseTradingStrategy(TradingStrategy):
    """Base implementation of trading strategy"""
    
    def __init__(self, name: str, risk_level: float):
        self.name = name
        self.risk_level = risk_level
    
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute base trading strategy"""
        return {
            "strategy": self.name,
            "execution_time": datetime.now().isoformat(),
            "risk_level": self.risk_level,
            "status": "executed"
        }
    
    def get_risk_score(self) -> float:
        """Get base risk score"""
        return self.risk_level

class TradingStrategyDecorator(TradingStrategy):
    """Decorator base class for trading strategies"""
    
    def __init__(self, strategy: TradingStrategy):
        self._strategy = strategy
    
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute decorated strategy"""
        return self._strategy.execute(market_data)
    
    def get_risk_score(self) -> float:
        """Get decorated risk score"""
        return self._strategy.get_risk_score()

class RiskManagementDecorator(TradingStrategyDecorator):
    """Decorator that adds risk management to trading strategies"""
    
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with risk management"""
        base_result = self._strategy.execute(market_data)
        
        # Add risk management logic
        risk_assessment = self._assess_risk(market_data)
        
        base_result["risk_management"] = {
            "risk_assessment": risk_assessment,
            "stop_loss": self._calculate_stop_loss(market_data),
            "position_size": self._calculate_position_size(market_data)
        }
        
        return base_result
    
    def get_risk_score(self) -> float:
        """Get adjusted risk score with risk management"""
        base_score = self._strategy.get_risk_score()
        return max(0.1, base_score * 0.8)  # Reduce risk by 20%
    
    def _assess_risk(self, market_data: Dict[str, Any]) -> str:
        """Assess market risk"""
        volatility = market_data.get("volatility", 0)
        if volatility > 0.3:
            return "high"
        elif volatility > 0.15:
            return "medium"
        else:
            return "low"
    
    def _calculate_stop_loss(self, market_data: Dict[str, Any]) -> float:
        """Calculate stop loss level"""
        current_price = market_data.get("current_price", 100)
        volatility = market_data.get("volatility", 0.1)
        return current_price * (1 - volatility)
    
    def _calculate_position_size(self, market_data: Dict[str, Any]) -> float:
        """Calculate recommended position size"""
        risk_score = self.get_risk_score()
        return max(0.1, 1.0 - risk_score)

class ComplianceDecorator(TradingStrategyDecorator):
    """Decorator that adds compliance checks to trading strategies"""
    
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with compliance checks"""
        base_result = self._strategy.execute(market_data)
        
        # Add compliance checks
        compliance_status = self._check_compliance(market_data)
        
        base_result["compliance"] = {
            "status": compliance_status,
            "checks": self._run_compliance_checks(market_data),
            "timestamp": datetime.now().isoformat()
        }
        
        return base_result
    
    def get_risk_score(self) -> float:
        """Get compliance-adjusted risk score"""
        base_score = self._strategy.get_risk_score()
        return base_score  # Compliance doesn't change risk score
    
    def _check_compliance(self, market_data: Dict[str, Any]) -> str:
        """Check trading compliance"""
        # Basic compliance checks
        if market_data.get("market_hours", True):
            return "compliant"
        else:
            return "non_compliant"
    
    def _run_compliance_checks(self, market_data: Dict[str, Any]) -> List[str]:
        """Run all compliance checks"""
        checks = []
        
        # Market hours check
        if market_data.get("market_hours", True):
            checks.append("Market hours: PASS")
        else:
            checks.append("Market hours: FAIL")
        
        # Position limits check
        if market_data.get("position_size", 0) <= 1000:
            checks.append("Position limits: PASS")
        else:
            checks.append("Position limits: FAIL")
        
        return checks

class EnergyTradingService:
    """Main energy trading service using decorator pattern"""
    
    def __init__(self):
        self.strategies = {}
        self._initialize_strategies()
    
    def _initialize_strategies(self):
        """Initialize available trading strategies"""
        # Base strategies
        base_strategy = BaseTradingStrategy("Basic Energy Trading", 0.5)
        
        # Decorated strategies
        self.strategies["basic"] = base_strategy
        self.strategies["risk_managed"] = RiskManagementDecorator(base_strategy)
        self.strategies["compliant"] = ComplianceDecorator(base_strategy)
        self.strategies["full_featured"] = ComplianceDecorator(
            RiskManagementDecorator(base_strategy)
        )
    
    def execute_strategy(self, strategy_name: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific trading strategy"""
        if strategy_name not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        strategy = self.strategies[strategy_name]
        return strategy.execute(market_data)
    
    def get_strategy_risk_score(self, strategy_name: str) -> float:
        """Get risk score for a specific strategy"""
        if strategy_name not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        strategy = self.strategies[strategy_name]
        return strategy.get_risk_score()
    
    def list_strategies(self) -> List[str]:
        """List all available strategies"""
        return list(self.strategies.keys())
