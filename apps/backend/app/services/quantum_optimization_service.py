"""
Quantum Optimization Service using Qiskit v0.45.0
Provides quantum portfolio optimization for energy trading
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import structlog
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit.algorithms import QAOA
    from qiskit.algorithms.optimizers import COBYLA
    from qiskit.primitives import Sampler
    from qiskit_optimization import QuadraticProgram
    from qiskit_optimization.algorithms import MinimumEigenOptimizer
    from qiskit_optimization.converters import QuadraticProgramToQubo
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    logger = structlog.get_logger(__name__)
    logger.warning("Qiskit not available - using classical optimization fallback")

logger = structlog.get_logger(__name__)

class QuantumOptimizationService:
    """Quantum-powered portfolio optimization service"""
    
    def __init__(self):
        self.qiskit_available = QISKIT_AVAILABLE
        if not self.qiskit_available:
            logger.warning("Qiskit not available - using classical optimization")
    
    def optimize_portfolio(self, 
                          assets: List[str],
                          expected_returns: List[float],
                          risk_matrix: List[List[float]],
                          risk_tolerance: float = 0.5,
                          budget: float = 1000000.0) -> Dict:
        """
        Optimize energy trading portfolio using quantum algorithms
        
        Args:
            assets: List of asset names
            expected_returns: Expected returns for each asset
            risk_matrix: Risk covariance matrix
            risk_tolerance: Risk tolerance (0-1)
            budget: Total budget available
            
        Returns:
            Dictionary containing optimization results
        """
        try:
            logger.info("Starting portfolio optimization", 
                       assets=len(assets), 
                       budget=budget,
                       risk_tolerance=risk_tolerance)
            
            if self.qiskit_available:
                result = self._quantum_optimization(assets, expected_returns, risk_matrix, risk_tolerance, budget)
            else:
                result = self._classical_optimization(assets, expected_returns, risk_matrix, risk_tolerance, budget)
            
            logger.info("Portfolio optimization completed", 
                       optimal_return=result['expected_return'],
                       risk_score=result['risk_score'])
            
            return result
            
        except Exception as e:
            logger.error("Portfolio optimization failed", error=str(e))
            raise Exception(f"Optimization failed: {str(e)}")
    
    def _quantum_optimization(self, 
                             assets: List[str],
                             expected_returns: List[float],
                             risk_matrix: List[List[float]],
                             risk_tolerance: float,
                             budget: float) -> Dict:
        """Perform quantum optimization using QAOA"""
        try:
            # Create quadratic program
            qp = QuadraticProgram()
            
            # Add binary variables for each asset
            for i, asset in enumerate(assets):
                qp.binary_var(name=f'x_{i}')
            
            # Objective: maximize expected return
            linear = {}
            for i, ret in enumerate(expected_returns):
                linear[f'x_{i}'] = -ret  # Negative for maximization
            
            qp.minimize(linear=linear)
            
            # Add constraint: budget constraint
            budget_constraint = {}
            for i in range(len(assets)):
                budget_constraint[f'x_{i}'] = 1.0  # Each asset costs 1 unit
            qp.linear_constraint(linear=budget_constraint, sense='<=', rhs=budget)
            
            # Convert to QUBO
            converter = QuadraticProgramToQubo()
            qubo = converter.convert(qp)
            
            # Set up QAOA
            optimizer = COBYLA(maxiter=100)
            qaoa = QAOA(optimizer=optimizer, reps=2)
            
            # Solve
            algorithm = MinimumEigenOptimizer(qaoa)
            result = algorithm.solve(qubo)
            
            # Extract solution
            solution = result.x
            selected_assets = [assets[i] for i, selected in enumerate(solution) if selected]
            
            # Calculate metrics
            total_return = sum(expected_returns[i] for i, selected in enumerate(solution) if selected)
            risk_score = self._calculate_portfolio_risk(solution, risk_matrix)
            
            return {
                'optimization_type': 'quantum_QAOA',
                'selected_assets': selected_assets,
                'allocation': {assets[i]: float(solution[i]) for i in range(len(assets))},
                'expected_return': float(total_return),
                'risk_score': float(risk_score),
                'sharpe_ratio': float(total_return / risk_score) if risk_score > 0 else 0,
                'budget_used': float(sum(solution)),
                'optimization_time': datetime.now().isoformat(),
                'quantum_advantage': True
            }
            
        except Exception as e:
            logger.warning("Quantum optimization failed, falling back to classical", error=str(e))
            return self._classical_optimization(assets, expected_returns, risk_matrix, risk_tolerance, budget)
    
    def _classical_optimization(self, 
                               assets: List[str],
                               expected_returns: List[float],
                               risk_matrix: List[List[float]],
                               risk_tolerance: float,
                               budget: float) -> Dict:
        """Perform classical optimization as fallback"""
        try:
            # Simple greedy optimization
            n_assets = len(assets)
            
            # Calculate risk-adjusted returns
            risk_adjusted_returns = []
            for i in range(n_assets):
                risk = np.sqrt(risk_matrix[i][i]) if i < len(risk_matrix) else 1.0
                risk_adjusted_returns.append(expected_returns[i] / (risk + 1e-6))
            
            # Sort by risk-adjusted returns
            sorted_indices = sorted(range(n_assets), key=lambda i: risk_adjusted_returns[i], reverse=True)
            
            # Select top assets within budget
            selected_assets = []
            allocation = {}
            total_budget_used = 0
            
            for i in sorted_indices:
                if total_budget_used + 1 <= budget:
                    selected_assets.append(assets[i])
                    allocation[assets[i]] = 1.0
                    total_budget_used += 1
            
            # Calculate metrics
            total_return = sum(expected_returns[i] for i in range(n_assets) if assets[i] in selected_assets)
            solution = [1.0 if assets[i] in selected_assets else 0.0 for i in range(n_assets)]
            risk_score = self._calculate_portfolio_risk(solution, risk_matrix)
            
            return {
                'optimization_type': 'classical_greedy',
                'selected_assets': selected_assets,
                'allocation': allocation,
                'expected_return': float(total_return),
                'risk_score': float(risk_score),
                'sharpe_ratio': float(total_return / risk_score) if risk_score > 0 else 0,
                'budget_used': float(total_budget_used),
                'optimization_time': datetime.now().isoformat(),
                'quantum_advantage': False
            }
            
        except Exception as e:
            logger.error("Classical optimization failed", error=str(e))
            raise Exception(f"Classical optimization failed: {str(e)}")
    
    def _calculate_portfolio_risk(self, allocation: List[float], risk_matrix: List[List[float]]) -> float:
        """Calculate portfolio risk using covariance matrix"""
        try:
            allocation = np.array(allocation)
            risk_matrix = np.array(risk_matrix)
            
            # Ensure matrices are compatible
            min_size = min(len(allocation), len(risk_matrix))
            allocation = allocation[:min_size]
            risk_matrix = risk_matrix[:min_size, :min_size]
            
            # Calculate portfolio variance
            portfolio_variance = np.dot(allocation, np.dot(risk_matrix, allocation))
            
            # Return standard deviation (risk)
            return np.sqrt(portfolio_variance)
            
        except Exception as e:
            logger.warning("Risk calculation failed", error=str(e))
            return 1.0  # Default risk value
    
    def optimize_trading_strategy(self, 
                                 market_data: Dict,
                                 constraints: Dict) -> Dict:
        """
        Optimize trading strategy using quantum algorithms
        
        Args:
            market_data: Current market data
            constraints: Trading constraints
            
        Returns:
            Dictionary containing optimized strategy
        """
        try:
            logger.info("Optimizing trading strategy")
            
            # Extract market data
            assets = market_data.get('assets', ['crude_oil', 'natural_gas', 'electricity'])
            prices = market_data.get('prices', [50.0, 3.0, 0.1])
            volatilities = market_data.get('volatilities', [0.1, 0.15, 0.2])
            
            # Calculate expected returns (simplified)
            expected_returns = [price * 0.05 for price in prices]  # 5% expected return
            
            # Create risk matrix
            risk_matrix = [[vol**2 for vol in volatilities] for _ in volatilities]
            
            # Set diagonal elements
            for i in range(len(volatilities)):
                risk_matrix[i][i] = volatilities[i]**2
            
            # Optimize portfolio
            result = self.optimize_portfolio(
                assets=assets,
                expected_returns=expected_returns,
                risk_matrix=risk_matrix,
                risk_tolerance=constraints.get('risk_tolerance', 0.5),
                budget=constraints.get('budget', 1000000.0)
            )
            
            # Add strategy-specific recommendations
            result['strategy_recommendations'] = self._generate_strategy_recommendations(result)
            result['market_conditions'] = self._analyze_market_conditions(market_data)
            
            return result
            
        except Exception as e:
            logger.error("Strategy optimization failed", error=str(e))
            raise Exception(f"Strategy optimization failed: {str(e)}")
    
    def _generate_strategy_recommendations(self, optimization_result: Dict) -> List[str]:
        """Generate trading strategy recommendations"""
        recommendations = []
        
        if optimization_result['sharpe_ratio'] > 2.0:
            recommendations.append("High Sharpe ratio - consider increasing position size")
        elif optimization_result['sharpe_ratio'] < 0.5:
            recommendations.append("Low Sharpe ratio - consider reducing risk or diversifying")
        
        if optimization_result['risk_score'] > 0.2:
            recommendations.append("High portfolio risk - consider hedging strategies")
        
        if len(optimization_result['selected_assets']) < 3:
            recommendations.append("Low diversification - consider adding more assets")
        
        return recommendations
    
    def _analyze_market_conditions(self, market_data: Dict) -> Dict:
        """Analyze current market conditions"""
        try:
            prices = market_data.get('prices', [])
            volatilities = market_data.get('volatilities', [])
            
            avg_volatility = np.mean(volatilities) if volatilities else 0.1
            price_trend = np.mean(np.diff(prices)) if len(prices) > 1 else 0
            
            return {
                'market_volatility': float(avg_volatility),
                'price_trend': float(price_trend),
                'market_regime': 'bull' if price_trend > 0 else 'bear' if price_trend < 0 else 'sideways',
                'risk_level': 'high' if avg_volatility > 0.15 else 'medium' if avg_volatility > 0.1 else 'low'
            }
            
        except Exception as e:
            logger.warning("Market analysis failed", error=str(e))
            return {
                'market_volatility': 0.1,
                'price_trend': 0.0,
                'market_regime': 'unknown',
                'risk_level': 'medium'
            }

# Global instance
quantum_optimization_service = QuantumOptimizationService()
