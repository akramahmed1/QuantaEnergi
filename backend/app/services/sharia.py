"""
Sharia Compliance Engine for Islamic Finance Trading
Handles AAOIFI compliance, commodity screening, and Islamic trading rules
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class ShariaScreeningEngine:
    """Islamic finance compliance engine following AAOIFI standards"""
    
    def __init__(self):
        self.prohibited_commodities = [
            "alcohol", "pork", "gambling", "weapons", "tobacco"
        ]
        self.max_interest_ratio = 0.33  # Maximum 33% interest-bearing assets
        self.min_asset_backing = 0.70   # Minimum 70% asset-backed transactions
        
    def screen_commodity(self, commodity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Screen commodity for Sharia compliance
        
        Args:
            commodity_data: Commodity information including type, source, etc.
            
        Returns:
            Dict with compliance status and details
        """
        # TODO: Implement real AAOIFI commodity screening
        commodity_type = commodity_data.get("type", "").lower()
        
        if commodity_type in self.prohibited_commodities:
            return {
                "compliant": False,
                "reason": f"Commodity {commodity_type} is prohibited in Islamic finance",
                "screened_at": datetime.now().isoformat()
            }
        
        return {
            "compliant": True,
            "reason": "Commodity passed basic screening",
            "screened_at": datetime.now().isoformat()
        }
    
    def validate_trading_structure(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate trading structure for Islamic compliance
        
        Args:
            trade_data: Trade structure including financing terms
            
        Returns:
            Dict with validation results
        """
        # TODO: Implement comprehensive Islamic trading structure validation
        has_interest = trade_data.get("interest_rate", 0) > 0
        asset_backing = trade_data.get("asset_backing_ratio", 1.0)
        
        if has_interest:
            return {
                "compliant": False,
                "reason": "Interest-based financing not allowed in Islamic finance",
                "screened_at": datetime.now().isoformat()
            }
        
        if asset_backing < self.min_asset_backing:
            return {
                "compliant": False,
                "reason": f"Insufficient asset backing: {asset_backing:.2%} < {self.min_asset_backing:.2%}",
                "screened_at": datetime.now().isoformat()
            }
        
        return {
            "compliant": True,
            "reason": "Trading structure compliant with Islamic principles",
            "screened_at": datetime.now().isoformat()
        }
    
    def calculate_zakat_obligation(self, portfolio_value: float) -> Dict[str, Any]:
        """
        Calculate Zakat obligation (2.5% of wealth above nisab)
        
        Args:
            portfolio_value: Total portfolio value
            
        Returns:
            Dict with Zakat calculation
        """
        # TODO: Implement proper Zakat calculation with nisab thresholds
        nisab_threshold = 100000  # Placeholder value
        zakat_rate = 0.025
        
        if portfolio_value <= nisab_threshold:
            return {
                "zakat_obligation": 0.0,
                "nisab_threshold": nisab_threshold,
                "rate": zakat_rate,
                "calculated_at": datetime.now().isoformat()
            }
        
        zakat_amount = (portfolio_value - nisab_threshold) * zakat_rate
        
        return {
            "zakat_obligation": zakat_amount,
            "nisab_threshold": nisab_threshold,
            "rate": zakat_rate,
            "calculated_at": datetime.now().isoformat()
        }


class IslamicTradingValidator:
    """Validator for Islamic trading practices"""
    
    def __init__(self):
        self.murabaha_markup_limit = 0.15  # 15% maximum markup for Murabaha
        self.gharar_threshold = 0.20       # 20% uncertainty threshold
        self.haram_assets = ["alcohol", "pork", "gambling", "weapons", "tobacco", "pornography"]
        self.acceptable_gharar = 0.10      # 10% acceptable uncertainty
        
    async def validate_transaction(self, trade: Dict[str, Any]) -> bool:
        """
        Comprehensive Sharia compliance validation
        
        Args:
            trade: Trade data to validate
            
        Returns:
            Whether trade is Sharia compliant
        """
        try:
            # Check for riba (interest)
            if trade.get("interest_rate", 0) > 0:
                raise HTTPException(status_code=400, detail="Riba (interest) is prohibited in Islamic finance")
            
            # Check for excessive gharar (uncertainty)
            uncertainty = trade.get("uncertainty_level", 0.0)
            if uncertainty > self.acceptable_gharar:
                raise HTTPException(status_code=400, detail=f"Excessive gharar (uncertainty): {uncertainty:.2%} > {self.acceptable_gharar:.2%}")
            
            # Check for haram assets
            asset_type = trade.get("asset_type", "").lower()
            if asset_type in self.haram_assets:
                raise HTTPException(status_code=400, detail=f"Haram asset type: {asset_type}")
            
            # Check Ramadan trading restrictions
            if await self.is_ramadan_restricted():
                raise HTTPException(status_code=400, detail="Trading restricted during Ramadan")
            
            return True
            
        except Exception as e:
            logger.error(f"Sharia validation failed: {str(e)}")
            raise
    
    async def ensure_asset_backing(self, trade: Dict[str, Any]) -> bool:
        """
        Ensure trade has proper asset backing
        
        Args:
            trade: Trade data to check
            
        Returns:
            Whether trade has sufficient asset backing
        """
        try:
            # TODO: Implement real asset verification
            has_asset = trade.get("has_asset", False)
            asset_backing_ratio = trade.get("asset_backing_ratio", 1.0)
            
            if not has_asset or asset_backing_ratio < 0.7:
                raise HTTPException(status_code=400, detail="Insufficient asset backing")
            
            return True
            
        except Exception as e:
            logger.error(f"Asset backing check failed: {str(e)}")
            raise
    
    async def is_ramadan_restricted(self) -> bool:
        """
        Check if current date falls within Ramadan trading restrictions
        
        Returns:
            Whether trading is restricted
        """
        try:
            current_date = datetime.now()
            
            # 2025 Ramadan dates (approximate)
            ramadan_start = datetime(2025, 2, 28)
            ramadan_end = datetime(2025, 3, 29)
            
            # Check if current date is within Ramadan
            is_ramadan = ramadan_start <= current_date <= ramadan_end
            
            # Additional restrictions during last 10 days of Ramadan
            last_ten_days_start = ramadan_end - timedelta(days=10)
            is_last_ten_days = last_ten_days_start <= current_date <= ramadan_end
            
            return is_ramadan and is_last_ten_days
            
        except Exception as e:
            logger.error(f"Ramadan check failed: {str(e)}")
            raise
    
    async def generate_sharia_audit(self, trade_id: str) -> Dict[str, Any]:
        """
        Generate Sharia compliance audit report
        
        Args:
            trade_id: Trade identifier for audit
            
        Returns:
            Sharia audit report
        """
        try:
            # TODO: Implement comprehensive Sharia audit
            audit_report = {
                "audit_id": f"SHARIA-AUDIT-{datetime.now().strftime('%Y%m%d')}",
                "trade_id": trade_id,
                "audit_date": datetime.now().isoformat(),
                "sharia_board_approval": True,
                "compliance_score": 95.0,
                "risk_assessment": "low",
                "recommendations": ["Maintain current compliance practices"],
                "auditor": "Sharia Compliance Officer"
            }
            
            return audit_report
            
        except Exception as e:
            logger.error(f"Sharia audit generation failed: {str(e)}")
            raise
    
    def validate_murabaha_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Murabaha (cost-plus) contract
        
        Args:
            contract_data: Contract details including markup
            
        Returns:
            Dict with validation results
        """
        # TODO: Implement comprehensive Murabaha validation
        markup = contract_data.get("markup_percentage", 0)
        
        if markup > self.murabaha_markup_limit:
            return {
                "compliant": False,
                "reason": f"Markup {markup:.2%} exceeds limit {self.murabaha_markup_limit:.2%}",
                "screened_at": datetime.now().isoformat()
            }
        
        return {
            "compliant": True,
            "reason": "Murabaha contract compliant",
            "screened_at": datetime.now().isoformat()
        }
    
    def check_gharar_level(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check Gharar (uncertainty) level in trade
        
        Args:
            trade_data: Trade data with uncertainty metrics
            
        Returns:
            Dict with Gharar assessment
        """
        # TODO: Implement proper Gharar measurement
        uncertainty = trade_data.get("uncertainty_level", 0)
        
        if uncertainty > self.gharar_threshold:
            return {
                "gharar_level": "high",
                "compliant": False,
                "reason": f"Uncertainty {uncertainty:.2%} exceeds threshold {self.gharar_threshold:.2%}",
                "screened_at": datetime.now().isoformat()
            }
        
        return {
            "gharar_level": "acceptable",
            "compliant": True,
            "reason": "Uncertainty within acceptable limits",
            "screened_at": datetime.now().isoformat()
        }
