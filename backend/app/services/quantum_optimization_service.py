import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import structlog
import warnings

logger = structlog.get_logger()

@dataclass
class PortfolioAsset:
    """Represents a portfolio asset with risk and return characteristics"""
    symbol: str
    weight: float
    expected_return: float
    volatility: float
    sector: str
    region: str
    esg_score: float

class QuantumOptimizationService:
    """Quantum computing service for portfolio optimization and risk management"""
    
    def __init__(self):
        self.qiskit_available = False
        self.quantum_backend = None
        self.classical_backend = None
        
        # Try to import Qiskit with proper error handling
        try:
            import qiskit
            from qiskit import QuantumCircuit, Aer, execute
            from qiskit.algorithms import VQE, QAOA
            from qiskit.algorithms.optimizers import SPSA, COBYLA
            from qiskit.circuit.library import TwoLocal
            from qiskit.quantum_info import Pauli
            from qiskit.opflow import PauliSumOp, I, X, Z
            from qiskit_machine_learning.algorithms import VQC
            from qiskit_machine_learning.neural_networks import CircuitQNN
            
            # Store Qiskit components
            self.qiskit = qiskit
            self.QuantumCircuit = QuantumCircuit
            self.Aer = Aer
            self.execute = execute
            self.VQE = VQE
            self.QAOA = QAOA
            self.SPSA = SPSA
            self.COBYLA = COBYLA
            self.TwoLocal = TwoLocal
            self.Pauli = Pauli
            self.PauliSumOp = PauliSumOp
            self.I = I
            self.X = X
            self.Z = Z
            self.VQC = VQC
            self.CircuitQNN = CircuitQNN
            
            self.qiskit_available = True
            self.quantum_backend = Aer.get_backend('qasm_simulator')
            self.classical_backend = Aer.get_backend('statevector_simulator')
            
            logger.info("Qiskit successfully imported and quantum backends configured")
            
        except ImportError as e:
            logger.warning(f"Qiskit not available: {e}. Using classical optimization fallback.")
            self.qiskit_available = False
        except Exception as e:
            logger.warning(f"Error initializing Qiskit: {e}. Using classical optimization fallback.")
            self.qiskit_available = False
        
        # Classical optimization backend
        try:
            from scipy.optimize import minimize
            self.scipy_minimize = minimize
        except ImportError:
            logger.warning("SciPy not available. Limited optimization capabilities.")
            self.scipy_minimize = None

    def optimize_portfolio_quantum(self, assets: List[PortfolioAsset], 
                                 target_return: float = None,
                                 risk_tolerance: float = 0.5,
                                 max_iterations: int = 100) -> Dict[str, Any]:
        """Optimize portfolio using quantum algorithms with classical fallback"""
        try:
            if not assets:
                return {"error": "No assets provided"}
            
            # Prepare data
            returns = np.array([asset.expected_return for asset in assets])
            volatilities = np.array([asset.volatility for asset in assets])
            correlation_matrix = self._create_correlation_matrix(len(assets))
            
            # Choose optimization method based on problem size and Qiskit availability
            if self.qiskit_available and len(assets) <= 8:  # Quantum algorithms work best for smaller problems
                if len(assets) <= 4:
                    result = self._optimize_with_qaoa(assets, returns, volatilities, correlation_matrix, 
                                                    target_return, risk_tolerance, max_iterations)
                else:
                    result = self._optimize_with_vqe(assets, returns, volatilities, correlation_matrix,
                                                   target_return, risk_tolerance, max_iterations)
            else:
                # Use classical optimization
                result = self._classical_portfolio_optimization(assets, target_return, risk_tolerance)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in portfolio optimization: {e}")
            return {"error": str(e)}

    def _optimize_with_qaoa(self, assets: List[PortfolioAsset], returns: np.ndarray, 
                           volatilities: np.ndarray, correlation_matrix: np.ndarray,
                           target_return: float, risk_tolerance: float, max_iterations: int) -> Dict[str, Any]:
        """Optimize portfolio using Quantum Approximate Optimization Algorithm (QAOA)"""
        try:
            # Create cost operator for portfolio optimization
            cost_operator = self._create_portfolio_cost_operator(assets, returns, volatilities, 
                                                              correlation_matrix, target_return, risk_tolerance)
            
            # Create QAOA circuit
            qaoa = self.QAOA(cost_operator, optimizer=self.SPSA(maxiter=max_iterations))
            
            # Execute on quantum backend
            result = qaoa.run(self.quantum_backend)
            
            # Extract optimal weights
            optimal_weights = self._extract_weights_from_qaoa_result(result, len(assets))
            
            # Calculate portfolio metrics
            portfolio_metrics = self._calculate_portfolio_metrics(assets, optimal_weights, 
                                                               returns, volatilities, correlation_matrix)
            
            return {
                "optimization_method": "QAOA",
                "optimal_weights": optimal_weights,
                "portfolio_metrics": portfolio_metrics,
                "quantum_result": str(result),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"QAOA optimization failed: {e}")
            # Fallback to classical optimization
            return self._classical_portfolio_optimization(assets, target_return, risk_tolerance)

    def _optimize_with_vqe(self, assets: List[PortfolioAsset], returns: np.ndarray,
                          volatilities: np.ndarray, correlation_matrix: np.ndarray,
                          target_return: float, risk_tolerance: float, max_iterations: int) -> Dict[str, Any]:
        """Optimize portfolio using Variational Quantum Eigensolver (VQE)"""
        try:
            # Create cost operator
            cost_operator = self._create_portfolio_cost_operator(assets, returns, volatilities, 
                                                              correlation_matrix, target_return, risk_tolerance)
            
            # Create variational form
            var_form = self.TwoLocal(cost_operator.num_qubits, ['ry', 'rz'], 'cz', reps=2)
            
            # Create VQE
            vqe = self.VQE(var_form, optimizer=self.COBYLA(maxiter=max_iterations))
            
            # Execute on quantum backend
            result = vqe.run(self.quantum_backend)
            
            # Extract optimal weights
            optimal_weights = self._extract_weights_from_vqe_result(result, len(assets))
            
            # Calculate portfolio metrics
            portfolio_metrics = self._calculate_portfolio_metrics(assets, optimal_weights, 
                                                               returns, volatilities, correlation_matrix)
            
            return {
                "optimization_method": "VQE",
                "optimal_weights": optimal_weights,
                "portfolio_metrics": portfolio_metrics,
                "quantum_result": str(result),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"VQE optimization failed: {e}")
            # Fallback to classical optimization
            return self._classical_portfolio_optimization(assets, target_return, risk_tolerance)

    def _create_portfolio_cost_operator(self, assets: List[PortfolioAsset], returns: np.ndarray,
                                      volatilities: np.ndarray, correlation_matrix: np.ndarray,
                                      target_return: float, risk_tolerance: float) -> Any:
        """Create quantum cost operator for portfolio optimization"""
        try:
            n_assets = len(assets)
            
            # Create Pauli operators for each asset
            pauli_operators = []
            for i in range(n_assets):
                # Return term
                return_op = returns[i] * self.I
                # Volatility term
                vol_op = volatilities[i] * self.Z
                # Add to list
                pauli_operators.append(return_op + vol_op)
            
            # Create correlation terms
            correlation_terms = []
            for i in range(n_assets):
                for j in range(i+1, n_assets):
                    if correlation_matrix[i, j] != 0:
                        corr_op = correlation_matrix[i, j] * (self.Z ^ self.Z)
                        correlation_terms.append(corr_op)
            
            # Combine all terms
            cost_operator = sum(pauli_operators) + sum(correlation_terms)
            
            # Add target return constraint if specified
            if target_return is not None:
                target_op = target_return * self.I
                cost_operator += target_op
            
            return cost_operator
            
        except Exception as e:
            logger.error(f"Error creating cost operator: {e}")
            # Return a simple operator as fallback
            return self.I

    def _extract_weights_from_qaoa_result(self, result: Any, n_assets: int) -> List[float]:
        """Extract portfolio weights from QAOA result"""
        try:
            # Get the most likely bitstring
            counts = result.get_counts()
            if not counts:
                return [1.0/n_assets] * n_assets
            
            # Find the bitstring with highest count
            best_bitstring = max(counts, key=counts.get)
            
            # Convert bitstring to weights
            weights = []
            for bit in best_bitstring:
                weights.append(float(bit))
            
            # Normalize weights to sum to 1
            total = sum(weights)
            if total > 0:
                weights = [w/total for w in weights]
            else:
                weights = [1.0/n_assets] * n_assets
            
            return weights
            
        except Exception as e:
            logger.error(f"Error extracting weights from QAOA result: {e}")
            return [1.0/n_assets] * n_assets

    def _extract_weights_from_vqe_result(self, result: Any, n_assets: int) -> List[float]:
        """Extract portfolio weights from VQE result"""
        try:
            # Get the optimal parameters
            optimal_params = result.optimal_parameters
            
            if not optimal_params:
                return [1.0/n_assets] * n_assets
            
            # Convert parameters to weights (simplified approach)
            weights = []
            for i in range(n_assets):
                if i < len(optimal_params):
                    # Normalize parameter to [0, 1] range
                    weight = (optimal_params[i] + 1) / 2
                    weights.append(max(0, min(1, weight)))
                else:
                    weights.append(1.0/n_assets)
            
            # Normalize weights to sum to 1
            total = sum(weights)
            if total > 0:
                weights = [w/total for w in weights]
            else:
                weights = [1.0/n_assets] * n_assets
            
            return weights
            
        except Exception as e:
            logger.error(f"Error extracting weights from VQE result: {e}")
            return [1.0/n_assets] * n_assets

    def _create_correlation_matrix(self, n_assets: int) -> np.ndarray:
        """Create a realistic correlation matrix for assets"""
        try:
            # Create a positive semi-definite correlation matrix
            np.random.seed(42)  # For reproducibility
            random_matrix = np.random.randn(n_assets, n_assets)
            correlation_matrix = np.dot(random_matrix, random_matrix.T)
            
            # Normalize to get correlation coefficients between -1 and 1
            for i in range(n_assets):
                for j in range(n_assets):
                    if i == j:
                        correlation_matrix[i, j] = 1.0
                    else:
                        correlation_matrix[i, j] = correlation_matrix[i, j] / np.sqrt(correlation_matrix[i, i] * correlation_matrix[j, j])
                        correlation_matrix[i, j] = max(-0.8, min(0.8, correlation_matrix[i, j]))  # Limit correlations
            
            return correlation_matrix
            
        except Exception as e:
            logger.error(f"Error creating correlation matrix: {e}")
            # Return identity matrix as fallback
            return np.eye(n_assets)

    def _calculate_portfolio_metrics(self, assets: List[PortfolioAsset], weights: List[float],
                                   returns: np.ndarray, volatilities: np.ndarray, 
                                   correlation_matrix: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive portfolio metrics"""
        try:
            # Expected return
            expected_return = np.sum(weights * returns)
            
            # Portfolio volatility
            portfolio_variance = 0
            for i in range(len(assets)):
                for j in range(len(assets)):
                    portfolio_variance += weights[i] * weights[j] * volatilities[i] * volatilities[j] * correlation_matrix[i, j]
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            # Sharpe ratio (assuming risk-free rate of 2%)
            risk_free_rate = 0.02
            sharpe_ratio = (expected_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
            
            # Portfolio ESG score
            portfolio_esg_score = np.sum([weights[i] * assets[i].esg_score for i in range(len(assets))])
            
            # Diversification ratio
            weighted_vol = np.sum(weights * volatilities)
            diversification_ratio = weighted_vol / portfolio_volatility if portfolio_volatility > 0 else 1
            
            return {
                "expected_return": round(expected_return, 4),
                "portfolio_volatility": round(portfolio_volatility, 4),
                "sharpe_ratio": round(sharpe_ratio, 4),
                "portfolio_esg_score": round(portfolio_esg_score, 2),
                "diversification_ratio": round(diversification_ratio, 4),
                "risk_adjusted_return": round(expected_return / portfolio_volatility if portfolio_volatility > 0 else 0, 4)
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return {
                "expected_return": 0.0,
                "portfolio_volatility": 0.0,
                "sharpe_ratio": 0.0,
                "portfolio_esg_score": 0.0,
                "diversification_ratio": 1.0,
                "risk_adjusted_return": 0.0
            }

    def _classical_portfolio_optimization(self, assets: List[PortfolioAsset], 
                                        target_return: float, risk_tolerance: float) -> Dict[str, Any]:
        """Classical portfolio optimization using scipy"""
        try:
            if not self.scipy_minimize:
                return {"error": "SciPy optimization not available"}
            
            n_assets = len(assets)
            returns = np.array([asset.expected_return for asset in assets])
            volatilities = np.array([asset.volatility for asset in assets])
            correlation_matrix = self._create_correlation_matrix(n_assets)
            
            # Define objective function (minimize risk)
            def objective(weights):
                portfolio_variance = 0
                for i in range(n_assets):
                    for j in range(n_assets):
                        portfolio_variance += weights[i] * weights[j] * volatilities[i] * volatilities[j] * correlation_matrix[i, j]
                return np.sqrt(portfolio_variance)
            
            # Constraints: weights sum to 1
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            
            # Bounds: weights between 0 and 1
            bounds = tuple((0, 1) for _ in range(n_assets))
            
            # Initial guess: equal weights
            initial_weights = np.array([1.0/n_assets] * n_assets)
            
            # Optimize
            result = self.scipy_minimize(
                objective, 
                initial_weights, 
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if result.success:
                optimal_weights = result.x.tolist()
                portfolio_metrics = self._calculate_portfolio_metrics(assets, optimal_weights, 
                                                                   returns, volatilities, correlation_matrix)
                
                return {
                    "optimization_method": "Classical (SLSQP)",
                    "optimal_weights": optimal_weights,
                    "portfolio_metrics": portfolio_metrics,
                    "optimization_success": True,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"Classical optimization failed: {result.message}"}
                
        except Exception as e:
            logger.error(f"Error in classical optimization: {e}")
            return {"error": str(e)}

    def quantum_risk_assessment(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform quantum-enhanced risk assessment"""
        try:
            if not self.qiskit_available:
                return self._classical_risk_assessment(portfolio_data)
            
            # Create quantum circuit for risk assessment
            n_qubits = min(8, len(portfolio_data.get("assets", [])))
            qc = self.QuantumCircuit(n_qubits, n_qubits)
            
            # Apply Hadamard gates to create superposition
            for i in range(n_qubits):
                qc.h(i)
            
            # Apply rotation gates based on risk parameters
            assets = portfolio_data.get("assets", [])
            for i in range(min(n_qubits, len(assets))):
                risk_factor = assets[i].volatility if hasattr(assets[i], 'volatility') else 0.1
                qc.ry(risk_factor * np.pi, i)
            
            # Measure all qubits
            qc.measure_all()
            
            # Execute on quantum backend
            job = self.execute(qc, self.quantum_backend, shots=1000)
            result = job.result()
            counts = result.get_counts()
            
            # Analyze quantum results
            risk_analysis = self._analyze_quantum_risk_patterns(counts, portfolio_data)
            
            return {
                "method": "quantum",
                "risk_metrics": risk_analysis,
                "quantum_circuit": str(qc),
                "measurement_counts": counts,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Quantum risk assessment failed: {e}")
            return self._classical_risk_assessment(portfolio_data)

    def _analyze_quantum_risk_patterns(self, counts: Dict[str, int], portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze quantum measurement results for risk patterns"""
        try:
            total_shots = sum(counts.values())
            if total_shots == 0:
                return {"error": "No quantum measurements available"}
            
            # Calculate entropy as a measure of uncertainty
            entropy = 0
            for bitstring, count in counts.items():
                probability = count / total_shots
                if probability > 0:
                    entropy -= probability * np.log2(probability)
            
            # Analyze bitstring patterns
            risk_levels = {"low": 0, "medium": 0, "high": 0}
            for bitstring, count in counts.items():
                # Count 1s in bitstring as risk indicator
                risk_count = bitstring.count('1')
                if risk_count <= len(bitstring) // 3:
                    risk_levels["low"] += count
                elif risk_count <= 2 * len(bitstring) // 3:
                    risk_levels["medium"] += count
                else:
                    risk_levels["high"] += count
            
            # Normalize risk levels
            for level in risk_levels:
                risk_levels[level] = risk_levels[level] / total_shots
            
            return {
                "quantum_entropy": round(entropy, 4),
                "risk_distribution": risk_levels,
                "total_measurements": total_shots,
                "uncertainty_level": "high" if entropy > 2 else "medium" if entropy > 1 else "low"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing quantum risk patterns: {e}")
            return {"error": str(e)}

    def _classical_risk_assessment(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classical risk assessment fallback"""
        try:
            assets = portfolio_data.get("assets", [])
            if not assets:
                return {"error": "No portfolio assets provided"}
            
            # Calculate classical risk metrics
            total_volatility = sum(asset.volatility for asset in assets)
            avg_volatility = total_volatility / len(assets)
            
            # Simple risk classification
            if avg_volatility < 0.1:
                risk_level = "low"
            elif avg_volatility < 0.2:
                risk_level = "medium"
            else:
                risk_level = "high"
            
            return {
                "method": "classical",
                "risk_metrics": {
                    "average_volatility": round(avg_volatility, 4),
                    "total_volatility": round(total_volatility, 4),
                    "risk_level": risk_level,
                    "asset_count": len(assets)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in classical risk assessment: {e}")
            return {"error": str(e)}

    def get_quantum_status(self) -> Dict[str, Any]:
        """Get quantum computing service status"""
        return {
            "qiskit_available": self.qiskit_available,
            "quantum_backend": str(self.quantum_backend) if self.quantum_backend else None,
            "classical_backend": str(self.classical_backend) if self.classical_backend else None,
            "scipy_available": self.scipy_minimize is not None,
            "supported_algorithms": ["QAOA", "VQE", "Classical"] if self.qiskit_available else ["Classical"],
            "max_qubits": 8 if self.qiskit_available else 0,
            "timestamp": datetime.now().isoformat()
        }

# Global instance
quantum_optimization_service = QuantumOptimizationService()
