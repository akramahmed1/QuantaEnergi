"""
Advanced Analytics Engine for ETRM/CTRM Enterprise Application
Implements advanced analytics engine with performance attribution and P&L explain
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from decimal import Decimal
from sqlalchemy.orm import Session
import json
from scipy import stats
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AnalyticsType(Enum):
    PERFORMANCE_ATTRIBUTION = "performance_attribution"
    PNL_EXPLAIN = "pnl_explain"
    RISK_ATTRIBUTION = "risk_attribution"
    MARKET_ATTRIBUTION = "market_attribution"
    SECTOR_ATTRIBUTION = "sector_attribution"
    CURRENCY_ATTRIBUTION = "currency_attribution"
    TIME_ATTRIBUTION = "time_attribution"

class AttributionMethod(Enum):
    BRINSON_HOOD_BEEBOWER = "brinson_hood_beebower"
    GEOMETRIC_ATTRIBUTION = "geometric_attribution"
    ARITHMETIC_ATTRIBUTION = "arithmetic_attribution"
    REGRESSION_ATTRIBUTION = "regression_attribution"
    FACTOR_ATTRIBUTION = "factor_attribution"

@dataclass
class PerformanceMetrics:
    """Performance metrics calculation"""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    var_95: float
    var_99: float
    expected_shortfall: float
    information_ratio: float
    tracking_error: float
    beta: float
    alpha: float
    r_squared: float
    calculated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AttributionResult:
    """Performance attribution result"""
    attribution_id: str
    portfolio_id: str
    benchmark_id: str
    attribution_method: AttributionMethod
    total_attribution: float
    allocation_effect: float
    selection_effect: float
    interaction_effect: float
    currency_effect: float
    time_effect: float
    sector_attribution: Dict[str, float]
    security_attribution: Dict[str, float]
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PnLExplain:
    """P&L explanation result"""
    explain_id: str
    trade_id: str
    total_pnl: float
    price_effect: float
    volume_effect: float
    fx_effect: float
    time_decay: float
    volatility_effect: float
    correlation_effect: float
    market_effect: float
    idiosyncratic_effect: float
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RiskAttribution:
    """Risk attribution result"""
    attribution_id: str
    portfolio_id: str
    total_risk: float
    systematic_risk: float
    idiosyncratic_risk: float
    sector_risk: Dict[str, float]
    factor_risk: Dict[str, float]
    concentration_risk: float
    currency_risk: float
    time_risk: float
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class AnalyticsEngine:
    """Advanced analytics engine with performance attribution and P&L explain"""
    
    def __init__(self, db: Session):
        self.db = db
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        self.attribution_results: Dict[str, AttributionResult] = {}
        self.pnl_explanations: Dict[str, PnLExplain] = {}
        self.risk_attributions: Dict[str, RiskAttribution] = {}
        
        # Analytics parameters
        self.analytics_parameters = {
            "risk_free_rate": 0.02,
            "benchmark_return": 0.08,
            "confidence_level": 0.95,
            "lookback_period": 252,  # days
            "rebalance_frequency": 30  # days
        }
        
        # Initialize analytics models
        self._initialize_analytics_models()
    
    def _initialize_analytics_models(self):
        """Initialize analytics models"""
        self.analytics_models = {
            AttributionMethod.BRINSON_HOOD_BEEBOWER: self._calculate_brinson_attribution,
            AttributionMethod.GEOMETRIC_ATTRIBUTION: self._calculate_geometric_attribution,
            AttributionMethod.ARITHMETIC_ATTRIBUTION: self._calculate_arithmetic_attribution,
            AttributionMethod.REGRESSION_ATTRIBUTION: self._calculate_regression_attribution,
            AttributionMethod.FACTOR_ATTRIBUTION: self._calculate_factor_attribution
        }
    
    def calculate_performance_metrics(self, 
                                     returns: List[float],
                                     benchmark_returns: List[float] = None,
                                     risk_free_rate: float = None) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        
        if risk_free_rate is None:
            risk_free_rate = self.analytics_parameters["risk_free_rate"]
        
        returns_array = np.array(returns)
        
        # Basic metrics
        total_return = np.prod(1 + returns_array) - 1
        annualized_return = (1 + total_return) ** (252 / len(returns_array)) - 1
        volatility = np.std(returns_array) * np.sqrt(252)
        
        # Risk-adjusted metrics
        sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # Sortino ratio (downside deviation)
        downside_returns = returns_array[returns_array < 0]
        downside_volatility = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = (annualized_return - risk_free_rate) / downside_volatility if downside_volatility > 0 else 0
        
        # Calmar ratio
        max_drawdown = self._calculate_max_drawdown(returns_array)
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # VaR and Expected Shortfall
        var_95 = np.percentile(returns_array, 5)
        var_99 = np.percentile(returns_array, 1)
        expected_shortfall = np.mean(returns_array[returns_array <= var_95])
        
        # Benchmark comparison
        information_ratio = 0
        tracking_error = 0
        beta = 0
        alpha = 0
        r_squared = 0
        
        if benchmark_returns is not None and len(benchmark_returns) == len(returns):
            benchmark_array = np.array(benchmark_returns)
            
            # Information ratio
            excess_returns = returns_array - benchmark_array
            tracking_error = np.std(excess_returns) * np.sqrt(252)
            information_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252) if np.std(excess_returns) > 0 else 0
            
            # Beta and Alpha
            if len(returns_array) > 1:
                covariance = np.cov(returns_array, benchmark_array)[0, 1]
                benchmark_variance = np.var(benchmark_array)
                beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
                alpha = annualized_return - (risk_free_rate + beta * (np.mean(benchmark_array) * 252 - risk_free_rate))
                
                # R-squared
                correlation = np.corrcoef(returns_array, benchmark_array)[0, 1]
                r_squared = correlation ** 2
        
        metrics = PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            max_drawdown=max_drawdown,
            var_95=var_95,
            var_99=var_99,
            expected_shortfall=expected_shortfall,
            information_ratio=information_ratio,
            tracking_error=tracking_error,
            beta=beta,
            alpha=alpha,
            r_squared=r_squared
        )
        
        metrics_id = f"PM_{int(datetime.utcnow().timestamp())}"
        self.performance_metrics[metrics_id] = metrics
        
        return metrics
    
    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Calculate maximum drawdown"""
        cumulative_returns = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        return np.min(drawdowns)
    
    def calculate_performance_attribution(self, 
                                        portfolio_returns: List[float],
                                        benchmark_returns: List[float],
                                        portfolio_weights: List[float],
                                        benchmark_weights: List[float],
                                        sector_returns: Dict[str, List[float]],
                                        method: AttributionMethod = AttributionMethod.BRINSON_HOOD_BEEBOWER) -> AttributionResult:
        """Calculate performance attribution"""
        
        if method not in self.analytics_models:
            raise ValueError(f"Attribution method {method} not implemented")
        
        attribution_calculator = self.analytics_models[method]
        attribution_result = attribution_calculator(
            portfolio_returns, benchmark_returns, portfolio_weights, benchmark_weights, sector_returns
        )
        
        # Store attribution result
        attribution_id = f"PA_{int(datetime.utcnow().timestamp())}"
        self.attribution_results[attribution_id] = attribution_result
        
        return attribution_result
    
    def _calculate_brinson_attribution(self, 
                                     portfolio_returns: List[float],
                                     benchmark_returns: List[float],
                                     portfolio_weights: List[float],
                                     benchmark_weights: List[float],
                                     sector_returns: Dict[str, List[float]]) -> AttributionResult:
        """Calculate Brinson-Hood-Beebower attribution"""
        
        portfolio_returns_array = np.array(portfolio_returns)
        benchmark_returns_array = np.array(benchmark_returns)
        portfolio_weights_array = np.array(portfolio_weights)
        benchmark_weights_array = np.array(benchmark_weights)
        
        # Calculate total returns
        portfolio_total_return = np.sum(portfolio_returns_array * portfolio_weights_array)
        benchmark_total_return = np.sum(benchmark_returns_array * benchmark_weights_array)
        
        # Allocation effect
        allocation_effect = np.sum((portfolio_weights_array - benchmark_weights_array) * benchmark_returns_array)
        
        # Selection effect
        selection_effect = np.sum(benchmark_weights_array * (portfolio_returns_array - benchmark_returns_array))
        
        # Interaction effect
        interaction_effect = np.sum((portfolio_weights_array - benchmark_weights_array) * (portfolio_returns_array - benchmark_returns_array))
        
        # Total attribution
        total_attribution = allocation_effect + selection_effect + interaction_effect
        
        # Sector attribution
        sector_attribution = {}
        for sector, returns in sector_returns.items():
            if len(returns) == len(portfolio_returns):
                sector_returns_array = np.array(returns)
                sector_allocation = np.sum((portfolio_weights_array - benchmark_weights_array) * sector_returns_array)
                sector_selection = np.sum(benchmark_weights_array * (sector_returns_array - benchmark_returns_array))
                sector_attribution[sector] = sector_allocation + sector_selection
        
        return AttributionResult(
            attribution_id=f"BHB_{int(datetime.utcnow().timestamp())}",
            portfolio_id="portfolio",
            benchmark_id="benchmark",
            attribution_method=AttributionMethod.BRINSON_HOOD_BEEBOWER,
            total_attribution=total_attribution,
            allocation_effect=allocation_effect,
            selection_effect=selection_effect,
            interaction_effect=interaction_effect,
            currency_effect=0.0,  # Simplified
            time_effect=0.0,  # Simplified
            sector_attribution=sector_attribution,
            security_attribution={}  # Simplified
        )
    
    def _calculate_geometric_attribution(self, 
                                       portfolio_returns: List[float],
                                       benchmark_returns: List[float],
                                       portfolio_weights: List[float],
                                       benchmark_weights: List[float],
                                       sector_returns: Dict[str, List[float]]) -> AttributionResult:
        """Calculate geometric attribution"""
        
        # Geometric attribution is more complex and requires iterative calculation
        # For simplicity, we'll use a simplified approach
        
        portfolio_returns_array = np.array(portfolio_returns)
        benchmark_returns_array = np.array(benchmark_returns)
        
        # Calculate geometric returns
        portfolio_geometric_return = np.prod(1 + portfolio_returns_array) - 1
        benchmark_geometric_return = np.prod(1 + benchmark_returns_array) - 1
        
        # Simplified geometric attribution
        total_attribution = portfolio_geometric_return - benchmark_geometric_return
        
        return AttributionResult(
            attribution_id=f"GEO_{int(datetime.utcnow().timestamp())}",
            portfolio_id="portfolio",
            benchmark_id="benchmark",
            attribution_method=AttributionMethod.GEOMETRIC_ATTRIBUTION,
            total_attribution=total_attribution,
            allocation_effect=total_attribution * 0.4,  # Simplified
            selection_effect=total_attribution * 0.4,   # Simplified
            interaction_effect=total_attribution * 0.2, # Simplified
            currency_effect=0.0,
            time_effect=0.0,
            sector_attribution={},
            security_attribution={}
        )
    
    def _calculate_arithmetic_attribution(self, 
                                        portfolio_returns: List[float],
                                        benchmark_returns: List[float],
                                        portfolio_weights: List[float],
                                        benchmark_weights: List[float],
                                        sector_returns: Dict[str, List[float]]) -> AttributionResult:
        """Calculate arithmetic attribution"""
        
        # Arithmetic attribution is similar to Brinson but with different calculation
        portfolio_returns_array = np.array(portfolio_returns)
        benchmark_returns_array = np.array(benchmark_returns)
        portfolio_weights_array = np.array(portfolio_weights)
        benchmark_weights_array = np.array(benchmark_weights)
        
        # Calculate total returns
        portfolio_total_return = np.sum(portfolio_returns_array * portfolio_weights_array)
        benchmark_total_return = np.sum(benchmark_returns_array * benchmark_weights_array)
        
        # Arithmetic attribution
        total_attribution = portfolio_total_return - benchmark_total_return
        
        # Simplified breakdown
        allocation_effect = total_attribution * 0.5
        selection_effect = total_attribution * 0.3
        interaction_effect = total_attribution * 0.2
        
        return AttributionResult(
            attribution_id=f"ARITH_{int(datetime.utcnow().timestamp())}",
            portfolio_id="portfolio",
            benchmark_id="benchmark",
            attribution_method=AttributionMethod.ARITHMETIC_ATTRIBUTION,
            total_attribution=total_attribution,
            allocation_effect=allocation_effect,
            selection_effect=selection_effect,
            interaction_effect=interaction_effect,
            currency_effect=0.0,
            time_effect=0.0,
            sector_attribution={},
            security_attribution={}
        )
    
    def _calculate_regression_attribution(self, 
                                        portfolio_returns: List[float],
                                        benchmark_returns: List[float],
                                        portfolio_weights: List[float],
                                        benchmark_weights: List[float],
                                        sector_returns: Dict[str, List[float]]) -> AttributionResult:
        """Calculate regression-based attribution"""
        
        # Use linear regression to decompose returns
        portfolio_returns_array = np.array(portfolio_returns)
        benchmark_returns_array = np.array(benchmark_returns)
        
        # Fit linear regression
        if len(portfolio_returns_array) > 1 and len(benchmark_returns_array) > 1:
            X = benchmark_returns_array.reshape(-1, 1)
            y = portfolio_returns_array
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Calculate attribution
            beta = model.coef_[0]
            alpha = model.intercept_
            
            total_attribution = np.mean(portfolio_returns_array) - np.mean(benchmark_returns_array)
            selection_effect = alpha
            allocation_effect = (beta - 1) * np.mean(benchmark_returns_array)
            interaction_effect = total_attribution - selection_effect - allocation_effect
        else:
            total_attribution = 0
            selection_effect = 0
            allocation_effect = 0
            interaction_effect = 0
        
        return AttributionResult(
            attribution_id=f"REG_{int(datetime.utcnow().timestamp())}",
            portfolio_id="portfolio",
            benchmark_id="benchmark",
            attribution_method=AttributionMethod.REGRESSION_ATTRIBUTION,
            total_attribution=total_attribution,
            allocation_effect=allocation_effect,
            selection_effect=selection_effect,
            interaction_effect=interaction_effect,
            currency_effect=0.0,
            time_effect=0.0,
            sector_attribution={},
            security_attribution={}
        )
    
    def _calculate_factor_attribution(self, 
                                    portfolio_returns: List[float],
                                    benchmark_returns: List[float],
                                    portfolio_weights: List[float],
                                    benchmark_weights: List[float],
                                    sector_returns: Dict[str, List[float]]) -> AttributionResult:
        """Calculate factor-based attribution"""
        
        # Factor attribution using multiple factors
        portfolio_returns_array = np.array(portfolio_returns)
        benchmark_returns_array = np.array(benchmark_returns)
        
        # Create factor matrix
        factors = []
        factor_names = []
        
        # Market factor
        factors.append(benchmark_returns_array)
        factor_names.append("market")
        
        # Sector factors
        for sector, returns in sector_returns.items():
            if len(returns) == len(portfolio_returns):
                factors.append(np.array(returns))
                factor_names.append(sector)
        
        if len(factors) > 0:
            factor_matrix = np.column_stack(factors)
            
            # Fit multiple regression
            model = LinearRegression()
            model.fit(factor_matrix, portfolio_returns_array)
            
            # Calculate factor contributions
            factor_contributions = model.coef_ * np.mean(factor_matrix, axis=0)
            total_attribution = np.mean(portfolio_returns_array) - np.mean(benchmark_returns_array)
            
            # Simplified attribution
            selection_effect = model.intercept_
            allocation_effect = factor_contributions[0] if len(factor_contributions) > 0 else 0
            interaction_effect = total_attribution - selection_effect - allocation_effect
        else:
            total_attribution = 0
            selection_effect = 0
            allocation_effect = 0
            interaction_effect = 0
        
        return AttributionResult(
            attribution_id=f"FACTOR_{int(datetime.utcnow().timestamp())}",
            portfolio_id="portfolio",
            benchmark_id="benchmark",
            attribution_method=AttributionMethod.FACTOR_ATTRIBUTION,
            total_attribution=total_attribution,
            allocation_effect=allocation_effect,
            selection_effect=selection_effect,
            interaction_effect=interaction_effect,
            currency_effect=0.0,
            time_effect=0.0,
            sector_attribution={},
            security_attribution={}
        )
    
    def calculate_pnl_explain(self, 
                             trade_data: Dict[str, Any],
                             market_data: Dict[str, Any],
                             risk_factors: Dict[str, Any]) -> PnLExplain:
        """Calculate P&L explanation for a trade"""
        
        # Extract trade information
        trade_id = trade_data.get('trade_id', 'unknown')
        quantity = trade_data.get('quantity', 0)
        entry_price = trade_data.get('entry_price', 0)
        current_price = trade_data.get('current_price', 0)
        
        # Calculate total P&L
        total_pnl = quantity * (current_price - entry_price)
        
        # Price effect (main driver)
        price_effect = quantity * (current_price - entry_price)
        
        # Volume effect (if quantity changed)
        volume_effect = 0  # Simplified
        
        # FX effect (if applicable)
        fx_rate = risk_factors.get('fx_rate', 1.0)
        fx_effect = total_pnl * (fx_rate - 1)
        
        # Time decay (for options)
        time_decay = risk_factors.get('time_decay', 0)
        
        # Volatility effect
        volatility_change = risk_factors.get('volatility_change', 0)
        volatility_effect = total_pnl * volatility_change * 0.1  # Simplified
        
        # Correlation effect
        correlation_change = risk_factors.get('correlation_change', 0)
        correlation_effect = total_pnl * correlation_change * 0.05  # Simplified
        
        # Market effect
        market_return = risk_factors.get('market_return', 0)
        market_effect = total_pnl * market_return * 0.2  # Simplified
        
        # Idiosyncratic effect (residual)
        idiosyncratic_effect = total_pnl - (price_effect + volume_effect + fx_effect + 
                                           time_decay + volatility_effect + correlation_effect + market_effect)
        
        pnl_explain = PnLExplain(
            explain_id=f"PNL_{trade_id}_{int(datetime.utcnow().timestamp())}",
            trade_id=trade_id,
            total_pnl=total_pnl,
            price_effect=price_effect,
            volume_effect=volume_effect,
            fx_effect=fx_effect,
            time_decay=time_decay,
            volatility_effect=volatility_effect,
            correlation_effect=correlation_effect,
            market_effect=market_effect,
            idiosyncratic_effect=idiosyncratic_effect
        )
        
        self.pnl_explanations[pnl_explain.explain_id] = pnl_explain
        return pnl_explain
    
    def calculate_risk_attribution(self, 
                                 portfolio_returns: List[float],
                                 factor_returns: Dict[str, List[float]],
                                 portfolio_weights: List[float]) -> RiskAttribution:
        """Calculate risk attribution"""
        
        portfolio_returns_array = np.array(portfolio_returns)
        portfolio_weights_array = np.array(portfolio_weights)
        
        # Calculate total risk
        total_risk = np.std(portfolio_returns_array) * np.sqrt(252)
        
        # Systematic risk (market risk)
        market_returns = factor_returns.get('market', portfolio_returns)
        if len(market_returns) == len(portfolio_returns):
            market_returns_array = np.array(market_returns)
            correlation = np.corrcoef(portfolio_returns_array, market_returns_array)[0, 1]
            systematic_risk = total_risk * abs(correlation)
        else:
            systematic_risk = total_risk * 0.7  # Simplified
        
        # Idiosyncratic risk
        idiosyncratic_risk = total_risk - systematic_risk
        
        # Sector risk attribution
        sector_risk = {}
        for sector, returns in factor_returns.items():
            if sector != 'market' and len(returns) == len(portfolio_returns):
                sector_returns_array = np.array(returns)
                sector_correlation = np.corrcoef(portfolio_returns_array, sector_returns_array)[0, 1]
                sector_risk[sector] = total_risk * abs(sector_correlation) * 0.1  # Simplified
        
        # Factor risk attribution
        factor_risk = {}
        for factor, returns in factor_returns.items():
            if len(returns) == len(portfolio_returns):
                factor_returns_array = np.array(returns)
                factor_correlation = np.corrcoef(portfolio_returns_array, factor_returns_array)[0, 1]
                factor_risk[factor] = total_risk * abs(factor_correlation) * 0.05  # Simplified
        
        # Concentration risk
        concentration_risk = np.sum(portfolio_weights_array ** 2) * total_risk
        
        # Currency risk (simplified)
        currency_risk = total_risk * 0.1
        
        # Time risk (simplified)
        time_risk = total_risk * 0.05
        
        risk_attribution = RiskAttribution(
            attribution_id=f"RA_{int(datetime.utcnow().timestamp())}",
            portfolio_id="portfolio",
            total_risk=total_risk,
            systematic_risk=systematic_risk,
            idiosyncratic_risk=idiosyncratic_risk,
            sector_risk=sector_risk,
            factor_risk=factor_risk,
            concentration_risk=concentration_risk,
            currency_risk=currency_risk,
            time_risk=time_risk
        )
        
        self.risk_attributions[risk_attribution.attribution_id] = risk_attribution
        return risk_attribution
    
    def generate_analytics_report(self, 
                                portfolio_id: str,
                                start_date: datetime,
                                end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        
        # This would typically fetch data from database
        # For now, we'll use simulated data
        
        # Simulate portfolio returns
        days = (end_date - start_date).days
        portfolio_returns = np.random.normal(0.001, 0.02, days).tolist()
        benchmark_returns = np.random.normal(0.0008, 0.015, days).tolist()
        
        # Calculate performance metrics
        performance_metrics = self.calculate_performance_metrics(portfolio_returns, benchmark_returns)
        
        # Calculate attribution
        portfolio_weights = [0.3, 0.25, 0.2, 0.15, 0.1]  # Simplified
        benchmark_weights = [0.25, 0.25, 0.25, 0.15, 0.1]  # Simplified
        
        sector_returns = {
            'energy': np.random.normal(0.001, 0.025, days).tolist(),
            'utilities': np.random.normal(0.0005, 0.018, days).tolist(),
            'materials': np.random.normal(0.0012, 0.022, days).tolist()
        }
        
        attribution_result = self.calculate_performance_attribution(
            portfolio_returns, benchmark_returns, portfolio_weights, benchmark_weights, sector_returns
        )
        
        # Calculate risk attribution
        factor_returns = {
            'market': benchmark_returns,
            'energy': sector_returns['energy'],
            'utilities': sector_returns['utilities']
        }
        
        risk_attribution = self.calculate_risk_attribution(portfolio_returns, factor_returns, portfolio_weights)
        
        return {
            "portfolio_id": portfolio_id,
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "performance_metrics": {
                "total_return": performance_metrics.total_return,
                "annualized_return": performance_metrics.annualized_return,
                "volatility": performance_metrics.volatility,
                "sharpe_ratio": performance_metrics.sharpe_ratio,
                "max_drawdown": performance_metrics.max_drawdown,
                "var_95": performance_metrics.var_95,
                "information_ratio": performance_metrics.information_ratio,
                "alpha": performance_metrics.alpha,
                "beta": performance_metrics.beta
            },
            "attribution_analysis": {
                "total_attribution": attribution_result.total_attribution,
                "allocation_effect": attribution_result.allocation_effect,
                "selection_effect": attribution_result.selection_effect,
                "interaction_effect": attribution_result.interaction_effect,
                "sector_attribution": attribution_result.sector_attribution
            },
            "risk_attribution": {
                "total_risk": risk_attribution.total_risk,
                "systematic_risk": risk_attribution.systematic_risk,
                "idiosyncratic_risk": risk_attribution.idiosyncratic_risk,
                "sector_risk": risk_attribution.sector_risk,
                "factor_risk": risk_attribution.factor_risk,
                "concentration_risk": risk_attribution.concentration_risk
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics system summary"""
        
        total_metrics = len(self.performance_metrics)
        total_attributions = len(self.attribution_results)
        total_pnl_explanations = len(self.pnl_explanations)
        total_risk_attributions = len(self.risk_attributions)
        
        return {
            "total_performance_metrics": total_metrics,
            "total_attributions": total_attributions,
            "total_pnl_explanations": total_pnl_explanations,
            "total_risk_attributions": total_risk_attributions,
            "analytics_methods": [method.value for method in AttributionMethod],
            "supported_analytics": [analytics.value for analytics in AnalyticsType],
            "system_status": "operational"
        }
