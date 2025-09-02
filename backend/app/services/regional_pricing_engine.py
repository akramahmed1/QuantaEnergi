"""
Regional Pricing Engine for ETRM/CTRM Trading
Handles commodity pricing across different regions and markets
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import math
import logging

logger = logging.getLogger(__name__)


class RegionalPricingEngine:
    """Service for managing regional commodity pricing"""
    
    def __init__(self):
        self.base_prices = {}  # In-memory storage for stubs
        self.regional_multipliers = {}
        self.quality_premiums = {}
        self.transport_costs = {}
        self.market_data = {}
        
        # Initialize stub data
        self._initialize_stub_data()
    
    def _initialize_stub_data(self):
        """Initialize stub pricing data"""
        # Base prices for major commodities (USD per unit)
        self.base_prices = {
            "crude_oil": 85.0,      # USD per barrel
            "natural_gas": 3.5,      # USD per MMBtu
            "refined_products": 2.8, # USD per gallon
            "coal": 120.0,           # USD per ton
            "lng": 12.0              # USD per MMBtu
        }
        
        # Regional multipliers
        self.regional_multipliers = {
            "middle_east": {
                "crude_oil": 1.05,      # 5% premium for Middle East crude
                "natural_gas": 1.02,    # 2% premium
                "refined_products": 1.03,
                "coal": 1.0,
                "lng": 1.08
            },
            "usa": {
                "crude_oil": 1.0,       # Base price
                "natural_gas": 1.0,
                "refined_products": 1.0,
                "coal": 1.0,
                "lng": 1.0
            },
            "europe": {
                "crude_oil": 1.08,      # 8% premium for European market
                "natural_gas": 1.15,    # 15% premium due to supply constraints
                "refined_products": 1.12,
                "coal": 1.05,
                "lng": 1.20
            },
            "uk": {
                "crude_oil": 1.10,      # 10% premium for UK market
                "natural_gas": 1.18,    # 18% premium
                "refined_products": 1.15,
                "coal": 1.08,
                "lng": 1.25
            },
            "guyana": {
                "crude_oil": 1.02,      # 2% premium for Guyana crude
                "natural_gas": 1.0,
                "refined_products": 1.0,
                "coal": 1.0,
                "lng": 1.0
            }
        }
        
        # Quality premiums
        self.quality_premiums = {
            "crude_oil": {
                "light_sweet": 1.05,    # 5% premium for light sweet crude
                "medium_sour": 1.0,     # Base price
                "heavy_sour": 0.95      # 5% discount for heavy sour crude
            },
            "natural_gas": {
                "high_btu": 1.03,       # 3% premium for high BTU gas
                "standard": 1.0,        # Base price
                "low_btu": 0.97         # 3% discount for low BTU gas
            }
        }
    
    def calculate_regional_price(self, commodity: str, region: str, 
                                quality: Optional[str] = None, 
                                delivery_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate regional price for commodity
        
        Args:
            commodity: Commodity type
            region: Target region
            quality: Quality specification
            delivery_date: Delivery date for forward pricing
            
        Returns:
            Dict with pricing details
        """
        # TODO: Implement real market data integration
        if commodity not in self.base_prices:
            return {
                "success": False,
                "error": f"Commodity {commodity} not supported"
            }
        
        if region not in self.regional_multipliers:
            return {
                "success": False,
                "error": f"Region {region} not supported"
            }
        
        base_price = self.base_prices[commodity]
        regional_multiplier = self.regional_multipliers[region].get(commodity, 1.0)
        
        # Calculate quality premium
        quality_multiplier = 1.0
        if quality and commodity in self.quality_premiums:
            quality_multiplier = self.quality_premiums[commodity].get(quality, 1.0)
        
        # Calculate forward premium if delivery date specified
        forward_premium = 1.0
        if delivery_date:
            try:
                delivery_dt = datetime.fromisoformat(delivery_date)
                days_forward = (delivery_dt - datetime.now()).days
                if days_forward > 0:
                    # Stub forward premium calculation
                    forward_premium = 1.0 + (days_forward * 0.0001)  # 0.01% per day
            except ValueError:
                pass
        
        # Calculate final price
        final_price = base_price * regional_multiplier * quality_multiplier * forward_premium
        
        return {
            "success": True,
            "commodity": commodity,
            "region": region,
            "quality": quality,
            "delivery_date": delivery_date,
            "base_price": base_price,
            "regional_multiplier": regional_multiplier,
            "quality_multiplier": quality_multiplier,
            "forward_premium": forward_premium,
            "final_price": final_price,
            "currency": "USD",
            "calculation_method": "stub",
            "calculated_at": datetime.now().isoformat()
        }
    
    def calculate_basis_differential(self, commodity: str, origin_region: str, 
                                    destination_region: str) -> Dict[str, Any]:
        """
        Calculate basis differential between regions
        
        Args:
            commodity: Commodity type
            origin_region: Origin region
            destination_region: Destination region
            
        Returns:
            Dict with basis differential
        """
        # TODO: Implement real basis calculation
        origin_price = self.calculate_regional_price(commodity, origin_region)
        destination_price = self.calculate_regional_price(commodity, destination_region)
        
        if not origin_price["success"] or not destination_price["success"]:
            return {
                "success": False,
                "error": "Failed to calculate regional prices"
            }
        
        basis_differential = destination_price["final_price"] - origin_price["final_price"]
        basis_percentage = (basis_differential / origin_price["final_price"]) * 100
        
        return {
            "success": True,
            "commodity": commodity,
            "origin_region": origin_region,
            "destination_region": destination_region,
            "origin_price": origin_price["final_price"],
            "destination_price": destination_price["final_price"],
            "basis_differential": basis_differential,
            "basis_percentage": basis_percentage,
            "calculation_method": "stub",
            "calculated_at": datetime.now().isoformat()
        }
    
    def calculate_transport_cost(self, origin: str, destination: str, 
                                commodity: str, quantity: float) -> Dict[str, Any]:
        """
        Calculate transport cost between locations
        
        Args:
            origin: Origin location
            destination: Destination location
            commodity: Commodity type
            quantity: Quantity to transport
            
        Returns:
            Dict with transport cost details
        """
        # TODO: Implement real transport cost calculation
        # Stub transport costs
        base_transport_cost = 0.05  # $0.05 per unit per km
        
        # Distance calculation stub
        distance = self._calculate_distance(origin, destination)
        
        # Mode-specific costs
        transport_costs = {
            "pipeline": base_transport_cost * 0.3,      # 30% of base cost
            "rail": base_transport_cost * 0.7,          # 70% of base cost
            "truck": base_transport_cost * 1.0,         # 100% of base cost
            "ship": base_transport_cost * 0.4           # 40% of base cost
        }
        
        # Calculate costs for each mode
        mode_costs = {}
        for mode, cost_per_km in transport_costs.items():
            total_cost = distance * cost_per_km * quantity
            mode_costs[mode] = {
                "cost_per_km": cost_per_km,
                "total_cost": total_cost,
                "cost_per_unit": total_cost / quantity if quantity > 0 else 0
            }
        
        return {
            "origin": origin,
            "destination": destination,
            "commodity": commodity,
            "quantity": quantity,
            "distance": distance,
            "transport_costs": mode_costs,
            "recommended_mode": min(mode_costs.keys(), key=lambda x: mode_costs[x]["total_cost"]),
            "calculation_method": "stub",
            "calculated_at": datetime.now().isoformat()
        }
    
    def calculate_total_delivered_cost(self, commodity: str, origin_region: str, 
                                      destination_region: str, quantity: float,
                                      transport_mode: str = "pipeline") -> Dict[str, Any]:
        """
        Calculate total delivered cost including transport
        
        Args:
            commodity: Commodity type
            origin_region: Origin region
            destination_region: Destination region
            quantity: Quantity to deliver
            transport_mode: Preferred transport mode
            
        Returns:
            Dict with total delivered cost
        """
        # TODO: Implement comprehensive cost calculation
        # Get regional prices
        origin_price = self.calculate_regional_price(commodity, origin_region)
        destination_price = self.calculate_regional_price(commodity, destination_region)
        
        if not origin_price["success"] or not destination_price["success"]:
            return {
                "success": False,
                "error": "Failed to calculate regional prices"
            }
        
        # Calculate transport cost
        transport_cost = self.calculate_transport_cost(
            origin_region, destination_region, commodity, quantity
        )
        
        if not transport_cost.get("success", True):
            return {
                "success": False,
                "error": "Failed to calculate transport cost"
            }
        
        # Calculate costs
        origin_cost = origin_price["final_price"] * quantity
        transport_cost_amount = transport_cost["transport_costs"][transport_mode]["total_cost"]
        total_delivered_cost = origin_cost + transport_cost_amount
        
        # Calculate arbitrage opportunity
        destination_value = destination_price["final_price"] * quantity
        arbitrage_profit = destination_value - total_delivered_cost
        arbitrage_margin = (arbitrage_profit / total_delivered_cost) * 100 if total_delivered_cost > 0 else 0
        
        return {
            "success": True,
            "commodity": commodity,
            "origin_region": origin_region,
            "destination_region": destination_region,
            "quantity": quantity,
            "transport_mode": transport_mode,
            "origin_price": origin_price["final_price"],
            "destination_price": destination_price["final_price"],
            "origin_cost": origin_cost,
            "transport_cost": transport_cost_amount,
            "total_delivered_cost": total_delivered_cost,
            "destination_value": destination_value,
            "arbitrage_profit": arbitrage_profit,
            "arbitrage_margin": arbitrage_margin,
            "profitable": arbitrage_profit > 0,
            "calculation_method": "stub",
            "calculated_at": datetime.now().isoformat()
        }
    
    def get_market_summary(self, commodity: str, regions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get market summary for commodity across regions
        
        Args:
            commodity: Commodity type
            regions: Optional list of regions to include
            
        Returns:
            Dict with market summary
        """
        # TODO: Implement real market data aggregation
        if regions is None:
            regions = list(self.regional_multipliers.keys())
        
        market_data = {}
        prices = []
        
        for region in regions:
            price_data = self.calculate_regional_price(commodity, region)
            if price_data["success"]:
                market_data[region] = price_data
                prices.append(price_data["final_price"])
        
        if not prices:
            return {
                "success": False,
                "error": "No valid prices found"
            }
        
        # Calculate market statistics
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        price_spread = max_price - min_price
        price_volatility = price_spread / avg_price if avg_price > 0 else 0
        
        return {
            "success": True,
            "commodity": commodity,
            "regions": regions,
            "market_data": market_data,
            "statistics": {
                "min_price": min_price,
                "max_price": max_price,
                "avg_price": avg_price,
                "price_spread": price_spread,
                "price_volatility": price_volatility,
                "total_regions": len(regions)
            },
            "calculation_method": "stub",
            "calculated_at": datetime.now().isoformat()
        }
    
    def _calculate_distance(self, origin: str, destination: str) -> float:
        """Stub distance calculation"""
        # TODO: Implement real distance calculation with geocoding
        # Placeholder distances between major regions
        distances = {
            ("middle_east", "europe"): 4000,
            ("middle_east", "usa"): 12000,
            ("middle_east", "uk"): 4500,
            ("middle_east", "guyana"): 11000,
            ("usa", "europe"): 7000,
            ("usa", "uk"): 6000,
            ("usa", "guyana"): 3000,
            ("europe", "uk"): 500,
            ("europe", "guyana"): 8000,
            ("uk", "guyana"): 7500
        }
        
        # Check both directions
        for (loc1, loc2), distance in distances.items():
            if (origin == loc1 and destination == loc2) or (origin == loc2 and destination == loc1):
                return distance
        
        # Default distance if not found
        return 5000.0
