"""
Risk Management Service for EnergyOpti-Pro.

Handles VaR calculations, stress testing, position limits, and compliance monitoring.
"""

import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import structlog
from dataclasses import dataclass
import numpy as np
from enum import Enum

logger = structlog.get_logger()

class RiskLevel(Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskMetrics:
    """Risk metrics for a portfolio or position."""
    var_95: Decimal  # 95% Value at Risk
    var_99: Decimal  # 99% Value at Risk
    expected_shortfall: Decimal  # Expected Shortfall (Conditional VaR)
    max_drawdown: Decimal  # Maximum historical drawdown
    sharpe_ratio: Decimal  # Risk-adjusted return
    volatility: Decimal  # Portfolio volatility
    correlation_risk: Decimal  # Correlation risk measure
    concentration_risk: Decimal  # Position concentration risk
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

@dataclass
class PositionLimit:
    """Position limit configuration."""
    commodity: str
    max_position_size: Decimal
    max_daily_loss: Decimal
    max_concentration: Decimal  # Max % of portfolio
    var_limit: Decimal  # Max VaR limit
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

class RiskManagementService:
    """Comprehensive risk management service with real-time monitoring."""
    
    def __init__(self):
        self.position_limits: Dict[str, PositionLimit] = {}
        self.risk_alerts: List[Dict[str, Any]] = []
        self.historical_data: Dict[str, List[float]] = {}
        self.correlation_matrix: Dict[str, Dict[str, float]] = {}
        
        # Initialize default position limits
        self._initialize_default_limits()
    
    def _initialize_default_limits(self):
        """Initialize default position limits for common commodities."""
        default_limits = {
            "crude_oil": PositionLimit(
                commodity="crude_oil",
                max_position_size=Decimal("1000000"),  # $1M
                max_daily_loss=Decimal("100000"),     # $100K
                max_concentration=Decimal("0.25"),    # 25%
                var_limit=Decimal("50000")            # $50K
            ),
            "natural_gas": PositionLimit(
                commodity="natural_gas",
                max_position_size=Decimal("500000"),  # $500K
                max_daily_loss=Decimal("50000"),      # $50K
                max_concentration=Decimal("0.20"),    # 20%
                var_limit=Decimal("25000")            # $25K
            ),
            "brent_crude": PositionLimit(
                commodity="brent_crude",
                max_position_size=Decimal("800000"),  # $800K
                max_daily_loss=Decimal("80000"),      # $80K
                max_concentration=Decimal("0.22"),    # 22%
                var_limit=Decimal("40000")            # $40K
            )
        }
        
        for commodity, limit in default_limits.items():
            self.position_limits[commodity] = limit
    
    async def calculate_var(
        self,
        positions: List[Dict[str, Any]],
        confidence_level: float = 0.95,
        time_horizon: int = 1
    ) -> RiskMetrics:
        """Calculate Value at Risk (VaR) for a portfolio."""
        try:
            if not positions:
                return RiskMetrics(
                    var_95=Decimal("0"),
                    var_99=Decimal("0"),
                    expected_shortfall=Decimal("0"),
                    max_drawdown=Decimal("0"),
                    sharpe_ratio=Decimal("0"),
                    volatility=Decimal("0"),
                    correlation_risk=Decimal("0"),
                    concentration_risk=Decimal("0")
                )
            
            # Extract position data
            position_values = []
            weights = []
            total_value = Decimal("0")
            
            for position in positions:
                value = position.get("quantity", 0) * position.get("current_price", 0)
                position_values.append(float(value))
                total_value += value
                weights.append(float(value))
            
            if total_value == 0:
                return RiskMetrics(
                    var_95=Decimal("0"),
                    var_99=Decimal("0"),
                    expected_shortfall=Decimal("0"),
                    max_drawdown=Decimal("0"),
                    sharpe_ratio=Decimal("0"),
                    volatility=Decimal("0"),
                    correlation_risk=Decimal("0"),
                    concentration_risk=Decimal("0")
                )
            
            # Normalize weights
            weights = np.array(weights) / float(total_value)
            
            # Simulate historical returns (in real implementation, use actual market data)
            returns = self._simulate_historical_returns(len(positions), 252)  # 252 trading days
            
            # Calculate portfolio returns
            portfolio_returns = np.dot(returns, weights)
            
            # Calculate VaR
            var_95 = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
            var_99 = np.percentile(portfolio_returns, (1 - 0.99) * 100)
            
            # Calculate Expected Shortfall
            es_threshold = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
            expected_shortfall = np.mean(portfolio_returns[portfolio_returns <= es_threshold])
            
            # Calculate other risk metrics
            volatility = np.std(portfolio_returns) * np.sqrt(252)  # Annualized
            sharpe_ratio = np.mean(portfolio_returns) / np.std(portfolio_returns) if np.std(portfolio_returns) > 0 else 0
            
            # Calculate maximum drawdown
            cumulative_returns = np.cumprod(1 + portfolio_returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdown)
            
            # Calculate concentration risk
            concentration_risk = np.max(weights)
            
            # Calculate correlation risk (simplified)
            correlation_risk = self._calculate_correlation_risk(positions)
            
            return RiskMetrics(
                var_95=Decimal(str(abs(var_95 * float(total_value)))),
                var_99=Decimal(str(abs(var_99 * float(total_value)))),
                expected_shortfall=Decimal(str(abs(expected_shortfall * float(total_value)))),
                max_drawdown=Decimal(str(abs(max_drawdown * float(total_value)))),
                sharpe_ratio=Decimal(str(sharpe_ratio)),
                volatility=Decimal(str(volatility)),
                correlation_risk=Decimal(str(correlation_risk)),
                concentration_risk=Decimal(str(concentration_risk))
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate VaR: {e}")
            raise
    
    def _simulate_historical_returns(self, num_positions: int, num_days: int) -> np.ndarray:
        """Simulate historical returns for risk calculations."""
        try:
            # Generate correlated random returns
            np.random.seed(42)  # For reproducible results
            
            # Base volatility for energy commodities
            base_volatility = 0.25  # 25% annual volatility
            
            # Generate returns with some correlation
            returns = np.random.normal(0, base_volatility / np.sqrt(252), (num_days, num_positions))
            
            # Add correlation structure (energy commodities tend to be correlated)
            correlation = 0.3
            for i in range(num_positions):
                for j in range(i + 1, num_positions):
                    returns[:, j] = correlation * returns[:, i] + np.sqrt(1 - correlation**2) * returns[:, j]
            
            return returns
            
        except Exception as e:
            logger.error(f"Failed to simulate historical returns: {e}")
            # Return uncorrelated returns as fallback
            return np.random.normal(0, 0.25 / np.sqrt(252), (num_days, num_positions))
    
    def _calculate_correlation_risk(self, positions: List[Dict[str, Any]]) -> float:
        """Calculate correlation risk for positions."""
        try:
            if len(positions) <= 1:
                return 0.0
            
            # Extract commodity types
            commodities = [pos.get("commodity", "unknown") for pos in positions]
            
            # Define commodity correlations (simplified)
            commodity_correlations = {
                "crude_oil": {"natural_gas": 0.3, "brent_crude": 0.95, "heating_oil": 0.8},
                "natural_gas": {"crude_oil": 0.3, "brent_crude": 0.25, "heating_oil": 0.2},
                "brent_crude": {"crude_oil": 0.95, "natural_gas": 0.25, "heating_oil": 0.85}
            }
            
            # Calculate average correlation
            total_correlation = 0.0
            correlation_count = 0
            
            for i, commodity1 in enumerate(commodities):
                for j, commodity2 in enumerate(commodities[i+1:], i+1):
                    if commodity1 in commodity_correlations and commodity2 in commodity_correlations[commodity1]:
                        total_correlation += commodity_correlations[commodity1][commodity2]
                        correlation_count += 1
            
            if correlation_count > 0:
                return total_correlation / correlation_count
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Failed to calculate correlation risk: {e}")
            return 0.0
    
    async def check_position_limits(
        self,
        user_id: str,
        positions: List[Dict[str, Any]],
        new_order: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Check if positions comply with risk limits."""
        try:
            violations = []
            warnings = []
            
            for position in positions:
                commodity = position.get("commodity", "unknown")
                
                if commodity not in self.position_limits:
                    continue
                
                limit = self.position_limits[commodity]
                position_value = position.get("quantity", 0) * position.get("current_price", 0)
                
                # Check position size limit
                if position_value > limit.max_position_size:
                    violations.append({
                        "type": "position_size_exceeded",
                        "commodity": commodity,
                        "current_value": position_value,
                        "limit": limit.max_position_size,
                        "severity": "high"
                    })
                
                # Check concentration limit
                total_portfolio_value = sum(pos.get("quantity", 0) * pos.get("current_price", 0) 
                                         for pos in positions)
                concentration = position_value / total_portfolio_value if total_portfolio_value > 0 else 0
                
                if concentration > limit.max_concentration:
                    warnings.append({
                        "type": "concentration_warning",
                        "commodity": commodity,
                        "current_concentration": concentration,
                        "limit": limit.max_concentration,
                        "severity": "medium"
                    })
            
            # Check VaR limits
            risk_metrics = await self.calculate_var(positions)
            
            for commodity, limit in self.position_limits.items():
                if risk_metrics.var_95 > limit.var_limit:
                    violations.append({
                        "type": "var_limit_exceeded",
                        "commodity": commodity,
                        "current_var": risk_metrics.var_95,
                        "limit": limit.var_limit,
                        "severity": "critical"
                    })
            
            return {
                "compliant": len(violations) == 0,
                "violations": violations,
                "warnings": warnings,
                "risk_metrics": risk_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to check position limits: {e}")
            raise
    
    async def perform_stress_test(
        self,
        positions: List[Dict[str, Any]],
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform stress testing under various market scenarios."""
        try:
            stress_test_results = {}
            
            for scenario in scenarios:
                scenario_name = scenario.get("name", "unknown")
                price_shock = scenario.get("price_shock", 0.0)
                volatility_shock = scenario.get("volatility_shock", 1.0)
                
                # Apply scenario to positions
                stressed_positions = []
                for position in positions:
                    stressed_position = position.copy()
                    
                    # Apply price shock
                    current_price = position.get("current_price", 0)
                    stressed_price = current_price * (1 + price_shock)
                    stressed_position["current_price"] = stressed_price
                    
                    # Calculate stressed P&L
                    quantity = position.get("quantity", 0)
                    original_value = quantity * current_price
                    stressed_value = quantity * stressed_price
                    stressed_pnl = stressed_value - original_value
                    
                    stressed_position["stressed_pnl"] = stressed_pnl
                    stressed_positions.append(stressed_position)
                
                # Calculate stressed VaR
                stressed_risk_metrics = await self.calculate_var(stressed_positions)
                
                stress_test_results[scenario_name] = {
                    "price_shock": price_shock,
                    "volatility_shock": volatility_shock,
                    "total_pnl_impact": sum(pos.get("stressed_pnl", 0) for pos in stressed_positions),
                    "stressed_var_95": stressed_risk_metrics.var_95,
                    "stressed_var_99": stressed_risk_metrics.var_99,
                    "positions_impact": stressed_positions
                }
            
            return {
                "scenarios": stress_test_results,
                "summary": {
                    "worst_case_pnl": min(result["total_pnl_impact"] for result in stress_test_results.values()),
                    "worst_case_var": max(result["stressed_var_95"] for result in stress_test_results.values()),
                    "scenarios_tested": len(scenarios)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to perform stress test: {e}")
            raise
    
    async def generate_risk_report(
        self,
        user_id: str,
        positions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive risk report."""
        try:
            # Calculate risk metrics
            risk_metrics = await self.calculate_var(positions)
            
            # Check compliance
            compliance_check = await self.check_position_limits(user_id, positions)
            
            # Perform stress testing
            stress_scenarios = [
                {"name": "market_crash", "price_shock": -0.20, "volatility_shock": 2.0},
                {"name": "moderate_decline", "price_shock": -0.10, "volatility_shock": 1.5},
                {"name": "volatility_spike", "price_shock": 0.0, "volatility_shock": 2.5}
            ]
            
            stress_test_results = await self.perform_stress_test(positions, stress_scenarios)
            
            # Generate risk score
            risk_score = self._calculate_risk_score(risk_metrics, compliance_check)
            
            return {
                "user_id": user_id,
                "risk_score": risk_score,
                "risk_level": self._get_risk_level(risk_score),
                "risk_metrics": risk_metrics,
                "compliance_status": compliance_check,
                "stress_test_results": stress_test_results,
                "recommendations": self._generate_recommendations(risk_metrics, compliance_check),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate risk report: {e}")
            raise
    
    def _calculate_risk_score(self, risk_metrics: RiskMetrics, compliance_check: Dict[str, Any]) -> float:
        """Calculate overall risk score (0-100, higher = more risky)."""
        try:
            score = 0.0
            
            # VaR contribution (40% weight)
            var_score = min(100, float(risk_metrics.var_99) / 100000 * 100)  # Normalize to $100K
            score += var_score * 0.4
            
            # Volatility contribution (20% weight)
            vol_score = min(100, float(risk_metrics.volatility) * 100)
            score += vol_score * 0.2
            
            # Concentration risk (20% weight)
            conc_score = float(risk_metrics.concentration_risk) * 100
            score += conc_score * 0.2
            
            # Compliance violations (20% weight)
            violation_score = len(compliance_check.get("violations", [])) * 20
            violation_score = min(100, violation_score)
            score += violation_score * 0.2
            
            return min(100, score)
            
        except Exception as e:
            logger.error(f"Failed to calculate risk score: {e}")
            return 50.0  # Default medium risk
    
    def _get_risk_level(self, risk_score: float) -> RiskLevel:
        """Convert risk score to risk level."""
        if risk_score < 25:
            return RiskLevel.LOW
        elif risk_score < 50:
            return RiskLevel.MEDIUM
        elif risk_score < 75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _generate_recommendations(
        self,
        risk_metrics: RiskMetrics,
        compliance_check: Dict[str, Any]
    ) -> List[str]:
        """Generate risk management recommendations."""
        recommendations = []
        
        # VaR recommendations
        if risk_metrics.var_99 > 100000:  # $100K
            recommendations.append("Consider reducing portfolio exposure to lower VaR")
        
        # Concentration recommendations
        if risk_metrics.concentration_risk > 0.3:  # 30%
            recommendations.append("Diversify portfolio to reduce concentration risk")
        
        # Compliance recommendations
        for violation in compliance_check.get("violations", []):
            if violation["type"] == "position_size_exceeded":
                recommendations.append(f"Reduce position size in {violation['commodity']}")
            elif violation["type"] == "var_limit_exceeded":
                recommendations.append(f"Implement hedging strategies for {violation['commodity']}")
        
        # Volatility recommendations
        if risk_metrics.volatility > 0.4:  # 40%
            recommendations.append("Consider volatility hedging strategies")
        
        if not recommendations:
            recommendations.append("Portfolio risk is within acceptable limits")
        
        return recommendations
