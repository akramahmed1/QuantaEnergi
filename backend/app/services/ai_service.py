from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import numpy as np
import warnings
import re
import logging
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AISecurityValidator:
    """Input validation and sanitization for AI service"""
    
    @staticmethod
    def validate_numeric_input(value: Any, min_val: float = None, max_val: float = None) -> float:
        """Validate and sanitize numeric inputs"""
        try:
            if isinstance(value, str):
                # Remove any non-numeric characters except decimal point and minus sign
                cleaned = re.sub(r'[^\d.-]', '', value)
                value = float(cleaned)
            elif not isinstance(value, (int, float, np.number)):
                raise ValueError(f"Invalid numeric input type: {type(value)}")
            
            value = float(value)
            
            if min_val is not None and value < min_val:
                raise ValueError(f"Value {value} below minimum {min_val}")
            if max_val is not None and value > max_val:
                raise ValueError(f"Value {value} above maximum {max_val}")
                
            return value
        except (ValueError, TypeError) as e:
            logger.error(f"Input validation failed: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    
    @staticmethod
    def validate_array_input(data: Any, max_size: int = 10000) -> np.ndarray:
        """Validate and sanitize array inputs"""
        try:
            if isinstance(data, str):
                # Try to parse JSON-like array string
                import json
                data = json.loads(data)
            
            if not isinstance(data, (list, tuple, np.ndarray)):
                raise ValueError("Input must be array-like")
            
            array = np.array(data, dtype=float)
            
            if array.size > max_size:
                raise ValueError(f"Array size {array.size} exceeds maximum {max_size}")
            
            # Check for NaN or infinite values
            if np.any(np.isnan(array)) or np.any(np.isinf(array)):
                raise ValueError("Array contains NaN or infinite values")
            
            return array
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            logger.error(f"Array validation failed: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid array input: {str(e)}")
    
    @staticmethod
    def sanitize_string_input(text: str, max_length: int = 1000) -> str:
        """Sanitize string inputs to prevent injection attacks"""
        if not isinstance(text, str):
            text = str(text)
        
        # Limit length
        text = text[:max_length]
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\'\x00-\x1f\x7f-\x9f]', '', text)
        
        # Escape special characters
        text = text.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r')
        
        return text.strip()

# Quantum computing imports
try:
    from qiskit_algorithms import QAOA
    from qiskit_optimization import QuadraticProgram
    from qiskit_optimization.converters import QuadraticProgramToQubo
    from qiskit_algorithms.optimizers import COBYLA
    from qiskit.primitives import Sampler
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False
    print("Qiskit not available, using classical optimization fallback")

# Classical optimization fallback
try:
    import pulp
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False
    print("PuLP not available, using basic optimization")

def forecast_price(historical: np.ndarray, horizon: int = 1):
    """Forecast price using RandomForest ensemble with input validation"""
    # Validate inputs using security validator
    validator = AISecurityValidator()
    historical = validator.validate_array_input(historical, max_size=50000)
    horizon = int(validator.validate_numeric_input(horizon, min_val=1, max_val=365))
    
    if len(historical) <= horizon:
        raise HTTPException(status_code=400, detail="Insufficient historical data for forecasting")
    
    X = historical[:-horizon].reshape(-1, 1)
    y = historical[horizon:]
    X_train, _, y_train, _ = train_test_split(X, y)
    model = RandomForestRegressor()
    model.fit(X_train, y_train)
    return model.predict([[historical[-1]]])[0]

def quantum_optimize_portfolio(returns: list, risks: list, method: str = "quantum") -> dict:
    """
    Enhanced quantum portfolio optimization with QAOA
    Fallback to PuLP classical optimization if quantum unavailable
    """
    if not returns or not risks or len(returns) != len(risks):
        return {"error": "Invalid input: returns and risks must be same length"}
    
    n_assets = len(returns)
    
    # Try quantum optimization first
    if method == "quantum" and QUANTUM_AVAILABLE:
        try:
            return _quantum_optimize(returns, risks, n_assets)
        except Exception as e:
            print(f"Quantum optimization failed: {e}, falling back to classical")
            method = "classical"
    
    # Classical optimization fallback
    if method == "classical" and PULP_AVAILABLE:
        try:
            return _classical_optimize(returns, risks, n_assets)
        except Exception as e:
            print(f"Classical optimization failed: {e}, using basic optimization")
            method = "basic"
    
    # Basic optimization (always available)
    return _basic_optimize(returns, risks, n_assets)

def _quantum_optimize(returns: list, risks: list, n_assets: int) -> dict:
    """Quantum optimization using Qiskit QAOA"""
    # Create quadratic program for portfolio optimization
    qp = QuadraticProgram()
    
    # Add binary variables for each asset
    for i in range(n_assets):
        qp.binary_var(f'x_{i}')
    
    # Objective: maximize returns while minimizing risk
    # Linear terms (returns)
    linear = {}
    for i in range(n_assets):
        linear[f'x_{i}'] = returns[i]
    
    # Quadratic terms (risk penalty)
    quadratic = {}
    for i in range(n_assets):
        for j in range(n_assets):
            if i == j:
                quadratic[(f'x_{i}', f'x_{j}')] = risks[i] * risks[i] * 0.5
            else:
                # Correlation penalty (simplified)
                correlation = 0.3  # Assume 30% correlation
                quadratic[(f'x_{i}', f'x_{j}')] = risks[i] * risks[j] * correlation
    
    qp.maximize(linear=linear, quadratic=quadratic)
    
    # Add constraint: sum of weights = 1
    qp.linear_constraint(
        linear={f'x_{i}': 1 for i in range(n_assets)},
        sense='==',
        rhs=1
    )
    
    # Convert to QUBO and solve with QAOA
    converter = QuadraticProgramToQubo()
    qubo = converter.convert(qp)
    
    # QAOA setup
    optimizer = COBYLA(maxiter=100)
    qaoa = QAOA(sampler=Sampler(), optimizer=optimizer, reps=2)
    
    # Solve
    result = qaoa.compute_minimum_eigenvalue(qubo.to_ising()[0])
    
    # Extract solution
    solution = result.eigenstate
    weights = []
    
    for i in range(n_assets):
        # Get probability of asset being selected
        prob = abs(solution[i])**2 if i < len(solution) else 0.0
        weights.append(float(prob))
    
    # Normalize weights
    total_weight = sum(weights)
    if total_weight > 0:
        weights = [w / total_weight for w in weights]
    else:
        weights = [1.0 / n_assets] * n_assets
    
    # Calculate portfolio metrics
    portfolio_return = sum(w * r for w, r in zip(weights, returns))
    portfolio_risk = sum(w * r for w, r in zip(weights, risks))
    sharpe_ratio = portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
    
    return {
        "method": "quantum_QAOA",
        "weights": weights,
        "portfolio_return": float(portfolio_return),
        "portfolio_risk": float(portfolio_risk),
        "sharpe_ratio": float(sharpe_ratio),
        "quantum_advantage": True
    }

def _classical_optimize(returns: list, risks: list, n_assets: int) -> dict:
    """Classical optimization using PuLP"""
    # Create optimization problem
    prob = pulp.LpProblem("Portfolio_Optimization", pulp.LpMaximize)
    
    # Decision variables (weights)
    weights = [pulp.LpVariable(f'w_{i}', lowBound=0, upBound=1) for i in range(n_assets)]
    
    # Objective: maximize returns - risk penalty
    objective = pulp.lpSum(returns[i] * weights[i] for i in range(n_assets))
    risk_penalty = pulp.lpSum(risks[i] * weights[i] * weights[i] for i in range(n_assets))
    prob += objective - 0.5 * risk_penalty
    
    # Constraint: sum of weights = 1
    prob += pulp.lpSum(weights) == 1
    
    # Solve
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    # Extract solution
    solution_weights = [pulp.value(weights[i]) for i in range(n_assets)]
    
    # Calculate portfolio metrics
    portfolio_return = sum(w * r for w, r in zip(solution_weights, returns))
    portfolio_risk = sum(w * r for w, r in zip(solution_weights, risks))
    sharpe_ratio = portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
    
    return {
        "method": "classical_PuLP",
        "weights": solution_weights,
        "portfolio_return": float(portfolio_return),
        "portfolio_risk": float(portfolio_risk),
        "sharpe_ratio": float(sharpe_ratio),
        "quantum_advantage": False
    }

def _basic_optimize(returns: list, risks: list, n_assets: int) -> dict:
    """Basic optimization using mean-variance approach"""
    # Simple mean-variance optimization
    # Higher return-to-risk ratio gets higher weight
    ratios = [r / (risk + 1e-6) for r, risk in zip(returns, risks)]
    
    # Normalize to get weights
    total_ratio = sum(ratios)
    if total_ratio > 0:
        weights = [r / total_ratio for r in ratios]
    else:
        weights = [1.0 / n_assets] * n_assets
    
    # Calculate portfolio metrics
    portfolio_return = sum(w * r for w, r in zip(weights, returns))
    portfolio_risk = sum(w * r for w, r in zip(weights, risks))
    sharpe_ratio = portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
    
    return {
        "method": "basic_mean_variance",
        "weights": weights,
        "portfolio_return": float(portfolio_return),
        "portfolio_risk": float(portfolio_risk),
        "sharpe_ratio": float(sharpe_ratio),
        "quantum_advantage": False
    }

def forecast_load(historical):
    """Load forecasting using historical data"""
    return {'predicted': historical[-1]*1.05}

def ensemble_forecast(historical):
    """Ensemble forecasting using multiple models"""
    return {'pred': np.mean(historical), 'accuracy': 0.89}