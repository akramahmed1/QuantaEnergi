"""
Risk Calculation Tasks
CPU-intensive risk analytics tasks using Celery
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing as mp

from celery import current_task
from celery.exceptions import Retry
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
import structlog

from app.core.celery_app import celery_app
from app.services.risk_analytics_service import RiskAnalyticsService

logger = structlog.get_logger(__name__)

# Configure multiprocessing
mp.set_start_method('spawn', force=True)


@celery_app.task(bind=True, name="app.tasks.risk_calculations.calculate_var_monte_carlo")
def calculate_var_monte_carlo(self, portfolio_data: Dict[str, Any], 
                            confidence_level: float = 0.95,
                            num_simulations: int = 10000,
                            time_horizon: int = 1,
                            tenant_id: str = "system") -> Dict[str, Any]:
    """
    Calculate Value at Risk using Monte Carlo simulation - SECURE VERSION
    
    Args:
        portfolio_data: Portfolio positions and market data
        confidence_level: Confidence level for VaR calculation
        num_simulations: Number of Monte Carlo simulations
        time_horizon: Time horizon in days
        tenant_id: Tenant identifier
        
    Returns:
        VaR calculation results
    """
    try:
        # SECURITY: Validate inputs to prevent RCE/DoS attacks
        if not isinstance(portfolio_data, dict):
            raise ValueError("Portfolio data must be a dictionary")
        
        if confidence_level < 0.01 or confidence_level > 0.99:
            raise ValueError("Confidence level must be between 0.01 and 0.99")
        
        if num_simulations < 100 or num_simulations > 100000:
            raise ValueError("Number of simulations must be between 100 and 100,000")
        
        if time_horizon < 1 or time_horizon > 365:
            raise ValueError("Time horizon must be between 1 and 365 days")
        
        if not isinstance(tenant_id, str) or len(tenant_id) > 100:
            raise ValueError("Invalid tenant ID")
        
        # SECURITY: Validate portfolio data structure
        required_keys = ['positions', 'market_data']
        for key in required_keys:
            if key not in portfolio_data:
                raise ValueError(f"Missing required key: {key}")
        
        positions = portfolio_data.get("positions", [])
        if not isinstance(positions, list) or len(positions) > 1000:
            raise ValueError("Invalid positions data - potential DoS risk")
        logger.info("Starting Monte Carlo VaR calculation", 
                   tenant_id=tenant_id, 
                   num_simulations=num_simulations,
                   task_id=self.request.id)
        
        start_time = time.time()
        
        # Extract portfolio data
        positions = portfolio_data.get("positions", [])
        market_data = portfolio_data.get("market_data", {})
        
        if not positions or not market_data:
            raise ValueError("Invalid portfolio data")
        
        # SECURITY: Limit multiprocessing to prevent resource exhaustion
        max_workers = min(mp.cpu_count(), 8)  # Cap at 8 workers
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # SECURITY: Split simulations across processes with safe chunking
            chunk_size = max(1, num_simulations // max_workers)
            futures = []
            
            for i in range(max_workers):
                chunk_start = i * chunk_size
                chunk_end = chunk_start + chunk_size if i < max_workers - 1 else num_simulations
                
                future = executor.submit(
                    _monte_carlo_chunk,
                    positions,
                    market_data,
                    confidence_level,
                    chunk_end - chunk_start,
                    time_horizon
                )
                futures.append(future)
            
            # Collect results
            chunk_results = []
            for future in futures:
                chunk_results.extend(future.result())
        
        # Calculate VaR from all simulations
        var_value = np.percentile(chunk_results, (1 - confidence_level) * 100)
        
        # Calculate additional risk metrics
        expected_shortfall = np.mean([x for x in chunk_results if x <= var_value])
        max_loss = np.min(chunk_results)
        
        duration = time.time() - start_time
        
        result = {
            "var_value": float(var_value),
            "expected_shortfall": float(expected_shortfall),
            "max_loss": float(max_loss),
            "confidence_level": confidence_level,
            "time_horizon": time_horizon,
            "num_simulations": num_simulations,
            "calculation_time": duration,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant_id": tenant_id
        }
        
        logger.info("Monte Carlo VaR calculation completed", 
                   tenant_id=tenant_id,
                   var_value=var_value,
                   duration=duration,
                   task_id=self.request.id)
        
        return result
        
    except Exception as exc:
        logger.error("Monte Carlo VaR calculation failed", 
                    tenant_id=tenant_id,
                    error=str(exc),
                    task_id=self.request.id)
        
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60, max_retries=3)


def _monte_carlo_chunk(positions: List[Dict], market_data: Dict, 
                      confidence_level: float, num_simulations: int, 
                      time_horizon: int) -> List[float]:
    """
    Calculate Monte Carlo simulations for a chunk of data
    
    Args:
        positions: Portfolio positions
        market_data: Market data
        confidence_level: Confidence level
        num_simulations: Number of simulations for this chunk
        time_horizon: Time horizon in days
        
    Returns:
        List of portfolio value changes
    """
    results = []
    
    for _ in range(num_simulations):
        # Simulate market movements
        portfolio_change = 0.0
        
        for position in positions:
            commodity = position["commodity"]
            quantity = position["quantity"]
            current_price = position["current_price"]
            
            # Get historical volatility
            volatility = market_data.get(commodity, {}).get("volatility", 0.02)
            
            # Simulate price change using log-normal distribution
            drift = 0.0  # Assume no drift for simplicity
            shock = np.random.normal(drift, volatility * np.sqrt(time_horizon))
            new_price = current_price * np.exp(shock)
            
            # Calculate position change
            position_change = quantity * (new_price - current_price)
            portfolio_change += position_change
        
        results.append(portfolio_change)
    
    return results


@celery_app.task(bind=True, name="app.tasks.risk_calculations.calculate_portfolio_var")
def calculate_portfolio_var(self, portfolio_id: str, tenant_id: str = "system") -> Dict[str, Any]:
    """
    Calculate VaR for a specific portfolio
    
    Args:
        portfolio_id: Portfolio identifier
        tenant_id: Tenant identifier
        
    Returns:
        Portfolio VaR results
    """
    try:
        logger.info("Starting portfolio VaR calculation", 
                   portfolio_id=portfolio_id,
                   tenant_id=tenant_id,
                   task_id=self.request.id)
        
        # Get portfolio data (this would be implemented with actual data service)
        portfolio_data = _get_portfolio_data(portfolio_id, tenant_id)
        
        # Calculate VaR at different confidence levels
        confidence_levels = [0.90, 0.95, 0.99]
        var_results = {}
        
        for conf_level in confidence_levels:
            result = calculate_var_monte_carlo.delay(
                portfolio_data,
                confidence_level=conf_level,
                tenant_id=tenant_id
            )
            var_results[f"var_{int(conf_level*100)}"] = result.get()
        
        # Calculate additional risk metrics
        risk_metrics = _calculate_additional_risk_metrics(portfolio_data)
        
        final_result = {
            "portfolio_id": portfolio_id,
            "tenant_id": tenant_id,
            "var_results": var_results,
            "risk_metrics": risk_metrics,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info("Portfolio VaR calculation completed", 
                   portfolio_id=portfolio_id,
                   tenant_id=tenant_id,
                   task_id=self.request.id)
        
        return final_result
        
    except Exception as exc:
        logger.error("Portfolio VaR calculation failed", 
                    portfolio_id=portfolio_id,
                    tenant_id=tenant_id,
                    error=str(exc),
                    task_id=self.request.id)
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@celery_app.task(bind=True, name="app.tasks.risk_calculations.calculate_stress_test")
def calculate_stress_test(self, portfolio_id: str, scenario_data: Dict[str, Any], 
                         tenant_id: str = "system") -> Dict[str, Any]:
    """
    Calculate stress test results for a portfolio
    
    Args:
        portfolio_id: Portfolio identifier
        scenario_data: Stress test scenario data
        tenant_id: Tenant identifier
        
    Returns:
        Stress test results
    """
    try:
        logger.info("Starting stress test calculation", 
                   portfolio_id=portfolio_id,
                   tenant_id=tenant_id,
                   task_id=self.request.id)
        
        start_time = time.time()
        
        # Get portfolio data
        portfolio_data = _get_portfolio_data(portfolio_id, tenant_id)
        positions = portfolio_data.get("positions", [])
        
        # Apply stress scenario
        scenario_name = scenario_data.get("scenario_name", "custom")
        market_shocks = scenario_data.get("market_shocks", {})
        
        portfolio_loss = 0.0
        position_losses = []
        
        for position in positions:
            commodity = position["commodity"]
            quantity = position["quantity"]
            current_price = position["current_price"]
            
            # Apply market shock
            shock = market_shocks.get(commodity, 0.0)
            stressed_price = current_price * (1 + shock)
            
            # Calculate position loss
            position_loss = quantity * (current_price - stressed_price)
            portfolio_loss += position_loss
            
            position_losses.append({
                "commodity": commodity,
                "position_loss": position_loss,
                "shock": shock,
                "stressed_price": stressed_price
            })
        
        duration = time.time() - start_time
        
        result = {
            "portfolio_id": portfolio_id,
            "scenario_name": scenario_name,
            "portfolio_loss": portfolio_loss,
            "position_losses": position_losses,
            "market_shocks": market_shocks,
            "calculation_time": duration,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant_id": tenant_id
        }
        
        logger.info("Stress test calculation completed", 
                   portfolio_id=portfolio_id,
                   tenant_id=tenant_id,
                   portfolio_loss=portfolio_loss,
                   duration=duration,
                   task_id=self.request.id)
        
        return result
        
    except Exception as exc:
        logger.error("Stress test calculation failed", 
                    portfolio_id=portfolio_id,
                    tenant_id=tenant_id,
                    error=str(exc),
                    task_id=self.request.id)
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@celery_app.task(bind=True, name="app.tasks.risk_calculations.calculate_daily_var")
def calculate_daily_var(self, tenant_id: str = "system") -> Dict[str, Any]:
    """
    Calculate daily VaR for all portfolios (scheduled task)
    
    Args:
        tenant_id: Tenant identifier
        
    Returns:
        Daily VaR results
    """
    try:
        logger.info("Starting daily VaR calculation", 
                   tenant_id=tenant_id,
                   task_id=self.request.id)
        
        # Get all portfolios for tenant
        portfolio_ids = _get_tenant_portfolio_ids(tenant_id)
        
        # Calculate VaR for each portfolio in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for portfolio_id in portfolio_ids:
                future = executor.submit(
                    calculate_portfolio_var.delay,
                    portfolio_id,
                    tenant_id
                )
                futures.append((portfolio_id, future))
            
            # Collect results
            results = {}
            for portfolio_id, future in futures:
                try:
                    result = future.result(timeout=300)  # 5 minute timeout
                    results[portfolio_id] = result
                except Exception as e:
                    logger.error("Portfolio VaR calculation failed", 
                               portfolio_id=portfolio_id,
                               error=str(e))
                    results[portfolio_id] = {"error": str(e)}
        
        # Generate summary
        summary = {
            "total_portfolios": len(portfolio_ids),
            "successful_calculations": len([r for r in results.values() if "error" not in r]),
            "failed_calculations": len([r for r in results.values() if "error" in r]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant_id": tenant_id
        }
        
        final_result = {
            "summary": summary,
            "portfolio_results": results
        }
        
        logger.info("Daily VaR calculation completed", 
                   tenant_id=tenant_id,
                   summary=summary,
                   task_id=self.request.id)
        
        return final_result
        
    except Exception as exc:
        logger.error("Daily VaR calculation failed", 
                    tenant_id=tenant_id,
                    error=str(exc),
                    task_id=self.request.id)
        raise self.retry(exc=exc, countdown=300, max_retries=2)


def _get_portfolio_data(portfolio_id: str, tenant_id: str) -> Dict[str, Any]:
    """
    Get portfolio data (mock implementation)
    
    Args:
        portfolio_id: Portfolio identifier
        tenant_id: Tenant identifier
        
    Returns:
        Portfolio data
    """
    # This would be implemented with actual data service
    return {
        "portfolio_id": portfolio_id,
        "positions": [
            {
                "commodity": "crude_oil",
                "quantity": 1000,
                "current_price": 85.50
            },
            {
                "commodity": "natural_gas",
                "quantity": 5000,
                "current_price": 3.45
            }
        ],
        "market_data": {
            "crude_oil": {"volatility": 0.02},
            "natural_gas": {"volatility": 0.03}
        }
    }


def _get_tenant_portfolio_ids(tenant_id: str) -> List[str]:
    """
    Get portfolio IDs for a tenant (mock implementation)
    
    Args:
        tenant_id: Tenant identifier
        
    Returns:
        List of portfolio IDs
    """
    # This would be implemented with actual data service
    return [f"portfolio_{i}" for i in range(1, 11)]


def _calculate_additional_risk_metrics(portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate additional risk metrics
    
    Args:
        portfolio_data: Portfolio data
        
    Returns:
        Additional risk metrics
    """
    positions = portfolio_data.get("positions", [])
    
    # Calculate portfolio concentration
    total_value = sum(pos["quantity"] * pos["current_price"] for pos in positions)
    concentration = {}
    
    for position in positions:
        position_value = position["quantity"] * position["current_price"]
        concentration[position["commodity"]] = position_value / total_value
    
    # Calculate portfolio volatility (simplified)
    portfolio_volatility = 0.02  # Mock value
    
    return {
        "portfolio_volatility": portfolio_volatility,
        "concentration": concentration,
        "total_value": total_value
    }
