import numpy as np
from scipy.stats import norm
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

def calculate_var(prices: List[float], confidence: float = 0.95, days: int = 252):
    """
    Calculate Value at Risk (VaR) using parametric method for US shale risk
    Enhanced for 95% confidence, 252-day horizon as specified
    """
    if len(prices) < 2:
        return {"param_var": 0.0, "method": "insufficient_data"}
    
    # Calculate log returns for better statistical properties
    returns = np.diff(np.log(prices))
    
    if len(returns) == 0:
        return {"param_var": 0.0, "method": "no_returns"}
    
    # Parametric VaR calculation
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    
    # Parametric VaR: mean - z_score * std * sqrt(days) (negative for losses)
    z_score = norm.ppf(1 - confidence)
    param_var = mean_return - z_score * std_return * np.sqrt(days)
    
    # Ensure VaR represents potential loss (negative value)
    if param_var > 0:
        param_var = -param_var
    
    return {
        "param_var": float(param_var),
        "confidence": confidence,
        "days": days,
        "method": "parametric",
        "mean_return": float(mean_return),
        "std_return": float(std_return)
    }

def monte_carlo_var(prices: List[float], simulations: int = 10000, days: int = 252, confidence: float = 0.95):
    """
    Calculate Value at Risk using Monte Carlo simulation for US shale disruption
    Simulates 10,000 price paths over 252 trading days
    """
    if len(prices) < 2:
        return {"mc_var": 0.0, "method": "insufficient_data"}
    
    # Calculate historical returns
    returns = np.diff(np.log(prices))
    
    if len(returns) == 0:
        return {"mc_var": 0.0, "method": "no_returns"}
    
    # Get current price and historical statistics
    current_price = prices[-1]
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    
    # Monte Carlo simulation
    np.random.seed(42)  # For reproducible results
    simulated_returns = np.random.normal(mean_return, std_return, (days, simulations))
    
    # Calculate price paths
    price_paths = np.zeros((days + 1, simulations))
    price_paths[0] = current_price
    
    for t in range(1, days + 1):
        price_paths[t] = price_paths[t-1] * np.exp(simulated_returns[t-1])
    
    # Calculate final returns for each simulation
    final_returns = (price_paths[-1] - current_price) / current_price
    
    # VaR is the percentile of losses (negative values represent losses)
    var_percentile = (1 - confidence) * 100
    mc_var = np.percentile(final_returns, var_percentile)
    
    # Ensure VaR represents potential loss (negative value)
    if mc_var > 0:
        mc_var = -mc_var
    
    return {
        "mc_var": float(mc_var),
        "simulations": simulations,
        "days": days,
        "confidence": confidence,
        "method": "monte_carlo",
        "mean_final_return": float(np.mean(final_returns)),
        "std_final_return": float(np.std(final_returns))
    }

def calculate_enhanced_var(prices: List[float], confidence: float = 0.95, days: int = 252, 
                          simulations: int = 10000, method: str = "both") -> Dict:
    """
    Enhanced VaR calculation with both parametric and Monte Carlo methods
    Optimized for US shale risk assessment with 95% confidence
    """
    if len(prices) < 2:
        return {"error": "Insufficient price data for VaR calculation"}
    
    results = {
        "input_data": {
            "price_count": len(prices),
            "confidence": confidence,
            "days": days,
            "simulations": simulations
        }
    }
    
    # Calculate parametric VaR
    if method in ["parametric", "both"]:
        param_result = calculate_var(prices, confidence, days)
        results["parametric"] = param_result
    
    # Calculate Monte Carlo VaR
    if method in ["monte_carlo", "both"]:
        mc_result = monte_carlo_var(prices, simulations, days, confidence)
        results["monte_carlo"] = mc_result
    
    # Risk assessment for US shale
    if method == "both" and "parametric" in results and "monte_carlo" in results:
        param_var = results["parametric"]["param_var"]
        mc_var = results["monte_carlo"]["mc_var"]
        
        # Risk level assessment
        max_var = max(abs(param_var), abs(mc_var))
        if max_var > 0.3:  # 30% potential loss
            risk_level = "CRITICAL"
        elif max_var > 0.15:  # 15% potential loss
            risk_level = "HIGH"
        elif max_var > 0.05:  # 5% potential loss
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        results["risk_assessment"] = {
            "level": risk_level,
            "max_var": float(max_var),
            "recommendation": f"US Shale {risk_level} risk detected - consider hedging strategies"
        }
    
    return results
