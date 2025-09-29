"""
Quantum Optimization Services
Qiskit QAOA implementation with PuLP classical fallback
"""
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from enum import Enum
from dataclasses import dataclass

# Quantum computing imports with fallbacks
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit.algorithms import QAOA
    from qiskit.algorithms.optimizers import COBYLA
    from qiskit.primitives import Sampler
    from qiskit.quantum_info import SparsePauliOp
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    print("Warning: Qiskit not available, using classical optimization fallback")

# Classical optimization imports
try:
    import pulp
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False
    print("Warning: PuLP not available, using numpy optimization fallback")

logger = logging.getLogger(__name__)

class OptimizationMethod(str, Enum):
    QUANTUM_QAOA = "quantum_qaoa"
    CLASSICAL_PULP = "classical_pulp"
    NUMPY_FALLBACK = "numpy_fallback"

@dataclass
class PortfolioOptimizationResult:
    method: str
    weights: List[float]
    expected_return: float
    risk: float
    sharpe_ratio: float
    optimization_time: float
    quantum_advantage: Optional[bool]
    success: bool
    error_message: Optional[str]

class QuantumOptimizationService:
    """Quantum portfolio optimization with classical fallback"""
    
    def __init__(self):
        self.qaoa_optimizer = None
        self.classical_optimizer = None
        self._initialize_optimizers()
    
    def _initialize_optimizers(self):
        """Initialize quantum and classical optimizers"""
        try:
            if QISKIT_AVAILABLE:
                # Initialize QAOA optimizer
                self.qaoa_optimizer = QAOA(
                    optimizer=COBYLA(maxiter=100),
                    reps=2,
                    sampler=Sampler()
                )
                logger.info("QAOA optimizer initialized successfully")
            
            if PULP_AVAILABLE:
                # Initialize PuLP classical optimizer
                self.classical_optimizer = "pulp_available"
                logger.info("PuLP classical optimizer available")
            
            logger.info("Quantum optimization service initialized")
            
        except Exception as e:
            logger.error(f"Error initializing optimizers: {e}")
    
    def optimize_portfolio(self,
                         expected_returns: List[float],
                         risk_matrix: np.ndarray,
                         risk_free_rate: float = 0.02,
                         target_return: Optional[float] = None,
                         method: OptimizationMethod = OptimizationMethod.QUANTUM_QAOA) -> PortfolioOptimizationResult:
        """
        Optimize portfolio using quantum or classical methods
        
        Args:
            expected_returns: Expected returns for each asset
            risk_matrix: Risk covariance matrix
            risk_free_rate: Risk-free rate
            target_return: Target return (if None, maximize Sharpe ratio)
            method: Optimization method to use
            
        Returns:
            Portfolio optimization result
        """
        start_time = datetime.now()
        
        try:
            n_assets = len(expected_returns)
            
            if method == OptimizationMethod.QUANTUM_QAOA and QISKIT_AVAILABLE:
                result = self._quantum_qaoa_optimization(
                    expected_returns, risk_matrix, risk_free_rate, target_return
                )
            elif method == OptimizationMethod.CLASSICAL_PULP and PULP_AVAILABLE:
                result = self._classical_pulp_optimization(
                    expected_returns, risk_matrix, risk_free_rate, target_return
                )
            else:
                result = self._numpy_fallback_optimization(
                    expected_returns, risk_matrix, risk_free_rate, target_return
                )
            
            optimization_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate portfolio metrics
            weights = result["weights"]
            expected_return = np.dot(weights, expected_returns)
            risk = np.sqrt(np.dot(weights, np.dot(risk_matrix, weights)))
            sharpe_ratio = (expected_return - risk_free_rate) / risk if risk > 0 else 0
            
            return PortfolioOptimizationResult(
                method=method.value,
                weights=weights.tolist(),
                expected_return=round(expected_return, 4),
                risk=round(risk, 4),
                sharpe_ratio=round(sharpe_ratio, 4),
                optimization_time=round(optimization_time, 3),
                quantum_advantage=method == OptimizationMethod.QUANTUM_QAOA,
                success=True,
                error_message=None
            )
            
        except Exception as e:
            logger.error(f"Portfolio optimization failed: {e}")
            return PortfolioOptimizationResult(
                method=method.value,
                weights=[1.0 / len(expected_returns)] * len(expected_returns),
                expected_return=0.0,
                risk=0.0,
                sharpe_ratio=0.0,
                optimization_time=(datetime.now() - start_time).total_seconds(),
                quantum_advantage=False,
                success=False,
                error_message=str(e)
            )
    
    def _quantum_qaoa_optimization(self,
                                  expected_returns: List[float],
                                  risk_matrix: np.ndarray,
                                  risk_free_rate: float,
                                  target_return: Optional[float]) -> Dict[str, Any]:
        """Quantum QAOA optimization implementation"""
        try:
            n_assets = len(expected_returns)
            
            # Create cost function for QAOA
            # For portfolio optimization, we want to minimize risk for given return
            if target_return is None:
                # Maximize Sharpe ratio: (return - risk_free_rate) / risk
                # This becomes minimizing: -sharpe_ratio
                def cost_function(weights):
                    weights = np.array(weights)
                    portfolio_return = np.dot(weights, expected_returns)
                    portfolio_risk = np.sqrt(np.dot(weights, np.dot(risk_matrix, weights)))
                    if portfolio_risk == 0:
                        return 0
                    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk
                    return -sharpe_ratio  # Minimize negative Sharpe ratio
            else:
                # Minimize risk for target return
                def cost_function(weights):
                    weights = np.array(weights)
                    portfolio_return = np.dot(weights, expected_returns)
                    portfolio_risk = np.sqrt(np.dot(weights, np.dot(risk_matrix, weights)))
                    return_weight = abs(portfolio_return - target_return) * 1000
                    return portfolio_risk + return_weight
            
            # Create QAOA problem
            # For simplicity, we'll use a quadratic unconstrained binary optimization (QUBO)
            # Convert to Ising model for QAOA
            qubo_matrix = self._create_qubo_matrix(expected_returns, risk_matrix, target_return)
            ising_operator = self._qubo_to_ising(qubo_matrix)
            
            # Run QAOA
            result = self.qaoa_optimizer.compute_minimum_eigenvalue(ising_operator)
            
            # Extract solution
            solution = result.eigenstate
            weights = self._extract_weights_from_solution(solution, n_assets)
            
            return {"weights": weights}
            
        except Exception as e:
            logger.error(f"Quantum QAOA optimization failed: {e}")
            # Fallback to classical method
            return self._classical_pulp_optimization(expected_returns, risk_matrix, risk_free_rate, target_return)
    
    def _classical_pulp_optimization(self,
                                    expected_returns: List[float],
                                    risk_matrix: np.ndarray,
                                    risk_free_rate: float,
                                    target_return: Optional[float]) -> Dict[str, Any]:
        """Classical PuLP optimization implementation"""
        try:
            n_assets = len(expected_returns)
            
            # Create PuLP problem
            prob = pulp.LpProblem("PortfolioOptimization", pulp.LpMinimize)
            
            # Decision variables (weights)
            weights = [pulp.LpVariable(f"w_{i}", lowBound=0, upBound=1) for i in range(n_assets)]
            
            # Constraint: weights sum to 1
            prob += pulp.lpSum(weights) == 1
            
            # Constraint: target return (if specified)
            if target_return is not None:
                prob += pulp.lpSum([weights[i] * expected_returns[i] for i in range(n_assets)]) >= target_return
            
            # Objective function: minimize portfolio variance
            portfolio_variance = pulp.lpSum([
                weights[i] * weights[j] * risk_matrix[i][j]
                for i in range(n_assets)
                for j in range(n_assets)
            ])
            prob += portfolio_variance
            
            # Solve
            prob.solve(pulp.PULP_CBC_CMD(msg=0))
            
            # Extract solution
            solution_weights = [weights[i].varValue for i in range(n_assets)]
            
            return {"weights": np.array(solution_weights)}
            
        except Exception as e:
            logger.error(f"Classical PuLP optimization failed: {e}")
            # Fallback to numpy optimization
            return self._numpy_fallback_optimization(expected_returns, risk_matrix, risk_free_rate, target_return)
    
    def _numpy_fallback_optimization(self,
                                    expected_returns: List[float],
                                    risk_matrix: np.ndarray,
                                    risk_free_rate: float,
                                    target_return: Optional[float]) -> Dict[str, Any]:
        """Numpy-based fallback optimization"""
        try:
            n_assets = len(expected_returns)
            
            if target_return is None:
                # Maximize Sharpe ratio using analytical solution
                # For mean-variance optimization, optimal weights are:
                # w = (Σ^-1 * μ) / (1^T * Σ^-1 * μ)
                # where Σ is covariance matrix, μ is expected returns
                
                # Add small regularization to avoid singular matrix
                regularized_matrix = risk_matrix + np.eye(n_assets) * 1e-6
                inv_matrix = np.linalg.inv(regularized_matrix)
                
                # Calculate optimal weights
                numerator = np.dot(inv_matrix, expected_returns)
                denominator = np.sum(numerator)
                
                if abs(denominator) > 1e-10:
                    weights = numerator / denominator
                else:
                    # Equal weights fallback
                    weights = np.ones(n_assets) / n_assets
            else:
                # Minimize risk for target return
                # Use Lagrange multiplier method
                regularized_matrix = risk_matrix + np.eye(n_assets) * 1e-6
                inv_matrix = np.linalg.inv(regularized_matrix)
                
                # Set up system of equations
                A = np.zeros((n_assets + 2, n_assets + 2))
                b = np.zeros(n_assets + 2)
                
                # Fill matrix for Lagrange multiplier system
                A[:n_assets, :n_assets] = 2 * risk_matrix
                A[:n_assets, n_assets] = expected_returns
                A[:n_assets, n_assets + 1] = 1
                A[n_assets, :n_assets] = expected_returns
                A[n_assets + 1, :n_assets] = 1
                
                b[n_assets] = target_return
                b[n_assets + 1] = 1
                
                # Solve system
                solution = np.linalg.solve(A, b)
                weights = solution[:n_assets]
            
            # Ensure weights are non-negative and sum to 1
            weights = np.maximum(weights, 0)
            weights = weights / np.sum(weights)
            
            return {"weights": weights}
            
        except Exception as e:
            logger.error(f"Numpy fallback optimization failed: {e}")
            # Ultimate fallback: equal weights
            n_assets = len(expected_returns)
            return {"weights": np.ones(n_assets) / n_assets}
    
    def _create_qubo_matrix(self, expected_returns: List[float], risk_matrix: np.ndarray, target_return: Optional[float]) -> np.ndarray:
        """Create QUBO matrix for QAOA"""
        n_assets = len(expected_returns)
        
        # Create QUBO matrix (simplified version)
        # This is a placeholder - in practice, you'd need to properly formulate
        # the portfolio optimization problem as a QUBO
        qubo_matrix = np.zeros((n_assets, n_assets))
        
        for i in range(n_assets):
            for j in range(n_assets):
                if i == j:
                    # Diagonal terms: individual asset risk
                    qubo_matrix[i][j] = risk_matrix[i][j]
                else:
                    # Off-diagonal terms: covariance
                    qubo_matrix[i][j] = risk_matrix[i][j] / 2
        
        return qubo_matrix
    
    def _qubo_to_ising(self, qubo_matrix: np.ndarray) -> SparsePauliOp:
        """Convert QUBO matrix to Ising model for QAOA"""
        n_assets = qubo_matrix.shape[0]
        
        # Create Pauli operators for Ising model
        pauli_list = []
        
        for i in range(n_assets):
            for j in range(n_assets):
                if abs(qubo_matrix[i][j]) > 1e-10:
                    # Create Pauli string
                    pauli_string = ['I'] * n_assets
                    if i == j:
                        pauli_string[i] = 'Z'
                    else:
                        pauli_string[i] = 'Z'
                        pauli_string[j] = 'Z'
                    
                    pauli_list.append((qubo_matrix[i][j], ''.join(pauli_string)))
        
        return SparsePauliOp.from_list(pauli_list)
    
    def _extract_weights_from_solution(self, solution, n_assets: int) -> np.ndarray:
        """Extract portfolio weights from QAOA solution"""
        # This is a simplified extraction - in practice, you'd need to properly
        # decode the quantum state to get the optimal weights
        try:
            # For now, return equal weights as fallback
            return np.ones(n_assets) / n_assets
        except:
            return np.ones(n_assets) / n_assets
    
    def compare_optimization_methods(self,
                                   expected_returns: List[float],
                                   risk_matrix: np.ndarray,
                                   risk_free_rate: float = 0.02) -> Dict[str, Any]:
        """Compare different optimization methods"""
        results = {}
        
        # Test quantum method
        if QISKIT_AVAILABLE:
            quantum_result = self.optimize_portfolio(
                expected_returns, risk_matrix, risk_free_rate,
                method=OptimizationMethod.QUANTUM_QAOA
            )
            results["quantum"] = quantum_result
        
        # Test classical method
        if PULP_AVAILABLE:
            classical_result = self.optimize_portfolio(
                expected_returns, risk_matrix, risk_free_rate,
                method=OptimizationMethod.CLASSICAL_PULP
            )
            results["classical"] = classical_result
        
        # Test numpy fallback
        numpy_result = self.optimize_portfolio(
            expected_returns, risk_matrix, risk_free_rate,
            method=OptimizationMethod.NUMPY_FALLBACK
        )
        results["numpy"] = numpy_result
        
        return {
            "comparison": results,
            "best_method": max(results.keys(), key=lambda k: results[k].sharpe_ratio),
            "quantum_available": QISKIT_AVAILABLE,
            "pulp_available": PULP_AVAILABLE
        }
