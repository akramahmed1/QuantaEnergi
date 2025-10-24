"""
Comprehensive Logistics Engine for QuantaEnergi ETRM/CTRM Platform
Implements full logistics and physical operations management including:
- Inventory management
- Shipping & transport management
- Batch ticketing
- Pipeline/grid interface
- Physical flow optimization
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

logger = logging.getLogger(__name__)

class LogisticsStatus(Enum):
    """Logistics status enumeration"""
    PLANNED = "planned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    DELAYED = "delayed"
    DAMAGED = "damaged"
    LOST = "lost"

class TransportMode(Enum):
    """Transportation modes"""
    PIPELINE = "pipeline"
    RAIL = "rail"
    TRUCK = "truck"
    SHIP = "ship"
    BARGES = "barges"
    AIR = "air"
    GRID = "grid"

class CommodityType(Enum):
    """Commodity types"""
    CRUDE_OIL = "crude_oil"
    NATURAL_GAS = "natural_gas"
    ELECTRICITY = "electricity"
    COAL = "coal"
    REFINED_PRODUCTS = "refined_products"
    LNG = "lng"
    LPG = "lpg"

@dataclass
class Location:
    """Physical location"""
    location_id: str
    name: str
    latitude: float
    longitude: float
    address: str
    country: str
    region: str
    location_type: str  # "terminal", "refinery", "power_plant", "storage", "port"
    capacity: Optional[float] = None
    current_inventory: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InventoryItem:
    """Inventory item"""
    item_id: str
    commodity_type: CommodityType
    quantity: float
    unit: str  # "bbl", "mmbtu", "mwh", "tonnes"
    location: Location
    quality_specs: Dict[str, Any] = field(default_factory=dict)
    batch_number: Optional[str] = None
    received_date: datetime = field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None
    status: str = "available"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TransportRoute:
    """Transport route between locations"""
    route_id: str
    origin: Location
    destination: Location
    transport_mode: TransportMode
    distance: float  # km
    estimated_duration: timedelta
    capacity: float
    cost_per_unit: float
    is_active: bool = True
    restrictions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Shipment:
    """Shipment tracking"""
    shipment_id: str
    commodity_type: CommodityType
    quantity: float
    unit: str
    origin: Location
    destination: Location
    transport_mode: TransportMode
    route: TransportRoute
    status: LogisticsStatus
    planned_departure: datetime
    actual_departure: Optional[datetime] = None
    planned_arrival: datetime
    actual_arrival: Optional[datetime] = None
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    batch_tickets: List[str] = field(default_factory=list)
    quality_certificates: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BatchTicket:
    """Batch ticket for commodity tracking"""
    ticket_id: str
    batch_number: str
    commodity_type: CommodityType
    quantity: float
    unit: str
    origin: Location
    destination: Location
    quality_specs: Dict[str, Any]
    created_date: datetime = field(default_factory=datetime.utcnow)
    status: str = "active"
    chain_of_custody: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PipelineSegment:
    """Pipeline segment"""
    segment_id: str
    name: str
    start_location: Location
    end_location: Location
    diameter: float  # inches
    length: float  # km
    capacity: float  # bbl/day
    current_flow: float = 0.0
    pressure: float = 0.0
    temperature: float = 0.0
    is_active: bool = True
    maintenance_schedule: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GridNode:
    """Electrical grid node"""
    node_id: str
    name: str
    location: Location
    voltage_level: float  # kV
    capacity: float  # MW
    current_load: float = 0.0
    is_active: bool = True
    grid_operator: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GridConnection:
    """Grid connection between nodes"""
    connection_id: str
    from_node: GridNode
    to_node: GridNode
    capacity: float  # MW
    current_flow: float = 0.0
    impedance: float = 0.0
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

class InventoryManager:
    """Inventory management system"""
    
    def __init__(self):
        self.inventory: Dict[str, InventoryItem] = {}
        self.locations: Dict[str, Location] = {}
        self.batch_tickets: Dict[str, BatchTicket] = {}
        
    def add_location(self, location: Location) -> bool:
        """Add a new location"""
        try:
            self.locations[location.location_id] = location
            logger.info(f"Added location: {location.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding location: {e}")
            return False
    
    def add_inventory_item(self, item: InventoryItem) -> bool:
        """Add inventory item"""
        try:
            self.inventory[item.item_id] = item
            logger.info(f"Added inventory item: {item.item_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding inventory item: {e}")
            return False
    
    def get_inventory_by_location(self, location_id: str) -> List[InventoryItem]:
        """Get inventory items by location"""
        try:
            return [item for item in self.inventory.values() if item.location.location_id == location_id]
        except Exception as e:
            logger.error(f"Error getting inventory by location: {e}")
            return []
    
    def get_inventory_by_commodity(self, commodity_type: CommodityType) -> List[InventoryItem]:
        """Get inventory items by commodity type"""
        try:
            return [item for item in self.inventory.values() if item.commodity_type == commodity_type]
        except Exception as e:
            logger.error(f"Error getting inventory by commodity: {e}")
            return []
    
    def update_inventory_quantity(self, item_id: str, quantity_change: float) -> bool:
        """Update inventory quantity"""
        try:
            if item_id in self.inventory:
                self.inventory[item_id].quantity += quantity_change
                if self.inventory[item_id].quantity < 0:
                    self.inventory[item_id].quantity = 0
                logger.info(f"Updated inventory quantity for {item_id}: {self.inventory[item_id].quantity}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating inventory quantity: {e}")
            return False
    
    def create_batch_ticket(self, batch_number: str, commodity_type: CommodityType, 
                           quantity: float, unit: str, origin: Location, 
                           destination: Location, quality_specs: Dict[str, Any]) -> str:
        """Create a batch ticket"""
        try:
            ticket_id = f"BATCH_{uuid.uuid4().hex[:8].upper()}"
            
            batch_ticket = BatchTicket(
                ticket_id=ticket_id,
                batch_number=batch_number,
                commodity_type=commodity_type,
                quantity=quantity,
                unit=unit,
                origin=origin,
                destination=destination,
                quality_specs=quality_specs
            )
            
            self.batch_tickets[ticket_id] = batch_ticket
            logger.info(f"Created batch ticket: {ticket_id}")
            return ticket_id
            
        except Exception as e:
            logger.error(f"Error creating batch ticket: {e}")
            return ""
    
    def get_inventory_summary(self) -> Dict[str, Any]:
        """Get inventory summary"""
        try:
            summary = {
                "total_items": len(self.inventory),
                "total_locations": len(self.locations),
                "inventory_by_commodity": {},
                "inventory_by_location": {},
                "total_batch_tickets": len(self.batch_tickets)
            }
            
            # Group by commodity type
            for item in self.inventory.values():
                commodity = item.commodity_type.value
                if commodity not in summary["inventory_by_commodity"]:
                    summary["inventory_by_commodity"][commodity] = 0
                summary["inventory_by_commodity"][commodity] += item.quantity
            
            # Group by location
            for item in self.inventory.values():
                location = item.location.name
                if location not in summary["inventory_by_location"]:
                    summary["inventory_by_location"][location] = 0
                summary["inventory_by_location"][location] += item.quantity
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting inventory summary: {e}")
            return {"error": str(e)}

class TransportManager:
    """Transport and shipping management system"""
    
    def __init__(self):
        self.shipments: Dict[str, Shipment] = {}
        self.routes: Dict[str, TransportRoute] = {}
        self.carriers: Dict[str, Dict[str, Any]] = {}
        
    def add_route(self, route: TransportRoute) -> bool:
        """Add a transport route"""
        try:
            self.routes[route.route_id] = route
            logger.info(f"Added route: {route.route_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding route: {e}")
            return False
    
    def create_shipment(self, commodity_type: CommodityType, quantity: float, unit: str,
                       origin: Location, destination: Location, transport_mode: TransportMode,
                       planned_departure: datetime, planned_arrival: datetime,
                       carrier: Optional[str] = None) -> str:
        """Create a new shipment"""
        try:
            shipment_id = f"SHIP_{uuid.uuid4().hex[:8].upper()}"
            
            # Find best route
            route = self._find_best_route(origin, destination, transport_mode)
            
            shipment = Shipment(
                shipment_id=shipment_id,
                commodity_type=commodity_type,
                quantity=quantity,
                unit=unit,
                origin=origin,
                destination=destination,
                transport_mode=transport_mode,
                route=route,
                status=LogisticsStatus.PLANNED,
                planned_departure=planned_departure,
                planned_arrival=planned_arrival,
                carrier=carrier
            )
            
            self.shipments[shipment_id] = shipment
            logger.info(f"Created shipment: {shipment_id}")
            return shipment_id
            
        except Exception as e:
            logger.error(f"Error creating shipment: {e}")
            return ""
    
    def _find_best_route(self, origin: Location, destination: Location, 
                        transport_mode: TransportMode) -> Optional[TransportRoute]:
        """Find the best route between locations"""
        try:
            best_route = None
            best_cost = float('inf')
            
            for route in self.routes.values():
                if (route.origin.location_id == origin.location_id and 
                    route.destination.location_id == destination.location_id and
                    route.transport_mode == transport_mode and
                    route.is_active):
                    
                    cost = route.cost_per_unit
                    if cost < best_cost:
                        best_cost = cost
                        best_route = route
            
            return best_route
            
        except Exception as e:
            logger.error(f"Error finding best route: {e}")
            return None
    
    def update_shipment_status(self, shipment_id: str, status: LogisticsStatus, 
                              actual_time: Optional[datetime] = None) -> bool:
        """Update shipment status"""
        try:
            if shipment_id not in self.shipments:
                return False
            
            shipment = self.shipments[shipment_id]
            shipment.status = status
            
            if status == LogisticsStatus.IN_TRANSIT and not shipment.actual_departure:
                shipment.actual_departure = actual_time or datetime.utcnow()
            elif status == LogisticsStatus.DELIVERED and not shipment.actual_arrival:
                shipment.actual_arrival = actual_time or datetime.utcnow()
            
            logger.info(f"Updated shipment {shipment_id} status to {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating shipment status: {e}")
            return False
    
    def track_shipment(self, shipment_id: str) -> Dict[str, Any]:
        """Track shipment status"""
        try:
            if shipment_id not in self.shipments:
                return {"error": "Shipment not found"}
            
            shipment = self.shipments[shipment_id]
            
            return {
                "shipment_id": shipment_id,
                "status": shipment.status.value,
                "commodity_type": shipment.commodity_type.value,
                "quantity": shipment.quantity,
                "unit": shipment.unit,
                "origin": shipment.origin.name,
                "destination": shipment.destination.name,
                "transport_mode": shipment.transport_mode.value,
                "planned_departure": shipment.planned_departure.isoformat(),
                "actual_departure": shipment.actual_departure.isoformat() if shipment.actual_departure else None,
                "planned_arrival": shipment.planned_arrival.isoformat(),
                "actual_arrival": shipment.actual_arrival.isoformat() if shipment.actual_arrival else None,
                "carrier": shipment.carrier,
                "tracking_number": shipment.tracking_number
            }
            
        except Exception as e:
            logger.error(f"Error tracking shipment: {e}")
            return {"error": str(e)}
    
    def get_shipment_summary(self) -> Dict[str, Any]:
        """Get shipment summary"""
        try:
            summary = {
                "total_shipments": len(self.shipments),
                "shipments_by_status": {},
                "shipments_by_mode": {},
                "total_routes": len(self.routes)
            }
            
            # Group by status
            for shipment in self.shipments.values():
                status = shipment.status.value
                if status not in summary["shipments_by_status"]:
                    summary["shipments_by_status"][status] = 0
                summary["shipments_by_status"][status] += 1
                
                # Group by transport mode
                mode = shipment.transport_mode.value
                if mode not in summary["shipments_by_mode"]:
                    summary["shipments_by_mode"][mode] = 0
                summary["shipments_by_mode"][mode] += 1
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting shipment summary: {e}")
            return {"error": str(e)}

class PipelineManager:
    """Pipeline management system"""
    
    def __init__(self):
        self.segments: Dict[str, PipelineSegment] = {}
        self.flow_optimizer = FlowOptimizer()
        
    def add_pipeline_segment(self, segment: PipelineSegment) -> bool:
        """Add a pipeline segment"""
        try:
            self.segments[segment.segment_id] = segment
            logger.info(f"Added pipeline segment: {segment.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding pipeline segment: {e}")
            return False
    
    def update_segment_flow(self, segment_id: str, flow: float, pressure: float, 
                           temperature: float) -> bool:
        """Update pipeline segment flow"""
        try:
            if segment_id not in self.segments:
                return False
            
            segment = self.segments[segment_id]
            segment.current_flow = flow
            segment.pressure = pressure
            segment.temperature = temperature
            
            logger.info(f"Updated segment {segment_id} flow: {flow}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating segment flow: {e}")
            return False
    
    def optimize_flow(self, origin: Location, destination: Location, 
                     required_flow: float) -> Dict[str, Any]:
        """Optimize pipeline flow"""
        try:
            # Find path between origin and destination
            path = self._find_pipeline_path(origin, destination)
            
            if not path:
                return {"error": "No pipeline path found"}
            
            # Optimize flow through path
            optimization_result = self.flow_optimizer.optimize_flow(path, required_flow)
            
            return {
                "path": [seg.segment_id for seg in path],
                "optimized_flow": optimization_result["flow"],
                "total_capacity": optimization_result["capacity"],
                "pressure_drop": optimization_result["pressure_drop"],
                "optimization_status": optimization_result["status"]
            }
            
        except Exception as e:
            logger.error(f"Error optimizing flow: {e}")
            return {"error": str(e)}
    
    def _find_pipeline_path(self, origin: Location, destination: Location) -> List[PipelineSegment]:
        """Find pipeline path between locations"""
        try:
            # Simplified path finding - in practice would use graph algorithms
            path = []
            
            for segment in self.segments.values():
                if (segment.start_location.location_id == origin.location_id and
                    segment.end_location.location_id == destination.location_id):
                    path.append(segment)
                    break
            
            return path
            
        except Exception as e:
            logger.error(f"Error finding pipeline path: {e}")
            return []
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get pipeline system status"""
        try:
            status = {
                "total_segments": len(self.segments),
                "active_segments": 0,
                "total_capacity": 0,
                "current_flow": 0,
                "segments_by_status": {}
            }
            
            for segment in self.segments.values():
                if segment.is_active:
                    status["active_segments"] += 1
                    status["total_capacity"] += segment.capacity
                    status["current_flow"] += segment.current_flow
                
                # Group by status
                segment_status = "active" if segment.is_active else "inactive"
                if segment_status not in status["segments_by_status"]:
                    status["segments_by_status"][segment_status] = 0
                status["segments_by_status"][segment_status] += 1
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting pipeline status: {e}")
            return {"error": str(e)}

class GridManager:
    """Electrical grid management system"""
    
    def __init__(self):
        self.nodes: Dict[str, GridNode] = {}
        self.connections: Dict[str, GridConnection] = {}
        self.grid_optimizer = GridOptimizer()
        
    def add_grid_node(self, node: GridNode) -> bool:
        """Add a grid node"""
        try:
            self.nodes[node.node_id] = node
            logger.info(f"Added grid node: {node.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding grid node: {e}")
            return False
    
    def add_grid_connection(self, connection: GridConnection) -> bool:
        """Add a grid connection"""
        try:
            self.connections[connection.connection_id] = connection
            logger.info(f"Added grid connection: {connection.connection_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding grid connection: {e}")
            return False
    
    def update_node_load(self, node_id: str, load: float) -> bool:
        """Update node load"""
        try:
            if node_id not in self.nodes:
                return False
            
            self.nodes[node_id].current_load = load
            logger.info(f"Updated node {node_id} load: {load}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating node load: {e}")
            return False
    
    def optimize_grid_flow(self, source_node: GridNode, sink_node: GridNode, 
                          required_power: float) -> Dict[str, Any]:
        """Optimize grid power flow"""
        try:
            # Find path between nodes
            path = self._find_grid_path(source_node, sink_node)
            
            if not path:
                return {"error": "No grid path found"}
            
            # Optimize power flow
            optimization_result = self.grid_optimizer.optimize_power_flow(path, required_power)
            
            return {
                "path": [conn.connection_id for conn in path],
                "optimized_power": optimization_result["power"],
                "total_capacity": optimization_result["capacity"],
                "power_loss": optimization_result["loss"],
                "optimization_status": optimization_result["status"]
            }
            
        except Exception as e:
            logger.error(f"Error optimizing grid flow: {e}")
            return {"error": str(e)}
    
    def _find_grid_path(self, source_node: GridNode, sink_node: GridNode) -> List[GridConnection]:
        """Find grid path between nodes"""
        try:
            # Simplified path finding
            path = []
            
            for connection in self.connections.values():
                if (connection.from_node.node_id == source_node.node_id and
                    connection.to_node.node_id == sink_node.node_id):
                    path.append(connection)
                    break
            
            return path
            
        except Exception as e:
            logger.error(f"Error finding grid path: {e}")
            return []
    
    def get_grid_status(self) -> Dict[str, Any]:
        """Get grid system status"""
        try:
            status = {
                "total_nodes": len(self.nodes),
                "active_nodes": 0,
                "total_connections": len(self.connections),
                "active_connections": 0,
                "total_capacity": 0,
                "current_load": 0
            }
            
            for node in self.nodes.values():
                if node.is_active:
                    status["active_nodes"] += 1
                    status["total_capacity"] += node.capacity
                    status["current_load"] += node.current_load
            
            for connection in self.connections.values():
                if connection.is_active:
                    status["active_connections"] += 1
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting grid status: {e}")
            return {"error": str(e)}

class FlowOptimizer:
    """Pipeline flow optimization"""
    
    def optimize_flow(self, path: List[PipelineSegment], required_flow: float) -> Dict[str, Any]:
        """Optimize flow through pipeline path"""
        try:
            # Calculate total capacity
            total_capacity = min(seg.capacity for seg in path)
            
            # Calculate optimized flow
            optimized_flow = min(required_flow, total_capacity)
            
            # Calculate pressure drop (simplified)
            pressure_drop = sum(seg.length * 0.1 for seg in path)  # 0.1 bar/km
            
            return {
                "flow": optimized_flow,
                "capacity": total_capacity,
                "pressure_drop": pressure_drop,
                "status": "optimized" if optimized_flow >= required_flow else "constrained"
            }
            
        except Exception as e:
            logger.error(f"Error optimizing flow: {e}")
            return {"error": str(e)}

class GridOptimizer:
    """Grid power flow optimization"""
    
    def optimize_power_flow(self, path: List[GridConnection], required_power: float) -> Dict[str, Any]:
        """Optimize power flow through grid path"""
        try:
            # Calculate total capacity
            total_capacity = min(conn.capacity for conn in path)
            
            # Calculate optimized power
            optimized_power = min(required_power, total_capacity)
            
            # Calculate power loss (simplified)
            power_loss = sum(conn.impedance * optimized_power**2 for conn in path)
            
            return {
                "power": optimized_power,
                "capacity": total_capacity,
                "loss": power_loss,
                "status": "optimized" if optimized_power >= required_power else "constrained"
            }
            
        except Exception as e:
            logger.error(f"Error optimizing power flow: {e}")
            return {"error": str(e)}

class LogisticsEngine:
    """Main logistics engine"""
    
    def __init__(self):
        self.inventory_manager = InventoryManager()
        self.transport_manager = TransportManager()
        self.pipeline_manager = PipelineManager()
        self.grid_manager = GridManager()
        self.optimization_engine = LogisticsOptimizationEngine()
        
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive logistics status"""
        try:
            return {
                "inventory": self.inventory_manager.get_inventory_summary(),
                "transport": self.transport_manager.get_shipment_summary(),
                "pipeline": self.pipeline_manager.get_pipeline_status(),
                "grid": self.grid_manager.get_grid_status(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive status: {e}")
            return {"error": str(e)}
    
    def optimize_logistics_network(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize entire logistics network"""
        try:
            return self.optimization_engine.optimize_network(
                self.inventory_manager,
                self.transport_manager,
                self.pipeline_manager,
                self.grid_manager,
                requirements
            )
            
        except Exception as e:
            logger.error(f"Error optimizing logistics network: {e}")
            return {"error": str(e)}

class LogisticsOptimizationEngine:
    """Logistics network optimization engine"""
    
    def optimize_network(self, inventory_manager: InventoryManager,
                        transport_manager: TransportManager,
                        pipeline_manager: PipelineManager,
                        grid_manager: GridManager,
                        requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize entire logistics network"""
        try:
            optimization_result = {
                "inventory_optimization": self._optimize_inventory(inventory_manager, requirements),
                "transport_optimization": self._optimize_transport(transport_manager, requirements),
                "pipeline_optimization": self._optimize_pipeline(pipeline_manager, requirements),
                "grid_optimization": self._optimize_grid(grid_manager, requirements),
                "overall_efficiency": 0.0,
                "cost_savings": 0.0,
                "recommendations": []
            }
            
            # Calculate overall efficiency
            optimization_result["overall_efficiency"] = self._calculate_overall_efficiency(optimization_result)
            
            # Calculate cost savings
            optimization_result["cost_savings"] = self._calculate_cost_savings(optimization_result)
            
            # Generate recommendations
            optimization_result["recommendations"] = self._generate_recommendations(optimization_result)
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error optimizing network: {e}")
            return {"error": str(e)}
    
    def _optimize_inventory(self, inventory_manager: InventoryManager, 
                           requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize inventory management"""
        try:
            # Get current inventory
            inventory_summary = inventory_manager.get_inventory_summary()
            
            # Calculate optimization metrics
            total_inventory = sum(inventory_summary.get("inventory_by_commodity", {}).values())
            target_inventory = requirements.get("target_inventory", total_inventory)
            
            efficiency = min(total_inventory / target_inventory, 1.0) if target_inventory > 0 else 1.0
            
            return {
                "current_inventory": total_inventory,
                "target_inventory": target_inventory,
                "efficiency": efficiency,
                "recommendations": ["Optimize inventory levels", "Implement just-in-time delivery"]
            }
            
        except Exception as e:
            logger.error(f"Error optimizing inventory: {e}")
            return {"error": str(e)}
    
    def _optimize_transport(self, transport_manager: TransportManager, 
                           requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize transport management"""
        try:
            # Get current transport status
            transport_summary = transport_manager.get_shipment_summary()
            
            # Calculate optimization metrics
            total_shipments = transport_summary.get("total_shipments", 0)
            active_shipments = transport_summary.get("shipments_by_status", {}).get("in_transit", 0)
            
            efficiency = active_shipments / total_shipments if total_shipments > 0 else 1.0
            
            return {
                "total_shipments": total_shipments,
                "active_shipments": active_shipments,
                "efficiency": efficiency,
                "recommendations": ["Optimize route selection", "Implement real-time tracking"]
            }
            
        except Exception as e:
            logger.error(f"Error optimizing transport: {e}")
            return {"error": str(e)}
    
    def _optimize_pipeline(self, pipeline_manager: PipelineManager, 
                          requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize pipeline management"""
        try:
            # Get current pipeline status
            pipeline_status = pipeline_manager.get_pipeline_status()
            
            # Calculate optimization metrics
            total_capacity = pipeline_status.get("total_capacity", 0)
            current_flow = pipeline_status.get("current_flow", 0)
            
            efficiency = current_flow / total_capacity if total_capacity > 0 else 1.0
            
            return {
                "total_capacity": total_capacity,
                "current_flow": current_flow,
                "efficiency": efficiency,
                "recommendations": ["Optimize flow rates", "Implement predictive maintenance"]
            }
            
        except Exception as e:
            logger.error(f"Error optimizing pipeline: {e}")
            return {"error": str(e)}
    
    def _optimize_grid(self, grid_manager: GridManager, 
                      requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize grid management"""
        try:
            # Get current grid status
            grid_status = grid_manager.get_grid_status()
            
            # Calculate optimization metrics
            total_capacity = grid_status.get("total_capacity", 0)
            current_load = grid_status.get("current_load", 0)
            
            efficiency = current_load / total_capacity if total_capacity > 0 else 1.0
            
            return {
                "total_capacity": total_capacity,
                "current_load": current_load,
                "efficiency": efficiency,
                "recommendations": ["Optimize power flow", "Implement smart grid technologies"]
            }
            
        except Exception as e:
            logger.error(f"Error optimizing grid: {e}")
            return {"error": str(e)}
    
    def _calculate_overall_efficiency(self, optimization_result: Dict[str, Any]) -> float:
        """Calculate overall efficiency"""
        try:
            efficiencies = []
            
            for key, value in optimization_result.items():
                if isinstance(value, dict) and "efficiency" in value:
                    efficiencies.append(value["efficiency"])
            
            return np.mean(efficiencies) if efficiencies else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating overall efficiency: {e}")
            return 0.0
    
    def _calculate_cost_savings(self, optimization_result: Dict[str, Any]) -> float:
        """Calculate cost savings"""
        try:
            # Simplified cost savings calculation
            overall_efficiency = optimization_result.get("overall_efficiency", 0.0)
            base_cost = 1000000  # Base cost assumption
            
            cost_savings = base_cost * (1 - overall_efficiency) * 0.1  # 10% of inefficiency
            
            return cost_savings
            
        except Exception as e:
            logger.error(f"Error calculating cost savings: {e}")
            return 0.0
    
    def _generate_recommendations(self, optimization_result: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations"""
        try:
            recommendations = []
            
            for key, value in optimization_result.items():
                if isinstance(value, dict) and "recommendations" in value:
                    recommendations.extend(value["recommendations"])
            
            # Remove duplicates
            return list(set(recommendations))
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

# Global logistics engine instance
logistics_engine = LogisticsEngine()

def get_logistics_status() -> Dict[str, Any]:
    """Get comprehensive logistics status"""
    return logistics_engine.get_comprehensive_status()

def optimize_logistics_network(requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Optimize entire logistics network"""
    return logistics_engine.optimize_logistics_network(requirements)

def create_shipment(commodity_type: CommodityType, quantity: float, unit: str,
                   origin: Location, destination: Location, transport_mode: TransportMode,
                   planned_departure: datetime, planned_arrival: datetime,
                   carrier: Optional[str] = None) -> str:
    """Create a new shipment"""
    return logistics_engine.transport_manager.create_shipment(
        commodity_type, quantity, unit, origin, destination, transport_mode,
        planned_departure, planned_arrival, carrier
    )

def track_shipment(shipment_id: str) -> Dict[str, Any]:
    """Track shipment status"""
    return logistics_engine.transport_manager.track_shipment(shipment_id)

def get_inventory_summary() -> Dict[str, Any]:
    """Get inventory summary"""
    return logistics_engine.inventory_manager.get_inventory_summary()

def get_pipeline_status() -> Dict[str, Any]:
    """Get pipeline system status"""
    return logistics_engine.pipeline_manager.get_pipeline_status()

def get_grid_status() -> Dict[str, Any]:
    """Get grid system status"""
    return logistics_engine.grid_manager.get_grid_status()
