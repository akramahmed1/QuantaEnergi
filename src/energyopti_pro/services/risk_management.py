import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import json

class RiskManagementService:
    """Comprehensive risk management service for ETRM/CTRM"""
    
    def __init__(self):
        self.risk_models = {
            "var": self._calculate_var,
            "stress_test": self._run_stress_tests,
            "correlation": self._calculate_correlations,
            "credit_risk": self._assess_credit_risk,
            "liquidity_risk": self._assess_liquidity_risk,
            "operational_risk": self._assess_operational_risk
        }
        
        # Regional risk parameters
        self.regional_params = {
            "ME": {
                "volatility_multiplier": 1.2,
                "correlation_threshold": 0.4,
                "liquidity_factor": 0.8
            },
            "US": {
                "volatility_multiplier": 1.0,
                "correlation_threshold": 0.3,
                "liquidity_factor": 1.0
            },
            "UK": {
                "volatility_multiplier": 1.1,
                "correlation_threshold": 0.35,
                "liquidity_factor": 0.9
            },
            "EU": {
                "volatility_multiplier": 1.05,
                "correlation_threshold": 0.32,
                "liquidity_factor": 0.95
            },
            "GUYANA": {
                "volatility_multiplier": 1.5,
                "correlation_threshold": 0.6,
                "liquidity_factor": 0.6
            }
        }
    
    async def calculate_portfolio_risk(
        self, 
        positions: List[Dict], 
        market_data: List[Dict],
        region: str,
        confidence_level: float = 0.95
    ) -> Dict:
        """Calculate comprehensive portfolio risk metrics"""
        
        # Calculate VaR
        var_result = await self._calculate_var(positions, market_data, region, confidence_level)
        
        # Run stress tests
        stress_result = await self._run_stress_tests(positions, market_data, region)
        
        # Calculate correlations
        correlation_result = await self._calculate_correlations(positions, market_data, region)
        
        # Assess credit risk
        credit_result = await self._assess_credit_risk(positions, region)
        
        # Assess liquidity risk
        liquidity_result = await self._assess_liquidity_risk(positions, market_data, region)
        
        # Calculate Expected Shortfall (Conditional VaR)
        es_result = await self._calculate_expected_shortfall(positions, market_data, region, confidence_level)
        
        return {
            "portfolio_risk_summary": {
                "total_var": var_result["var"],
                "expected_shortfall": es_result["expected_shortfall"],
                "stress_test_worst_case": stress_result["worst_case_scenario"],
                "credit_exposure": credit_result["total_exposure"],
                "liquidity_score": liquidity_result["liquidity_score"]
            },
            "detailed_metrics": {
                "var_analysis": var_result,
                "stress_testing": stress_result,
                "correlation_analysis": correlation_result,
                "credit_risk": credit_result,
                "liquidity_risk": liquidity_result,
                "expected_shortfall": es_result
            },
            "risk_limits": await self._get_risk_limits(region),
            "compliance_status": await self._check_compliance(positions, region),
            "calculation_timestamp": datetime.now(),
            "region": region
        }
    
    async def _calculate_var(
        self, 
        positions: List[Dict], 
        market_data: List[Dict],
        region: str,
        confidence_level: float
    ) -> Dict:
        """Calculate Value at Risk using historical simulation"""
        
        # Get regional parameters
        regional_params = self.regional_params.get(region, self.regional_params["US"])
        
        # Calculate position values and P&L
        position_values = []
        for position in positions:
            # Find corresponding market price
            market_price = next(
                (m["price"] for m in market_data if m["commodity"] == position["commodity"]), 
                0
            )
            
            if market_price > 0:
                position_value = position["net_quantity"] * market_price
                position_values.append(position_value)
        
        if not position_values:
            return {"var": 0, "confidence_level": confidence_level, "method": "historical_simulation"}
        
        # Calculate returns (simplified)
        returns = np.diff(position_values) / position_values[:-1] if len(position_values) > 1 else [0]
        
        # Apply regional volatility adjustment
        volatility_multiplier = regional_params["volatility_multiplier"]
        adjusted_returns = [r * volatility_multiplier for r in returns]
        
        # Calculate VaR
        if len(adjusted_returns) > 0:
            var_percentile = np.percentile(adjusted_returns, (1 - confidence_level) * 100)
            var = abs(var_percentile) * sum(position_values)
        else:
            var = 0
        
        return {
            "var": float(var),
            "confidence_level": confidence_level,
            "method": "historical_simulation",
            "volatility_multiplier": volatility_multiplier,
            "total_position_value": sum(position_values)
        }
    
    async def _run_stress_tests(
        self, 
        positions: List[Dict], 
        market_data: List[Dict],
        region: str
    ) -> Dict:
        """Run comprehensive stress tests"""
        
        scenarios = {
            "market_crash": {
                "price_shock": -0.30,
                "volatility_increase": 2.0,
                "correlation_breakdown": True
            },
            "liquidity_crisis": {
                "price_shock": -0.15,
                "volatility_increase": 1.5,
                "correlation_breakdown": False
            },
            "regulatory_change": {
                "price_shock": -0.10,
                "volatility_increase": 1.2,
                "correlation_breakdown": False
            },
            "extreme_weather": {
                "price_shock": 0.25,
                "volatility_increase": 1.8,
                "correlation_breakdown": True
            }
        }
        
        stress_results = {}
        total_position_value = sum(p.get("net_quantity", 0) for p in positions)
        
        for scenario_name, scenario_params in scenarios.items():
            # Apply regional adjustments
            regional_adjustment = self.regional_params.get(region, {}).get("volatility_multiplier", 1.0)
            adjusted_price_shock = scenario_params["price_shock"] * regional_adjustment
            
            # Calculate scenario impact
            scenario_impact = total_position_value * adjusted_price_shock
            
            stress_results[scenario_name] = {
                "price_shock": adjusted_price_shock,
                "impact_on_portfolio": float(scenario_impact),
                "volatility_increase": scenario_params["volatility_increase"],
                "correlation_breakdown": scenario_params["correlation_breakdown"]
            }
        
        # Find worst case scenario
        worst_case = min(stress_results.items(), key=lambda x: x[1]["impact_on_portfolio"])
        
        return {
            "scenarios": stress_results,
            "worst_case_scenario": {
                "name": worst_case[0],
                "impact": worst_case[1]["impact_on_portfolio"]
            },
            "total_portfolio_value": total_position_value
        }
    
    async def _calculate_correlations(
        self, 
        positions: List[Dict], 
        market_data: List[Dict],
        region: str
    ) -> Dict:
        """Calculate correlation matrix and identify concentration risks"""
        
        regional_params = self.regional_params.get(region, self.regional_params["US"])
        correlation_threshold = regional_params["correlation_threshold"]
        
        # Extract commodities from positions
        commodities = list(set(p["commodity"] for p in positions))
        
        if len(commodities) < 2:
            return {
                "correlation_matrix": {},
                "concentration_risks": [],
                "diversification_score": 1.0
            }
        
        # Mock correlation matrix (in production, calculate from historical data)
        correlation_matrix = {}
        for i, comm1 in enumerate(commodities):
            for j, comm2 in enumerate(commodities):
                if i == j:
                    correlation_matrix[f"{comm1}_{comm2}"] = 1.0
                else:
                    # Mock correlations based on commodity types
                    if "power" in comm1.lower() and "power" in comm2.lower():
                        correlation_matrix[f"{comm1}_{comm2}"] = 0.8
                    elif "gas" in comm1.lower() and "gas" in comm2.lower():
                        correlation_matrix[f"{comm1}_{comm2}"] = 0.7
                    else:
                        correlation_matrix[f"{comm1}_{comm2}"] = np.random.uniform(0.1, 0.5)
        
        # Identify high correlations (concentration risks)
        concentration_risks = []
        for key, value in correlation_matrix.items():
            if value > correlation_threshold and key.split("_")[0] != key.split("_")[1]:
                concentration_risks.append({
                    "commodities": key.split("_"),
                    "correlation": value,
                    "risk_level": "high" if value > 0.7 else "medium"
                })
        
        # Calculate diversification score
        diversification_score = 1.0 - (len(concentration_risks) / len(correlation_matrix))
        
        return {
            "correlation_matrix": correlation_matrix,
            "concentration_risks": concentration_risks,
            "diversification_score": diversification_score,
            "correlation_threshold": correlation_threshold
        }
    
    async def _assess_credit_risk(self, positions: List[Dict], region: str) -> Dict:
        """Assess counterparty credit risk"""
        
        # Group positions by counterparty
        counterparty_exposure = {}
        for position in positions:
            counterparty = position.get("counterparty_id", "unknown")
            if counterparty not in counterparty_exposure:
                counterparty_exposure[counterparty] = 0
            counterparty_exposure[counterparty] += abs(position.get("net_quantity", 0))
        
        # Calculate credit risk metrics
        total_exposure = sum(counterparty_exposure.values())
        max_single_exposure = max(counterparty_exposure.values()) if counterparty_exposure else 0
        concentration_ratio = max_single_exposure / total_exposure if total_exposure > 0 else 0
        
        # Regional credit risk adjustments
        regional_credit_factors = {
            "ME": 1.1,  # Higher credit risk in emerging markets
            "US": 1.0,  # Baseline
            "UK": 1.05, # Slightly higher due to Brexit uncertainty
            "EU": 1.02, # Slightly higher due to regulatory complexity
            "GUYANA": 1.3  # Higher credit risk in developing markets
        }
        
        credit_factor = regional_credit_factors.get(region, 1.0)
        adjusted_total_exposure = total_exposure * credit_factor
        
        return {
            "total_exposure": float(adjusted_total_exposure),
            "counterparty_exposure": counterparty_exposure,
            "max_single_exposure": float(max_single_exposure),
            "concentration_ratio": concentration_ratio,
            "credit_risk_score": "high" if concentration_ratio > 0.3 else "medium" if concentration_ratio > 0.1 else "low",
            "regional_credit_factor": credit_factor
        }
    
    async def _assess_liquidity_risk(
        self, 
        positions: List[Dict], 
        market_data: List[Dict],
        region: str
    ) -> Dict:
        """Assess liquidity risk based on position size and market depth"""
        
        regional_params = self.regional_params.get(region, self.regional_params["US"])
        liquidity_factor = regional_params["liquidity_factor"]
        
        # Calculate liquidity metrics
        total_position_size = sum(abs(p.get("net_quantity", 0)) for p in positions)
        
        # Mock market depth (in production, get from market data providers)
        market_depth = {
            "power": 1000000,  # MW
            "gas": 500000,     # MMBtu
            "oil": 100000,     # barrels
            "carbon": 1000000  # tons CO2
        }
        
        # Calculate liquidity score
        liquidity_scores = []
        for position in positions:
            commodity = position.get("commodity", "unknown")
            quantity = abs(position.get("net_quantity", 0))
            depth = market_depth.get(commodity.lower(), 100000)
            
            # Liquidity score based on position size relative to market depth
            if depth > 0:
                score = 1.0 - (quantity / depth)
                liquidity_scores.append(max(0, score))
            else:
                liquidity_scores.append(0)
        
        # Apply regional liquidity factor
        adjusted_liquidity_score = np.mean(liquidity_scores) * liquidity_factor
        
        return {
            "liquidity_score": float(adjusted_liquidity_score),
            "total_position_size": float(total_position_size),
            "market_depth": market_depth,
            "individual_scores": liquidity_scores,
            "regional_liquidity_factor": liquidity_factor,
            "risk_level": "high" if adjusted_liquidity_score < 0.3 else "medium" if adjusted_liquidity_score < 0.7 else "low"
        }
    
    async def _calculate_expected_shortfall(
        self, 
        positions: List[Dict], 
        market_data: List[Dict],
        region: str,
        confidence_level: float
    ) -> Dict:
        """Calculate Expected Shortfall (Conditional VaR)"""
        
        # Get VaR first
        var_result = await self._calculate_var(positions, market_data, region, confidence_level)
        var = var_result["var"]
        
        # Calculate Expected Shortfall (average of losses beyond VaR)
        # In production, this would use historical simulation or Monte Carlo
        expected_shortfall = var * 1.2  # Typical ES is 20-30% higher than VaR
        
        return {
            "expected_shortfall": float(expected_shortfall),
            "var": var,
            "confidence_level": confidence_level,
            "es_to_var_ratio": 1.2
        }
    
    async def _get_risk_limits(self, region: str) -> Dict:
        """Get risk limits for the region"""
        
        limits = {
            "ME": {
                "var_limit": 1000000,
                "position_limit": 5000000,
                "credit_limit": 2000000,
                "concentration_limit": 0.25
            },
            "US": {
                "var_limit": 2000000,
                "position_limit": 10000000,
                "credit_limit": 5000000,
                "concentration_limit": 0.20
            },
            "UK": {
                "var_limit": 1500000,
                "position_limit": 7500000,
                "credit_limit": 3000000,
                "concentration_limit": 0.22
            },
            "EU": {
                "var_limit": 1800000,
                "position_limit": 9000000,
                "credit_limit": 4000000,
                "concentration_limit": 0.21
            },
            "GUYANA": {
                "var_limit": 500000,
                "position_limit": 2500000,
                "credit_limit": 1000000,
                "concentration_limit": 0.30
            }
        }
        
        return limits.get(region, limits["US"])
    
    async def _check_compliance(self, positions: List[Dict], region: str) -> Dict:
        """Check compliance with regional regulations"""
        
        compliance_checks = {
            "position_limits": True,
            "concentration_limits": True,
            "reporting_requirements": True,
            "documentation": True
        }
        
        # Check position limits
        total_position_value = sum(abs(p.get("net_quantity", 0)) for p in positions)
        limits = await self._get_risk_limits(region)
        
        if total_position_value > limits["position_limit"]:
            compliance_checks["position_limits"] = False
        
        # Check concentration limits
        if len(positions) > 0:
            max_position = max(abs(p.get("net_quantity", 0)) for p in positions)
            concentration_ratio = max_position / total_position_value if total_position_value > 0 else 0
            
            if concentration_ratio > limits["concentration_limit"]:
                compliance_checks["concentration_limits"] = False
        
        return {
            "overall_compliance": all(compliance_checks.values()),
            "checks": compliance_checks,
            "region": region,
            "limits_applied": limits
        }
    
    async def generate_risk_report(
        self, 
        portfolio_id: str,
        positions: List[Dict],
        market_data: List[Dict],
        region: str
    ) -> Dict:
        """Generate comprehensive risk report"""
        
        risk_metrics = await self.calculate_portfolio_risk(positions, market_data, region)
        
        report = {
            "report_id": f"RISK-{region}-{datetime.now().strftime('%Y%m%d')}-{portfolio_id}",
            "portfolio_id": portfolio_id,
            "region": region,
            "generation_date": datetime.now(),
            "executive_summary": {
                "total_risk_score": self._calculate_overall_risk_score(risk_metrics),
                "key_risk_factors": self._identify_key_risk_factors(risk_metrics),
                "recommendations": self._generate_risk_recommendations(risk_metrics)
            },
            "detailed_analysis": risk_metrics,
            "compliance_summary": risk_metrics["compliance_status"]
        }
        
        return report
    
    def _calculate_overall_risk_score(self, risk_metrics: Dict) -> str:
        """Calculate overall risk score based on all metrics"""
        
        risk_factors = []
        
        # VaR analysis
        var = risk_metrics["detailed_metrics"]["var_analysis"]["var"]
        var_limit = risk_metrics["risk_limits"]["var_limit"]
        if var > var_limit * 0.8:
            risk_factors.append("high_var")
        
        # Stress testing
        worst_case = risk_metrics["detailed_metrics"]["stress_testing"]["worst_case_scenario"]["impact"]
        if abs(worst_case) > var_limit:
            risk_factors.append("high_stress_impact")
        
        # Credit risk
        credit_score = risk_metrics["detailed_metrics"]["credit_risk"]["credit_risk_score"]
        if credit_score == "high":
            risk_factors.append("high_credit_risk")
        
        # Liquidity risk
        liquidity_score = risk_metrics["detailed_metrics"]["liquidity_risk"]["liquidity_score"]
        if liquidity_score < 0.5:
            risk_factors.append("low_liquidity")
        
        # Determine overall score
        if len(risk_factors) >= 3:
            return "HIGH"
        elif len(risk_factors) >= 1:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _identify_key_risk_factors(self, risk_metrics: Dict) -> List[str]:
        """Identify key risk factors"""
        
        factors = []
        
        # Check various risk metrics and identify concerns
        if risk_metrics["detailed_metrics"]["var_analysis"]["var"] > 1000000:
            factors.append("High Value at Risk")
        
        if risk_metrics["detailed_metrics"]["credit_risk"]["concentration_ratio"] > 0.2:
            factors.append("High Counterparty Concentration")
        
        if risk_metrics["detailed_metrics"]["liquidity_risk"]["liquidity_score"] < 0.6:
            factors.append("Low Liquidity")
        
        if not risk_metrics["compliance_status"]["overall_compliance"]:
            factors.append("Compliance Violations")
        
        return factors
    
    def _generate_risk_recommendations(self, risk_metrics: Dict) -> List[str]:
        """Generate risk management recommendations"""
        
        recommendations = []
        
        # VaR recommendations
        if risk_metrics["detailed_metrics"]["var_analysis"]["var"] > 1000000:
            recommendations.append("Consider reducing position sizes to lower VaR")
        
        # Concentration recommendations
        if risk_metrics["detailed_metrics"]["credit_risk"]["concentration_ratio"] > 0.2:
            recommendations.append("Diversify counterparty exposure to reduce concentration risk")
        
        # Liquidity recommendations
        if risk_metrics["detailed_metrics"]["liquidity_risk"]["liquidity_score"] < 0.6:
            recommendations.append("Review position sizes relative to market depth")
        
        # Compliance recommendations
        if not risk_metrics["compliance_status"]["overall_compliance"]:
            recommendations.append("Immediate action required to address compliance violations")
        
        return recommendations 