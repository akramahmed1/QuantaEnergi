"""
Advanced Portfolio Optimization Engine for ETRM/CTRM Enterprise Application
Implements portfolio optimization with constraints, objectives, and multi-objective optimization
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from scipy.optimize import minimize, minimize_scalar
from scipy.linalg import cholesky, solve_triangular
import cvxpy as cp
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class OptimizationObjective(Enum):
    MAXIMIZE_RETURN = "maximize_return"
    MINIMIZE_RISK = "minimize_risk"
    MAXIMIZE_SHARPE = "maximize_sharpe"
    MINIMIZE_VAR = "minimize_var"
    MAXIMIZE_UTILITY = "maximize_utility"
    MINIMIZE_TRACKING_ERROR = "minimize_tracking_error"

class ConstraintType(Enum):
    EQUALITY = "equality"
    INEQUALITY = "inequality"
    BOUNDS = "bounds"
    INTEGER = "integer"

@dataclass
class Asset:
    """Asset definition for portfolio optimization"""
    symbol: str
    name: str
    expected_return: float
    volatility: float
    market_cap: float = 0.0
    sector: str = ""
    region: str = ""
    currency: str = "USD"
    liquidity_score: float = 1.0
    esg_score: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Constraint:
    """Portfolio constraint definition"""
    constraint_id: str
    constraint_type: ConstraintType
    expression: str  # Mathematical expression
    bound: float
    description: str = ""
    is_active: bool = True

@dataclass
class OptimizationResult:
    """Portfolio optimization result"""
    weights: np.ndarray
    expected_return: float
    expected_risk: float
    sharpe_ratio: float
    var_95: float
    var_99: float
    expected_shortfall: float
    diversification_ratio: float
    concentration_risk: float
    optimization_time: float
    convergence_status: str
    objective_value: float
    constraints_satisfied: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

class PortfolioOptimizer:
    """Advanced portfolio optimization engine"""
    
    def __init__(self):
        self.assets: List[Asset] = []
        self.returns_matrix: Optional[np.ndarray] = None
        self.covariance_matrix: Optional[np.ndarray] = None
        self.correlation_matrix: Optional[np.ndarray] = None
        self.constraints: List[Constraint] = []
        self.risk_free_rate: float = 0.02
        self.optimization_history: List[OptimizationResult] = []
        
    def add_asset(self, asset: Asset):
        """Add asset to optimization universe"""
        self.assets.append(asset)
        logger.info(f"Asset added: {asset.symbol} - {asset.name}")
    
    def set_returns_matrix(self, returns_matrix: np.ndarray):
        """Set historical returns matrix"""
        self.returns_matrix = returns_matrix
        logger.info(f"Returns matrix set: {returns_matrix.shape}")
    
    def set_covariance_matrix(self, covariance_matrix: np.ndarray):
        """Set covariance matrix"""
        self.covariance_matrix = covariance_matrix
        logger.info(f"Covariance matrix set: {covariance_matrix.shape}")
    
    def calculate_covariance_matrix(self, returns_matrix: np.ndarray):
        """Calculate covariance matrix from returns"""
        self.returns_matrix = returns_matrix
        self.covariance_matrix = np.cov(returns_matrix.T)
        self.correlation_matrix = self._cov_to_corr(self.covariance_matrix)
        logger.info("Covariance matrix calculated from returns")
    
    def _cov_to_corr(self, cov_matrix: np.ndarray) -> np.ndarray:
        """Convert covariance matrix to correlation matrix"""
        std_devs = np.sqrt(np.diag(cov_matrix))
        corr_matrix = cov_matrix / np.outer(std_devs, std_devs)
        return corr_matrix
    
    def add_constraint(self, constraint: Constraint):
        """Add constraint to optimization problem"""
        self.constraints.append(constraint)
        logger.info(f"Constraint added: {constraint.constraint_id}")
    
    def optimize_portfolio(self, 
                          objective: OptimizationObjective,
                          constraints: List[Constraint] = None,
                          method: str = "scipy",
                          **kwargs) -> OptimizationResult:
        """Optimize portfolio with specified objective and constraints"""
        
        start_time = datetime.now()
        
        if not self.assets:
            raise ValueError("No assets in optimization universe")
        
        n_assets = len(self.assets)
        
        # Get expected returns and covariance matrix
        expected_returns = np.array([asset.expected_return for asset in self.assets])
        
        if self.covariance_matrix is None:
            # Use simplified covariance matrix
            self.covariance_matrix = np.eye(n_assets) * 0.04  # 20% volatility
        
        # Set up optimization problem
        if method == "scipy":
            result = self._optimize_scipy(objective, expected_returns, self.covariance_matrix, constraints, **kwargs)
        elif method == "cvxpy":
            result = self._optimize_cvxpy(objective, expected_returns, self.covariance_matrix, constraints, **kwargs)
        else:
            raise ValueError(f"Unknown optimization method: {method}")
        
        # Calculate portfolio metrics
        portfolio_metrics = self._calculate_portfolio_metrics(result.weights, expected_returns, self.covariance_matrix)
        
        # Create optimization result
        optimization_result = OptimizationResult(
            weights=result.weights,
            expected_return=portfolio_metrics['expected_return'],
            expected_risk=portfolio_metrics['expected_risk'],
            sharpe_ratio=portfolio_metrics['sharpe_ratio'],
            var_95=portfolio_metrics['var_95'],
            var_99=portfolio_metrics['var_99'],
            expected_shortfall=portfolio_metrics['expected_shortfall'],
            diversification_ratio=portfolio_metrics['diversification_ratio'],
            concentration_risk=portfolio_metrics['concentration_risk'],
            optimization_time=(datetime.now() - start_time).total_seconds(),
            convergence_status=result.status,
            objective_value=result.fun if hasattr(result, 'fun') else 0.0,
            constraints_satisfied=result.success if hasattr(result, 'success') else True,
            metadata=result.metadata if hasattr(result, 'metadata') else {}
        )
        
        self.optimization_history.append(optimization_result)
        return optimization_result
    
    def _optimize_scipy(self, 
                       objective: OptimizationObjective,
                       expected_returns: np.ndarray,
                       covariance_matrix: np.ndarray,
                       constraints: List[Constraint] = None,
                       **kwargs) -> Any:
        """Optimize using scipy.optimize"""
        
        n_assets = len(expected_returns)
        
        # Initial guess (equal weights)
        x0 = np.ones(n_assets) / n_assets
        
        # Bounds (weights between 0 and 1)
        bounds = [(0, 1) for _ in range(n_assets)]
        
        # Constraints
        scipy_constraints = []
        
        # Budget constraint (weights sum to 1)
        scipy_constraints.append({
            'type': 'eq',
            'fun': lambda x: np.sum(x) - 1
        })
        
        # Add custom constraints
        if constraints:
            for constraint in constraints:
                if constraint.constraint_type == ConstraintType.EQUALITY:
                    scipy_constraints.append({
                        'type': 'eq',
                        'fun': self._create_constraint_function(constraint, expected_returns, covariance_matrix)
                    })
                elif constraint.constraint_type == ConstraintType.INEQUALITY:
                    scipy_constraints.append({
                        'type': 'ineq',
                        'fun': self._create_constraint_function(constraint, expected_returns, covariance_matrix)
                    })
        
        # Objective function
        if objective == OptimizationObjective.MAXIMIZE_RETURN:
            objective_func = lambda x: -np.dot(x, expected_returns)
        elif objective == OptimizationObjective.MINIMIZE_RISK:
            objective_func = lambda x: np.dot(x, np.dot(covariance_matrix, x))
        elif objective == OptimizationObjective.MAXIMIZE_SHARPE:
            objective_func = lambda x: -self._calculate_sharpe_ratio(x, expected_returns, covariance_matrix)
        elif objective == OptimizationObjective.MINIMIZE_VAR:
            objective_func = lambda x: self._calculate_var(x, covariance_matrix, confidence_level=0.95)
        else:
            raise ValueError(f"Unknown objective: {objective}")
        
        # Optimize
        result = minimize(
            objective_func,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=scipy_constraints,
            options={'maxiter': 1000, 'ftol': 1e-9}
        )
        
        return result
    
    def _optimize_cvxpy(self, 
                       objective: OptimizationObjective,
                       expected_returns: np.ndarray,
                       covariance_matrix: np.ndarray,
                       constraints: List[Constraint] = None,
                       **kwargs) -> Any:
        """Optimize using CVXPY"""
        
        n_assets = len(expected_returns)
        
        # Variables
        weights = cp.Variable(n_assets)
        
        # Constraints
        cvxpy_constraints = [weights >= 0, weights <= 1, cp.sum(weights) == 1]
        
        # Add custom constraints
        if constraints:
            for constraint in constraints:
                if constraint.constraint_type == ConstraintType.EQUALITY:
                    cvxpy_constraints.append(self._create_cvxpy_constraint(constraint, weights, expected_returns, covariance_matrix))
                elif constraint.constraint_type == ConstraintType.INEQUALITY:
                    cvxpy_constraints.append(self._create_cvxpy_constraint(constraint, weights, expected_returns, covariance_matrix))
        
        # Objective
        if objective == OptimizationObjective.MAXIMIZE_RETURN:
            obj = cp.Maximize(weights.T @ expected_returns)
        elif objective == OptimizationObjective.MINIMIZE_RISK:
            obj = cp.Minimize(cp.quad_form(weights, covariance_matrix))
        elif objective == OptimizationObjective.MAXIMIZE_SHARPE:
            obj = cp.Maximize((weights.T @ expected_returns - self.risk_free_rate) / cp.sqrt(cp.quad_form(weights, covariance_matrix)))
        else:
            raise ValueError(f"Unknown objective: {objective}")
        
        # Solve
        problem = cp.Problem(obj, cvxpy_constraints)
        problem.solve()
        
        # Create result object
        class CVXPYResult:
            def __init__(self, weights, status, value):
                self.weights = weights
                self.status = status
                self.fun = value
                self.success = status == 'optimal'
                self.metadata = {}
        
        return CVXPYResult(weights.value, problem.status, problem.value)
    
    def _create_constraint_function(self, constraint: Constraint, expected_returns: np.ndarray, covariance_matrix: np.ndarray) -> Callable:
        """Create constraint function for scipy optimization"""
        
        if constraint.expression == "max_weight":
            return lambda x: constraint.bound - np.max(x)
        elif constraint.expression == "min_weight":
            return lambda x: np.min(x) - constraint.bound
        elif constraint.expression == "sector_limit":
            # This would need sector information
            return lambda x: constraint.bound - np.sum(x)
        elif constraint.expression == "var_limit":
            return lambda x: constraint.bound - self._calculate_var(x, covariance_matrix)
        else:
            return lambda x: 0  # Default constraint
    
    def _create_cvxpy_constraint(self, constraint: Constraint, weights, expected_returns: np.ndarray, covariance_matrix: np.ndarray):
        """Create constraint for CVXPY optimization"""
        
        if constraint.expression == "max_weight":
            return weights <= constraint.bound
        elif constraint.expression == "min_weight":
            return weights >= constraint.bound
        elif constraint.expression == "sector_limit":
            return cp.sum(weights) <= constraint.bound
        elif constraint.expression == "var_limit":
            return cp.quad_form(weights, covariance_matrix) <= constraint.bound
        else:
            return weights >= 0  # Default constraint
    
    def _calculate_sharpe_ratio(self, weights: np.ndarray, expected_returns: np.ndarray, covariance_matrix: np.ndarray) -> float:
        """Calculate Sharpe ratio"""
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_risk = np.sqrt(np.dot(weights, np.dot(covariance_matrix, weights)))
        
        if portfolio_risk == 0:
            return 0
        
        return (portfolio_return - self.risk_free_rate) / portfolio_risk
    
    def _calculate_var(self, weights: np.ndarray, covariance_matrix: np.ndarray, confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk"""
        portfolio_variance = np.dot(weights, np.dot(covariance_matrix, weights))
        portfolio_std = np.sqrt(portfolio_variance)
        
        # Assuming normal distribution
        z_score = -stats.norm.ppf(1 - confidence_level)
        return z_score * portfolio_std
    
    def _calculate_portfolio_metrics(self, weights: np.ndarray, expected_returns: np.ndarray, covariance_matrix: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive portfolio metrics"""
        
        # Basic metrics
        expected_return = np.dot(weights, expected_returns)
        expected_risk = np.sqrt(np.dot(weights, np.dot(covariance_matrix, weights)))
        sharpe_ratio = (expected_return - self.risk_free_rate) / expected_risk if expected_risk > 0 else 0
        
        # Risk metrics
        var_95 = self._calculate_var(weights, covariance_matrix, 0.95)
        var_99 = self._calculate_var(weights, covariance_matrix, 0.99)
        expected_shortfall = var_95 * 1.3  # Simplified ES calculation
        
        # Diversification metrics
        diversification_ratio = self._calculate_diversification_ratio(weights, expected_returns, covariance_matrix)
        concentration_risk = self._calculate_concentration_risk(weights)
        
        return {
            'expected_return': expected_return,
            'expected_risk': expected_risk,
            'sharpe_ratio': sharpe_ratio,
            'var_95': var_95,
            'var_99': var_99,
            'expected_shortfall': expected_shortfall,
            'diversification_ratio': diversification_ratio,
            'concentration_risk': concentration_risk
        }
    
    def _calculate_diversification_ratio(self, weights: np.ndarray, expected_returns: np.ndarray, covariance_matrix: np.ndarray) -> float:
        """Calculate diversification ratio"""
        portfolio_risk = np.sqrt(np.dot(weights, np.dot(covariance_matrix, weights)))
        weighted_avg_risk = np.dot(weights, np.sqrt(np.diag(covariance_matrix)))
        
        if weighted_avg_risk == 0:
            return 1.0
        
        return weighted_avg_risk / portfolio_risk
    
    def _calculate_concentration_risk(self, weights: np.ndarray) -> float:
        """Calculate concentration risk using Herfindahl-Hirschman Index"""
        return np.sum(weights ** 2)
    
    def optimize_multi_objective(self, 
                                 objectives: List[OptimizationObjective],
                                 weights: List[float] = None,
                                 constraints: List[Constraint] = None,
                                 method: str = "weighted_sum") -> OptimizationResult:
        """Multi-objective portfolio optimization"""
        
        if weights is None:
            weights = [1.0 / len(objectives)] * len(objectives)
        
        if len(objectives) != len(weights):
            raise ValueError("Number of objectives must match number of weights")
        
        # Create combined objective
        def combined_objective(x):
            total_objective = 0
            for i, objective in enumerate(objectives):
                if objective == OptimizationObjective.MAXIMIZE_RETURN:
                    total_objective += weights[i] * (-np.dot(x, [asset.expected_return for asset in self.assets]))
                elif objective == OptimizationObjective.MINIMIZE_RISK:
                    total_objective += weights[i] * np.dot(x, np.dot(self.covariance_matrix, x))
                elif objective == OptimizationObjective.MAXIMIZE_SHARPE:
                    total_objective += weights[i] * (-self._calculate_sharpe_ratio(x, [asset.expected_return for asset in self.assets], self.covariance_matrix))
                # Add more objectives as needed
            
            return total_objective
        
        # Optimize combined objective
        n_assets = len(self.assets)
        x0 = np.ones(n_assets) / n_assets
        bounds = [(0, 1) for _ in range(n_assets)]
        
        constraints_scipy = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        result = minimize(
            combined_objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints_scipy,
            options={'maxiter': 1000, 'ftol': 1e-9}
        )
        
        # Calculate metrics
        portfolio_metrics = self._calculate_portfolio_metrics(
            result.x, 
            np.array([asset.expected_return for asset in self.assets]), 
            self.covariance_matrix
        )
        
        return OptimizationResult(
            weights=result.x,
            expected_return=portfolio_metrics['expected_return'],
            expected_risk=portfolio_metrics['expected_risk'],
            sharpe_ratio=portfolio_metrics['sharpe_ratio'],
            var_95=portfolio_metrics['var_95'],
            var_99=portfolio_metrics['var_99'],
            expected_shortfall=portfolio_metrics['expected_shortfall'],
            diversification_ratio=portfolio_metrics['diversification_ratio'],
            concentration_risk=portfolio_metrics['concentration_risk'],
            optimization_time=0.0,  # Would need timing
            convergence_status=result.status,
            objective_value=result.fun,
            constraints_satisfied=result.success,
            metadata={'method': method, 'objectives': [obj.value for obj in objectives], 'weights': weights}
        )
    
    def generate_efficient_frontier(self, 
                                  num_portfolios: int = 100,
                                  constraints: List[Constraint] = None) -> Dict[str, List[float]]:
        """Generate efficient frontier"""
        
        if self.covariance_matrix is None:
            raise ValueError("Covariance matrix not set")
        
        expected_returns = np.array([asset.expected_return for asset in self.assets])
        
        # Find minimum and maximum expected returns
        min_return = np.min(expected_returns)
        max_return = np.max(expected_returns)
        
        target_returns = np.linspace(min_return, max_return, num_portfolios)
        
        efficient_portfolios = []
        efficient_returns = []
        efficient_risks = []
        
        for target_return in target_returns:
            try:
                # Optimize for minimum risk given target return
                result = self._optimize_min_risk_target_return(target_return, expected_returns, self.covariance_matrix, constraints)
                
                if result.success:
                    portfolio_risk = np.sqrt(np.dot(result.x, np.dot(self.covariance_matrix, result.x)))
                    efficient_portfolios.append(result.x)
                    efficient_returns.append(target_return)
                    efficient_risks.append(portfolio_risk)
            except Exception as e:
                logger.warning(f"Failed to optimize for target return {target_return}: {e}")
                continue
        
        return {
            'returns': efficient_returns,
            'risks': efficient_risks,
            'portfolios': efficient_portfolios
        }
    
    def _optimize_min_risk_target_return(self, 
                                       target_return: float,
                                       expected_returns: np.ndarray,
                                       covariance_matrix: np.ndarray,
                                       constraints: List[Constraint] = None) -> Any:
        """Optimize for minimum risk given target return"""
        
        n_assets = len(expected_returns)
        
        def objective(x):
            return np.dot(x, np.dot(covariance_matrix, x))
        
        constraints_scipy = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Budget constraint
            {'type': 'eq', 'fun': lambda x: np.dot(x, expected_returns) - target_return}  # Return constraint
        ]
        
        bounds = [(0, 1) for _ in range(n_assets)]
        x0 = np.ones(n_assets) / n_assets
        
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints_scipy,
            options={'maxiter': 1000, 'ftol': 1e-9}
        )
        
        return result
    
    def calculate_portfolio_attribution(self, 
                                      weights: np.ndarray,
                                      returns: np.ndarray,
                                      benchmark_returns: np.ndarray = None) -> Dict[str, Any]:
        """Calculate portfolio performance attribution"""
        
        if returns.shape[1] != len(weights):
            raise ValueError("Returns matrix columns must match number of assets")
        
        # Portfolio returns
        portfolio_returns = np.dot(returns, weights)
        
        # Calculate metrics
        total_return = np.prod(1 + portfolio_returns) - 1
        annualized_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
        volatility = np.std(portfolio_returns) * np.sqrt(252)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = np.cumprod(1 + portfolio_returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdowns)
        
        # Benchmark comparison
        benchmark_metrics = {}
        if benchmark_returns is not None:
            benchmark_total_return = np.prod(1 + benchmark_returns) - 1
            benchmark_annualized = (1 + benchmark_total_return) ** (252 / len(benchmark_returns)) - 1
            benchmark_volatility = np.std(benchmark_returns) * np.sqrt(252)
            
            # Tracking error
            excess_returns = portfolio_returns - benchmark_returns
            tracking_error = np.std(excess_returns) * np.sqrt(252)
            
            # Information ratio
            information_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252) if np.std(excess_returns) > 0 else 0
            
            benchmark_metrics = {
                'benchmark_return': benchmark_annualized,
                'benchmark_volatility': benchmark_volatility,
                'tracking_error': tracking_error,
                'information_ratio': information_ratio,
                'excess_return': annualized_return - benchmark_annualized
            }
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'benchmark_metrics': benchmark_metrics
        }
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of optimization history"""
        
        if not self.optimization_history:
            return {"message": "No optimization history available"}
        
        latest_result = self.optimization_history[-1]
        
        return {
            "total_optimizations": len(self.optimization_history),
            "latest_result": {
                "expected_return": latest_result.expected_return,
                "expected_risk": latest_result.expected_risk,
                "sharpe_ratio": latest_result.sharpe_ratio,
                "var_95": latest_result.var_95,
                "diversification_ratio": latest_result.diversification_ratio,
                "concentration_risk": latest_result.concentration_risk
            },
            "optimization_times": [result.optimization_time for result in self.optimization_history],
            "convergence_rates": [result.convergence_status for result in self.optimization_history]
        }
