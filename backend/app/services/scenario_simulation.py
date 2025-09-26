"""
Scenario Simulation Service
Advanced stress testing and scenario analysis for risk management
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import structlog
from dataclasses import dataclass
from enum import Enum
import json

logger = structlog.get_logger()

class ScenarioType(str, Enum):
    STRESS_TEST = "stress_test"
    MONTE_CARLO = "monte_carlo"
    HISTORICAL = "historical"
    REGULATORY = "regulatory"
    CLIMATE = "climate"
    GEOPOLITICAL = "geopolitical"

class SeverityLevel(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"

@dataclass
class ScenarioResult:
    """Scenario simulation result"""
    scenario_name: str
    scenario_type: ScenarioType
    severity: SeverityLevel
    portfolio_value_change: float
    var_95: float
    var_99: float
    expected_shortfall: float
    max_drawdown: float
    recovery_time: int  # days
    worst_case_loss: float
    probability: float
    confidence_interval: Tuple[float, float]
    risk_metrics: Dict[str, float]
    recommendations: List[str]

class ScenarioSimulator:
    """Advanced scenario simulation and stress testing engine"""
    
    def __init__(self):
        self.scenario_library = {}
        self.historical_scenarios = {}
        self.regulatory_scenarios = {}
        self.climate_scenarios = {}
        self.simulation_results = []
        
    def run_stress_test(self, portfolio: Dict[str, float], 
                       market_data: Dict[str, Any],
                       scenarios: List[str] = None) -> List[ScenarioResult]:
        """Run comprehensive stress testing"""
        try:
            if scenarios is None:
                scenarios = [
                    'market_crash', 'oil_price_shock', 'interest_rate_spike',
                    'currency_crisis', 'supply_disruption', 'regulatory_change'
                ]
            
            results = []
            
            for scenario_name in scenarios:
                if scenario_name == 'market_crash':
                    result = self._simulate_market_crash(portfolio, market_data)
                elif scenario_name == 'oil_price_shock':
                    result = self._simulate_oil_price_shock(portfolio, market_data)
                elif scenario_name == 'interest_rate_spike':
                    result = self._simulate_interest_rate_spike(portfolio, market_data)
                elif scenario_name == 'currency_crisis':
                    result = self._simulate_currency_crisis(portfolio, market_data)
                elif scenario_name == 'supply_disruption':
                    result = self._simulate_supply_disruption(portfolio, market_data)
                elif scenario_name == 'regulatory_change':
                    result = self._simulate_regulatory_change(portfolio, market_data)
                else:
                    result = self._simulate_custom_scenario(portfolio, market_data, scenario_name)
                
                results.append(result)
            
            self.simulation_results.extend(results)
            logger.info("Stress testing completed", scenarios=len(scenarios))
            
            return results
            
        except Exception as e:
            logger.error("Stress testing failed", error=str(e))
            raise
    
    def run_monte_carlo_simulation(self, portfolio: Dict[str, float],
                                  market_data: Dict[str, Any],
                                  num_simulations: int = 10000,
                                  time_horizon: int = 30) -> ScenarioResult:
        """Run Monte Carlo simulation for portfolio risk assessment"""
        try:
            # Generate random scenarios
            scenarios = []
            for _ in range(num_simulations):
                scenario = self._generate_random_scenario(market_data, time_horizon)
                scenarios.append(scenario)
            
            # Calculate portfolio performance for each scenario
            portfolio_returns = []
            for scenario in scenarios:
                portfolio_return = self._calculate_portfolio_return(portfolio, scenario)
                portfolio_returns.append(portfolio_return)
            
            # Calculate risk metrics
            portfolio_returns = np.array(portfolio_returns)
            var_95 = np.percentile(portfolio_returns, 5)
            var_99 = np.percentile(portfolio_returns, 1)
            expected_shortfall = np.mean(portfolio_returns[portfolio_returns <= var_95])
            max_drawdown = np.min(portfolio_returns)
            
            # Calculate confidence intervals
            mean_return = np.mean(portfolio_returns)
            std_return = np.std(portfolio_returns)
            confidence_interval = (
                mean_return - 1.96 * std_return,
                mean_return + 1.96 * std_return
            )
            
            # Generate recommendations
            recommendations = self._generate_monte_carlo_recommendations(
                portfolio_returns, var_95, var_99, expected_shortfall
            )
            
            result = ScenarioResult(
                scenario_name="Monte Carlo Simulation",
                scenario_type=ScenarioType.MONTE_CARLO,
                severity=SeverityLevel.MODERATE,
                portfolio_value_change=mean_return,
                var_95=var_95,
                var_99=var_99,
                expected_shortfall=expected_shortfall,
                max_drawdown=max_drawdown,
                recovery_time=self._estimate_recovery_time(portfolio_returns),
                worst_case_loss=var_99,
                probability=0.5,  # 50% probability for Monte Carlo
                confidence_interval=confidence_interval,
                risk_metrics={
                    'mean_return': mean_return,
                    'volatility': std_return,
                    'sharpe_ratio': mean_return / std_return if std_return > 0 else 0,
                    'skewness': self._calculate_skewness(portfolio_returns),
                    'kurtosis': self._calculate_kurtosis(portfolio_returns)
                },
                recommendations=recommendations
            )
            
            logger.info("Monte Carlo simulation completed", 
                       simulations=num_simulations,
                       var_95=var_95,
                       var_99=var_99)
            
            return result
            
        except Exception as e:
            logger.error("Monte Carlo simulation failed", error=str(e))
            raise
    
    def run_historical_scenario(self, portfolio: Dict[str, float],
                               historical_period: str = "2008_financial_crisis") -> ScenarioResult:
        """Run historical scenario analysis"""
        try:
            # Load historical scenario data
            historical_data = self._load_historical_scenario(historical_period)
            
            # Apply historical shocks to current portfolio
            portfolio_impact = self._apply_historical_shocks(portfolio, historical_data)
            
            # Calculate risk metrics
            var_95 = np.percentile(portfolio_impact, 5)
            var_99 = np.percentile(portfolio_impact, 1)
            expected_shortfall = np.mean(portfolio_impact[portfolio_impact <= var_95])
            max_drawdown = np.min(portfolio_impact)
            
            # Generate recommendations
            recommendations = self._generate_historical_recommendations(
                historical_period, portfolio_impact
            )
            
            result = ScenarioResult(
                scenario_name=f"Historical: {historical_period}",
                scenario_type=ScenarioType.HISTORICAL,
                severity=self._assess_historical_severity(historical_period),
                portfolio_value_change=np.mean(portfolio_impact),
                var_95=var_95,
                var_99=var_99,
                expected_shortfall=expected_shortfall,
                max_drawdown=max_drawdown,
                recovery_time=historical_data.get('recovery_time', 365),
                worst_case_loss=var_99,
                probability=historical_data.get('probability', 0.01),
                confidence_interval=(var_95, var_99),
                risk_metrics={
                    'historical_volatility': np.std(portfolio_impact),
                    'correlation_breakdown': historical_data.get('correlation_breakdown', 0.8),
                    'liquidity_crisis': historical_data.get('liquidity_crisis', 0.5)
                },
                recommendations=recommendations
            )
            
            logger.info("Historical scenario completed", period=historical_period)
            
            return result
            
        except Exception as e:
            logger.error("Historical scenario failed", error=str(e))
            raise
    
    def run_climate_scenario(self, portfolio: Dict[str, float],
                           climate_scenario: str = "net_zero_2050") -> ScenarioResult:
        """Run climate scenario analysis"""
        try:
            # Load climate scenario data
            climate_data = self._load_climate_scenario(climate_scenario)
            
            # Apply climate transition risks
            portfolio_impact = self._apply_climate_risks(portfolio, climate_data)
            
            # Calculate climate-specific metrics
            var_95 = np.percentile(portfolio_impact, 5)
            var_99 = np.percentile(portfolio_impact, 1)
            expected_shortfall = np.mean(portfolio_impact[portfolio_impact <= var_95])
            max_drawdown = np.min(portfolio_impact)
            
            # Generate climate recommendations
            recommendations = self._generate_climate_recommendations(
                climate_scenario, portfolio_impact, climate_data
            )
            
            result = ScenarioResult(
                scenario_name=f"Climate: {climate_scenario}",
                scenario_type=ScenarioType.CLIMATE,
                severity=self._assess_climate_severity(climate_scenario),
                portfolio_value_change=np.mean(portfolio_impact),
                var_95=var_95,
                var_99=var_99,
                expected_shortfall=expected_shortfall,
                max_drawdown=max_drawdown,
                recovery_time=climate_data.get('transition_period', 730),
                worst_case_loss=var_99,
                probability=climate_data.get('probability', 0.3),
                confidence_interval=(var_95, var_99),
                risk_metrics={
                    'carbon_intensity': climate_data.get('carbon_intensity', 0.5),
                    'transition_risk': climate_data.get('transition_risk', 0.3),
                    'physical_risk': climate_data.get('physical_risk', 0.2),
                    'stranded_assets': climate_data.get('stranded_assets', 0.1)
                },
                recommendations=recommendations
            )
            
            logger.info("Climate scenario completed", scenario=climate_scenario)
            
            return result
            
        except Exception as e:
            logger.error("Climate scenario failed", error=str(e))
            raise
    
    def _simulate_market_crash(self, portfolio: Dict[str, float], 
                              market_data: Dict[str, Any]) -> ScenarioResult:
        """Simulate market crash scenario"""
        # Market crash: -30% to -50% across all assets
        crash_factor = np.random.uniform(0.5, 0.7)
        
        portfolio_impact = []
        for commodity, weight in portfolio.items():
            impact = weight * crash_factor
            portfolio_impact.append(impact)
        
        total_impact = sum(portfolio_impact)
        
        return ScenarioResult(
            scenario_name="Market Crash",
            scenario_type=ScenarioType.STRESS_TEST,
            severity=SeverityLevel.EXTREME,
            portfolio_value_change=total_impact,
            var_95=total_impact * 0.8,
            var_99=total_impact * 0.9,
            expected_shortfall=total_impact * 0.85,
            max_drawdown=total_impact,
            recovery_time=365,
            worst_case_loss=total_impact,
            probability=0.05,
            confidence_interval=(total_impact * 0.8, total_impact),
            risk_metrics={'crash_factor': crash_factor},
            recommendations=[
                "Reduce portfolio concentration",
                "Increase cash position",
                "Consider hedging strategies"
            ]
        )
    
    def _simulate_oil_price_shock(self, portfolio: Dict[str, float], 
                                 market_data: Dict[str, Any]) -> ScenarioResult:
        """Simulate oil price shock scenario"""
        # Oil price shock: -40% to -60%
        oil_shock = np.random.uniform(0.4, 0.6)
        
        portfolio_impact = 0
        if 'crude_oil' in portfolio:
            portfolio_impact += portfolio['crude_oil'] * oil_shock
        
        return ScenarioResult(
            scenario_name="Oil Price Shock",
            scenario_type=ScenarioType.STRESS_TEST,
            severity=SeverityLevel.SEVERE,
            portfolio_value_change=portfolio_impact,
            var_95=portfolio_impact * 0.9,
            var_99=portfolio_impact,
            expected_shortfall=portfolio_impact * 0.95,
            max_drawdown=portfolio_impact,
            recovery_time=180,
            worst_case_loss=portfolio_impact,
            probability=0.1,
            confidence_interval=(portfolio_impact * 0.9, portfolio_impact),
            risk_metrics={'oil_shock': oil_shock},
            recommendations=[
                "Diversify away from oil exposure",
                "Consider alternative energy investments",
                "Implement dynamic hedging"
            ]
        )
    
    def _simulate_interest_rate_spike(self, portfolio: Dict[str, float], 
                                    market_data: Dict[str, Any]) -> ScenarioResult:
        """Simulate interest rate spike scenario"""
        # Interest rate spike: +200 to +400 basis points
        rate_spike = np.random.uniform(2.0, 4.0)
        
        # Impact on fixed income and equity valuations
        portfolio_impact = -0.02 * rate_spike  # Simplified impact
        
        return ScenarioResult(
            scenario_name="Interest Rate Spike",
            scenario_type=ScenarioType.STRESS_TEST,
            severity=SeverityLevel.MODERATE,
            portfolio_value_change=portfolio_impact,
            var_95=portfolio_impact * 1.1,
            var_99=portfolio_impact * 1.2,
            expected_shortfall=portfolio_impact * 1.05,
            max_drawdown=portfolio_impact,
            recovery_time=90,
            worst_case_loss=portfolio_impact,
            probability=0.15,
            confidence_interval=(portfolio_impact * 1.1, portfolio_impact),
            risk_metrics={'rate_spike': rate_spike},
            recommendations=[
                "Reduce duration exposure",
                "Consider floating rate instruments",
                "Monitor central bank communications"
            ]
        )
    
    def _simulate_currency_crisis(self, portfolio: Dict[str, float], 
                                 market_data: Dict[str, Any]) -> ScenarioResult:
        """Simulate currency crisis scenario"""
        # Currency crisis: -20% to -40% in emerging market currencies
        currency_shock = np.random.uniform(0.2, 0.4)
        
        portfolio_impact = 0
        # Assume some exposure to emerging market currencies
        em_exposure = 0.2  # 20% exposure
        portfolio_impact = em_exposure * currency_shock
        
        return ScenarioResult(
            scenario_name="Currency Crisis",
            scenario_type=ScenarioType.STRESS_TEST,
            severity=SeverityLevel.SEVERE,
            portfolio_value_change=portfolio_impact,
            var_95=portfolio_impact * 1.1,
            var_99=portfolio_impact * 1.2,
            expected_shortfall=portfolio_impact * 1.05,
            max_drawdown=portfolio_impact,
            recovery_time=270,
            worst_case_loss=portfolio_impact,
            probability=0.08,
            confidence_interval=(portfolio_impact * 1.1, portfolio_impact),
            risk_metrics={'currency_shock': currency_shock},
            recommendations=[
                "Hedge currency exposure",
                "Diversify across currencies",
                "Monitor political stability"
            ]
        )
    
    def _simulate_supply_disruption(self, portfolio: Dict[str, float], 
                                   market_data: Dict[str, Any]) -> ScenarioResult:
        """Simulate supply disruption scenario"""
        # Supply disruption: +30% to +50% price increase
        supply_shock = np.random.uniform(0.3, 0.5)
        
        portfolio_impact = 0
        # Impact on energy commodities
        energy_exposure = sum(weight for commodity, weight in portfolio.items() 
                            if commodity in ['crude_oil', 'natural_gas'])
        portfolio_impact = energy_exposure * supply_shock
        
        return ScenarioResult(
            scenario_name="Supply Disruption",
            scenario_type=ScenarioType.STRESS_TEST,
            severity=SeverityLevel.MODERATE,
            portfolio_value_change=portfolio_impact,
            var_95=portfolio_impact * 0.9,
            var_99=portfolio_impact,
            expected_shortfall=portfolio_impact * 0.95,
            max_drawdown=portfolio_impact,
            recovery_time=120,
            worst_case_loss=portfolio_impact,
            probability=0.12,
            confidence_interval=(portfolio_impact * 0.9, portfolio_impact),
            risk_metrics={'supply_shock': supply_shock},
            recommendations=[
                "Diversify supply sources",
                "Consider storage strategies",
                "Monitor geopolitical risks"
            ]
        )
    
    def _simulate_regulatory_change(self, portfolio: Dict[str, float], 
                                   market_data: Dict[str, Any]) -> ScenarioResult:
        """Simulate regulatory change scenario"""
        # Regulatory change: -10% to -20% impact
        regulatory_impact = np.random.uniform(0.1, 0.2)
        
        portfolio_impact = -regulatory_impact  # Negative impact
        
        return ScenarioResult(
            scenario_name="Regulatory Change",
            scenario_type=ScenarioType.REGULATORY,
            severity=SeverityLevel.MODERATE,
            portfolio_value_change=portfolio_impact,
            var_95=portfolio_impact * 1.1,
            var_99=portfolio_impact * 1.2,
            expected_shortfall=portfolio_impact * 1.05,
            max_drawdown=portfolio_impact,
            recovery_time=180,
            worst_case_loss=portfolio_impact,
            probability=0.2,
            confidence_interval=(portfolio_impact * 1.1, portfolio_impact),
            risk_metrics={'regulatory_impact': regulatory_impact},
            recommendations=[
                "Monitor regulatory developments",
                "Engage with policymakers",
                "Consider compliance costs"
            ]
        )
    
    def _simulate_custom_scenario(self, portfolio: Dict[str, float], 
                                 market_data: Dict[str, Any], 
                                 scenario_name: str) -> ScenarioResult:
        """Simulate custom scenario"""
        # Generic custom scenario
        impact = np.random.uniform(-0.2, 0.2)
        
        return ScenarioResult(
            scenario_name=f"Custom: {scenario_name}",
            scenario_type=ScenarioType.STRESS_TEST,
            severity=SeverityLevel.MODERATE,
            portfolio_value_change=impact,
            var_95=impact * 1.1,
            var_99=impact * 1.2,
            expected_shortfall=impact * 1.05,
            max_drawdown=impact,
            recovery_time=90,
            worst_case_loss=impact,
            probability=0.1,
            confidence_interval=(impact * 1.1, impact),
            risk_metrics={'custom_impact': impact},
            recommendations=["Monitor scenario developments", "Adjust risk management"]
        )
    
    def _generate_random_scenario(self, market_data: Dict[str, Any], 
                                 time_horizon: int) -> Dict[str, Any]:
        """Generate random scenario for Monte Carlo"""
        scenario = {}
        
        for commodity in market_data.keys():
            # Generate random returns
            mean_return = market_data[commodity].get('mean_return', 0.001)
            volatility = market_data[commodity].get('volatility', 0.02)
            
            # Generate time series of returns
            returns = np.random.normal(mean_return, volatility, time_horizon)
            scenario[commodity] = returns
        
        return scenario
    
    def _calculate_portfolio_return(self, portfolio: Dict[str, float], 
                                  scenario: Dict[str, Any]) -> float:
        """Calculate portfolio return for a scenario"""
        total_return = 0
        
        for commodity, weight in portfolio.items():
            if commodity in scenario:
                # Calculate cumulative return
                cumulative_return = np.prod(1 + scenario[commodity]) - 1
                total_return += weight * cumulative_return
        
        return total_return
    
    def _estimate_recovery_time(self, portfolio_returns: np.ndarray) -> int:
        """Estimate recovery time from drawdowns"""
        # Simplified recovery time estimation
        max_drawdown = np.min(portfolio_returns)
        if max_drawdown < -0.1:  # 10% drawdown
            return 180  # 6 months
        elif max_drawdown < -0.05:  # 5% drawdown
            return 90   # 3 months
        else:
            return 30   # 1 month
    
    def _calculate_skewness(self, returns: np.ndarray) -> float:
        """Calculate skewness of returns"""
        mean = np.mean(returns)
        std = np.std(returns)
        if std == 0:
            return 0
        return np.mean(((returns - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, returns: np.ndarray) -> float:
        """Calculate kurtosis of returns"""
        mean = np.mean(returns)
        std = np.std(returns)
        if std == 0:
            return 0
        return np.mean(((returns - mean) / std) ** 4) - 3
    
    def _load_historical_scenario(self, period: str) -> Dict[str, Any]:
        """Load historical scenario data"""
        scenarios = {
            "2008_financial_crisis": {
                'market_decline': -0.5,
                'volatility_spike': 0.8,
                'correlation_breakdown': 0.9,
                'liquidity_crisis': 0.7,
                'recovery_time': 1095  # 3 years
            },
            "2020_covid_crash": {
                'market_decline': -0.35,
                'volatility_spike': 0.6,
                'correlation_breakdown': 0.8,
                'liquidity_crisis': 0.5,
                'recovery_time': 180  # 6 months
            }
        }
        
        return scenarios.get(period, scenarios["2008_financial_crisis"])
    
    def _load_climate_scenario(self, scenario: str) -> Dict[str, Any]:
        """Load climate scenario data"""
        scenarios = {
            "net_zero_2050": {
                'carbon_intensity': 0.3,
                'transition_risk': 0.4,
                'physical_risk': 0.2,
                'stranded_assets': 0.15,
                'transition_period': 1095  # 3 years
            },
            "delayed_transition": {
                'carbon_intensity': 0.6,
                'transition_risk': 0.6,
                'physical_risk': 0.4,
                'stranded_assets': 0.25,
                'transition_period': 1825  # 5 years
            }
        }
        
        return scenarios.get(scenario, scenarios["net_zero_2050"])
    
    def _apply_historical_shocks(self, portfolio: Dict[str, float], 
                               historical_data: Dict[str, Any]) -> np.ndarray:
        """Apply historical shocks to portfolio"""
        # Generate portfolio impact based on historical data
        base_impact = historical_data['market_decline']
        volatility = historical_data.get('volatility_spike', 0.3)
        
        # Add some randomness
        impacts = np.random.normal(base_impact, volatility, 1000)
        return impacts
    
    def _apply_climate_risks(self, portfolio: Dict[str, float], 
                            climate_data: Dict[str, Any]) -> np.ndarray:
        """Apply climate risks to portfolio"""
        # Calculate climate impact based on carbon intensity
        carbon_intensity = climate_data['carbon_intensity']
        transition_risk = climate_data['transition_risk']
        
        # Generate climate impact scenarios
        base_impact = -carbon_intensity * transition_risk
        volatility = 0.1
        
        impacts = np.random.normal(base_impact, volatility, 1000)
        return impacts
    
    def _assess_historical_severity(self, period: str) -> SeverityLevel:
        """Assess severity of historical period"""
        if period == "2008_financial_crisis":
            return SeverityLevel.EXTREME
        elif period == "2020_covid_crash":
            return SeverityLevel.SEVERE
        else:
            return SeverityLevel.MODERATE
    
    def _assess_climate_severity(self, scenario: str) -> SeverityLevel:
        """Assess severity of climate scenario"""
        if scenario == "net_zero_2050":
            return SeverityLevel.MODERATE
        elif scenario == "delayed_transition":
            return SeverityLevel.SEVERE
        else:
            return SeverityLevel.MODERATE
    
    def _generate_monte_carlo_recommendations(self, returns: np.ndarray, 
                                            var_95: float, var_99: float, 
                                            expected_shortfall: float) -> List[str]:
        """Generate recommendations based on Monte Carlo results"""
        recommendations = []
        
        if var_95 < -0.1:
            recommendations.append("Consider reducing portfolio risk")
        
        if expected_shortfall < -0.05:
            recommendations.append("Implement tail risk hedging")
        
        if np.std(returns) > 0.05:
            recommendations.append("Diversify portfolio holdings")
        
        return recommendations
    
    def _generate_historical_recommendations(self, period: str, 
                                           portfolio_impact: np.ndarray) -> List[str]:
        """Generate recommendations based on historical scenario"""
        recommendations = []
        
        if period == "2008_financial_crisis":
            recommendations.extend([
                "Maintain high liquidity buffers",
                "Diversify across asset classes",
                "Monitor correlation breakdowns"
            ])
        elif period == "2020_covid_crash":
            recommendations.extend([
                "Prepare for rapid market changes",
                "Consider defensive positioning",
                "Monitor global health indicators"
            ])
        
        return recommendations
    
    def _generate_climate_recommendations(self, scenario: str, 
                                        portfolio_impact: np.ndarray, 
                                        climate_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on climate scenario"""
        recommendations = []
        
        if scenario == "net_zero_2050":
            recommendations.extend([
                "Transition to low-carbon investments",
                "Monitor carbon pricing developments",
                "Assess stranded asset risks"
            ])
        elif scenario == "delayed_transition":
            recommendations.extend([
                "Prepare for higher transition costs",
                "Consider climate adaptation strategies",
                "Monitor regulatory developments"
            ])
        
        return recommendations

# Global scenario simulator instance
scenario_simulator = ScenarioSimulator()
