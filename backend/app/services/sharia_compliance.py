"""
Sharia Compliance Service for Islamic Finance Trading
Handles AAOIFI compliance, commodity screening, and Islamic trading rules
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ShariaComplianceService:
    """Islamic finance compliance service following AAOIFI standards"""
    
    def __init__(self):
        self.prohibited_commodities = [
            "alcohol", "pork", "gambling", "weapons", "tobacco"
        ]
        self.max_interest_ratio = 0.33  # Maximum 33% interest-bearing assets
        self.min_asset_backing = 0.70   # Minimum 70% asset-backed transactions
        
        # Islamic trading restrictions
        self.ramadan_trading_hours = {
            "start": "09:00",
            "end": "15:00"  # Reduced hours during Ramadan
        }
        
        # Zakat calculation parameters
        self.nisab_threshold = 100000  # Minimum wealth threshold for Zakat
        self.zakat_rate = 0.025  # 2.5% Zakat rate
        
    async def validate_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate trade for Sharia compliance
        
        Args:
            trade_data: Trade information including commodity, structure, etc.
            
        Returns:
            Dict with compliance status and details
        """
        try:
            # Basic commodity screening
            commodity_result = self._screen_commodity(trade_data.get("commodity", ""))
            if not commodity_result["compliant"]:
                return commodity_result
            
            # Trading structure validation
            structure_result = self._validate_trading_structure(trade_data)
            if not structure_result["compliant"]:
                return structure_result
            
            # Time-based restrictions (e.g., Ramadan)
            time_result = self._check_time_restrictions(trade_data)
            if not time_result["compliant"]:
                return time_result
            
            # Asset backing validation
            asset_result = self._validate_asset_backing(trade_data)
            if not asset_result["compliant"]:
                return asset_result
            
            # All checks passed
            return {
                "compliant": True,
                "reason": "Trade compliant with Islamic principles",
                "screened_at": datetime.utcnow().isoformat(),
                "restrictions": [],
                "recommendations": [
                    "Ensure proper documentation for asset backing",
                    "Monitor for any changes in commodity classification",
                    "Maintain compliance with regional Islamic finance regulations"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in Sharia compliance validation: {e}")
            return {
                "compliant": False,
                "reason": f"Error during compliance validation: {str(e)}",
                "screened_at": datetime.utcnow().isoformat(),
                "restrictions": ["System error - manual review required"],
                "recommendations": ["Contact compliance team for manual review"]
            }
    
    def _screen_commodity(self, commodity: str) -> Dict[str, Any]:
        """Screen commodity for Sharia compliance"""
        commodity_lower = commodity.lower()
        
        if commodity_lower in self.prohibited_commodities:
            return {
                "compliant": False,
                "reason": f"Commodity {commodity} is prohibited in Islamic finance",
                "restrictions": [f"Trading in {commodity} is not permitted"],
                "screened_at": datetime.utcnow().isoformat()
            }
        
        # Check for specific commodity restrictions
        if commodity_lower in ["crude_oil", "natural_gas", "lng"]:
            # Energy commodities are generally compliant
            return {
                "compliant": True,
                "reason": f"Energy commodity {commodity} is compliant",
                "restrictions": [],
                "screened_at": datetime.utcnow().isoformat()
            }
        
        return {
            "compliant": True,
            "reason": f"Commodity {commodity} passed basic screening",
            "restrictions": [],
            "screened_at": datetime.utcnow().isoformat()
        }
    
    def _validate_trading_structure(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trading structure for Islamic compliance"""
        # Check for interest-based financing
        interest_rate = trade_data.get("interest_rate", 0)
        if interest_rate > 0:
            return {
                "compliant": False,
                "reason": "Interest-based financing not allowed in Islamic finance",
                "restrictions": ["No interest-bearing instruments allowed"],
                "screened_at": datetime.utcnow().isoformat()
            }
        
        # Check for speculative trading (gharar)
        if trade_data.get("is_speculative", False):
            return {
                "compliant": False,
                "reason": "Speculative trading (gharar) not allowed in Islamic finance",
                "restrictions": ["No speculative or gambling-like trading"],
                "screened_at": datetime.utcnow().isoformat()
            }
        
        return {
            "compliant": True,
            "reason": "Trading structure compliant with Islamic principles",
            "restrictions": [],
            "screened_at": datetime.utcnow().isoformat()
        }
    
    def _check_time_restrictions(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check time-based trading restrictions"""
        # Check if trading is during Ramadan
        current_time = datetime.utcnow()
        # This is a simplified check - in production, use proper Islamic calendar
        is_ramadan = False  # Placeholder for actual Ramadan detection
        
        if is_ramadan:
            # Check if trading is within allowed hours
            current_hour = current_time.hour
            if current_hour < 9 or current_hour > 15:
                return {
                    "compliant": False,
                    "reason": "Trading outside Ramadan hours not permitted",
                    "restrictions": ["Trading restricted to 09:00-15:00 during Ramadan"],
                    "screened_at": datetime.utcnow().isoformat()
                }
        
        return {
            "compliant": True,
            "reason": "Time restrictions satisfied",
            "restrictions": [],
            "screened_at": datetime.utcnow().isoformat()
        }
    
    def _validate_asset_backing(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate asset backing for Islamic compliance"""
        asset_backing_ratio = trade_data.get("asset_backing_ratio", 1.0)
        
        if asset_backing_ratio < self.min_asset_backing:
            return {
                "compliant": False,
                "reason": f"Insufficient asset backing: {asset_backing_ratio:.2%} < {self.min_asset_backing:.2%}",
                "restrictions": [f"Minimum {self.min_asset_backing:.0%} asset backing required"],
                "screened_at": datetime.utcnow().isoformat()
            }
        
        return {
            "compliant": True,
            "reason": "Asset backing requirements satisfied",
            "restrictions": [],
            "screened_at": datetime.utcnow().isoformat()
        }
    
    async def calculate_zakat_obligation(self, portfolio_value: float) -> Dict[str, Any]:
        """
        Calculate Zakat obligation (2.5% of wealth above nisab)
        
        Args:
            portfolio_value: Total portfolio value
            
        Returns:
            Dict with Zakat calculation
        """
        try:
            if portfolio_value <= self.nisab_threshold:
                return {
                    "zakat_obligation": 0.0,
                    "reason": f"Portfolio value {portfolio_value} below nisab threshold {self.nisab_threshold}",
                    "nisab_threshold": self.nisab_threshold,
                    "calculated_at": datetime.utcnow().isoformat()
                }
            
            zakat_amount = (portfolio_value - self.nisab_threshold) * self.zakat_rate
            
            return {
                "zakat_obligation": zakat_amount,
                "reason": f"Zakat calculated on wealth above nisab threshold",
                "nisab_threshold": self.nisab_threshold,
                "zakat_rate": self.zakat_rate,
                "taxable_amount": portfolio_value - self.nisab_threshold,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating Zakat: {e}")
            return {
                "zakat_obligation": 0.0,
                "reason": f"Error in Zakat calculation: {str(e)}",
                "calculated_at": datetime.utcnow().isoformat()
            }
    
    async def get_islamic_trading_guidelines(self, region: str = "global") -> Dict[str, Any]:
        """
        Get Islamic trading guidelines for a specific region
        
        Args:
            region: Trading region (ME, US, UK, EU, global)
            
        Returns:
            Dict with regional guidelines
        """
        guidelines = {
            "ME": {
                "primary_standard": "AAOIFI",
                "commodity_screening": "Strict",
                "asset_backing": "100% required",
                "interest_prohibition": "Absolute",
                "ramadan_restrictions": "Yes",
                "zakat_requirements": "Mandatory"
            },
            "US": {
                "primary_standard": "IFSB + Local",
                "commodity_screening": "Moderate",
                "asset_backing": "70% minimum",
                "interest_prohibition": "Relative",
                "ramadan_restrictions": "Optional",
                "zakat_requirements": "Voluntary"
            },
            "UK": {
                "primary_standard": "IFSB + FCA",
                "commodity_screening": "Moderate",
                "asset_backing": "70% minimum",
                "interest_prohibition": "Relative",
                "ramadan_restrictions": "Optional",
                "zakat_requirements": "Voluntary"
            },
            "EU": {
                "primary_standard": "IFSB + MiFID",
                "commodity_screening": "Moderate",
                "asset_backing": "70% minimum",
                "interest_prohibition": "Relative",
                "ramadan_restrictions": "Optional",
                "zakat_requirements": "Voluntary"
            },
            "global": {
                "primary_standard": "IFSB",
                "commodity_screening": "Basic",
                "asset_backing": "70% minimum",
                "interest_prohibition": "Relative",
                "ramadan_restrictions": "Optional",
                "zakat_requirements": "Voluntary"
            }
        }
        
        return guidelines.get(region, guidelines["global"])
    
    async def validate_murabaha_structure(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Murabaha (cost-plus financing) structure
        
        Args:
            trade_data: Trade data including markup, asset details
            
        Returns:
            Dict with validation results
        """
        try:
            markup = trade_data.get("murabaha_markup", 0)
            asset_details = trade_data.get("asset_details", {})
            
            # Check markup is reasonable (not excessive)
            if markup > 0.50:  # 50% maximum markup
                return {
                    "compliant": False,
                    "reason": f"Excessive markup {markup:.1%} not permitted in Murabaha",
                    "restrictions": ["Maximum 50% markup allowed"],
                    "screened_at": datetime.utcnow().isoformat()
                }
            
            # Check asset details are provided
            if not asset_details:
                return {
                    "compliant": False,
                    "reason": "Asset details required for Murabaha structure",
                    "restrictions": ["Complete asset documentation required"],
                    "screened_at": datetime.utcnow().isoformat()
                }
            
            return {
                "compliant": True,
                "reason": "Murabaha structure compliant with Islamic principles",
                "restrictions": [],
                "screened_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error validating Murabaha structure: {e}")
            return {
                "compliant": False,
                "reason": f"Error in Murabaha validation: {str(e)}",
                "restrictions": ["Manual review required"],
                "screened_at": datetime.utcnow().isoformat()
            }
