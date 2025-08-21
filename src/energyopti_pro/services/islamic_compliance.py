import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests
from hijri_converter import Gregorian
import json
import uuid
from decimal import Decimal, ROUND_HALF_UP

from .islamic_finance.base_service import (
    BaseIslamicFinanceService, 
    IslamicComplianceCheck, 
    ComplianceStatus,
    ZakatCalculation,
    SukukStructure,
    MurabahaContract
)

class IslamicComplianceService(BaseIslamicFinanceService):
    """Comprehensive Islamic compliance service for Middle East operations"""
    
    def __init__(self):
        super().__init__()
        
        # Islamic finance principles
        self.islamic_principles = {
            "riba_prohibition": "No interest-based transactions",
            "gharar_prohibition": "No excessive uncertainty",
            "maysir_prohibition": "No gambling or speculation",
            "halal_investment": "Only Sharia-compliant investments",
            "asset_backed": "All transactions must be asset-backed",
            "ethical_business": "No alcohol, gambling, or pork-related businesses",
            "zakat_obligation": "Annual charitable giving requirement",
            "qard_hasan": "Interest-free benevolent loans",
            "takaful": "Islamic insurance based on mutual assistance"
        }
        
        # Sharia-compliant trading structures
        self.sharia_structures = {
            "murabaha": {
                "name": "Cost-plus financing",
                "description": "Sale with disclosed profit margin",
                "sharia_compliant": True,
                "risk_level": "Low",
                "suitable_for": ["Equipment financing", "Real estate", "Trade finance"]
            },
            "ijara": {
                "name": "Lease-based financing",
                "description": "Asset leasing with ownership transfer option",
                "sharia_compliant": True,
                "risk_level": "Medium",
                "suitable_for": ["Real estate", "Equipment", "Vehicles"]
            },
            "sukuk": {
                "name": "Islamic bonds",
                "description": "Asset-backed securities",
                "sharia_compliant": True,
                "risk_level": "Medium",
                "suitable_for": ["Infrastructure", "Government projects", "Corporate finance"]
            },
            "musharaka": {
                "name": "Partnership financing",
                "description": "Joint venture with profit/loss sharing",
                "sharia_compliant": True,
                "risk_level": "High",
                "suitable_for": ["Business ventures", "Real estate", "Joint projects"]
            },
            "wakala": {
                "name": "Agency-based financing",
                "description": "Investment management for fee",
                "sharia_compliant": True,
                "risk_level": "Low",
                "suitable_for": ["Fund management", "Investment advisory"]
            },
            "istisna": {
                "name": "Manufacturing contract",
                "description": "Forward contract for manufactured goods",
                "sharia_compliant": True,
                "risk_level": "Medium",
                "suitable_for": ["Construction", "Manufacturing", "Infrastructure"]
            },
            "salam": {
                "name": "Forward sale contract",
                "description": "Advance payment for future delivery",
                "sharia_compliant": True,
                "risk_level": "Medium",
                "suitable_for": ["Agricultural products", "Commodities"]
            }
        }
        
        # Islamic calendar months
        self.islamic_months = [
            "Muharram", "Safar", "Rabi al-Awwal", "Rabi al-Thani",
            "Jumada al-Awwal", "Jumada al-Thani", "Rajab", "Sha'ban",
            "Ramadan", "Shawwal", "Dhu al-Qadah", "Dhu al-Hijjah"
        ]
        
        # Compliance check history
        self.compliance_history = {}
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information."""
        return {
            "service_name": "Islamic Compliance Service",
            "version": "1.0",
            "principles_count": len(self.islamic_principles),
            "structures_count": len(self.sharia_structures),
            "compliance_rules": self.compliance_rules,
            "zakat_rates": self.zakat_rates
        }
    
    def get_compliance_history(self, entity_id: str) -> List[IslamicComplianceCheck]:
        """Get compliance history for an entity."""
        return self.compliance_history.get(entity_id, [])
    
    async def check_trade_compliance(
        self, 
        trade_data: Dict[str, Any]
    ) -> IslamicComplianceCheck:
        """
        Check if a trade complies with Islamic principles.
        
        Args:
            trade_data: Trade data to check
            
        Returns:
            Compliance check result
        """
        self.logger.info(f"Checking trade compliance: {trade_data.get('id', 'unknown')}")
        
        # Perform all compliance checks
        riba_check = self.validate_riba(trade_data)
        gharar_check = self.validate_gharar(trade_data)
        maysir_check = self.validate_maysir(trade_data)
        
        checks = [riba_check, gharar_check, maysir_check]
        
        # Store in history
        entity_id = trade_data.get("entity_id", "unknown")
        if entity_id not in self.compliance_history:
            self.compliance_history[entity_id] = []
        self.compliance_history[entity_id].extend(checks)
        
        # Generate summary
        summary = self.get_compliance_summary(checks)
        
        # Determine overall status
        if summary["overall_status"] == "compliant":
            overall_status = ComplianceStatus.COMPLIANT
            details = "Trade is fully Shariah-compliant"
        else:
            overall_status = ComplianceStatus.REQUIRES_REVIEW
            details = f"Trade requires attention: {summary['compliance_rate']}% compliance"
        
        return IslamicComplianceCheck(
            check_type="trade_compliance",
            status=overall_status,
            details=details,
            recommendations=summary.get("recommendations", []),
            timestamp=datetime.now(),
            checker_id=self.__class__.__name__,
            metadata=summary
        )
    
    async def check_portfolio_compliance(
        self, 
        portfolio: Dict[str, Any]
    ) -> List[IslamicComplianceCheck]:
        """
        Check portfolio compliance with Islamic principles.
        
        Args:
            portfolio: Portfolio data to check
            
        Returns:
            List of compliance checks
        """
        self.logger.info(f"Checking portfolio compliance: {portfolio.get('id', 'unknown')}")
        
        checks = []
        
        # Check each holding
        for holding in portfolio.get("holdings", []):
            holding_check = await self.check_trade_compliance(holding)
            checks.append(holding_check)
        
        # Check overall portfolio structure
        portfolio_check = IslamicComplianceCheck(
            check_type="portfolio_structure",
            status=ComplianceStatus.COMPLIANT,
            details="Portfolio structure analysis complete",
            recommendations=["Monitor individual holdings for compliance"],
            timestamp=datetime.now(),
            checker_id=self.__class__.__name__,
            metadata={"total_holdings": len(portfolio.get("holdings", []))}
        )
        checks.append(portfolio_check)
        
        return checks
    
    async def calculate_portfolio_zakat(
        self, 
        portfolio: Dict[str, Any]
    ) -> ZakatCalculation:
        """
        Calculate Zakat for portfolio assets.
        
        Args:
            portfolio: Portfolio data
            
        Returns:
            Zakat calculation result
        """
        self.logger.info(f"Calculating portfolio Zakat: {portfolio.get('id', 'unknown')}")
        
        # Extract asset values
        assets = {}
        for holding in portfolio.get("holdings", []):
            asset_type = holding.get("asset_type", "cash")
            value = holding.get("market_value", 0)
            
            if asset_type in assets:
                assets[asset_type] += value
            else:
                assets[asset_type] = value
        
        # Use base class Zakat calculation
        return self.calculate_zakat(assets)
    
    async def validate_sukuk_issuance(
        self, 
        sukuk_data: Dict[str, Any]
    ) -> IslamicComplianceCheck:
        """
        Validate Sukuk issuance for Shariah compliance.
        
        Args:
            sukuk_data: Sukuk data to validate
            
        Returns:
            Compliance check result
        """
        self.logger.info(f"Validating Sukuk issuance: {sukuk_data.get('id', 'unknown')}")
        
        # Create SukukStructure object
        sukuk = SukukStructure(
            sukuk_id=sukuk_data.get("id", ""),
            type=sukuk_data.get("type"),
            face_value=sukuk_data.get("face_value", 0),
            maturity_date=sukuk_data.get("maturity_date"),
            profit_rate=sukuk_data.get("profit_rate", 0),
            underlying_asset=sukuk_data.get("underlying_asset", ""),
            asset_value=sukuk_data.get("asset_value", 0),
            compliance_status=ComplianceStatus.PENDING_APPROVAL,
            issuance_date=datetime.now(),
            metadata=sukuk_data
        )
        
        # Use base class validation
        return self.validate_sukuk_structure(sukuk)
    
    async def validate_murabaha_contract(
        self, 
        contract_data: Dict[str, Any]
    ) -> IslamicComplianceCheck:
        """
        Validate Murabaha contract for Shariah compliance.
        
        Args:
            contract_data: Contract data to validate
            
        Returns:
            Compliance check result
        """
        self.logger.info(f"Validating Murabaha contract: {contract_data.get('id', 'unknown')}")
        
        # Create MurabahaContract object
        contract = MurabahaContract(
            contract_id=contract_data.get("id", ""),
            asset_description=contract_data.get("asset_description", ""),
            cost_price=contract_data.get("cost_price", 0),
            markup=contract_data.get("markup", 0),
            selling_price=contract_data.get("selling_price", 0),
            payment_terms=contract_data.get("payment_terms", ""),
            delivery_date=contract_data.get("delivery_date"),
            compliance_status=ComplianceStatus.PENDING_APPROVAL,
            contract_date=datetime.now(),
            metadata=contract_data
        )
        
        # Use base class validation
        return self.validate_murabaha_contract(contract)
    
    async def get_islamic_calendar_info(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get Islamic calendar information for a date.
        
        Args:
            date: Date to convert (defaults to current date)
            
        Returns:
            Islamic calendar information
        """
        if not date:
            date = datetime.now()
        
        try:
            hijri_date = Gregorian(date.year, date.month, date.day).to_hijri()
            
            return {
                "gregorian_date": date.strftime("%Y-%m-%d"),
                "hijri_date": f"{hijri_date.year}-{hijri_date.month:02d}-{hijri_date.day:02d}",
                "hijri_year": hijri_date.year,
                "hijri_month": hijri_date.month,
                "hijri_day": hijri_date.day,
                "hijri_month_name": self.islamic_months[hijri_date.month - 1],
                "is_ramadan": hijri_date.month == 9,
                "is_eid_al_fitr": hijri_date.month == 10 and hijri_date.day <= 3,
                "is_eid_al_adha": hijri_date.month == 12 and hijri_date.day >= 10 and hijri_date.day <= 13
            }
        except Exception as e:
            self.logger.error(f"Error converting to Hijri date: {e}")
            return {
                "error": "Unable to convert date",
                "gregorian_date": date.strftime("%Y-%m-%d")
            }
    
    async def get_compliance_report(
        self, 
        entity_id: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive compliance report.
        
        Args:
            entity_id: Entity identifier
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Compliance report
        """
        self.logger.info(f"Generating compliance report for entity: {entity_id}")
        
        # Get compliance history
        history = self.get_compliance_history(entity_id)
        
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)
        if not end_date:
            end_date = datetime.now()
        
        # Filter by date range
        filtered_history = [
            check for check in history
            if start_date <= check.timestamp <= end_date
        ]
        
        # Generate summary
        summary = self.get_compliance_summary(filtered_history)
        
        # Add entity-specific information
        report = {
            "entity_id": entity_id,
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "compliance_summary": summary,
            "total_checks": len(filtered_history),
            "compliance_trend": self._calculate_compliance_trend(filtered_history),
            "recommendations": self._generate_recommendations(summary),
            "report_generated": datetime.now().isoformat(),
            "service_version": "1.0"
        }
        
        return report
    
    def _calculate_compliance_trend(self, checks: List[IslamicComplianceCheck]) -> str:
        """Calculate compliance trend over time."""
        if len(checks) < 2:
            return "insufficient_data"
        
        # Sort by timestamp
        sorted_checks = sorted(checks, key=lambda x: x.timestamp)
        
        # Calculate trend
        first_half = sorted_checks[:len(sorted_checks)//2]
        second_half = sorted_checks[len(sorted_checks)//2:]
        
        first_compliance = sum(1 for c in first_half if c.status == ComplianceStatus.COMPLIANT) / len(first_half)
        second_compliance = sum(1 for c in second_half if c.status == ComplianceStatus.COMPLIANT) / len(second_half)
        
        if second_compliance > first_compliance + 0.1:
            return "improving"
        elif second_compliance < first_compliance - 0.1:
            return "declining"
        else:
            return "stable"
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on compliance summary."""
        recommendations = []
        
        if summary["compliance_rate"] < 90:
            recommendations.append("Immediate attention required for compliance issues")
        
        if summary["non_compliant"] > 0:
            recommendations.append("Address non-compliant items promptly")
        
        if summary["requires_review"] > 0:
            recommendations.append("Review items requiring attention")
        
        if summary["compliance_rate"] >= 95:
            recommendations.append("Excellent compliance - maintain current standards")
        
        return recommendations

# Utility functions for easy access
async def check_trade_compliance(trade_data: Dict[str, Any]) -> IslamicComplianceCheck:
    """Check trade compliance using default service."""
    service = IslamicComplianceService()
    return await service.check_trade_compliance(trade_data)

async def calculate_portfolio_zakat(portfolio: Dict[str, Any]) -> ZakatCalculation:
    """Calculate portfolio Zakat using default service."""
    service = IslamicComplianceService()
    return await service.calculate_portfolio_zakat(portfolio)

async def get_islamic_calendar_info(date: Optional[datetime] = None) -> Dict[str, Any]:
    """Get Islamic calendar info using default service."""
    service = IslamicComplianceService()
    return await service.get_islamic_calendar_info(date) 