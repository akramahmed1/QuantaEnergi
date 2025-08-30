import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog
from ..core.config import settings
from ..services.forecasting_service import forecasting_service

logger = structlog.get_logger()

class GenerativeAIService:
    """Generative AI service for scenario simulation and market analysis"""
    
    def __init__(self):
        self.grok_api_key = settings.GROK_API_KEY
        self.session = None
        self.scenario_templates = self._load_scenario_templates()
        
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    def _load_scenario_templates(self) -> Dict[str, Any]:
        """Load predefined scenario templates"""
        return {
            "geopolitical_event": {
                "name": "Geopolitical Event Impact",
                "description": "Simulate market impact of geopolitical events",
                "parameters": ["region", "event_type", "severity", "commodity"],
                "examples": [
                    "Middle East conflict affecting oil supply",
                    "Trade war between major economies",
                    "Sanctions on energy-producing nations"
                ]
            },
            "natural_disaster": {
                "name": "Natural Disaster Impact",
                "description": "Simulate market impact of natural disasters",
                "parameters": ["disaster_type", "affected_region", "commodity", "duration"],
                "examples": [
                    "Hurricane affecting Gulf Coast refineries",
                    "Earthquake disrupting pipeline infrastructure",
                    "Drought affecting hydroelectric generation"
                ]
            },
            "regulatory_change": {
                "name": "Regulatory Change Impact",
                "description": "Simulate market impact of regulatory changes",
                "parameters": ["regulation_type", "affected_sector", "implementation_timeline"],
                "examples": [
                    "Carbon tax implementation",
                    "Renewable energy mandates",
                    "Emissions trading schemes"
                ]
            },
            "technological_breakthrough": {
                "name": "Technological Breakthrough",
                "description": "Simulate market impact of technological advances",
                "parameters": ["technology_type", "affected_commodity", "adoption_rate"],
                "examples": [
                    "Battery storage breakthrough",
                    "Fusion power development",
                    "Hydrogen fuel cell advancement"
                ]
            },
            "economic_recession": {
                "name": "Economic Recession",
                "description": "Simulate market impact of economic downturns",
                "parameters": ["recession_severity", "duration", "affected_regions"],
                "examples": [
                    "Global economic slowdown",
                    "Regional financial crisis",
                    "Inflationary pressure scenarios"
                ]
            }
        }
    
    async def simulate_scenario(self, scenario_params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a market scenario using generative AI"""
        try:
            scenario_type = scenario_params.get("scenario_type", "geopolitical_event")
            commodity = scenario_params.get("commodity", "crude_oil")
            region = scenario_params.get("region", "global")
            duration_days = scenario_params.get("duration_days", 30)
            
            # Generate scenario narrative using Grok API or fallback
            scenario_narrative = await self._generate_scenario_narrative(scenario_params)
            
            # Get base forecast data
            base_forecast = forecasting_service.forecast_future_consumption(commodity, duration_days)
            
            # Apply scenario modifications
            modified_forecast = self._apply_scenario_modifications(
                base_forecast, 
                scenario_params, 
                scenario_narrative
            )
            
            # Generate insights and recommendations
            insights = await self._generate_scenario_insights(
                scenario_params, 
                modified_forecast, 
                scenario_narrative
            )
            
            return {
                "scenario_id": f"scenario_{int(datetime.now().timestamp())}",
                "scenario_type": scenario_type,
                "parameters": scenario_params,
                "narrative": scenario_narrative,
                "base_forecast": base_forecast,
                "modified_forecast": modified_forecast,
                "insights": insights,
                "risk_assessment": self._assess_scenario_risk(scenario_params),
                "created_at": datetime.now().isoformat(),
                "simulation_duration_days": duration_days
            }
            
        except Exception as e:
            logger.error(f"Error simulating scenario: {e}")
            return {"error": str(e)}
    
    async def _generate_scenario_narrative(self, params: Dict[str, Any]) -> str:
        """Generate scenario narrative using Grok API or fallback"""
        try:
            if self.grok_api_key:
                return await self._call_grok_api(params)
            else:
                return self._generate_fallback_narrative(params)
                
        except Exception as e:
            logger.warning(f"Error generating narrative with Grok: {e}")
            return self._generate_fallback_narrative(params)
    
    async def _call_grok_api(self, params: Dict[str, Any]) -> str:
        """Call Grok API for scenario generation"""
        try:
            session = await self.get_session()
            
            # Construct prompt for Grok
            prompt = self._construct_grok_prompt(params)
            
            # This is a placeholder for actual Grok API call
            # In production, you would use the actual Grok API endpoint
            headers = {
                "Authorization": f"Bearer {self.grok_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": prompt,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            # Simulate API call for now
            await asyncio.sleep(0.1)  # Simulate API latency
            
            # Return generated narrative
            return self._generate_enhanced_narrative(params)
            
        except Exception as e:
            logger.error(f"Error calling Grok API: {e}")
            return self._generate_fallback_narrative(params)
    
    def _construct_grok_prompt(self, params: Dict[str, Any]) -> str:
        """Construct prompt for Grok API"""
        scenario_type = params.get("scenario_type", "geopolitical_event")
        commodity = params.get("commodity", "crude_oil")
        region = params.get("region", "global")
        
        prompt = f"""
        As an energy market expert, simulate the impact of a {scenario_type} on {commodity} markets in the {region} region.
        
        Consider:
        - Supply and demand dynamics
        - Price volatility patterns
        - Market sentiment changes
        - Regulatory responses
        - Long-term market implications
        
        Provide a detailed narrative analysis with specific price projections and market behavior predictions.
        """
        
        return prompt.strip()
    
    def _generate_fallback_narrative(self, params: Dict[str, Any]) -> str:
        """Generate fallback narrative when Grok API is unavailable"""
        scenario_type = params.get("scenario_type", "geopolitical_event")
        commodity = params.get("commodity", "crude_oil")
        region = params.get("region", "global")
        severity = params.get("severity", "moderate")
        
        narratives = {
            "geopolitical_event": {
                "low": f"A minor {scenario_type} in {region} may cause temporary price fluctuations in {commodity} markets, with potential 5-10% price movements over the next 30 days.",
                "moderate": f"A {scenario_type} in {region} is expected to significantly impact {commodity} supply chains, potentially causing 15-25% price volatility and supply disruptions lasting 2-3 months.",
                "high": f"A major {scenario_type} in {region} could severely disrupt {commodity} markets, leading to 30-50% price spikes, supply shortages, and market instability lasting 6-12 months."
            },
            "natural_disaster": {
                "low": f"A {scenario_type} affecting {region} may temporarily impact {commodity} infrastructure, causing 3-8% price increases and minor supply disruptions.",
                "moderate": f"A {scenario_type} in {region} could significantly damage {commodity} facilities, leading to 10-20% price increases and supply constraints lasting 1-2 months.",
                "high": f"A catastrophic {scenario_type} in {region} may severely damage {commodity} infrastructure, causing 25-40% price spikes and major supply disruptions lasting 3-6 months."
            }
        }
        
        return narratives.get(scenario_type, {}).get(severity, "Market impact analysis unavailable.")
    
    def _generate_enhanced_narrative(self, params: Dict[str, Any]) -> str:
        """Generate enhanced narrative with more sophisticated analysis"""
        scenario_type = params.get("scenario_type", "geopolitical_event")
        commodity = params.get("commodity", "crude_oil")
        region = params.get("region", "global")
        severity = params.get("severity", "moderate")
        
        enhanced_narratives = {
            "geopolitical_event": f"""
            **Market Impact Analysis: {scenario_type.title()} in {region}**
            
            The {scenario_type} in {region} is expected to create significant market volatility in {commodity} markets. Based on historical precedent and current market conditions, we anticipate:
            
            **Immediate Impact (0-7 days):**
            - Initial price spike of 15-25% due to supply uncertainty
            - Increased trading volume and volatility
            - Risk premium expansion in forward contracts
            
            **Short-term Impact (1-4 weeks):**
            - Supply chain disruptions affecting 10-20% of regional capacity
            - Price stabilization at 8-15% above pre-event levels
            - Increased demand for alternative supply sources
            
            **Medium-term Impact (1-3 months):**
            - Gradual supply recovery as alternative routes are established
            - Price normalization with 5-10% premium remaining
            - Market structure adjustments to new risk factors
            
            **Risk Factors:**
            - Escalation potential: High
            - Supply recovery timeline: 2-3 months
            - Market sentiment impact: Significant
            """,
            
            "natural_disaster": f"""
            **Market Impact Analysis: {scenario_type.title()} in {region}**
            
            The {scenario_type} affecting {region} has created immediate infrastructure challenges for {commodity} markets. Our analysis indicates:
            
            **Infrastructure Impact:**
            - Direct facility damage: 15-30% of regional capacity
            - Transportation disruptions: 20-35% of supply routes affected
            - Recovery timeline: 3-6 months for full restoration
            
            **Price Dynamics:**
            - Initial price reaction: 20-35% increase
            - Sustained premium: 10-20% for 2-4 months
            - Volatility spike: 2-3x normal levels
            
            **Supply Adjustments:**
            - Emergency reserves activation
            - Alternative supply source development
            - Demand response programs implementation
            """
        }
        
        return enhanced_narratives.get(scenario_type, self._generate_fallback_narrative(params))
    
    def _apply_scenario_modifications(self, base_forecast: Dict[str, Any], 
                                    scenario_params: Dict[str, Any], 
                                    narrative: str) -> Dict[str, Any]:
        """Apply scenario modifications to base forecast"""
        try:
            if "error" in base_forecast:
                return base_forecast
            
            modified_forecast = base_forecast.copy()
            scenario_type = scenario_params.get("scenario_type", "geopolitical_event")
            severity = scenario_params.get("severity", "moderate")
            
            # Calculate modification factors based on scenario type and severity
            modification_factors = self._calculate_modification_factors(scenario_type, severity)
            
            # Apply modifications to forecast data
            if "forecast_data" in modified_forecast:
                for forecast_point in modified_forecast["forecast_data"]:
                    base_price = forecast_point.get("predicted_price", 0)
                    
                    # Apply scenario-specific modifications
                    if scenario_type == "geopolitical_event":
                        # Geopolitical events typically increase volatility and prices
                        price_modifier = 1 + (modification_factors["price_impact"] * 
                                           (1 - forecast_point.get("forecast_horizon", 0) / 168))  # Decay over time
                        forecast_point["scenario_modified_price"] = round(base_price * price_modifier, 2)
                        forecast_point["scenario_confidence"] = max(0.3, forecast_point.get("confidence", 0.85) * 0.8)
                        
                    elif scenario_type == "natural_disaster":
                        # Natural disasters have immediate impact that gradually recovers
                        if forecast_point.get("forecast_horizon", 0) < 72:  # First 3 days
                            price_modifier = 1 + modification_factors["price_impact"]
                        else:
                            recovery_factor = min(1, (forecast_point.get("forecast_horizon", 0) - 72) / 1440)  # 60 days
                            price_modifier = 1 + (modification_factors["price_impact"] * (1 - recovery_factor))
                        
                        forecast_point["scenario_modified_price"] = round(base_price * price_modifier, 2)
                        forecast_point["scenario_confidence"] = max(0.4, forecast_point.get("confidence", 0.85) * 0.9)
                    
                    else:
                        # Default modification
                        forecast_point["scenario_modified_price"] = base_price
                        forecast_point["scenario_confidence"] = forecast_point.get("confidence", 0.85)
                    
                    # Add scenario metadata
                    forecast_point["scenario_type"] = scenario_type
                    forecast_point["scenario_severity"] = severity
                    forecast_point["modification_factor"] = round(price_modifier - 1, 3)
            
            # Add scenario summary
            modified_forecast["scenario_summary"] = {
                "type": scenario_type,
                "severity": severity,
                "price_impact_range": f"{modification_factors['price_impact']*100:.1f}%",
                "volatility_impact": f"{modification_factors['volatility_impact']*100:.1f}%",
                "recovery_timeline": modification_factors["recovery_timeline"],
                "narrative_summary": narrative[:200] + "..." if len(narrative) > 200 else narrative
            }
            
            return modified_forecast
            
        except Exception as e:
            logger.error(f"Error applying scenario modifications: {e}")
            return base_forecast
    
    def _calculate_modification_factors(self, scenario_type: str, severity: str) -> Dict[str, Any]:
        """Calculate modification factors for different scenarios and severities"""
        base_factors = {
            "geopolitical_event": {
                "price_impact": 0.15,
                "volatility_impact": 0.25,
                "recovery_timeline": "2-3 months"
            },
            "natural_disaster": {
                "price_impact": 0.25,
                "volatility_impact": 0.35,
                "recovery_timeline": "3-6 months"
            },
            "regulatory_change": {
                "price_impact": 0.10,
                "volatility_impact": 0.15,
                "recovery_timeline": "6-12 months"
            },
            "technological_breakthrough": {
                "price_impact": -0.15,  # Negative for price reduction
                "volatility_impact": 0.20,
                "recovery_timeline": "1-2 years"
            },
            "economic_recession": {
                "price_impact": -0.20,  # Negative for price reduction
                "volatility_impact": 0.30,
                "recovery_timeline": "1-3 years"
            }
        }
        
        severity_multipliers = {
            "low": 0.5,
            "moderate": 1.0,
            "high": 1.5
        }
        
        base = base_factors.get(scenario_type, {"price_impact": 0.10, "volatility_impact": 0.15, "recovery_timeline": "3-6 months"})
        multiplier = severity_multipliers.get(severity, 1.0)
        
        return {
            "price_impact": base["price_impact"] * multiplier,
            "volatility_impact": base["volatility_impact"] * multiplier,
            "recovery_timeline": base["recovery_timeline"]
        }
    
    async def _generate_scenario_insights(self, params: Dict[str, Any], 
                                        modified_forecast: Dict[str, Any], 
                                        narrative: str) -> Dict[str, Any]:
        """Generate insights and recommendations based on scenario simulation"""
        try:
            scenario_type = params.get("scenario_type", "geopolitical_event")
            commodity = params.get("commodity", "crude_oil")
            severity = params.get("severity", "moderate")
            
            insights = {
                "market_analysis": self._analyze_market_implications(params, modified_forecast),
                "risk_assessment": self._assess_scenario_risk(params),
                "trading_recommendations": self._generate_trading_recommendations(params, modified_forecast),
                "hedging_strategies": self._suggest_hedging_strategies(params, modified_forecast),
                "operational_impact": self._assess_operational_impact(params, modified_forecast)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating scenario insights: {e}")
            return {"error": str(e)}
    
    def _analyze_market_implications(self, params: Dict[str, Any], 
                                   modified_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market implications of the scenario"""
        scenario_type = params.get("scenario_type", "geopolitical_event")
        commodity = params.get("commodity", "crude_oil")
        
        implications = {
            "supply_chain_impact": "Moderate disruption expected",
            "demand_dynamics": "Demand likely to remain stable with price elasticity",
            "market_structure": "Increased volatility and risk premium",
            "regulatory_response": "Potential for emergency measures",
            "long_term_outlook": "Market fundamentals expected to normalize over time"
        }
        
        if scenario_type == "geopolitical_event":
            implications.update({
                "supply_chain_impact": "Significant disruption due to trade restrictions",
                "regulatory_response": "High probability of sanctions and trade barriers",
                "long_term_outlook": "Structural changes to global supply chains"
            })
        elif scenario_type == "natural_disaster":
            implications.update({
                "supply_chain_impact": "Physical infrastructure damage affecting production",
                "demand_dynamics": "Potential demand destruction in affected regions",
                "long_term_outlook": "Infrastructure rebuilding will drive demand recovery"
            })
        
        return implications
    
    def _assess_scenario_risk(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk level of the scenario"""
        scenario_type = params.get("scenario_type", "geopolitical_event")
        severity = params.get("severity", "moderate")
        
        risk_levels = {
            "geopolitical_event": {"low": "Low", "moderate": "Medium", "high": "High"},
            "natural_disaster": {"low": "Low", "moderate": "Medium", "high": "High"},
            "regulatory_change": {"low": "Low", "moderate": "Medium", "high": "Medium"},
            "technological_breakthrough": {"low": "Low", "moderate": "Low", "high": "Medium"},
            "economic_recession": {"low": "Medium", "moderate": "High", "high": "Very High"}
        }
        
        risk_level = risk_levels.get(scenario_type, {}).get(severity, "Medium")
        
        return {
            "overall_risk": risk_level,
            "market_risk": "High" if risk_level in ["High", "Very High"] else "Medium",
            "operational_risk": "Medium" if scenario_type in ["natural_disaster", "regulatory_change"] else "Low",
            "financial_risk": "High" if risk_level in ["High", "Very High"] else "Medium",
            "mitigation_priority": "Immediate" if risk_level in ["High", "Very High"] else "High"
        }
    
    def _generate_trading_recommendations(self, params: Dict[str, Any], 
                                        modified_forecast: Dict[str, Any]) -> List[str]:
        """Generate trading recommendations based on scenario"""
        scenario_type = params.get("scenario_type", "geopolitical_event")
        commodity = params.get("commodity", "crude_oil")
        
        recommendations = []
        
        if scenario_type == "geopolitical_event":
            recommendations.extend([
                "Consider long positions in {commodity} futures",
                "Implement volatility trading strategies",
                "Monitor geopolitical developments closely",
                "Diversify supply sources and contracts"
            ])
        elif scenario_type == "natural_disaster":
            recommendations.extend([
                "Short-term price spikes expected - consider options strategies",
                "Monitor infrastructure recovery timelines",
                "Evaluate alternative supply routes",
                "Consider demand destruction in affected regions"
            ])
        
        return recommendations
    
    def _suggest_hedging_strategies(self, params: Dict[str, Any], 
                                   modified_forecast: Dict[str, Any]) -> List[str]:
        """Suggest hedging strategies for the scenario"""
        scenario_type = params.get("scenario_type", "geopolitical_event")
        severity = params.get("severity", "moderate")
        
        strategies = []
        
        if severity in ["moderate", "high"]:
            strategies.extend([
                "Increase hedge ratios to 80-90%",
                "Extend hedge duration to 6-12 months",
                "Consider cross-commodity hedges",
                "Implement dynamic hedging programs"
            ])
        else:
            strategies.extend([
                "Maintain current hedge ratios",
                "Monitor scenario developments",
                "Prepare contingency hedging plans"
            ])
        
        return strategies
    
    def _assess_operational_impact(self, params: Dict[str, Any], 
                                  modified_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Assess operational impact of the scenario"""
        scenario_type = params.get("scenario_type", "geopolitical_event")
        severity = params.get("severity", "moderate")
        
        operational_impact = {
            "supply_chain": "Low impact expected",
            "logistics": "Minimal disruption",
            "storage": "Normal operations",
            "personnel": "No impact",
            "technology": "No impact"
        }
        
        if scenario_type == "geopolitical_event":
            operational_impact.update({
                "supply_chain": "High impact - trade restrictions expected",
                "logistics": "Moderate disruption - route changes required",
                "storage": "Increased demand for storage capacity"
            })
        elif scenario_type == "natural_disaster":
            operational_impact.update({
                "supply_chain": "High impact - infrastructure damage",
                "logistics": "High disruption - route closures",
                "storage": "Potential damage to storage facilities"
            })
        
        return operational_impact
    
    async def get_scenario_templates(self) -> Dict[str, Any]:
        """Get available scenario templates"""
        return {
            "templates": self.scenario_templates,
            "total_templates": len(self.scenario_templates),
            "timestamp": datetime.now().isoformat()
        }
    
    async def close(self):
        """Close the service"""
        if self.session and not self.session.closed:
            await self.session.close()

# Global instance
generative_ai_service = GenerativeAIService()
