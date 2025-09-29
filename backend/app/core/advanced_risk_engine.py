"""
Advanced Risk Engine for ETRM/CTRM Enterprise Application
Implements comprehensive risk models including stress testing, scenario analysis, and Greeks
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from scipy import stats
from scipy.optimize import minimize
import json
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class RiskType(Enum):
    MARKET = "market"
    CREDIT = "credit"
    OPERATIONAL = "operational"
    LIQUIDITY = "liquidity"
    CONCENTRATION = "concentration"
    REGULATORY = "regulatory"

class StressTestType(Enum):
    HISTORICAL = "historical"
    HYPOTHETICAL = "hypothetical"
    MONTE_CARLO = "monte_carlo"
    REGIME_CHANGE = "regime_change"

@dataclass
class RiskLimit:
    """Risk limit definition"""
    limit_id: str
    risk_type: RiskType
    limit_value: float
    current_value: float
    breach_threshold: float = 0.8  # 80% of limit
    currency: str = "USD"
    unit: str = "absolute"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def utilization(self) -> float:
        return self.current_value / self.limit_value if self.limit_value > 0 else 0
    
    @property
    def is_breached(self) -> bool:
        return self.current_value > self.limit_value
    
    @property
    def is_warning(self) -> bool:
        return self.utilization >= self.breach_threshold

@dataclass
class StressScenario:
    """Stress test scenario definition"""
    scenario_id: str
    name: str
    description: str
    scenario_type: StressTestType
    market_shocks: Dict[str, float]  # {instrument: shock_percentage}
    correlation_changes: Dict[Tuple[str, str], float]  # {(asset1, asset2): new_correlation}
    volatility_multipliers: Dict[str, float]  # {instrument: volatility_multiplier}
    probability: float = 0.01  # 1% probability
    severity: str = "high"  # low, medium, high, extreme
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Greeks:
    """Option Greeks calculation"""
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0
    rho: float = 0.0
    vanna: float = 0.0
    volga: float = 0.0
    charm: float = 0.0
    speed: float = 0.0
    color: float = 0.0
    ultima: float = 0.0

class AdvancedRiskEngine:
    """Enterprise-grade risk engine with comprehensive risk models"""
    
    def __init__(self, db: Session):
        self.db = db
        self.risk_limits: Dict[str, RiskLimit] = {}
        self.stress_scenarios: Dict[str, StressScenario] = {}
        self.correlation_matrix: Optional[np.ndarray] = None
        self.volatility_matrix: Optional[np.ndarray] = None
        self.positions: Dict[str, Dict[str, Any]] = {}
        
    def add_risk_limit(self, 
                       limit_id: str,
                       risk_type: RiskType,
                       limit_value: float,
                       breach_threshold: float = 0.8,
                       currency: str = "USD",
                       unit: str = "absolute") -> RiskLimit:
        """Add a new risk limit"""
        
        limit = RiskLimit(
            limit_id=limit_id,
            risk_type=risk_type,
            limit_value=limit_value,
            current_value=0.0,
            breach_threshold=breach_threshold,
            currency=currency,
            unit=unit
        )
        
        self.risk_limits[limit_id] = limit
        logger.info(f"Risk limit added: {limit_id} = {limit_value} {currency}")
        return limit
    
    def update_risk_limits(self, positions: Dict[str, Dict[str, Any]]):
        """Update current risk limit values based on positions"""
        
        # Calculate VaR for each position
        for instrument, position in positions.items():
            if instrument not in self.positions:
                self.positions[instrument] = position
            
            # Update position data
            self.positions[instrument].update(position)
        
        # Calculate portfolio VaR
        portfolio_var = self.calculate_portfolio_var(positions)
        
        # Update VaR limits
        for limit_id, limit in self.risk_limits.items():
            if limit.risk_type == RiskType.MARKET:
                limit.current_value = portfolio_var
            elif limit.risk_type == RiskType.CONCENTRATION:
                limit.current_value = self.calculate_concentration_risk(positions)
            elif limit.risk_type == RiskType.LIQUIDITY:
                limit.current_value = self.calculate_liquidity_risk(positions)
            
            limit.updated_at = datetime.utcnow()
    
    def calculate_portfolio_var(self, 
                               positions: Dict[str, Dict[str, Any]], 
                               confidence_level: float = 0.95,
                               time_horizon: int = 1,
                               method: str = "monte_carlo") -> float:
        """Calculate portfolio VaR using multiple methods"""
        
        if not positions:
            return 0.0
        
        # Get position data
        position_values = []
        position_weights = []
        instruments = []
        
        for instrument, pos in positions.items():
            market_value = pos.get('market_value', 0)
            if market_value > 0:
                position_values.append(market_value)
                instruments.append(instrument)
        
        if not position_values:
            return 0.0
        
        total_value = sum(position_values)
        position_weights = [v / total_value for v in position_values]
        
        if method == "monte_carlo":
            return self._calculate_monte_carlo_var(position_values, position_weights, instruments, confidence_level, time_horizon)
        elif method == "parametric":
            return self._calculate_parametric_var(position_values, position_weights, instruments, confidence_level, time_horizon)
        elif method == "historical":
            return self._calculate_historical_var(position_values, position_weights, instruments, confidence_level, time_horizon)
        else:
            raise ValueError(f"Unknown VaR method: {method}")
    
    def _calculate_monte_carlo_var(self, 
                                   position_values: List[float],
                                   position_weights: List[float],
                                   instruments: List[str],
                                   confidence_level: float,
                                   time_horizon: int,
                                   num_simulations: int = 10000) -> float:
        """Monte Carlo VaR with correlation matrix"""
        
        # Get correlation matrix
        if self.correlation_matrix is None:
            self._build_correlation_matrix(instruments)
        
        # Generate correlated random returns
        n_assets = len(instruments)
        np.random.seed(42)  # For reproducibility
        
        # Generate uncorrelated random numbers
        uncorrelated_returns = np.random.normal(0, 1, (num_simulations, n_assets))
        
        # Apply correlation using Cholesky decomposition
        try:
            L = np.linalg.cholesky(self.correlation_matrix)
            correlated_returns = uncorrelated_returns @ L.T
        except np.linalg.LinAlgError:
            # Fallback to uncorrelated if correlation matrix is not positive definite
            correlated_returns = uncorrelated_returns
        
        # Apply volatility scaling
        if self.volatility_matrix is not None:
            volatilities = np.diag(self.volatility_matrix)
        else:
            volatilities = np.array([0.02] * n_assets)  # Default 2% daily volatility
        
        scaled_returns = correlated_returns * volatilities * np.sqrt(time_horizon)
        
        # Calculate portfolio returns
        portfolio_returns = np.dot(scaled_returns, position_weights)
        
        # Calculate VaR
        var_percentile = (1 - confidence_level) * 100
        var_value = -np.percentile(portfolio_returns, var_percentile) * total_value
        
        return float(var_value)
    
    def _calculate_parametric_var(self, 
                                 position_values: List[float],
                                 position_weights: List[float],
                                 instruments: List[str],
                                 confidence_level: float,
                                 time_horizon: int) -> float:
        """Parametric VaR using normal distribution assumption"""
        
        # Calculate portfolio volatility
        if self.correlation_matrix is None:
            self._build_correlation_matrix(instruments)
        
        # Get individual volatilities
        if self.volatility_matrix is not None:
            volatilities = np.diag(self.volatility_matrix)
        else:
            volatilities = np.array([0.02] * len(instruments))
        
        # Calculate portfolio variance
        portfolio_variance = np.dot(position_weights, np.dot(self.correlation_matrix, position_weights))
        portfolio_variance *= np.dot(volatilities, volatilities)
        portfolio_volatility = np.sqrt(portfolio_variance * time_horizon)
        
        # Calculate VaR
        z_score = stats.norm.ppf(confidence_level)
        total_value = sum(position_values)
        var_value = z_score * portfolio_volatility * total_value
        
        return float(var_value)
    
    def _calculate_historical_var(self, 
                                 position_values: List[float],
                                 position_weights: List[float],
                                 instruments: List[str],
                                 confidence_level: float,
                                 time_horizon: int) -> float:
        """Historical simulation VaR"""
        
        # This would typically use historical price data
        # For now, we'll simulate historical returns
        np.random.seed(42)
        historical_returns = np.random.normal(0, 0.02, 252)  # 1 year of daily returns
        
        # Calculate portfolio returns
        portfolio_returns = historical_returns * np.sum(position_weights)
        
        # Calculate VaR
        var_percentile = (1 - confidence_level) * 100
        total_value = sum(position_values)
        var_value = -np.percentile(portfolio_returns, var_percentile) * total_value
        
        return float(var_value)
    
    def _build_correlation_matrix(self, instruments: List[str]):
        """Build correlation matrix for instruments"""
        n = len(instruments)
        
        # Create base correlation matrix
        correlation_matrix = np.eye(n)
        
        # Add some correlation between similar instruments
        for i in range(n):
            for j in range(i + 1, n):
                # Higher correlation for similar asset types
                if self._are_similar_assets(instruments[i], instruments[j]):
                    correlation = 0.7
                else:
                    correlation = 0.3
                
                correlation_matrix[i, j] = correlation
                correlation_matrix[j, i] = correlation
        
        self.correlation_matrix = correlation_matrix
    
    def _build_volatility_matrix(self, instruments: List[str]):
        """Build volatility matrix for instruments"""
        n = len(instruments)
        
        # Create volatility matrix (diagonal matrix)
        volatility_matrix = np.eye(n)
        
        # Set volatilities based on instrument type
        for i, instrument in enumerate(instruments):
            if 'crude' in instrument.lower():
                volatility = 0.03  # 3% daily volatility
            elif 'gas' in instrument.lower():
                volatility = 0.04  # 4% daily volatility
            elif 'power' in instrument.lower():
                volatility = 0.05  # 5% daily volatility
            else:
                volatility = 0.02  # 2% daily volatility
            
            volatility_matrix[i, i] = volatility
        
        self.volatility_matrix = volatility_matrix
    
    def _are_similar_assets(self, asset1: str, asset2: str) -> bool:
        """Check if two assets are similar for correlation purposes"""
        asset1_type = self._get_asset_type(asset1)
        asset2_type = self._get_asset_type(asset2)
        return asset1_type == asset2_type
    
    def _get_asset_type(self, instrument: str) -> str:
        """Get asset type from instrument name"""
        instrument_lower = instrument.lower()
        if 'crude' in instrument_lower or 'oil' in instrument_lower:
            return 'crude_oil'
        elif 'gas' in instrument_lower:
            return 'natural_gas'
        elif 'power' in instrument_lower or 'electricity' in instrument_lower:
            return 'power'
        elif 'coal' in instrument_lower:
            return 'coal'
        else:
            return 'other'
    
    def calculate_concentration_risk(self, positions: Dict[str, Dict[str, Any]]) -> float:
        """Calculate concentration risk using Herfindahl-Hirschman Index"""
        
        if not positions:
            return 0.0
        
        # Get market values
        market_values = [pos.get('market_value', 0) for pos in positions.values()]
        total_value = sum(market_values)
        
        if total_value == 0:
            return 0.0
        
        # Calculate HHI
        weights = [v / total_value for v in market_values]
        hhi = sum(w ** 2 for w in weights)
        
        # Convert to percentage (0-100)
        concentration_risk = hhi * 100
        
        return concentration_risk
    
    def calculate_liquidity_risk(self, positions: Dict[str, Dict[str, Any]]) -> float:
        """Calculate liquidity risk based on position sizes and market depth"""
        
        if not positions:
            return 0.0
        
        # Get position data
        liquidity_risk = 0.0
        
        for instrument, pos in positions.items():
            market_value = pos.get('market_value', 0)
            quantity = pos.get('quantity', 0)
            
            if market_value > 0 and quantity > 0:
                # Estimate liquidity risk based on position size
                # Larger positions relative to typical market size = higher risk
                position_size_risk = min(market_value / 1000000, 1.0)  # Cap at 1M
                liquidity_risk += position_size_risk
        
        return liquidity_risk
    
    def add_stress_scenario(self, 
                           scenario_id: str,
                           name: str,
                           description: str,
                           scenario_type: StressTestType,
                           market_shocks: Dict[str, float],
                           correlation_changes: Dict[Tuple[str, str], float] = None,
                           volatility_multipliers: Dict[str, float] = None,
                           probability: float = 0.01,
                           severity: str = "high") -> StressScenario:
        """Add a new stress test scenario"""
        
        scenario = StressScenario(
            scenario_id=scenario_id,
            name=name,
            description=description,
            scenario_type=scenario_type,
            market_shocks=market_shocks,
            correlation_changes=correlation_changes or {},
            volatility_multipliers=volatility_multipliers or {},
            probability=probability,
            severity=severity
        )
        
        self.stress_scenarios[scenario_id] = scenario
        logger.info(f"Stress scenario added: {scenario_id} - {name}")
        return scenario
    
    def run_stress_test(self, 
                       scenario_id: str,
                       positions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Run stress test on portfolio"""
        
        if scenario_id not in self.stress_scenarios:
            raise ValueError(f"Stress scenario {scenario_id} not found")
        
        scenario = self.stress_scenarios[scenario_id]
        
        # Apply market shocks
        stressed_positions = {}
        total_pnl_impact = 0.0
        
        for instrument, pos in positions.items():
            market_value = pos.get('market_value', 0)
            current_price = pos.get('current_price', 0)
            quantity = pos.get('quantity', 0)
            
            if instrument in scenario.market_shocks:
                shock = scenario.market_shocks[instrument]
                new_price = current_price * (1 + shock)
                new_market_value = quantity * new_price
                pnl_impact = new_market_value - market_value
                total_pnl_impact += pnl_impact
                
                stressed_positions[instrument] = {
                    **pos,
                    'stressed_price': new_price,
                    'stressed_market_value': new_market_value,
                    'pnl_impact': pnl_impact
                }
            else:
                stressed_positions[instrument] = pos
        
        # Calculate stressed VaR
        stressed_var = self.calculate_portfolio_var(stressed_positions)
        
        return {
            "scenario_id": scenario_id,
            "scenario_name": scenario.name,
            "scenario_description": scenario.description,
            "scenario_type": scenario.scenario_type.value,
            "probability": scenario.probability,
            "severity": scenario.severity,
            "total_pnl_impact": total_pnl_impact,
            "stressed_var": stressed_var,
            "stressed_positions": stressed_positions,
            "run_time": datetime.utcnow().isoformat()
        }
    
    def calculate_greeks(self, 
                       instrument: str,
                       position: Dict[str, Any],
                       option_type: str = "call",
                       strike_price: float = None,
                       time_to_expiry: float = None,
                       risk_free_rate: float = 0.05,
                       volatility: float = 0.2) -> Greeks:
        """Calculate option Greeks for a position"""
        
        if strike_price is None or time_to_expiry is None:
            # For non-option instruments, return zero Greeks
            return Greeks()
        
        current_price = position.get('current_price', 0)
        quantity = position.get('quantity', 0)
        
        if current_price <= 0 or quantity == 0:
            return Greeks()
        
        # Black-Scholes Greeks calculation
        S = current_price
        K = strike_price
        T = time_to_expiry
        r = risk_free_rate
        sigma = volatility
        
        if T <= 0:
            return Greeks()
        
        # Calculate d1 and d2
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        # Calculate Greeks
        delta = stats.norm.cdf(d1) if option_type == "call" else stats.norm.cdf(d1) - 1
        gamma = stats.norm.pdf(d1) / (S * sigma * np.sqrt(T))
        theta = (-S * stats.norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - 
                 r * K * np.exp(-r * T) * stats.norm.cdf(d2)) if option_type == "call" else \
                (-S * stats.norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + 
                 r * K * np.exp(-r * T) * stats.norm.cdf(-d2))
        vega = S * stats.norm.pdf(d1) * np.sqrt(T)
        rho = K * T * np.exp(-r * T) * stats.norm.cdf(d2) if option_type == "call" else \
              -K * T * np.exp(-r * T) * stats.norm.cdf(-d2)
        
        # Second-order Greeks
        vanna = -stats.norm.pdf(d1) * d2 / sigma
        volga = S * stats.norm.pdf(d1) * np.sqrt(T) * d1 * d2 / sigma
        charm = -stats.norm.pdf(d1) * (2 * (r - 0.5 * sigma ** 2) * T - d2 * sigma * np.sqrt(T)) / (2 * T * sigma * np.sqrt(T))
        speed = -stats.norm.pdf(d1) / (S ** 2 * sigma * np.sqrt(T)) * (d1 / (sigma * np.sqrt(T)) + 1)
        color = -stats.norm.pdf(d1) / (2 * S * T * sigma * np.sqrt(T)) * (2 * r * T - d2 * sigma * np.sqrt(T))
        ultima = -vega / sigma ** 2 * (d1 * d2 * (1 - d1 * d2) + d1 ** 2 + d2 ** 2)
        
        # Scale by quantity
        quantity_float = float(quantity)
        
        return Greeks(
            delta=delta * quantity_float,
            gamma=gamma * quantity_float,
            theta=theta * quantity_float,
            vega=vega * quantity_float,
            rho=rho * quantity_float,
            vanna=vanna * quantity_float,
            volga=volga * quantity_float,
            charm=charm * quantity_float,
            speed=speed * quantity_float,
            color=color * quantity_float,
            ultima=ultima * quantity_float
        )
    
    def calculate_expected_shortfall(self, 
                                   positions: Dict[str, Dict[str, Any]],
                                   confidence_level: float = 0.95) -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        
        # Calculate VaR first
        var_value = self.calculate_portfolio_var(positions, confidence_level)
        
        # For Expected Shortfall, we need the tail of the distribution
        # This is a simplified calculation - in practice, you'd use the actual return distribution
        expected_shortfall = var_value * 1.3  # Typical ES is 1.3x VaR for normal distributions
        
        return expected_shortfall
    
    def get_risk_limits_status(self) -> Dict[str, Any]:
        """Get status of all risk limits"""
        
        status = {
            "total_limits": len(self.risk_limits),
            "breached_limits": [],
            "warning_limits": [],
            "healthy_limits": [],
            "summary": {
                "breached_count": 0,
                "warning_count": 0,
                "healthy_count": 0
            }
        }
        
        for limit_id, limit in self.risk_limits.items():
            limit_status = {
                "limit_id": limit_id,
                "risk_type": limit.risk_type.value,
                "limit_value": limit.limit_value,
                "current_value": limit.current_value,
                "utilization": limit.utilization,
                "currency": limit.currency,
                "unit": limit.unit,
                "status": "breached" if limit.is_breached else "warning" if limit.is_warning else "healthy"
            }
            
            if limit.is_breached:
                status["breached_limits"].append(limit_status)
                status["summary"]["breached_count"] += 1
            elif limit.is_warning:
                status["warning_limits"].append(limit_status)
                status["summary"]["warning_count"] += 1
            else:
                status["healthy_limits"].append(limit_status)
                status["summary"]["healthy_count"] += 1
        
        return status
    
    def validate_order(self, order) -> Dict[str, Any]:
        """Validate order against risk limits"""
        
        # This is a simplified validation - in practice, you'd check against all relevant limits
        validation_result = {
            "approved": True,
            "reason": "Order passed risk checks",
            "warnings": [],
            "rejections": []
        }
        
        # Check if any limits are breached
        for limit_id, limit in self.risk_limits.items():
            if limit.is_breached:
                validation_result["approved"] = False
                validation_result["reason"] = f"Risk limit breached: {limit_id}"
                validation_result["rejections"].append(f"Limit {limit_id} is breached")
            elif limit.is_warning:
                validation_result["warnings"].append(f"Limit {limit_id} is at {limit.utilization:.1%} utilization")
        
        return validation_result
