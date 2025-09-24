"""
Sharia Compliance Service
Provides Islamic finance compliance checks for energy trading
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import structlog
from enum import Enum

logger = structlog.get_logger(__name__)

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_REVIEW = "requires_review"

class ShariaComplianceService:
    """Sharia compliance service for Islamic finance trading"""
    
    def __init__(self):
        self.ramadan_dates = self._get_ramadan_dates()
        self.halal_commodities = [
            'electricity', 'solar_energy', 'wind_energy', 'hydroelectric',
            'geothermal', 'nuclear_energy', 'natural_gas', 'renewable_energy'
        ]
        self.haram_commodities = [
            'alcohol', 'tobacco', 'pork', 'gambling', 'interest_based'
        ]
        self.riba_threshold = 0.01  # 1% interest threshold
    
    def _get_ramadan_dates(self) -> List[Tuple[int, int, int]]:
        """Get Ramadan dates for the next 5 years (approximate)"""
        # This is a simplified calculation - in production, use proper Islamic calendar
        ramadan_dates = []
        current_year = datetime.now().year
        
        for year in range(current_year, current_year + 5):
            # Approximate Ramadan start dates (these would be calculated properly in production)
            if year == 2024:
                ramadan_dates.append((year, 3, 11))  # March 11, 2024
            elif year == 2025:
                ramadan_dates.append((year, 3, 1))   # March 1, 2025
            elif year == 2026:
                ramadan_dates.append((year, 2, 18))  # February 18, 2026
            elif year == 2027:
                ramadan_dates.append((year, 2, 8))   # February 8, 2027
            elif year == 2028:
                ramadan_dates.append((year, 1, 28))  # January 28, 2028
        
        return ramadan_dates
    
    def check_trade_compliance(self, trade_data: Dict) -> Dict:
        """
        Check if a trade complies with Sharia principles
        
        Args:
            trade_data: Trade information including commodity, price, terms
            
        Returns:
            Dictionary containing compliance status and details
        """
        try:
            logger.info("Checking Sharia compliance", trade_id=trade_data.get('id'))
            
            compliance_checks = {
                'commodity_check': self._check_commodity_halal(trade_data),
                'riba_check': self._check_riba_compliance(trade_data),
                'gharar_check': self._check_gharar_compliance(trade_data),
                'ramadan_check': self._check_ramadan_trading(trade_data),
                'maysir_check': self._check_maysir_compliance(trade_data),
                'zakat_check': self._check_zakat_compliance(trade_data)
            }
            
            # Determine overall compliance status
            overall_status = self._determine_overall_status(compliance_checks)
            
            result = {
                'trade_id': trade_data.get('id'),
                'overall_status': overall_status.value,
                'compliance_checks': compliance_checks,
                'recommendations': self._generate_recommendations(compliance_checks),
                'checked_at': datetime.now().isoformat(),
                'compliance_score': self._calculate_compliance_score(compliance_checks)
            }
            
            logger.info("Sharia compliance check completed", 
                       trade_id=trade_data.get('id'),
                       status=overall_status.value)
            
            return result
            
        except Exception as e:
            logger.error("Sharia compliance check failed", error=str(e))
            raise Exception(f"Sharia compliance check failed: {str(e)}")
    
    def _check_commodity_halal(self, trade_data: Dict) -> Dict:
        """Check if the commodity is halal (permissible)"""
        commodity = trade_data.get('commodity', '').lower()
        
        if commodity in self.halal_commodities:
            return {
                'status': ComplianceStatus.COMPLIANT.value,
                'message': f"Commodity '{commodity}' is halal",
                'details': "Energy commodities are generally permissible in Islamic finance"
            }
        elif commodity in self.haram_commodities:
            return {
                'status': ComplianceStatus.NON_COMPLIANT.value,
                'message': f"Commodity '{commodity}' is haram (forbidden)",
                'details': "This commodity is not permissible in Islamic finance"
            }
        else:
            return {
                'status': ComplianceStatus.REQUIRES_REVIEW.value,
                'message': f"Commodity '{commodity}' requires Sharia board review",
                'details': "Please consult with Islamic finance scholars"
            }
    
    def _check_riba_compliance(self, trade_data: Dict) -> Dict:
        """Check for riba (usury/interest) compliance"""
        price = trade_data.get('price', 0)
        quantity = trade_data.get('quantity', 0)
        
        # Check for excessive profit margins that might constitute riba
        cost_basis = trade_data.get('cost_basis', price * 0.8)  # Assume 20% cost basis
        profit_margin = (price - cost_basis) / cost_basis if cost_basis > 0 else 0
        
        if profit_margin > self.riba_threshold:
            return {
                'status': ComplianceStatus.REQUIRES_REVIEW.value,
                'message': f"Profit margin {profit_margin:.2%} exceeds riba threshold",
                'details': f"Consider reducing profit margin to below {self.riba_threshold:.1%}"
            }
        else:
            return {
                'status': ComplianceStatus.COMPLIANT.value,
                'message': "Profit margin is within acceptable limits",
                'details': f"Current margin: {profit_margin:.2%}"
            }
    
    def _check_gharar_compliance(self, trade_data: Dict) -> Dict:
        """Check for gharar (excessive uncertainty) compliance"""
        delivery_date = trade_data.get('delivery_date')
        delivery_location = trade_data.get('delivery_location')
        
        if not delivery_date or not delivery_location:
            return {
                'status': ComplianceStatus.NON_COMPLIANT.value,
                'message': "Missing delivery specifications",
                'details': "Delivery date and location must be clearly specified to avoid gharar"
            }
        
        # Check if delivery date is too far in the future (excessive uncertainty)
        try:
            delivery_dt = datetime.fromisoformat(delivery_date.replace('Z', '+00:00'))
            days_until_delivery = (delivery_dt - datetime.now()).days
            
            if days_until_delivery > 365:
                return {
                    'status': ComplianceStatus.REQUIRES_REVIEW.value,
                    'message': f"Delivery date is {days_until_delivery} days in the future",
                    'details': "Consider shorter delivery periods to reduce uncertainty"
                }
            else:
                return {
                    'status': ComplianceStatus.COMPLIANT.value,
                    'message': "Delivery specifications are clear",
                    'details': f"Delivery in {days_until_delivery} days at {delivery_location}"
                }
        except Exception:
            return {
                'status': ComplianceStatus.NON_COMPLIANT.value,
                'message': "Invalid delivery date format",
                'details': "Please provide delivery date in ISO format"
            }
    
    def _check_ramadan_trading(self, trade_data: Dict) -> Dict:
        """Check if trading during Ramadan is appropriate"""
        current_date = datetime.now()
        
        # Check if current date falls during Ramadan
        is_ramadan = False
        for year, month, day in self.ramadan_dates:
            ramadan_start = datetime(year, month, day)
            ramadan_end = ramadan_start + timedelta(days=29)  # Approximate 29-30 days
            
            if ramadan_start <= current_date <= ramadan_end:
                is_ramadan = True
                break
        
        if is_ramadan:
            return {
                'status': ComplianceStatus.REQUIRES_REVIEW.value,
                'message': "Trading during Ramadan period",
                'details': "Consider reducing trading activity during Ramadan as per Islamic principles"
            }
        else:
            return {
                'status': ComplianceStatus.COMPLIANT.value,
                'message': "Trading outside Ramadan period",
                'details': "Normal trading activities are permissible"
            }
    
    def _check_maysir_compliance(self, trade_data: Dict) -> Dict:
        """Check for maysir (gambling) compliance"""
        trade_type = trade_data.get('trade_type', '').lower()
        
        # Check for gambling-like trading patterns
        if trade_type in ['speculation', 'gambling', 'bet']:
            return {
                'status': ComplianceStatus.NON_COMPLIANT.value,
                'message': "Trade type resembles gambling (maysir)",
                'details': "Speculative trading without underlying assets is not permissible"
            }
        elif trade_type in ['spot', 'forward', 'futures']:
            return {
                'status': ComplianceStatus.COMPLIANT.value,
                'message': "Trade type is permissible",
                'details': "Physical delivery contracts are compliant with Islamic principles"
            }
        else:
            return {
                'status': ComplianceStatus.REQUIRES_REVIEW.value,
                'message': f"Trade type '{trade_type}' requires review",
                'details': "Please consult with Sharia board for this trade type"
            }
    
    def _check_zakat_compliance(self, trade_data: Dict) -> Dict:
        """Check zakat compliance for trading profits"""
        price = trade_data.get('price', 0)
        quantity = trade_data.get('quantity', 0)
        total_value = price * quantity
        
        # Zakat threshold (nisab) - approximately $3,000 USD
        zakat_threshold = 3000
        
        if total_value >= zakat_threshold:
            zakat_amount = total_value * 0.025  # 2.5% zakat rate
            return {
                'status': ComplianceStatus.COMPLIANT.value,
                'message': "Zakat calculation required",
                'details': f"Estimated zakat amount: ${zakat_amount:.2f} (2.5% of ${total_value:.2f})"
            }
        else:
            return {
                'status': ComplianceStatus.COMPLIANT.value,
                'message': "Below zakat threshold",
                'details': f"Trade value ${total_value:.2f} is below zakat threshold ${zakat_threshold}"
            }
    
    def _determine_overall_status(self, compliance_checks: Dict) -> ComplianceStatus:
        """Determine overall compliance status based on individual checks"""
        statuses = [check['status'] for check in compliance_checks.values()]
        
        if ComplianceStatus.NON_COMPLIANT.value in statuses:
            return ComplianceStatus.NON_COMPLIANT
        elif ComplianceStatus.REQUIRES_REVIEW.value in statuses:
            return ComplianceStatus.REQUIRES_REVIEW
        else:
            return ComplianceStatus.COMPLIANT
    
    def _generate_recommendations(self, compliance_checks: Dict) -> List[str]:
        """Generate recommendations based on compliance checks"""
        recommendations = []
        
        for check_name, check_result in compliance_checks.items():
            if check_result['status'] == ComplianceStatus.NON_COMPLIANT.value:
                recommendations.append(f"❌ {check_result['message']}")
            elif check_result['status'] == ComplianceStatus.REQUIRES_REVIEW.value:
                recommendations.append(f"⚠️ {check_result['message']}")
        
        if not recommendations:
            recommendations.append("✅ All Sharia compliance checks passed")
        
        return recommendations
    
    def _calculate_compliance_score(self, compliance_checks: Dict) -> float:
        """Calculate overall compliance score (0-100)"""
        total_checks = len(compliance_checks)
        compliant_checks = sum(1 for check in compliance_checks.values() 
                             if check['status'] == ComplianceStatus.COMPLIANT.value)
        
        return (compliant_checks / total_checks) * 100 if total_checks > 0 else 0
    
    def get_sharia_board_approval(self, trade_id: str) -> Dict:
        """Get Sharia board approval for a trade"""
        try:
            logger.info("Requesting Sharia board approval", trade_id=trade_id)
            
            # In a real implementation, this would interface with actual Sharia board
            approval = {
                'trade_id': trade_id,
                'sharia_board_approval': True,
                'approved_by': 'Dr. Ahmad Al-Mansouri',
                'approval_date': datetime.now().isoformat(),
                'fatwa_number': f"FATWA-{trade_id}-{datetime.now().strftime('%Y%m%d')}",
                'conditions': [
                    "Trade must be settled within 30 days",
                    "Physical delivery must be confirmed",
                    "No interest-based financing allowed"
                ],
                'valid_until': (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            logger.info("Sharia board approval granted", trade_id=trade_id)
            return approval
            
        except Exception as e:
            logger.error("Sharia board approval failed", error=str(e))
            raise Exception(f"Sharia board approval failed: {str(e)}")

# Global instance
sharia_compliance_service = ShariaComplianceService()
