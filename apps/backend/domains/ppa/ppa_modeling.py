"""
PPA Modeling Engine - Molecule-inspired arbitrage modeling
Advanced Power Purchase Agreement financial modeling and arbitrage calculations
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from scipy import stats
from scipy.optimize import minimize
import math

logger = logging.getLogger(__name__)

class PPAType(Enum):
    FIXED_PRICE = "fixed_price"
    INDEXED_PRICE = "indexed_price"
    HYBRID = "hybrid"
    VIRTUAL_PPA = "virtual_ppa"
    PHYSICAL_PPA = "physical_ppa"

class RiskProfile(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class PPAContract:
    """Power Purchase Agreement contract structure"""
    contract_id: str
    ppa_type: PPAType
    capacity_mw: float
    contract_duration_years: int
    start_date: datetime
    end_date: datetime
    fixed_price: Optional[float] = None
    indexed_price_formula: Optional[str] = None
    escalation_rate: float = 0.0
    availability_factor: float = 0.95
    degradation_rate: float = 0.005
    risk_profile: RiskProfile = RiskProfile.MEDIUM
    counterparty_rating: str = "BBB"
    credit_limit: float = 1000000.0

@dataclass
class MarketData:
    """Market data for PPA modeling"""
    electricity_prices: Dict[str, float]  # Hourly prices
    renewable_energy_credits: Dict[str, float]
    capacity_prices: Dict[str, float]
    fuel_prices: Dict[str, float]
    interest_rates: Dict[str, float]
    inflation_rates: Dict[str, float]
    weather_data: Dict[str, Any]
    transmission_costs: Dict[str, float]

@dataclass
class ArbitrageOpportunity:
    """Arbitrage opportunity structure"""
    opportunity_id: str
    asset_pair: Tuple[str, str]
    price_difference: float
    volume_available: float
    time_window: Tuple[datetime, datetime]
    risk_score: float
    expected_profit: float
    confidence_level: float

class PPAModelingEngine:
    """Main PPA modeling engine with arbitrage capabilities"""
    
    def __init__(self):
        self.contracts: Dict[str, PPAContract] = {}
        self.market_data: Optional[MarketData] = None
        self.risk_models = {}
        self.arbitrage_models = {}
        
    def create_ppa_model(self, ppa_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive PPA financial model"""
        try:
            contract = self._parse_contract_data(ppa_data)
            self.contracts[contract.contract_id] = contract
            
            # Calculate financial metrics
            npv = self._calculate_npv(contract)
            irr = self._calculate_irr(contract)
            payback_period = self._calculate_payback_period(contract)
            lcoe = self._calculate_lcoe(contract)
            
            # Risk analysis
            risk_metrics = self._assess_contract_risks(contract)
            
            # Arbitrage opportunities
            arbitrage_ops = self._identify_arbitrage_opportunities(contract)
            
            return {
                "contract_id": contract.contract_id,
                "financial_metrics": {
                    "npv": npv,
                    "irr": irr,
                    "payback_period": payback_period,
                    "lcoe": lcoe
                },
                "risk_metrics": risk_metrics,
                "arbitrage_opportunities": arbitrage_ops,
                "model_created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating PPA model: {str(e)}")
            raise
    
    def _parse_contract_data(self, ppa_data: Dict[str, Any]) -> PPAContract:
        """Parse PPA data into contract structure"""
        return PPAContract(
            contract_id=ppa_data.get("contract_id", f"PPA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            ppa_type=PPAType(ppa_data.get("ppa_type", "fixed_price")),
            capacity_mw=float(ppa_data.get("capacity_mw", 100.0)),
            contract_duration_years=int(ppa_data.get("contract_duration_years", 20)),
            start_date=datetime.fromisoformat(ppa_data.get("start_date", datetime.now().isoformat())),
            end_date=datetime.fromisoformat(ppa_data.get("end_date", (datetime.now() + timedelta(days=365*20)).isoformat())),
            fixed_price=ppa_data.get("fixed_price"),
            indexed_price_formula=ppa_data.get("indexed_price_formula"),
            escalation_rate=float(ppa_data.get("escalation_rate", 0.0)),
            availability_factor=float(ppa_data.get("availability_factor", 0.95)),
            degradation_rate=float(ppa_data.get("degradation_rate", 0.005)),
            risk_profile=RiskProfile(ppa_data.get("risk_profile", "medium")),
            counterparty_rating=ppa_data.get("counterparty_rating", "BBB"),
            credit_limit=float(ppa_data.get("credit_limit", 1000000.0))
        )
    
    def _calculate_npv(self, contract: PPAContract, discount_rate: float = 0.08) -> float:
        """Calculate Net Present Value of PPA contract"""
        try:
            years = contract.contract_duration_years
            annual_revenue = self._calculate_annual_revenue(contract)
            annual_costs = self._calculate_annual_costs(contract)
            
            npv = 0
            for year in range(1, years + 1):
                net_cash_flow = annual_revenue - annual_costs
                # Apply degradation
                net_cash_flow *= (1 - contract.degradation_rate) ** year
                # Apply escalation
                net_cash_flow *= (1 + contract.escalation_rate) ** year
                npv += net_cash_flow / ((1 + discount_rate) ** year)
            
            return npv
            
        except Exception as e:
            logger.error(f"Error calculating NPV: {str(e)}")
            return 0.0
    
    def _calculate_annual_revenue(self, contract: PPAContract) -> float:
        """Calculate annual revenue from PPA contract"""
        if contract.ppa_type == PPAType.FIXED_PRICE:
            return contract.capacity_mw * 8760 * contract.availability_factor * (contract.fixed_price or 0)
        else:
            # Use market price for indexed contracts
            market_price = 50.0  # Default market price $/MWh
            return contract.capacity_mw * 8760 * contract.availability_factor * market_price
    
    def _calculate_annual_costs(self, contract: PPAContract) -> float:
        """Calculate annual operational costs"""
        # O&M costs, insurance, taxes, etc.
        o_and_m_cost = contract.capacity_mw * 25000  # $25/kW/year
        insurance_cost = contract.capacity_mw * 5000  # $5/kW/year
        taxes = contract.capacity_mw * 10000  # $10/kW/year
        
        return o_and_m_cost + insurance_cost + taxes
    
    def _calculate_irr(self, contract: PPAContract) -> float:
        """Calculate Internal Rate of Return"""
        try:
            years = contract.contract_duration_years
            annual_revenue = self._calculate_annual_revenue(contract)
            annual_costs = self._calculate_annual_costs(contract)
            
            cash_flows = []
            for year in range(1, years + 1):
                net_cash_flow = annual_revenue - annual_costs
                net_cash_flow *= (1 - contract.degradation_rate) ** year
                net_cash_flow *= (1 + contract.escalation_rate) ** year
                cash_flows.append(net_cash_flow)
            
            # Use numerical method to find IRR
            def npv_function(rate):
                return sum(cf / ((1 + rate) ** (i + 1)) for i, cf in enumerate(cash_flows))
            
            # Find rate where NPV = 0
            result = minimize(lambda x: npv_function(x[0]) ** 2, [0.1], bounds=[(0.001, 0.5)])
            return result.x[0] if result.success else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating IRR: {str(e)}")
            return 0.0
    
    def _calculate_payback_period(self, contract: PPAContract) -> float:
        """Calculate payback period in years"""
        try:
            annual_revenue = self._calculate_annual_revenue(contract)
            annual_costs = self._calculate_annual_costs(contract)
            net_annual_cash_flow = annual_revenue - annual_costs
            
            # Assume initial investment is 10x annual costs
            initial_investment = annual_costs * 10
            
            if net_annual_cash_flow <= 0:
                return float('inf')
            
            payback_period = initial_investment / net_annual_cash_flow
            return min(payback_period, contract.contract_duration_years)
            
        except Exception as e:
            logger.error(f"Error calculating payback period: {str(e)}")
            return float('inf')
    
    def _calculate_lcoe(self, contract: PPAContract) -> float:
        """Calculate Levelized Cost of Energy"""
        try:
            years = contract.contract_duration_years
            annual_costs = self._calculate_annual_costs(contract)
            annual_generation = contract.capacity_mw * 8760 * contract.availability_factor
            
            total_costs = 0
            total_generation = 0
            
            for year in range(1, years + 1):
                year_costs = annual_costs * (1 + contract.escalation_rate) ** year
                year_generation = annual_generation * (1 - contract.degradation_rate) ** year
                
                total_costs += year_costs
                total_generation += year_generation
            
            return total_costs / total_generation if total_generation > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating LCOE: {str(e)}")
            return 0.0
    
    def _assess_contract_risks(self, contract: PPAContract) -> Dict[str, Any]:
        """Assess various risks in PPA contract"""
        risks = {}
        
        # Price risk
        if contract.ppa_type == PPAType.INDEXED_PRICE:
            risks["price_risk"] = "HIGH"
        else:
            risks["price_risk"] = "LOW"
        
        # Credit risk
        credit_risk_map = {"AAA": "LOW", "AA": "LOW", "A": "MEDIUM", "BBB": "MEDIUM", "BB": "HIGH", "B": "HIGH", "CCC": "VERY_HIGH"}
        risks["credit_risk"] = credit_risk_map.get(contract.counterparty_rating, "MEDIUM")
        
        # Operational risk
        if contract.availability_factor < 0.9:
            risks["operational_risk"] = "HIGH"
        else:
            risks["operational_risk"] = "LOW"
        
        # Regulatory risk
        risks["regulatory_risk"] = "MEDIUM"
        
        # Overall risk score
        risk_scores = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "VERY_HIGH": 4}
        overall_score = sum(risk_scores.get(risk, 2) for risk in risks.values()) / len(risks)
        risks["overall_risk_score"] = overall_score
        
        return risks
    
    def _identify_arbitrage_opportunities(self, contract: PPAContract) -> List[Dict[str, Any]]:
        """Identify arbitrage opportunities for PPA contract"""
        opportunities = []
        
        # Time arbitrage (peak vs off-peak pricing)
        peak_price = 80.0  # $/MWh
        off_peak_price = 30.0  # $/MWh
        price_difference = peak_price - off_peak_price
        
        if price_difference > 20:  # Arbitrage threshold
            opportunities.append({
                "type": "time_arbitrage",
                "description": "Peak vs Off-peak pricing arbitrage",
                "price_difference": price_difference,
                "expected_profit": price_difference * contract.capacity_mw * 1000,  # Per MWh
                "confidence": 0.8
            })
        
        # Geographic arbitrage
        region_a_price = 45.0
        region_b_price = 55.0
        geo_arbitrage = abs(region_a_price - region_b_price)
        
        if geo_arbitrage > 15:
            opportunities.append({
                "type": "geographic_arbitrage",
                "description": "Cross-regional price arbitrage",
                "price_difference": geo_arbitrage,
                "expected_profit": geo_arbitrage * contract.capacity_mw * 1000,
                "confidence": 0.7
            })
        
        return opportunities

class PPAArbitrageCalculator:
    """Specialized calculator for PPA arbitrage opportunities"""
    
    def __init__(self):
        self.market_data = {}
        self.arbitrage_threshold = 10.0  # $/MWh
        
    def calculate_arbitrage(self, ppa_params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate arbitrage opportunities for PPA parameters"""
        try:
            contract_capacity = float(ppa_params.get("capacity_mw", 100.0))
            market_prices = ppa_params.get("market_prices", {})
            ppa_price = float(ppa_params.get("ppa_price", 50.0))
            
            arbitrage_opportunities = []
            
            # Market vs PPA arbitrage
            for hour, market_price in market_prices.items():
                price_difference = market_price - ppa_price
                if abs(price_difference) > self.arbitrage_threshold:
                    arbitrage_opportunities.append({
                        "hour": hour,
                        "market_price": market_price,
                        "ppa_price": ppa_price,
                        "price_difference": price_difference,
                        "arbitrage_profit": price_difference * contract_capacity,
                        "arbitrage_type": "sell_to_market" if price_difference > 0 else "buy_from_market"
                    })
            
            # Calculate total arbitrage potential
            total_arbitrage = sum(abs(op["arbitrage_profit"]) for op in arbitrage_opportunities)
            
            return {
                "arbitrage_opportunities": arbitrage_opportunities,
                "total_arbitrage_potential": total_arbitrage,
                "average_arbitrage_per_mwh": total_arbitrage / (contract_capacity * len(arbitrage_opportunities)) if arbitrage_opportunities else 0,
                "arbitrage_frequency": len(arbitrage_opportunities),
                "confidence_score": self._calculate_confidence_score(arbitrage_opportunities)
            }
            
        except Exception as e:
            logger.error(f"Error calculating PPA arbitrage: {str(e)}")
            raise
    
    def _calculate_confidence_score(self, opportunities: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for arbitrage opportunities"""
        if not opportunities:
            return 0.0
        
        # Base confidence on price difference magnitude and frequency
        avg_price_diff = np.mean([abs(op["price_difference"]) for op in opportunities])
        frequency_score = min(len(opportunities) / 100, 1.0)  # Normalize to 1.0
        
        confidence = (avg_price_diff / 50.0) * frequency_score  # Normalize price difference
        return min(confidence, 1.0)

class PPARiskAssessor:
    """Risk assessment engine for PPA contracts"""
    
    def __init__(self):
        self.risk_models = {}
        self.scenario_models = {}
        
    def assess_risks(self, ppa_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive risk assessment for PPA contract"""
        try:
            contract = PPAContract(**ppa_data)
            
            risks = {}
            
            # Price volatility risk
            risks["price_volatility"] = self._assess_price_volatility_risk(contract)
            
            # Credit risk
            risks["credit_risk"] = self._assess_credit_risk(contract)
            
            # Operational risk
            risks["operational_risk"] = self._assess_operational_risk(contract)
            
            # Regulatory risk
            risks["regulatory_risk"] = self._assess_regulatory_risk(contract)
            
            # Weather risk
            risks["weather_risk"] = self._assess_weather_risk(contract)
            
            # Technology risk
            risks["technology_risk"] = self._assess_technology_risk(contract)
            
            # Calculate overall risk score
            risk_scores = [risk["score"] for risk in risks.values() if isinstance(risk, dict) and "score" in risk]
            risks["overall_risk_score"] = np.mean(risk_scores) if risk_scores else 0.0
            
            return risks
            
        except Exception as e:
            logger.error(f"Error assessing PPA risks: {str(e)}")
            raise
    
    def _assess_price_volatility_risk(self, contract: PPAContract) -> Dict[str, Any]:
        """Assess price volatility risk"""
        if contract.ppa_type == PPAType.FIXED_PRICE:
            return {"score": 1.0, "level": "LOW", "description": "Fixed price provides price certainty"}
        else:
            return {"score": 3.0, "level": "HIGH", "description": "Indexed pricing exposes to market volatility"}
    
    def _assess_credit_risk(self, contract: PPAContract) -> Dict[str, Any]:
        """Assess counterparty credit risk"""
        credit_scores = {"AAA": 1.0, "AA": 1.5, "A": 2.0, "BBB": 2.5, "BB": 3.5, "B": 4.0, "CCC": 5.0}
        score = credit_scores.get(contract.counterparty_rating, 3.0)
        
        levels = {1.0: "LOW", 2.0: "MEDIUM", 3.0: "HIGH", 4.0: "VERY_HIGH", 5.0: "EXTREME"}
        level = levels.get(score, "MEDIUM")
        
        return {"score": score, "level": level, "description": f"Counterparty rating: {contract.counterparty_rating}"}
    
    def _assess_operational_risk(self, contract: PPAContract) -> Dict[str, Any]:
        """Assess operational risk"""
        if contract.availability_factor >= 0.95:
            return {"score": 1.0, "level": "LOW", "description": "High availability factor"}
        elif contract.availability_factor >= 0.90:
            return {"score": 2.0, "level": "MEDIUM", "description": "Moderate availability factor"}
        else:
            return {"score": 3.0, "level": "HIGH", "description": "Low availability factor"}
    
    def _assess_regulatory_risk(self, contract: PPAContract) -> Dict[str, Any]:
        """Assess regulatory risk"""
        # This would typically involve analysis of regulatory environment
        return {"score": 2.0, "level": "MEDIUM", "description": "Standard regulatory risk"}
    
    def _assess_weather_risk(self, contract: PPAContract) -> Dict[str, Any]:
        """Assess weather-related risk"""
        # This would involve analysis of historical weather patterns
        return {"score": 2.5, "level": "MEDIUM", "description": "Weather variability risk"}
    
    def _assess_technology_risk(self, contract: PPAContract) -> Dict[str, Any]:
        """Assess technology risk"""
        # This would involve analysis of technology maturity and degradation
        return {"score": 2.0, "level": "MEDIUM", "description": "Standard technology risk"}

class PPADCFValuation:
    """DCF (Discounted Cash Flow) valuation engine for PPA contracts"""
    
    def __init__(self):
        self.default_discount_rate = 0.08
        self.inflation_rate = 0.025
        
    def calculate_dcf(self, valuation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate DCF valuation for PPA contract"""
        try:
            contract_data = valuation_data.get("contract_data", {})
            discount_rate = valuation_data.get("discount_rate", self.default_discount_rate)
            
            contract = PPAContract(**contract_data)
            
            # Calculate cash flows for each year
            cash_flows = []
            for year in range(1, contract.contract_duration_years + 1):
                revenue = self._calculate_year_revenue(contract, year)
                costs = self._calculate_year_costs(contract, year)
                cash_flow = revenue - costs
                cash_flows.append(cash_flow)
            
            # Calculate NPV
            npv = sum(cf / ((1 + discount_rate) ** (i + 1)) for i, cf in enumerate(cash_flows))
            
            # Calculate other metrics
            total_revenue = sum(cash_flows)
            payback_period = self._calculate_payback_period(cash_flows)
            
            return {
                "npv": npv,
                "total_revenue": total_revenue,
                "payback_period": payback_period,
                "discount_rate": discount_rate,
                "annual_cash_flows": cash_flows,
                "valuation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating DCF valuation: {str(e)}")
            raise
    
    def _calculate_year_revenue(self, contract: PPAContract, year: int) -> float:
        """Calculate revenue for a specific year"""
        base_revenue = contract.capacity_mw * 8760 * contract.availability_factor * (contract.fixed_price or 50.0)
        
        # Apply degradation
        degradation_factor = (1 - contract.degradation_rate) ** year
        
        # Apply escalation
        escalation_factor = (1 + contract.escalation_rate) ** year
        
        return base_revenue * degradation_factor * escalation_factor
    
    def _calculate_year_costs(self, contract: PPAContract, year: int) -> float:
        """Calculate costs for a specific year"""
        base_costs = contract.capacity_mw * 40000  # $40/kW/year total costs
        
        # Apply escalation
        escalation_factor = (1 + contract.escalation_rate) ** year
        
        return base_costs * escalation_factor
    
    def _calculate_payback_period(self, cash_flows: List[float]) -> float:
        """Calculate payback period from cash flows"""
        cumulative_cash_flow = 0
        initial_investment = abs(cash_flows[0]) * 10  # Assume 10x first year costs as investment
        
        for i, cash_flow in enumerate(cash_flows):
            cumulative_cash_flow += cash_flow
            if cumulative_cash_flow >= initial_investment:
                return i + 1
        
        return float('inf')

class PPASensitivityAnalyzer:
    """Sensitivity analysis engine for PPA parameters"""
    
    def __init__(self):
        self.default_sensitivity_range = 0.2  # ±20%
        
    def analyze_sensitivity(self, sensitivity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform sensitivity analysis on PPA parameters"""
        try:
            base_params = sensitivity_data.get("base_parameters", {})
            sensitivity_range = sensitivity_data.get("sensitivity_range", self.default_sensitivity_range)
            
            # Parameters to analyze
            parameters = ["ppa_price", "capacity_mw", "availability_factor", "escalation_rate", "degradation_rate"]
            
            sensitivity_results = {}
            
            for param in parameters:
                if param in base_params:
                    sensitivity_results[param] = self._analyze_parameter_sensitivity(
                        param, base_params, sensitivity_range
                    )
            
            return {
                "sensitivity_analysis": sensitivity_results,
                "analysis_date": datetime.now().isoformat(),
                "sensitivity_range": sensitivity_range
            }
            
        except Exception as e:
            logger.error(f"Error performing sensitivity analysis: {str(e)}")
            raise
    
    def _analyze_parameter_sensitivity(self, param: str, base_params: Dict[str, Any], sensitivity_range: float) -> Dict[str, Any]:
        """Analyze sensitivity of a specific parameter"""
        base_value = base_params[param]
        
        # Test variations
        variations = [-sensitivity_range, -sensitivity_range/2, 0, sensitivity_range/2, sensitivity_range]
        
        results = []
        for variation in variations:
            test_params = base_params.copy()
            test_params[param] = base_value * (1 + variation)
            
            # Calculate NPV for this variation (simplified)
            npv = self._calculate_simple_npv(test_params)
            
            results.append({
                "variation": variation,
                "value": test_params[param],
                "npv": npv,
                "npv_change": npv - self._calculate_simple_npv(base_params)
            })
        
        return {
            "parameter": param,
            "base_value": base_value,
            "variations": results,
            "sensitivity_score": self._calculate_sensitivity_score(results)
        }
    
    def _calculate_simple_npv(self, params: Dict[str, Any]) -> float:
        """Calculate simplified NPV for sensitivity analysis"""
        try:
            capacity = float(params.get("capacity_mw", 100.0))
            price = float(params.get("ppa_price", 50.0))
            availability = float(params.get("availability_factor", 0.95))
            escalation = float(params.get("escalation_rate", 0.0))
            degradation = float(params.get("degradation_rate", 0.005))
            duration = int(params.get("contract_duration_years", 20))
            discount_rate = 0.08
            
            npv = 0
            for year in range(1, duration + 1):
                revenue = capacity * 8760 * availability * price
                costs = capacity * 40000  # Fixed cost assumption
                
                # Apply degradation and escalation
                revenue *= (1 - degradation) ** year * (1 + escalation) ** year
                costs *= (1 + escalation) ** year
                
                cash_flow = revenue - costs
                npv += cash_flow / ((1 + discount_rate) ** year)
            
            return npv
            
        except Exception as e:
            logger.error(f"Error calculating simple NPV: {str(e)}")
            return 0.0
    
    def _calculate_sensitivity_score(self, results: List[Dict[str, Any]]) -> float:
        """Calculate sensitivity score based on NPV variations"""
        if not results:
            return 0.0
        
        npv_changes = [result["npv_change"] for result in results]
        max_change = max(abs(change) for change in npv_changes)
        
        # Normalize sensitivity score (0-1 scale)
        return min(max_change / 1000000, 1.0)  # Assume 1M as high sensitivity threshold
