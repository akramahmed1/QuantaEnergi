"""
Exotic Derivatives Engine for QuantaEnergi ETRM/CTRM Platform
Implements support for exotic derivatives: Swaptions, FTRs, Virtuals, and other complex instruments
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import uuid
import json
from scipy.stats import norm
from scipy.optimize import minimize
import asyncio

logger = logging.getLogger(__name__)

class DerivativeType(Enum):
    """Derivative instrument types"""
    SWAPTION = "swaption"
    FTR = "ftr"  # Financial Transmission Right
    VIRTUAL = "virtual"
    SPREAD_OPTION = "spread_option"
    ASIAN_OPTION = "asian_option"
    BARRIER_OPTION = "barrier_option"
    LOOKBACK_OPTION = "lookback_option"
    COMPOUND_OPTION = "compound_option"
    EXOTIC_SWAP = "exotic_swap"
    CAP_FLOOR = "cap_floor"

class OptionStyle(Enum):
    """Option exercise styles"""
    EUROPEAN = "european"
    AMERICAN = "american"
    BERMUDAN = "bermudan"
    ASIAN = "asian"

class SettlementType(Enum):
    """Settlement types"""
    PHYSICAL = "physical"
    CASH = "cash"
    NET = "net"

@dataclass
class DerivativeInstrument:
    """Base derivative instrument"""
    instrument_id: str
    instrument_type: DerivativeType
    underlying_asset: str
    notional_amount: float
    strike_price: Optional[float] = None
    expiry_date: Optional[datetime] = None
    exercise_style: OptionStyle = OptionStyle.EUROPEAN
    settlement_type: SettlementType = SettlementType.CASH
    currency: str = "USD"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Swaption(DerivativeInstrument):
    """Swaption derivative instrument"""
    swap_tenor: str  # e.g., "5Y", "10Y"
    fixed_rate: float
    floating_rate_index: str  # e.g., "LIBOR", "SOFR"
    payment_frequency: str = "quarterly"
    day_count_convention: str = "30/360"
    
    def __post_init__(self):
        self.instrument_type = DerivativeType.SWAPTION

@dataclass
class FTR(DerivativeInstrument):
    """Financial Transmission Right"""
    source_node: str
    sink_node: str
    transmission_path: str
    congestion_zone: str
    transmission_capacity: float
    congestion_price: Optional[float] = None
    
    def __post_init__(self):
        self.instrument_type = DerivativeType.FTR

@dataclass
class Virtual(DerivativeInstrument):
    """Virtual power plant derivative"""
    generation_capacity: float
    storage_capacity: float
    fuel_type: str  # e.g., "solar", "wind", "battery"
    location: str
    grid_connection: str
    dispatch_profile: List[float] = field(default_factory=list)
    
    def __post_init__(self):
        self.instrument_type = DerivativeType.VIRTUAL

@dataclass
class SpreadOption(DerivativeInstrument):
    """Spread option between two assets"""
    asset1: str
    asset2: str
    spread_strike: float
    correlation: float = 0.0
    
    def __post_init__(self):
        self.instrument_type = DerivativeType.SPREAD_OPTION

@dataclass
class AsianOption(DerivativeInstrument):
    """Asian option with average price"""
    averaging_period: int  # days
    averaging_frequency: str = "daily"
    observation_dates: List[datetime] = field(default_factory=list)
    
    def __post_init__(self):
        self.instrument_type = DerivativeType.ASIAN_OPTION

@dataclass
class BarrierOption(DerivativeInstrument):
    """Barrier option"""
    barrier_level: float
    barrier_type: str  # "up", "down", "up_and_out", "down_and_out"
    rebate: float = 0.0
    
    def __post_init__(self):
        self.instrument_type = DerivativeType.BARRIER_OPTION

class PricingModel(ABC):
    """Abstract base class for pricing models"""
    
    @abstractmethod
    def calculate_price(self, instrument: DerivativeInstrument, market_data: Dict[str, Any]) -> float:
        """Calculate instrument price"""
        pass
    
    @abstractmethod
    def calculate_greeks(self, instrument: DerivativeInstrument, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate Greeks (delta, gamma, theta, vega, rho)"""
        pass

class BlackScholesModel(PricingModel):
    """Black-Scholes pricing model for vanilla options"""
    
    def calculate_price(self, instrument: DerivativeInstrument, market_data: Dict[str, Any]) -> float:
        """Calculate Black-Scholes price"""
        try:
            S = market_data.get('spot_price', 0)
            K = instrument.strike_price or 0
            T = self._time_to_expiry(instrument.expiry_date)
            r = market_data.get('risk_free_rate', 0.05)
            sigma = market_data.get('volatility', 0.2)
            
            if T <= 0:
                return max(S - K, 0) if instrument.instrument_type == DerivativeType.SWAPTION else 0
            
            d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)
            
            if instrument.instrument_type == DerivativeType.SWAPTION:
                price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
            else:
                price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            
            return max(price, 0)
            
        except Exception as e:
            logger.error(f"Black-Scholes pricing error: {e}")
            return 0.0
    
    def calculate_greeks(self, instrument: DerivativeInstrument, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate Greeks"""
        try:
            S = market_data.get('spot_price', 0)
            K = instrument.strike_price or 0
            T = self._time_to_expiry(instrument.expiry_date)
            r = market_data.get('risk_free_rate', 0.05)
            sigma = market_data.get('volatility', 0.2)
            
            if T <= 0:
                return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}
            
            d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)
            
            delta = norm.cdf(d1)
            gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
            theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)
            vega = S * norm.pdf(d1) * np.sqrt(T)
            rho = K * T * np.exp(-r * T) * norm.cdf(d2)
            
            return {
                "delta": delta,
                "gamma": gamma,
                "theta": theta,
                "vega": vega,
                "rho": rho
            }
            
        except Exception as e:
            logger.error(f"Greeks calculation error: {e}")
            return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}
    
    def _time_to_expiry(self, expiry_date: Optional[datetime]) -> float:
        """Calculate time to expiry in years"""
        if not expiry_date:
            return 0.0
        return (expiry_date - datetime.utcnow()).days / 365.25

class MonteCarloModel(PricingModel):
    """Monte Carlo pricing model for exotic derivatives"""
    
    def __init__(self, n_simulations: int = 10000):
        self.n_simulations = n_simulations
    
    def calculate_price(self, instrument: DerivativeInstrument, market_data: Dict[str, Any]) -> float:
        """Calculate price using Monte Carlo simulation"""
        try:
            if instrument.instrument_type == DerivativeType.ASIAN_OPTION:
                return self._price_asian_option(instrument, market_data)
            elif instrument.instrument_type == DerivativeType.BARRIER_OPTION:
                return self._price_barrier_option(instrument, market_data)
            elif instrument.instrument_type == DerivativeType.SPREAD_OPTION:
                return self._price_spread_option(instrument, market_data)
            else:
                return self._price_generic_exotic(instrument, market_data)
                
        except Exception as e:
            logger.error(f"Monte Carlo pricing error: {e}")
            return 0.0
    
    def _price_asian_option(self, instrument: AsianOption, market_data: Dict[str, Any]) -> float:
        """Price Asian option using Monte Carlo"""
        S0 = market_data.get('spot_price', 0)
        K = instrument.strike_price or 0
        T = self._time_to_expiry(instrument.expiry_date)
        r = market_data.get('risk_free_rate', 0.05)
        sigma = market_data.get('volatility', 0.2)
        n_observations = instrument.averaging_period
        
        if T <= 0:
            return 0.0
        
        dt = T / n_observations
        payoffs = []
        
        for _ in range(self.n_simulations):
            S = S0
            price_path = [S]
            
            for _ in range(n_observations):
                dW = np.random.normal(0, np.sqrt(dt))
                S *= np.exp((r - 0.5 * sigma**2) * dt + sigma * dW)
                price_path.append(S)
            
            average_price = np.mean(price_path)
            payoff = max(average_price - K, 0)
            payoffs.append(payoff)
        
        return np.exp(-r * T) * np.mean(payoffs)
    
    def _price_barrier_option(self, instrument: BarrierOption, market_data: Dict[str, Any]) -> float:
        """Price barrier option using Monte Carlo"""
        S0 = market_data.get('spot_price', 0)
        K = instrument.strike_price or 0
        B = instrument.barrier_level
        T = self._time_to_expiry(instrument.expiry_date)
        r = market_data.get('risk_free_rate', 0.05)
        sigma = market_data.get('volatility', 0.2)
        n_steps = 100
        
        if T <= 0:
            return 0.0
        
        dt = T / n_steps
        payoffs = []
        
        for _ in range(self.n_simulations):
            S = S0
            barrier_hit = False
            
            for _ in range(n_steps):
                dW = np.random.normal(0, np.sqrt(dt))
                S *= np.exp((r - 0.5 * sigma**2) * dt + sigma * dW)
                
                if instrument.barrier_type == "up_and_out" and S >= B:
                    barrier_hit = True
                    break
                elif instrument.barrier_type == "down_and_out" and S <= B:
                    barrier_hit = True
                    break
            
            if not barrier_hit:
                payoff = max(S - K, 0)
            else:
                payoff = instrument.rebate
            
            payoffs.append(payoff)
        
        return np.exp(-r * T) * np.mean(payoffs)
    
    def _price_spread_option(self, instrument: SpreadOption, market_data: Dict[str, Any]) -> float:
        """Price spread option using Monte Carlo"""
        S1 = market_data.get('asset1_price', 0)
        S2 = market_data.get('asset2_price', 0)
        K = instrument.spread_strike
        T = self._time_to_expiry(instrument.expiry_date)
        r = market_data.get('risk_free_rate', 0.05)
        sigma1 = market_data.get('asset1_volatility', 0.2)
        sigma2 = market_data.get('asset2_volatility', 0.2)
        rho = instrument.correlation
        
        if T <= 0:
            return 0.0
        
        payoffs = []
        
        for _ in range(self.n_simulations):
            # Generate correlated random numbers
            Z1 = np.random.normal(0, 1)
            Z2 = rho * Z1 + np.sqrt(1 - rho**2) * np.random.normal(0, 1)
            
            S1_T = S1 * np.exp((r - 0.5 * sigma1**2) * T + sigma1 * np.sqrt(T) * Z1)
            S2_T = S2 * np.exp((r - 0.5 * sigma2**2) * T + sigma2 * np.sqrt(T) * Z2)
            
            spread = S1_T - S2_T
            payoff = max(spread - K, 0)
            payoffs.append(payoff)
        
        return np.exp(-r * T) * np.mean(payoffs)
    
    def _price_generic_exotic(self, instrument: DerivativeInstrument, market_data: Dict[str, Any]) -> float:
        """Price generic exotic derivative"""
        # Simplified pricing for demonstration
        S = market_data.get('spot_price', 0)
        K = instrument.strike_price or 0
        T = self._time_to_expiry(instrument.expiry_date)
        r = market_data.get('risk_free_rate', 0.05)
        
        if T <= 0:
            return 0.0
        
        # Simple exotic pricing logic
        intrinsic_value = max(S - K, 0)
        time_value = intrinsic_value * np.exp(-r * T) * 0.1  # Simplified time value
        
        return intrinsic_value + time_value
    
    def calculate_greeks(self, instrument: DerivativeInstrument, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate Greeks using finite differences"""
        try:
            # Calculate base price
            base_price = self.calculate_price(instrument, market_data)
            
            # Delta calculation
            market_data_up = market_data.copy()
            market_data_up['spot_price'] *= 1.01
            price_up = self.calculate_price(instrument, market_data_up)
            delta = (price_up - base_price) / (market_data['spot_price'] * 0.01)
            
            # Gamma calculation
            market_data_down = market_data.copy()
            market_data_down['spot_price'] *= 0.99
            price_down = self.calculate_price(instrument, market_data_down)
            gamma = (price_up - 2 * base_price + price_down) / (market_data['spot_price'] * 0.01)**2
            
            return {
                "delta": delta,
                "gamma": gamma,
                "theta": 0,  # Simplified
                "vega": 0,   # Simplified
                "rho": 0     # Simplified
            }
            
        except Exception as e:
            logger.error(f"Greeks calculation error: {e}")
            return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}
    
    def _time_to_expiry(self, expiry_date: Optional[datetime]) -> float:
        """Calculate time to expiry in years"""
        if not expiry_date:
            return 0.0
        return (expiry_date - datetime.utcnow()).days / 365.25

class FTRPricingModel(PricingModel):
    """Specialized pricing model for Financial Transmission Rights"""
    
    def calculate_price(self, instrument: FTR, market_data: Dict[str, Any]) -> float:
        """Calculate FTR price based on congestion value"""
        try:
            # Get congestion data
            congestion_price = market_data.get('congestion_price', 0)
            transmission_capacity = instrument.transmission_capacity
            time_to_expiry = self._time_to_expiry(instrument.expiry_date)
            
            # FTR value is the expected congestion value
            expected_congestion = congestion_price * transmission_capacity
            
            # Apply time discounting
            discount_factor = np.exp(-0.05 * time_to_expiry)  # 5% discount rate
            ftr_value = expected_congestion * discount_factor
            
            return max(ftr_value, 0)
            
        except Exception as e:
            logger.error(f"FTR pricing error: {e}")
            return 0.0
    
    def calculate_greeks(self, instrument: FTR, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate FTR Greeks"""
        try:
            congestion_price = market_data.get('congestion_price', 0)
            transmission_capacity = instrument.transmission_capacity
            
            # Delta is the transmission capacity
            delta = transmission_capacity
            
            # Other Greeks are simplified for FTRs
            return {
                "delta": delta,
                "gamma": 0,
                "theta": 0,
                "vega": 0,
                "rho": 0
            }
            
        except Exception as e:
            logger.error(f"FTR Greeks calculation error: {e}")
            return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}
    
    def _time_to_expiry(self, expiry_date: Optional[datetime]) -> float:
        """Calculate time to expiry in years"""
        if not expiry_date:
            return 0.0
        return (expiry_date - datetime.utcnow()).days / 365.25

class VirtualPricingModel(PricingModel):
    """Specialized pricing model for Virtual Power Plant derivatives"""
    
    def calculate_price(self, instrument: Virtual, market_data: Dict[str, Any]) -> float:
        """Calculate Virtual PPA price"""
        try:
            # Get market data
            electricity_price = market_data.get('electricity_price', 0)
            fuel_price = market_data.get('fuel_price', 0)
            capacity_factor = market_data.get('capacity_factor', 0.8)
            
            # Calculate generation value
            generation_capacity = instrument.generation_capacity
            generation_value = electricity_price * generation_capacity * capacity_factor
            
            # Calculate storage value
            storage_capacity = instrument.storage_capacity
            storage_value = storage_capacity * electricity_price * 0.1  # 10% of electricity price
            
            # Calculate fuel cost
            fuel_cost = fuel_price * generation_capacity * capacity_factor * 0.1  # 10% fuel efficiency
            
            # Net value
            virtual_value = generation_value + storage_value - fuel_cost
            
            return max(virtual_value, 0)
            
        except Exception as e:
            logger.error(f"Virtual pricing error: {e}")
            return 0.0
    
    def calculate_greeks(self, instrument: Virtual, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate Virtual Greeks"""
        try:
            capacity_factor = market_data.get('capacity_factor', 0.8)
            generation_capacity = instrument.generation_capacity
            
            # Delta is the generation capacity
            delta = generation_capacity * capacity_factor
            
            return {
                "delta": delta,
                "gamma": 0,
                "theta": 0,
                "vega": 0,
                "rho": 0
            }
            
        except Exception as e:
            logger.error(f"Virtual Greeks calculation error: {e}")
            return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}

class ExoticDerivativesEngine:
    """Main engine for exotic derivatives management"""
    
    def __init__(self):
        self.instruments: Dict[str, DerivativeInstrument] = {}
        self.pricing_models: Dict[DerivativeType, PricingModel] = {
            DerivativeType.SWAPTION: BlackScholesModel(),
            DerivativeType.FTR: FTRPricingModel(),
            DerivativeType.VIRTUAL: VirtualPricingModel(),
            DerivativeType.SPREAD_OPTION: MonteCarloModel(),
            DerivativeType.ASIAN_OPTION: MonteCarloModel(),
            DerivativeType.BARRIER_OPTION: MonteCarloModel()
        }
        self.portfolio_risk = PortfolioRiskManager()
        
    def create_swaption(self, 
                       underlying_asset: str,
                       notional_amount: float,
                       strike_price: float,
                       expiry_date: datetime,
                       swap_tenor: str,
                       fixed_rate: float,
                       floating_rate_index: str = "SOFR") -> str:
        """Create a swaption instrument"""
        try:
            instrument_id = f"SWAPTION_{uuid.uuid4().hex[:8].upper()}"
            
            swaption = Swaption(
                instrument_id=instrument_id,
                instrument_type=DerivativeType.SWAPTION,
                underlying_asset=underlying_asset,
                notional_amount=notional_amount,
                strike_price=strike_price,
                expiry_date=expiry_date,
                swap_tenor=swap_tenor,
                fixed_rate=fixed_rate,
                floating_rate_index=floating_rate_index
            )
            
            self.instruments[instrument_id] = swaption
            logger.info(f"Created swaption: {instrument_id}")
            return instrument_id
            
        except Exception as e:
            logger.error(f"Error creating swaption: {e}")
            return ""
    
    def create_ftr(self,
                   source_node: str,
                   sink_node: str,
                   transmission_path: str,
                   congestion_zone: str,
                   transmission_capacity: float,
                   notional_amount: float,
                   expiry_date: datetime) -> str:
        """Create an FTR instrument"""
        try:
            instrument_id = f"FTR_{uuid.uuid4().hex[:8].upper()}"
            
            ftr = FTR(
                instrument_id=instrument_id,
                instrument_type=DerivativeType.FTR,
                underlying_asset=f"{source_node}-{sink_node}",
                notional_amount=notional_amount,
                expiry_date=expiry_date,
                source_node=source_node,
                sink_node=sink_node,
                transmission_path=transmission_path,
                congestion_zone=congestion_zone,
                transmission_capacity=transmission_capacity
            )
            
            self.instruments[instrument_id] = ftr
            logger.info(f"Created FTR: {instrument_id}")
            return instrument_id
            
        except Exception as e:
            logger.error(f"Error creating FTR: {e}")
            return ""
    
    def create_virtual(self,
                      generation_capacity: float,
                      storage_capacity: float,
                      fuel_type: str,
                      location: str,
                      grid_connection: str,
                      notional_amount: float,
                      expiry_date: datetime) -> str:
        """Create a virtual power plant instrument"""
        try:
            instrument_id = f"VIRTUAL_{uuid.uuid4().hex[:8].upper()}"
            
            virtual = Virtual(
                instrument_id=instrument_id,
                instrument_type=DerivativeType.VIRTUAL,
                underlying_asset=f"{fuel_type}_{location}",
                notional_amount=notional_amount,
                expiry_date=expiry_date,
                generation_capacity=generation_capacity,
                storage_capacity=storage_capacity,
                fuel_type=fuel_type,
                location=location,
                grid_connection=grid_connection
            )
            
            self.instruments[instrument_id] = virtual
            logger.info(f"Created Virtual: {instrument_id}")
            return instrument_id
            
        except Exception as e:
            logger.error(f"Error creating Virtual: {e}")
            return ""
    
    def create_spread_option(self,
                            asset1: str,
                            asset2: str,
                            notional_amount: float,
                            spread_strike: float,
                            expiry_date: datetime,
                            correlation: float = 0.0) -> str:
        """Create a spread option instrument"""
        try:
            instrument_id = f"SPREAD_{uuid.uuid4().hex[:8].upper()}"
            
            spread_option = SpreadOption(
                instrument_id=instrument_id,
                instrument_type=DerivativeType.SPREAD_OPTION,
                underlying_asset=f"{asset1}-{asset2}",
                notional_amount=notional_amount,
                strike_price=spread_strike,
                expiry_date=expiry_date,
                asset1=asset1,
                asset2=asset2,
                spread_strike=spread_strike,
                correlation=correlation
            )
            
            self.instruments[instrument_id] = spread_option
            logger.info(f"Created Spread Option: {instrument_id}")
            return instrument_id
            
        except Exception as e:
            logger.error(f"Error creating spread option: {e}")
            return ""
    
    def create_asian_option(self,
                           underlying_asset: str,
                           notional_amount: float,
                           strike_price: float,
                           expiry_date: datetime,
                           averaging_period: int) -> str:
        """Create an Asian option instrument"""
        try:
            instrument_id = f"ASIAN_{uuid.uuid4().hex[:8].upper()}"
            
            asian_option = AsianOption(
                instrument_id=instrument_id,
                instrument_type=DerivativeType.ASIAN_OPTION,
                underlying_asset=underlying_asset,
                notional_amount=notional_amount,
                strike_price=strike_price,
                expiry_date=expiry_date,
                averaging_period=averaging_period
            )
            
            self.instruments[instrument_id] = asian_option
            logger.info(f"Created Asian Option: {instrument_id}")
            return instrument_id
            
        except Exception as e:
            logger.error(f"Error creating Asian option: {e}")
            return ""
    
    def create_barrier_option(self,
                             underlying_asset: str,
                             notional_amount: float,
                             strike_price: float,
                             expiry_date: datetime,
                             barrier_level: float,
                             barrier_type: str) -> str:
        """Create a barrier option instrument"""
        try:
            instrument_id = f"BARRIER_{uuid.uuid4().hex[:8].upper()}"
            
            barrier_option = BarrierOption(
                instrument_id=instrument_id,
                instrument_type=DerivativeType.BARRIER_OPTION,
                underlying_asset=underlying_asset,
                notional_amount=notional_amount,
                strike_price=strike_price,
                expiry_date=expiry_date,
                barrier_level=barrier_level,
                barrier_type=barrier_type
            )
            
            self.instruments[instrument_id] = barrier_option
            logger.info(f"Created Barrier Option: {instrument_id}")
            return instrument_id
            
        except Exception as e:
            logger.error(f"Error creating barrier option: {e}")
            return ""
    
    def price_instrument(self, instrument_id: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Price an exotic derivative instrument"""
        try:
            if instrument_id not in self.instruments:
                return {"error": "Instrument not found"}
            
            instrument = self.instruments[instrument_id]
            pricing_model = self.pricing_models.get(instrument.instrument_type)
            
            if not pricing_model:
                return {"error": f"No pricing model for {instrument.instrument_type}"}
            
            # Calculate price and Greeks
            price = pricing_model.calculate_price(instrument, market_data)
            greeks = pricing_model.calculate_greeks(instrument, market_data)
            
            # Calculate risk metrics
            risk_metrics = self.portfolio_risk.calculate_instrument_risk(instrument, market_data)
            
            return {
                "instrument_id": instrument_id,
                "instrument_type": instrument.instrument_type.value,
                "price": round(price, 4),
                "greeks": greeks,
                "risk_metrics": risk_metrics,
                "market_data": market_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error pricing instrument {instrument_id}: {e}")
            return {"error": str(e)}
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary of all exotic derivatives"""
        try:
            summary = {
                "total_instruments": len(self.instruments),
                "instruments_by_type": {},
                "total_notional": 0,
                "expiring_soon": [],
                "high_risk_instruments": []
            }
            
            for instrument_id, instrument in self.instruments.items():
                # Count by type
                instrument_type = instrument.instrument_type.value
                if instrument_type not in summary["instruments_by_type"]:
                    summary["instruments_by_type"][instrument_type] = 0
                summary["instruments_by_type"][instrument_type] += 1
                
                # Sum notional amounts
                summary["total_notional"] += instrument.notional_amount
                
                # Check expiring soon (within 30 days)
                if instrument.expiry_date:
                    days_to_expiry = (instrument.expiry_date - datetime.utcnow()).days
                    if days_to_expiry <= 30:
                        summary["expiring_soon"].append({
                            "instrument_id": instrument_id,
                            "expiry_date": instrument.expiry_date.isoformat(),
                            "days_to_expiry": days_to_expiry
                        })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {"error": str(e)}
    
    def get_instrument_details(self, instrument_id: str) -> Dict[str, Any]:
        """Get detailed information about an instrument"""
        try:
            if instrument_id not in self.instruments:
                return {"error": "Instrument not found"}
            
            instrument = self.instruments[instrument_id]
            
            return {
                "instrument_id": instrument_id,
                "instrument_type": instrument.instrument_type.value,
                "underlying_asset": instrument.underlying_asset,
                "notional_amount": instrument.notional_amount,
                "strike_price": instrument.strike_price,
                "expiry_date": instrument.expiry_date.isoformat() if instrument.expiry_date else None,
                "exercise_style": instrument.exercise_style.value,
                "settlement_type": instrument.settlement_type.value,
                "currency": instrument.currency,
                "created_at": instrument.created_at.isoformat(),
                "metadata": instrument.metadata
            }
            
        except Exception as e:
            logger.error(f"Error getting instrument details: {e}")
            return {"error": str(e)}

class PortfolioRiskManager:
    """Portfolio risk management for exotic derivatives"""
    
    def calculate_instrument_risk(self, instrument: DerivativeInstrument, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate risk metrics for an instrument"""
        try:
            # Basic risk metrics
            notional = instrument.notional_amount
            volatility = market_data.get('volatility', 0.2)
            
            # Value at Risk (VaR) calculation
            confidence_level = 0.95
            var_1d = notional * volatility * norm.ppf(confidence_level)
            
            # Expected Shortfall (ES)
            es_1d = notional * volatility * norm.pdf(norm.ppf(confidence_level)) / (1 - confidence_level)
            
            # Maximum Drawdown
            max_drawdown = notional * volatility * 2  # Simplified
            
            return {
                "var_1d": round(var_1d, 2),
                "expected_shortfall_1d": round(es_1d, 2),
                "max_drawdown": round(max_drawdown, 2),
                "volatility": volatility,
                "notional": notional
            }
            
        except Exception as e:
            logger.error(f"Error calculating instrument risk: {e}")
            return {"error": str(e)}

# Global exotic derivatives engine instance
exotic_derivatives_engine = ExoticDerivativesEngine()

def create_swaption(underlying_asset: str, notional_amount: float, strike_price: float, 
                   expiry_date: datetime, swap_tenor: str, fixed_rate: float, 
                   floating_rate_index: str = "SOFR") -> str:
    """Create a swaption instrument"""
    return exotic_derivatives_engine.create_swaption(
        underlying_asset, notional_amount, strike_price, expiry_date, 
        swap_tenor, fixed_rate, floating_rate_index
    )

def create_ftr(source_node: str, sink_node: str, transmission_path: str, 
               congestion_zone: str, transmission_capacity: float, 
               notional_amount: float, expiry_date: datetime) -> str:
    """Create an FTR instrument"""
    return exotic_derivatives_engine.create_ftr(
        source_node, sink_node, transmission_path, congestion_zone, 
        transmission_capacity, notional_amount, expiry_date
    )

def create_virtual(generation_capacity: float, storage_capacity: float, fuel_type: str, 
                  location: str, grid_connection: str, notional_amount: float, 
                  expiry_date: datetime) -> str:
    """Create a virtual power plant instrument"""
    return exotic_derivatives_engine.create_virtual(
        generation_capacity, storage_capacity, fuel_type, location, 
        grid_connection, notional_amount, expiry_date
    )

def create_spread_option(asset1: str, asset2: str, notional_amount: float, 
                         spread_strike: float, expiry_date: datetime, 
                         correlation: float = 0.0) -> str:
    """Create a spread option instrument"""
    return exotic_derivatives_engine.create_spread_option(
        asset1, asset2, notional_amount, spread_strike, expiry_date, correlation
    )

def create_asian_option(underlying_asset: str, notional_amount: float, strike_price: float, 
                       expiry_date: datetime, averaging_period: int) -> str:
    """Create an Asian option instrument"""
    return exotic_derivatives_engine.create_asian_option(
        underlying_asset, notional_amount, strike_price, expiry_date, averaging_period
    )

def create_barrier_option(underlying_asset: str, notional_amount: float, strike_price: float, 
                          expiry_date: datetime, barrier_level: float, barrier_type: str) -> str:
    """Create a barrier option instrument"""
    return exotic_derivatives_engine.create_barrier_option(
        underlying_asset, notional_amount, strike_price, expiry_date, barrier_level, barrier_type
    )

def price_instrument(instrument_id: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
    """Price an exotic derivative instrument"""
    return exotic_derivatives_engine.price_instrument(instrument_id, market_data)

def get_portfolio_summary() -> Dict[str, Any]:
    """Get portfolio summary of all exotic derivatives"""
    return exotic_derivatives_engine.get_portfolio_summary()

def get_instrument_details(instrument_id: str) -> Dict[str, Any]:
    """Get detailed information about an instrument"""
    return exotic_derivatives_engine.get_instrument_details(instrument_id)
