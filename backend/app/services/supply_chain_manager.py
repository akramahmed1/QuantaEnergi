"""
Supply Chain Management Service for ETRM/CTRM Trading
Handles logistics, inventory tracking, delivery scheduling, and supply chain optimization
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from fastapi import HTTPException
import asyncio
import uuid
from enum import Enum

logger = logging.getLogger(__name__)

class SupplyChainStatus(Enum):
    """Supply chain status enumeration"""
    PLANNED = "planned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    CANCELLED = "cancelled"

class InventoryStatus(Enum):
    """Inventory status enumeration"""
    AVAILABLE = "available"
    RESERVED = "reserved"
    IN_TRANSIT = "in_transit"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"

class SupplyChainManager:
    """Service for managing supply chain operations and logistics"""
    
    def __init__(self):
        self.supply_chains = {}
        self.inventory_records = {}
        self.logistics_routes = {}
        self.delivery_schedules = {}
        self.supply_chain_counter = 1000
        
    async def create_supply_chain(
        self, 
        supply_chain_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new supply chain for commodity delivery
        
        Args:
            supply_chain_data: Supply chain configuration and requirements
            
        Returns:
            Dict with created supply chain details
        """
        try:
            # Validate required fields
            required_fields = ["commodity", "quantity", "source_location", "destination", "delivery_date"]
            for field in required_fields:
                if field not in supply_chain_data or not supply_chain_data[field]:
                    raise HTTPException(status_code=400, detail=f"Required field '{field}' is missing")
            
            # Generate unique supply chain ID
            supply_chain_id = str(uuid.uuid4())
            self.supply_chain_counter += 1
            
            # Create supply chain record
            supply_chain = {
                "supply_chain_id": supply_chain_id,
                "status": SupplyChainStatus.PLANNED.value,
                "created_at": datetime.now().isoformat(),
                "commodity": supply_chain_data["commodity"],
                "quantity": supply_chain_data["quantity"],
                "source_location": supply_chain_data["source_location"],
                "destination": supply_chain_data["destination"],
                "delivery_date": supply_chain_data["delivery_date"],
                "transport_mode": supply_chain_data.get("transport_mode", "pipeline"),
                "storage_requirements": supply_chain_data.get("storage_requirements", {}),
                "quality_specifications": supply_chain_data.get("quality_specifications", {}),
                "cost_estimates": self._calculate_cost_estimates(supply_chain_data),
                "risk_assessment": self._assess_supply_chain_risk(supply_chain_data),
                "logistics_route": self._plan_logistics_route(supply_chain_data),
                "inventory_allocation": self._allocate_inventory(supply_chain_data)
            }
            
            self.supply_chains[supply_chain_id] = supply_chain
            
            logger.info(f"Supply chain created successfully: {supply_chain_id}")
            
            return {
                "success": True,
                "supply_chain_id": supply_chain_id,
                "supply_chain": supply_chain
            }
            
        except Exception as e:
            logger.error(f"Supply chain creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _calculate_cost_estimates(self, supply_chain_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate cost estimates for supply chain"""
        
        quantity = supply_chain_data.get("quantity", 0)
        transport_mode = supply_chain_data.get("transport_mode", "pipeline")
        
        # Base cost per unit (simplified)
        base_costs = {
            "pipeline": 2.0,      # $2 per barrel
            "tanker": 5.0,        # $5 per barrel
            "rail": 8.0,          # $8 per barrel
            "truck": 12.0         # $12 per barrel
        }
        
        transport_cost = base_costs.get(transport_mode, 5.0) * quantity
        
        # Additional costs
        storage_cost = quantity * 0.5  # $0.5 per barrel storage
        insurance_cost = transport_cost * 0.02  # 2% insurance
        
        total_cost = transport_cost + storage_cost + insurance_cost
        
        return {
            "transport_cost": transport_cost,
            "storage_cost": storage_cost,
            "insurance_cost": insurance_cost,
            "total_cost": total_cost,
            "cost_per_unit": total_cost / quantity if quantity > 0 else 0
        }
    
    def _assess_supply_chain_risk(self, supply_chain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess supply chain risks"""
        
        risk_factors = []
        risk_score = 0
        
        # Distance risk
        source = supply_chain_data.get("source_location", "")
        destination = supply_chain_data.get("destination", "")
        
        if source and destination:
            # Simplified distance calculation
            distance_risk = 0.1  # Base risk
            if "international" in [source, destination]:
                distance_risk += 0.3
            risk_score += distance_risk
            risk_factors.append(f"Distance risk: {distance_risk:.2f}")
        
        # Transport mode risk
        transport_mode = supply_chain_data.get("transport_mode", "pipeline")
        transport_risks = {
            "pipeline": 0.1,
            "tanker": 0.3,
            "rail": 0.2,
            "truck": 0.4
        }
        transport_risk = transport_risks.get(transport_mode, 0.3)
        risk_score += transport_risk
        risk_factors.append(f"Transport risk: {transport_risk:.2f}")
        
        # Commodity risk
        commodity = supply_chain_data.get("commodity", "")
        if commodity in ["crude_oil", "natural_gas"]:
            commodity_risk = 0.2
        else:
            commodity_risk = 0.1
        risk_score += commodity_risk
        risk_factors.append(f"Commodity risk: {commodity_risk:.2f}")
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = "low"
        elif risk_score < 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "mitigation_strategies": self._generate_risk_mitigation_strategies(risk_score, risk_factors)
        }
    
    def _generate_risk_mitigation_strategies(self, risk_score: float, risk_factors: List[str]) -> List[str]:
        """Generate risk mitigation strategies"""
        
        strategies = []
        
        if risk_score > 0.5:
            strategies.append("Implement real-time tracking and monitoring")
            strategies.append("Establish backup transport routes")
            strategies.append("Increase insurance coverage")
        
        if "international" in str(risk_factors):
            strategies.append("Use established trade corridors")
            strategies.append("Implement customs compliance procedures")
        
        if "tanker" in str(risk_factors) or "truck" in str(risk_factors):
            strategies.append("Regular vehicle maintenance and inspection")
            strategies.append("Driver safety training and certification")
        
        if not strategies:
            strategies.append("Standard monitoring and control procedures")
        
        return strategies
    
    def _plan_logistics_route(self, supply_chain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Plan logistics route for supply chain"""
        
        source = supply_chain_data.get("source_location", "")
        destination = supply_chain_data.get("destination", "")
        transport_mode = supply_chain_data.get("transport_mode", "pipeline")
        
        # Simplified route planning
        route_id = f"ROUTE-{self.supply_chain_counter:06d}"
        
        route = {
            "route_id": route_id,
            "source": source,
            "destination": destination,
            "transport_mode": transport_mode,
            "estimated_distance": self._estimate_distance(source, destination),
            "estimated_duration": self._estimate_duration(source, destination, transport_mode),
            "waypoints": self._generate_waypoints(source, destination, transport_mode),
            "restrictions": self._get_route_restrictions(source, destination, transport_mode)
        }
        
        self.logistics_routes[route_id] = route
        
        return route
    
    def _estimate_distance(self, source: str, destination: str) -> float:
        """Estimate distance between source and destination"""
        
        # Simplified distance estimation
        if "international" in [source, destination]:
            return 5000.0  # 5000 km for international
        elif "regional" in [source, destination]:
            return 1000.0  # 1000 km for regional
        else:
            return 500.0   # 500 km for local
        
        return 1000.0  # Default
    
    def _estimate_duration(self, source: str, destination: str, transport_mode: str) -> int:
        """Estimate delivery duration in hours"""
        
        distance = self._estimate_distance(source, destination)
        
        # Speed in km/h for different transport modes
        speeds = {
            "pipeline": 50,    # 50 km/h average
            "tanker": 30,      # 30 km/h average
            "rail": 60,        # 60 km/h average
            "truck": 80        # 80 km/h average
        }
        
        speed = speeds.get(transport_mode, 50)
        duration = distance / speed
        
        # Add buffer time for loading/unloading
        buffer_time = 24  # 24 hours buffer
        
        return int(duration + buffer_time)
    
    def _generate_waypoints(self, source: str, destination: str, transport_mode: str) -> List[Dict[str, Any]]:
        """Generate waypoints for logistics route"""
        
        waypoints = []
        
        if transport_mode == "pipeline":
            # Pipeline waypoints
            waypoints = [
                {"location": source, "type": "source", "estimated_time": 0},
                {"location": "pump_station_1", "type": "pump", "estimated_time": 8},
                {"location": "pump_station_2", "type": "pump", "estimated_time": 16},
                {"location": destination, "type": "destination", "estimated_time": 24}
            ]
        elif transport_mode == "tanker":
            # Tanker waypoints
            waypoints = [
                {"location": source, "type": "loading_port", "estimated_time": 0},
                {"location": "transit_point", "type": "transit", "estimated_time": 12},
                {"location": destination, "type": "unloading_port", "estimated_time": 24}
            ]
        else:
            # Generic waypoints
            waypoints = [
                {"location": source, "type": "source", "estimated_time": 0},
                {"location": "transit_point", "type": "transit", "estimated_time": 12},
                {"location": destination, "type": "destination", "estimated_time": 24}
            ]
        
        return waypoints
    
    def _get_route_restrictions(self, source: str, destination: str, transport_mode: str) -> List[str]:
        """Get route restrictions and requirements"""
        
        restrictions = []
        
        if "international" in [source, destination]:
            restrictions.extend([
                "Customs documentation required",
                "Import/export permits needed",
                "International trade compliance"
            ])
        
        if transport_mode == "pipeline":
            restrictions.extend([
                "Pipeline capacity verification",
                "Pressure and flow rate limits",
                "Maintenance schedule coordination"
            ])
        elif transport_mode == "tanker":
            restrictions.extend([
                "Port scheduling and berth availability",
                "Weather and sea conditions",
                "Maritime safety regulations"
            ])
        
        return restrictions
    
    def _allocate_inventory(self, supply_chain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Allocate inventory for supply chain"""
        
        commodity = supply_chain_data.get("commodity", "")
        quantity = supply_chain_data.get("quantity", 0)
        
        # Check available inventory
        available_inventory = self._get_available_inventory(commodity)
        
        if available_inventory >= quantity:
            allocation_status = "fully_allocated"
            allocated_quantity = quantity
        else:
            allocation_status = "partially_allocated"
            allocated_quantity = available_inventory
        
        allocation = {
            "allocation_id": f"INV-ALLOC-{self.supply_chain_counter:06d}",
            "commodity": commodity,
            "requested_quantity": quantity,
            "allocated_quantity": allocated_quantity,
            "available_inventory": available_inventory,
            "allocation_status": allocation_status,
            "allocation_date": datetime.now().isoformat()
        }
        
        return allocation
    
    def _get_available_inventory(self, commodity: str) -> float:
        """Get available inventory for commodity"""
        
        # Simplified inventory check
        # In practice, this would query a real inventory database
        
        base_inventory = {
            "crude_oil": 100000,      # 100k barrels
            "natural_gas": 500000,    # 500k MMBtu
            "electricity": 1000,      # 1000 MWh
            "coal": 50000,            # 50k tons
            "renewables": 2000        # 2000 MWh
        }
        
        return base_inventory.get(commodity, 10000)
    
    async def update_supply_chain_status(
        self, 
        supply_chain_id: str, 
        status_update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update supply chain status and progress
        
        Args:
            supply_chain_id: Supply chain identifier
            status_update: Status update information
            
        Returns:
            Dict with updated supply chain details
        """
        try:
            if supply_chain_id not in self.supply_chains:
                raise HTTPException(status_code=404, detail="Supply chain not found")
            
            supply_chain = self.supply_chains[supply_chain_id]
            
            # Update status
            new_status = status_update.get("status")
            if new_status and new_status in [s.value for s in SupplyChainStatus]:
                supply_chain["status"] = new_status
            
            # Update progress
            progress = status_update.get("progress", {})
            if progress:
                supply_chain["progress"] = progress
                supply_chain["last_updated"] = datetime.now().isoformat()
            
            # Update location if provided
            current_location = status_update.get("current_location")
            if current_location:
                supply_chain["current_location"] = current_location
            
            # Update estimated arrival time
            eta = status_update.get("estimated_arrival")
            if eta:
                supply_chain["estimated_arrival"] = eta
            
            # Add status update to history
            if "status_history" not in supply_chain:
                supply_chain["status_history"] = []
            
            status_history_entry = {
                "timestamp": datetime.now().isoformat(),
                "status": new_status or supply_chain["status"],
                "location": current_location,
                "notes": status_update.get("notes", "")
            }
            
            supply_chain["status_history"].append(status_history_entry)
            
            logger.info(f"Supply chain status updated: {supply_chain_id} -> {new_status}")
            
            return {
                "success": True,
                "supply_chain": supply_chain
            }
            
        except Exception as e:
            logger.error(f"Supply chain status update failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def track_supply_chain(self, supply_chain_id: str) -> Dict[str, Any]:
        """
        Track supply chain progress and status
        
        Args:
            supply_chain_id: Supply chain identifier
            
        Returns:
            Dict with tracking information
        """
        try:
            if supply_chain_id not in self.supply_chains:
                raise HTTPException(status_code=404, detail="Supply chain not found")
            
            supply_chain = self.supply_chains[supply_chain_id]
            
            # Calculate progress percentage
            progress_percentage = self._calculate_progress_percentage(supply_chain)
            
            # Generate tracking summary
            tracking_info = {
                "supply_chain_id": supply_chain_id,
                "current_status": supply_chain["status"],
                "progress_percentage": progress_percentage,
                "current_location": supply_chain.get("current_location", supply_chain["source_location"]),
                "estimated_arrival": supply_chain.get("estimated_arrival"),
                "route_progress": self._get_route_progress(supply_chain),
                "status_history": supply_chain.get("status_history", []),
                "last_updated": supply_chain.get("last_updated", supply_chain["created_at"])
            }
            
            return {
                "success": True,
                "tracking_info": tracking_info
            }
            
        except Exception as e:
            logger.error(f"Supply chain tracking failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _calculate_progress_percentage(self, supply_chain: Dict[str, Any]) -> float:
        """Calculate progress percentage for supply chain"""
        
        status = supply_chain.get("status")
        
        if status == SupplyChainStatus.PLANNED.value:
            return 0.0
        elif status == SupplyChainStatus.IN_TRANSIT.value:
            return 50.0
        elif status == SupplyChainStatus.DELIVERED.value:
            return 100.0
        elif status == SupplyChainStatus.DELAYED.value:
            return 25.0
        elif status == SupplyChainStatus.CANCELLED.value:
            return 0.0
        else:
            return 0.0
    
    def _get_route_progress(self, supply_chain: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get route progress information"""
        
        route = supply_chain.get("logistics_route", {})
        waypoints = route.get("waypoints", [])
        current_location = supply_chain.get("current_location", supply_chain["source_location"])
        
        route_progress = []
        
        for waypoint in waypoints:
            waypoint_location = waypoint["location"]
            waypoint_type = waypoint["type"]
            
            if waypoint_location == current_location:
                status = "current"
            elif waypoint_location == supply_chain["source_location"]:
                status = "completed"
            elif waypoint_location == supply_chain["destination"]:
                if supply_chain["status"] == SupplyChainStatus.DELIVERED.value:
                    status = "completed"
                else:
                    status = "pending"
            else:
                status = "pending"
            
            route_progress.append({
                "location": waypoint_location,
                "type": waypoint_type,
                "status": status,
                "estimated_time": waypoint["estimated_time"]
            })
        
        return route_progress
    
    async def optimize_supply_chain(
        self, 
        supply_chain_id: str, 
        optimization_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize supply chain based on specified criteria
        
        Args:
            supply_chain_id: Supply chain identifier
            optimization_criteria: Optimization criteria and constraints
            
        Returns:
            Dict with optimization results
        """
        try:
            if supply_chain_id not in self.supply_chains:
                raise HTTPException(status_code=404, detail="Supply chain not found")
            
            supply_chain = self.supply_chains[supply_chain_id]
            
            # Run optimization algorithms
            optimization_result = self._run_supply_chain_optimization(
                supply_chain, optimization_criteria
            )
            
            # Store optimization result
            optimization_id = f"OPT-{self.supply_chain_counter:06d}"
            self.supply_chain_counter += 1
            
            result = {
                "optimization_id": optimization_id,
                "supply_chain_id": supply_chain_id,
                "optimization_criteria": optimization_criteria,
                "original_route": supply_chain["logistics_route"],
                "optimized_route": optimization_result["optimized_route"],
                "cost_savings": optimization_result["cost_savings"],
                "time_savings": optimization_result["time_savings"],
                "risk_improvement": optimization_result["risk_improvement"],
                "optimization_date": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "optimization_result": result
            }
            
        except Exception as e:
            logger.error(f"Supply chain optimization failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _run_supply_chain_optimization(
        self, 
        supply_chain: Dict[str, Any], 
        criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run supply chain optimization algorithms"""
        
        # Simplified optimization simulation
        # In practice, this would use sophisticated optimization algorithms
        
        original_route = supply_chain["logistics_route"]
        original_cost = supply_chain["cost_estimates"]["total_cost"]
        original_duration = original_route["estimated_duration"]
        
        # Simulate optimization improvements
        cost_reduction = 0.15  # 15% cost reduction
        time_reduction = 0.20  # 20% time reduction
        risk_reduction = 0.10  # 10% risk reduction
        
        optimized_cost = original_cost * (1 - cost_reduction)
        optimized_duration = original_duration * (1 - time_reduction)
        
        # Create optimized route
        optimized_route = original_route.copy()
        optimized_route["estimated_duration"] = optimized_duration
        optimized_route["waypoints"] = self._optimize_waypoints(original_route["waypoints"])
        
        return {
            "optimized_route": optimized_route,
            "cost_savings": original_cost - optimized_cost,
            "time_savings": original_duration - optimized_duration,
            "risk_improvement": risk_reduction
        }
    
    def _optimize_waypoints(self, waypoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize waypoints for better efficiency"""
        
        optimized_waypoints = []
        
        for i, waypoint in enumerate(waypoints):
            optimized_waypoint = waypoint.copy()
            
            # Reduce estimated time for intermediate waypoints
            if waypoint["type"] not in ["source", "destination"]:
                optimized_waypoint["estimated_time"] = int(waypoint["estimated_time"] * 0.8)
            
            optimized_waypoints.append(optimized_waypoint)
        
        return optimized_waypoints
    
    async def get_supply_chain_analytics(
        self, 
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get supply chain analytics and performance metrics
        
        Args:
            filters: Optional filters for analytics
            
        Returns:
            Dict with analytics data
        """
        try:
            # Aggregate supply chain data
            total_supply_chains = len(self.supply_chains)
            
            if total_supply_chains == 0:
                return {
                    "success": True,
                    "analytics": {
                        "total_supply_chains": 0,
                        "performance_metrics": {},
                        "status_distribution": {},
                        "cost_analysis": {}
                    }
                }
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics()
            
            # Calculate status distribution
            status_distribution = self._calculate_status_distribution()
            
            # Calculate cost analysis
            cost_analysis = self._calculate_cost_analysis()
            
            analytics = {
                "total_supply_chains": total_supply_chains,
                "performance_metrics": performance_metrics,
                "status_distribution": status_distribution,
                "cost_analysis": cost_analysis,
                "generated_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "analytics": analytics
            }
            
        except Exception as e:
            logger.error(f"Supply chain analytics failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate supply chain performance metrics"""
        
        total_delivered = sum(1 for sc in self.supply_chains.values() 
                            if sc["status"] == SupplyChainStatus.DELIVERED.value)
        
        total_planned = len(self.supply_chains)
        
        on_time_delivery_rate = total_delivered / total_planned if total_planned > 0 else 0
        
        # Calculate average delivery time
        delivery_times = []
        for sc in self.supply_chains.values():
            if sc["status"] == SupplyChainStatus.DELIVERED.value:
                created = datetime.fromisoformat(sc["created_at"])
                # Simulate delivery time
                delivery_time = 24  # 24 hours for simulation
                delivery_times.append(delivery_time)
        
        avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0
        
        return {
            "on_time_delivery_rate": on_time_delivery_rate,
            "average_delivery_time": avg_delivery_time,
            "total_delivered": total_delivered,
            "total_planned": total_planned
        }
    
    def _calculate_status_distribution(self) -> Dict[str, int]:
        """Calculate distribution of supply chain statuses"""
        
        status_counts = {}
        
        for sc in self.supply_chains.values():
            status = sc["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return status_counts
    
    def _calculate_cost_analysis(self) -> Dict[str, Any]:
        """Calculate cost analysis for supply chains"""
        
        total_cost = 0
        cost_by_commodity = {}
        
        for sc in self.supply_chains.values():
            cost = sc["cost_estimates"]["total_cost"]
            commodity = sc["commodity"]
            
            total_cost += cost
            cost_by_commodity[commodity] = cost_by_commodity.get(commodity, 0) + cost
        
        avg_cost = total_cost / len(self.supply_chains) if self.supply_chains else 0
        
        return {
            "total_cost": total_cost,
            "average_cost": avg_cost,
            "cost_by_commodity": cost_by_commodity
        }
