"""
Base Islamic Finance Service for EnergyOpti-Pro.

This module provides a unified base class for all Islamic finance services,
eliminating duplication and providing consistent patterns for:
- Shariah compliance validation
- Islamic finance calculations
- Riba, Gharar, and Maysir checks
- Zakat calculations
- Sukuk and Murabaha handling
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

from ...core.logging import get_logger
from ...core.config import settings

logger = get_logger(__name__)

class IslamicFinanceType(Enum):
    """Types of Islamic finance products."""
    SUKUK = "sukuk"
    MURABAHA = "murabaha"
    IJARA = "ijara"
    MUSHARAKA = "musharaka"
    MUDARABA = "mudaraba"
    ISTISNA = "istisna"
    SALAM = "salam"
    QARD_HASAN = "qard_hasan"

class ComplianceStatus(Enum):
    """Islamic compliance status."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    CONDITIONAL = "conditional"
    REQUIRES_REVIEW = "requires_review"
    PENDING_APPROVAL = "pending_approval"

class RibaType(Enum):
    """Types of Riba (usury)."""
    RIBA_AL_NAJASH = "riba_al_najash"      # Riba of trade
    RIBA_AL_FAHL = "riba_al_fahl"          # Riba of excess
    RIBA_AL_YAD = "riba_al_yad"            # Riba of hand
    RIBA_AL_QURUD = "riba_al_qurud"        # Riba of loans

class GhararType(Enum):
    """Types of Gharar (uncertainty)."""
    GHARAR_FISHEEN = "gharar_fisheen"      # Excessive uncertainty
    GHARAR_YASEER = "gharar_yaseer"         # Minor uncertainty
    GHARAR_KATHEER = "gharar_katheer"      # Major uncertainty

@dataclass
class IslamicComplianceCheck:
    """Result of an Islamic compliance check."""
    check_type: str
    status: ComplianceStatus
    details: str
    recommendations: List[str]
    timestamp: datetime
    checker_id: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ZakatCalculation:
    """Zakat calculation result."""
    asset_type: str
    asset_value: float
    zakat_rate: float
    zakat_amount: float
    calculation_date: datetime
    nisab_threshold: float
    is_zakatable: bool
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SukukStructure:
    """Sukuk (Islamic bonds) structure."""
    sukuk_id: str
    type: IslamicFinanceType
    face_value: float
    maturity_date: date
    profit_rate: float
    underlying_asset: str
    asset_value: float
    compliance_status: ComplianceStatus
    issuance_date: datetime
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class MurabahaContract:
    """Murabaha (cost-plus financing) contract."""
    contract_id: str
    asset_description: str
    cost_price: float
    markup: float
    selling_price: float
    payment_terms: str
    delivery_date: date
    compliance_status: ComplianceStatus
    contract_date: datetime
    metadata: Optional[Dict[str, Any]] = None

class BaseIslamicFinanceService(ABC):
    """
    Base class for all Islamic finance services.
    
    This class provides:
    - Unified Shariah compliance validation
    - Consistent Islamic finance calculations
    - Shared business rules and patterns
    - Common utility functions
    """
    
    def __init__(self):
        """Initialize base Islamic finance service."""
        self.logger = logger.getChild(self.__class__.__name__)
        self.compliance_rules = self._setup_compliance_rules()
        self.zakat_rates = self._setup_zakat_rates()
        self.gharar_thresholds = self._setup_gharar_thresholds()
    
    def _setup_compliance_rules(self) -> Dict[str, Any]:
        """Setup Islamic compliance rules."""
        return {
            "riba": {
                "max_interest_rate": 0.0,
                "allowable_markup": 0.15,  # 15% maximum markup
                "prohibited_activities": [
                    "interest_charging",
                    "speculative_trading",
                    "gambling",
                    "alcohol_trading",
                    "pork_trading"
                ]
            },
            "gharar": {
                "max_uncertainty": 0.20,  # 20% maximum uncertainty
                "allowable_uncertainty": 0.10,  # 10% acceptable uncertainty
                "prohibited_contracts": [
                    "futures_speculation",
                    "options_gambling",
                    "insurance_gambling"
                ]
            },
            "maysir": {
                "prohibited_activities": [
                    "gambling",
                    "lottery",
                    "speculative_trading",
                    "zero_sum_games"
                ]
            }
        }
    
    def _setup_zakat_rates(self) -> Dict[str, float]:
        """Setup Zakat rates for different asset types."""
        return {
            "cash": 0.025,      # 2.5%
            "gold": 0.025,      # 2.5%
            "silver": 0.025,    # 2.5%
            "livestock": 0.025, # 2.5%
            "agriculture": 0.10, # 10% (irrigated)
            "agriculture_rain": 0.05, # 5% (rain-fed)
            "minerals": 0.20,   # 20%
            "treasure": 0.20    # 20%
        }
    
    def _setup_gharar_thresholds(self) -> Dict[str, float]:
        """Setup Gharar uncertainty thresholds."""
        return {
            "low": 0.05,        # 5% - Acceptable
            "medium": 0.10,     # 10% - Requires review
            "high": 0.20,       # 20% - Prohibited
            "excessive": 0.30   # 30% - Absolutely prohibited
        }
    
    def validate_riba(self, transaction: Dict[str, Any]) -> IslamicComplianceCheck:
        """
        Validate transaction for Riba (usury) compliance.
        
        Args:
            transaction: Transaction data to validate
            
        Returns:
            Compliance check result
        """
        self.logger.info(f"Validating Riba compliance for transaction: {transaction.get('id', 'unknown')}")
        
        violations = []
        recommendations = []
        
        # Check for interest charges
        if transaction.get("interest_rate", 0) > 0:
            violations.append("Interest rate greater than 0%")
            recommendations.append("Use profit-sharing or markup-based pricing")
        
        # Check for excessive markup
        cost = transaction.get("cost", 0)
        selling_price = transaction.get("selling_price", 0)
        if cost > 0 and selling_price > 0:
            markup_percentage = (selling_price - cost) / cost
            max_markup = self.compliance_rules["riba"]["allowable_markup"]
            if markup_percentage > max_markup:
                violations.append(f"Markup {markup_percentage:.1%} exceeds maximum {max_markup:.1%}")
                recommendations.append(f"Reduce markup to maximum {max_markup:.1%}")
        
        # Check for prohibited activities
        activity = transaction.get("activity_type", "").lower()
        for prohibited in self.compliance_rules["riba"]["prohibited_activities"]:
            if prohibited in activity:
                violations.append(f"Prohibited activity: {prohibited}")
                recommendations.append("Choose Shariah-compliant alternative")
        
        # Determine compliance status
        if violations:
            status = ComplianceStatus.NON_COMPLIANT
            details = f"Riba violations found: {', '.join(violations)}"
        else:
            status = ComplianceStatus.COMPLIANT
            details = "Transaction is Riba-compliant"
            recommendations.append("Continue with current structure")
        
        return IslamicComplianceCheck(
            check_type="riba_validation",
            status=status,
            details=details,
            recommendations=recommendations,
            timestamp=datetime.now(),
            checker_id=self.__class__.__name__,
            metadata={
                "violations": violations,
                "markup_percentage": markup_percentage if 'markup_percentage' in locals() else None,
                "activity_type": activity
            }
        )
    
    def validate_gharar(self, contract: Dict[str, Any]) -> IslamicComplianceCheck:
        """
        Validate contract for Gharar (uncertainty) compliance.
        
        Args:
            contract: Contract data to validate
            
        Returns:
            Compliance check result
        """
        self.logger.info(f"Validating Gharar compliance for contract: {contract.get('id', 'unknown')}")
        
        violations = []
        recommendations = []
        
        # Calculate uncertainty level
        uncertainty_factors = []
        
        # Asset specification uncertainty
        asset_spec = contract.get("asset_specification", "")
        if not asset_spec or asset_spec == "TBD":
            uncertainty_factors.append("Asset specification unclear")
        
        # Price uncertainty
        price = contract.get("price", 0)
        if price <= 0:
            uncertainty_factors.append("Price not determined")
        
        # Delivery uncertainty
        delivery_date = contract.get("delivery_date")
        if not delivery_date:
            uncertainty_factors.append("Delivery date unclear")
        
        # Calculate overall uncertainty
        uncertainty_level = len(uncertainty_factors) / 3.0  # Normalize to 0-1
        
        # Check against thresholds
        if uncertainty_level > self.gharar_thresholds["excessive"]:
            status = ComplianceStatus.NON_COMPLIANT
            details = "Excessive uncertainty - contract prohibited"
            recommendations.append("Clarify all contract terms before proceeding")
        elif uncertainty_level > self.gharar_thresholds["high"]:
            status = ComplianceStatus.NON_COMPLIANT
            details = "High uncertainty - contract requires major revisions"
            recommendations.append("Reduce uncertainty to acceptable levels")
        elif uncertainty_level > self.gharar_thresholds["medium"]:
            status = ComplianceStatus.REQUIRES_REVIEW
            details = "Medium uncertainty - contract requires review"
            recommendations.append("Clarify unclear terms")
        elif uncertainty_level > self.gharar_thresholds["low"]:
            status = ComplianceStatus.CONDITIONAL
            details = "Low uncertainty - contract acceptable with conditions"
            recommendations.append("Document any remaining uncertainties")
        else:
            status = ComplianceStatus.COMPLIANT
            details = "Contract has acceptable uncertainty levels"
            recommendations.append("Proceed with current structure")
        
        return IslamicComplianceCheck(
            check_type="gharar_validation",
            status=status,
            details=details,
            recommendations=recommendations,
            timestamp=datetime.now(),
            checker_id=self.__class__.__name__,
            metadata={
                "uncertainty_level": uncertainty_level,
                "uncertainty_factors": uncertainty_factors,
                "thresholds": self.gharar_thresholds
            }
        )
    
    def validate_maysir(self, activity: Dict[str, Any]) -> IslamicComplianceCheck:
        """
        Validate activity for Maysir (gambling) compliance.
        
        Args:
            activity: Activity data to validate
            
        Returns:
            Compliance check result
        """
        self.logger.info(f"Validating Maysir compliance for activity: {activity.get('id', 'unknown')}")
        
        violations = []
        recommendations = []
        
        # Check for gambling elements
        activity_type = activity.get("type", "").lower()
        for prohibited in self.compliance_rules["maysir"]["prohibited_activities"]:
            if prohibited in activity_type:
                violations.append(f"Prohibited activity: {prohibited}")
                recommendations.append("Choose Shariah-compliant alternative")
        
        # Check for zero-sum games
        if activity.get("zero_sum", False):
            violations.append("Zero-sum game detected")
            recommendations.append("Ensure all parties benefit from transaction")
        
        # Check for speculative trading
        if activity.get("speculative", False):
            violations.append("Speculative trading detected")
            recommendations.append("Ensure trading is based on real assets and needs")
        
        # Determine compliance status
        if violations:
            status = ComplianceStatus.NON_COMPLIANT
            details = f"Maysir violations found: {', '.join(violations)}"
        else:
            status = ComplianceStatus.COMPLIANT
            details = "Activity is Maysir-compliant"
            recommendations.append("Continue with current structure")
        
        return IslamicComplianceCheck(
            check_type="maysir_validation",
            status=status,
            details=details,
            recommendations=recommendations,
            timestamp=datetime.now(),
            checker_id=self.__class__.__name__,
            metadata={
                "violations": violations,
                "activity_type": activity_type,
                "zero_sum": activity.get("zero_sum", False),
                "speculative": activity.get("speculative", False)
            }
        )
    
    def calculate_zakat(self, assets: Dict[str, float]) -> ZakatCalculation:
        """
        Calculate Zakat for given assets.
        
        Args:
            assets: Dictionary of asset types and values
            
        Returns:
            Zakat calculation result
        """
        self.logger.info("Calculating Zakat for assets")
        
        total_value = sum(assets.values())
        nisab_threshold = self._get_nisab_threshold()
        
        if total_value < nisab_threshold:
            return ZakatCalculation(
                asset_type="total",
                asset_value=total_value,
                zakat_rate=0.0,
                zakat_amount=0.0,
                calculation_date=datetime.now(),
                nisab_threshold=nisab_threshold,
                is_zakatable=False,
                metadata={"reason": "Below Nisab threshold"}
            )
        
        # Calculate Zakat for each asset type
        total_zakat = 0.0
        asset_calculations = {}
        
        for asset_type, value in assets.items():
            if asset_type in self.zakat_rates:
                rate = self.zakat_rates[asset_type]
                zakat_amount = value * rate
                total_zakat += zakat_amount
                asset_calculations[asset_type] = {
                    "value": value,
                    "rate": rate,
                    "zakat": zakat_amount
                }
        
        return ZakatCalculation(
            asset_type="total",
            asset_value=total_value,
            zakat_rate=0.025,  # Standard rate for most assets
            zakat_amount=total_zakat,
            calculation_date=datetime.now(),
            nisab_threshold=nisab_threshold,
            is_zakatable=True,
            metadata={
                "asset_breakdown": asset_calculations,
                "total_zakat": total_zakat
            }
        )
    
    def _get_nisab_threshold(self) -> float:
        """Get current Nisab threshold (minimum wealth for Zakat)."""
        # This would typically be based on current gold/silver prices
        # For now, using a standard threshold
        return 5000.0  # USD equivalent
    
    def validate_sukuk_structure(self, sukuk: SukukStructure) -> IslamicComplianceCheck:
        """
        Validate Sukuk structure for Shariah compliance.
        
        Args:
            sukuk: Sukuk structure to validate
            
        Returns:
            Compliance check result
        """
        self.logger.info(f"Validating Sukuk structure: {sukuk.sukuk_id}")
        
        # Check underlying asset
        if not sukuk.underlying_asset or sukuk.asset_value <= 0:
            return IslamicComplianceCheck(
                check_type="sukuk_validation",
                status=ComplianceStatus.NON_COMPLIANT,
                details="Sukuk must have real underlying asset",
                recommendations=["Ensure underlying asset exists and has value"],
                timestamp=datetime.now(),
                checker_id=self.__class__.__name__
            )
        
        # Check profit rate (should not be interest-based)
        if sukuk.profit_rate <= 0:
            return IslamicComplianceCheck(
                check_type="sukuk_validation",
                status=ComplianceStatus.REQUIRES_REVIEW,
                details="Profit rate must be positive",
                recommendations=["Set appropriate profit rate based on asset performance"],
                timestamp=datetime.now(),
                checker_id=self.__class__.__name__
            )
        
        # Check asset backing
        if sukuk.asset_value < sukuk.face_value:
            return IslamicComplianceCheck(
                check_type="sukuk_validation",
                status=ComplianceStatus.CONDITIONAL,
                details="Asset value less than face value",
                recommendations=["Ensure adequate asset backing or reduce face value"],
                timestamp=datetime.now(),
                checker_id=self.__class__.__name__
            )
        
        return IslamicComplianceCheck(
            check_type="sukuk_validation",
            status=ComplianceStatus.COMPLIANT,
            details="Sukuk structure is Shariah-compliant",
            recommendations=["Proceed with issuance"],
            timestamp=datetime.now(),
            checker_id=self.__class__.__name__
        )
    
    def validate_murabaha_contract(self, contract: MurabahaContract) -> IslamicComplianceCheck:
        """
        Validate Murabaha contract for Shariah compliance.
        
        Args:
            contract: Murabaha contract to validate
            
        Returns:
            Compliance check result
        """
        self.logger.info(f"Validating Murabaha contract: {contract.contract_id}")
        
        # Check markup
        if contract.markup <= 0:
            return IslamicComplianceCheck(
                check_type="murabaha_validation",
                status=ComplianceStatus.NON_COMPLIANT,
                details="Markup must be positive",
                recommendations=["Set appropriate markup rate"],
                timestamp=datetime.now(),
                checker_id=self.__class__.__name__
            )
        
        # Check selling price calculation
        expected_selling_price = contract.cost_price * (1 + contract.markup)
        if abs(contract.selling_price - expected_selling_price) > 0.01:
            return IslamicComplianceCheck(
                check_type="murabaha_validation",
                status=ComplianceStatus.REQUIRES_REVIEW,
                details="Selling price does not match cost + markup",
                recommendations=["Verify price calculation"],
                timestamp=datetime.now(),
                checker_id=self.__class__.__name__
            )
        
        # Check asset description
        if not contract.asset_description:
            return IslamicComplianceCheck(
                check_type="murabaha_validation",
                status=ComplianceStatus.NON_COMPLIANT,
                details="Asset description required",
                recommendations=["Provide detailed asset description"],
                timestamp=datetime.now(),
                checker_id=self.__class__.__name__
            )
        
        return IslamicComplianceCheck(
            check_type="murabaha_validation",
            status=ComplianceStatus.COMPLIANT,
            details="Murabaha contract is Shariah-compliant",
            recommendations=["Proceed with contract execution"],
            timestamp=datetime.now(),
            checker_id=self.__class__.__name__
        )
    
    def get_compliance_summary(self, checks: List[IslamicComplianceCheck]) -> Dict[str, Any]:
        """
        Generate compliance summary from multiple checks.
        
        Args:
            checks: List of compliance checks
            
        Returns:
            Compliance summary
        """
        total_checks = len(checks)
        compliant = sum(1 for check in checks if check.status == ComplianceStatus.COMPLIANT)
        non_compliant = sum(1 for check in checks if check.status == ComplianceStatus.NON_COMPLIANT)
        conditional = sum(1 for check in checks if check.status == ComplianceStatus.CONDITIONAL)
        requires_review = sum(1 for check in checks if check.status == ComplianceStatus.REQUIRES_REVIEW)
        
        compliance_rate = (compliant / total_checks * 100) if total_checks > 0 else 0
        
        return {
            "total_checks": total_checks,
            "compliant": compliant,
            "non_compliant": non_compliant,
            "conditional": conditional,
            "requires_review": requires_review,
            "compliance_rate": round(compliance_rate, 2),
            "overall_status": "compliant" if compliance_rate >= 90 else "requires_attention",
            "summary_date": datetime.now().isoformat(),
            "checks": [
                {
                    "type": check.check_type,
                    "status": check.status.value,
                    "details": check.details
                }
                for check in checks
            ]
        }
    
    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information - must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_compliance_history(self, entity_id: str) -> List[IslamicComplianceCheck]:
        """Get compliance history for an entity - must be implemented by subclasses."""
        pass

# Utility functions
def is_riba_compliant(transaction: Dict[str, Any]) -> bool:
    """Quick check if transaction is Riba-compliant."""
    service = BaseIslamicFinanceService()
    check = service.validate_riba(transaction)
    return check.status == ComplianceStatus.COMPLIANT

def is_gharar_compliant(contract: Dict[str, Any]) -> bool:
    """Quick check if contract is Gharar-compliant."""
    service = BaseIslamicFinanceService()
    check = service.validate_gharar(contract)
    return check.status == ComplianceStatus.COMPLIANT

def calculate_quick_zakat(assets: Dict[str, float]) -> float:
    """Quick Zakat calculation."""
    service = BaseIslamicFinanceService()
    result = service.calculate_zakat(assets)
    return result.zakat_amount if result.is_zakatable else 0.0 