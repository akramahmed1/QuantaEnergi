import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import structlog
import warnings
import threading
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

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
        
        # Initialize thread pool for concurrent operations
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.optimization_lock = threading.Lock()
    
    def optimize_portfolio_concurrent(self, assets: List[PortfolioAsset], 
                                    target_return: float = None,
                                    risk_tolerance: float = 0.5,
                                    max_iterations: int = 100) -> Dict[str, Any]:
        """Optimize portfolio using concurrent classical methods for better performance"""
        try:
            if not assets:
                return {"error": "No assets provided"}
            
            # Split assets into chunks for parallel processing
            chunk_size = max(1, len(assets) // 4)
            asset_chunks = [assets[i:i + chunk_size] for i in range(0, len(assets), chunk_size)]
            
            # Submit optimization tasks to thread pool
            futures = []
            for i, chunk in enumerate(asset_chunks):
                future = self.thread_pool.submit(
                    self._optimize_chunk,
                    chunk, target_return, risk_tolerance, max_iterations, i
                )
                futures.append(future)
            
            # Collect results
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)  # 30 second timeout per chunk
                    results.append(result)
                except Exception as e:
                    logger.error(f"Chunk optimization failed: {e}")
                    results.append({"error": str(e)})
            
            # Combine results
            combined_result = self._combine_chunk_results(results, assets)
            return combined_result
            
        except Exception as e:
            logger.error(f"Concurrent optimization failed: {e}")
            return {"error": str(e)}
    
    def _optimize_chunk(self, assets: List[PortfolioAsset], 
                        target_return: float, risk_tolerance: float, 
                        max_iterations: int, chunk_id: int) -> Dict[str, Any]:
        """Optimize a chunk of assets"""
        try:
            with self.optimization_lock:
                logger.info(f"Optimizing chunk {chunk_id} with {len(assets)} assets")
                
                # Handle empty assets case
                if not assets:
                    return {
                        "chunk_id": chunk_id,
                        "error": "No assets provided for optimization"
                    }
                
                # Use classical optimization for this chunk
                returns = np.array([asset.expected_return for asset in assets])
                volatilities = np.array([asset.volatility for asset in assets])
                
                # Simple optimization: maximize return while minimizing risk
                weights = np.ones(len(assets)) / len(assets)  # Equal weights initially
                
                # Adjust weights based on risk tolerance
                for i in range(len(assets)):
                    if volatilities[i] > np.mean(volatilities):
                        weights[i] *= (1 - risk_tolerance)
                    else:
                        weights[i] *= (1 + risk_tolerance)
                
                # Normalize weights
                weights = weights / np.sum(weights)
                
                return {
                    "chunk_id": chunk_id,
                    "assets": [asset.symbol for asset in assets],
                    "weights": weights.tolist(),
                    "expected_return": np.sum(returns * weights),
                    "volatility": np.sqrt(np.sum((weights * volatilities) ** 2)),
                    "status": "success"
                }
                
        except Exception as e:
            logger.error(f"Chunk {chunk_id} optimization failed: {e}")
            return {"chunk_id": chunk_id, "error": str(e)}
    
    def _combine_chunk_results(self, chunk_results: List[Dict[str, Any]], 
                              all_assets: List[PortfolioAsset]) -> Dict[str, Any]:
        """Combine results from multiple optimization chunks"""
        try:
            successful_chunks = [r for r in chunk_results if "error" not in r]
            
            if not successful_chunks:
                return {"error": "All optimization chunks failed"}
            
            # Combine weights from successful chunks
            combined_weights = []
            combined_return = 0
            combined_volatility = 0
            
            for chunk in successful_chunks:
                combined_weights.extend(chunk["weights"])
                combined_return += chunk["expected_return"]
                combined_volatility += chunk["volatility"]
            
            # Normalize combined weights
            combined_weights = np.array(combined_weights)
            combined_weights = combined_weights / np.sum(combined_weights)
            
            return {
                "optimization_method": "concurrent_classical",
                "total_assets": len(all_assets),
                "chunks_processed": len(successful_chunks),
                "weights": combined_weights.tolist(),
                "expected_return": combined_return / len(successful_chunks),
                "volatility": combined_volatility / len(successful_chunks),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error combining chunk results: {e}")
            return {"error": str(e)}
    
    def cleanup(self):
        """Clean up thread pool resources"""
        try:
            if hasattr(self, 'thread_pool'):
                self.thread_pool.shutdown(wait=True)
                logger.info("Thread pool shutdown completed")
        except Exception as e:
            logger.error(f"Error during thread pool cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()

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
    
    def optimize_portfolio_esg_focused(self, assets: List[PortfolioAsset], 
                                     target_esg_score: float = 80.0,
                                     risk_tolerance: float = 0.5,
                                     return_target: float = None) -> Dict[str, Any]:
        """Optimize portfolio with ESG focus using multi-objective optimization"""
        try:
            if not assets:
                return {"error": "No assets provided"}
            
            # Filter assets by minimum ESG score
            min_esg_threshold = target_esg_score - 10  # Allow some flexibility
            filtered_assets = [asset for asset in assets if asset.esg_score >= min_esg_threshold]
            
            if not filtered_assets:
                return {"error": f"No assets meet minimum ESG threshold of {min_esg_threshold}"}
            
            # Multi-objective optimization: balance ESG, return, and risk
            def esg_objective(weights):
                portfolio_esg = np.sum([weights[i] * filtered_assets[i].esg_score for i in range(len(filtered_assets))])
                return -portfolio_esg  # Minimize negative ESG (maximize ESG)
            
            def risk_objective(weights):
                returns = np.array([asset.expected_return for asset in filtered_assets])
                volatilities = np.array([asset.volatility for asset in filtered_assets])
                correlation_matrix = self._create_correlation_matrix(len(filtered_assets))
                
                portfolio_variance = 0
                for i in range(len(filtered_assets)):
                    for j in range(len(filtered_assets)):
                        portfolio_variance += weights[i] * weights[j] * volatilities[i] * volatilities[j] * correlation_matrix[i, j]
                return np.sqrt(portfolio_variance)
            
            def return_objective(weights):
                returns = np.array([asset.expected_return for asset in filtered_assets])
                portfolio_return = np.sum(weights * returns)
                return -portfolio_return  # Minimize negative return (maximize return)
            
            # Combined objective function
            def combined_objective(weights):
                esg_weight = 0.4  # ESG importance
                risk_weight = 0.3  # Risk importance
                return_weight = 0.3  # Return importance
                
                esg_score = -esg_objective(weights)
                risk_score = risk_objective(weights)
                return_score = -return_objective(weights)
                
                # Normalize scores to 0-1 range
                esg_normalized = esg_score / 100.0
                risk_normalized = 1.0 / (1.0 + risk_score)  # Lower risk is better
                return_normalized = return_score / 0.2  # Assuming max return around 20%
                
                return -(esg_weight * esg_normalized + risk_weight * risk_normalized + return_weight * return_normalized)
            
            # Constraints and bounds
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            bounds = tuple((0, 1) for _ in range(len(filtered_assets)))
            initial_weights = np.array([1.0/len(filtered_assets)] * len(filtered_assets))
            
            # Optimize using classical method (more reliable for ESG optimization)
            if self.scipy_minimize:
                result = self.scipy_minimize(
                    combined_objective,
                    initial_weights,
                    method='SLSQP',
                    bounds=bounds,
                    constraints=constraints
                )
                
                if result.success:
                    optimal_weights = result.x.tolist()
                    
                    # Calculate final metrics
                    returns = np.array([asset.expected_return for asset in filtered_assets])
                    volatilities = np.array([asset.volatility for asset in filtered_assets])
                    correlation_matrix = self._create_correlation_matrix(len(filtered_assets))
                    
                    portfolio_metrics = self._calculate_portfolio_metrics(
                        filtered_assets, optimal_weights, returns, volatilities, correlation_matrix
                    )
                    
                    # ESG-specific metrics
                    esg_breakdown = {
                        "overall_score": portfolio_metrics["portfolio_esg_score"],
                        "min_score": min([asset.esg_score for asset in filtered_assets]),
                        "max_score": max([asset.esg_score for asset in filtered_assets]),
                        "score_distribution": self._analyze_esg_distribution(filtered_assets, optimal_weights)
                    }
                    
                    return {
                        "optimization_method": "ESG-Focused Multi-Objective",
                        "target_esg_score": target_esg_score,
                        "optimal_weights": optimal_weights,
                        "portfolio_metrics": portfolio_metrics,
                        "esg_analysis": esg_breakdown,
                        "optimization_success": True,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"error": f"ESG optimization failed: {result.message}"}
            else:
                return {"error": "Optimization backend not available"}
                
        except Exception as e:
            logger.error(f"Error in ESG-focused optimization: {e}")
            return {"error": str(e)}
    
    def _analyze_esg_distribution(self, assets: List[PortfolioAsset], weights: List[float]) -> Dict[str, Any]:
        """Analyze ESG score distribution across portfolio"""
        try:
            esg_scores = [asset.esg_score for asset in assets]
            weighted_esg = [weights[i] * esg_scores[i] for i in range(len(assets))]
            
            return {
                "mean_esg": round(np.mean(esg_scores), 2),
                "weighted_mean_esg": round(np.sum(weighted_esg), 2),
                "esg_std": round(np.std(esg_scores), 2),
                "esg_range": round(max(esg_scores) - min(esg_scores), 2),
                "high_esg_assets": len([score for score in esg_scores if score >= 80]),
                "medium_esg_assets": len([score for score in esg_scores if 60 <= score < 80]),
                "low_esg_assets": len([score for score in esg_scores if score < 60])
            }
        except Exception as e:
            logger.error(f"Error analyzing ESG distribution: {e}")
            return {"error": str(e)}
    
    def generate_esg_report(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive ESG report for portfolio"""
        try:
            assets = portfolio_data.get("assets", [])
            if not assets:
                return {"error": "No portfolio data provided"}
            
            # Calculate ESG metrics
            esg_scores = [asset.esg_score for asset in assets]
            sector_esg = {}
            region_esg = {}
            
            for asset in assets:
                # Sector analysis
                if asset.sector not in sector_esg:
                    sector_esg[asset.sector] = []
                sector_esg[asset.sector].append(asset.esg_score)
                
                # Region analysis
                if asset.region not in region_esg:
                    region_esg[asset.region] = []
                region_esg[asset.region].append(asset.esg_score)
            
            # Calculate sector and region averages
            sector_averages = {sector: round(np.mean(scores), 2) for sector, scores in sector_esg.items()}
            region_averages = {region: round(np.mean(scores), 2) for region, scores in region_esg.items()}
            
            # ESG risk assessment
            esg_risk_level = "Low"
            if np.mean(esg_scores) < 50:
                esg_risk_level = "High"
            elif np.mean(esg_scores) < 70:
                esg_risk_level = "Medium"
            
            return {
                "overall_esg_score": round(np.mean(esg_scores), 2),
                "esg_risk_level": esg_risk_level,
                "sector_analysis": sector_averages,
                "region_analysis": region_averages,
                "esg_distribution": {
                    "excellent": len([score for score in esg_scores if score >= 90]),
                    "good": len([score for score in esg_scores if 80 <= score < 90]),
                    "fair": len([score for score in esg_scores if 70 <= score < 80]),
                    "poor": len([score for score in esg_scores if score < 70])
                },
                "recommendations": self._generate_esg_recommendations(esg_scores, sector_averages),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating ESG report: {e}")
            return {"error": str(e)}
    
    def _generate_esg_recommendations(self, esg_scores: List[float], sector_averages: Dict[str, float]) -> List[str]:
        """Generate ESG improvement recommendations"""
        recommendations = []
        
        try:
            avg_esg = np.mean(esg_scores)
            
            if avg_esg < 70:
                recommendations.append("Consider increasing allocation to high-ESG assets")
                recommendations.append("Review ESG policies and engagement strategies")
            
            if avg_esg < 80:
                recommendations.append("Implement ESG screening criteria for new investments")
                recommendations.append("Engage with companies to improve ESG practices")
            
            # Sector-specific recommendations
            for sector, avg_score in sector_averages.items():
                if avg_score < 70:
                    recommendations.append(f"Review {sector} sector ESG exposure")
                elif avg_score >= 85:
                    recommendations.append(f"Maintain {sector} sector ESG leadership")
            
            if not recommendations:
                recommendations.append("Portfolio ESG performance is strong - maintain current strategy")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating ESG recommendations: {e}")
            return ["Unable to generate recommendations"]

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
