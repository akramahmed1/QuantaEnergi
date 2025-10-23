"""
Quantum Optimization API Routers
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from ..base import get_db
from .services import QuantumOptimizationService, OptimizationMethod

router = APIRouter(prefix="/quantum", tags=["Quantum Optimization"])

@router.post("/optimize-portfolio")
async def optimize_portfolio(
    expected_returns: List[float] = Body(..., description="Expected returns for each asset"),
    risk_matrix: List[List[float]] = Body(..., description="Risk covariance matrix"),
    risk_free_rate: float = Query(0.02, description="Risk-free rate"),
    target_return: float = Query(None, description="Target return (if None, maximize Sharpe ratio)"),
    method: OptimizationMethod = Query(OptimizationMethod.QUANTUM_QAOA, description="Optimization method"),
    db: Session = Depends(get_db)
):
    """Optimize portfolio using quantum or classical methods"""
    quantum_service = QuantumOptimizationService()
    
    import numpy as np
    risk_matrix_array = np.array(risk_matrix)
    
    result = quantum_service.optimize_portfolio(
        expected_returns, risk_matrix_array, risk_free_rate, target_return, method
    )
    
    return {
        "success": result.success,
        "method": result.method,
        "weights": result.weights,
        "expected_return": result.expected_return,
        "risk": result.risk,
        "sharpe_ratio": result.sharpe_ratio,
        "optimization_time": result.optimization_time,
        "quantum_advantage": result.quantum_advantage,
        "error_message": result.error_message
    }

@router.post("/compare-methods")
async def compare_optimization_methods(
    expected_returns: List[float] = Body(..., description="Expected returns for each asset"),
    risk_matrix: List[List[float]] = Body(..., description="Risk covariance matrix"),
    risk_free_rate: float = Query(0.02, description="Risk-free rate"),
    db: Session = Depends(get_db)
):
    """Compare different optimization methods"""
    quantum_service = QuantumOptimizationService()
    
    import numpy as np
    risk_matrix_array = np.array(risk_matrix)
    
    comparison = quantum_service.compare_optimization_methods(
        expected_returns, risk_matrix_array, risk_free_rate
    )
    
    return {
        "success": True,
        "comparison": comparison,
        "recommendations": {
            "best_method": comparison["best_method"],
            "quantum_available": comparison["quantum_available"],
            "pulp_available": comparison["pulp_available"]
        }
    }

@router.get("/methods")
async def get_optimization_methods():
    """Get available optimization methods"""
    return {
        "methods": [
            {
                "method": "quantum_qaoa",
                "name": "Quantum QAOA",
                "description": "Quantum Approximate Optimization Algorithm using Qiskit",
                "advantage": "Potential quantum advantage for complex portfolios",
                "requirements": "Qiskit library and quantum hardware access"
            },
            {
                "method": "classical_pulp",
                "name": "Classical PuLP",
                "description": "Classical optimization using PuLP linear programming",
                "advantage": "Proven classical optimization with guaranteed optimality",
                "requirements": "PuLP library"
            },
            {
                "method": "numpy_fallback",
                "name": "NumPy Fallback",
                "description": "NumPy-based optimization using analytical solutions",
                "advantage": "No external dependencies, fast execution",
                "requirements": "NumPy library only"
            }
        ],
        "availability": {
            "quantum_available": True,  # Will be determined at runtime
            "pulp_available": True,     # Will be determined at runtime
            "numpy_available": True     # Always available
        }
    }

@router.get("/quantum-status")
async def get_quantum_status():
    """Get quantum computing status and capabilities"""
    quantum_service = QuantumOptimizationService()
    
    return {
        "quantum_available": quantum_service.qaoa_optimizer is not None,
        "classical_available": quantum_service.classical_optimizer is not None,
        "capabilities": {
            "qaoa_optimization": quantum_service.qaoa_optimizer is not None,
            "classical_fallback": True,
            "numpy_fallback": True
        },
        "recommendations": [
            "Use quantum QAOA for complex portfolios with quantum advantage",
            "Use classical PuLP for guaranteed optimal solutions",
            "Use NumPy fallback for simple portfolios or when dependencies unavailable"
        ]
    }
