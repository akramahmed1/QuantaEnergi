"""
Renewables & DER Engine for QuantaEnergi ETRM/CTRM Platform
Implements renewables/DER-specific modules including:
- Battery storage optimization
- Virtual power plants
- Renewables certificate/offsets
- DER aggregation
- Grid integration
- Carbon trading
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import math

logger = logging.getLogger(__name__)

class DERType(Enum):
    """Distributed Energy Resource types"""
    SOLAR_PV = "solar_pv"
    WIND_TURBINE = "wind_turbine"
    BATTERY_STORAGE = "battery_storage"
    FUEL_CELL = "fuel_cell"
    MICROTURBINE = "microturbine"
    CHP = "chp"  # Combined Heat and Power
    EV_CHARGER = "ev_charger"
    SMART_LOAD = "smart_load"

class CertificateType(Enum):
    """Renewable certificate types"""
    REC = "rec"  # Renewable Energy Certificate
    SREC = "srec"  # Solar Renewable Energy Certificate
    OREC = "orec"  # Offshore Renewable Energy Certificate
    CREDIT = "credit"  # Carbon Credit
    OFFSET = "offset"  # Carbon Offset

class GridService(Enum):
    """Grid services provided by DERs"""
    FREQUENCY_REGULATION = "frequency_regulation"
    SPINNING_RESERVE = "spinning_reserve"
    NON_SPINNING_RESERVE = "non_spinning_reserve"
    VOLTAGE_SUPPORT = "voltage_support"
    BLACK_START = "black_start"
    DEMAND_RESPONSE = "demand_response"

@dataclass
class DERAsset:
    """Distributed Energy Resource asset"""
    asset_id: str
    name: str
    der_type: DERType
    location: Dict[str, float]  # latitude, longitude
    capacity_kw: float
    efficiency: float = 0.85
    degradation_rate: float = 0.005  # per year
    installation_date: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    grid_connection: str = ""
    inverter_type: str = ""
    battery_chemistry: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BatteryStorage:
    """Battery storage system"""
    battery_id: str
    asset_id: str
    capacity_kwh: float
    power_kw: float
    chemistry: str  # "lithium_ion", "lead_acid", "flow", etc.
    round_trip_efficiency: float = 0.85
    depth_of_discharge: float = 0.8
    cycle_life: int = 5000
    current_soc: float = 0.5  # State of Charge (0-1)
    min_soc: float = 0.1
    max_soc: float = 0.9
    temperature: float = 25.0  # Celsius
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VirtualPowerPlant:
    """Virtual Power Plant"""
    vpp_id: str
    name: str
    description: str = ""
    der_assets: List[str] = field(default_factory=list)
    total_capacity_kw: float = 0.0
    total_storage_kwh: float = 0.0
    grid_services: List[GridService] = field(default_factory=list)
    aggregation_strategy: str = "centralized"
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RenewableCertificate:
    """Renewable Energy Certificate"""
    certificate_id: str
    certificate_type: CertificateType
    asset_id: str
    generation_mwh: float
    generation_date: datetime
    certificate_date: datetime = field(default_factory=datetime.utcnow)
    price_per_mwh: float = 0.0
    buyer: Optional[str] = None
    seller: Optional[str] = None
    is_traded: bool = False
    is_retired: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CarbonOffset:
    """Carbon offset"""
    offset_id: str
    project_type: str  # "renewable", "forest", "energy_efficiency", etc.
    project_location: str
    co2_reduction_tonnes: float
    offset_date: datetime
    price_per_tonne: float = 0.0
    buyer: Optional[str] = None
    seller: Optional[str] = None
    is_traded: bool = False
    is_retired: bool = False
    verification_standard: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GridIntegration:
    """Grid integration parameters"""
    integration_id: str
    asset_id: str
    grid_operator: str
    interconnection_capacity_kw: float
    voltage_level: float  # kV
    power_factor: float = 0.95
    frequency_range: Tuple[float, float] = (59.5, 60.5)  # Hz
    voltage_range: Tuple[float, float] = (0.95, 1.05)  # per unit
    is_synchronized: bool = False
    last_sync: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class BatteryOptimizer:
    """Battery storage optimization engine"""
    
    def __init__(self):
        self.optimization_algorithms = {
            "economic": self._economic_optimization,
            "grid_services": self._grid_services_optimization,
            "renewable_matching": self._renewable_matching_optimization,
            "demand_response": self._demand_response_optimization
        }
    
    def optimize_battery_schedule(self, battery: BatteryStorage, 
                                market_prices: List[float],
                                renewable_forecast: List[float],
                                load_forecast: List[float],
                                optimization_horizon: int = 24,
                                algorithm: str = "economic") -> Dict[str, Any]:
        """Optimize battery charging/discharging schedule"""
        try:
            optimizer = self.optimization_algorithms.get(algorithm)
            if not optimizer:
                return {"error": f"Unknown optimization algorithm: {algorithm}"}
            
            return optimizer(battery, market_prices, renewable_forecast, 
                           load_forecast, optimization_horizon)
            
        except Exception as e:
            logger.error(f"Error optimizing battery schedule: {e}")
            return {"error": str(e)}
    
    def _economic_optimization(self, battery: BatteryStorage, market_prices: List[float],
                             renewable_forecast: List[float], load_forecast: List[float],
                             optimization_horizon: int) -> Dict[str, Any]:
        """Economic optimization - maximize profit from price arbitrage"""
        try:
            # Initialize optimization variables
            schedule = []
            soc = battery.current_soc
            total_profit = 0.0
            
            for hour in range(optimization_horizon):
                price = market_prices[hour] if hour < len(market_prices) else market_prices[-1]
                renewable = renewable_forecast[hour] if hour < len(renewable_forecast) else 0.0
                load = load_forecast[hour] if hour < len(load_forecast) else 0.0
                
                # Calculate net load (load - renewable)
                net_load = load - renewable
                
                # Determine optimal action
                if price < 0:  # Negative prices - charge battery
                    action = "charge"
                    power = min(battery.power_kw, (battery.max_soc - soc) * battery.capacity_kwh)
                    soc += power / battery.capacity_kwh
                elif price > 50:  # High prices - discharge battery
                    action = "discharge"
                    power = min(battery.power_kw, (soc - battery.min_soc) * battery.capacity_kwh)
                    soc -= power / battery.capacity_kwh
                else:  # Medium prices - hold
                    action = "hold"
                    power = 0.0
                
                # Calculate profit
                profit = power * price * battery.round_trip_efficiency
                total_profit += profit
                
                schedule.append({
                    "hour": hour,
                    "action": action,
                    "power_kw": power,
                    "soc": soc,
                    "price": price,
                    "profit": profit
                })
            
            return {
                "schedule": schedule,
                "total_profit": total_profit,
                "final_soc": soc,
                "algorithm": "economic"
            }
            
        except Exception as e:
            logger.error(f"Error in economic optimization: {e}")
            return {"error": str(e)}
    
    def _grid_services_optimization(self, battery: BatteryStorage, market_prices: List[float],
                                   renewable_forecast: List[float], load_forecast: List[float],
                                   optimization_horizon: int) -> Dict[str, Any]:
        """Grid services optimization - provide frequency regulation and reserves"""
        try:
            schedule = []
            soc = battery.current_soc
            total_revenue = 0.0
            
            for hour in range(optimization_horizon):
                # Grid services revenue (simplified)
                frequency_reg_revenue = 50.0  # $/MW
                spinning_reserve_revenue = 30.0  # $/MW
                
                # Calculate available capacity for grid services
                available_capacity = min(battery.power_kw, 
                                       (soc - battery.min_soc) * battery.capacity_kwh)
                
                # Provide grid services
                if available_capacity > 0:
                    action = "grid_services"
                    power = available_capacity * 0.5  # Use 50% for grid services
                    revenue = power * (frequency_reg_revenue + spinning_reserve_revenue) / 1000
                    total_revenue += revenue
                else:
                    action = "hold"
                    power = 0.0
                    revenue = 0.0
                
                schedule.append({
                    "hour": hour,
                    "action": action,
                    "power_kw": power,
                    "soc": soc,
                    "revenue": revenue
                })
            
            return {
                "schedule": schedule,
                "total_revenue": total_revenue,
                "final_soc": soc,
                "algorithm": "grid_services"
            }
            
        except Exception as e:
            logger.error(f"Error in grid services optimization: {e}")
            return {"error": str(e)}
    
    def _renewable_matching_optimization(self, battery: BatteryStorage, market_prices: List[float],
                                       renewable_forecast: List[float], load_forecast: List[float],
                                       optimization_horizon: int) -> Dict[str, Any]:
        """Renewable matching optimization - maximize renewable energy usage"""
        try:
            schedule = []
            soc = battery.current_soc
            renewable_usage = 0.0
            
            for hour in range(optimization_horizon):
                renewable = renewable_forecast[hour] if hour < len(renewable_forecast) else 0.0
                load = load_forecast[hour] if hour < len(load_forecast) else 0.0
                
                # Calculate net renewable generation
                net_renewable = renewable - load
                
                if net_renewable > 0:  # Excess renewable - charge battery
                    action = "charge"
                    power = min(battery.power_kw, net_renewable, 
                              (battery.max_soc - soc) * battery.capacity_kwh)
                    soc += power / battery.capacity_kwh
                    renewable_usage += power
                elif net_renewable < 0:  # Deficit - discharge battery
                    action = "discharge"
                    power = min(battery.power_kw, abs(net_renewable),
                              (soc - battery.min_soc) * battery.capacity_kwh)
                    soc -= power / battery.capacity_kwh
                else:  # Balanced - hold
                    action = "hold"
                    power = 0.0
                
                schedule.append({
                    "hour": hour,
                    "action": action,
                    "power_kw": power,
                    "soc": soc,
                    "renewable_usage": renewable_usage
                })
            
            return {
                "schedule": schedule,
                "total_renewable_usage": renewable_usage,
                "final_soc": soc,
                "algorithm": "renewable_matching"
            }
            
        except Exception as e:
            logger.error(f"Error in renewable matching optimization: {e}")
            return {"error": str(e)}
    
    def _demand_response_optimization(self, battery: BatteryStorage, market_prices: List[float],
                                    renewable_forecast: List[float], load_forecast: List[float],
                                    optimization_horizon: int) -> Dict[str, Any]:
        """Demand response optimization - reduce peak demand"""
        try:
            schedule = []
            soc = battery.current_soc
            peak_reduction = 0.0
            
            for hour in range(optimization_horizon):
                load = load_forecast[hour] if hour < len(load_forecast) else 0.0
                
                # Identify peak demand hours (simplified)
                is_peak = load > np.mean(load_forecast) * 1.2
                
                if is_peak and soc > battery.min_soc:
                    action = "discharge"
                    power = min(battery.power_kw, 
                              (soc - battery.min_soc) * battery.capacity_kwh)
                    soc -= power / battery.capacity_kwh
                    peak_reduction += power
                else:
                    action = "hold"
                    power = 0.0
                
                schedule.append({
                    "hour": hour,
                    "action": action,
                    "power_kw": power,
                    "soc": soc,
                    "is_peak": is_peak
                })
            
            return {
                "schedule": schedule,
                "total_peak_reduction": peak_reduction,
                "final_soc": soc,
                "algorithm": "demand_response"
            }
            
        except Exception as e:
            logger.error(f"Error in demand response optimization: {e}")
            return {"error": str(e)}

class VirtualPowerPlantManager:
    """Virtual Power Plant management"""
    
    def __init__(self):
        self.vpps: Dict[str, VirtualPowerPlant] = {}
        self.der_assets: Dict[str, DERAsset] = {}
        self.battery_optimizer = BatteryOptimizer()
        self.aggregation_engine = DERAggregationEngine()
        
    def create_vpp(self, name: str, description: str = "",
                  aggregation_strategy: str = "centralized") -> str:
        """Create Virtual Power Plant"""
        try:
            vpp_id = f"VPP_{uuid.uuid4().hex[:8].upper()}"
            
            vpp = VirtualPowerPlant(
                vpp_id=vpp_id,
                name=name,
                description=description,
                aggregation_strategy=aggregation_strategy
            )
            
            self.vpps[vpp_id] = vpp
            logger.info(f"Created VPP: {name}")
            return vpp_id
            
        except Exception as e:
            logger.error(f"Error creating VPP: {e}")
            return ""
    
    def add_der_to_vpp(self, vpp_id: str, der_asset: DERAsset) -> bool:
        """Add DER asset to VPP"""
        try:
            if vpp_id not in self.vpps:
                return False
            
            vpp = self.vpps[vpp_id]
            vpp.der_assets.append(der_asset.asset_id)
            vpp.total_capacity_kw += der_asset.capacity_kw
            
            # Add to DER assets registry
            self.der_assets[der_asset.asset_id] = der_asset
            
            # Update VPP capacity
            self._update_vpp_capacity(vpp_id)
            
            logger.info(f"Added DER {der_asset.asset_id} to VPP {vpp_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding DER to VPP: {e}")
            return False
    
    def _update_vpp_capacity(self, vpp_id: str):
        """Update VPP total capacity"""
        try:
            vpp = self.vpps[vpp_id]
            total_capacity = 0.0
            total_storage = 0.0
            
            for asset_id in vpp.der_assets:
                asset = self.der_assets.get(asset_id)
                if asset:
                    total_capacity += asset.capacity_kw
                    if asset.der_type == DERType.BATTERY_STORAGE:
                        # Get battery storage capacity
                        total_storage += asset.capacity_kw * 4  # Assume 4-hour storage
            
            vpp.total_capacity_kw = total_capacity
            vpp.total_storage_kwh = total_storage
            
        except Exception as e:
            logger.error(f"Error updating VPP capacity: {e}")
    
    def optimize_vpp_dispatch(self, vpp_id: str, market_prices: List[float],
                             renewable_forecast: List[float], load_forecast: List[float]) -> Dict[str, Any]:
        """Optimize VPP dispatch"""
        try:
            if vpp_id not in self.vpps:
                return {"error": "VPP not found"}
            
            vpp = self.vpps[vpp_id]
            
            # Get DER assets
            der_assets = [self.der_assets[asset_id] for asset_id in vpp.der_assets 
                         if asset_id in self.der_assets]
            
            # Optimize each DER asset
            optimization_results = {}
            total_dispatch = 0.0
            
            for asset in der_assets:
                if asset.der_type == DERType.BATTERY_STORAGE:
                    # Get battery storage
                    battery = self._get_battery_storage(asset.asset_id)
                    if battery:
                        result = self.battery_optimizer.optimize_battery_schedule(
                            battery, market_prices, renewable_forecast, load_forecast
                        )
                        optimization_results[asset.asset_id] = result
                        total_dispatch += result.get("total_profit", 0.0)
                else:
                    # Simple optimization for other DERs
                    result = self._optimize_der_asset(asset, market_prices)
                    optimization_results[asset.asset_id] = result
                    total_dispatch += result.get("dispatch", 0.0)
            
            return {
                "vpp_id": vpp_id,
                "total_dispatch": total_dispatch,
                "optimization_results": optimization_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error optimizing VPP dispatch: {e}")
            return {"error": str(e)}
    
    def _get_battery_storage(self, asset_id: str) -> Optional[BatteryStorage]:
        """Get battery storage for asset"""
        try:
            # This would integrate with actual battery storage system
            # For now, return mock battery
            return BatteryStorage(
                battery_id=f"BAT_{asset_id}",
                asset_id=asset_id,
                capacity_kwh=100.0,
                power_kw=25.0,
                chemistry="lithium_ion"
            )
        except Exception as e:
            logger.error(f"Error getting battery storage: {e}")
            return None
    
    def _optimize_der_asset(self, asset: DERAsset, market_prices: List[float]) -> Dict[str, Any]:
        """Optimize individual DER asset"""
        try:
            # Simple optimization based on market prices
            avg_price = np.mean(market_prices)
            
            if avg_price > 50:  # High prices - maximize generation
                dispatch = asset.capacity_kw * 0.9
            elif avg_price < 20:  # Low prices - minimize generation
                dispatch = asset.capacity_kw * 0.1
            else:  # Medium prices - moderate generation
                dispatch = asset.capacity_kw * 0.5
            
            return {
                "asset_id": asset.asset_id,
                "dispatch": dispatch,
                "revenue": dispatch * avg_price,
                "efficiency": asset.efficiency
            }
            
        except Exception as e:
            logger.error(f"Error optimizing DER asset: {e}")
            return {"error": str(e)}

class DERAggregationEngine:
    """DER aggregation engine"""
    
    def __init__(self):
        self.aggregation_strategies = {
            "centralized": self._centralized_aggregation,
            "distributed": self._distributed_aggregation,
            "hybrid": self._hybrid_aggregation
        }
    
    def aggregate_ders(self, der_assets: List[DERAsset], 
                      aggregation_strategy: str = "centralized") -> Dict[str, Any]:
        """Aggregate DER assets"""
        try:
            strategy = self.aggregation_strategies.get(aggregation_strategy)
            if not strategy:
                return {"error": f"Unknown aggregation strategy: {aggregation_strategy}"}
            
            return strategy(der_assets)
            
        except Exception as e:
            logger.error(f"Error aggregating DERs: {e}")
            return {"error": str(e)}
    
    def _centralized_aggregation(self, der_assets: List[DERAsset]) -> Dict[str, Any]:
        """Centralized aggregation strategy"""
        try:
            total_capacity = sum(asset.capacity_kw for asset in der_assets)
            total_storage = sum(asset.capacity_kw for asset in der_assets 
                              if asset.der_type == DERType.BATTERY_STORAGE)
            
            # Calculate aggregated characteristics
            avg_efficiency = np.mean([asset.efficiency for asset in der_assets])
            avg_degradation = np.mean([asset.degradation_rate for asset in der_assets])
            
            return {
                "strategy": "centralized",
                "total_capacity_kw": total_capacity,
                "total_storage_kwh": total_storage,
                "average_efficiency": avg_efficiency,
                "average_degradation_rate": avg_degradation,
                "asset_count": len(der_assets),
                "aggregated_power_curve": self._calculate_aggregated_power_curve(der_assets)
            }
            
        except Exception as e:
            logger.error(f"Error in centralized aggregation: {e}")
            return {"error": str(e)}
    
    def _distributed_aggregation(self, der_assets: List[DERAsset]) -> Dict[str, Any]:
        """Distributed aggregation strategy"""
        try:
            # Group assets by type
            assets_by_type = {}
            for asset in der_assets:
                asset_type = asset.der_type.value
                if asset_type not in assets_by_type:
                    assets_by_type[asset_type] = []
                assets_by_type[asset_type].append(asset)
            
            # Calculate type-specific aggregations
            type_aggregations = {}
            for asset_type, assets in assets_by_type.items():
                type_aggregations[asset_type] = {
                    "count": len(assets),
                    "total_capacity_kw": sum(asset.capacity_kw for asset in assets),
                    "average_efficiency": np.mean([asset.efficiency for asset in assets])
                }
            
            return {
                "strategy": "distributed",
                "type_aggregations": type_aggregations,
                "total_assets": len(der_assets)
            }
            
        except Exception as e:
            logger.error(f"Error in distributed aggregation: {e}")
            return {"error": str(e)}
    
    def _hybrid_aggregation(self, der_assets: List[DERAsset]) -> Dict[str, Any]:
        """Hybrid aggregation strategy"""
        try:
            # Combine centralized and distributed approaches
            centralized_result = self._centralized_aggregation(der_assets)
            distributed_result = self._distributed_aggregation(der_assets)
            
            return {
                "strategy": "hybrid",
                "centralized": centralized_result,
                "distributed": distributed_result,
                "recommendation": self._get_hybrid_recommendation(der_assets)
            }
            
        except Exception as e:
            logger.error(f"Error in hybrid aggregation: {e}")
            return {"error": str(e)}
    
    def _calculate_aggregated_power_curve(self, der_assets: List[DERAsset]) -> List[float]:
        """Calculate aggregated power curve"""
        try:
            # Generate 24-hour power curve
            power_curve = []
            
            for hour in range(24):
                total_power = 0.0
                
                for asset in der_assets:
                    if asset.der_type == DERType.SOLAR_PV:
                        # Solar generation curve
                        solar_factor = max(0, math.sin(math.pi * (hour - 6) / 12))
                        total_power += asset.capacity_kw * solar_factor
                    elif asset.der_type == DERType.WIND_TURBINE:
                        # Wind generation (simplified)
                        wind_factor = 0.3 + 0.4 * math.sin(2 * math.pi * hour / 24)
                        total_power += asset.capacity_kw * wind_factor
                    elif asset.der_type == DERType.BATTERY_STORAGE:
                        # Battery can charge/discharge
                        total_power += asset.capacity_kw * 0.5  # Assume 50% utilization
                
                power_curve.append(total_power)
            
            return power_curve
            
        except Exception as e:
            logger.error(f"Error calculating aggregated power curve: {e}")
            return []
    
    def _get_hybrid_recommendation(self, der_assets: List[DERAsset]) -> str:
        """Get hybrid aggregation recommendation"""
        try:
            # Analyze asset mix
            solar_count = len([a for a in der_assets if a.der_type == DERType.SOLAR_PV])
            wind_count = len([a for a in der_assets if a.der_type == DERType.WIND_TURBINE])
            battery_count = len([a for a in der_assets if a.der_type == DERType.BATTERY_STORAGE])
            
            if battery_count > 0:
                return "Use centralized control for storage, distributed for generation"
            elif solar_count > wind_count:
                return "Use distributed control for solar, centralized for wind"
            else:
                return "Use centralized control for all assets"
                
        except Exception as e:
            logger.error(f"Error getting hybrid recommendation: {e}")
            return "Use centralized control"

class RenewableCertificateManager:
    """Renewable certificate management"""
    
    def __init__(self):
        self.certificates: Dict[str, RenewableCertificate] = {}
        self.carbon_offsets: Dict[str, CarbonOffset] = {}
        self.trading_engine = CertificateTradingEngine()
        
    def create_certificate(self, certificate_type: CertificateType, asset_id: str,
                          generation_mwh: float, generation_date: datetime,
                          price_per_mwh: float = 0.0) -> str:
        """Create renewable certificate"""
        try:
            certificate_id = f"CERT_{uuid.uuid4().hex[:8].upper()}"
            
            certificate = RenewableCertificate(
                certificate_id=certificate_id,
                certificate_type=certificate_type,
                asset_id=asset_id,
                generation_mwh=generation_mwh,
                generation_date=generation_date,
                price_per_mwh=price_per_mwh
            )
            
            self.certificates[certificate_id] = certificate
            logger.info(f"Created certificate: {certificate_id}")
            return certificate_id
            
        except Exception as e:
            logger.error(f"Error creating certificate: {e}")
            return ""
    
    def create_carbon_offset(self, project_type: str, project_location: str,
                           co2_reduction_tonnes: float, offset_date: datetime,
                           price_per_tonne: float = 0.0) -> str:
        """Create carbon offset"""
        try:
            offset_id = f"OFFSET_{uuid.uuid4().hex[:8].upper()}"
            
            offset = CarbonOffset(
                offset_id=offset_id,
                project_type=project_type,
                project_location=project_location,
                co2_reduction_tonnes=co2_reduction_tonnes,
                offset_date=offset_date,
                price_per_tonne=price_per_tonne
            )
            
            self.carbon_offsets[offset_id] = offset
            logger.info(f"Created carbon offset: {offset_id}")
            return offset_id
            
        except Exception as e:
            logger.error(f"Error creating carbon offset: {e}")
            return ""
    
    def trade_certificate(self, certificate_id: str, buyer: str, seller: str,
                         trade_price: float) -> bool:
        """Trade renewable certificate"""
        try:
            if certificate_id not in self.certificates:
                return False
            
            certificate = self.certificates[certificate_id]
            certificate.buyer = buyer
            certificate.seller = seller
            certificate.price_per_mwh = trade_price
            certificate.is_traded = True
            
            logger.info(f"Traded certificate: {certificate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error trading certificate: {e}")
            return False
    
    def retire_certificate(self, certificate_id: str, retirement_reason: str) -> bool:
        """Retire renewable certificate"""
        try:
            if certificate_id not in self.certificates:
                return False
            
            certificate = self.certificates[certificate_id]
            certificate.is_retired = True
            certificate.metadata["retirement_reason"] = retirement_reason
            certificate.metadata["retirement_date"] = datetime.utcnow().isoformat()
            
            logger.info(f"Retired certificate: {certificate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error retiring certificate: {e}")
            return False
    
    def get_certificate_portfolio(self, owner: str) -> Dict[str, Any]:
        """Get certificate portfolio for owner"""
        try:
            owned_certificates = []
            traded_certificates = []
            retired_certificates = []
            
            for cert in self.certificates.values():
                if cert.seller == owner:
                    owned_certificates.append(cert)
                elif cert.buyer == owner:
                    traded_certificates.append(cert)
                
                if cert.is_retired:
                    retired_certificates.append(cert)
            
            return {
                "owner": owner,
                "owned_certificates": len(owned_certificates),
                "traded_certificates": len(traded_certificates),
                "retired_certificates": len(retired_certificates),
                "total_mwh": sum(cert.generation_mwh for cert in owned_certificates),
                "total_value": sum(cert.generation_mwh * cert.price_per_mwh for cert in owned_certificates)
            }
            
        except Exception as e:
            logger.error(f"Error getting certificate portfolio: {e}")
            return {"error": str(e)}

class CertificateTradingEngine:
    """Certificate trading engine"""
    
    def __init__(self):
        self.market_prices: Dict[str, float] = {}
        self.trading_history: List[Dict[str, Any]] = []
        
    def get_market_price(self, certificate_type: CertificateType) -> float:
        """Get current market price for certificate type"""
        try:
            # Simulate market prices
            base_prices = {
                CertificateType.REC: 5.0,
                CertificateType.SREC: 15.0,
                CertificateType.OREC: 25.0,
                CertificateType.CREDIT: 50.0,
                CertificateType.OFFSET: 10.0
            }
            
            base_price = base_prices.get(certificate_type, 5.0)
            
            # Add some volatility
            volatility = 0.1
            price_change = np.random.normal(0, volatility)
            current_price = base_price * (1 + price_change)
            
            return max(current_price, 0.1)  # Minimum price
            
        except Exception as e:
            logger.error(f"Error getting market price: {e}")
            return 5.0
    
    def execute_trade(self, certificate_id: str, buyer: str, seller: str,
                     quantity: float, price: float) -> Dict[str, Any]:
        """Execute certificate trade"""
        try:
            trade_id = f"TRADE_{uuid.uuid4().hex[:8].upper()}"
            
            trade = {
                "trade_id": trade_id,
                "certificate_id": certificate_id,
                "buyer": buyer,
                "seller": seller,
                "quantity": quantity,
                "price": price,
                "total_value": quantity * price,
                "trade_date": datetime.utcnow().isoformat(),
                "status": "completed"
            }
            
            self.trading_history.append(trade)
            
            logger.info(f"Executed trade: {trade_id}")
            return trade
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return {"error": str(e)}

class GridIntegrationManager:
    """Grid integration management"""
    
    def __init__(self):
        self.grid_integrations: Dict[str, GridIntegration] = {}
        self.synchronization_engine = GridSynchronizationEngine()
        
    def create_grid_integration(self, asset_id: str, grid_operator: str,
                              interconnection_capacity_kw: float,
                              voltage_level: float) -> str:
        """Create grid integration"""
        try:
            integration_id = f"GRID_{uuid.uuid4().hex[:8].upper()}"
            
            integration = GridIntegration(
                integration_id=integration_id,
                asset_id=asset_id,
                grid_operator=grid_operator,
                interconnection_capacity_kw=interconnection_capacity_kw,
                voltage_level=voltage_level
            )
            
            self.grid_integrations[integration_id] = integration
            logger.info(f"Created grid integration: {integration_id}")
            return integration_id
            
        except Exception as e:
            logger.error(f"Error creating grid integration: {e}")
            return ""
    
    def synchronize_with_grid(self, integration_id: str) -> bool:
        """Synchronize DER with grid"""
        try:
            if integration_id not in self.grid_integrations:
                return False
            
            integration = self.grid_integrations[integration_id]
            
            # Perform synchronization
            sync_result = self.synchronization_engine.synchronize(integration)
            
            if sync_result["success"]:
                integration.is_synchronized = True
                integration.last_sync = datetime.utcnow()
                logger.info(f"Synchronized with grid: {integration_id}")
                return True
            else:
                logger.error(f"Grid synchronization failed: {sync_result['error']}")
                return False
            
        except Exception as e:
            logger.error(f"Error synchronizing with grid: {e}")
            return False

class GridSynchronizationEngine:
    """Grid synchronization engine"""
    
    def synchronize(self, integration: GridIntegration) -> Dict[str, Any]:
        """Synchronize DER with grid"""
        try:
            # Simulate synchronization process
            sync_checks = {
                "frequency_match": self._check_frequency_match(integration),
                "voltage_match": self._check_voltage_match(integration),
                "phase_match": self._check_phase_match(integration),
                "power_factor_match": self._check_power_factor_match(integration)
            }
            
            all_checks_passed = all(sync_checks.values())
            
            if all_checks_passed:
                return {
                    "success": True,
                    "sync_checks": sync_checks,
                    "message": "Successfully synchronized with grid"
                }
            else:
                return {
                    "success": False,
                    "sync_checks": sync_checks,
                    "error": "Synchronization checks failed"
                }
            
        except Exception as e:
            logger.error(f"Error in grid synchronization: {e}")
            return {"success": False, "error": str(e)}
    
    def _check_frequency_match(self, integration: GridIntegration) -> bool:
        """Check frequency match"""
        try:
            # Simulate frequency check
            current_frequency = 60.0 + np.random.normal(0, 0.1)
            min_freq, max_freq = integration.frequency_range
            
            return min_freq <= current_frequency <= max_freq
            
        except Exception as e:
            logger.error(f"Error checking frequency match: {e}")
            return False
    
    def _check_voltage_match(self, integration: GridIntegration) -> bool:
        """Check voltage match"""
        try:
            # Simulate voltage check
            current_voltage = 1.0 + np.random.normal(0, 0.02)
            min_voltage, max_voltage = integration.voltage_range
            
            return min_voltage <= current_voltage <= max_voltage
            
        except Exception as e:
            logger.error(f"Error checking voltage match: {e}")
            return False
    
    def _check_phase_match(self, integration: GridIntegration) -> bool:
        """Check phase match"""
        try:
            # Simulate phase check
            return True  # Simplified
            
        except Exception as e:
            logger.error(f"Error checking phase match: {e}")
            return False
    
    def _check_power_factor_match(self, integration: GridIntegration) -> bool:
        """Check power factor match"""
        try:
            # Simulate power factor check
            current_pf = integration.power_factor + np.random.normal(0, 0.01)
            
            return 0.9 <= current_pf <= 1.0
            
        except Exception as e:
            logger.error(f"Error checking power factor match: {e}")
            return False

class RenewablesDEREngine:
    """Main renewables and DER engine"""
    
    def __init__(self):
        self.battery_optimizer = BatteryOptimizer()
        self.vpp_manager = VirtualPowerPlantManager()
        self.certificate_manager = RenewableCertificateManager()
        self.grid_integration_manager = GridIntegrationManager()
        self.der_assets: Dict[str, DERAsset] = {}
        
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive renewables/DER status"""
        try:
            return {
                "der_assets": {
                    "total": len(self.der_assets),
                    "by_type": self._get_assets_by_type(),
                    "total_capacity_kw": sum(asset.capacity_kw for asset in self.der_assets.values())
                },
                "virtual_power_plants": {
                    "total": len(self.vpp_manager.vpps),
                    "total_capacity_kw": sum(vpp.total_capacity_kw for vpp in self.vpp_manager.vpps.values()),
                    "total_storage_kwh": sum(vpp.total_storage_kwh for vpp in self.vpp_manager.vpps.values())
                },
                "certificates": {
                    "total": len(self.certificate_manager.certificates),
                    "traded": len([c for c in self.certificate_manager.certificates.values() if c.is_traded]),
                    "retired": len([c for c in self.certificate_manager.certificates.values() if c.is_retired])
                },
                "carbon_offsets": {
                    "total": len(self.certificate_manager.carbon_offsets),
                    "total_co2_tonnes": sum(offset.co2_reduction_tonnes for offset in self.certificate_manager.carbon_offsets.values())
                },
                "grid_integrations": {
                    "total": len(self.grid_integration_manager.grid_integrations),
                    "synchronized": len([g for g in self.grid_integration_manager.grid_integrations.values() if g.is_synchronized])
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive status: {e}")
            return {"error": str(e)}
    
    def _get_assets_by_type(self) -> Dict[str, int]:
        """Get asset count by type"""
        try:
            assets_by_type = {}
            
            for asset in self.der_assets.values():
                asset_type = asset.der_type.value
                if asset_type not in assets_by_type:
                    assets_by_type[asset_type] = 0
                assets_by_type[asset_type] += 1
            
            return assets_by_type
            
        except Exception as e:
            logger.error(f"Error getting assets by type: {e}")
            return {}

# Global renewables/DER engine instance
renewables_der_engine = RenewablesDEREngine()

def create_der_asset(name: str, der_type: DERType, location: Dict[str, float],
                    capacity_kw: float, efficiency: float = 0.85) -> str:
    """Create DER asset"""
    try:
        asset_id = f"DER_{uuid.uuid4().hex[:8].upper()}"
        
        asset = DERAsset(
            asset_id=asset_id,
            name=name,
            der_type=der_type,
            location=location,
            capacity_kw=capacity_kw,
            efficiency=efficiency
        )
        
        renewables_der_engine.der_assets[asset_id] = asset
        logger.info(f"Created DER asset: {name}")
        return asset_id
        
    except Exception as e:
        logger.error(f"Error creating DER asset: {e}")
        return ""

def create_vpp(name: str, description: str = "",
              aggregation_strategy: str = "centralized") -> str:
    """Create Virtual Power Plant"""
    return renewables_der_engine.vpp_manager.create_vpp(name, description, aggregation_strategy)

def optimize_battery_schedule(battery_id: str, market_prices: List[float],
                            renewable_forecast: List[float], load_forecast: List[float],
                            algorithm: str = "economic") -> Dict[str, Any]:
    """Optimize battery schedule"""
    try:
        # Get battery storage
        battery = renewables_der_engine.vpp_manager._get_battery_storage(battery_id)
        if not battery:
            return {"error": "Battery not found"}
        
        return renewables_der_engine.battery_optimizer.optimize_battery_schedule(
            battery, market_prices, renewable_forecast, load_forecast, algorithm=algorithm
        )
        
    except Exception as e:
        logger.error(f"Error optimizing battery schedule: {e}")
        return {"error": str(e)}

def create_renewable_certificate(certificate_type: CertificateType, asset_id: str,
                              generation_mwh: float, generation_date: datetime,
                              price_per_mwh: float = 0.0) -> str:
    """Create renewable certificate"""
    return renewables_der_engine.certificate_manager.create_certificate(
        certificate_type, asset_id, generation_mwh, generation_date, price_per_mwh
    )

def create_carbon_offset(project_type: str, project_location: str,
                        co2_reduction_tonnes: float, offset_date: datetime,
                        price_per_tonne: float = 0.0) -> str:
    """Create carbon offset"""
    return renewables_der_engine.certificate_manager.create_carbon_offset(
        project_type, project_location, co2_reduction_tonnes, offset_date, price_per_tonne
    )

def get_renewables_der_status() -> Dict[str, Any]:
    """Get comprehensive renewables/DER status"""
    return renewables_der_engine.get_comprehensive_status()
