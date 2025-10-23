"""
Inventory Manager Service for ETRM/CTRM Trading
Handles inventory tracking, storage optimization, and commodity management
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import math
import logging

logger = logging.getLogger(__name__)


class InventoryManager:
    """Service for managing commodity inventory and storage"""
    
    def __init__(self):
        self.inventories = {}  # In-memory storage for stubs
        self.storage_facilities = {}
        self.transactions = []
        self.transaction_counter = 1000
        
    def add_inventory(self, commodity: str, quantity: float, location: str, 
                      quality_specs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add commodity to inventory
        
        Args:
            commodity: Commodity type
            quantity: Quantity to add
            location: Storage location
            quality_specs: Quality specifications
            
        Returns:
            Dict with inventory update details
        """
        # TODO: Implement real inventory management with database
        inventory_key = f"{commodity}-{location}"
        
        if inventory_key not in self.inventories:
            self.inventories[inventory_key] = {
                "commodity": commodity,
                "location": location,
                "total_quantity": 0,
                "available_quantity": 0,
                "reserved_quantity": 0,
                "quality_specs": quality_specs or {},
                "last_updated": datetime.now().isoformat()
            }
        
        inventory = self.inventories[inventory_key]
        inventory["total_quantity"] += quantity
        inventory["available_quantity"] += quantity
        inventory["last_updated"] = datetime.now().isoformat()
        
        # Record transaction
        transaction_id = f"TXN-{self.transaction_counter:06d}"
        self.transaction_counter += 1
        
        transaction = {
            "transaction_id": transaction_id,
            "type": "add",
            "commodity": commodity,
            "quantity": quantity,
            "location": location,
            "timestamp": datetime.now().isoformat(),
            "quality_specs": quality_specs
        }
        
        self.transactions.append(transaction)
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "inventory_key": inventory_key,
            "new_total": inventory["total_quantity"],
            "new_available": inventory["available_quantity"]
        }
    
    def reserve_inventory(self, commodity: str, quantity: float, location: str, 
                         reservation_id: str) -> Dict[str, Any]:
        """
        Reserve inventory for future use
        
        Args:
            commodity: Commodity type
            quantity: Quantity to reserve
            location: Storage location
            reservation_id: Unique reservation identifier
            
        Returns:
            Dict with reservation details
        """
        # TODO: Implement real reservation system
        inventory_key = f"{commodity}-{location}"
        
        if inventory_key not in self.inventories:
            return {
                "success": False,
                "error": "Inventory not found"
            }
        
        inventory = self.inventories[inventory_key]
        
        if inventory["available_quantity"] < quantity:
            return {
                "success": False,
                "error": f"Insufficient available quantity. Available: {inventory['available_quantity']}, Requested: {quantity}"
            }
        
        # Update inventory
        inventory["available_quantity"] -= quantity
        inventory["reserved_quantity"] += quantity
        inventory["last_updated"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "reservation_id": reservation_id,
            "commodity": commodity,
            "quantity": quantity,
            "location": location,
            "available_after_reservation": inventory["available_quantity"]
        }
    
    def release_inventory(self, commodity: str, quantity: float, location: str, 
                         reservation_id: str) -> Dict[str, Any]:
        """
        Release reserved inventory back to available
        
        Args:
            commodity: Commodity type
            quantity: Quantity to release
            location: Storage location
            reservation_id: Reservation identifier
            
        Returns:
            Dict with release details
        """
        # TODO: Implement real reservation release
        inventory_key = f"{commodity}-{location}"
        
        if inventory_key not in self.inventories:
            return {
                "success": False,
                "error": "Inventory not found"
            }
        
        inventory = self.inventories[inventory_key]
        
        if inventory["reserved_quantity"] < quantity:
            return {
                "success": False,
                "error": f"Insufficient reserved quantity. Reserved: {inventory['reserved_quantity']}, Requested: {quantity}"
            }
        
        # Update inventory
        inventory["reserved_quantity"] -= quantity
        inventory["available_quantity"] += quantity
        inventory["last_updated"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "reservation_id": reservation_id,
            "commodity": commodity,
            "quantity": quantity,
            "location": location,
            "available_after_release": inventory["available_quantity"]
        }
    
    def consume_inventory(self, commodity: str, quantity: float, location: str, 
                         consumption_id: str) -> Dict[str, Any]:
        """
        Consume inventory (remove from reserved)
        
        Args:
            commodity: Commodity type
            quantity: Quantity to consume
            location: Storage location
            consumption_id: Consumption identifier
            
        Returns:
            Dict with consumption details
        """
        # TODO: Implement real consumption tracking
        inventory_key = f"{commodity}-{location}"
        
        if inventory_key not in self.inventories:
            return {
                "success": False,
                "error": "Inventory not found"
            }
        
        inventory = self.inventories[inventory_key]
        
        if inventory["reserved_quantity"] < quantity:
            return {
                "success": False,
                "error": f"Insufficient reserved quantity. Reserved: {inventory['reserved_quantity']}, Requested: {quantity}"
            }
        
        # Update inventory
        inventory["reserved_quantity"] -= quantity
        inventory["total_quantity"] -= quantity
        inventory["last_updated"] = datetime.now().isoformat()
        
        # Record transaction
        transaction_id = f"TXN-{self.transaction_counter:06d}"
        self.transaction_counter += 1
        
        transaction = {
            "transaction_id": transaction_id,
            "type": "consume",
            "commodity": commodity,
            "quantity": quantity,
            "location": location,
            "timestamp": datetime.now().isoformat(),
            "consumption_id": consumption_id
        }
        
        self.transactions.append(transaction)
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "consumption_id": consumption_id,
            "commodity": commodity,
            "quantity": quantity,
            "location": location,
            "remaining_total": inventory["total_quantity"]
        }
    
    def get_inventory_status(self, commodity: Optional[str] = None, 
                            location: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get current inventory status
        
        Args:
            commodity: Optional commodity filter
            location: Optional location filter
            
        Returns:
            List of inventory status records
        """
        # TODO: Implement real inventory reporting
        results = []
        
        for key, inventory in self.inventories.items():
            if commodity and inventory["commodity"] != commodity:
                continue
            if location and inventory["location"] != location:
                continue
            
            results.append({
                "inventory_key": key,
                "commodity": inventory["commodity"],
                "location": inventory["location"],
                "total_quantity": inventory["total_quantity"],
                "available_quantity": inventory["available_quantity"],
                "reserved_quantity": inventory["reserved_quantity"],
                "utilization_rate": (inventory["total_quantity"] - inventory["available_quantity"]) / inventory["total_quantity"] if inventory["total_quantity"] > 0 else 0,
                "last_updated": inventory["last_updated"]
            })
        
        return results
    
    def optimize_storage_allocation(self, commodities: List[str], 
                                   total_capacity: float) -> Dict[str, Any]:
        """
        Optimize storage allocation across commodities
        
        Args:
            commodities: List of commodities to optimize
            total_capacity: Total storage capacity
            
        Returns:
            Dict with optimization results
        """
        # TODO: Implement real storage optimization with linear programming
        # Stub optimization
        commodity_weights = {}
        total_demand = 0
        
        for commodity in commodities:
            # Calculate demand based on current inventory
            demand = 0
            for key, inventory in self.inventories.items():
                if inventory["commodity"] == commodity:
                    demand += inventory["total_quantity"]
            
            commodity_weights[commodity] = demand
            total_demand += demand
        
        # Allocate capacity proportionally
        allocations = {}
        if total_demand > 0:
            for commodity, demand in commodity_weights.items():
                allocations[commodity] = (demand / total_demand) * total_capacity
        else:
            # Equal allocation if no demand
            equal_share = total_capacity / len(commodities)
            allocations = {commodity: equal_share for commodity in commodities}
        
        return {
            "total_capacity": total_capacity,
            "commodities": commodities,
            "allocations": allocations,
            "optimization_method": "proportional_allocation_stub",
            "calculated_at": datetime.now().isoformat()
        }
    
    def calculate_inventory_costs(self, inventory_key: str, 
                                 period_days: int = 30) -> Dict[str, Any]:
        """
        Calculate inventory holding costs
        
        Args:
            inventory_key: Inventory identifier
            period_days: Period for cost calculation in days
            
        Returns:
            Dict with cost calculations
        """
        # TODO: Implement real cost calculation
        if inventory_key not in self.inventories:
            return {
                "success": False,
                "error": "Inventory not found"
            }
        
        inventory = self.inventories[inventory_key]
        
        # Stub cost factors
        storage_cost_per_unit_per_day = 0.01  # $0.01 per unit per day
        insurance_cost_rate = 0.001  # 0.1% per day
        opportunity_cost_rate = 0.0001  # 0.01% per day (interest rate)
        
        avg_quantity = (inventory["total_quantity"] + inventory["available_quantity"]) / 2
        period_fraction = period_days / 365
        
        storage_cost = avg_quantity * storage_cost_per_unit_per_day * period_days
        insurance_cost = avg_quantity * insurance_cost_rate * period_days
        opportunity_cost = avg_quantity * opportunity_cost_rate * period_days
        
        total_cost = storage_cost + insurance_cost + opportunity_cost
        
        return {
            "inventory_key": inventory_key,
            "period_days": period_days,
            "avg_quantity": avg_quantity,
            "costs": {
                "storage_cost": storage_cost,
                "insurance_cost": insurance_cost,
                "opportunity_cost": opportunity_cost,
                "total_cost": total_cost
            },
            "cost_per_unit_per_day": total_cost / (avg_quantity * period_days) if avg_quantity > 0 else 0,
            "calculation_method": "stub",
            "calculated_at": datetime.now().isoformat()
        }
    
    def get_inventory_transactions(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get inventory transaction history
        
        Args:
            filters: Optional filter criteria
            
        Returns:
            List of transactions
        """
        # TODO: Implement real transaction filtering
        transactions = self.transactions.copy()
        
        if filters:
            if "commodity" in filters:
                transactions = [t for t in transactions if t.get("commodity") == filters["commodity"]]
            if "location" in filters:
                transactions = [t for t in transactions if t.get("location") == filters["location"]]
            if "type" in filters:
                transactions = [t for t in transactions if t.get("type") == filters["type"]]
            if "start_date" in filters:
                start_date = datetime.fromisoformat(filters["start_date"])
                transactions = [t for t in transactions if datetime.fromisoformat(t["timestamp"]) >= start_date]
            if "end_date" in filters:
                end_date = datetime.fromisoformat(filters["end_date"])
                transactions = [t for t in transactions if datetime.fromisoformat(t["timestamp"]) <= end_date]
        
        # Sort by timestamp (newest first)
        transactions.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return transactions
