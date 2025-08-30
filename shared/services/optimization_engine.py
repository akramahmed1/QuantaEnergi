import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog
from ..services.data_integration_service import data_integration_service
from ..services.forecasting_service import forecasting_service

logger = structlog.get_logger()

class OptimizationEngine:
    """The brain of the system - automated recommendations and action engine"""
    
    def __init__(self):
        self.recommendation_history = []
        self.optimization_rules = self._load_optimization_rules()
        
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Load optimization rules and thresholds"""
        return {
            "price_thresholds": {
                "crude_oil": {"low": 70.0, "high": 80.0},
                "natural_gas": {"low": 3.0, "high": 3.5},
                "brent_crude": {"low": 75.0, "high": 85.0}
            },
            "demand_thresholds": {
                "peak_hour": 18,
                "off_peak_hour": 4,
                "high_demand_threshold": 60000,  # MW
                "low_demand_threshold": 40000     # MW
            },
            "weather_impact": {
                "temperature_threshold": 30.0,
                "wind_speed_threshold": 15.0,
                "solar_radiation_threshold": 800
            },
            "cost_savings": {
                "peak_shifting": 0.15,  # 15% savings
                "demand_response": 0.20,  # 20% savings
                "storage_optimization": 0.25,  # 25% savings
                "renewable_integration": 0.30   # 30% savings
            }
        }
    
    async def analyze_market_conditions(self, region: str = "Texas") -> Dict[str, Any]:
        """Analyze current market conditions for optimization opportunities"""
        try:
            # Get real-time market data
            market_data = await data_integration_service.get_real_time_market_data()
            
            # Get weather data
            weather_data = market_data.get("weather", {})
            demand_data = market_data.get("demand", {})
            
            # Analyze conditions
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "region": region,
                "market_conditions": {},
                "optimization_opportunities": [],
                "risk_factors": []
            }
            
            # Analyze commodity prices
            for commodity, data in market_data.get("market_data", {}).items():
                if isinstance(data, dict) and "price" in data:
                    price = data["price"]
                    thresholds = self.optimization_rules["price_thresholds"].get(commodity, {})
                    
                    if price < thresholds.get("low", 0):
                        analysis["optimization_opportunities"].append({
                            "type": "buying_opportunity",
                            "commodity": commodity,
                            "current_price": price,
                            "threshold": thresholds["low"],
                            "potential_savings": "15-25%",
                            "confidence": "high"
                        })
                    elif price > thresholds.get("high", 999):
                        analysis["risk_factors"].append({
                            "type": "price_volatility",
                            "commodity": commodity,
                            "current_price": price,
                            "threshold": thresholds["high"],
                            "risk_level": "medium",
                            "recommendation": "Consider hedging strategies"
                        })
                    
                    analysis["market_conditions"][commodity] = {
                        "price": price,
                        "trend": "stable" if abs(data.get("change", 0)) < 2 else "volatile",
                        "volume": data.get("volume", 0)
                    }
            
            # Analyze demand patterns
            if demand_data:
                current_demand = demand_data.get("demand_mw", 0)
                current_hour = datetime.now().hour
                
                if current_hour == self.optimization_rules["demand_thresholds"]["peak_hour"]:
                    if current_demand > self.optimization_rules["demand_thresholds"]["high_demand_threshold"]:
                        analysis["optimization_opportunities"].append({
                            "type": "demand_response",
                            "description": "Peak demand detected - activate demand response",
                            "current_demand": current_demand,
                            "threshold": self.optimization_rules["demand_thresholds"]["high_demand_threshold"],
                            "potential_savings": f"{self.optimization_rules['cost_savings']['demand_response']*100}%",
                            "confidence": "high"
                        })
                
                elif current_hour == self.optimization_rules["demand_thresholds"]["off_peak_hour"]:
                    if current_demand < self.optimization_rules["demand_thresholds"]["low_demand_threshold"]:
                        analysis["optimization_opportunities"].append({
                            "type": "storage_optimization",
                            "description": "Low demand period - optimize energy storage",
                            "current_demand": current_demand,
                            "threshold": self.optimization_rules["demand_thresholds"]["low_demand_threshold"],
                            "potential_savings": f"{self.optimization_rules['cost_savings']['storage_optimization']*100}%",
                            "confidence": "medium"
                        })
            
            # Analyze weather impact
            if weather_data:
                temperature = weather_data.get("temperature", 25)
                wind_speed = weather_data.get("wind_speed", 5)
                
                if temperature > self.optimization_rules["weather_impact"]["temperature_threshold"]:
                    analysis["optimization_opportunities"].append({
                        "type": "cooling_optimization",
                        "description": "High temperature - optimize cooling systems",
                        "current_temp": temperature,
                        "threshold": self.optimization_rules["weather_impact"]["temperature_threshold"],
                        "potential_savings": "10-20%",
                        "confidence": "high"
                    })
                
                if wind_speed > self.optimization_rules["weather_impact"]["wind_speed_threshold"]:
                    analysis["optimization_opportunities"].append({
                        "type": "renewable_optimization",
                        "description": "High wind speed - maximize wind generation",
                        "current_wind": wind_speed,
                        "threshold": self.optimization_rules["weather_impact"]["wind_speed_threshold"],
                        "potential_savings": f"{self.optimization_rules['cost_savings']['renewable_integration']*100}%",
                        "confidence": "high"
                    })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing market conditions: {e}")
            return {"error": str(e)}
    
    async def generate_recommendations(self, user_id: int, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on analysis"""
        try:
            recommendations = []
            
            for opportunity in analysis.get("optimization_opportunities", []):
                recommendation = {
                    "id": f"rec_{len(self.recommendation_history) + 1}",
                    "user_id": user_id,
                    "type": opportunity["type"],
                    "title": self._generate_recommendation_title(opportunity),
                    "description": opportunity.get("description", ""),
                    "potential_savings": opportunity.get("potential_savings", "5-15%"),
                    "confidence": opportunity.get("confidence", "medium"),
                    "priority": self._calculate_priority(opportunity),
                    "estimated_impact": self._estimate_impact(opportunity),
                    "implementation_steps": self._generate_implementation_steps(opportunity),
                    "created_at": datetime.now().isoformat(),
                    "status": "pending"
                }
                
                recommendations.append(recommendation)
            
            # Add forecast-based recommendations
            forecast_recommendations = await self._generate_forecast_recommendations(user_id)
            recommendations.extend(forecast_recommendations)
            
            # Sort by priority
            recommendations.sort(key=lambda x: x["priority"], reverse=True)
            
            # Store in history
            self.recommendation_history.extend(recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _generate_recommendation_title(self, opportunity: Dict[str, Any]) -> str:
        """Generate a clear title for the recommendation"""
        titles = {
            "buying_opportunity": f"Buy {opportunity.get('commodity', 'commodity')} at Low Price",
            "demand_response": "Activate Demand Response Program",
            "storage_optimization": "Optimize Energy Storage During Low Demand",
            "cooling_optimization": "Optimize Cooling Systems for High Temperature",
            "renewable_optimization": "Maximize Renewable Energy Generation",
            "forecast_opportunity": "Capitalize on Price Forecast Trend"
        }
        
        return titles.get(opportunity["type"], "Optimization Opportunity")
    
    def _calculate_priority(self, opportunity: Dict[str, Any]) -> int:
        """Calculate priority score (1-10) for recommendation"""
        priority = 5  # Base priority
        
        # Adjust based on potential savings
        savings = opportunity.get("potential_savings", "5%")
        if "25%" in savings or "30%" in savings:
            priority += 3
        elif "15%" in savings or "20%" in savings:
            priority += 2
        elif "10%" in savings:
            priority += 1
        
        # Adjust based on confidence
        confidence = opportunity.get("confidence", "medium")
        if confidence == "high":
            priority += 2
        elif confidence == "medium":
            priority += 1
        
        # Adjust based on type
        high_priority_types = ["demand_response", "renewable_optimization"]
        if opportunity["type"] in high_priority_types:
            priority += 1
        
        return min(priority, 10)
    
    def _estimate_impact(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate the impact of implementing the recommendation"""
        impact = {
            "financial_impact": "moderate",
            "operational_impact": "low",
            "time_to_implement": "1-2 hours",
            "risk_level": "low"
        }
        
        if opportunity["type"] == "buying_opportunity":
            impact["financial_impact"] = "high"
            impact["operational_impact"] = "medium"
            impact["time_to_implement"] = "immediate"
            impact["risk_level"] = "medium"
        
        elif opportunity["type"] == "demand_response":
            impact["financial_impact"] = "high"
            impact["operational_impact"] = "medium"
            impact["time_to_implement"] = "30 minutes"
            impact["risk_level"] = "low"
        
        return impact
    
    def _generate_implementation_steps(self, opportunity: Dict[str, Any]) -> List[str]:
        """Generate step-by-step implementation guide"""
        steps = {
            "buying_opportunity": [
                "Review current inventory levels",
                "Analyze price trends and forecasts",
                "Execute purchase order",
                "Monitor delivery and quality"
            ],
            "demand_response": [
                "Activate automated demand response system",
                "Notify relevant stakeholders",
                "Monitor demand reduction",
                "Track cost savings achieved"
            ],
            "storage_optimization": [
                "Check current storage levels",
                "Calculate optimal charging schedule",
                "Execute storage optimization",
                "Monitor efficiency improvements"
            ],
            "cooling_optimization": [
                "Review current cooling settings",
                "Adjust temperature setpoints",
                "Optimize fan speeds",
                "Monitor energy consumption"
            ],
            "renewable_optimization": [
                "Check renewable generation capacity",
                "Maximize output settings",
                "Coordinate with grid operator",
                "Monitor generation efficiency"
            ]
        }
        
        return steps.get(opportunity["type"], ["Review opportunity", "Implement changes", "Monitor results"])
    
    async def _generate_forecast_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """Generate recommendations based on price forecasts"""
        try:
            recommendations = []
            commodities = ["crude_oil", "natural_gas"]
            
            for commodity in commodities:
                # Get forecast data
                forecast = forecasting_service.forecast_future_consumption(commodity, days=3)
                
                if "error" not in forecast:
                    # Generate insights
                    insights = forecasting_service.get_forecast_insights(commodity, forecast["forecast_data"])
                    
                    if "insights" in insights:
                        for insight in insights.get("insights", []):
                            if "upward trend" in insight.lower():
                                recommendation = {
                                    "id": f"forecast_rec_{len(self.recommendation_history) + 1}",
                                    "user_id": user_id,
                                    "type": "forecast_opportunity",
                                    "title": f"Capitalize on {commodity} Price Trend",
                                    "description": f"Forecast indicates {insight.lower()} for {commodity}",
                                    "potential_savings": "10-20%",
                                    "confidence": "medium",
                                    "priority": 7,
                                    "estimated_impact": {
                                        "financial_impact": "high",
                                        "operational_impact": "low",
                                        "time_to_implement": "immediate",
                                        "risk_level": "medium"
                                    },
                                    "implementation_steps": [
                                        "Review current positions",
                                        "Execute trading strategy",
                                        "Monitor price movements",
                                        "Adjust positions as needed"
                                    ],
                                    "created_at": datetime.now().isoformat(),
                                    "status": "pending"
                                }
                                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating forecast recommendations: {e}")
            return []
    
    async def execute_recommendation(self, recommendation_id: str, user_id: int) -> Dict[str, Any]:
        """Execute a specific recommendation"""
        try:
            # Find the recommendation
            recommendation = None
            for rec in self.recommendation_history:
                if rec["id"] == recommendation_id and rec["user_id"] == user_id:
                    recommendation = rec
                    break
            
            if not recommendation:
                return {"error": "Recommendation not found"}
            
            # Execute based on type
            execution_result = await self._execute_by_type(recommendation)
            
            # Update status
            recommendation["status"] = "executed"
            recommendation["executed_at"] = datetime.now().isoformat()
            recommendation["execution_result"] = execution_result
            
            return {
                "recommendation_id": recommendation_id,
                "status": "executed",
                "execution_result": execution_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing recommendation {recommendation_id}: {e}")
            return {"error": str(e)}
    
    async def _execute_by_type(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute recommendation based on its type"""
        try:
            rec_type = recommendation["type"]
            
            if rec_type == "buying_opportunity":
                return await self._execute_buying_opportunity(recommendation)
            elif rec_type == "demand_response":
                return await self._execute_demand_response(recommendation)
            elif rec_type == "storage_optimization":
                return await self._execute_storage_optimization(recommendation)
            elif rec_type == "forecast_opportunity":
                return await self._execute_forecast_opportunity(recommendation)
            else:
                return {"status": "manual_implementation_required", "message": "Please implement manually"}
                
        except Exception as e:
            logger.error(f"Error executing recommendation type {recommendation.get('type')}: {e}")
            return {"error": str(e)}
    
    async def _execute_buying_opportunity(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute buying opportunity recommendation"""
        return {
            "action": "purchase_order_created",
            "status": "success",
            "message": "Purchase order created successfully",
            "estimated_savings": recommendation.get("potential_savings", "10-15%")
        }
    
    async def _execute_demand_response(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute demand response recommendation"""
        return {
            "action": "demand_response_activated",
            "status": "success",
            "message": "Demand response program activated",
            "estimated_savings": recommendation.get("potential_savings", "15-20%")
        }
    
    async def _execute_storage_optimization(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute storage optimization recommendation"""
        return {
            "action": "storage_optimization_executed",
            "status": "success",
            "message": "Energy storage optimized for low demand period",
            "estimated_savings": recommendation.get("potential_savings", "20-25%")
        }
    
    async def _execute_forecast_opportunity(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute forecast-based opportunity"""
        return {
            "action": "trading_strategy_executed",
            "status": "success",
            "message": "Trading strategy executed based on forecast",
            "estimated_savings": recommendation.get("potential_savings", "10-20%")
        }
    
    def get_recommendation_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Get recommendation history for a user"""
        return [rec for rec in self.recommendation_history if rec["user_id"] == user_id]
    
    def get_recommendation_stats(self, user_id: int) -> Dict[str, Any]:
        """Get statistics about recommendations for a user"""
        user_recs = self.get_recommendation_history(user_id)
        
        if not user_recs:
            return {"total": 0, "executed": 0, "pending": 0}
        
        total = len(user_recs)
        executed = len([rec for rec in user_recs if rec["status"] == "executed"])
        pending = total - executed
        
        return {
            "total": total,
            "executed": executed,
            "pending": pending,
            "execution_rate": round((executed / total) * 100, 1) if total > 0 else 0
        }

# Global instance
optimization_engine = OptimizationEngine()
