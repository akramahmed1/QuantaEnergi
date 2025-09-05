"""
Advanced Risk Management Service
ETRM/CTRM Credit Risk Modeling, Counterparty Assessment, Stress Testing
"""

from fastapi import HTTPException
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import random
import math
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from uuid import uuid4
import numpy as np

logger = logging.getLogger(__name__)

class RiskType(Enum):
    """Risk type enumeration"""
    CREDIT = "credit"
    MARKET = "market"
    OPERATIONAL = "operational"
    LIQUIDITY = "liquidity"
    COUNTERPARTY = "counterparty"
    REGULATORY = "regulatory"

class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class StressTestScenario(Enum):
    """Stress test scenario enumeration"""
    MARKET_CRASH = "market_crash"
    INTEREST_RATE_SHOCK = "interest_rate_shock"
    COMMODITY_PRICE_SHOCK = "commodity_price_shock"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    COUNTERPARTY_DEFAULT = "counterparty_default"

class AdvancedRiskManagement:
    """Advanced risk management with credit modeling and stress testing"""
    
    def __init__(self):
        self.risk_models = {}
        self.counterparty_ratings = {}
        self.stress_test_results = {}
        self.risk_limits = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def credit_risk_model(self, counterparty_id: str, trade_data: Dict) -> Dict:
        """Credit risk modeling for counterparty assessment"""
        try:
            if not counterparty_id:
                raise ValueError("Counterparty ID is required")
            
            # Get or create counterparty rating
            if counterparty_id not in self.counterparty_ratings:
                await self._initialize_counterparty_rating(counterparty_id)
            
            rating = self.counterparty_ratings[counterparty_id]
            
            # Calculate credit risk metrics
            notional_amount = trade_data.get("notional_amount", 0)
            exposure_at_default = notional_amount * 0.4  # 40% EAD assumption
            
            # Probability of Default (PD) based on rating
            pd = self._calculate_pd(rating["rating"])
            
            # Loss Given Default (LGD) - varies by asset type
            lgd = self._calculate_lgd(trade_data.get("asset_type", "energy"))
            
            # Expected Loss
            expected_loss = exposure_at_default * pd * lgd
            
            # Credit Value Adjustment (CVA)
            cva = self._calculate_cva(notional_amount, pd, lgd)
            
            # Risk metrics
            risk_metrics = {
                "counterparty_id": counterparty_id,
                "rating": rating["rating"],
                "exposure_at_default": round(exposure_at_default, 2),
                "probability_of_default": round(pd, 4),
                "loss_given_default": round(lgd, 4),
                "expected_loss": round(expected_loss, 2),
                "credit_value_adjustment": round(cva, 2),
                "risk_level": self._determine_risk_level(pd, expected_loss),
                "model_timestamp": datetime.utcnow().isoformat(),
                "confidence_score": rating.get("confidence_score", 0.85)
            }
            
            # Store risk model results
            model_id = str(hash(f"{counterparty_id}_{datetime.utcnow()}"))
            self.risk_models[model_id] = risk_metrics
            
            logger.info(f"Credit risk model completed for counterparty {counterparty_id}")
            return risk_metrics
            
        except ValueError as e:
            logger.error(f"Credit risk model validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Credit risk model failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Credit risk model failed: {str(e)}")
    
    async def _initialize_counterparty_rating(self, counterparty_id: str):
        """Initialize counterparty rating"""
        # Simulate rating calculation (integrate with external rating agencies in production)
        ratings = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "CC", "C", "D"]
        rating_weights = [0.05, 0.10, 0.15, 0.20, 0.15, 0.15, 0.10, 0.05, 0.03, 0.02]
        
        # Weighted random selection
        selected_rating = random.choices(ratings, weights=rating_weights)[0]
        
        self.counterparty_ratings[counterparty_id] = {
            "rating": selected_rating,
            "confidence_score": random.uniform(0.7, 0.95),
            "last_updated": datetime.utcnow().isoformat(),
            "rating_agency": "internal_model"
        }
    
    def _calculate_pd(self, rating: str) -> float:
        """Calculate Probability of Default based on rating"""
        pd_mapping = {
            "AAA": 0.0001,
            "AA": 0.0005,
            "A": 0.001,
            "BBB": 0.005,
            "BB": 0.02,
            "B": 0.05,
            "CCC": 0.15,
            "CC": 0.30,
            "C": 0.50,
            "D": 1.00
        }
        return pd_mapping.get(rating, 0.01)
    
    def _calculate_lgd(self, asset_type: str) -> float:
        """Calculate Loss Given Default based on asset type"""
        lgd_mapping = {
            "energy": 0.40,
            "crude_oil": 0.35,
            "natural_gas": 0.45,
            "electricity": 0.50,
            "carbon_credit": 0.60,
            "coal": 0.30
        }
        return lgd_mapping.get(asset_type, 0.40)
    
    def _calculate_cva(self, notional: float, pd: float, lgd: float) -> float:
        """Calculate Credit Value Adjustment"""
        # Simplified CVA calculation
        return notional * pd * lgd * 0.1  # 10% discount factor
    
    def _determine_risk_level(self, pd: float, expected_loss: float) -> str:
        """Determine risk level based on PD and expected loss"""
        if pd < 0.001 and expected_loss < 1000:
            return RiskLevel.LOW.value
        elif pd < 0.01 and expected_loss < 10000:
            return RiskLevel.MEDIUM.value
        elif pd < 0.05 and expected_loss < 50000:
            return RiskLevel.HIGH.value
        else:
            return RiskLevel.CRITICAL.value
    
    async def counterparty_assessment(self, counterparty_id: str, assessment_data: Dict) -> Dict:
        """Comprehensive counterparty assessment"""
        try:
            if not counterparty_id:
                raise ValueError("Counterparty ID is required")
            
            # Financial metrics
            financial_metrics = {
                "revenue": assessment_data.get("revenue", 0),
                "assets": assessment_data.get("assets", 0),
                "liabilities": assessment_data.get("liabilities", 0),
                "debt_to_equity": assessment_data.get("debt_to_equity", 0),
                "current_ratio": assessment_data.get("current_ratio", 0),
                "profit_margin": assessment_data.get("profit_margin", 0)
            }
            
            # Calculate financial health score
            health_score = self._calculate_financial_health_score(financial_metrics)
            
            # Industry risk assessment
            industry_risk = self._assess_industry_risk(assessment_data.get("industry", "energy"))
            
            # Geographic risk
            geographic_risk = self._assess_geographic_risk(assessment_data.get("country", "US"))
            
            # Overall assessment
            overall_score = (health_score + industry_risk + geographic_risk) / 3
            
            assessment_result = {
                "counterparty_id": counterparty_id,
                "assessment_date": datetime.utcnow().isoformat(),
                "financial_health_score": round(health_score, 2),
                "industry_risk_score": round(industry_risk, 2),
                "geographic_risk_score": round(geographic_risk, 2),
                "overall_score": round(overall_score, 2),
                "risk_level": self._determine_risk_level_from_score(overall_score),
                "recommendation": self._get_recommendation(overall_score),
                "financial_metrics": financial_metrics,
                "assessment_confidence": random.uniform(0.8, 0.95)
            }
            
            logger.info(f"Counterparty assessment completed for {counterparty_id}")
            return assessment_result
            
        except ValueError as e:
            logger.error(f"Counterparty assessment validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Counterparty assessment failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Counterparty assessment failed: {str(e)}")
    
    def _calculate_financial_health_score(self, metrics: Dict) -> float:
        """Calculate financial health score (0-100)"""
        score = 50  # Base score
        
        # Debt to equity ratio (lower is better)
        debt_to_equity = metrics.get("debt_to_equity", 1.0)
        if debt_to_equity < 0.5:
            score += 20
        elif debt_to_equity < 1.0:
            score += 10
        elif debt_to_equity > 2.0:
            score -= 20
        
        # Current ratio (higher is better)
        current_ratio = metrics.get("current_ratio", 1.0)
        if current_ratio > 2.0:
            score += 15
        elif current_ratio > 1.5:
            score += 10
        elif current_ratio < 1.0:
            score -= 15
        
        # Profit margin (higher is better)
        profit_margin = metrics.get("profit_margin", 0.0)
        if profit_margin > 0.15:
            score += 15
        elif profit_margin > 0.10:
            score += 10
        elif profit_margin < 0.05:
            score -= 10
        
        return max(0, min(100, score))
    
    def _assess_industry_risk(self, industry: str) -> float:
        """Assess industry risk (0-100)"""
        industry_risks = {
            "energy": 60,
            "oil_gas": 70,
            "renewable_energy": 40,
            "utilities": 30,
            "mining": 80,
            "agriculture": 50,
            "technology": 20
        }
        return industry_risks.get(industry, 50)
    
    def _assess_geographic_risk(self, country: str) -> float:
        """Assess geographic risk (0-100)"""
        country_risks = {
            "US": 20,
            "UK": 25,
            "Germany": 30,
            "Japan": 35,
            "China": 60,
            "India": 70,
            "Brazil": 65,
            "Russia": 80
        }
        return country_risks.get(country, 50)
    
    def _determine_risk_level_from_score(self, score: float) -> str:
        """Determine risk level from assessment score"""
        if score >= 80:
            return RiskLevel.LOW.value
        elif score >= 60:
            return RiskLevel.MEDIUM.value
        elif score >= 40:
            return RiskLevel.HIGH.value
        else:
            return RiskLevel.CRITICAL.value
    
    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on assessment score"""
        if score >= 80:
            return "Approve with standard terms"
        elif score >= 60:
            return "Approve with enhanced monitoring"
        elif score >= 40:
            return "Approve with collateral requirements"
        else:
            return "Reject or require significant collateral"
    
    def stress_testing(self, scenarios: List[Dict]) -> Dict:
        """Multithreaded stress testing for multiple scenarios"""
        try:
            if not scenarios:
                raise ValueError("At least one stress test scenario is required")
            
            def run_stress_test(scenario):
                """Run individual stress test scenario"""
                try:
                    scenario_type = scenario.get("type", "market_crash")
                    portfolio_value = scenario.get("portfolio_value", 1000000)
                    shock_magnitude = scenario.get("shock_magnitude", 0.2)
                    
                    # Calculate stress test impact
                    if scenario_type == "market_crash":
                        impact = portfolio_value * shock_magnitude * -1
                    elif scenario_type == "interest_rate_shock":
                        impact = portfolio_value * shock_magnitude * 0.5
                    elif scenario_type == "commodity_price_shock":
                        impact = portfolio_value * shock_magnitude * -0.8
                    elif scenario_type == "liquidity_crisis":
                        impact = portfolio_value * shock_magnitude * -0.3
                    elif scenario_type == "counterparty_default":
                        impact = portfolio_value * shock_magnitude * -0.6
                    else:
                        impact = portfolio_value * shock_magnitude * -0.5
                    
                    return {
                        "scenario_type": scenario_type,
                        "portfolio_value": portfolio_value,
                        "shock_magnitude": shock_magnitude,
                        "impact": round(impact, 2),
                        "impact_percent": round((impact / portfolio_value) * 100, 2),
                        "var_95": round(impact * 1.65, 2),  # 95% VaR
                        "var_99": round(impact * 2.33, 2),  # 99% VaR
                        "scenario_id": str(hash(f"{scenario_type}_{datetime.utcnow()}"))
                    }
                    
                except Exception as e:
                    logger.error(f"Stress test scenario failed: {str(e)}")
                    return {
                        "scenario_type": scenario.get("type", "unknown"),
                        "error": str(e),
                        "impact": 0
                    }
            
            # Run stress tests in parallel
            futures = [self.executor.submit(run_stress_test, scenario) for scenario in scenarios]
            results = [future.result(timeout=30) for future in futures]
            
            # Calculate aggregate metrics
            total_impact = sum(r.get("impact", 0) for r in results)
            max_impact = max(r.get("impact", 0) for r in results)
            avg_impact = total_impact / len(results) if results else 0
            
            stress_test_summary = {
                "test_id": str(uuid4()),
                "test_date": datetime.utcnow().isoformat(),
                "scenarios_tested": len(scenarios),
                "results": results,
                "aggregate_metrics": {
                    "total_impact": round(total_impact, 2),
                    "max_impact": round(max_impact, 2),
                    "average_impact": round(avg_impact, 2),
                    "worst_case_scenario": max(results, key=lambda x: abs(x.get("impact", 0))),
                    "portfolio_var_95": round(max_impact * 1.65, 2),
                    "portfolio_var_99": round(max_impact * 2.33, 2)
                },
                "recommendations": self._generate_stress_test_recommendations(results)
            }
            
            # Store results
            self.stress_test_results[stress_test_summary["test_id"]] = stress_test_summary
            
            logger.info(f"Stress testing completed for {len(scenarios)} scenarios")
            return stress_test_summary
            
        except ValueError as e:
            logger.error(f"Stress testing validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Stress testing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Stress testing failed: {str(e)}")
    
    def _generate_stress_test_recommendations(self, results: List[Dict]) -> List[str]:
        """Generate recommendations based on stress test results"""
        recommendations = []
        
        max_impact = max(r.get("impact", 0) for r in results)
        
        if abs(max_impact) > 500000:  # $500K threshold
            recommendations.append("Consider reducing portfolio concentration")
        
        if any(r.get("impact_percent", 0) < -20 for r in results):
            recommendations.append("Implement additional hedging strategies")
        
        if any(r.get("scenario_type") == "counterparty_default" and r.get("impact", 0) < -100000 for r in results):
            recommendations.append("Review counterparty exposure limits")
        
        if len([r for r in results if r.get("impact", 0) < -50000]) > len(results) * 0.5:
            recommendations.append("Consider portfolio diversification")
        
        if not recommendations:
            recommendations.append("Portfolio appears resilient to stress scenarios")
        
        return recommendations
    
    async def get_risk_analytics(self, organization_id: str) -> Dict:
        """Get comprehensive risk analytics"""
        try:
            # Filter risk models by organization (simplified for demo)
            org_risk_models = list(self.risk_models.values())
            
            # Calculate risk metrics
            total_exposure = sum(rm.get("exposure_at_default", 0) for rm in org_risk_models)
            total_expected_loss = sum(rm.get("expected_loss", 0) for rm in org_risk_models)
            total_cva = sum(rm.get("credit_value_adjustment", 0) for rm in org_risk_models)
            
            # Risk level distribution
            risk_levels = {}
            for rm in org_risk_models:
                risk_level = rm.get("risk_level", "unknown")
                risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
            
            # Counterparty concentration
            counterparty_exposure = {}
            for rm in org_risk_models:
                cp_id = rm.get("counterparty_id", "unknown")
                exposure = rm.get("exposure_at_default", 0)
                counterparty_exposure[cp_id] = counterparty_exposure.get(cp_id, 0) + exposure
            
            # Top counterparties by exposure
            top_counterparties = sorted(
                counterparty_exposure.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            analytics = {
                "organization_id": organization_id,
                "total_exposure": round(total_exposure, 2),
                "total_expected_loss": round(total_expected_loss, 2),
                "total_cva": round(total_cva, 2),
                "risk_level_distribution": risk_levels,
                "top_counterparties": [
                    {"counterparty_id": cp_id, "exposure": round(exposure, 2)} 
                    for cp_id, exposure in top_counterparties
                ],
                "average_pd": round(
                    sum(rm.get("probability_of_default", 0) for rm in org_risk_models) / 
                    max(len(org_risk_models), 1), 4
                ),
                "average_lgd": round(
                    sum(rm.get("loss_given_default", 0) for rm in org_risk_models) / 
                    max(len(org_risk_models), 1), 4
                ),
                "risk_concentration": round(
                    max(counterparty_exposure.values()) / max(total_exposure, 1), 4
                ),
                "analytics_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Risk analytics generated for organization {organization_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Risk analytics generation failed for {organization_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Risk analytics generation failed: {str(e)}")
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.executor.shutdown(wait=True)
            logger.info("Advanced risk management cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
