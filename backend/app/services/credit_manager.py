"""
Credit Management Service for ETRM/CTRM Trading
Handles credit limits, exposure tracking, and credit risk management
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class CreditManager:
    """Service for managing credit limits and exposure"""
    
    def __init__(self):
        self.credit_limits = {}  # In-memory storage for stubs
        self.exposure_records = {}
        self.credit_counter = 1000
        
    async def set_credit_limit(self, counterparty_id: str, limit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set credit limit for counterparty
        
        Args:
            counterparty_id: Counterparty identifier
            limit_data: Credit limit information
            
        Returns:
            Dict with credit limit details
        """
        try:
            # Handle both field names for compatibility
            limit_amount = limit_data.get("limit_amount") or limit_data.get("credit_limit", 0)
            
            # Validate limit data
            if limit_amount <= 0:
                raise HTTPException(status_code=400, detail="Credit limit must be positive")
            
            # Create or update credit limit
            credit_limit = {
                "limit_id": f"CREDIT-{self.credit_counter:06d}",
                "counterparty_id": counterparty_id,
                "credit_limit": limit_amount,
                "limit_amount": limit_amount,  # Store both for compatibility
                "currency": limit_data.get("currency", "USD"),
                "effective_date": limit_data.get("effective_date", datetime.now().isoformat()),
                "expiry_date": limit_data.get("expiry_date"),
                "limit_type": limit_data.get("limit_type", "total"),
                "collateral_required": limit_data.get("collateral_required", False),
                "collateral_value": limit_data.get("collateral_value", 0.0),
                "status": "active",
                "set_at": datetime.now().isoformat()
            }
            
            self.credit_limits[counterparty_id] = credit_limit
            self.credit_counter += 1
            
            logger.info(f"Credit limit set for {counterparty_id}: {credit_limit['credit_limit']}")
            
            return {
                "success": True,
                "credit_limit": credit_limit
            }
            
        except Exception as e:
            logger.error(f"Credit limit setting failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_credit_limit(self, counterparty_id: str) -> Dict[str, Any]:
        """
        Get credit limit for counterparty
        
        Args:
            counterparty_id: Counterparty identifier
            
        Returns:
            Dict with credit limit information
        """
        try:
            if counterparty_id not in self.credit_limits:
                raise HTTPException(status_code=404, detail="Credit limit not found")
            
            return {
                "success": True,
                "credit_limit": self.credit_limits[counterparty_id]
            }
            
        except Exception as e:
            logger.error(f"Credit limit retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def calculate_exposure(self, counterparty_id: str, positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate current exposure for counterparty
        
        Args:
            counterparty_id: Counterparty identifier
            positions: List of trading positions
            
        Returns:
            Dict with exposure calculations
        """
        try:
            # Filter positions for this counterparty
            counterparty_positions = [p for p in positions if p.get("counterparty_id") == counterparty_id]
            
            # Calculate exposure metrics
            total_exposure = sum(p.get("notional_value", 0) for p in counterparty_positions)
            unrealized_pnl = sum(p.get("unrealized_pnl", 0) for p in counterparty_positions)
            net_exposure = total_exposure + unrealized_pnl
            
            # Get credit limit
            credit_limit = self.credit_limits.get(counterparty_id, {}).get("credit_limit", 0)
            
            # Calculate utilization
            utilization_ratio = (net_exposure / credit_limit * 100) if credit_limit > 0 else 0
            
            exposure_record = {
                "exposure_id": f"EXP-{self.credit_counter:06d}",
                "counterparty_id": counterparty_id,
                "calculated_at": datetime.now().isoformat(),
                "total_exposure": total_exposure,
                "unrealized_pnl": unrealized_pnl,
                "net_exposure": net_exposure,
                "credit_limit": credit_limit,
                "utilization_ratio": utilization_ratio,
                "available_credit": max(0, credit_limit - net_exposure),
                "risk_level": self._calculate_risk_level(utilization_ratio)
            }
            
            self.exposure_records[counterparty_id] = exposure_record
            self.credit_counter += 1
            
            return {
                "success": True,
                "exposure": exposure_record
            }
            
        except Exception as e:
            logger.error(f"Exposure calculation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def check_credit_availability(self, counterparty_id: str, trade_value: float) -> Dict[str, Any]:
        """
        Check if trade can be executed within credit limits
        
        Args:
            counterparty_id: Counterparty identifier
            trade_value: Value of proposed trade
            
        Returns:
            Dict with credit availability check
        """
        try:
            if counterparty_id not in self.credit_limits:
                raise HTTPException(status_code=404, detail="Credit limit not found")
            
            credit_limit = self.credit_limits[counterparty_id]
            current_exposure = self.exposure_records.get(counterparty_id, {}).get("net_exposure", 0)
            
            # Check if trade fits within available credit
            available_credit = credit_limit["credit_limit"] - current_exposure
            can_execute = trade_value <= available_credit
            
            return {
                "success": True,
                "can_execute": can_execute,
                "trade_value": trade_value,
                "available_credit": available_credit,
                "credit_limit": credit_limit["credit_limit"],
                "current_exposure": current_exposure,
                "remaining_credit": available_credit - trade_value if can_execute else 0
            }
            
        except Exception as e:
            logger.error(f"Credit availability check failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def generate_credit_report(self, counterparty_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate credit risk report
        
        Args:
            counterparty_id: Optional specific counterparty, otherwise all
            
        Returns:
            Dict with credit report
        """
        try:
            if counterparty_id:
                # Single counterparty report
                if counterparty_id not in self.credit_limits:
                    raise HTTPException(status_code=404, detail="Counterparty not found")
                
                credit_limit = self.credit_limits[counterparty_id]
                exposure = self.exposure_records.get(counterparty_id, {})
                
                report = {
                    "report_id": f"CREDIT-REPORT-{datetime.now().strftime('%Y%m%d')}",
                    "counterparty_id": counterparty_id,
                    "generated_at": datetime.now().isoformat(),
                    "credit_limit": credit_limit,
                    "current_exposure": exposure,
                    "risk_assessment": self._assess_credit_risk(counterparty_id)
                }
            else:
                # Portfolio credit report
                total_credit_limit = sum(cl["credit_limit"] for cl in self.credit_limits.values())
                total_exposure = sum(exp.get("net_exposure", 0) for exp in self.exposure_records.values())
                portfolio_utilization = (total_exposure / total_credit_limit * 100) if total_credit_limit > 0 else 0
                
                report = {
                    "report_id": f"CREDIT-PORTFOLIO-{datetime.now().strftime('%Y%m%d')}",
                    "generated_at": datetime.now().isoformat(),
                    "portfolio_summary": {
                        "total_counterparties": len(self.credit_limits),
                        "total_credit_limit": total_credit_limit,
                        "total_exposure": total_exposure,
                        "portfolio_utilization": portfolio_utilization,
                        "available_credit": total_credit_limit - total_exposure
                    },
                    "counterparty_details": [
                        {
                            "counterparty_id": cp_id,
                            "credit_limit": cl,
                            "exposure": self.exposure_records.get(cp_id, {})
                        }
                        for cp_id, cl in self.credit_limits.items()
                    ]
                }
            
            return {
                "success": True,
                "report": report
            }
            
        except Exception as e:
            logger.error(f"Credit report generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _calculate_risk_level(self, utilization_ratio: float) -> str:
        """Calculate credit risk level based on utilization"""
        if utilization_ratio >= 90:
            return "critical"
        elif utilization_ratio >= 75:
            return "high"
        elif utilization_ratio >= 50:
            return "medium"
        else:
            return "low"
    
    def _assess_credit_risk(self, counterparty_id: str) -> Dict[str, Any]:
        """Assess credit risk for counterparty"""
        try:
            exposure = self.exposure_records.get(counterparty_id, {})
            utilization = exposure.get("utilization_ratio", 0)
            
            risk_factors = []
            if utilization > 90:
                risk_factors.append("Credit limit nearly exhausted")
            if utilization > 75:
                risk_factors.append("High credit utilization")
            
            return {
                "risk_level": exposure.get("risk_level", "low"),
                "risk_factors": risk_factors,
                "recommendations": self._generate_risk_recommendations(utilization)
            }
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {str(e)}")
            return {"risk_level": "unknown", "risk_factors": [], "recommendations": []}
    
    def _generate_risk_recommendations(self, utilization: float) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        if utilization > 90:
            recommendations.extend([
                "Immediate credit limit increase required",
                "Consider collateral requirements",
                "Monitor exposure daily"
            ])
        elif utilization > 75:
            recommendations.extend([
                "Consider credit limit increase",
                "Monitor exposure closely",
                "Review trading activity"
            ])
        elif utilization > 50:
            recommendations.extend([
                "Monitor utilization trends",
                "Consider risk mitigation strategies"
            ])
        else:
            recommendations.append("Maintain current credit practices")
        
        return recommendations
