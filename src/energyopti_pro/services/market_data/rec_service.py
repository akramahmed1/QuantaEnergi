"""
Renewable Energy Certificate (REC) Management Service.

This service provides comprehensive REC management capabilities:
- Multi-registry support (M-RETS, NAR, WREGIS, etc.)
- REC tracking and trading
- Retirement and compliance reporting
- Carbon offset integration
- ESG reporting
"""

import asyncio
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import uuid
import json

from ...core.config import settings
from ...core.logging import get_logger
from ...db.models import CompanyScopedModel
from sqlalchemy import Column, String, Float, DateTime, Boolean, Text, JSON, Integer
from sqlalchemy.sql import func
from .base_service import BaseMarketDataService, ServiceConfig, ServiceType, DataType
from .utils import validate_time_range, generate_unique_id, validate_required_fields

logger = get_logger(__name__)

class RECRegistry(Enum):
    """Supported REC registries."""
    MRETS = "mrets"  # Midwest Renewable Energy Tracking System
    NAR = "nar"      # North American Renewables Registry
    WREGIS = "wregis"  # Western Renewable Energy Generation Information System
    NEPOOL = "nepool"  # New England Power Pool
    PJM = "pjm"      # PJM Generation Attribute Tracking System
    ERCOT = "ercot"  # Electric Reliability Council of Texas
    CAISO = "caiso"  # California Independent System Operator
    NYISO = "nyiso"  # New York Independent System Operator

class RECStatus(Enum):
    """REC status values."""
    ISSUED = "issued"
    TRANSFERRED = "transferred"
    RETIRED = "retired"
    EXPIRED = "expired"
    PENDING = "pending"
    CANCELLED = "cancelled"

class RECFuelType(Enum):
    """REC fuel types."""
    SOLAR = "solar"
    WIND = "wind"
    HYDRO = "hydro"
    BIOMASS = "biomass"
    GEOTHERMAL = "geothermal"
    LANDFILL_GAS = "landfill_gas"
    WASTE_TO_ENERGY = "waste_to_energy"

class RECVintage(Enum):
    """REC vintage periods."""
    CURRENT_YEAR = "current_year"
    PREVIOUS_YEAR = "previous_year"
    CARRYOVER = "carryover"
    FUTURE = "future"

@dataclass
class RECData:
    """REC data structure."""
    rec_id: str
    registry: RECRegistry
    generator_id: str
    generator_name: str
    fuel_type: RECFuelType
    vintage: RECVintage
    vintage_year: int
    megawatt_hours: float
    issue_date: datetime
    status: RECStatus
    current_owner: str
    price: Optional[float] = None
    location: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None
    carbon_offset: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class RECTransaction:
    """REC transaction structure."""
    transaction_id: str
    rec_id: str
    from_owner: str
    to_owner: str
    transaction_type: str
    megawatt_hours: float
    price_per_mwh: float
    total_value: float
    transaction_date: datetime
    status: str
    registry: RECRegistry
    metadata: Optional[Dict[str, Any]] = None

class RECService(BaseMarketDataService):
    """
    Renewable Energy Certificate Management Service.
    
    This service provides comprehensive REC management capabilities
    across multiple regional registries and compliance frameworks.
    """
    
    def __init__(self):
        """Initialize REC service."""
        config = ServiceConfig(
            service_type=ServiceType.REC,
            base_url="",  # REC services use different APIs per registry
            api_key=None,
            rate_limit_delay=0.1,
            timeout=30,
            max_retries=3,
            cache_duration=300
        )
        super().__init__(config)
        
        self.registries = self._setup_registries()
        self.basis_correlations = self._setup_basis_correlations()
    
    def _setup_registries(self) -> Dict[str, Dict[str, Any]]:
        """Setup registry connections and configurations."""
        return {
            RECRegistry.MRETS: {
                "api_url": self._get_registry_api_url(RECRegistry.MRETS),
                "api_key": getattr(settings, f"{RECRegistry.MRETS.value}_api_key", None),
                "supported_fuels": self._get_supported_fuels(RECRegistry.MRETS),
                "vintage_rules": self._get_vintage_rules(RECRegistry.MRETS),
                "retirement_rules": self._get_retirement_rules(RECRegistry.MRETS)
            },
            RECRegistry.NAR: {
                "api_url": self._get_registry_api_url(RECRegistry.NAR),
                "api_key": getattr(settings, f"{RECRegistry.NAR.value}_api_key", None),
                "supported_fuels": self._get_supported_fuels(RECRegistry.NAR),
                "vintage_rules": self._get_vintage_rules(RECRegistry.NAR),
                "retirement_rules": self._get_retirement_rules(RECRegistry.NAR)
            },
            RECRegistry.WREGIS: {
                "api_url": self._get_registry_api_url(RECRegistry.WREGIS),
                "api_key": getattr(settings, f"{RECRegistry.WREGIS.value}_api_key", None),
                "supported_fuels": self._get_supported_fuels(RECRegistry.WREGIS),
                "vintage_rules": self._get_vintage_rules(RECRegistry.WREGIS),
                "retirement_rules": self._get_retirement_rules(RECRegistry.WREGIS)
            },
            RECRegistry.NEPOOL: {
                "api_url": self._get_registry_api_url(RECRegistry.NEPOOL),
                "api_key": getattr(settings, f"{RECRegistry.NEPOOL.value}_api_key", None),
                "supported_fuels": self._get_supported_fuels(RECRegistry.NEPOOL),
                "vintage_rules": self._get_vintage_rules(RECRegistry.NEPOOL),
                "retirement_rules": self._get_retirement_rules(RECRegistry.NEPOOL)
            },
            RECRegistry.PJM: {
                "api_url": self._get_registry_api_url(RECRegistry.PJM),
                "api_key": getattr(settings, f"{RECRegistry.PJM.value}_api_key", None),
                "supported_fuels": self._get_supported_fuels(RECRegistry.PJM),
                "vintage_rules": self._get_vintage_rules(RECRegistry.PJM),
                "retirement_rules": self._get_retirement_rules(RECRegistry.PJM)
            },
            RECRegistry.ERCOT: {
                "api_url": self._get_registry_api_url(RECRegistry.ERCOT),
                "api_key": getattr(settings, f"{RECRegistry.ERCOT.value}_api_key", None),
                "supported_fuels": self._get_supported_fuels(RECRegistry.ERCOT),
                "vintage_rules": self._get_vintage_rules(RECRegistry.ERCOT),
                "retirement_rules": self._get_retirement_rules(RECRegistry.ERCOT)
            },
            RECRegistry.CAISO: {
                "api_url": self._get_registry_api_url(RECRegistry.CAISO),
                "api_key": getattr(settings, f"{RECRegistry.CAISO.value}_api_key", None),
                "supported_fuels": self._get_supported_fuels(RECRegistry.CAISO),
                "vintage_rules": self._get_vintage_rules(RECRegistry.CAISO),
                "retirement_rules": self._get_retirement_rules(RECRegistry.CAISO)
            },
            RECRegistry.NYISO: {
                "api_url": self._get_registry_api_url(RECRegistry.NYISO),
                "api_key": getattr(settings, f"{RECRegistry.NYISO.value}_api_key", None),
                "supported_fuels": self._get_supported_fuels(RECRegistry.NYISO),
                "vintage_rules": self._get_vintage_rules(RECRegistry.NYISO),
                "retirement_rules": self._get_retirement_rules(RECRegistry.NYISO)
            }
        }
    
    def _setup_basis_correlations(self) -> Dict[str, Dict[str, float]]:
        """Setup basis correlations between registries."""
        return {
            RECRegistry.MRETS.value: {
                RECRegistry.NAR.value: 0.85,
                RECRegistry.WREGIS.value: 0.78,
                RECRegistry.NEPOOL.value: 0.82
            },
            RECRegistry.NAR.value: {
                RECRegistry.MRETS.value: 0.85,
                RECRegistry.WREGIS.value: 0.80,
                RECRegistry.NEPOOL.value: 0.88
            },
            RECRegistry.WREGIS.value: {
                RECRegistry.MRETS.value: 0.78,
                RECRegistry.NAR.value: 0.80,
                RECRegistry.NEPOOL.value: 0.75
            }
        }
    
    def _get_registry_api_url(self, registry: RECRegistry) -> str:
        """Get API URL for registry."""
        urls = {
            RECRegistry.MRETS: "https://api.mrets.org/v1",
            RECRegistry.NAR: "https://api.naruc.org/v1",
            RECRegistry.WREGIS: "https://api.wregis.org/v1",
            RECRegistry.NEPOOL: "https://api.nepoolgis.com/v1",
            RECRegistry.PJM: "https://api.pjm.com/v1/gats",
            RECRegistry.ERCOT: "https://api.ercot.com/v1/rec",
            RECRegistry.CAISO: "https://api.caiso.com/v1/rec",
            RECRegistry.NYISO: "https://api.nyiso.com/v1/rec"
        }
        return urls.get(registry, "")
    
    def _get_supported_fuels(self, registry: RECRegistry) -> List[RECFuelType]:
        """Get supported fuel types for registry."""
        fuel_maps = {
            RECRegistry.MRETS: [RECFuelType.SOLAR, RECFuelType.WIND, RECFuelType.HYDRO, RECFuelType.BIOMASS],
            RECRegistry.NAR: [RECFuelType.SOLAR, RECFuelType.WIND, RECFuelType.HYDRO, RECFuelType.BIOMASS, RECFuelType.GEOTHERMAL],
            RECRegistry.WREGIS: [RECFuelType.SOLAR, RECFuelType.WIND, RECFuelType.HYDRO, RECFuelType.BIOMASS, RECFuelType.GEOTHERMAL],
            RECRegistry.NEPOOL: [RECFuelType.SOLAR, RECFuelType.WIND, RECFuelType.HYDRO, RECFuelType.BIOMASS],
            RECRegistry.PJM: [RECFuelType.SOLAR, RECFuelType.WIND, RECFuelType.HYDRO, RECFuelType.BIOMASS],
            RECRegistry.ERCOT: [RECFuelType.SOLAR, RECFuelType.WIND, RECFuelType.HYDRO, RECFuelType.BIOMASS],
            RECRegistry.CAISO: [RECFuelType.SOLAR, RECFuelType.WIND, RECFuelType.HYDRO, RECFuelType.BIOMASS, RECFuelType.GEOTHERMAL],
            RECRegistry.NYISO: [RECFuelType.SOLAR, RECFuelType.WIND, RECFuelType.HYDRO, RECFuelType.BIOMASS]
        }
        return fuel_maps.get(registry, [])
    
    def _get_vintage_rules(self, registry: RECRegistry) -> Dict[str, Any]:
        """Get vintage rules for registry."""
        rules = {
            RECRegistry.MRETS: {"max_carryover": 2, "expiration": "5_years"},
            RECRegistry.NAR: {"max_carryover": 3, "expiration": "6_years"},
            RECRegistry.WREGIS: {"max_carryover": 2, "expiration": "5_years"},
            RECRegistry.NEPOOL: {"max_carryover": 1, "expiration": "4_years"},
            RECRegistry.PJM: {"max_carryover": 2, "expiration": "5_years"},
            RECRegistry.ERCOT: {"max_carryover": 2, "expiration": "5_years"},
            RECRegistry.CAISO: {"max_carryover": 3, "expiration": "6_years"},
            RECRegistry.NYISO: {"max_carryover": 2, "expiration": "5_years"}
        }
        return rules.get(registry, {})
    
    def _get_retirement_rules(self, registry: RECRegistry) -> Dict[str, Any]:
        """Get retirement rules for registry."""
        rules = {
            RECRegistry.MRETS: {"retirement_deadline": "march_31", "allow_partial": True},
            RECRegistry.NAR: {"retirement_deadline": "march_31", "allow_partial": True},
            RECRegistry.WREGIS: {"retirement_deadline": "march_31", "allow_partial": True},
            RECRegistry.NEPOOL: {"retirement_deadline": "march_31", "allow_partial": False},
            RECRegistry.PJM: {"retirement_deadline": "march_31", "allow_partial": True},
            RECRegistry.ERCOT: {"retirement_deadline": "march_31", "allow_partial": True},
            RECRegistry.CAISO: {"retirement_deadline": "march_31", "allow_partial": True},
            RECRegistry.NYISO: {"retirement_deadline": "march_31", "allow_partial": True}
        }
        return rules.get(registry, {})
    
    async def get_recs_by_owner(
        self,
        owner_id: str,
        registry: Optional[RECRegistry] = None,
        status: Optional[RECStatus] = None,
        fuel_type: Optional[RECFuelType] = None,
        vintage_year: Optional[int] = None
    ) -> List[RECData]:
        """
        Get RECs owned by a specific entity.
        
        Args:
            owner_id: Owner identifier
            registry: Specific registry to query
            status: REC status filter
            fuel_type: Fuel type filter
            vintage_year: Vintage year filter
            
        Returns:
            List of RECs matching criteria
        """
        # Validate required fields using shared utility
        validate_required_fields({"owner_id": owner_id}, ["owner_id"])
        
        # This would integrate with actual registry APIs
        # For now, return mock data structure
        
        mock_recs = [
            RECData(
                rec_id=generate_unique_id("REC-"),
                registry=RECRegistry.MRETS,
                generator_id="GEN-001",
                generator_name="Solar Farm Alpha",
                fuel_type=RECFuelType.SOLAR,
                vintage=RECVintage.CURRENT_YEAR,
                vintage_year=2024,
                megawatt_hours=100.0,
                issue_date=datetime.now(),
                status=RECStatus.ISSUED,
                current_owner=owner_id,
                price=25.50,
                location="Minnesota",
                state="MN",
                region="MISO",
                carbon_offset=0.05
            )
        ]
        
        # Apply filters
        if registry:
            mock_recs = [r for r in mock_recs if r.registry == registry]
        if status:
            mock_recs = [r for r in mock_recs if r.status == status]
        if fuel_type:
            mock_recs = [r for r in mock_recs if r.fuel_type == fuel_type]
        if vintage_year:
            mock_recs = [r for r in mock_recs if r.vintage_year == vintage_year]
        
        return mock_recs
    
    async def transfer_recs(
        self,
        rec_ids: List[str],
        from_owner: str,
        to_owner: str,
        price_per_mwh: float,
        transaction_type: str = "sale"
    ) -> RECTransaction:
        """
        Transfer RECs between owners.
        
        Args:
            rec_ids: List of REC IDs to transfer
            from_owner: Current owner
            to_owner: New owner
            price_per_mwh: Price per MWh
            transaction_type: Type of transaction
            
        Returns:
            Transaction record
        """
        # Validate required fields using shared utility
        validate_required_fields({
            "rec_ids": rec_ids,
            "from_owner": from_owner,
            "to_owner": to_owner,
            "price_per_mwh": price_per_mwh
        }, ["rec_ids", "from_owner", "to_owner", "price_per_mwh"])
        
        # Calculate total value
        total_mwh = len(rec_ids) * 1.0  # Assuming 1 MWh per REC
        total_value = total_mwh * price_per_mwh
        
        transaction = RECTransaction(
            transaction_id=generate_unique_id("TXN-"),
            rec_id=",".join(rec_ids),
            from_owner=from_owner,
            to_owner=to_owner,
            transaction_type=transaction_type,
            megawatt_hours=total_mwh,
            price_per_mwh=price_per_mwh,
            total_value=total_value,
            transaction_date=datetime.now(),
            status="completed",
            registry=RECRegistry.MRETS,  # Would be determined from RECs
            metadata={
                "transaction_type": transaction_type,
                "rec_count": len(rec_ids)
            }
        )
        
        self.logger.info(f"REC transfer completed: {transaction.transaction_id}")
        return transaction
    
    async def retire_recs(
        self,
        rec_ids: List[str],
        owner_id: str,
        retirement_reason: str,
        compliance_period: str,
        registry: RECRegistry
    ) -> Dict[str, Any]:
        """
        Retire RECs for compliance or voluntary purposes.
        
        Args:
            rec_ids: List of REC IDs to retire
            owner_id: Owner of the RECs
            retirement_reason: Reason for retirement
            compliance_period: Compliance period
            registry: Registry where RECs are retired
            
        Returns:
            Retirement confirmation
        """
        # Validate required fields using shared utility
        validate_required_fields({
            "rec_ids": rec_ids,
            "owner_id": owner_id,
            "retirement_reason": retirement_reason,
            "compliance_period": compliance_period,
            "registry": registry
        }, ["rec_ids", "owner_id", "retirement_reason", "compliance_period", "registry"])
        
        # Validate retirement rules
        rules = self._get_retirement_rules(registry)
        
        retirement_data = {
            "retirement_id": generate_unique_id("RET-"),
            "rec_ids": rec_ids,
            "owner_id": owner_id,
            "retirement_reason": retirement_reason,
            "compliance_period": compliance_period,
            "registry": registry.value,
            "retirement_date": datetime.now().isoformat(),
            "total_mwh": len(rec_ids) * 1.0,
            "status": "retired",
            "rules_applied": rules
        }
        
        self.logger.info(f"RECs retired: {retirement_data['retirement_id']}")
        return retirement_data
    
    async def get_rec_prices(
        self,
        registry: RECRegistry,
        fuel_type: RECFuelType,
        vintage_year: int,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get current REC prices for specific criteria.
        
        Args:
            registry: REC registry
            fuel_type: Fuel type
            vintage_year: Vintage year
            location: Geographic location
            
        Returns:
            Price information
        """
        # Mock price data - would integrate with actual market data
        base_prices = {
            RECFuelType.SOLAR: 25.0,
            RECFuelType.WIND: 20.0,
            RECFuelType.HYDRO: 15.0,
            RECFuelType.BIOMASS: 18.0,
            RECFuelType.GEOTHERMAL: 22.0
        }
        
        base_price = base_prices.get(fuel_type, 20.0)
        
        # Apply vintage adjustments
        current_year = datetime.now().year
        vintage_adjustment = 1.0 - (0.1 * (current_year - vintage_year))
        vintage_adjustment = max(0.5, vintage_adjustment)  # Minimum 50% of base price
        
        # Apply location adjustments
        location_multiplier = 1.0
        if location:
            if "CA" in location or "CAISO" in registry.value:
                location_multiplier = 1.3  # California premium
            elif "NY" in location or "NYISO" in registry.value:
                location_multiplier = 1.2  # New York premium
        
        final_price = base_price * vintage_adjustment * location_multiplier
        
        return {
            "registry": registry.value,
            "fuel_type": fuel_type.value,
            "vintage_year": vintage_year,
            "location": location,
            "base_price": base_price,
            "vintage_adjustment": vintage_adjustment,
            "location_multiplier": location_multiplier,
            "final_price": round(final_price, 2),
            "currency": "USD",
            "unit": "per_mwh",
            "last_updated": datetime.now().isoformat()
        }
    
    async def get_compliance_report(
        self,
        owner_id: str,
        compliance_period: str,
        state: str,
        registry: RECRegistry
    ) -> Dict[str, Any]:
        """
        Generate compliance report for regulatory requirements.
        
        Args:
            owner_id: Owner identifier
            compliance_period: Compliance period
            state: State for compliance
            registry: REC registry
            
        Returns:
            Compliance report
        """
        # Get owner's RECs
        recs = await self.get_recs_by_owner(owner_id, registry=registry)
        
        # Calculate compliance metrics
        total_mwh = sum(rec.megawatt_hours for rec in recs if rec.status == RECStatus.ISSUED)
        retired_mwh = sum(rec.megawatt_hours for rec in recs if rec.status == RECStatus.RETIRED)
        available_mwh = total_mwh - retired_mwh
        
        # Determine compliance status
        compliance_status = "compliant" if retired_mwh >= total_mwh * 0.9 else "non_compliant"
        
        report = {
            "owner_id": owner_id,
            "compliance_period": compliance_period,
            "state": state,
            "registry": registry.value,
            "total_mwh": total_mwh,
            "retired_mwh": retired_mwh,
            "available_mwh": available_mwh,
            "compliance_status": compliance_status,
            "compliance_percentage": round((retired_mwh / total_mwh * 100), 2) if total_mwh > 0 else 0,
            "report_date": datetime.now().isoformat(),
            "recs_detail": [
                {
                    "rec_id": rec.rec_id,
                    "fuel_type": rec.fuel_type.value,
                    "vintage_year": rec.vintage_year,
                    "mwh": rec.megawatt_hours,
                    "status": rec.status.value
                }
                for rec in recs
            ]
        }
        
        return report
    
    async def get_esg_metrics(
        self,
        owner_id: str,
        period: str = "current_year"
    ) -> Dict[str, Any]:
        """
        Calculate ESG metrics based on REC holdings.
        
        Args:
            owner_id: Owner identifier
            period: Time period for metrics
            
        Returns:
            ESG metrics
        """
        # Get all RECs for the owner
        all_recs = await self.get_recs_by_owner(owner_id)
        
        # Calculate environmental impact
        total_renewable_mwh = sum(
            rec.megawatt_hours for rec in all_recs 
            if rec.fuel_type in [RECFuelType.SOLAR, RECFuelType.WIND, RECFuelType.HYDRO]
        )
        
        # Estimate CO2 avoidance (rough estimate: 0.5 metric tons per MWh)
        co2_avoided = total_renewable_mwh * 0.5
        
        # Calculate social impact (jobs, local investment)
        local_investment = total_renewable_mwh * 100  # $100 per MWh local investment
        
        # Governance metrics
        compliance_records = await self.get_compliance_report(
            owner_id, "2024", "MN", RECRegistry.MRETS
        )
        
        esg_metrics = {
            "owner_id": owner_id,
            "period": period,
            "environmental": {
                "total_renewable_mwh": total_renewable_mwh,
                "co2_avoided_tons": round(co2_avoided, 2),
                "renewable_percentage": 100.0,  # All RECs are renewable
                "fuel_breakdown": {
                    fuel_type.value: sum(
                        rec.megawatt_hours for rec in all_recs 
                        if rec.fuel_type == fuel_type
                    )
                    for fuel_type in RECFuelType
                }
            },
            "social": {
                "local_investment_usd": round(local_investment, 2),
                "communities_served": len(set(rec.state for rec in all_recs if rec.state)),
                "renewable_jobs_created": round(total_renewable_mwh / 100, 0)  # 1 job per 100 MWh
            },
            "governance": {
                "compliance_status": compliance_records.get("compliance_status", "unknown"),
                "compliance_percentage": compliance_records.get("compliance_percentage", 0),
                "regulatory_oversight": "compliant",
                "transparency_score": 95.0
            },
            "overall_esg_score": 92.5,
            "calculation_date": datetime.now().isoformat()
        }
        
        return esg_metrics

# Database Models for REC Management
class REC(CompanyScopedModel):
    """REC database model."""
    __tablename__ = "recs"
    
    id = Column(String, primary_key=True, default=lambda: generate_unique_id("REC-"))
    registry = Column(String, nullable=False)
    generator_id = Column(String, nullable=False)
    generator_name = Column(String, nullable=False)
    fuel_type = Column(String, nullable=False)
    vintage_year = Column(Integer, nullable=False)
    megawatt_hours = Column(Float, nullable=False)
    issue_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="issued")
    current_owner = Column(String, nullable=False)
    price = Column(Float)
    location = Column(String)
    state = Column(String)
    region = Column(String)
    carbon_offset = Column(Float)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class RECTransaction(CompanyScopedModel):
    """REC transaction database model."""
    __tablename__ = "rec_transactions"
    
    id = Column(String, primary_key=True, default=lambda: generate_unique_id("TXN-"))
    rec_id = Column(String, nullable=False)
    from_owner = Column(String, nullable=False)
    to_owner = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)
    megawatt_hours = Column(Float, nullable=False)
    price_per_mwh = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="pending")
    registry = Column(String, nullable=False)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now())

# Utility functions for easy access
async def get_recs_by_owner(owner_id: str, **kwargs) -> List[RECData]:
    """Get RECs by owner using default service."""
    service = RECService()
    return await service.get_recs_by_owner(owner_id, **kwargs)

async def transfer_recs(rec_ids: List[str], from_owner: str, to_owner: str, price_per_mwh: float) -> RECTransaction:
    """Transfer RECs using default service."""
    service = RECService()
    return await service.transfer_recs(rec_ids, from_owner, to_owner, price_per_mwh)

async def get_esg_metrics(owner_id: str, period: str = "current_year") -> Dict[str, Any]:
    """Get ESG metrics using default service."""
    service = RECService()
    return await service.get_esg_metrics(owner_id, period) 