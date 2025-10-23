"""
Physical Delivery Service for ETRM/CTRM Trading
Handles cargo/pipeline scheduling, delivery tracking, and MQTT integration
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import asyncio
import uuid
import json
from enum import Enum
from fastapi import HTTPException
import paho.mqtt.client as mqtt
import threading
import time

logger = logging.getLogger(__name__)

class DeliveryStatus(Enum):
    """Delivery status enumeration"""
    SCHEDULED = "scheduled"
    IN_TRANSIT = "in_transit"
    AT_DEPOT = "at_depot"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DeliveryType(Enum):
    """Delivery type enumeration"""
    PIPELINE = "pipeline"
    TANKER = "tanker"
    RAIL = "rail"
    TRUCK = "truck"
    BARGES = "barges"

class DeliveryService:
    """
    Service for managing physical delivery operations
    Includes MQTT integration for real-time tracking
    """
    
    def __init__(self):
        # Delivery storage
        self.deliveries = {}
        self.delivery_schedules = {}
        self.delivery_routes = {}
        self.delivery_counter = 1000
        
        # MQTT client for real-time tracking
        self.mqtt_client = None
        self.mqtt_connected = False
        self.mqtt_topics = [
            "delivery/status",
            "delivery/location",
            "delivery/alerts",
            "delivery/temperature",
            "delivery/pressure"
        ]
        
        # Delivery tracking data
        self.tracking_data = {}
        self.alert_history = []
        
        # Initialize MQTT client
        self._initialize_mqtt_client()
    
    def _initialize_mqtt_client(self):
        """Initialize MQTT client for real-time tracking"""
        try:
            self.mqtt_client = mqtt.Client(client_id=f"delivery_service_{uuid.uuid4().hex[:8]}")
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            self.mqtt_client.on_message = self._on_mqtt_message
            
            # Connect to MQTT broker (using localhost for demo)
            self.mqtt_client.connect("localhost", 1883, 60)
            self.mqtt_client.loop_start()
            
            logger.info("MQTT client initialized for delivery tracking")
            
        except Exception as e:
            logger.warning(f"MQTT client initialization failed: {e}. Running without real-time tracking.")
            self.mqtt_client = None
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.mqtt_connected = True
            logger.info("Connected to MQTT broker")
            
            # Subscribe to delivery tracking topics
            for topic in self.mqtt_topics:
                client.subscribe(topic)
                logger.info(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.mqtt_connected = False
        logger.warning("Disconnected from MQTT broker")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # Process delivery tracking data
            if topic == "delivery/status":
                self._process_status_update(payload)
            elif topic == "delivery/location":
                self._process_location_update(payload)
            elif topic == "delivery/alerts":
                self._process_alert(payload)
            elif topic in ["delivery/temperature", "delivery/pressure"]:
                self._process_sensor_data(topic, payload)
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def _process_status_update(self, payload: Dict[str, Any]):
        """Process delivery status update from MQTT"""
        delivery_id = payload.get("delivery_id")
        if delivery_id and delivery_id in self.deliveries:
            self.deliveries[delivery_id]["status"] = payload.get("status")
            self.deliveries[delivery_id]["last_updated"] = datetime.now().isoformat()
            
            # Store tracking data
            if delivery_id not in self.tracking_data:
                self.tracking_data[delivery_id] = []
            
            self.tracking_data[delivery_id].append({
                "timestamp": datetime.now().isoformat(),
                "type": "status_update",
                "data": payload
            })
            
            logger.info(f"Status update received for delivery {delivery_id}: {payload.get('status')}")
    
    def _process_location_update(self, payload: Dict[str, Any]):
        """Process location update from MQTT"""
        delivery_id = payload.get("delivery_id")
        if delivery_id and delivery_id in self.deliveries:
            location_data = {
                "latitude": payload.get("latitude"),
                "longitude": payload.get("longitude"),
                "address": payload.get("address"),
                "timestamp": datetime.now().isoformat()
            }
            
            self.deliveries[delivery_id]["current_location"] = location_data
            
            # Store tracking data
            if delivery_id not in self.tracking_data:
                self.tracking_data[delivery_id] = []
            
            self.tracking_data[delivery_id].append({
                "timestamp": datetime.now().isoformat(),
                "type": "location_update",
                "data": location_data
            })
            
            logger.info(f"Location update received for delivery {delivery_id}")
    
    def _process_alert(self, payload: Dict[str, Any]):
        """Process alert from MQTT"""
        delivery_id = payload.get("delivery_id")
        alert_data = {
            "delivery_id": delivery_id,
            "alert_type": payload.get("alert_type"),
            "severity": payload.get("severity", "medium"),
            "message": payload.get("message"),
            "timestamp": datetime.now().isoformat()
        }
        
        self.alert_history.append(alert_data)
        
        # Update delivery status if critical alert
        if payload.get("severity") == "critical" and delivery_id in self.deliveries:
            self.deliveries[delivery_id]["status"] = DeliveryStatus.FAILED.value
            self.deliveries[delivery_id]["alert_history"] = self.deliveries[delivery_id].get("alert_history", [])
            self.deliveries[delivery_id]["alert_history"].append(alert_data)
        
        logger.warning(f"Alert received for delivery {delivery_id}: {payload.get('message')}")
    
    def _process_sensor_data(self, topic: str, payload: Dict[str, Any]):
        """Process sensor data from MQTT"""
        delivery_id = payload.get("delivery_id")
        sensor_type = topic.split("/")[-1]  # temperature or pressure
        
        if delivery_id and delivery_id in self.deliveries:
            if "sensor_data" not in self.deliveries[delivery_id]:
                self.deliveries[delivery_id]["sensor_data"] = {}
            
            if sensor_type not in self.deliveries[delivery_id]["sensor_data"]:
                self.deliveries[delivery_id]["sensor_data"][sensor_type] = []
            
            sensor_reading = {
                "value": payload.get("value"),
                "unit": payload.get("unit"),
                "timestamp": datetime.now().isoformat()
            }
            
            self.deliveries[delivery_id]["sensor_data"][sensor_type].append(sensor_reading)
            
            # Keep only last 100 readings
            if len(self.deliveries[delivery_id]["sensor_data"][sensor_type]) > 100:
                self.deliveries[delivery_id]["sensor_data"][sensor_type] = \
                    self.deliveries[delivery_id]["sensor_data"][sensor_type][-100:]
    
    async def schedule_delivery(self, delivery_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule a new delivery
        
        Args:
            delivery_data: Delivery information including cargo, route, timing
            
        Returns:
            Dict with scheduled delivery details
        """
        try:
            # Validate required fields
            required_fields = ["commodity", "quantity", "origin", "destination", "delivery_date"]
            for field in required_fields:
                if field not in delivery_data or not delivery_data[field]:
                    raise HTTPException(status_code=400, detail=f"Required field '{field}' is missing")
            
            # Generate unique delivery ID
            delivery_id = str(uuid.uuid4())
            self.delivery_counter += 1
            
            # Determine delivery type based on commodity and route
            delivery_type = self._determine_delivery_type(
                delivery_data["commodity"], 
                delivery_data.get("origin", ""), 
                delivery_data.get("destination", "")
            )
            
            # Create delivery record
            delivery = {
                "delivery_id": delivery_id,
                "status": DeliveryStatus.SCHEDULED.value,
                "delivery_type": delivery_type.value,
                "commodity": delivery_data["commodity"],
                "quantity": delivery_data["quantity"],
                "unit": delivery_data.get("unit", "barrels"),
                "origin": delivery_data["origin"],
                "destination": delivery_data["destination"],
                "scheduled_date": delivery_data["delivery_date"],
                "estimated_arrival": self._calculate_estimated_arrival(
                    delivery_data["delivery_date"], delivery_type, 
                    delivery_data.get("origin", ""), delivery_data.get("destination", "")
                ),
                "delivery_route": self._plan_delivery_route(delivery_data),
                "transport_requirements": self._get_transport_requirements(
                    delivery_data["commodity"], delivery_type
                ),
                "special_instructions": delivery_data.get("special_instructions", []),
                "contact_info": delivery_data.get("contact_info", {}),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Store delivery
            self.deliveries[delivery_id] = delivery
            
            # Add to delivery schedule
            schedule_date = datetime.fromisoformat(delivery_data["delivery_date"].replace('Z', '+00:00'))
            if schedule_date.date() not in self.delivery_schedules:
                self.delivery_schedules[schedule_date.date()] = []
            self.delivery_schedules[schedule_date.date()].append(delivery_id)
            
            # Publish delivery scheduled event via MQTT
            if self.mqtt_connected:
                self._publish_mqtt_message("delivery/scheduled", {
                    "delivery_id": delivery_id,
                    "delivery_type": delivery_type.value,
                    "scheduled_date": delivery_data["delivery_date"]
                })
            
            logger.info(f"Delivery scheduled successfully: {delivery_id}")
            
            return {
                "success": True,
                "delivery_id": delivery_id,
                "delivery": delivery
            }
            
        except Exception as e:
            logger.error(f"Delivery scheduling failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def start_delivery(self, delivery_id: str, user_id: str) -> Dict[str, Any]:
        """
        Start a scheduled delivery
        
        Args:
            delivery_id: Delivery identifier
            user_id: User starting the delivery
            
        Returns:
            Dict with updated delivery details
        """
        try:
            if delivery_id not in self.deliveries:
                raise HTTPException(status_code=404, detail="Delivery not found")
            
            delivery = self.deliveries[delivery_id]
            
            if delivery["status"] != DeliveryStatus.SCHEDULED.value:
                raise HTTPException(status_code=400, detail="Delivery is not in scheduled status")
            
            # Update delivery status
            delivery["status"] = DeliveryStatus.IN_TRANSIT.value
            delivery["started_at"] = datetime.now().isoformat()
            delivery["started_by"] = user_id
            delivery["updated_at"] = datetime.now().isoformat()
            
            # Initialize tracking data
            self.tracking_data[delivery_id] = [{
                "timestamp": datetime.now().isoformat(),
                "type": "delivery_started",
                "data": {
                    "status": "in_transit",
                    "started_by": user_id,
                    "location": delivery["origin"]
                }
            }]
            
            # Publish delivery started event via MQTT
            if self.mqtt_connected:
                self._publish_mqtt_message("delivery/status", {
                    "delivery_id": delivery_id,
                    "status": "in_transit",
                    "started_by": user_id,
                    "timestamp": datetime.now().isoformat()
                })
            
            logger.info(f"Delivery started: {delivery_id}")
            
            return {
                "success": True,
                "delivery": delivery
            }
            
        except Exception as e:
            logger.error(f"Failed to start delivery {delivery_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_delivery_status(
        self, 
        delivery_id: str, 
        status_update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update delivery status and progress
        
        Args:
            delivery_id: Delivery identifier
            status_update: Status update information
            
        Returns:
            Dict with updated delivery details
        """
        try:
            if delivery_id not in self.deliveries:
                raise HTTPException(status_code=404, detail="Delivery not found")
            
            delivery = self.deliveries[delivery_id]
            
            # Update status
            new_status = status_update.get("status")
            if new_status and new_status in [s.value for s in DeliveryStatus]:
                delivery["status"] = new_status
            
            # Update location if provided
            if "location" in status_update:
                delivery["current_location"] = status_update["location"]
            
            # Update progress percentage
            if "progress_percentage" in status_update:
                delivery["progress_percentage"] = status_update["progress_percentage"]
            
            # Add notes if provided
            if "notes" in status_update:
                if "status_history" not in delivery:
                    delivery["status_history"] = []
                delivery["status_history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "status": new_status or delivery["status"],
                    "notes": status_update["notes"],
                    "updated_by": status_update.get("updated_by", "system")
                })
            
            delivery["updated_at"] = datetime.now().isoformat()
            
            # Store tracking data
            if delivery_id not in self.tracking_data:
                self.tracking_data[delivery_id] = []
            
            self.tracking_data[delivery_id].append({
                "timestamp": datetime.now().isoformat(),
                "type": "status_update",
                "data": status_update
            })
            
            # Publish status update via MQTT
            if self.mqtt_connected:
                self._publish_mqtt_message("delivery/status", {
                    "delivery_id": delivery_id,
                    "status": new_status or delivery["status"],
                    "progress_percentage": delivery.get("progress_percentage"),
                    "timestamp": datetime.now().isoformat()
                })
            
            logger.info(f"Delivery status updated: {delivery_id} -> {new_status}")
            
            return {
                "success": True,
                "delivery": delivery
            }
            
        except Exception as e:
            logger.error(f"Delivery status update failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def track_delivery(self, delivery_id: str) -> Dict[str, Any]:
        """
        Track delivery progress and current status
        
        Args:
            delivery_id: Delivery identifier
            
        Returns:
            Dict with tracking information
        """
        try:
            if delivery_id not in self.deliveries:
                raise HTTPException(status_code=404, detail="Delivery not found")
            
            delivery = self.deliveries[delivery_id]
            
            # Calculate progress percentage
            progress_percentage = self._calculate_delivery_progress(delivery)
            
            # Get tracking data
            tracking_history = self.tracking_data.get(delivery_id, [])
            
            # Get sensor data if available
            sensor_data = delivery.get("sensor_data", {})
            
            # Get alerts for this delivery
            delivery_alerts = [
                alert for alert in self.alert_history 
                if alert.get("delivery_id") == delivery_id
            ]
            
            tracking_info = {
                "delivery_id": delivery_id,
                "current_status": delivery["status"],
                "progress_percentage": progress_percentage,
                "current_location": delivery.get("current_location"),
                "estimated_arrival": delivery.get("estimated_arrival"),
                "delivery_type": delivery["delivery_type"],
                "commodity": delivery["commodity"],
                "quantity": delivery["quantity"],
                "origin": delivery["origin"],
                "destination": delivery["destination"],
                "tracking_history": tracking_history,
                "sensor_data": sensor_data,
                "alerts": delivery_alerts,
                "last_updated": delivery["updated_at"]
            }
            
            return {
                "success": True,
                "tracking_info": tracking_info
            }
            
        except Exception as e:
            logger.error(f"Delivery tracking failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def complete_delivery(
        self, 
        delivery_id: str, 
        completion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete a delivery
        
        Args:
            delivery_id: Delivery identifier
            completion_data: Completion information including delivery confirmation
            
        Returns:
            Dict with completed delivery details
        """
        try:
            if delivery_id not in self.deliveries:
                raise HTTPException(status_code=404, detail="Delivery not found")
            
            delivery = self.deliveries[delivery_id]
            
            # Update delivery status
            delivery["status"] = DeliveryStatus.DELIVERED.value
            delivery["completed_at"] = datetime.now().isoformat()
            delivery["delivery_confirmation"] = completion_data.get("delivery_confirmation", {})
            delivery["delivered_quantity"] = completion_data.get("delivered_quantity", delivery["quantity"])
            delivery["delivery_notes"] = completion_data.get("delivery_notes", "")
            delivery["delivered_by"] = completion_data.get("delivered_by", "")
            delivery["updated_at"] = datetime.now().isoformat()
            
            # Store tracking data
            if delivery_id not in self.tracking_data:
                self.tracking_data[delivery_id] = []
            
            self.tracking_data[delivery_id].append({
                "timestamp": datetime.now().isoformat(),
                "type": "delivery_completed",
                "data": completion_data
            })
            
            # Publish delivery completed event via MQTT
            if self.mqtt_connected:
                self._publish_mqtt_message("delivery/status", {
                    "delivery_id": delivery_id,
                    "status": "delivered",
                    "delivered_quantity": delivery["delivered_quantity"],
                    "timestamp": datetime.now().isoformat()
                })
            
            logger.info(f"Delivery completed: {delivery_id}")
            
            return {
                "success": True,
                "delivery": delivery
            }
            
        except Exception as e:
            logger.error(f"Delivery completion failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_delivery_schedule(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get delivery schedule for a specific date or today
        
        Args:
            date: Specific date to get schedule for (defaults to today)
            
        Returns:
            Dict with delivery schedule
        """
        try:
            if date is None:
                date = datetime.now()
            
            schedule_date = date.date()
            
            # Get scheduled deliveries for the date
            scheduled_deliveries = self.delivery_schedules.get(schedule_date, [])
            
            # Get delivery details
            delivery_details = []
            for delivery_id in scheduled_deliveries:
                if delivery_id in self.deliveries:
                    delivery_details.append(self.deliveries[delivery_id])
            
            # Sort by scheduled time
            delivery_details.sort(key=lambda x: x.get("scheduled_date", ""))
            
            return {
                "success": True,
                "schedule_date": schedule_date.isoformat(),
                "total_deliveries": len(delivery_details),
                "deliveries": delivery_details
            }
            
        except Exception as e:
            logger.error(f"Failed to get delivery schedule: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_delivery_analytics(self, date_from: Optional[datetime] = None, 
                                   date_to: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get delivery analytics and performance metrics
        
        Args:
            date_from: Start date for analytics (defaults to 30 days ago)
            date_to: End date for analytics (defaults to today)
            
        Returns:
            Dict with analytics data
        """
        try:
            if date_from is None:
                date_from = datetime.now() - timedelta(days=30)
            if date_to is None:
                date_to = datetime.now()
            
            # Filter deliveries by date range
            filtered_deliveries = []
            for delivery in self.deliveries.values():
                created_date = datetime.fromisoformat(delivery["created_at"].replace('Z', '+00:00'))
                if date_from <= created_date <= date_to:
                    filtered_deliveries.append(delivery)
            
            # Calculate analytics
            total_deliveries = len(filtered_deliveries)
            completed_deliveries = len([d for d in filtered_deliveries if d["status"] == DeliveryStatus.DELIVERED.value])
            failed_deliveries = len([d for d in filtered_deliveries if d["status"] == DeliveryStatus.FAILED.value])
            
            # Calculate on-time delivery rate
            on_time_deliveries = 0
            for delivery in filtered_deliveries:
                if delivery["status"] == DeliveryStatus.DELIVERED.value:
                    estimated_arrival = datetime.fromisoformat(delivery.get("estimated_arrival", "").replace('Z', '+00:00'))
                    completed_at = datetime.fromisoformat(delivery.get("completed_at", "").replace('Z', '+00:00'))
                    if completed_at <= estimated_arrival:
                        on_time_deliveries += 1
            
            on_time_rate = on_time_deliveries / completed_deliveries if completed_deliveries > 0 else 0
            
            # Calculate average delivery time
            delivery_times = []
            for delivery in filtered_deliveries:
                if delivery["status"] == DeliveryStatus.DELIVERED.value:
                    started_at = datetime.fromisoformat(delivery.get("started_at", "").replace('Z', '+00:00'))
                    completed_at = datetime.fromisoformat(delivery.get("completed_at", "").replace('Z', '+00:00'))
                    delivery_time = (completed_at - started_at).total_seconds() / 3600  # hours
                    delivery_times.append(delivery_time)
            
            avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0
            
            # Status distribution
            status_distribution = {}
            for delivery in filtered_deliveries:
                status = delivery["status"]
                status_distribution[status] = status_distribution.get(status, 0) + 1
            
            # Delivery type distribution
            type_distribution = {}
            for delivery in filtered_deliveries:
                delivery_type = delivery["delivery_type"]
                type_distribution[delivery_type] = type_distribution.get(delivery_type, 0) + 1
            
            analytics = {
                "period": {
                    "from": date_from.isoformat(),
                    "to": date_to.isoformat()
                },
                "total_deliveries": total_deliveries,
                "completed_deliveries": completed_deliveries,
                "failed_deliveries": failed_deliveries,
                "success_rate": completed_deliveries / total_deliveries if total_deliveries > 0 else 0,
                "on_time_delivery_rate": on_time_rate,
                "average_delivery_time_hours": avg_delivery_time,
                "status_distribution": status_distribution,
                "delivery_type_distribution": type_distribution,
                "generated_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "analytics": analytics
            }
            
        except Exception as e:
            logger.error(f"Delivery analytics failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== HELPER METHODS ====================
    
    def _determine_delivery_type(self, commodity: str, origin: str, destination: str) -> DeliveryType:
        """Determine optimal delivery type based on commodity and route"""
        
        # Oil and gas commodities
        if commodity in ["crude_oil", "natural_gas", "lng", "refined_products"]:
            if "pipeline" in origin.lower() or "pipeline" in destination.lower():
                return DeliveryType.PIPELINE
            elif "port" in origin.lower() or "port" in destination.lower():
                return DeliveryType.TANKER
            else:
                return DeliveryType.TRUCK
        
        # Bulk commodities
        elif commodity in ["coal", "iron_ore", "grain"]:
            return DeliveryType.RAIL
        
        # General commodities
        else:
            return DeliveryType.TRUCK
    
    def _calculate_estimated_arrival(
        self, 
        scheduled_date: str, 
        delivery_type: DeliveryType, 
        origin: str, 
        destination: str
    ) -> str:
        """Calculate estimated arrival time based on delivery type and route"""
        
        # Base delivery times by type (in hours)
        delivery_times = {
            DeliveryType.PIPELINE: 24,      # 1 day
            DeliveryType.TANKER: 168,       # 7 days
            DeliveryType.RAIL: 72,          # 3 days
            DeliveryType.TRUCK: 48,         # 2 days
            DeliveryType.BARGES: 96         # 4 days
        }
        
        base_time = delivery_times.get(delivery_type, 48)
        
        # Add distance factor
        if "international" in [origin.lower(), destination.lower()]:
            base_time *= 2
        
        # Calculate estimated arrival
        scheduled_dt = datetime.fromisoformat(scheduled_date.replace('Z', '+00:00'))
        estimated_arrival = scheduled_dt + timedelta(hours=base_time)
        
        return estimated_arrival.isoformat()
    
    def _plan_delivery_route(self, delivery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Plan delivery route with waypoints"""
        
        origin = delivery_data.get("origin", "")
        destination = delivery_data.get("destination", "")
        delivery_type = self._determine_delivery_type(
            delivery_data["commodity"], origin, destination
        )
        
        # Generate route waypoints based on delivery type
        waypoints = []
        
        if delivery_type == DeliveryType.PIPELINE:
            waypoints = [
                {"location": origin, "type": "source", "estimated_time": 0},
                {"location": "pump_station_1", "type": "pump", "estimated_time": 8},
                {"location": "pump_station_2", "type": "pump", "estimated_time": 16},
                {"location": destination, "type": "destination", "estimated_time": 24}
            ]
        elif delivery_type == DeliveryType.TANKER:
            waypoints = [
                {"location": origin, "type": "loading_port", "estimated_time": 0},
                {"location": "transit_point", "type": "transit", "estimated_time": 84},
                {"location": destination, "type": "unloading_port", "estimated_time": 168}
            ]
        else:
            waypoints = [
                {"location": origin, "type": "source", "estimated_time": 0},
                {"location": "transit_hub", "type": "transit", "estimated_time": 24},
                {"location": destination, "type": "destination", "estimated_time": 48}
            ]
        
        return {
            "route_id": f"ROUTE-{self.delivery_counter:06d}",
            "delivery_type": delivery_type.value,
            "origin": origin,
            "destination": destination,
            "waypoints": waypoints,
            "total_distance_km": self._estimate_distance(origin, destination),
            "estimated_duration_hours": waypoints[-1]["estimated_time"]
        }
    
    def _estimate_distance(self, origin: str, destination: str) -> float:
        """Estimate distance between origin and destination"""
        
        if "international" in [origin.lower(), destination.lower()]:
            return 5000.0  # 5000 km for international
        elif "regional" in [origin.lower(), destination.lower()]:
            return 1000.0  # 1000 km for regional
        else:
            return 500.0   # 500 km for local
    
    def _get_transport_requirements(self, commodity: str, delivery_type: DeliveryType) -> Dict[str, Any]:
        """Get transport requirements for commodity and delivery type"""
        
        requirements = {
            "temperature_controlled": False,
            "pressure_controlled": False,
            "special_handling": [],
            "documentation_required": [],
            "safety_requirements": []
        }
        
        # Commodity-specific requirements
        if commodity in ["lng", "lpg"]:
            requirements["temperature_controlled"] = True
            requirements["pressure_controlled"] = True
            requirements["special_handling"].append("cryogenic_handling")
            requirements["safety_requirements"].append("hazmat_certification")
        
        elif commodity == "crude_oil":
            requirements["special_handling"].append("oil_spill_protection")
            requirements["safety_requirements"].append("fire_safety")
        
        elif commodity == "natural_gas":
            requirements["pressure_controlled"] = True
            requirements["safety_requirements"].append("gas_leak_detection")
        
        # Delivery type specific requirements
        if delivery_type == DeliveryType.TANKER:
            requirements["documentation_required"].extend([
                "bill_of_lading",
                "maritime_insurance",
                "port_clearance"
            ])
        elif delivery_type == DeliveryType.RAIL:
            requirements["documentation_required"].extend([
                "railway_bill",
                "freight_manifest"
            ])
        
        return requirements
    
    def _calculate_delivery_progress(self, delivery: Dict[str, Any]) -> float:
        """Calculate delivery progress percentage"""
        
        status = delivery.get("status")
        
        progress_map = {
            DeliveryStatus.SCHEDULED.value: 0.0,
            DeliveryStatus.IN_TRANSIT.value: 25.0,
            DeliveryStatus.AT_DEPOT.value: 50.0,
            DeliveryStatus.OUT_FOR_DELIVERY.value: 75.0,
            DeliveryStatus.DELIVERED.value: 100.0,
            DeliveryStatus.FAILED.value: 0.0,
            DeliveryStatus.CANCELLED.value: 0.0
        }
        
        return progress_map.get(status, 0.0)
    
    def _publish_mqtt_message(self, topic: str, payload: Dict[str, Any]):
        """Publish message to MQTT broker"""
        try:
            if self.mqtt_client and self.mqtt_connected:
                message = json.dumps(payload)
                self.mqtt_client.publish(topic, message)
                logger.debug(f"Published MQTT message to {topic}: {payload}")
        except Exception as e:
            logger.error(f"Failed to publish MQTT message: {e}")


# Global service instance
delivery_service = DeliveryService()
