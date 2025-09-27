import numpy as np
from typing import List

def calculate_var(prices: List[float], confidence: float = 0.95):
    """Calculate Value at Risk (VaR) using historical simulation"""
    returns = np.diff(prices) / prices[:-1]
    return np.percentile(returns, (1-confidence)*100) * -1
