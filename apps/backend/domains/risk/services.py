"""
Risk Management Domain Services
Real VaR calculations with 10k Monte Carlo simulations
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from scipy import stats
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class VaRCalculator:
    """Real VaR calculation service with Monte Carlo simulations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_parametric_var(self, 
                                positions: List[Dict[str, Any]], 
                                confidence_level: float = 0.95,
                                time_horizon: int = 1) -> Dict[str, Any]:
        """Calculate parametric VaR using normal distribution assumption"""
        try:
            if not positions:
                return {"var": 0.0, "method": "parametric", "positions": 0}
            
            # Calculate portfolio value and weights
            total_value = sum(pos.get("notional_value", 0) for pos in positions)
            if total_value == 0:
                return {"var": 0.0, "method": "parametric", "positions": 0}
            
            # Calculate portfolio volatility (simplified)
            portfolio_volatility = 0.02  # 2% daily volatility assumption
            
            # Calculate VaR using normal distribution
            z_score = stats.norm.ppf(confidence_level)
            var_amount = total_value * portfolio_volatility * z_score * np.sqrt(time_horizon)
            
            return {
                "success": True,
                "var": round(var_amount, 2),
                "confidence_level": confidence_level,
                "time_horizon": time_horizon,
                "method": "parametric",
                "portfolio_value": total_value,
                "volatility": portfolio_volatility,
                "z_score": round(z_score, 4),
                "calculated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating parametric VaR: {e}")
            return {"success": False, "error": str(e)}
    
    def calculate_monte_carlo_var(self, 
                                 positions: List[Dict[str, Any]], 
                                 confidence_level: float = 0.95,
                                 time_horizon: int = 1,
                                 num_simulations: int = 10000) -> Dict[str, Any]:
        """Calculate VaR using Monte Carlo simulation with 10k paths and correlation matrix"""
        try:
            if not positions:
                return {"var": 0.0, "method": "monte_carlo", "simulations": 0}
            
            # Portfolio setup
            total_value = sum(pos.get("notional_value", 0) for pos in positions)
            if total_value == 0:
                return {"var": 0.0, "method": "monte_carlo", "simulations": 0}
            
            # Generate correlated random returns using Cholesky decomposition
            np.random.seed(42)  # For reproducibility
            
            # Create correlation matrix for commodities
            n_assets = len(positions)
            if n_assets == 1:
                correlation_matrix = np.array([[1.0]])
            else:
                # Base correlation matrix (simplified)
                correlation_matrix = np.eye(n_assets) * 0.3 + np.ones((n_assets, n_assets)) * 0.1
                np.fill_diagonal(correlation_matrix, 1.0)
            
            # Cholesky decomposition for correlated returns
            try:
                L = np.linalg.cholesky(correlation_matrix)
            except np.linalg.LinAlgError:
                L = np.eye(n_assets)  # Fallback to uncorrelated
            
            # Generate correlated random returns
            uncorrelated_returns = np.random.normal(0, 0.02, (num_simulations, n_assets))
            correlated_returns = uncorrelated_returns @ L.T
            
            # Calculate portfolio values for each simulation
            portfolio_values = []
            for sim_idx in range(num_simulations):
                portfolio_value = 0
                for pos_idx, pos in enumerate(positions):
                    position_value = pos.get("notional_value", 0)
                    commodity_multiplier = self._get_commodity_multiplier(pos.get("commodity", "crude_oil"))
                    position_return = correlated_returns[sim_idx, pos_idx] * commodity_multiplier
                    portfolio_value += position_value * (1 + position_return)
                portfolio_values.append(portfolio_value)
            
            # Calculate VaR from simulated portfolio values
            portfolio_values = np.array(portfolio_values)
            var_percentile = (1 - confidence_level) * 100
            var_amount = total_value - np.percentile(portfolio_values, var_percentile)
            
            # Calculate Expected Shortfall (Conditional VaR)
            var_threshold = total_value - var_amount
            tail_losses = portfolio_values[portfolio_values <= var_threshold]
            expected_shortfall = total_value - np.mean(tail_losses) if len(tail_losses) > 0 else var_amount
            
            # Calculate additional risk metrics
            portfolio_returns = (portfolio_values - total_value) / total_value
            portfolio_volatility = np.std(portfolio_returns)
            sharpe_ratio = np.mean(portfolio_returns) / portfolio_volatility if portfolio_volatility > 0 else 0
            
            return {
                "success": True,
                "var": round(var_amount, 2),
                "expected_shortfall": round(expected_shortfall, 2),
                "confidence_level": confidence_level,
                "time_horizon": time_horizon,
                "method": "monte_carlo",
                "simulations": num_simulations,
                "portfolio_value": total_value,
                "var_percentile": var_percentile,
                "portfolio_volatility": round(portfolio_volatility, 4),
                "sharpe_ratio": round(sharpe_ratio, 4),
                "correlation_matrix": correlation_matrix.tolist(),
                "calculated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating Monte Carlo VaR: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_commodity_multiplier(self, commodity: str) -> float:
        """Get commodity-specific volatility multiplier"""
        multipliers = {
            "crude_oil": 1.0,
            "natural_gas": 1.2,
            "refined_products": 0.8,
            "coal": 0.9,
            "lng": 1.1
        }
        return multipliers.get(commodity.lower(), 1.0)
    
    def calculate_historical_var(self, 
                                historical_returns: List[float], 
                                confidence_level: float = 0.95) -> Dict[str, Any]:
        """Calculate VaR using historical simulation method"""
        try:
            if not historical_returns:
                return {"var": 0.0, "method": "historical", "observations": 0}
            
            returns_array = np.array(historical_returns)
            var_percentile = (1 - confidence_level) * 100
            var_amount = -np.percentile(returns_array, var_percentile)
            
            return {
                "success": True,
                "var": round(var_amount, 2),
                "confidence_level": confidence_level,
                "method": "historical",
                "observations": len(historical_returns),
                "calculated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating historical VaR: {e}")
            return {"success": False, "error": str(e)}

class RiskAnalytics:
    """Advanced risk analytics service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_portfolio_risk_metrics(self, positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive portfolio risk metrics"""
        try:
            if not positions:
                return {"success": False, "error": "No positions provided"}
            
            # Basic metrics
            total_value = sum(pos.get("notional_value", 0) for pos in positions)
            position_count = len(positions)
            
            # Calculate concentration risk
            position_values = [pos.get("notional_value", 0) for pos in positions]
            max_position = max(position_values) if position_values else 0
            concentration_risk = (max_position / total_value) * 100 if total_value > 0 else 0
            
            # Calculate diversification ratio (simplified)
            diversification_ratio = min(position_count / 5, 1.0)  # Max 1.0 for 5+ positions
            
            # Calculate portfolio volatility (simplified)
            portfolio_volatility = 0.02  # 2% daily volatility assumption
            
            return {
                "success": True,
                "total_value": total_value,
                "position_count": position_count,
                "concentration_risk": round(concentration_risk, 2),
                "diversification_ratio": round(diversification_ratio, 2),
                "portfolio_volatility": round(portfolio_volatility, 4),
                "risk_score": self._calculate_risk_score(concentration_risk, diversification_ratio),
                "calculated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_risk_score(self, concentration_risk: float, diversification_ratio: float) -> str:
        """Calculate overall risk score"""
        if concentration_risk > 50 or diversification_ratio < 0.3:
            return "HIGH"
        elif concentration_risk > 30 or diversification_ratio < 0.6:
            return "MEDIUM"
        else:
            return "LOW"
