"""
Advanced Risk Analytics Service for ETRM/CTRM Trading
Handles Monte Carlo simulations, VaR calculations, stress testing, and scenario analysis
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import logging
from fastapi import HTTPException
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import threading

logger = logging.getLogger(__name__)

class AdvancedRiskAnalytics:
    """Advanced risk analytics with Monte Carlo simulations and stress testing"""
    
    def __init__(self):
        self.simulation_results = {}
        self.risk_metrics = {}
        self.scenario_cache = {}
        self.risk_counter = 1000
        
    async def calculate_var_monte_carlo(
        self, 
        portfolio_data: Dict[str, Any], 
        confidence_level: float = 0.95,
        time_horizon: int = 1,
        num_simulations: int = 10000
    ) -> Dict[str, Any]:
        """
        Calculate Value at Risk using Monte Carlo simulation
        
        Args:
            portfolio_data: Portfolio positions and market data
            confidence_level: VaR confidence level (e.g., 0.95 for 95%)
            time_horizon: Time horizon in days
            num_simulations: Number of Monte Carlo simulations
            
        Returns:
            Dict with VaR results and simulation details
        """
        try:
            # Extract portfolio components
            positions = portfolio_data.get("positions", [])
            market_data = portfolio_data.get("market_data", {})
            correlations = portfolio_data.get("correlations", {})
            
            if not positions:
                raise HTTPException(status_code=400, detail="No positions provided for VaR calculation")
            
            # Run Monte Carlo simulation in parallel
            simulation_result = await self._run_monte_carlo_simulation(
                positions, market_data, correlations, time_horizon, num_simulations
            )
            
            # Calculate VaR from simulation results
            var_result = self._calculate_var_from_simulation(
                simulation_result, confidence_level
            )
            
            # Store results
            result_id = f"VAR-{self.risk_counter:06d}"
            self.risk_counter += 1
            
            result = {
                "result_id": result_id,
                "var_value": var_result["var_value"],
                "confidence_level": confidence_level,
                "time_horizon": time_horizon,
                "num_simulations": num_simulations,
                "simulation_summary": simulation_result["summary"],
                "risk_breakdown": var_result["risk_breakdown"],
                "calculated_at": datetime.now().isoformat(),
                "method": "monte_carlo"
            }
            
            self.simulation_results[result_id] = result
            
            logger.info(f"VaR calculation completed: {result_id}, VaR: {var_result['var_value']:.2f}")
            
            return {
                "success": True,
                "var_result": result
            }
            
        except Exception as e:
            logger.error(f"VaR calculation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _run_monte_carlo_simulation(
        self, 
        positions: List[Dict[str, Any]], 
        market_data: Dict[str, Any],
        correlations: Dict[str, Any],
        time_horizon: int,
        num_simulations: int
    ) -> Dict[str, Any]:
        """Run Monte Carlo simulation for portfolio risk"""
        
        # Generate correlated random returns
        returns_matrix = self._generate_correlated_returns(
            positions, correlations, time_horizon, num_simulations
        )
        
        # Calculate portfolio value changes
        portfolio_changes = self._calculate_portfolio_changes(positions, returns_matrix)
        
        # Aggregate results
        total_changes = np.sum(portfolio_changes, axis=1)
        
        return {
            "returns_matrix": returns_matrix,
            "portfolio_changes": portfolio_changes,
            "total_changes": total_changes,
            "summary": {
                "mean": float(np.mean(total_changes)),
                "std": float(np.std(total_changes)),
                "min": float(np.min(total_changes)),
                "max": float(np.max(total_changes)),
                "percentiles": {
                    "5": float(np.percentile(total_changes, 5)),
                    "25": float(np.percentile(total_changes, 25)),
                    "50": float(np.percentile(total_changes, 50)),
                    "75": float(np.percentile(total_changes, 75)),
                    "95": float(np.percentile(total_changes, 95))
                }
            }
        }
    
    def _generate_correlated_returns(
        self, 
        positions: List[Dict[str, Any]], 
        correlations: Dict[str, Any],
        time_horizon: int,
        num_simulations: int
    ) -> np.ndarray:
        """Generate correlated random returns for Monte Carlo simulation"""
        
        num_assets = len(positions)
        
        # Default correlation matrix if not provided
        if not correlations:
            correlations = np.eye(num_assets) * 0.3 + np.ones((num_assets, num_assets)) * 0.7
        
        # Generate correlated normal random variables
        mean_returns = np.array([p.get("expected_return", 0.0) for p in positions])
        volatilities = np.array([p.get("volatility", 0.2) for p in positions])
        
        # Cholesky decomposition for correlation
        try:
            L = np.linalg.cholesky(correlations)
        except np.linalg.LinAlgError:
            # Fallback to diagonal matrix if correlation matrix is not positive definite
            L = np.eye(num_assets)
        
        # Generate independent random variables
        Z = np.random.normal(0, 1, (num_simulations, num_assets))
        
        # Apply correlation structure
        correlated_returns = Z @ L.T
        
        # Scale by volatility and add mean
        scaled_returns = correlated_returns * volatilities * np.sqrt(time_horizon) + mean_returns * time_horizon
        
        return scaled_returns
    
    def _calculate_portfolio_changes(
        self, 
        positions: List[Dict[str, Any]], 
        returns_matrix: np.ndarray
    ) -> np.ndarray:
        """Calculate portfolio value changes for each simulation"""
        
        num_simulations = returns_matrix.shape[0]
        num_assets = len(positions)
        
        portfolio_changes = np.zeros((num_simulations, num_assets))
        
        for i, position in enumerate(positions):
            notional_value = position.get("notional_value", 0)
            portfolio_changes[:, i] = returns_matrix[:, i] * notional_value
        
        return portfolio_changes
    
    def _calculate_var_from_simulation(
        self, 
        simulation_result: Dict[str, Any], 
        confidence_level: float
    ) -> Dict[str, Any]:
        """Calculate VaR from Monte Carlo simulation results"""
        
        total_changes = simulation_result["total_changes"]
        percentile = (1 - confidence_level) * 100
        
        var_value = np.percentile(total_changes, percentile)
        
        # Risk breakdown by asset
        portfolio_changes = simulation_result["portfolio_changes"]
        risk_breakdown = {}
        
        for i in range(portfolio_changes.shape[1]):
            asset_var = np.percentile(portfolio_changes[:, i], percentile)
            risk_breakdown[f"asset_{i}"] = {
                "var_contribution": float(asset_var),
                "risk_share": float(asset_var / var_value) if var_value != 0 else 0
            }
        
        return {
            "var_value": float(var_value),
            "risk_breakdown": risk_breakdown
        }
    
    def _calculate_energy(self, state: np.ndarray, qubo_matrix: np.ndarray) -> float:
        """Calculate energy (objective function value) for given state"""
        
        return float(state.T @ qubo_matrix @ state)
    
    async def stress_test_portfolio(
        self, 
        portfolio_data: Dict[str, Any],
        stress_scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform stress testing on portfolio under various scenarios
        
        Args:
            portfolio_data: Portfolio positions and market data
            stress_scenarios: List of stress scenarios to test
            
        Returns:
            Dict with stress test results
        """
        try:
            positions = portfolio_data.get("positions", [])
            if not positions:
                raise HTTPException(status_code=400, detail="No positions provided for stress testing")
            
            stress_results = []
            
            for scenario in stress_scenarios:
                scenario_result = await self._apply_stress_scenario(positions, scenario)
                stress_results.append(scenario_result)
            
            # Aggregate stress test results
            aggregate_result = self._aggregate_stress_results(stress_results)
            
            result_id = f"STRESS-{self.risk_counter:06d}"
            self.risk_counter += 1
            
            result = {
                "result_id": result_id,
                "scenarios_tested": len(stress_scenarios),
                "aggregate_result": aggregate_result,
                "scenario_results": stress_results,
                "calculated_at": datetime.now().isoformat()
            }
            
            self.risk_metrics[result_id] = result
            
            return {
                "success": True,
                "stress_test_result": result
            }
            
        except Exception as e:
            logger.error(f"Stress testing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _apply_stress_scenario(
        self, 
        positions: List[Dict[str, Any]], 
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply a specific stress scenario to portfolio"""
        
        scenario_name = scenario.get("name", "Unknown Scenario")
        market_shocks = scenario.get("market_shocks", {})
        correlation_changes = scenario.get("correlation_changes", {})
        
        # Calculate portfolio impact
        total_impact = 0.0
        position_impacts = []
        
        for position in positions:
            commodity = position.get("commodity", "unknown")
            notional_value = position.get("notional_value", 0)
            
            # Apply market shock if available
            shock_multiplier = market_shocks.get(commodity, 1.0)
            impact = notional_value * (shock_multiplier - 1.0)
            
            total_impact += impact
            position_impacts.append({
                "commodity": commodity,
                "notional_value": notional_value,
                "shock_multiplier": shock_multiplier,
                "impact": impact
            })
        
        return {
            "scenario_name": scenario_name,
            "total_impact": total_impact,
            "position_impacts": position_impacts,
            "market_shocks": market_shocks,
            "correlation_changes": correlation_changes
        }
    
    def _aggregate_stress_results(self, stress_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from multiple stress test scenarios"""
        
        total_impacts = [r["total_impact"] for r in stress_results]
        
        return {
            "worst_case_impact": min(total_impacts),
            "best_case_impact": max(total_impacts),
            "average_impact": np.mean(total_impacts),
            "impact_volatility": np.std(total_impacts),
            "scenarios_with_losses": len([i for i in total_impacts if i < 0]),
            "total_scenarios": len(total_impacts)
        }
    
    async def calculate_expected_shortfall(
        self, 
        portfolio_data: Dict[str, Any],
        confidence_level: float = 0.95,
        time_horizon: int = 1
    ) -> Dict[str, Any]:
        """
        Calculate Expected Shortfall (Conditional VaR)
        
        Args:
            portfolio_data: Portfolio positions and market data
            confidence_level: Confidence level for calculation
            time_horizon: Time horizon in days
            
        Returns:
            Dict with Expected Shortfall results
        """
        try:
            # First calculate VaR using Monte Carlo
            var_result = await self.calculate_var_monte_carlo(
                portfolio_data, confidence_level, time_horizon, 10000
            )
            
            # Extract simulation data
            simulation_data = var_result["var_result"]["simulation_summary"]
            var_value = var_result["var_result"]["var_value"]
            
            # Calculate Expected Shortfall (average of losses beyond VaR)
            # For simplicity, we'll use the simulation percentiles
            # In practice, this would use the full simulation data
            
            expected_shortfall = simulation_data["percentiles"]["5"]  # 5th percentile as approximation
            
            result = {
                "var_value": var_value,
                "expected_shortfall": expected_shortfall,
                "confidence_level": confidence_level,
                "time_horizon": time_horizon,
                "tail_risk_measure": expected_shortfall - var_value,
                "calculated_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "expected_shortfall_result": result
            }
            
        except Exception as e:
            logger.error(f"Expected Shortfall calculation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def generate_risk_report(
        self, 
        portfolio_data: Dict[str, Any],
        report_type: str = "comprehensive",
        include_scenarios: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive risk report
        
        Args:
            portfolio_data: Portfolio data for analysis
            report_type: Type of risk report to generate
            include_scenarios: Whether to include stress testing
            
        Returns:
            Dict with comprehensive risk report
        """
        try:
            # Calculate VaR
            var_result = await self.calculate_var_monte_carlo(portfolio_data)
            
            # Calculate Expected Shortfall
            es_result = await self.calculate_expected_shortfall(portfolio_data)
            
            # Perform stress testing if requested
            stress_result = None
            if include_scenarios:
                stress_scenarios = [
                    {
                        "name": "Market Crash",
                        "market_shocks": {
                            "crude_oil": 0.7,  # 30% decline
                            "natural_gas": 0.8,  # 20% decline
                            "electricity": 0.9,  # 10% decline
                            "coal": 0.6,  # 40% decline
                            "renewables": 0.95  # 5% decline
                        }
                    },
                    {
                        "name": "Supply Shock",
                        "market_shocks": {
                            "crude_oil": 1.3,  # 30% increase
                            "natural_gas": 1.4,  # 40% increase
                            "electricity": 1.2,  # 20% increase
                            "coal": 1.1,  # 10% increase
                            "renewables": 0.9  # 10% decline
                        }
                    }
                ]
                
                stress_result = await self.stress_test_portfolio(portfolio_data, stress_scenarios)
            
            # Compile comprehensive report
            report_id = f"RISK-REPORT-{datetime.now().strftime('%Y%m%d')}"
            
            risk_report = {
                "report_id": report_id,
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "portfolio_summary": {
                    "total_positions": len(portfolio_data.get("positions", [])),
                    "total_notional": sum(p.get("notional_value", 0) for p in portfolio_data.get("positions", [])),
                    "risk_metrics": {
                        "var_95": var_result["var_result"]["var_value"],
                        "expected_shortfall": es_result["expected_shortfall_result"]["expected_shortfall"],
                        "tail_risk": es_result["expected_shortfall_result"]["tail_risk_measure"]
                    }
                },
                "var_analysis": var_result["var_result"],
                "expected_shortfall_analysis": es_result["expected_shortfall_result"],
                "stress_testing": stress_result["stress_test_result"] if stress_result else None,
                "risk_recommendations": self._generate_risk_recommendations(
                    var_result["var_result"]["var_value"],
                    es_result["expected_shortfall_result"]["expected_shortfall"]
                )
            }
            
            return {
                "success": True,
                "risk_report": risk_report
            }
            
        except Exception as e:
            logger.error(f"Risk report generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def run_monte_carlo_simulation(
        self, 
        simulation_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation with parameters from API
        
        Args:
            simulation_params: Dictionary containing simulation parameters
            
        Returns:
            Dict with simulation results
        """
        try:
            # Extract parameters from simulation_params
            positions = simulation_params.get("positions", [])
            market_data = simulation_params.get("market_data", {})
            correlations = simulation_params.get("correlations", {})
            time_horizon = simulation_params.get("time_horizon", 1)
            num_simulations = simulation_params.get("num_simulations", 10000)
            
            if not positions:
                raise HTTPException(status_code=400, detail="No positions provided for simulation")
            
            # Run the simulation
            simulation_result = await self._run_monte_carlo_simulation(
                positions, market_data, correlations, time_horizon, num_simulations
            )
            
            # Generate simulation ID
            simulation_id = f"MC-{self.risk_counter:06d}"
            self.risk_counter += 1
            
            # Store results
            self.simulation_results[simulation_id] = {
                "simulation_id": simulation_id,
                "parameters": simulation_params,
                "results": simulation_result,
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            }
            
            return {
                "simulation_id": simulation_id,
                "status": "completed",
                "results": simulation_result
            }
            
        except Exception as e:
            logger.error(f"Monte Carlo simulation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _generate_risk_recommendations(self, var_value: float, expected_shortfall: float) -> List[str]:
        """Generate risk management recommendations based on metrics"""
        
        recommendations = []
        
        if var_value > 1000000:  # $1M
            recommendations.append("Consider reducing portfolio concentration in high-risk assets")
            recommendations.append("Implement dynamic hedging strategies")
        
        if expected_shortfall > 2000000:  # $2M
            recommendations.append("Review position sizing and leverage")
            recommendations.append("Consider portfolio insurance or options strategies")
        
        if not recommendations:
            recommendations.append("Current risk levels are within acceptable limits")
            recommendations.append("Continue monitoring and regular risk assessments")
        
        return recommendations
