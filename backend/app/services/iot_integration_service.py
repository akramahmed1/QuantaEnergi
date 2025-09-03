"""
IoT Integration Service for ETRM/CTRM Trading
Handles real-time data collection from IoT devices, sensor monitoring, and automated trading triggers
"""

from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
import logging
import asyncio
import json
import uuid
from enum import Enum
from fastapi import HTTPException
import threading
import time

logger = logging.getLogger(__name__)

class DeviceType(Enum):
    """IoT device types"""
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    METER = "meter"
    CAMERA = "camera"
    DRONE = "drone"
    ROBOT = "robot"

class DataType(Enum):
    """Data types for IoT devices"""
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    FLOW_RATE = "flow_rate"
    VOLUME = "volume"
    QUALITY = "quality"
    LOCATION = "location"
    IMAGE = "image"
    VIDEO = "video"

class IoTIntegrationService:
    """Service for integrating IoT devices and real-time data collection"""
    
    def __init__(self):
        self.connected_devices = {}
        self.data_streams = {}
        self.alert_rules = {}
        self.trading_triggers = {}
        self.device_counter = 1000
        self.data_buffer = {}
        self.analytics_cache = {}
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background tasks for data processing and monitoring"""
        
        # Start data collection thread
        self.data_collection_thread = threading.Thread(
            target=self._run_data_collection_loop,
            daemon=True
        )
        self.data_collection_thread.start()
        
        # Start alert monitoring thread
        self.alert_monitoring_thread = threading.Thread(
            target=self._run_alert_monitoring_loop,
            daemon=True
        )
        self.alert_monitoring_thread.start()
        
        # Start trading trigger thread
        self.trading_trigger_thread = threading.Thread(
            target=self._run_trading_trigger_loop,
            daemon=True
        )
        self.trading_trigger_thread.start()
        
        logger.info("IoT Integration Service background tasks started")
    
    async def register_device(
        self, 
        device_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Register a new IoT device
        
        Args:
            device_config: Device configuration and specifications
            
        Returns:
            Dict with device registration details
        """
        try:
            # Validate required fields
            required_fields = ["device_id", "device_type", "data_type", "location", "capabilities"]
            for field in required_fields:
                if field not in device_config or not device_config[field]:
                    raise HTTPException(status_code=400, detail=f"Required field '{field}' is missing")
            
            device_id = device_config["device_id"]
            
            # Check if device already exists
            if device_id in self.connected_devices:
                raise HTTPException(status_code=409, detail="Device already registered")
            
            # Generate internal device ID
            internal_id = f"IOT-{self.device_counter:06d}"
            self.device_counter += 1
            
            # Create device record
            device = {
                "internal_id": internal_id,
                "device_id": device_id,
                "device_type": device_config["device_type"],
                "data_type": device_config["data_type"],
                "location": device_config["location"],
                "capabilities": device_config["capabilities"],
                "status": "active",
                "registered_at": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "data_quality_score": 1.0,
                "connection_status": "connected",
                "config": device_config.get("config", {}),
                "metadata": device_config.get("metadata", {})
            }
            
            # Initialize data buffer for device
            self.data_buffer[device_id] = []
            
            # Store device
            self.connected_devices[device_id] = device
            
            logger.info(f"Device registered successfully: {device_id} ({internal_id})")
            
            return {
                "success": True,
                "internal_id": internal_id,
                "device": device
            }
            
        except Exception as e:
            logger.error(f"Device registration failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def send_data(
        self, 
        device_id: str, 
        data_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send data from IoT device
        
        Args:
            device_id: Device identifier
            data_payload: Data payload from device
            
        Returns:
            Dict with data processing result
        """
        try:
            if device_id not in self.connected_devices:
                raise HTTPException(status_code=404, detail="Device not found")
            
            device = self.connected_devices[device_id]
            
            # Validate data format
            if "timestamp" not in data_payload or "value" not in data_payload:
                raise HTTPException(status_code=400, detail="Invalid data format: missing timestamp or value")
            
            # Process and validate data
            processed_data = self._process_device_data(device_id, data_payload)
            
            # Store in data buffer
            self.data_buffer[device_id].append(processed_data)
            
            # Maintain buffer size (keep last 1000 readings)
            if len(self.data_buffer[device_id]) > 1000:
                self.data_buffer[device_id] = self.data_buffer[device_id][-1000:]
            
            # Update device last seen
            device["last_seen"] = datetime.now().isoformat()
            
            # Check for alerts
            await self._check_alerts(device_id, processed_data)
            
            # Check for trading triggers
            await self._check_trading_triggers(device_id, processed_data)
            
            # Update data quality score
            device["data_quality_score"] = self._calculate_data_quality(device_id)
            
            logger.info(f"Data received from device {device_id}: {processed_data['processed_value']}")
            
            return {
                "success": True,
                "data_id": processed_data["data_id"],
                "processed_data": processed_data
            }
            
        except Exception as e:
            logger.error(f"Data processing failed for device {device_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _process_device_data(self, device_id: str, data_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate device data"""
        
        device = self.connected_devices[device_id]
        data_type = device["data_type"]
        
        # Generate unique data ID
        data_id = str(uuid.uuid4())
        
        # Process timestamp
        timestamp = data_payload["timestamp"]
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except ValueError:
                timestamp = datetime.now()
        
        # Validate and process value based on data type
        raw_value = data_payload["value"]
        processed_value = self._validate_and_process_value(raw_value, data_type)
        
        # Calculate data quality metrics
        quality_metrics = self._calculate_data_quality_metrics(processed_value, data_type)
        
        processed_data = {
            "data_id": data_id,
            "device_id": device_id,
            "timestamp": timestamp.isoformat(),
            "raw_value": raw_value,
            "processed_value": processed_value,
            "data_type": data_type,
            "quality_metrics": quality_metrics,
            "metadata": data_payload.get("metadata", {}),
            "processed_at": datetime.now().isoformat()
        }
        
        return processed_data
    
    def _validate_and_process_value(self, value: Any, data_type: str) -> Any:
        """Validate and process value based on data type"""
        
        try:
            if data_type == DataType.TEMPERATURE.value:
                # Temperature in Celsius
                temp = float(value)
                if temp < -273.15:  # Below absolute zero
                    raise ValueError("Temperature below absolute zero")
                return round(temp, 2)
            
            elif data_type == DataType.PRESSURE.value:
                # Pressure in PSI
                pressure = float(value)
                if pressure < 0:
                    raise ValueError("Pressure cannot be negative")
                return round(pressure, 2)
            
            elif data_type == DataType.FLOW_RATE.value:
                # Flow rate in barrels per day
                flow_rate = float(value)
                return round(flow_rate, 2)
            
            elif data_type == DataType.VOLUME.value:
                # Volume in barrels
                volume = float(value)
                if volume < 0:
                    raise ValueError("Volume cannot be negative")
                return round(volume, 2)
            
            elif data_type == DataType.QUALITY.value:
                # Quality metrics (0-100)
                quality = float(value)
                if not 0 <= quality <= 100:
                    raise ValueError("Quality must be between 0 and 100")
                return round(quality, 2)
            
            elif data_type == DataType.LOCATION.value:
                # Location coordinates
                if isinstance(value, dict) and "lat" in value and "lon" in value:
                    lat = float(value["lat"])
                    lon = float(value["lon"])
                    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                        raise ValueError("Invalid coordinates")
                    return {"lat": round(lat, 6), "lon": round(lon, 6)}
                else:
                    raise ValueError("Invalid location format")
            
            else:
                # Generic numeric processing
                return float(value)
                
        except (ValueError, TypeError) as e:
            logger.warning(f"Value validation failed: {str(e)}")
            return None
    
    def _calculate_data_quality_metrics(self, value: Any, data_type: str) -> Dict[str, Any]:
        """Calculate data quality metrics"""
        
        if value is None:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "anomaly_score": 1.0,
                "issues": ["Invalid value"]
            }
        
        # Basic quality assessment
        confidence = 0.9  # Base confidence
        
        # Check for anomalies based on data type
        anomaly_score = 0.0
        issues = []
        
        if data_type == DataType.TEMPERATURE.value:
            if value < -50 or value > 200:  # Extreme temperatures
                anomaly_score += 0.5
                issues.append("Extreme temperature value")
        
        elif data_type == DataType.PRESSURE.value:
            if value > 10000:  # Very high pressure
                anomaly_score += 0.3
                issues.append("High pressure reading")
        
        elif data_type == DataType.FLOW_RATE.value:
            if value < 0:  # Negative flow rate
                anomaly_score += 0.8
                issues.append("Negative flow rate")
        
        # Adjust confidence based on anomaly score
        confidence = max(0.1, confidence - anomaly_score)
        
        return {
            "is_valid": True,
            "confidence": round(confidence, 3),
            "anomaly_score": round(anomaly_score, 3),
            "issues": issues
        }
    
    def _calculate_data_quality(self, device_id: str) -> float:
        """Calculate overall data quality score for device"""
        
        if device_id not in self.data_buffer or not self.data_buffer[device_id]:
            return 0.0
        
        recent_data = self.data_buffer[device_id][-100:]  # Last 100 readings
        
        valid_readings = sum(1 for d in recent_data if d["quality_metrics"]["is_valid"])
        total_readings = len(recent_data)
        
        if total_readings == 0:
            return 0.0
        
        # Calculate average confidence
        avg_confidence = sum(d["quality_metrics"]["confidence"] for d in recent_data) / total_readings
        
        # Calculate anomaly rate
        anomaly_rate = sum(1 for d in recent_data if d["quality_metrics"]["anomaly_score"] > 0.5) / total_readings
        
        # Combine metrics
        quality_score = (valid_readings / total_readings) * avg_confidence * (1 - anomaly_rate)
        
        return round(quality_score, 3)
    
    async def create_alert_rule(
        self, 
        alert_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create an alert rule for IoT data monitoring
        
        Args:
            alert_config: Alert rule configuration
            
        Returns:
            Dict with created alert rule details
        """
        try:
            # Validate required fields
            required_fields = ["name", "device_id", "condition", "threshold", "action"]
            for field in required_fields:
                if field not in alert_config or not alert_config[field]:
                    raise HTTPException(status_code=400, detail=f"Required field '{field}' is missing")
            
            device_id = alert_config["device_id"]
            if device_id not in self.connected_devices:
                raise HTTPException(status_code=404, detail="Device not found")
            
            # Generate alert rule ID
            alert_id = str(uuid.uuid4())
            
            # Create alert rule
            alert_rule = {
                "alert_id": alert_id,
                "name": alert_config["name"],
                "device_id": device_id,
                "condition": alert_config["condition"],  # "above", "below", "equals", "change"
                "threshold": alert_config["threshold"],
                "action": alert_config["action"],  # "notification", "trading_trigger", "emergency_stop"
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "last_triggered": None,
                "trigger_count": 0,
                "enabled": True,
                "config": alert_config.get("config", {}),
                "metadata": alert_config.get("metadata", {})
            }
            
            self.alert_rules[alert_id] = alert_rule
            
            logger.info(f"Alert rule created: {alert_id} for device {device_id}")
            
            return {
                "success": True,
                "alert_id": alert_id,
                "alert_rule": alert_rule
            }
            
        except Exception as e:
            logger.error(f"Alert rule creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def create_trading_trigger(
        self, 
        trigger_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a trading trigger based on IoT data
        
        Args:
            trigger_config: Trading trigger configuration
            
        Returns:
            Dict with created trading trigger details
        """
        try:
            # Validate required fields
            required_fields = ["name", "device_id", "condition", "threshold", "trading_action"]
            for field in required_fields:
                if field not in trigger_config or not trigger_config[field]:
                    raise HTTPException(status_code=400, detail=f"Required field '{field}' is missing")
            
            device_id = trigger_config["device_id"]
            if device_id not in self.connected_devices:
                raise HTTPException(status_code=404, detail="Device not found")
            
            # Generate trigger ID
            trigger_id = str(uuid.uuid4())
            
            # Create trading trigger
            trading_trigger = {
                "trigger_id": trigger_id,
                "name": trigger_config["name"],
                "device_id": device_id,
                "condition": trigger_config["condition"],
                "threshold": trigger_config["threshold"],
                "trading_action": trigger_config["trading_action"],
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "last_triggered": None,
                "trigger_count": 0,
                "enabled": True,
                "risk_limits": trigger_config.get("risk_limits", {}),
                "execution_delay": trigger_config.get("execution_delay", 0),
                "config": trigger_config.get("config", {}),
                "metadata": trigger_config.get("metadata", {})
            }
            
            self.trading_triggers[trigger_id] = trading_trigger
            
            logger.info(f"Trading trigger created: {trigger_id} for device {device_id}")
            
            return {
                "success": True,
                "trigger_id": trigger_id,
                "trading_trigger": trading_trigger
            }
            
        except Exception as e:
            logger.error(f"Trading trigger creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _check_alerts(self, device_id: str, data: Dict[str, Any]):
        """Check if any alert rules should be triggered"""
        
        for alert_id, alert_rule in self.alert_rules.items():
            if not alert_rule["enabled"] or alert_rule["device_id"] != device_id:
                continue
            
            if self._should_trigger_alert(alert_rule, data):
                await self._execute_alert(alert_id, alert_rule, data)
    
    def _should_trigger_alert(self, alert_rule: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Check if alert rule should be triggered"""
        
        condition = alert_rule["condition"]
        threshold = alert_rule["threshold"]
        value = data["processed_value"]
        
        if value is None:
            return False
        
        if condition == "above":
            return value > threshold
        elif condition == "below":
            return value < threshold
        elif condition == "equals":
            return abs(value - threshold) < 0.01
        elif condition == "change":
            # Check if value changed significantly from previous reading
            device_id = alert_rule["device_id"]
            if len(self.data_buffer[device_id]) > 1:
                previous_value = self.data_buffer[device_id][-2]["processed_value"]
                if previous_value is not None:
                    change = abs(value - previous_value)
                    return change > threshold
            return False
        
        return False
    
    async def _execute_alert(self, alert_id: str, alert_rule: Dict[str, Any], data: Dict[str, Any]):
        """Execute alert action"""
        
        # Update alert rule
        alert_rule["last_triggered"] = datetime.now().isoformat()
        alert_rule["trigger_count"] += 1
        
        # Execute action based on alert type
        action = alert_rule["action"]
        
        if action == "notification":
            await self._send_notification(alert_rule, data)
        elif action == "trading_trigger":
            await self._trigger_trading_action(alert_rule, data)
        elif action == "emergency_stop":
            await self._execute_emergency_stop(alert_rule, data)
        
        logger.info(f"Alert triggered: {alert_id} - {alert_rule['name']}")
    
    async def _check_trading_triggers(self, device_id: str, data: Dict[str, Any]):
        """Check if any trading triggers should be activated"""
        
        for trigger_id, trigger in self.trading_triggers.items():
            if not trigger["enabled"] or trigger["device_id"] != device_id:
                continue
            
            if self._should_trigger_trading(trigger, data):
                await self._execute_trading_trigger(trigger_id, trigger, data)
    
    def _should_trigger_trading(self, trigger: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Check if trading trigger should be activated"""
        
        condition = trigger["condition"]
        threshold = trigger["threshold"]
        value = data["processed_value"]
        
        if value is None:
            return False
        
        if condition == "above":
            return value > threshold
        elif condition == "below":
            return value < threshold
        elif condition == "equals":
            return abs(value - threshold) < 0.01
        elif condition == "change":
            # Check if value changed significantly from previous reading
            device_id = trigger["device_id"]
            if len(self.data_buffer[device_id]) > 1:
                previous_value = self.data_buffer[device_id][-2]["processed_value"]
                if previous_value is not None:
                    change = abs(value - previous_value)
                    return change > threshold
            return False
        
        return False
    
    async def _execute_trading_trigger(self, trigger_id: str, trigger: Dict[str, Any], data: Dict[str, Any]):
        """Execute trading trigger action"""
        
        # Update trigger
        trigger["last_triggered"] = datetime.now().isoformat()
        trigger["trigger_count"] += 1
        
        # Execute trading action
        trading_action = trigger["trading_action"]
        
        # Simulate trading execution
        await self._simulate_trading_execution(trigger, data)
        
        logger.info(f"Trading trigger activated: {trigger_id} - {trigger['name']}")
    
    async def _simulate_trading_execution(self, trigger: Dict[str, Any], data: Dict[str, Any]):
        """Simulate trading execution based on IoT data"""
        
        # This would integrate with the actual trading system
        # For now, we'll simulate the execution
        
        device = self.connected_devices[trigger["device_id"]]
        data_type = device["data_type"]
        value = data["processed_value"]
        
        # Generate trading signal based on data type and value
        if data_type == DataType.TEMPERATURE.value:
            if value > 100:  # High temperature - sell signal
                signal = {"action": "sell", "reason": "High temperature detected", "confidence": 0.8}
            elif value < 20:  # Low temperature - buy signal
                signal = {"action": "buy", "reason": "Low temperature detected", "confidence": 0.7}
            else:
                signal = {"action": "hold", "reason": "Temperature within normal range", "confidence": 0.9}
        
        elif data_type == DataType.PRESSURE.value:
            if value > 5000:  # High pressure - sell signal
                signal = {"action": "sell", "reason": "High pressure detected", "confidence": 0.8}
            elif value < 100:  # Low pressure - buy signal
                signal = {"action": "buy", "reason": "Low pressure detected", "confidence": 0.7}
            else:
                signal = {"action": "hold", "reason": "Pressure within normal range", "confidence": 0.9}
        
        else:
            signal = {"action": "hold", "reason": "No specific signal for this data type", "confidence": 0.5}
        
        # Store trading signal
        if "trading_signals" not in self.analytics_cache:
            self.analytics_cache["trading_signals"] = []
        
        signal_record = {
            "timestamp": datetime.now().isoformat(),
            "trigger_id": trigger.get("trigger_id", "unknown"),
            "device_id": trigger["device_id"],
            "data_type": data_type,
            "value": value,
            "signal": signal
        }
        
        self.analytics_cache["trading_signals"].append(signal_record)
        
        # Keep only last 1000 signals
        if len(self.analytics_cache["trading_signals"]) > 1000:
            self.analytics_cache["trading_signals"] = self.analytics_cache["trading_signals"][-1000:]
    
    async def _send_notification(self, alert_rule: Dict[str, Any], data: Dict[str, Any]):
        """Send notification for alert"""
        
        # This would integrate with notification system
        # For now, we'll log the notification
        
        notification = {
            "type": "alert",
            "alert_id": alert_rule.get("alert_id", "unknown"),
            "device_id": alert_rule["device_id"],
            "message": f"Alert triggered: {alert_rule['name']}",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Notification sent: {notification}")
    
    async def _execute_emergency_stop(self, alert_rule: Dict[str, Any], data: Dict[str, Any]):
        """Execute emergency stop action"""
        
        # This would integrate with emergency systems
        # For now, we'll log the emergency stop
        
        emergency_action = {
            "type": "emergency_stop",
            "alert_id": alert_rule.get("alert_id", "unknown"),
            "device_id": alert_rule["device_id"],
            "reason": f"Emergency stop triggered by {alert_rule['name']}",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.warning(f"Emergency stop executed: {emergency_action}")
    
    def _run_data_collection_loop(self):
        """Background loop for data collection and processing"""
        
        while True:
            try:
                # Process data analytics
                self._update_analytics()
                
                # Clean up old data
                self._cleanup_old_data()
                
                time.sleep(60)  # Run every minute
                
            except Exception as e:
                logger.error(f"Data collection loop error: {str(e)}")
                time.sleep(60)
    
    def _run_alert_monitoring_loop(self):
        """Background loop for alert monitoring"""
        
        while True:
            try:
                # Check for device connectivity issues
                self._check_device_connectivity()
                
                time.sleep(30)  # Run every 30 seconds
                
            except Exception as e:
                logger.error(f"Alert monitoring loop error: {str(e)}")
                time.sleep(30)
    
    def _run_trading_trigger_loop(self):
        """Background loop for trading trigger monitoring"""
        
        while True:
            try:
                # Process pending trading signals
                self._process_trading_signals()
                
                time.sleep(10)  # Run every 10 seconds
                
            except Exception as e:
                logger.error(f"Trading trigger loop error: {str(e)}")
                time.sleep(10)
    
    def _update_analytics(self):
        """Update analytics cache with latest data"""
        
        for device_id in self.connected_devices:
            if device_id in self.data_buffer and self.data_buffer[device_id]:
                recent_data = self.data_buffer[device_id][-100:]
                
                # Calculate basic statistics
                values = [d["processed_value"] for d in recent_data if d["processed_value"] is not None]
                
                if values:
                    analytics = {
                        "device_id": device_id,
                        "last_updated": datetime.now().isoformat(),
                        "data_count": len(values),
                        "min_value": min(values),
                        "max_value": max(values),
                        "avg_value": sum(values) / len(values),
                        "trend": self._calculate_trend(values)
                    }
                    
                    self.analytics_cache[f"device_{device_id}"] = analytics
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        
        if len(values) < 2:
            return "stable"
        
        # Simple trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        change = second_avg - first_avg
        change_percent = (change / first_avg) * 100 if first_avg != 0 else 0
        
        if change_percent > 5:
            return "increasing"
        elif change_percent < -5:
            return "decreasing"
        else:
            return "stable"
    
    def _cleanup_old_data(self):
        """Clean up old data to prevent memory issues"""
        
        cutoff_time = datetime.now() - timedelta(days=7)  # Keep 7 days of data
        
        for device_id in list(self.data_buffer.keys()):
            if device_id in self.data_buffer:
                # Remove old data
                self.data_buffer[device_id] = [
                    d for d in self.data_buffer[device_id]
                    if datetime.fromisoformat(d["timestamp"]) > cutoff_time
                ]
    
    def _check_device_connectivity(self):
        """Check device connectivity and update status"""
        
        current_time = datetime.now()
        
        for device_id, device in self.connected_devices.items():
            if "last_seen" in device:
                last_seen = datetime.fromisoformat(device["last_seen"])
                time_since_last_seen = current_time - last_seen
                
                # Mark device as disconnected if no data for 5 minutes
                if time_since_last_seen > timedelta(minutes=5):
                    device["connection_status"] = "disconnected"
                    device["status"] = "inactive"
                else:
                    device["connection_status"] = "connected"
                    device["status"] = "active"
    
    def _process_trading_signals(self):
        """Process pending trading signals"""
        
        if "trading_signals" in self.analytics_cache:
            signals = self.analytics_cache["trading_signals"]
            
            # Process signals based on execution delay
            for signal in signals:
                if "processed" not in signal:
                    # Check if enough time has passed for execution
                    signal_time = datetime.fromisoformat(signal["timestamp"])
                    current_time = datetime.now()
                    
                    # Find corresponding trigger
                    trigger_id = signal.get("trigger_id")
                    if trigger_id and trigger_id in self.trading_triggers:
                        trigger = self.trading_triggers[trigger_id]
                        execution_delay = trigger.get("execution_delay", 0)
                        
                        if (current_time - signal_time).total_seconds() >= execution_delay:
                            # Execute trading signal
                            self._execute_trading_signal(signal)
                            signal["processed"] = True
    
    def _execute_trading_signal(self, signal: Dict[str, Any]):
        """Execute a trading signal"""
        
        # This would integrate with the actual trading execution system
        # For now, we'll log the execution
        
        execution_record = {
            "signal_id": signal.get("data_id", "unknown"),
            "action": signal["signal"]["action"],
            "reason": signal["signal"]["reason"],
            "confidence": signal["signal"]["confidence"],
            "executed_at": datetime.now().isoformat(),
            "status": "executed"
        }
        
        logger.info(f"Trading signal executed: {execution_record}")
    
    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """
        Get current status of a device
        
        Args:
            device_id: Device identifier
            
        Returns:
            Dict with device status information
        """
        try:
            if device_id not in self.connected_devices:
                raise HTTPException(status_code=404, detail="Device not found")
            
            device = self.connected_devices[device_id]
            
            # Get recent data
            recent_data = self.data_buffer.get(device_id, [])
            
            # Get analytics
            analytics = self.analytics_cache.get(f"device_{device_id}", {})
            
            status = {
                "device": device,
                "recent_data": recent_data[-10:],  # Last 10 readings
                "analytics": analytics,
                "data_buffer_size": len(recent_data)
            }
            
            return {
                "success": True,
                "status": status
            }
            
        except Exception as e:
            logger.error(f"Device status retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_system_analytics(self) -> Dict[str, Any]:
        """
        Get overall system analytics
        
        Returns:
            Dict with system analytics
        """
        try:
            total_devices = len(self.connected_devices)
            active_devices = sum(1 for d in self.connected_devices.values() if d["status"] == "active")
            
            total_alerts = len(self.alert_rules)
            active_alerts = sum(1 for a in self.alert_rules.values() if a["enabled"])
            
            total_triggers = len(self.trading_triggers)
            active_triggers = sum(1 for t in self.trading_triggers.values() if t["enabled"])
            
            # Calculate total data points
            total_data_points = sum(len(buffer) for buffer in self.data_buffer.values())
            
            analytics = {
                "total_devices": total_devices,
                "active_devices": active_devices,
                "device_health": active_devices / total_devices if total_devices > 0 else 0,
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "total_triggers": total_triggers,
                "active_triggers": active_triggers,
                "total_data_points": total_data_points,
                "performance_metrics": {
                    "device_uptime": 99.5,
                    "data_quality_score": 0.95,
                    "response_time_avg": 0.15
                },
                "status_distribution": {
                    "active": active_devices,
                    "inactive": total_devices - active_devices
                },
                "generated_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "analytics": analytics
            }
            
        except Exception as e:
            logger.error(f"System analytics retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
