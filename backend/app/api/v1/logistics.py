"""
Logistics and Inventory API endpoints for ETRM/CTRM operations
Handles supply chain optimization, inventory management, and logistics planning
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from ...services.logistics_manager import LogisticsManager
from ...services.inventory_manager import InventoryManager
from ...services.regional_pricing_engine import RegionalPricingEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/logistics", tags=["logistics_inventory"])

# Initialize services
logistics_manager = LogisticsManager()
inventory_manager = InventoryManager()
pricing_engine = RegionalPricingEngine()


@router.post("/transport/optimize-route")
async def optimize_transport_route(
    origin: str = Query(..., description="Origin location"),
    destination: str = Query(..., description="Destination location"),
    commodity: str = Query(..., description="Commodity type"),
    quantity: float = Query(..., description="Quantity to transport")
):
    """
    Optimize transportation route for commodity delivery
    """
    try:
        result = logistics_manager.optimize_transport_route(origin, destination, commodity, quantity)
        return result
        
    except Exception as e:
        logger.error(f"Error optimizing transport route: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/storage/plan-allocation")
async def plan_storage_allocation(
    commodity: str = Query(..., description="Commodity type"),
    quantity: float = Query(..., description="Quantity to store"),
    location: str = Query(..., description="Storage location"),
    duration: int = Query(..., description="Storage duration in days")
):
    """
    Plan storage allocation for commodity
    """
    try:
        result = inventory_manager.plan_storage_allocation(commodity, quantity, location, duration)
        return result
        
    except Exception as e:
        logger.error(f"Error planning storage allocation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/shipments/create")
async def create_shipment(shipment_data: Dict[str, Any]):
    """
    Create a new shipment
    """
    try:
        result = logistics_manager.create_shipment(shipment_data)
        return result
        
    except Exception as e:
        logger.error(f"Error creating shipment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/shipments/{shipment_id}/track")
async def track_shipment(shipment_id: str):
    """
    Track shipment status and location
    """
    try:
        result = logistics_manager.track_shipment(shipment_id)
        if not result:
            raise HTTPException(status_code=404, detail="Shipment not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking shipment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/supply-chain/optimize")
async def optimize_supply_chain(supply_chain_data: Dict[str, Any]):
    """
    Optimize entire supply chain network
    """
    try:
        result = logistics_manager.optimize_supply_chain(supply_chain_data)
        return result
        
    except Exception as e:
        logger.error(f"Error optimizing supply chain: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/carbon-footprint/calculate")
async def calculate_carbon_footprint(transport_data: Dict[str, Any]):
    """
    Calculate carbon footprint for transportation
    """
    try:
        result = logistics_manager.calculate_carbon_footprint(transport_data)
        return result
        
    except Exception as e:
        logger.error(f"Error calculating carbon footprint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/inventory/add")
async def add_inventory(
    commodity: str = Query(..., description="Commodity type"),
    quantity: float = Query(..., description="Quantity to add"),
    location: str = Query(..., description="Storage location"),
    quality_specs: Optional[Dict[str, Any]] = None
):
    """
    Add commodity to inventory
    """
    try:
        result = inventory_manager.add_inventory(commodity, quantity, location, quality_specs)
        return result
        
    except Exception as e:
        logger.error(f"Error adding inventory: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/inventory/reserve")
async def reserve_inventory(
    commodity: str = Query(..., description="Commodity type"),
    quantity: float = Query(..., description="Quantity to reserve"),
    location: str = Query(..., description="Storage location"),
    reservation_id: str = Query(..., description="Unique reservation identifier")
):
    """
    Reserve inventory for future use
    """
    try:
        result = inventory_manager.reserve_inventory(commodity, quantity, location, reservation_id)
        return result
        
    except Exception as e:
        logger.error(f"Error reserving inventory: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/inventory/release")
async def release_inventory(
    commodity: str = Query(..., description="Commodity type"),
    quantity: float = Query(..., description="Quantity to release"),
    location: str = Query(..., description="Storage location"),
    reservation_id: str = Query(..., description="Reservation identifier")
):
    """
    Release reserved inventory back to available
    """
    try:
        result = inventory_manager.release_inventory(commodity, quantity, location, reservation_id)
        return result
        
    except Exception as e:
        logger.error(f"Error releasing inventory: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/inventory/consume")
async def consume_inventory(
    commodity: str = Query(..., description="Commodity type"),
    quantity: float = Query(..., description="Quantity to consume"),
    location: str = Query(..., description="Storage location"),
    consumption_id: str = Query(..., description="Consumption identifier")
):
    """
    Consume inventory (remove from reserved)
    """
    try:
        result = inventory_manager.consume_inventory(commodity, quantity, location, consumption_id)
        return result
        
    except Exception as e:
        logger.error(f"Error consuming inventory: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/inventory/status")
async def get_inventory_status(
    commodity: Optional[str] = Query(None, description="Filter by commodity"),
    location: Optional[str] = Query(None, description="Filter by location")
):
    """
    Get current inventory status
    """
    try:
        result = inventory_manager.get_inventory_status(commodity, location)
        return result
        
    except Exception as e:
        logger.error(f"Error getting inventory status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/inventory/optimize-storage")
async def optimize_storage_allocation(
    commodities: List[str] = Query(..., description="List of commodities"),
    total_capacity: float = Query(..., description="Total storage capacity")
):
    """
    Optimize storage allocation across commodities
    """
    try:
        result = inventory_manager.optimize_storage_allocation(commodities, total_capacity)
        return result
        
    except Exception as e:
        logger.error(f"Error optimizing storage allocation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/inventory/costs/{inventory_key}")
async def calculate_inventory_costs(
    inventory_key: str,
    period_days: int = Query(30, description="Period for cost calculation in days")
):
    """
    Calculate inventory holding costs
    """
    try:
        result = inventory_manager.calculate_inventory_costs(inventory_key, period_days)
        return result
        
    except Exception as e:
        logger.error(f"Error calculating inventory costs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/inventory/transactions")
async def get_inventory_transactions(
    commodity: Optional[str] = Query(None, description="Filter by commodity"),
    location: Optional[str] = Query(None, description="Filter by location"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, description="Maximum number of transactions to return")
):
    """
    Get inventory transaction history
    """
    try:
        filters = {}
        if commodity:
            filters["commodity"] = commodity
        if location:
            filters["location"] = location
        if transaction_type:
            filters["type"] = transaction_type
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        
        result = inventory_manager.get_inventory_transactions(filters)
        return result[:limit]
        
    except Exception as e:
        logger.error(f"Error getting inventory transactions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/pricing/regional/{commodity}")
async def get_regional_price(
    commodity: str,
    region: str = Query(..., description="Target region"),
    quality: Optional[str] = Query(None, description="Quality specification"),
    delivery_date: Optional[str] = Query(None, description="Delivery date for forward pricing")
):
    """
    Calculate regional price for commodity
    """
    try:
        result = pricing_engine.calculate_regional_price(commodity, region, quality, delivery_date)
        return result
        
    except Exception as e:
        logger.error(f"Error calculating regional price: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/pricing/basis-differential")
async def get_basis_differential(
    commodity: str = Query(..., description="Commodity type"),
    origin_region: str = Query(..., description="Origin region"),
    destination_region: str = Query(..., description="Destination region")
):
    """
    Calculate basis differential between regions
    """
    try:
        result = pricing_engine.calculate_basis_differential(commodity, origin_region, destination_region)
        return result
        
    except Exception as e:
        logger.error(f"Error calculating basis differential: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/pricing/transport-cost")
async def get_transport_cost(
    origin: str = Query(..., description="Origin location"),
    destination: str = Query(..., description="Destination location"),
    commodity: str = Query(..., description="Commodity type"),
    quantity: float = Query(..., description="Quantity to transport")
):
    """
    Calculate transport cost between locations
    """
    try:
        result = pricing_engine.calculate_transport_cost(origin, destination, commodity, quantity)
        return result
        
    except Exception as e:
        logger.error(f"Error calculating transport cost: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/pricing/delivered-cost")
async def get_total_delivered_cost(
    commodity: str = Query(..., description="Commodity type"),
    origin_region: str = Query(..., description="Origin region"),
    destination_region: str = Query(..., description="Destination region"),
    quantity: float = Query(..., description="Quantity to deliver"),
    transport_mode: str = Query("pipeline", description="Preferred transport mode")
):
    """
    Calculate total delivered cost including transport
    """
    try:
        result = pricing_engine.calculate_total_delivered_cost(
            commodity, origin_region, destination_region, quantity, transport_mode
        )
        return result
        
    except Exception as e:
        logger.error(f"Error calculating delivered cost: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/pricing/market-summary/{commodity}")
async def get_market_summary(
    commodity: str,
    regions: Optional[List[str]] = Query(None, description="List of regions to include")
):
    """
    Get market summary for commodity across regions
    """
    try:
        result = pricing_engine.get_market_summary(commodity, regions)
        return result
        
    except Exception as e:
        logger.error(f"Error getting market summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
