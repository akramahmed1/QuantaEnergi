"""
Risk Manager Service for Trade Risk Assessment
Handles trade risk evaluation, limits checking, and risk metrics calculation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import math

logger = logging.getLogger(__name__)

class RiskManager:
    """Risk management service for trade risk assessment"""
    
    def __init__(self):
        # Risk limits and thresholds
        self.max_trade_size = 10000000  # $10M maximum trade size
        self.max_daily_exposure = 100000000  # $100M maximum daily exposure
        self.max_counterparty_exposure = 50000000  # $50M maximum per counterparty
        self.max_commodity_concentration = 0.30  # 30% maximum commodity concentration
        
        # Risk scoring parameters
        self.risk_weights = {
            "size": 0.3,
            "volatility": 0.25,
            "concentration": 0.2,
            "counterparty": 0.15,
            "liquidity": 0.1
        }
        
        # Commodity volatility factors (simplified)
        self.commodity_volatility = {
            "crude_oil": 0.35,
            "natural_gas": 0.45,
            "electricity": 0.60,
            "renewables": 0.25,
            "carbon_credits": 0.40,
            "lng": 0.30,
            "lpg": 0.35,
            "coal": 0.30,
            "uranium": 0.50,
            "biofuels": 0.40
        }
        
        # Counterparty risk ratings
        self.counterparty_ratings = {
            "A": 0.1,  # Low risk
            "B": 0.3,  # Medium risk
            "C": 0.6,  # High risk
            "D": 1.0   # Very high risk
        }
    
    async def assess_trade_risk(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess risk for a specific trade
        
        Args:
            trade_data: Trade information including size, commodity, counterparty
            
        Returns:
            Dict with risk assessment results
        """
        try:
            # Extract trade parameters
            trade_size = trade_data.get("quantity", 0) * trade_data.get("price", 0)
            commodity = trade_data.get("commodity", "unknown")
            counterparty = trade_data.get("counterparty", "unknown")
            
            # Calculate individual risk factors
            size_risk = self._calculate_size_risk(trade_size)
            volatility_risk = self._calculate_volatility_risk(commodity)
            concentration_risk = self._calculate_concentration_risk(trade_data)
            counterparty_risk = self._calculate_counterparty_risk(counterparty)
            liquidity_risk = self._calculate_liquidity_risk(commodity)
            
            # Calculate composite risk score
            risk_score = (
                size_risk * self.risk_weights["size"] +
                volatility_risk * self.risk_weights["volatility"] +
                concentration_risk * self.risk_weights["concentration"] +
                counterparty_risk * self.risk_weights["counterparty"] +
                liquidity_risk * self.risk_weights["liquidity"]
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Check risk limits
            limit_checks = self._check_risk_limits(trade_data)
            
            return {
                "risk_score": round(risk_score, 3),
                "risk_level": risk_level,
                "risk_factors": {
                    "size_risk": round(size_risk, 3),
                    "volatility_risk": round(volatility_risk, 3),
                    "concentration_risk": round(concentration_risk, 3),
                    "counterparty_risk": round(counterparty_risk, 3),
                    "liquidity_risk": round(liquidity_risk, 3)
                },
                "limit_checks": limit_checks,
                "recommendations": self._generate_risk_recommendations(risk_level, limit_checks),
                "assessed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assessing trade risk: {e}")
            return {
                "risk_score": 1.0,
                "risk_level": "high",
                "risk_factors": {},
                "limit_checks": {"error": str(e)},
                "recommendations": ["Manual risk review required"],
                "assessed_at": datetime.utcnow().isoformat()
            }
    
    def _calculate_size_risk(self, trade_size: float) -> float:
        """Calculate size-based risk factor"""
        if trade_size <= 0:
            return 0.0
        
        # Normalize size risk (0 = no risk, 1 = maximum risk)
        size_risk = min(trade_size / self.max_trade_size, 1.0)
        
        # Apply non-linear scaling for very large trades
        if size_risk > 0.8:
            size_risk = 0.8 + (size_risk - 0.8) * 2  # Accelerate risk for large trades
        
        return min(size_risk, 1.0)
    
    def _calculate_volatility_risk(self, commodity: str) -> float:
        """Calculate commodity volatility risk factor"""
        volatility = self.commodity_volatility.get(commodity.lower(), 0.40)
        
        # Normalize volatility risk (0 = low volatility, 1 = high volatility)
        # Assuming 0.25 is low risk and 0.60 is high risk
        volatility_risk = (volatility - 0.25) / (0.60 - 0.25)
        return max(0.0, min(volatility_risk, 1.0))
    
    def _calculate_concentration_risk(self, trade_data: Dict[str, Any]) -> float:
        """Calculate concentration risk factor"""
        # This is a simplified calculation
        # In production, this would consider portfolio composition
        
        commodity = trade_data.get("commodity", "unknown")
        trade_size = trade_data.get("quantity", 0) * trade_data.get("price", 0)
        
        # Placeholder for portfolio concentration calculation
        # For now, return a moderate risk level
        return 0.3
    
    def _calculate_counterparty_risk(self, counterparty: str) -> float:
        """Calculate counterparty risk factor"""
        # This is a simplified calculation
        # In production, this would use actual counterparty ratings
        
        # Placeholder logic - assume most counterparties are medium risk
        if "bank" in counterparty.lower() or "tier1" in counterparty.lower():
            return self.counterparty_ratings["A"]
        elif "tier2" in counterparty.lower():
            return self.counterparty_ratings["B"]
        elif "tier3" in counterparty.lower():
            return self.counterparty_ratings["C"]
        else:
            return self.counterparty_ratings["B"]  # Default to medium risk
    
    def _calculate_liquidity_risk(self, commodity: str) -> float:
        """Calculate liquidity risk factor"""
        # Liquidity risk based on commodity type
        high_liquidity = ["crude_oil", "natural_gas", "electricity"]
        medium_liquidity = ["lng", "lpg", "coal"]
        low_liquidity = ["uranium", "biofuels", "carbon_credits"]
        
        if commodity.lower() in high_liquidity:
            return 0.1  # Low liquidity risk
        elif commodity.lower() in medium_liquidity:
            return 0.4  # Medium liquidity risk
        elif commodity.lower() in low_liquidity:
            return 0.8  # High liquidity risk
        else:
            return 0.5  # Default medium risk
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on risk score"""
        if risk_score < 0.3:
            return "low"
        elif risk_score < 0.6:
            return "medium"
        else:
            return "high"
    
    def _check_risk_limits(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if trade exceeds risk limits"""
        trade_size = trade_data.get("quantity", 0) * trade_data.get("price", 0)
        commodity = trade_data.get("commodity", "unknown")
        
        limit_checks = {
            "size_limit": {
                "exceeded": trade_size > self.max_trade_size,
                "limit": self.max_trade_size,
                "current": trade_size,
                "available": max(0, self.max_trade_size - trade_size)
            },
            "daily_exposure": {
                "exceeded": False,  # Would check against actual daily exposure
                "limit": self.max_daily_exposure,
                "current": 0,  # Placeholder
                "available": self.max_daily_exposure
            },
            "counterparty_exposure": {
                "exceeded": False,  # Would check against actual counterparty exposure
                "limit": self.max_counterparty_exposure,
                "current": 0,  # Placeholder
                "available": self.max_counterparty_exposure
            },
            "commodity_concentration": {
                "exceeded": False,  # Would check against actual portfolio concentration
                "limit": self.max_commodity_concentration,
                "current": 0,  # Placeholder
                "available": self.max_commodity_concentration
            }
        }
        
        return limit_checks
    
    def _generate_risk_recommendations(self, risk_level: str, limit_checks: Dict[str, Any]) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        if risk_level == "high":
            recommendations.extend([
                "Consider reducing trade size",
                "Review commodity selection for lower volatility alternatives",
                "Assess counterparty creditworthiness",
                "Implement additional risk controls"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "Monitor trade execution closely",
                "Consider hedging strategies",
                "Review risk limits regularly"
            ])
        else:  # low risk
            recommendations.extend([
                "Standard risk controls sufficient",
                "Continue monitoring for changes in market conditions"
            ])
        
        # Add limit-specific recommendations
        for limit_name, limit_data in limit_checks.items():
            if limit_data.get("exceeded", False):
                recommendations.append(f"Trade exceeds {limit_name} - approval required")
        
        return recommendations
    
    async def calculate_portfolio_risk(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate portfolio-level risk metrics
        
        Args:
            portfolio_data: Portfolio composition and positions
            
        Returns:
            Dict with portfolio risk metrics
        """
        try:
            positions = portfolio_data.get("positions", [])
            total_value = portfolio_data.get("total_value", 0)
            
            if not positions or total_value <= 0:
                return {
                    "portfolio_risk_score": 0.0,
                    "var_95": 0.0,
                    "var_99": 0.0,
                    "expected_shortfall": 0.0,
                    "concentration_risk": 0.0,
                    "calculated_at": datetime.utcnow().isoformat()
                }
            
            # Calculate portfolio risk metrics
            portfolio_risk = self._calculate_portfolio_risk_metrics(positions, total_value)
            
            return {
                "portfolio_risk_score": round(portfolio_risk["risk_score"], 3),
                "var_95": round(portfolio_risk["var_95"], 2),
                "var_99": round(portfolio_risk["var_99"], 2),
                "expected_shortfall": round(portfolio_risk["expected_shortfall"], 2),
                "concentration_risk": round(portfolio_risk["concentration_risk"], 3),
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {e}")
            return {
                "portfolio_risk_score": 1.0,
                "var_95": 0.0,
                "var_99": 0.0,
                "expected_shortfall": 0.0,
                "concentration_risk": 1.0,
                "calculated_at": datetime.utcnow().isoformat()
            }
    
    def _calculate_portfolio_risk_metrics(self, positions: List[Dict[str, Any]], total_value: float) -> Dict[str, Any]:
        """Calculate portfolio risk metrics"""
        # Simplified risk calculation
        # In production, this would use proper VaR and ES calculations
        
        # Calculate weighted average risk score
        weighted_risk = 0.0
        for position in positions:
            position_value = position.get("value", 0)
            position_risk = position.get("risk_score", 0.5)
            weighted_risk += (position_value / total_value) * position_risk
        
        # Simplified VaR calculation (placeholder)
        var_95 = total_value * 0.05 * weighted_risk  # 5% VaR
        var_99 = total_value * 0.01 * weighted_risk  # 1% VaR
        expected_shortfall = var_95 * 1.4  # Simplified ES
        
        # Calculate concentration risk
        concentration_risk = self._calculate_portfolio_concentration(positions, total_value)
        
        return {
            "risk_score": weighted_risk,
            "var_95": var_95,
            "var_99": var_99,
            "expected_shortfall": expected_shortfall,
            "concentration_risk": concentration_risk
        }
    
    def _calculate_portfolio_concentration(self, positions: List[Dict[str, Any]], total_value: float) -> float:
        """Calculate portfolio concentration risk"""
        if not positions or total_value <= 0:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index (HHI) for concentration
        hhi = sum((position.get("value", 0) / total_value) ** 2 for position in positions)
        
        # Normalize HHI to 0-1 scale
        # HHI ranges from 1/n (perfect diversification) to 1 (perfect concentration)
        n = len(positions)
        normalized_hhi = (hhi - 1/n) / (1 - 1/n) if n > 1 else 0
        
        return min(normalized_hhi, 1.0)
    
    async def get_risk_limits(self) -> Dict[str, Any]:
        """Get current risk limits configuration"""
        return {
            "max_trade_size": self.max_trade_size,
            "max_daily_exposure": self.max_daily_exposure,
            "max_counterparty_exposure": self.max_counterparty_exposure,
            "max_commodity_concentration": self.max_commodity_concentration,
            "risk_weights": self.risk_weights,
            "commodity_volatility": self.commodity_volatility,
            "counterparty_ratings": self.counterparty_ratings
        }
    
    async def update_risk_limits(self, new_limits: Dict[str, Any]) -> Dict[str, Any]:
        """Update risk limits configuration"""
        try:
            # Update limits
            for key, value in new_limits.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            logger.info(f"Risk limits updated: {new_limits}")
            
            return {
                "success": True,
                "message": "Risk limits updated successfully",
                "updated_limits": new_limits,
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating risk limits: {e}")
            return {
                "success": False,
                "message": f"Error updating risk limits: {str(e)}",
                "updated_at": datetime.utcnow().isoformat()
            }
