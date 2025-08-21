"""
PJM (Pennsylvania-New Jersey-Maryland) Market Data Service.

This service provides real-time integration with PJM Interconnection for:
- Locational Marginal Prices (LMPs)
- Financial Transmission Rights (FTRs)
- Day-ahead and real-time scheduling
- Capacity market data
- Ancillary services
"""

import asyncio
import pandas as pd
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from ...core.config import settings
from .base_service import BaseMarketDataService, ServiceConfig, ServiceType, DataType
from .utils import validate_time_range, generate_unique_id, MarketDataValidationError

class PJMMarketType(Enum):
    """PJM market types."""
    DAY_AHEAD = "day_ahead"
    REAL_TIME = "real_time"
    CAPACITY = "capacity"
    ANCILLARY = "ancillary"

class PJMDataType(Enum):
    """PJM data types."""
    LMP = "lmp"
    FTR = "ftr"
    SCHEDULE = "schedule"
    CAPACITY = "capacity"
    ANCILLARY = "ancillary"

@dataclass
class PJMLMPData:
    """PJM LMP data structure."""
    timestamp: datetime
    node_id: str
    node_name: str
    lmp: float
    congestion: float
    marginal_loss: float
    energy: float
    market_type: PJMMarketType
    zone: str
    region: str

@dataclass
class PJMFTRData:
    """PJM FTR data structure."""
    timestamp: datetime
    source_node: str
    sink_node: str
    ftr_id: str
    megawatt: float
    price: float
    auction_type: str
    period: str
    status: str

@dataclass
class PJMScheduleData:
    """PJM schedule data structure."""
    timestamp: datetime
    unit_id: str
    unit_name: str
    megawatt: float
    schedule_type: str
    market_type: PJMMarketType
    zone: str
    fuel_type: str

class PJMService(BaseMarketDataService):
    """
    PJM Market Data Service for real-time integration.
    
    This service provides access to PJM's public APIs and data feeds,
    including LMPs, FTRs, scheduling, and capacity market data.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize PJM service.
        
        Args:
            api_key: Optional API key for enhanced access
        """
        config = ServiceConfig(
            service_type=ServiceType.PJM,
            base_url="https://api.pjm.com/api/v1",
            api_key=api_key or settings.pjm.api_key,
            rate_limit_delay=0.1,
            timeout=30,
            max_retries=3,
            cache_duration=300
        )
        super().__init__(config)
        
        # PJM zones and regions
        self.zones = self._setup_zones()
        
        # Market types and their endpoints
        self.endpoints = {
            "lmp": "/inst_load",
            "ftr": "/ftr",
            "schedule": "/inst_load",
            "capacity": "/capacity",
            "ancillary": "/ancillary"
        }
    
    def _setup_zones(self) -> Dict[str, str]:
        """Setup PJM zones and regions."""
        return {
            "AEP": "American Electric Power",
            "AP": "Allegheny Power",
            "ATSI": "American Transmission Systems",
            "BGE": "Baltimore Gas & Electric",
            "COMED": "Commonwealth Edison",
            "DAYTON": "Dayton Power & Light",
            "DEOK": "Dominion Energy Ohio/Kentucky",
            "DOM": "Dominion Energy",
            "DUQ": "Duquesne Light",
            "EES": "East Kentucky Power Cooperative",
            "JCPL": "Jersey Central Power & Light",
            "METED": "Metropolitan Edison",
            "PECO": "PECO Energy",
            "PENELEC": "Pennsylvania Electric",
            "PEPCO": "Potomac Electric Power",
            "PPL": "PPL Electric Utilities",
            "PSEG": "Public Service Enterprise Group",
            "RTO": "RTO-wide"
        }
    
    async def get_lmp_data(
        self,
        start_time: datetime,
        end_time: datetime,
        nodes: Optional[List[str]] = None,
        market_type: PJMMarketType = PJMMarketType.REAL_TIME
    ) -> List[PJMLMPData]:
        """
        Get LMP data for specified nodes and time range.
        
        Args:
            start_time: Start time for data query
            end_time: End time for data query
            nodes: List of node IDs to query (None for all)
            market_type: Market type (day-ahead or real-time)
            
        Returns:
            List of LMP data points
        """
        # Validate time range using shared utility
        validate_time_range(start_time, end_time)
        
        endpoint = "/inst_load"
        
        params = {
            "start": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "market": market_type.value
        }
        
        if nodes:
            params["nodes"] = ",".join(nodes)
        
        try:
            data = await self._get(endpoint, params)
            
            lmp_data = []
            for item in data.get("data", []):
                lmp_data.append(PJMLMPData(
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    node_id=item["node_id"],
                    node_name=item.get("node_name", ""),
                    lmp=float(item["lmp"]),
                    congestion=float(item.get("congestion", 0)),
                    marginal_loss=float(item.get("marginal_loss", 0)),
                    energy=float(item.get("energy", 0)),
                    market_type=market_type,
                    zone=item.get("zone", ""),
                    region=item.get("region", "")
                ))
            
            return lmp_data
            
        except Exception as e:
            self.logger.error(f"Failed to get LMP data: {e}")
            raise MarketDataValidationError(f"Failed to get LMP data: {str(e)}")
    
    async def get_ftr_data(
        self,
        start_time: datetime,
        end_time: datetime,
        source_nodes: Optional[List[str]] = None,
        sink_nodes: Optional[List[str]] = None
    ) -> List[PJMFTRData]:
        """
        Get FTR data for specified time range and nodes.
        
        Args:
            start_time: Start time for data query
            end_time: End time for data query
            source_nodes: List of source node IDs
            sink_nodes: List of sink node IDs
            
        Returns:
            List of FTR data points
        """
        # Validate time range using shared utility
        validate_time_range(start_time, end_time)
        
        endpoint = "/ftr"
        
        params = {
            "start": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": end_time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        
        if source_nodes:
            params["source_nodes"] = ",".join(source_nodes)
        if sink_nodes:
            params["sink_nodes"] = ",".join(sink_nodes)
        
        try:
            data = await self._get(endpoint, params)
            
            ftr_data = []
            for item in data.get("data", []):
                ftr_data.append(PJMFTRData(
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    source_node=item["source_node"],
                    sink_node=item["sink_node"],
                    ftr_id=item["ftr_id"],
                    megawatt=float(item["megawatt"]),
                    price=float(item["price"]),
                    auction_type=item.get("auction_type", ""),
                    period=item.get("period", ""),
                    status=item.get("status", "")
                ))
            
            return ftr_data
            
        except Exception as e:
            self.logger.error(f"Failed to get FTR data: {e}")
            raise MarketDataValidationError(f"Failed to get FTR data: {str(e)}")
    
    async def get_schedule_data(
        self,
        start_time: datetime,
        end_time: datetime,
        units: Optional[List[str]] = None,
        market_type: PJMMarketType = PJMMarketType.DAY_AHEAD
    ) -> List[PJMScheduleData]:
        """
        Get scheduling data for specified units and time range.
        
        Args:
            start_time: Start time for data query
            end_time: End time for data query
            units: List of unit IDs to query
            market_type: Market type (day-ahead or real-time)
            
        Returns:
            List of schedule data points
        """
        # Validate time range using shared utility
        validate_time_range(start_time, end_time)
        
        endpoint = "/inst_load"
        
        params = {
            "start": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "market": market_type.value,
            "type": "schedule"
        }
        
        if units:
            params["units"] = ",".join(units)
        
        try:
            data = await self._get(endpoint, params)
            
            schedule_data = []
            for item in data.get("data", []):
                schedule_data.append(PJMScheduleData(
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    unit_id=item["unit_id"],
                    unit_name=item.get("unit_name", ""),
                    megawatt=float(item["megawatt"]),
                    schedule_type=item.get("schedule_type", ""),
                    market_type=market_type,
                    zone=item.get("zone", ""),
                    fuel_type=item.get("fuel_type", "")
                ))
            
            return schedule_data
            
        except Exception as e:
            self.logger.error(f"Failed to get schedule data: {e}")
            raise MarketDataValidationError(f"Failed to get schedule data: {str(e)}")
    
    async def get_capacity_market_data(
        self,
        delivery_year: int,
        zone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get capacity market data for specified delivery year.
        
        Args:
            delivery_year: Delivery year for capacity
            zone: PJM zone (None for all zones)
            
        Returns:
            Capacity market data
        """
        endpoint = "/capacity"
        
        params = {
            "delivery_year": delivery_year
        }
        
        if zone:
            params["zone"] = zone
        
        try:
            data = await self._get(endpoint, params)
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get capacity market data: {e}")
            raise MarketDataValidationError(f"Failed to get capacity market data: {str(e)}")
    
    async def get_ancillary_services_data(
        self,
        start_time: datetime,
        end_time: datetime,
        service_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get ancillary services data.
        
        Args:
            start_time: Start time for data query
            end_time: End time for data query
            service_type: Type of ancillary service
            
        Returns:
            Ancillary services data
        """
        # Validate time range using shared utility
        validate_time_range(start_time, end_time)
        
        endpoint = "/ancillary"
        
        params = {
            "start": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": end_time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        
        if service_type:
            params["service_type"] = service_type
        
        try:
            data = await self._get(endpoint, params)
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get ancillary services data: {e}")
            raise MarketDataValidationError(f"Failed to get ancillary services data: {str(e)}")
    
    async def get_market_summary(self, date: date) -> Dict[str, Any]:
        """
        Get daily market summary for specified date.
        
        Args:
            date: Date for market summary
            
        Returns:
            Market summary data
        """
        start_time = datetime.combine(date, datetime.min.time())
        end_time = datetime.combine(date, datetime.max.time())
        
        try:
            # Get LMP summary
            lmp_data = await self.get_lmp_data(start_time, end_time)
            
            # Get schedule summary
            schedule_data = await self.get_schedule_data(start_time, end_time)
            
            # Calculate summary statistics
            summary = {
                "date": date.isoformat(),
                "total_lmp_points": len(lmp_data),
                "avg_lmp": sum(d.lmp for d in lmp_data) / len(lmp_data) if lmp_data else 0,
                "max_lmp": max(d.lmp for d in lmp_data) if lmp_data else 0,
                "min_lmp": min(d.lmp for d in lmp_data) if lmp_data else 0,
                "total_schedule_points": len(schedule_data),
                "total_megawatt": sum(d.megawatt for d in schedule_data),
                "zones": list(set(d.zone for d in lmp_data if d.zone)),
                "market_types": list(set(d.market_type.value for d in lmp_data))
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get market summary: {e}")
            raise MarketDataValidationError(f"Failed to get market summary: {str(e)}")
    
    def get_zone_info(self, zone_code: str) -> Optional[Dict[str, str]]:
        """
        Get information about a PJM zone.
        
        Args:
            zone_code: PJM zone code
            
        Returns:
            Zone information or None if not found
        """
        if zone_code in self.zones:
            return {
                "code": zone_code,
                "name": self.zones[zone_code]
            }
        return None
    
    def get_all_zones(self) -> List[Dict[str, str]]:
        """
        Get all available PJM zones.
        
        Returns:
            List of all zones
        """
        return [
            {"code": code, "name": name}
            for code, name in self.zones.items()
        ]

# Utility functions for easy access
async def get_pjm_lmp_data(
    start_time: datetime,
    end_time: datetime,
    nodes: Optional[List[str]] = None,
    market_type: PJMMarketType = PJMMarketType.REAL_TIME
) -> List[PJMLMPData]:
    """Get PJM LMP data using default service."""
    async with PJMService() as service:
        return await service.get_lmp_data(start_time, end_time, nodes, market_type)

async def get_pjm_ftr_data(
    start_time: datetime,
    end_time: datetime,
    source_nodes: Optional[List[str]] = None,
    sink_nodes: Optional[List[str]] = None
) -> List[PJMFTRData]:
    """Get PJM FTR data using default service."""
    async with PJMService() as service:
        return await service.get_ftr_data(start_time, end_time, source_nodes, sink_nodes)

async def get_pjm_market_summary(date: date) -> Dict[str, Any]:
    """Get PJM market summary using default service."""
    async with PJMService() as service:
        return await service.get_market_summary(date) 