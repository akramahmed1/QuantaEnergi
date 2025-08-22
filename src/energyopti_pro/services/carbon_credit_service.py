"""
Carbon Credit Trading Service for EnergyOpti-Pro.

Implements carbon credit trading with:
- Verra and Gold Standard registry integration
- Carbon-neutral energy trading pairs
- Automated carbon offsetting
- ESG compliance reporting
- Real-time carbon pricing
"""

import asyncio
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timezone, timedelta
import structlog
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

logger = structlog.get_logger()

class CarbonStandard(Enum):
    """Carbon credit standards."""
    VERRA = "verra"
    GOLD_STANDARD = "gold_standard"
    AMERICAN_CARBON_REGISTRY = "acr"
    CLIMATE_ACTION_RESERVE = "car"
    PLAN_VIVO = "plan_vivo"

class CarbonProjectType(Enum):
    """Carbon project types."""
    RENEWABLE_ENERGY = "renewable_energy"
    FORESTRY = "forestry"
    AGRICULTURE = "agriculture"
    WASTE_MANAGEMENT = "waste_management"
    TRANSPORT = "transport"
    INDUSTRIAL = "industrial"
    BUILDING_EFFICIENCY = "building_efficiency"

class CarbonCreditStatus(Enum):
    """Carbon credit status."""
    AVAILABLE = "available"
    RESERVED = "reserved"
    RETIRED = "retired"
    TRANSFERRED = "transferred"
    EXPIRED = "expired"

@dataclass
class CarbonProject:
    """Carbon project details."""
    project_id: str
    name: str
    standard: CarbonStandard
    project_type: CarbonProjectType
    location: str
    developer: str
    vintage_year: int
    total_credits: int
    available_credits: int
    price_per_credit: Decimal
    currency: str
    verification_date: datetime
    expiry_date: datetime
    co2_equivalent: float
    additional_benefits: List[str]
    metadata: Dict[str, Any]

@dataclass
class CarbonCredit:
    """Carbon credit details."""
    credit_id: str
    project_id: str
    serial_number: str
    vintage_year: int
    issuance_date: datetime
    expiry_date: datetime
    status: CarbonCreditStatus
    price: Decimal
    currency: str
    buyer_id: Optional[str] = None
    purchase_date: Optional[datetime] = None
    retirement_date: Optional[datetime] = None
    blockchain_hash: Optional[str] = None

@dataclass
class CarbonOffset:
    """Carbon offset transaction."""
    offset_id: str
    user_id: str
    energy_trade_id: str
    carbon_credits_used: int
    total_cost: Decimal
    currency: str
    offset_date: datetime
    verification_status: str
    blockchain_transaction_id: Optional[str] = None

@dataclass
class CarbonNeutralTrade:
    """Carbon-neutral energy trade."""
    trade_id: str
    user_id: str
    energy_symbol: str
    energy_quantity: float
    energy_price: Decimal
    carbon_footprint: float
    carbon_credits_required: int
    carbon_credit_cost: Decimal
    total_trade_cost: Decimal
    trade_date: datetime
    carbon_neutral: bool
    offset_transaction_id: Optional[str] = None

class VerraRegistryClient:
    """Client for Verra carbon registry."""
    
    def __init__(self, api_key: str, base_url: str = "https://registry.verra.org/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_projects(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get carbon projects from Verra registry."""
        url = f"{self.base_url}/projects"
        params = {
            "limit": limit,
            "offset": offset,
            "status": "active"
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("projects", [])
            else:
                logger.error(f"Failed to fetch Verra projects: {response.status}")
                return []
    
    async def get_project_details(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed project information."""
        url = f"{self.base_url}/projects/{project_id}"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"Failed to fetch project {project_id}: {response.status}")
                return None
    
    async def get_available_credits(self, project_id: str) -> int:
        """Get available credits for a project."""
        url = f"{self.base_url}/projects/{project_id}/credits"
        params = {"status": "available"}
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("total_available", 0)
            else:
                logger.error(f"Failed to fetch credits for {project_id}: {response.status}")
                return 0

class GoldStandardRegistryClient:
    """Client for Gold Standard carbon registry."""
    
    def __init__(self, api_key: str, base_url: str = "https://registry.goldstandard.org/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_projects(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get carbon projects from Gold Standard registry."""
        url = f"{self.base_url}/projects"
        params = {
            "limit": limit,
            "offset": offset,
            "status": "active"
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("projects", [])
            else:
                logger.error(f"Failed to fetch Gold Standard projects: {response.status}")
                return []
    
    async def get_project_details(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed project information."""
        url = f"{self.base_url}/projects/{project_id}"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"Failed to fetch project {project_id}: {response.status}")
                return None

class CarbonCreditService:
    """Main carbon credit trading service."""
    
    def __init__(self, database_url: str, verra_api_key: str, gold_standard_api_key: str):
        self.database_url = database_url
        self.verra_api_key = verra_api_key
        self.gold_standard_api_key = gold_standard_api_key
        
        # Initialize registry clients
        self.verra_client = VerraRegistryClient(verra_api_key)
        self.gold_standard_client = GoldStandardRegistryClient(gold_standard_api_key)
        
        # Carbon pricing data
        self.carbon_prices: Dict[str, Dict[str, Any]] = {}
        self.price_update_interval = 300  # 5 minutes
        
        # Service state
        self.projects: Dict[str, CarbonProject] = {}
        self.credits: Dict[str, CarbonCredit] = {}
        self.offsets: List[CarbonOffset] = []
        self.carbon_neutral_trades: List[CarbonNeutralTrade] = []
        
        # Start background tasks
        asyncio.create_task(self._update_carbon_prices())
        asyncio.create_task(self._sync_registry_data())
    
    async def _update_carbon_prices(self):
        """Update carbon credit prices from external sources."""
        while True:
            try:
                await self._fetch_carbon_prices()
                await asyncio.sleep(self.price_update_interval)
            except Exception as e:
                logger.error(f"Error updating carbon prices: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _fetch_carbon_prices(self):
        """Fetch carbon credit prices from multiple sources."""
        # Fetch from carbon pricing APIs
        sources = [
            "https://api.carbonpricing.com/v1/prices",
            "https://api.carboncredits.com/v1/market-data",
            "https://api.verra.org/v1/market-data"
        ]
        
        for source in sources:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(source) as response:
                        if response.status == 200:
                            data = await response.json()
                            await self._process_price_data(data, source)
            except Exception as e:
                logger.error(f"Failed to fetch prices from {source}: {e}")
    
    async def _process_price_data(self, data: Dict[str, Any], source: str):
        """Process carbon price data from external sources."""
        timestamp = datetime.now(timezone.utc)
        
        # Extract price information
        if "prices" in data:
            for price_info in data["prices"]:
                standard = price_info.get("standard", "unknown")
                price = Decimal(str(price_info.get("price", 0)))
                currency = price_info.get("currency", "USD")
                
                self.carbon_prices[standard] = {
                    "price": price,
                    "currency": currency,
                    "source": source,
                    "timestamp": timestamp,
                    "change_24h": price_info.get("change_24h", 0),
                    "volume_24h": price_info.get("volume_24h", 0)
                }
    
    async def _sync_registry_data(self):
        """Synchronize data from carbon registries."""
        while True:
            try:
                await self._sync_verra_projects()
                await self._sync_gold_standard_projects()
                await asyncio.sleep(3600)  # Sync every hour
            except Exception as e:
                logger.error(f"Error syncing registry data: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes on error
    
    async def _sync_verra_projects(self):
        """Synchronize projects from Verra registry."""
        async with self.verra_client as client:
            projects = await client.get_projects(limit=1000)
            
            for project_data in projects:
                project = await self._create_verra_project(project_data)
                if project:
                    self.projects[project.project_id] = project
    
    async def _sync_gold_standard_projects(self):
        """Synchronize projects from Gold Standard registry."""
        async with self.gold_standard_client as client:
            projects = await client.get_projects(limit=1000)
            
            for project_data in projects:
                project = await self._create_gold_standard_project(project_data)
                if project:
                    self.projects[project.project_id] = project
    
    async def _create_verra_project(self, project_data: Dict[str, Any]) -> Optional[CarbonProject]:
        """Create CarbonProject from Verra data."""
        try:
            project = CarbonProject(
                project_id=project_data["id"],
                name=project_data["name"],
                standard=CarbonStandard.VERRA,
                project_type=self._map_project_type(project_data.get("type", "")),
                location=project_data.get("location", "Unknown"),
                developer=project_data.get("developer", "Unknown"),
                vintage_year=project_data.get("vintage_year", datetime.now().year),
                total_credits=project_data.get("total_credits", 0),
                available_credits=project_data.get("available_credits", 0),
                price_per_credit=Decimal(str(project_data.get("price", 0))),
                currency=project_data.get("currency", "USD"),
                verification_date=datetime.fromisoformat(project_data.get("verification_date", datetime.now().isoformat())),
                expiry_date=datetime.fromisoformat(project_data.get("expiry_date", (datetime.now() + timedelta(days=365)).isoformat())),
                co2_equivalent=project_data.get("co2_equivalent", 0.0),
                additional_benefits=project_data.get("additional_benefits", []),
                metadata=project_data
            )
            return project
        except Exception as e:
            logger.error(f"Error creating Verra project: {e}")
            return None
    
    async def _create_gold_standard_project(self, project_data: Dict[str, Any]) -> Optional[CarbonProject]:
        """Create CarbonProject from Gold Standard data."""
        try:
            project = CarbonProject(
                project_id=project_data["id"],
                name=project_data["name"],
                standard=CarbonStandard.GOLD_STANDARD,
                project_type=self._map_project_type(project_data.get("type", "")),
                location=project_data.get("location", "Unknown"),
                developer=project_data.get("developer", "Unknown"),
                vintage_year=project_data.get("vintage_year", datetime.now().year),
                total_credits=project_data.get("total_credits", 0),
                available_credits=project_data.get("available_credits", 0),
                price_per_credit=Decimal(str(project_data.get("price", 0))),
                currency=project_data.get("currency", "USD"),
                verification_date=datetime.fromisoformat(project_data.get("verification_date", datetime.now().isoformat())),
                expiry_date=datetime.fromisoformat(project_data.get("expiry_date", (datetime.now() + timedelta(days=365)).isoformat())),
                co2_equivalent=project_data.get("co2_equivalent", 0.0),
                additional_benefits=project_data.get("additional_benefits", []),
                metadata=project_data
            )
            return project
        except Exception as e:
            logger.error(f"Error creating Gold Standard project: {e}")
            return None
    
    def _map_project_type(self, type_string: str) -> CarbonProjectType:
        """Map project type string to enum."""
        type_mapping = {
            "renewable_energy": CarbonProjectType.RENEWABLE_ENERGY,
            "forestry": CarbonProjectType.FORESTRY,
            "agriculture": CarbonProjectType.AGRICULTURE,
            "waste_management": CarbonProjectType.WASTE_MANAGEMENT,
            "transport": CarbonProjectType.TRANSPORT,
            "industrial": CarbonProjectType.INDUSTRIAL,
            "building_efficiency": CarbonProjectType.BUILDING_EFFICIENCY
        }
        return type_mapping.get(type_string.lower(), CarbonProjectType.RENEWABLE_ENERGY)
    
    async def purchase_carbon_credits(self, user_id: str, project_id: str, 
                                    quantity: int) -> Optional[CarbonCredit]:
        """Purchase carbon credits from a project."""
        logger.info(f"User {user_id} purchasing {quantity} credits from project {project_id}")
        
        if project_id not in self.projects:
            raise ValueError(f"Project not found: {project_id}")
        
        project = self.projects[project_id]
        
        if project.available_credits < quantity:
            raise ValueError(f"Insufficient credits available: {project.available_credits}")
        
        # Create carbon credit
        credit = CarbonCredit(
            credit_id=f"credit_{int(time.time())}_{hash(project_id)}",
            project_id=project_id,
            serial_number=f"{project.standard.value}_{project_id}_{int(time.time())}",
            vintage_year=project.vintage_year,
            issuance_date=datetime.now(timezone.utc),
            expiry_date=project.expiry_date,
            status=CarbonCreditStatus.RESERVED,
            price=project.price_per_credit,
            currency=project.currency,
            buyer_id=user_id,
            purchase_date=datetime.now(timezone.utc)
        )
        
        # Update project availability
        project.available_credits -= quantity
        
        # Store credit
        self.credits[credit.credit_id] = credit
        
        # Generate blockchain hash
        credit.blockchain_hash = await self._generate_credit_hash(credit)
        
        logger.info(f"Carbon credit purchased: {credit.credit_id}")
        return credit
    
    async def retire_carbon_credits(self, credit_id: str, 
                                  retirement_reason: str = "Energy trade offset") -> bool:
        """Retire carbon credits for offsetting."""
        if credit_id not in self.credits:
            raise ValueError(f"Credit not found: {credit_id}")
        
        credit = self.credits[credit_id]
        
        if credit.status != CarbonCreditStatus.RESERVED:
            raise ValueError(f"Credit not available for retirement: {credit.status}")
        
        # Retire credit
        credit.status = CarbonCreditStatus.RETIRED
        credit.retirement_date = datetime.now(timezone.utc)
        
        # Update blockchain
        await self._update_credit_on_blockchain(credit)
        
        logger.info(f"Carbon credit retired: {credit_id}")
        return True
    
    async def calculate_carbon_footprint(self, energy_symbol: str, 
                                      energy_quantity: float) -> float:
        """Calculate carbon footprint for energy trade."""
        # Carbon intensity factors (kg CO2 per MWh)
        carbon_intensities = {
            "OIL_USD": 650.0,
            "GAS_USD": 400.0,
            "COAL_USD": 900.0,
            "SOLAR_USD": 0.0,
            "WIND_USD": 0.0,
            "HYDRO_USD": 0.0,
            "NUCLEAR_USD": 0.0,
            "BATTERY_USD": 0.0
        }
        
        carbon_intensity = carbon_intensities.get(energy_symbol, 500.0)  # Default
        carbon_footprint = energy_quantity * carbon_intensity / 1000  # Convert to tons
        
        return carbon_footprint
    
    async def create_carbon_neutral_trade(self, user_id: str, energy_symbol: str,
                                        energy_quantity: float, energy_price: Decimal) -> CarbonNeutralTrade:
        """Create a carbon-neutral energy trade."""
        logger.info(f"Creating carbon-neutral trade for user {user_id}")
        
        # Calculate carbon footprint
        carbon_footprint = await self.calculate_carbon_footprint(energy_symbol, energy_quantity)
        
        # Calculate credits needed
        carbon_credits_required = int(np.ceil(carbon_footprint))
        
        # Get current carbon credit price
        current_price = await self._get_current_carbon_price()
        carbon_credit_cost = Decimal(str(current_price)) * carbon_credits_required
        
        # Calculate total cost
        energy_cost = energy_price * Decimal(str(energy_quantity))
        total_trade_cost = energy_cost + carbon_credit_cost
        
        # Create trade
        trade = CarbonNeutralTrade(
            trade_id=f"trade_{int(time.time())}_{hash(user_id)}",
            user_id=user_id,
            energy_symbol=energy_symbol,
            energy_quantity=energy_quantity,
            energy_price=energy_price,
            carbon_footprint=carbon_footprint,
            carbon_credits_required=carbon_credits_required,
            carbon_credit_cost=carbon_credit_cost,
            total_trade_cost=total_trade_cost,
            trade_date=datetime.now(timezone.utc),
            carbon_neutral=True
        )
        
        self.carbon_neutral_trades.append(trade)
        
        logger.info(f"Carbon-neutral trade created: {trade.trade_id}")
        return trade
    
    async def offset_energy_trade(self, trade_id: str, user_id: str) -> CarbonOffset:
        """Offset carbon footprint of an energy trade."""
        logger.info(f"Offsetting energy trade: {trade_id}")
        
        # Find trade
        trade = next((t for t in self.carbon_neutral_trades if t.trade_id == trade_id), None)
        if not trade:
            raise ValueError(f"Trade not found: {trade_id}")
        
        if trade.user_id != user_id:
            raise ValueError("User not authorized to offset this trade")
        
        # Purchase and retire carbon credits
        project_id = await self._select_offset_project()
        credit = await self.purchase_carbon_credits(user_id, project_id, trade.carbon_credits_required)
        
        if credit:
            await self.retire_carbon_credits(credit.credit_id, f"Offset for trade {trade_id}")
        
        # Create offset record
        offset = CarbonOffset(
            offset_id=f"offset_{int(time.time())}_{hash(trade_id)}",
            user_id=user_id,
            energy_trade_id=trade_id,
            carbon_credits_used=trade.carbon_credits_required,
            total_cost=trade.carbon_credit_cost,
            currency="USD",
            offset_date=datetime.now(timezone.utc),
            verification_status="verified"
        )
        
        # Link offset to trade
        trade.offset_transaction_id = offset.offset_id
        
        self.offsets.append(offset)
        
        logger.info(f"Carbon offset created: {offset.offset_id}")
        return offset
    
    async def _select_offset_project(self) -> str:
        """Select a carbon project for offsetting."""
        # Simple selection logic - can be enhanced
        available_projects = [
            pid for pid, project in self.projects.items()
            if project.available_credits > 0 and project.standard in [CarbonStandard.VERRA, CarbonStandard.GOLD_STANDARD]
        ]
        
        if not available_projects:
            raise ValueError("No available carbon projects for offsetting")
        
        # Select project with lowest price
        selected_project = min(available_projects, key=lambda pid: self.projects[pid].price_per_credit)
        return selected_project
    
    async def _get_current_carbon_price(self) -> float:
        """Get current carbon credit price."""
        # Use average price from all standards
        if not self.carbon_prices:
            return 15.0  # Default price
        
        prices = [data["price"] for data in self.carbon_prices.values()]
        return float(np.mean(prices))
    
    async def _generate_credit_hash(self, credit: CarbonCredit) -> str:
        """Generate blockchain hash for carbon credit."""
        credit_data = {
            "credit_id": credit.credit_id,
            "project_id": credit.project_id,
            "serial_number": credit.serial_number,
            "vintage_year": credit.vintage_year,
            "issuance_date": credit.issuance_date.isoformat(),
            "status": credit.status.value
        }
        
        data_string = json.dumps(credit_data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    async def _update_credit_on_blockchain(self, credit: CarbonCredit):
        """Update credit status on blockchain."""
        # Placeholder for blockchain integration
        logger.info(f"Credit {credit.credit_id} updated on blockchain")
    
    async def get_user_carbon_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Get user's carbon credit portfolio."""
        user_credits = [c for c in self.credits.values() if c.buyer_id == user_id]
        user_offsets = [o for o in self.offsets if o.user_id == user_id]
        user_trades = [t for t in self.carbon_neutral_trades if t.user_id == user_id]
        
        portfolio = {
            "user_id": user_id,
            "total_credits": len(user_credits),
            "available_credits": len([c for c in user_credits if c.status == CarbonCreditStatus.RESERVED]),
            "retired_credits": len([c for c in user_credits if c.status == CarbonCreditStatus.RETIRED]),
            "total_offset": sum(o.carbon_credits_used for o in user_offsets),
            "carbon_neutral_trades": len(user_trades),
            "total_investment": sum(c.price for c in user_credits),
            "credits": [asdict(c) for c in user_credits],
            "offsets": [asdict(o) for o in user_offsets],
            "trades": [asdict(t) for t in user_trades]
        }
        
        return portfolio
    
    async def get_carbon_market_data(self) -> Dict[str, Any]:
        """Get carbon market data and analytics."""
        market_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_projects": len(self.projects),
            "total_available_credits": sum(p.available_credits for p in self.projects.values()),
            "average_price": float(np.mean([p.price_per_credit for p in self.projects.values()])),
            "price_by_standard": {
                standard.value: {
                    "count": len([p for p in self.projects.values() if p.standard == standard]),
                    "avg_price": float(np.mean([p.price_per_credit for p in self.projects.values() if p.standard == standard]))
                }
                for standard in CarbonStandard
            },
            "price_by_type": {
                project_type.value: {
                    "count": len([p for p in self.projects.values() if p.project_type == project_type]),
                    "avg_price": float(np.mean([p.price_per_credit for p in self.projects.values() if p.project_type == project_type]))
                }
                for project_type in CarbonProjectType
            },
            "recent_prices": self.carbon_prices,
            "market_volume": {
                "total_trades": len(self.carbon_neutral_trades),
                "total_offsets": len(self.offsets),
                "total_credits_traded": sum(o.carbon_credits_used for o in self.offsets)
            }
        }
        
        return market_data
    
    async def generate_esg_report(self, user_id: str, 
                                start_date: datetime, 
                                end_date: datetime) -> Dict[str, Any]:
        """Generate ESG compliance report for user."""
        # Filter data by date range
        user_offsets = [
            o for o in self.offsets 
            if o.user_id == user_id and start_date <= o.offset_date <= end_date
        ]
        
        user_trades = [
            t for t in self.carbon_neutral_trades 
            if t.user_id == user_id and start_date <= t.trade_date <= end_date
        ]
        
        # Calculate metrics
        total_carbon_offset = sum(o.carbon_credits_used for o in user_offsets)
        total_energy_traded = sum(t.energy_quantity for t in user_trades)
        total_carbon_footprint = sum(t.carbon_footprint for t in user_trades)
        carbon_neutrality_ratio = total_carbon_offset / max(total_carbon_footprint, 1)
        
        # Generate report
        report = {
            "user_id": user_id,
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "carbon_metrics": {
                "total_carbon_offset_tons": total_carbon_offset,
                "total_carbon_footprint_tons": total_carbon_footprint,
                "carbon_neutrality_ratio": carbon_neutrality_ratio,
                "carbon_neutrality_percentage": min(100.0, carbon_neutrality_ratio * 100)
            },
            "energy_metrics": {
                "total_energy_traded_mwh": total_energy_traded,
                "carbon_neutral_trades": len(user_trades),
                "average_trade_size_mwh": total_energy_traded / max(len(user_trades), 1)
            },
            "esg_compliance": {
                "carbon_neutral": carbon_neutrality_ratio >= 1.0,
                "sustainable_energy_ratio": len([t for t in user_trades if t.energy_symbol in ["SOLAR_USD", "WIND_USD", "HYDRO_USD"]]) / max(len(user_trades), 1),
                "carbon_offset_verification": all(o.verification_status == "verified" for o in user_offsets)
            },
            "recommendations": self._generate_esg_recommendations(carbon_neutrality_ratio, user_trades)
        }
        
        return report
    
    def _generate_esg_recommendations(self, carbon_neutrality_ratio: float, 
                                    trades: List[CarbonNeutralTrade]) -> List[str]:
        """Generate ESG improvement recommendations."""
        recommendations = []
        
        if carbon_neutrality_ratio < 1.0:
            recommendations.append("Increase carbon offset purchases to achieve carbon neutrality")
        
        renewable_trades = [t for t in trades if t.energy_symbol in ["SOLAR_USD", "WIND_USD", "HYDRO_USD"]]
        renewable_ratio = len(renewable_trades) / max(len(trades), 1)
        
        if renewable_ratio < 0.5:
            recommendations.append("Increase renewable energy trading to improve sustainability profile")
        
        if len(trades) > 0:
            avg_carbon_footprint = sum(t.carbon_footprint for t in trades) / len(trades)
            if avg_carbon_footprint > 100:  # High carbon intensity
                recommendations.append("Consider lower carbon intensity energy sources")
        
        recommendations.append("Continue monitoring and reporting carbon footprint for ESG compliance")
        
        return recommendations
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get carbon credit service status."""
        return {
            "status": "operational",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_projects": len(self.projects),
            "total_credits": len(self.credits),
            "total_offsets": len(self.offsets),
            "total_trades": len(self.carbon_neutral_trades),
            "price_sources": len(self.carbon_prices),
            "last_price_update": max([data["timestamp"] for data in self.carbon_prices.values()]) if self.carbon_prices else None,
            "supported_standards": [standard.value for standard in CarbonStandard],
            "supported_project_types": [pt.value for pt in CarbonProjectType]
        }
