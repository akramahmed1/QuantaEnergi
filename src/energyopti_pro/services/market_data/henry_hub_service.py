"""
Henry Hub Futures & Basis Trading Service.

This service provides comprehensive integration with Henry Hub natural gas markets:
- NYMEX Henry Hub futures contracts
- Basis trading across major hubs
- Natural gas storage data
- Pipeline capacity and flow information
- Weather correlation analysis
"""

import asyncio
import pandas as pd
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import uuid
import json

from ...core.config import settings
from ...core.logging import get_logger
from .base_service import BaseMarketDataService, ServiceConfig, ServiceType, DataType
from .utils import validate_time_range, generate_unique_id, MarketDataValidationError

logger = get_logger(__name__)

class GasHub(Enum):
    """Major natural gas trading hubs."""
    HENRY_HUB = "henry_hub"      # Louisiana - NYMEX benchmark
    TRANSCO_Z6 = "transco_z6"    # New York
    ALGONQUIN = "algonquin"      # Boston
    CHICAGO = "chicago"          # Chicago
    HOUSTON = "houston"          # Houston
    WAHA = "waha"                # West Texas
    TETCO_M3 = "tetco_m3"       # Appalachia
    DOMINION = "dominion"        # Virginia
    COLUMBIA_GULF = "columbia_gulf"  # Louisiana
    SABINE_PASS = "sabine_pass"  # Louisiana LNG

class ContractMonth(Enum):
    """Futures contract months."""
    JAN = "F"
    FEB = "G"
    MAR = "H"
    APR = "J"
    MAY = "K"
    JUN = "M"
    JUL = "N"
    AUG = "Q"
    SEP = "U"
    OCT = "V"
    NOV = "X"
    DEC = "Z"

class BasisType(Enum):
    """Basis trading types."""
    LOCATIONAL = "locational"      # Geographic basis
    TEMPORAL = "temporal"          # Time basis
    QUALITY = "quality"            # Quality basis
    TRANSPORTATION = "transportation"  # Pipeline basis

@dataclass
class HenryHubFuturesData:
    """Henry Hub futures data structure."""
    contract_month: str
    contract_year: int
    symbol: str
    last_price: float
    bid: float
    ask: float
    volume: int
    open_interest: int
    high: float
    low: float
    settlement: float
    change: float
    change_percent: float
    timestamp: datetime
    exchange: str = "NYMEX"

@dataclass
class BasisData:
    """Basis trading data structure."""
    hub: GasHub
    contract_month: str
    contract_year: int
    basis: float
    basis_type: BasisType
    volume: int
    open_interest: int
    last_trade: float
    timestamp: datetime
    correlation: Optional[float] = None

@dataclass
class StorageData:
    """Natural gas storage data structure."""
    report_date: date
    working_gas: float  # Bcf
    total_gas: float    # Bcf
    net_change: float   # Bcf
    year_ago: float     # Bcf
    five_year_avg: float # Bcf
    five_year_range: Dict[str, float]
    region: str
    timestamp: datetime

@dataclass
class PipelineFlowData:
    """Pipeline flow data structure."""
    pipeline: str
    receipt_point: str
    delivery_point: str
    flow_rate: float  # MMcf/d
    capacity: float   # MMcf/d
    utilization: float # Percentage
    timestamp: datetime
    direction: str = "forward"

class HenryHubService(BaseMarketDataService):
    """
    Henry Hub Futures & Basis Trading Service.
    
    This service provides comprehensive access to Henry Hub natural gas markets,
    including futures contracts, basis trading, storage data, and pipeline flows.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Henry Hub service.
        
        Args:
            api_key: Optional API key for enhanced access
        """
        config = ServiceConfig(
            service_type=ServiceType.HENRY_HUB,
            base_url="https://api.cmegroup.com/v1",
            api_key=api_key or settings.henry_hub.api_key,
            rate_limit_delay=0.1,
            timeout=30,
            max_retries=3,
            cache_duration=300
        )
        super().__init__(config)
        
        # Hub information and correlations
        self.hub_info = self._setup_hub_info()
        self.basis_correlations = self._setup_basis_correlations()
        
        # Contract month mapping
        self.contract_months = {
            "F": "January", "G": "February", "H": "March", "J": "April",
            "K": "May", "M": "June", "N": "July", "Q": "August",
            "U": "September", "V": "October", "X": "November", "Z": "December"
        }
    
    def _setup_hub_info(self) -> Dict[str, Dict[str, Any]]:
        """Setup hub information and characteristics."""
        return {
            GasHub.HENRY_HUB.value: {
                "name": "Henry Hub",
                "location": "Erath, Louisiana",
                "pipeline": "Sabine Pipeline",
                "benchmark": True,
                "liquidity": "Very High",
                "typical_basis": 0.0
            },
            GasHub.TRANSCO_Z6.value: {
                "name": "Transco Zone 6",
                "location": "New York City",
                "pipeline": "Transcontinental Gas Pipeline",
                "benchmark": False,
                "liquidity": "High",
                "typical_basis": 0.50
            },
            GasHub.ALGONQUIN.value: {
                "name": "Algonquin Citygate",
                "location": "Boston, Massachusetts",
                "pipeline": "Algonquin Gas Transmission",
                "benchmark": False,
                "liquidity": "High",
                "typical_basis": 0.75
            },
            GasHub.CHICAGO.value: {
                "name": "Chicago Citygate",
                "location": "Chicago, Illinois",
                "pipeline": "Northern Natural Gas",
                "benchmark": False,
                "liquidity": "High",
                "typical_basis": 0.25
            },
            GasHub.WAHA.value: {
                "name": "Waha Hub",
                "location": "West Texas",
                "pipeline": "El Paso Natural Gas",
                "benchmark": False,
                "liquidity": "Medium",
                "typical_basis": -0.50
            }
        }
    
    def _setup_basis_correlations(self) -> Dict[str, Dict[str, float]]:
        """Setup basis correlations between hubs."""
        return {
            GasHub.TRANSCO_Z6.value: {
                GasHub.HENRY_HUB.value: 0.85,
                GasHub.ALGONQUIN.value: 0.92,
                GasHub.CHICAGO.value: 0.78
            },
            GasHub.ALGONQUIN.value: {
                GasHub.HENRY_HUB.value: 0.82,
                GasHub.TRANSCO_Z6.value: 0.92,
                GasHub.CHICAGO.value: 0.75
            },
            GasHub.CHICAGO.value: {
                GasHub.HENRY_HUB.value: 0.88,
                GasHub.TRANSCO_Z6.value: 0.78,
                GasHub.ALGONQUIN.value: 0.75
            },
            GasHub.WAHA.value: {
                GasHub.HENRY_HUB.value: 0.65,
                GasHub.TRANSCO_Z6.value: 0.45,
                GasHub.ALGONQUIN.value: 0.42
            }
        }
    
    def _get_month_code(self, month: int) -> str:
        """Get contract month code from month number."""
        month_codes = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]
        return month_codes[month - 1]
    
    async def get_henry_hub_futures(
        self,
        contract_month: Optional[str] = None,
        contract_year: Optional[int] = None,
        limit: int = 20
    ) -> List[HenryHubFuturesData]:
        """
        Get Henry Hub futures data.
        
        Args:
            contract_month: Specific contract month (F, G, H, etc.)
            contract_year: Specific contract year
            limit: Maximum number of contracts to return
            
        Returns:
            List of futures data
        """
        # This would integrate with actual CME/NYMEX APIs
        # For now, return mock data structure
        
        current_year = datetime.now().year
        futures_data = []
        
        # Generate mock data for next 24 months
        for i in range(min(limit, 24)):
            future_date = datetime.now() + timedelta(days=30*i)
            month_code = self._get_month_code(future_date.month)
            year = future_date.year
            
            if contract_month and month_code != contract_month:
                continue
            if contract_year and year != contract_year:
                continue
            
            # Mock price data with realistic ranges
            base_price = 3.50 + (i * 0.02)  # Gradual price increase
            volatility = 0.15
            
            futures_data.append(HenryHubFuturesData(
                contract_month=month_code,
                contract_year=year,
                symbol=f"NG{month_code}{str(year)[-2:]}",
                last_price=round(base_price, 3),
                bid=round(base_price - volatility, 3),
                ask=round(base_price + volatility, 3),
                volume=1000 + (i * 100),
                open_interest=5000 + (i * 500),
                high=round(base_price + volatility * 2, 3),
                low=round(base_price - volatility * 2, 3),
                settlement=round(base_price, 3),
                change=round(volatility * 0.5, 3),
                change_percent=round((volatility * 0.5 / base_price) * 100, 2),
                timestamp=datetime.now()
            ))
        
        return futures_data
    
    async def get_basis_data(
        self,
        hub: GasHub,
        contract_month: Optional[str] = None,
        contract_year: Optional[int] = None
    ) -> List[BasisData]:
        """
        Get basis trading data for a specific hub.
        
        Args:
            hub: Gas hub to query
            contract_month: Specific contract month
            contract_year: Specific contract year
            
        Returns:
            List of basis data
        """
        # Mock basis data - would integrate with actual market data
        basis_data = []
        current_year = datetime.now().year
        
        for i in range(12):  # Next 12 months
            future_date = datetime.now() + timedelta(days=30*i)
            month_code = self._get_month_code(future_date.month)
            year = future_date.year
            
            if contract_month and month_code != contract_month:
                continue
            if contract_year and year != contract_year:
                continue
            
            # Calculate basis based on hub characteristics
            hub_info = self.hub_info.get(hub.value, {})
            typical_basis = hub_info.get("typical_basis", 0.0)
            
            # Add seasonal and market variations
            seasonal_adjustment = 0.1 * (i - 6)  # Winter premium
            market_variation = 0.05 * (i % 3)    # Market cycles
            
            basis = typical_basis + seasonal_adjustment + market_variation
            
            basis_data.append(BasisData(
                hub=hub,
                contract_month=month_code,
                contract_year=year,
                basis=round(basis, 3),
                basis_type=BasisType.LOCATIONAL,
                volume=500 + (i * 50),
                open_interest=2000 + (i * 200),
                last_trade=round(basis, 3),
                timestamp=datetime.now(),
                correlation=self._get_basis_correlation(hub, month_code, year)
            ))
        
        return basis_data
    
    def _get_basis_correlation(self, hub: GasHub, month: str, year: int) -> Optional[float]:
        """Get basis correlation with Henry Hub."""
        if hub == GasHub.HENRY_HUB:
            return 1.0
        
        correlations = self.basis_correlations.get(hub.value, {})
        return correlations.get(GasHub.HENRY_HUB.value, 0.8)
    
    async def get_storage_data(
        self,
        region: str = "total",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[StorageData]:
        """
        Get natural gas storage data.
        
        Args:
            region: Storage region (total, east, west, south central)
            start_date: Start date for data
            end_date: End date for data
            
        Returns:
            List of storage data
        """
        # Mock storage data - would integrate with EIA API
        storage_data = []
        
        if not start_date:
            start_date = date.today() - timedelta(days=365)
        if not end_date:
            end_date = date.today()
        
        # Validate time range using shared utility
        validate_time_range(
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.max.time())
        )
        
        current_date = start_date
        while current_date <= end_date:
            # Generate realistic storage data
            base_storage = 3500  # Bcf
            seasonal_variation = 500 * (1 + 0.5 * (current_date.month - 6) / 6)  # Winter build
            
            working_gas = base_storage + seasonal_variation
            total_gas = working_gas + 500  # Cushion gas
            
            storage_data.append(StorageData(
                report_date=current_date,
                working_gas=round(working_gas, 1),
                total_gas=round(total_gas, 1),
                net_change=round(seasonal_variation * 0.1, 1),
                year_ago=round(working_gas * 0.95, 1),
                five_year_avg=round(working_gas * 0.98, 1),
                five_year_range={
                    "min": round(working_gas * 0.85, 1),
                    "max": round(working_gas * 1.15, 1)
                },
                region=region,
                timestamp=datetime.now()
            ))
            
            current_date += timedelta(days=7)  # Weekly data
        
        return storage_data
    
    async def get_pipeline_flows(
        self,
        pipeline: Optional[str] = None,
        receipt_point: Optional[str] = None,
        delivery_point: Optional[str] = None
    ) -> List[PipelineFlowData]:
        """
        Get pipeline flow data.
        
        Args:
            pipeline: Specific pipeline
            receipt_point: Receipt point
            delivery_point: Delivery point
            
        Returns:
            List of pipeline flow data
        """
        # Mock pipeline flow data
        pipelines = [
            "Transcontinental Gas Pipeline",
            "Algonquin Gas Transmission",
            "Northern Natural Gas",
            "El Paso Natural Gas",
            "Sabine Pipeline"
        ]
        
        flow_data = []
        for pipe in pipelines:
            if pipeline and pipe != pipeline:
                continue
            
            # Generate realistic flow data
            base_flow = 1000  # MMcf/d
            capacity = base_flow * 1.2
            utilization = 0.85
            
            flow_data.append(PipelineFlowData(
                pipeline=pipe,
                receipt_point="Receipt Point",
                delivery_point="Delivery Point",
                flow_rate=round(base_flow, 1),
                capacity=round(capacity, 1),
                utilization=round(utilization * 100, 1),
                timestamp=datetime.now(),
                direction="forward"
            ))
        
        return flow_data
    
    async def calculate_basis_spread(
        self,
        hub1: GasHub,
        hub2: GasHub,
        contract_month: str,
        contract_year: int
    ) -> Dict[str, Any]:
        """
        Calculate basis spread between two hubs.
        
        Args:
            hub1: First hub
            hub2: Second hub
            contract_month: Contract month
            contract_year: Contract year
            
        Returns:
            Basis spread calculation
        """
        # Get basis data for both hubs
        basis1 = await self.get_basis_data(hub1, contract_month, contract_year)
        basis2 = await self.get_basis_data(hub2, contract_month, contract_year)
        
        if not basis1 or not basis2:
            return {"error": "No basis data available"}
        
        # Calculate spread
        spread = basis1[0].basis - basis2[0].basis
        
        # Get correlation
        correlation = self._get_basis_correlation(hub1, contract_month, contract_year)
        
        return {
            "hub1": hub1.value,
            "hub2": hub2.value,
            "contract_month": contract_month,
            "contract_year": contract_year,
            "basis1": basis1[0].basis,
            "basis2": basis2[0].basis,
            "spread": round(spread, 3),
            "correlation": correlation,
            "trading_opportunity": abs(spread) > 0.10,  # 10 cent threshold
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_weather_correlation(
        self,
        hub: GasHub,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get weather correlation analysis for a hub.
        
        Args:
            hub: Gas hub
            days: Number of days for analysis
            
        Returns:
            Weather correlation data
        """
        # Mock weather correlation data
        # In production, this would integrate with weather APIs
        
        correlation_data = {
            "hub": hub.value,
            "analysis_period_days": days,
            "temperature_correlation": 0.75,
            "heating_degree_days_correlation": 0.82,
            "cooling_degree_days_correlation": 0.68,
            "precipitation_correlation": 0.45,
            "wind_correlation": 0.35,
            "overall_correlation": 0.78,
            "weather_sensitivity": "High" if hub in [GasHub.TRANSCO_Z6, GasHub.ALGONQUIN] else "Medium",
            "seasonal_factors": ["Winter heating demand", "Summer cooling demand"],
            "analysis_date": datetime.now().isoformat()
        }
        
        return correlation_data
    
    async def get_market_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive market summary.
        
        Returns:
            Market summary data
        """
        try:
            # Get current month futures
            current_futures = await self.get_henry_hub_futures(limit=1)
            
            # Get storage data
            storage = await self.get_storage_data(limit=1)
            
            # Get basis data for major hubs
            major_hubs = [GasHub.TRANSCO_Z6, GasHub.ALGONQUIN, GasHub.CHICAGO, GasHub.WAHA]
            basis_summary = {}
            
            for hub in major_hubs:
                basis_data = await self.get_basis_data(hub, limit=1)
                if basis_data:
                    basis_summary[hub.value] = {
                        "current_basis": basis_data[0].basis,
                        "volume": basis_data[0].volume,
                        "open_interest": basis_data[0].open_interest
                    }
            
            summary = {
                "timestamp": datetime.now().isoformat(),
                "henry_hub_futures": {
                    "current_month": current_futures[0].contract_month if current_futures else None,
                    "current_price": current_futures[0].last_price if current_futures else None,
                    "change": current_futures[0].change if current_futures else None,
                    "volume": current_futures[0].volume if current_futures else None
                },
                "storage": {
                    "working_gas": storage[0].working_gas if storage else None,
                    "net_change": storage[0].net_change if storage else None,
                    "five_year_avg": storage[0].five_year_avg if storage else None
                },
                "basis_summary": basis_summary,
                "market_status": "active",
                "volatility": "medium",
                "liquidity": "high"
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get market summary: {e}")
            raise MarketDataValidationError(f"Failed to get market summary: {str(e)}")
    
    def get_hub_info(self, hub_code: str) -> Optional[Dict[str, Any]]:
        """Get information about a gas hub."""
        if hub_code in self.hub_info:
            return self.hub_info[hub_code]
        return None
    
    def get_all_hubs(self) -> List[Dict[str, Any]]:
        """Get all available gas hubs."""
        return [
            {"code": code, "info": info}
            for code, info in self.hub_info.items()
        ]

# Database Models for Henry Hub Data
class HenryHubFutures(CompanyScopedModel):
    """Henry Hub futures database model."""
    __tablename__ = "henry_hub_futures"
    
    id = Column(String, primary_key=True, default=lambda: generate_unique_id("HH-"))
    contract_month = Column(String, nullable=False)
    contract_year = Column(Integer, nullable=False)
    symbol = Column(String, nullable=False)
    last_price = Column(Float, nullable=False)
    bid = Column(Float)
    ask = Column(Float)
    volume = Column(Integer)
    open_interest = Column(Integer)
    high = Column(Float)
    low = Column(Float)
    settlement = Column(Float)
    change = Column(Float)
    change_percent = Column(Float)
    timestamp = Column(DateTime, nullable=False)
    exchange = Column(String, default="NYMEX")
    created_at = Column(DateTime, default=func.now())

class BasisTrade(CompanyScopedModel):
    """Basis trade database model."""
    __tablename__ = "basis_trades"
    
    id = Column(String, primary_key=True, default=lambda: generate_unique_id("BASIS-"))
    hub = Column(String, nullable=False)
    contract_month = Column(String, nullable=False)
    contract_year = Column(Integer, nullable=False)
    basis = Column(Float, nullable=False)
    basis_type = Column(String, nullable=False)
    volume = Column(Integer)
    open_interest = Column(Integer)
    last_trade = Column(Float)
    timestamp = Column(DateTime, nullable=False)
    correlation = Column(Float)
    created_at = Column(DateTime, default=func.now())

# Utility functions for easy access
async def get_henry_hub_futures(**kwargs) -> List[HenryHubFuturesData]:
    """Get Henry Hub futures using default service."""
    async with HenryHubService() as service:
        return await service.get_henry_hub_futures(**kwargs)

async def get_basis_data(hub: GasHub, **kwargs) -> List[BasisData]:
    """Get basis data using default service."""
    async with HenryHubService() as service:
        return await service.get_basis_data(hub, **kwargs)

async def get_market_summary() -> Dict[str, Any]:
    """Get market summary using default service."""
    async with HenryHubService() as service:
        return await service.get_market_summary() 