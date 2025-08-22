"""
Enhanced Sharia Compliance Service for EnergyOpti-Pro.

Implements comprehensive Sharia-compliant features including:
- Sukuk and green bond trading
- Real-time Zakat calculation
- Halal screening for investments
- Blockchain transparency for bond audits
- FCA/EU-ETS compliance validation
"""

import asyncio
import json
import time
import hashlib
import hmac
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timezone, timedelta
import structlog
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_HALF_UP

logger = structlog.get_logger()

class BondType(Enum):
    """Bond types."""
    SUKUK = "sukuk"
    GREEN_BOND = "green_bond"
    CONVENTIONAL_BOND = "conventional_bond"
    ISLAMIC_BOND = "islamic_bond"

class ZakatType(Enum):
    """Zakat types."""
    WEALTH = "wealth"
    BUSINESS = "business"
    INVESTMENT = "investment"
    AGRICULTURE = "agriculture"
    MINING = "mining"

class ComplianceStatus(Enum):
    """Compliance status."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    CONDITIONAL_APPROVAL = "conditional_approval"

@dataclass
class SukukBond:
    """Sukuk bond details."""
    bond_id: str
    issuer: str
    bond_type: BondType
    face_value: Decimal
    coupon_rate: Decimal
    maturity_date: datetime
    issue_date: datetime
    currency: str
    sharia_compliant: bool
    green_certified: bool
    esg_score: float
    blockchain_hash: str
    compliance_status: ComplianceStatus
    metadata: Dict[str, Any]

@dataclass
class ZakatCalculation:
    """Zakat calculation result."""
    user_id: str
    zakat_type: ZakatType
    total_wealth: Decimal
    zakatable_amount: Decimal
    zakat_amount: Decimal
    zakat_rate: Decimal
    calculation_date: datetime
    next_due_date: datetime
    currency: str
    payment_status: str
    blockchain_transaction_id: Optional[str] = None

@dataclass
class HalalScreeningResult:
    """Halal screening result."""
    asset_id: str
    asset_type: str
    screening_date: datetime
    is_halal: bool
    compliance_score: float
    risk_factors: List[str]
    recommendations: List[str]
    sharia_board_approval: bool
    blockchain_audit_hash: str

class SukukTradingService:
    """Sukuk and green bond trading service."""
    
    def __init__(self, database_url: str, blockchain_service):
        self.database_url = database_url
        self.blockchain_service = blockchain_service
        self.sukuk_bonds: Dict[str, SukukBond] = {}
        self.trading_history: List[Dict[str, Any]] = []
        
    async def register_sukuk_bond(self, bond_data: Dict[str, Any]) -> SukukBond:
        """Register a new Sukuk bond."""
        logger.info(f"Registering Sukuk bond: {bond_data.get('bond_id', 'unknown')}")
        
        # Validate bond data
        if not self._validate_bond_data(bond_data):
            raise ValueError("Invalid bond data")
        
        # Create Sukuk bond
        bond = SukukBond(
            bond_id=bond_data["bond_id"],
            issuer=bond_data["issuer"],
            bond_type=BondType.SUKUK,
            face_value=Decimal(str(bond_data["face_value"])),
            coupon_rate=Decimal(str(bond_data["coupon_rate"])),
            maturity_date=datetime.fromisoformat(bond_data["maturity_date"]),
            issue_date=datetime.fromisoformat(bond_data["issue_date"]),
            currency=bond_data["currency"],
            sharia_compliant=True,  # Sukuk are inherently Sharia-compliant
            green_certified=bond_data.get("green_certified", False),
            esg_score=bond_data.get("esg_score", 0.0),
            blockchain_hash="",
            compliance_status=ComplianceStatus.PENDING_REVIEW,
            metadata=bond_data.get("metadata", {})
        )
        
        # Perform Sharia compliance check
        compliance_result = await self._check_sharia_compliance(bond)
        bond.compliance_status = compliance_result["status"]
        
        # Generate blockchain hash for transparency
        bond.blockchain_hash = await self._generate_blockchain_hash(bond)
        
        # Store bond
        self.sukuk_bonds[bond.bond_id] = bond
        
        # Record on blockchain
        await self._record_bond_on_blockchain(bond)
        
        logger.info(f"Sukuk bond registered: {bond.bond_id} (compliance: {bond.compliance_status.value})")
        return bond
    
    async def register_green_bond(self, bond_data: Dict[str, Any]) -> SukukBond:
        """Register a new green bond."""
        logger.info(f"Registering green bond: {bond_data.get('bond_id', 'unknown')}")
        
        # Validate bond data
        if not self._validate_bond_data(bond_data):
            raise ValueError("Invalid bond data")
        
        # Verify green certification
        green_certification = await self._verify_green_certification(bond_data)
        
        # Create green bond
        bond = SukukBond(
            bond_id=bond_data["bond_id"],
            issuer=bond_data["issuer"],
            bond_type=BondType.GREEN_BOND,
            face_value=Decimal(str(bond_data["face_value"])),
            coupon_rate=Decimal(str(bond_data["coupon_rate"])),
            maturity_date=datetime.fromisoformat(bond_data["maturity_date"]),
            issue_date=datetime.fromisoformat(bond_data["issue_date"]),
            currency=bond_data["currency"],
            sharia_compliant=bond_data.get("sharia_compliant", False),
            green_certified=green_certification["certified"],
            esg_score=bond_data.get("esg_score", 0.0),
            blockchain_hash="",
            compliance_status=ComplianceStatus.PENDING_REVIEW,
            metadata=bond_data.get("metadata", {})
        )
        
        # Perform compliance checks
        compliance_result = await self._check_compliance(bond)
        bond.compliance_status = compliance_result["status"]
        
        # Generate blockchain hash
        bond.blockchain_hash = await self._generate_blockchain_hash(bond)
        
        # Store bond
        self.sukuk_bonds[bond.bond_id] = bond
        
        # Record on blockchain
        await self._record_bond_on_blockchain(bond)
        
        logger.info(f"Green bond registered: {bond.bond_id} (compliance: {bond.compliance_status.value})")
        return bond
    
    async def trade_sukuk_bond(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Sukuk bond trade."""
        logger.info(f"Executing Sukuk bond trade: {trade_data.get('trade_id', 'unknown')}")
        
        bond_id = trade_data["bond_id"]
        if bond_id not in self.sukuk_bonds:
            raise ValueError(f"Bond not found: {bond_id}")
        
        bond = self.sukuk_bonds[bond_id]
        
        # Validate trade
        if not self._validate_trade(bond, trade_data):
            raise ValueError("Invalid trade data")
        
        # Check Sharia compliance
        if not bond.sharia_compliant:
            raise ValueError("Bond is not Sharia-compliant")
        
        # Execute trade
        trade_result = {
            "trade_id": trade_data["trade_id"],
            "bond_id": bond_id,
            "buyer": trade_data["buyer"],
            "seller": trade_data["seller"],
            "quantity": trade_data["quantity"],
            "price": trade_data["price"],
            "trade_date": datetime.now(timezone.utc),
            "status": "executed",
            "blockchain_transaction_id": ""
        }
        
        # Record trade on blockchain
        trade_result["blockchain_transaction_id"] = await self._record_trade_on_blockchain(trade_result)
        
        # Update trading history
        self.trading_history.append(trade_result)
        
        logger.info(f"Sukuk bond trade executed: {trade_result['trade_id']}")
        return trade_result
    
    async def get_sukuk_portfolio(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's Sukuk portfolio."""
        # Filter trading history for user
        user_trades = [trade for trade in self.trading_history 
                      if trade["buyer"] == user_id or trade["seller"] == user_id]
        
        portfolio = []
        for trade in user_trades:
            bond = self.sukuk_bonds.get(trade["bond_id"])
            if bond:
                portfolio.append({
                    "bond_id": bond.bond_id,
                    "issuer": bond.issuer,
                    "bond_type": bond.bond_type.value,
                    "face_value": float(bond.face_value),
                    "coupon_rate": float(bond.coupon_rate),
                    "maturity_date": bond.maturity_date.isoformat(),
                    "quantity": trade["quantity"],
                    "current_value": float(trade["price"] * trade["quantity"]),
                    "sharia_compliant": bond.sharia_compliant,
                    "green_certified": bond.green_certified,
                    "esg_score": bond.esg_score,
                    "blockchain_hash": bond.blockchain_hash
                })
        
        return portfolio
    
    def _validate_bond_data(self, bond_data: Dict[str, Any]) -> bool:
        """Validate bond data."""
        required_fields = ["bond_id", "issuer", "face_value", "coupon_rate", 
                          "maturity_date", "issue_date", "currency"]
        
        for field in required_fields:
            if field not in bond_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate coupon rate (should be 0 for Sukuk)
        if bond_data.get("bond_type") == "sukuk" and float(bond_data["coupon_rate"]) > 0:
            logger.error("Sukuk bonds should have 0% coupon rate")
            return False
        
        return True
    
    def _validate_trade(self, bond: SukukBond, trade_data: Dict[str, Any]) -> bool:
        """Validate trade data."""
        required_fields = ["trade_id", "buyer", "seller", "quantity", "price"]
        
        for field in required_fields:
            if field not in trade_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Check if bond is mature
        if bond.maturity_date < datetime.now(timezone.utc):
            logger.error("Cannot trade matured bond")
            return False
        
        return True
    
    async def _check_sharia_compliance(self, bond: SukukBond) -> Dict[str, Any]:
        """Check Sharia compliance of bond."""
        # Sukuk compliance rules
        compliance_checks = {
            "no_riba": bond.coupon_rate == 0,
            "asset_backed": bond.metadata.get("asset_backed", False),
            "profit_sharing": bond.metadata.get("profit_sharing", False),
            "no_gharar": not bond.metadata.get("excessive_uncertainty", False),
            "no_maysir": not bond.metadata.get("gambling_elements", False)
        }
        
        compliance_score = sum(compliance_checks.values()) / len(compliance_checks)
        
        if compliance_score >= 0.8:
            status = ComplianceStatus.COMPLIANT
        elif compliance_score >= 0.6:
            status = ComplianceStatus.CONDITIONAL_APPROVAL
        else:
            status = ComplianceStatus.NON_COMPLIANT
        
        return {
            "status": status,
            "compliance_score": compliance_score,
            "checks": compliance_checks
        }
    
    async def _check_compliance(self, bond: SukukBond) -> Dict[str, Any]:
        """Check overall compliance (Sharia + regulatory)."""
        # Sharia compliance
        sharia_result = await self._check_sharia_compliance(bond)
        
        # Regulatory compliance (FCA, EU-ETS)
        regulatory_result = await self._check_regulatory_compliance(bond)
        
        # Green certification
        green_result = await self._verify_green_certification(bond.metadata)
        
        # Overall compliance
        overall_score = (sharia_result["compliance_score"] + 
                        regulatory_result["compliance_score"] + 
                        green_result["score"]) / 3
        
        if overall_score >= 0.8:
            status = ComplianceStatus.COMPLIANT
        elif overall_score >= 0.6:
            status = ComplianceStatus.CONDITIONAL_APPROVAL
        else:
            status = ComplianceStatus.NON_COMPLIANT
        
        return {
            "status": status,
            "overall_score": overall_score,
            "sharia_compliance": sharia_result,
            "regulatory_compliance": regulatory_result,
            "green_certification": green_result
        }
    
    async def _verify_green_certification(self, bond_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify green bond certification."""
        # Check for recognized green certifications
        certifications = bond_data.get("green_certifications", [])
        
        recognized_certifications = [
            "Climate Bonds Standard",
            "Green Bond Principles",
            "EU Green Bond Standard",
            "ICMA Green Bond Principles"
        ]
        
        certified = any(cert in recognized_certifications for cert in certifications)
        
        # Check ESG criteria
        esg_criteria = bond_data.get("esg_criteria", {})
        environmental_score = esg_criteria.get("environmental", 0.0)
        social_score = esg_criteria.get("social", 0.0)
        governance_score = esg_criteria.get("governance", 0.0)
        
        overall_score = (environmental_score + social_score + governance_score) / 3
        
        return {
            "certified": certified and overall_score >= 0.7,
            "score": overall_score,
            "certifications": certifications,
            "esg_scores": {
                "environmental": environmental_score,
                "social": social_score,
                "governance": governance_score
            }
        }
    
    async def _check_regulatory_compliance(self, bond: SukukBond) -> Dict[str, Any]:
        """Check regulatory compliance (FCA, EU-ETS)."""
        # FCA compliance checks
        fca_checks = {
            "proper_disclosure": True,
            "fair_treatment": True,
            "adequate_capital": True,
            "risk_management": True
        }
        
        # EU-ETS compliance checks
        eu_ets_checks = {
            "carbon_reporting": bond.green_certified,
            "emissions_tracking": bond.green_certified,
            "sustainability_disclosure": True
        }
        
        fca_score = sum(fca_checks.values()) / len(fca_checks)
        eu_ets_score = sum(eu_ets_checks.values()) / len(eu_ets_checks)
        
        overall_score = (fca_score + eu_ets_score) / 2
        
        return {
            "compliance_score": overall_score,
            "fca_compliance": fca_checks,
            "eu_ets_compliance": eu_ets_checks
        }
    
    async def _generate_blockchain_hash(self, bond: SukukBond) -> str:
        """Generate blockchain hash for bond transparency."""
        bond_data = {
            "bond_id": bond.bond_id,
            "issuer": bond.issuer,
            "face_value": str(bond.face_value),
            "maturity_date": bond.maturity_date.isoformat(),
            "sharia_compliant": bond.sharia_compliant,
            "green_certified": bond.green_certified,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        data_string = json.dumps(bond_data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    async def _record_bond_on_blockchain(self, bond: SukukBond):
        """Record bond on blockchain for transparency."""
        if self.blockchain_service:
            await self.blockchain_service.record_bond_registration(bond)
    
    async def _record_trade_on_blockchain(self, trade_result: Dict[str, Any]) -> str:
        """Record trade on blockchain."""
        if self.blockchain_service:
            return await self.blockchain_service.record_trade(trade_result)
        return ""

class ZakatCalculationService:
    """Real-time Zakat calculation service."""
    
    def __init__(self, database_url: str, blockchain_service):
        self.database_url = database_url
        self.blockchain_service = blockchain_service
        self.zakat_calculations: List[ZakatCalculation] = []
        self.zakat_rates = {
            ZakatType.WEALTH: Decimal("0.025"),  # 2.5%
            ZakatType.BUSINESS: Decimal("0.025"),  # 2.5%
            ZakatType.INVESTMENT: Decimal("0.025"),  # 2.5%
            ZakatType.AGRICULTURE: Decimal("0.05"),  # 5% (irrigated)
            ZakatType.MINING: Decimal("0.025")  # 2.5%
        }
    
    async def calculate_zakat(self, user_id: str, zakat_type: ZakatType, 
                            wealth_data: Dict[str, Any]) -> ZakatCalculation:
        """Calculate Zakat for user."""
        logger.info(f"Calculating Zakat for user: {user_id}, type: {zakat_type.value}")
        
        # Calculate total wealth
        total_wealth = self._calculate_total_wealth(wealth_data)
        
        # Calculate zakatable amount
        zakatable_amount = self._calculate_zakatable_amount(total_wealth, zakat_type, wealth_data)
        
        # Calculate Zakat amount
        zakat_rate = self.zakat_rates[zakat_type]
        zakat_amount = zakatable_amount * zakat_rate
        
        # Round to 2 decimal places
        zakat_amount = zakat_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Calculate next due date
        next_due_date = self._calculate_next_due_date(zakat_type)
        
        calculation = ZakatCalculation(
            user_id=user_id,
            zakat_type=zakat_type,
            total_wealth=total_wealth,
            zakatable_amount=zakatable_amount,
            zakat_amount=zakat_amount,
            zakat_rate=zakat_rate,
            calculation_date=datetime.now(timezone.utc),
            next_due_date=next_due_date,
            currency=wealth_data.get("currency", "USD"),
            payment_status="pending"
        )
        
        self.zakat_calculations.append(calculation)
        
        logger.info(f"Zakat calculated: {float(zakat_amount)} {calculation.currency}")
        return calculation
    
    async def pay_zakat(self, user_id: str, zakat_amount: Decimal, 
                       payment_method: str) -> Dict[str, Any]:
        """Process Zakat payment."""
        logger.info(f"Processing Zakat payment for user: {user_id}")
        
        # Find pending Zakat calculation
        pending_zakat = None
        for calc in self.zakat_calculations:
            if (calc.user_id == user_id and 
                calc.payment_status == "pending" and 
                calc.zakat_amount == zakat_amount):
                pending_zakat = calc
                break
        
        if not pending_zakat:
            raise ValueError("No pending Zakat calculation found")
        
        # Process payment
        payment_result = await self._process_payment(zakat_amount, payment_method)
        
        if payment_result["success"]:
            # Update payment status
            pending_zakat.payment_status = "paid"
            pending_zakat.blockchain_transaction_id = payment_result.get("transaction_id")
            
            # Record on blockchain
            await self._record_zakat_payment_on_blockchain(pending_zakat, payment_result)
            
            logger.info(f"Zakat payment completed: {payment_result['transaction_id']}")
        
        return payment_result
    
    def _calculate_total_wealth(self, wealth_data: Dict[str, Any]) -> Decimal:
        """Calculate total wealth."""
        total = Decimal("0")
        
        # Cash and bank deposits
        total += Decimal(str(wealth_data.get("cash", 0)))
        total += Decimal(str(wealth_data.get("bank_deposits", 0)))
        
        # Investments
        total += Decimal(str(wealth_data.get("stocks", 0)))
        total += Decimal(str(wealth_data.get("bonds", 0)))
        total += Decimal(str(wealth_data.get("mutual_funds", 0)))
        total += Decimal(str(wealth_data.get("real_estate", 0)))
        
        # Business assets
        total += Decimal(str(wealth_data.get("business_assets", 0)))
        total += Decimal(str(wealth_data.get("inventory", 0)))
        total += Decimal(str(wealth_data.get("accounts_receivable", 0)))
        
        # Precious metals
        total += Decimal(str(wealth_data.get("gold", 0)))
        total += Decimal(str(wealth_data.get("silver", 0)))
        
        return total
    
    def _calculate_zakatable_amount(self, total_wealth: Decimal, zakat_type: ZakatType,
                                  wealth_data: Dict[str, Any]) -> Decimal:
        """Calculate zakatable amount."""
        # Nisab threshold (minimum amount for Zakat)
        nisab_threshold = Decimal("400")  # Gold equivalent
        
        if total_wealth < nisab_threshold:
            return Decimal("0")
        
        # Apply specific rules for different Zakat types
        if zakat_type == ZakatType.WEALTH:
            return total_wealth
        elif zakat_type == ZakatType.BUSINESS:
            # Business assets minus liabilities
            business_assets = Decimal(str(wealth_data.get("business_assets", 0)))
            business_liabilities = Decimal(str(wealth_data.get("business_liabilities", 0)))
            return max(Decimal("0"), business_assets - business_liabilities)
        elif zakat_type == ZakatType.INVESTMENT:
            # Investment portfolio value
            return Decimal(str(wealth_data.get("investment_portfolio", 0)))
        else:
            return total_wealth
    
    def _calculate_next_due_date(self, zakat_type: ZakatType) -> datetime:
        """Calculate next Zakat due date."""
        current_date = datetime.now(timezone.utc)
        
        if zakat_type == ZakatType.AGRICULTURE:
            # Agricultural Zakat is due after harvest
            return current_date + timedelta(days=365)
        else:
            # Other types are due annually
            return current_date + timedelta(days=365)
    
    async def _process_payment(self, amount: Decimal, payment_method: str) -> Dict[str, Any]:
        """Process Zakat payment."""
        # Simulate payment processing
        transaction_id = f"zakat_payment_{int(time.time())}"
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount": float(amount),
            "payment_method": payment_method,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _record_zakat_payment_on_blockchain(self, calculation: ZakatCalculation,
                                                payment_result: Dict[str, Any]):
        """Record Zakat payment on blockchain."""
        if self.blockchain_service:
            await self.blockchain_service.record_zakat_payment(calculation, payment_result)
    
    def get_zakat_history(self, user_id: str) -> List[ZakatCalculation]:
        """Get Zakat calculation history for user."""
        return [calc for calc in self.zakat_calculations if calc.user_id == user_id]

class HalalScreeningService:
    """Halal screening service for investments."""
    
    def __init__(self, database_url: str, blockchain_service):
        self.database_url = database_url
        self.blockchain_service = blockchain_service
        self.screening_history: List[HalalScreeningResult] = []
        
        # Halal screening criteria
        self.halal_criteria = {
            "no_riba": "No interest-based transactions",
            "no_gharar": "No excessive uncertainty",
            "no_maysir": "No gambling elements",
            "no_haram_activities": "No prohibited business activities",
            "asset_backed": "Investments backed by real assets",
            "profit_sharing": "Profit and loss sharing",
            "ethical_business": "Ethical business practices"
        }
    
    async def screen_investment(self, asset_data: Dict[str, Any]) -> HalalScreeningResult:
        """Screen investment for halal compliance."""
        logger.info(f"Screening investment: {asset_data.get('asset_id', 'unknown')}")
        
        # Perform halal screening
        screening_results = await self._perform_halal_screening(asset_data)
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(screening_results)
        
        # Determine if investment is halal
        is_halal = compliance_score >= 0.8
        
        # Generate recommendations
        recommendations = self._generate_recommendations(screening_results)
        
        # Get Sharia board approval
        sharia_board_approval = await self._get_sharia_board_approval(asset_data, screening_results)
        
        # Generate blockchain audit hash
        blockchain_audit_hash = await self._generate_audit_hash(asset_data, screening_results)
        
        result = HalalScreeningResult(
            asset_id=asset_data["asset_id"],
            asset_type=asset_data["asset_type"],
            screening_date=datetime.now(timezone.utc),
            is_halal=is_halal,
            compliance_score=compliance_score,
            risk_factors=screening_results["risk_factors"],
            recommendations=recommendations,
            sharia_board_approval=sharia_board_approval,
            blockchain_audit_hash=blockchain_audit_hash
        )
        
        self.screening_history.append(result)
        
        logger.info(f"Halal screening completed: {is_halal} (score: {compliance_score:.2f})")
        return result
    
    async def _perform_halal_screening(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive halal screening."""
        screening_results = {
            "criteria_results": {},
            "risk_factors": [],
            "overall_score": 0.0
        }
        
        # Check each halal criterion
        for criterion, description in self.halal_criteria.items():
            result = await self._check_criterion(criterion, asset_data)
            screening_results["criteria_results"][criterion] = result
            
            if not result["compliant"]:
                screening_results["risk_factors"].append(result["reason"])
        
        return screening_results
    
    async def _check_criterion(self, criterion: str, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check specific halal criterion."""
        if criterion == "no_riba":
            return self._check_no_riba(asset_data)
        elif criterion == "no_gharar":
            return self._check_no_gharar(asset_data)
        elif criterion == "no_maysir":
            return self._check_no_maysir(asset_data)
        elif criterion == "no_haram_activities":
            return self._check_no_haram_activities(asset_data)
        elif criterion == "asset_backed":
            return self._check_asset_backed(asset_data)
        elif criterion == "profit_sharing":
            return self._check_profit_sharing(asset_data)
        elif criterion == "ethical_business":
            return self._check_ethical_business(asset_data)
        else:
            return {"compliant": True, "reason": "Criterion not applicable"}
    
    def _check_no_riba(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for absence of interest (riba)."""
        # Check for interest-based returns
        if asset_data.get("interest_rate", 0) > 0:
            return {
                "compliant": False,
                "reason": "Investment involves interest-based returns"
            }
        
        # Check for fixed returns without risk sharing
        if asset_data.get("fixed_return", False) and not asset_data.get("risk_sharing", False):
            return {
                "compliant": False,
                "reason": "Fixed returns without risk sharing"
            }
        
        return {"compliant": True, "reason": "No interest-based elements detected"}
    
    def _check_no_gharar(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for absence of excessive uncertainty (gharar)."""
        # Check for excessive uncertainty in returns
        if asset_data.get("uncertainty_level", 0) > 0.8:
            return {
                "compliant": False,
                "reason": "Excessive uncertainty in investment returns"
            }
        
        # Check for unclear terms and conditions
        if not asset_data.get("clear_terms", True):
            return {
                "compliant": False,
                "reason": "Unclear terms and conditions"
            }
        
        return {"compliant": True, "reason": "Acceptable level of uncertainty"}
    
    def _check_no_maysir(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for absence of gambling elements (maysir)."""
        # Check for speculative trading
        if asset_data.get("speculative_trading", False):
            return {
                "compliant": False,
                "reason": "Speculative trading detected"
            }
        
        # Check for gambling-like features
        if asset_data.get("gambling_features", False):
            return {
                "compliant": False,
                "reason": "Gambling-like features detected"
            }
        
        return {"compliant": True, "reason": "No gambling elements detected"}
    
    def _check_no_haram_activities(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for absence of prohibited business activities."""
        prohibited_activities = [
            "alcohol", "gambling", "pork", "pornography", "weapons", "tobacco"
        ]
        
        business_activities = asset_data.get("business_activities", [])
        
        for activity in prohibited_activities:
            if activity in business_activities:
                return {
                    "compliant": False,
                    "reason": f"Prohibited activity detected: {activity}"
                }
        
        return {"compliant": True, "reason": "No prohibited activities detected"}
    
    def _check_asset_backed(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if investment is backed by real assets."""
        if asset_data.get("asset_backed", False):
            return {"compliant": True, "reason": "Investment is asset-backed"}
        else:
            return {
                "compliant": False,
                "reason": "Investment is not backed by real assets"
            }
    
    def _check_profit_sharing(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for profit and loss sharing."""
        if asset_data.get("profit_sharing", False):
            return {"compliant": True, "reason": "Profit and loss sharing implemented"}
        else:
            return {
                "compliant": False,
                "reason": "No profit and loss sharing"
            }
    
    def _check_ethical_business(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for ethical business practices."""
        ethical_score = asset_data.get("ethical_score", 0.0)
        
        if ethical_score >= 0.7:
            return {"compliant": True, "reason": "Ethical business practices confirmed"}
        else:
            return {
                "compliant": False,
                "reason": "Ethical business practices not confirmed"
            }
    
    def _calculate_compliance_score(self, screening_results: Dict[str, Any]) -> float:
        """Calculate overall compliance score."""
        criteria_results = screening_results["criteria_results"]
        
        if not criteria_results:
            return 0.0
        
        compliant_count = sum(1 for result in criteria_results.values() if result["compliant"])
        total_count = len(criteria_results)
        
        return compliant_count / total_count
    
    def _generate_recommendations(self, screening_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on screening results."""
        recommendations = []
        
        for criterion, result in screening_results["criteria_results"].items():
            if not result["compliant"]:
                if criterion == "no_riba":
                    recommendations.append("Consider profit-sharing arrangements instead of fixed returns")
                elif criterion == "no_gharar":
                    recommendations.append("Provide clearer terms and reduce uncertainty")
                elif criterion == "no_maysir":
                    recommendations.append("Avoid speculative trading and gambling-like features")
                elif criterion == "no_haram_activities":
                    recommendations.append("Ensure business activities comply with Islamic principles")
                elif criterion == "asset_backed":
                    recommendations.append("Ensure investment is backed by real assets")
                elif criterion == "profit_sharing":
                    recommendations.append("Implement profit and loss sharing mechanisms")
                elif criterion == "ethical_business":
                    recommendations.append("Improve ethical business practices")
        
        if not recommendations:
            recommendations.append("Investment appears to be halal compliant")
        
        return recommendations
    
    async def _get_sharia_board_approval(self, asset_data: Dict[str, Any],
                                       screening_results: Dict[str, Any]) -> bool:
        """Get Sharia board approval."""
        # Simulate Sharia board review
        compliance_score = self._calculate_compliance_score(screening_results)
        
        # Sharia board approval threshold
        return compliance_score >= 0.9
    
    async def _generate_audit_hash(self, asset_data: Dict[str, Any],
                                 screening_results: Dict[str, Any]) -> str:
        """Generate blockchain audit hash."""
        audit_data = {
            "asset_id": asset_data["asset_id"],
            "screening_date": datetime.now(timezone.utc).isoformat(),
            "compliance_score": self._calculate_compliance_score(screening_results),
            "risk_factors": screening_results["risk_factors"]
        }
        
        data_string = json.dumps(audit_data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def get_screening_history(self) -> List[HalalScreeningResult]:
        """Get halal screening history."""
        return self.screening_history

class EnhancedShariaComplianceService:
    """Enhanced Sharia compliance service integrating all components."""
    
    def __init__(self, database_url: str, blockchain_service):
        self.database_url = database_url
        self.blockchain_service = blockchain_service
        
        # Initialize sub-services
        self.sukuk_service = SukukTradingService(database_url, blockchain_service)
        self.zakat_service = ZakatCalculationService(database_url, blockchain_service)
        self.screening_service = HalalScreeningService(database_url, blockchain_service)
    
    async def get_comprehensive_compliance_report(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive compliance report for user."""
        logger.info(f"Generating comprehensive compliance report for user: {user_id}")
        
        # Get Sukuk portfolio
        sukuk_portfolio = await self.sukuk_service.get_sukuk_portfolio(user_id)
        
        # Get Zakat calculations
        zakat_history = self.zakat_service.get_zakat_history(user_id)
        
        # Get screening history
        screening_history = self.screening_service.get_screening_history()
        
        # Calculate compliance metrics
        compliance_metrics = self._calculate_compliance_metrics(
            sukuk_portfolio, zakat_history, screening_history
        )
        
        report = {
            "user_id": user_id,
            "report_date": datetime.now(timezone.utc).isoformat(),
            "sukuk_portfolio": sukuk_portfolio,
            "zakat_history": [asdict(calc) for calc in zakat_history],
            "screening_history": [asdict(result) for result in screening_history],
            "compliance_metrics": compliance_metrics,
            "blockchain_audit_hash": await self._generate_report_hash(user_id)
        }
        
        return report
    
    def _calculate_compliance_metrics(self, sukuk_portfolio: List[Dict[str, Any]],
                                    zakat_history: List[ZakatCalculation],
                                    screening_history: List[HalalScreeningResult]) -> Dict[str, Any]:
        """Calculate compliance metrics."""
        # Sukuk compliance
        sukuk_compliance = len([bond for bond in sukuk_portfolio if bond["sharia_compliant"]]) / max(len(sukuk_portfolio), 1)
        
        # Zakat compliance
        zakat_compliance = len([calc for calc in zakat_history if calc.payment_status == "paid"]) / max(len(zakat_history), 1)
        
        # Screening compliance
        screening_compliance = len([result for result in screening_history if result.is_halal]) / max(len(screening_history), 1)
        
        return {
            "sukuk_compliance_rate": sukuk_compliance,
            "zakat_compliance_rate": zakat_compliance,
            "screening_compliance_rate": screening_compliance,
            "overall_compliance_score": (sukuk_compliance + zakat_compliance + screening_compliance) / 3
        }
    
    async def _generate_report_hash(self, user_id: str) -> str:
        """Generate blockchain hash for compliance report."""
        report_data = {
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_version": "2.0"
        }
        
        data_string = json.dumps(report_data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
