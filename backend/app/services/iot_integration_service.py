"""
IoT Integration Service
Provides IoT device integration capabilities
"""

from typing import Dict, Any, List
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class DeviceType(Enum):
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    GATEWAY = "gateway"

class DataType(Enum):
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    FLOW = "flow"
    VOLTAGE = "voltage"

class IoTIntegrationService:
    """Service for IoT device integration"""
    
    def __init__(self):
        self.devices = {}
        self.sensor_data = {}
        logger.info("IoT integration service initialized")
    
    async def register_device(self, device_id: str, device_type: str, location: str) -> Dict[str, Any]:
        """Register an IoT device"""
        device = {
            "device_id": device_id,
            "type": device_type,
            "location": location,
            "status": "active",
            "registered_at": datetime.utcnow().isoformat()
        }
        
        self.devices[device_id] = device
        return device
    
    async def collect_sensor_data(self, device_id: str, sensor_type: str) -> Dict[str, Any]:
        """Collect data from IoT sensors"""
        data = {
            "device_id": device_id,
            "sensor_type": sensor_type,
            "value": 25.5,  # Mock sensor reading
            "unit": "celsius",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.sensor_data[f"{device_id}_{sensor_type}"] = data
        return data