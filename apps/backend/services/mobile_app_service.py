"""
Mobile Application Service for ETRM/CTRM Trading
Handles mobile-specific functionality, push notifications, offline sync, and mobile-optimized APIs
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import asyncio
import json
import uuid
from enum import Enum
from fastapi import HTTPException
import hashlib
import base64

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Push notification types"""
    TRADE_ALERT = "trade_alert"
    PRICE_ALERT = "price_alert"
    RISK_ALERT = "risk_alert"
    COMPLIANCE_ALERT = "compliance_alert"
    SYSTEM_ALERT = "system_alert"
    NEWS_UPDATE = "news_update"

class SyncStatus(Enum):
    """Data synchronization status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"

class MobileAppService:
    """Service for mobile application functionality and optimization"""
    
    def __init__(self):
        self.registered_devices = {}
        self.push_tokens = {}
        self.notification_queue = []
        self.sync_sessions = {}
        self.offline_data_cache = {}
        self.device_counter = 1000
        
        # Mobile-specific configurations
        self.mobile_configs = {
            "max_offline_days": 7,
            "max_cache_size_mb": 100,
            "sync_batch_size": 50,
            "notification_retry_attempts": 3,
            "offline_data_ttl_hours": 168  # 7 days
        }
    
    async def register_mobile_device(
        self, 
        device_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Register a mobile device for push notifications and mobile services
        
        Args:
            device_info: Mobile device information
            
        Returns:
            Dict with device registration details
        """
        try:
            # Validate required fields
            required_fields = ["device_id", "platform", "app_version", "device_model"]
            for field in required_fields:
                if field not in device_info or not device_info[field]:
                    raise HTTPException(status_code=400, detail=f"Required field '{field}' is missing")
            
            device_id = device_info["device_id"]
            
            # Check if device already exists
            if device_id in self.registered_devices:
                # Update existing device
                device = self.registered_devices[device_id]
                device.update({
                    "last_updated": datetime.now().isoformat(),
                    "app_version": device_info["app_version"],
                    "device_model": device_info["device_model"],
                    "platform": device_info["platform"]
                })
            else:
                # Create new device record
                internal_id = f"MOBILE-{self.device_counter:06d}"
                self.device_counter += 1
                
                device = {
                    "internal_id": internal_id,
                    "device_id": device_id,
                    "platform": device_info["platform"],
                    "app_version": device_info["app_version"],
                    "device_model": device_info["device_model"],
                    "os_version": device_info.get("os_version", ""),
                    "screen_resolution": device_info.get("screen_resolution", ""),
                    "timezone": device_info.get("timezone", "UTC"),
                    "language": device_info.get("language", "en"),
                    "status": "active",
                    "registered_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "last_active": datetime.now().isoformat(),
                    "push_enabled": device_info.get("push_enabled", True),
                    "offline_sync_enabled": device_info.get("offline_sync_enabled", True),
                    "metadata": device_info.get("metadata", {})
                }
                
                self.registered_devices[device_id] = device
                
                # Initialize offline data cache
                self.offline_data_cache[device_id] = {
                    "trades": [],
                    "positions": [],
                    "market_data": [],
                    "notifications": [],
                    "last_sync": None,
                    "cache_size_mb": 0
                }
            
            logger.info(f"Mobile device registered/updated: {device_id}")
            
            return {
                "success": True,
                "device": device
            }
            
        except Exception as e:
            logger.error(f"Mobile device registration failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def register_push_token(
        self, 
        device_id: str, 
        push_token: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Register push notification token for a device
        
        Args:
            device_id: Device identifier
            push_token: Push notification token
            platform: Platform (ios, android, web)
            
        Returns:
            Dict with registration result
        """
        try:
            if device_id not in self.registered_devices:
                raise HTTPException(status_code=404, detail="Device not found")
            
            # Store push token
            token_id = str(uuid.uuid4())
            
            self.push_tokens[device_id] = {
                "token_id": token_id,
                "push_token": push_token,
                "platform": platform,
                "registered_at": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat(),
                "status": "active"
            }
            
            # Update device
            device = self.registered_devices[device_id]
            device["push_enabled"] = True
            device["last_updated"] = datetime.now().isoformat()
            
            logger.info(f"Push token registered for device: {device_id}")
            
            return {
                "success": True,
                "token_id": token_id
            }
            
        except Exception as e:
            logger.error(f"Push token registration failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def send_push_notification(
        self, 
        device_ids: List[str],
        notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send push notification to mobile devices
        
        Args:
            device_ids: List of device identifiers
            notification_data: Notification content and configuration
            
        Returns:
            Dict with notification sending results
        """
        try:
            # Validate notification data
            required_fields = ["title", "body", "type"]
            for field in required_fields:
                if field not in notification_data or not notification_data[field]:
                    raise HTTPException(status_code=400, detail=f"Required field '{field}' is missing")
            
            notification_type = notification_data["type"]
            if notification_type not in [t.value for t in NotificationType]:
                raise HTTPException(status_code=400, detail=f"Invalid notification type: {notification_type}")
            
            # Generate notification ID
            notification_id = str(uuid.uuid4())
            
            # Create notification record
            notification = {
                "notification_id": notification_id,
                "title": notification_data["title"],
                "body": notification_data["body"],
                "type": notification_type,
                "data": notification_data.get("data", {}),
                "priority": notification_data.get("priority", "normal"),
                "expires_at": notification_data.get("expires_at"),
                "created_at": datetime.now().isoformat(),
                "status": "queued"
            }
            
            # Add to notification queue
            self.notification_queue.append(notification)
            
            # Send to each device
            results = []
            for device_id in device_ids:
                if device_id in self.push_tokens:
                    result = await self._send_to_device(device_id, notification)
                    results.append({
                        "device_id": device_id,
                        "status": result["status"],
                        "message": result.get("message", "")
                    })
                else:
                    results.append({
                        "device_id": device_id,
                        "status": "failed",
                        "message": "Push token not found"
                    })
            
            logger.info(f"Push notification sent: {notification_id} to {len(device_ids)} devices")
            
            return {
                "success": True,
                "notification_id": notification_id,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Push notification sending failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _send_to_device(self, device_id: str, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification to a specific device"""
        
        try:
            push_token_info = self.push_tokens[device_id]
            platform = push_token_info["platform"]
            
            # Simulate push notification sending
            # In practice, this would integrate with FCM (Firebase), APNS (Apple), etc.
            
            if platform == "ios":
                # Simulate iOS push notification
                await asyncio.sleep(0.1)  # Simulate network delay
                success = True
                message = "iOS notification sent successfully"
            elif platform == "android":
                # Simulate Android push notification
                await asyncio.sleep(0.1)  # Simulate network delay
                success = True
                message = "Android notification sent successfully"
            elif platform == "web":
                # Simulate web push notification
                await asyncio.sleep(0.1)  # Simulate network delay
                success = True
                message = "Web notification sent successfully"
            else:
                success = False
                message = f"Unsupported platform: {platform}"
            
            # Update push token last used
            push_token_info["last_used"] = datetime.now().isoformat()
            
            # Update notification status
            if success:
                notification["status"] = "sent"
            else:
                notification["status"] = "failed"
            
            return {
                "status": "success" if success else "failed",
                "message": message
            }
            
        except Exception as e:
            logger.error(f"Failed to send notification to device {device_id}: {str(e)}")
            return {
                "status": "failed",
                "message": str(e)
            }
    
    async def start_offline_sync(
        self, 
        device_id: str,
        sync_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Start offline data synchronization for a mobile device
        
        Args:
            device_id: Device identifier
            sync_config: Synchronization configuration
            
        Returns:
            Dict with sync session details
        """
        try:
            if device_id not in self.registered_devices:
                raise HTTPException(status_code=404, detail="Device not found")
            
            # Check if sync is already in progress
            if device_id in self.sync_sessions and self.sync_sessions[device_id]["status"] == SyncStatus.IN_PROGRESS.value:
                raise HTTPException(status_code=409, detail="Sync already in progress")
            
            # Generate sync session ID
            session_id = str(uuid.uuid4())
            
            # Create sync session
            sync_session = {
                "session_id": session_id,
                "device_id": device_id,
                "status": SyncStatus.IN_PROGRESS.value,
                "started_at": datetime.now().isoformat(),
                "config": sync_config,
                "progress": 0,
                "total_items": 0,
                "synced_items": 0,
                "errors": []
            }
            
            self.sync_sessions[device_id] = sync_session
            
            # Start sync process in background
            asyncio.create_task(self._perform_offline_sync(device_id, session_id))
            
            logger.info(f"Offline sync started for device: {device_id} (session: {session_id})")
            
            return {
                "success": True,
                "session_id": session_id,
                "sync_session": sync_session
            }
            
        except Exception as e:
            logger.error(f"Offline sync start failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _perform_offline_sync(self, device_id: str, session_id: str):
        """Perform offline data synchronization"""
        
        try:
            sync_session = self.sync_sessions[device_id]
            
            # Simulate sync process
            sync_steps = [
                ("trades", 0.3),
                ("positions", 0.5),
                ("market_data", 0.7),
                ("notifications", 0.9),
                ("finalization", 1.0)
            ]
            
            for step_name, progress in sync_steps:
                await asyncio.sleep(1)  # Simulate processing time
                
                sync_session["progress"] = progress
                sync_session["synced_items"] += 10
                
                # Update session
                self.sync_sessions[device_id] = sync_session
            
            # Mark sync as completed
            sync_session["status"] = SyncStatus.COMPLETED.value
            sync_session["completed_at"] = datetime.now().isoformat()
            
            # Update offline data cache
            if device_id in self.offline_data_cache:
                self.offline_data_cache[device_id]["last_sync"] = datetime.now().isoformat()
            
            logger.info(f"Offline sync completed for device: {device_id} (session: {session_id})")
            
        except Exception as e:
            logger.error(f"Offline sync failed for device {device_id}: {str(e)}")
            
            # Mark sync as failed
            sync_session["status"] = SyncStatus.FAILED.value
            sync_session["completed_at"] = datetime.now().isoformat()
            sync_session["errors"].append(str(e))
            
            self.sync_sessions[device_id] = sync_session
    
    async def get_sync_status(self, device_id: str, session_id: str) -> Dict[str, Any]:
        """
        Get synchronization status for a device
        
        Args:
            device_id: Device identifier
            session_id: Sync session identifier
            
        Returns:
            Dict with sync status information
        """
        try:
            if device_id not in self.sync_sessions:
                raise HTTPException(status_code=404, detail="Sync session not found")
            
            sync_session = self.sync_sessions[device_id]
            
            if sync_session["session_id"] != session_id:
                raise HTTPException(status_code=404, detail="Sync session not found")
            
            return {
                "success": True,
                "sync_status": sync_session
            }
            
        except Exception as e:
            logger.error(f"Sync status retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_mobile_optimized_data(
        self, 
        device_id: str,
        data_type: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get mobile-optimized data for a specific device
        
        Args:
            device_id: Device identifier
            data_type: Type of data to retrieve
            filters: Optional filters for data
            
        Returns:
            Dict with mobile-optimized data
        """
        try:
            if device_id not in self.registered_devices:
                raise HTTPException(status_code=404, detail="Device not found")
            
            device = self.registered_devices[device_id]
            
            # Get device capabilities and preferences
            platform = device["platform"]
            screen_resolution = device.get("screen_resolution", "")
            language = device.get("language", "en")
            
            # Generate mobile-optimized data based on type
            if data_type == "trades":
                data = await self._get_mobile_trades(device_id, filters)
            elif data_type == "positions":
                data = await self._get_mobile_positions(device_id, filters)
            elif data_type == "market_data":
                data = await self._get_mobile_market_data(device_id, filters)
            elif data_type == "notifications":
                data = await self._get_mobile_notifications(device_id, filters)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported data type: {data_type}")
            
            # Optimize data for mobile
            optimized_data = self._optimize_for_mobile(data, platform, screen_resolution, language)
            
            # Update device last active
            device["last_active"] = datetime.now().isoformat()
            self.registered_devices[device_id] = device
            
            return {
                "success": True,
                "data_type": data_type,
                "data": optimized_data,
                "optimized_for": {
                    "platform": platform,
                    "screen_resolution": screen_resolution,
                    "language": language
                }
            }
            
        except Exception as e:
            logger.error(f"Mobile optimized data retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_mobile_trades(self, device_id: str, filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get mobile-optimized trades data"""
        
        # Simulate trades data
        # In practice, this would query the actual trades database
        
        trades = [
            {
                "trade_id": "TRADE-001",
                "commodity": "crude_oil",
                "side": "buy",
                "quantity": 1000,
                "price": 85.50,
                "status": "executed",
                "timestamp": datetime.now().isoformat(),
                "counterparty": "Shell Trading",
                "location": "Houston"
            },
            {
                "trade_id": "TRADE-002",
                "commodity": "natural_gas",
                "side": "sell",
                "quantity": 500,
                "price": 3.25,
                "status": "pending",
                "timestamp": datetime.now().isoformat(),
                "counterparty": "BP Energy",
                "location": "London"
            }
        ]
        
        return trades
    
    async def _get_mobile_positions(self, device_id: str, filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get mobile-optimized positions data"""
        
        # Simulate positions data
        positions = [
            {
                "commodity": "crude_oil",
                "long_position": 5000,
                "short_position": 2000,
                "net_position": 3000,
                "mtm_value": 255000.0,
                "unrealized_pnl": 15000.0,
                "last_updated": datetime.now().isoformat()
            },
            {
                "commodity": "natural_gas",
                "long_position": 3000,
                "short_position": 1000,
                "net_position": 2000,
                "mtm_value": 6500.0,
                "unrealized_pnl": 500.0,
                "last_updated": datetime.now().isoformat()
            }
        ]
        
        return positions
    
    async def _get_mobile_market_data(self, device_id: str, filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get mobile-optimized market data"""
        
        # Simulate market data
        market_data = [
            {
                "commodity": "crude_oil",
                "current_price": 85.50,
                "change": 1.25,
                "change_percent": 1.48,
                "volume": 1000000,
                "high": 86.00,
                "low": 84.25,
                "last_updated": datetime.now().isoformat()
            },
            {
                "commodity": "natural_gas",
                "current_price": 3.25,
                "change": -0.05,
                "change_percent": -1.52,
                "volume": 500000,
                "high": 3.30,
                "low": 3.20,
                "last_updated": datetime.now().isoformat()
            }
        ]
        
        return market_data
    
    async def _get_mobile_notifications(self, device_id: str, filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get mobile-optimized notifications"""
        
        # Get notifications from queue
        notifications = []
        for notification in self.notification_queue:
            if notification["status"] == "sent":
                notifications.append({
                    "notification_id": notification["notification_id"],
                    "title": notification["title"],
                    "body": notification["body"],
                    "type": notification["type"],
                    "timestamp": notification["created_at"],
                    "read": False
                })
        
        return notifications
    
    def _optimize_for_mobile(self, data: Any, platform: str, screen_resolution: str, language: str) -> Any:
        """Optimize data for mobile consumption"""
        
        if isinstance(data, list):
            # Limit list size for mobile
            max_items = 20 if platform == "ios" else 25
            if len(data) > max_items:
                data = data[:max_items]
            
            # Add mobile-specific metadata
            for item in data:
                if isinstance(item, dict):
                    item["_mobile_optimized"] = True
                    item["_platform"] = platform
        
        elif isinstance(data, dict):
            # Add mobile-specific metadata
            data["_mobile_optimized"] = True
            data["_platform"] = platform
        
        return data
    
    async def update_device_preferences(
        self, 
        device_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update mobile device preferences
        
        Args:
            device_id: Device identifier
            preferences: Device preferences to update
            
        Returns:
            Dict with update result
        """
        try:
            if device_id not in self.registered_devices:
                raise HTTPException(status_code=404, detail="Device not found")
            
            device = self.registered_devices[device_id]
            
            # Update preferences
            allowed_preferences = [
                "push_enabled", "offline_sync_enabled", "timezone", 
                "language", "notification_frequency", "data_refresh_interval"
            ]
            
            for key, value in preferences.items():
                if key in allowed_preferences:
                    device[key] = value
            
            device["last_updated"] = datetime.now().isoformat()
            self.registered_devices[device_id] = device
            
            logger.info(f"Device preferences updated for: {device_id}")
            
            return {
                "success": True,
                "device": device
            }
            
        except Exception as e:
            logger.error(f"Device preferences update failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_device_analytics(self, device_id: str) -> Dict[str, Any]:
        """
        Get analytics for a specific mobile device
        
        Args:
            device_id: Device identifier
            
        Returns:
            Dict with device analytics
        """
        try:
            if device_id not in self.registered_devices:
                raise HTTPException(status_code=404, detail="Device not found")
            
            device = self.registered_devices[device_id]
            
            # Calculate device usage metrics
            registered_date = datetime.fromisoformat(device["registered_at"])
            last_active = datetime.fromisoformat(device["last_active"])
            
            days_since_registration = (datetime.now() - registered_date).days
            hours_since_last_active = (datetime.now() - last_active).total_seconds() / 3600
            
            # Get sync statistics
            sync_stats = self._get_sync_statistics(device_id)
            
            # Get notification statistics
            notification_stats = self._get_notification_statistics(device_id)
            
            analytics = {
                "device_id": device_id,
                "usage_metrics": {
                    "days_since_registration": days_since_registration,
                    "hours_since_last_active": round(hours_since_last_active, 2),
                    "total_sessions": device.get("total_sessions", 0),
                    "last_session_duration": device.get("last_session_duration", 0)
                },
                "sync_statistics": sync_stats,
                "notification_statistics": notification_stats,
                "performance_metrics": {
                    "app_crash_rate": device.get("crash_rate", 0.0),
                    "response_time_avg": device.get("avg_response_time", 0.0),
                    "data_usage_mb": device.get("data_usage_mb", 0.0)
                },
                "generated_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "analytics": analytics
            }
            
        except Exception as e:
            logger.error(f"Device analytics retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _get_sync_statistics(self, device_id: str) -> Dict[str, Any]:
        """Get synchronization statistics for a device"""
        
        if device_id not in self.sync_sessions:
            return {
                "total_syncs": 0,
                "successful_syncs": 0,
                "failed_syncs": 0,
                "last_sync": None,
                "average_sync_duration": 0
            }
        
        sync_sessions = [s for s in self.sync_sessions.values() if s["device_id"] == device_id]
        
        total_syncs = len(sync_sessions)
        successful_syncs = sum(1 for s in sync_sessions if s["status"] == SyncStatus.COMPLETED.value)
        failed_syncs = sum(1 for s in sync_sessions if s["status"] == SyncStatus.FAILED.value)
        
        # Calculate average sync duration
        completed_syncs = [s for s in sync_sessions if s["status"] == SyncStatus.COMPLETED.value]
        if completed_syncs:
            durations = []
            for sync in completed_syncs:
                if "completed_at" in sync:
                    start_time = datetime.fromisoformat(sync["started_at"])
                    end_time = datetime.fromisoformat(sync["completed_at"])
                    duration = (end_time - start_time).total_seconds()
                    durations.append(duration)
            
            avg_duration = sum(durations) / len(durations) if durations else 0
        else:
            avg_duration = 0
        
        # Get last sync
        last_sync = None
        if completed_syncs:
            last_sync = max(completed_syncs, key=lambda x: x["started_at"])["started_at"]
        
        return {
            "total_syncs": total_syncs,
            "successful_syncs": successful_syncs,
            "failed_syncs": failed_syncs,
            "last_sync": last_sync,
            "average_sync_duration": round(avg_duration, 2)
        }
    
    def _get_notification_statistics(self, device_id: str) -> Dict[str, Any]:
        """Get notification statistics for a device"""
        
        # Count notifications sent to this device
        device_notifications = []
        for notification in self.notification_queue:
            # In practice, we'd track which notifications were sent to which devices
            # For now, we'll simulate this
            device_notifications.append(notification)
        
        total_notifications = len(device_notifications)
        sent_notifications = sum(1 for n in device_notifications if n["status"] == "sent")
        failed_notifications = sum(1 for n in device_notifications if n["status"] == "failed")
        
        return {
            "total_notifications": total_notifications,
            "sent_notifications": sent_notifications,
            "failed_notifications": failed_notifications,
            "delivery_rate": (sent_notifications / total_notifications * 100) if total_notifications > 0 else 0
        }
    
    async def get_system_mobile_analytics(self) -> Dict[str, Any]:
        """
        Get overall mobile system analytics
        
        Returns:
            Dict with system mobile analytics
        """
        try:
            total_devices = len(self.registered_devices)
            active_devices = sum(1 for d in self.registered_devices.values() if d["status"] == "active")
            
            # Platform distribution
            platform_distribution = {}
            for device in self.registered_devices.values():
                platform = device["platform"]
                platform_distribution[platform] = platform_distribution.get(platform, 0) + 1
            
            # App version distribution
            version_distribution = {}
            for device in self.registered_devices.values():
                version = device["app_version"]
                version_distribution[version] = version_distribution.get(version, 0) + 1
            
            # Push notification statistics
            total_push_tokens = len(self.push_tokens)
            active_push_tokens = sum(1 for t in self.push_tokens.values() if t["status"] == "active")
            
            # Sync statistics
            total_sync_sessions = len(self.sync_sessions)
            active_sync_sessions = sum(1 for s in self.sync_sessions.values() if s["status"] == SyncStatus.IN_PROGRESS.value)
            
            analytics = {
                "total_devices": total_devices,
                "active_devices": active_devices,
                "device_health": (active_devices / total_devices * 100) if total_devices > 0 else 0,
                "platform_distribution": platform_distribution,
                "version_distribution": version_distribution,
                "push_notifications": {
                    "total_tokens": total_push_tokens,
                    "active_tokens": active_push_tokens,
                    "coverage_rate": (active_push_tokens / total_devices * 100) if total_devices > 0 else 0
                },
                "sync_statistics": {
                    "total_sessions": total_sync_sessions,
                    "active_sessions": active_sync_sessions
                },
                "generated_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "analytics": analytics
            }
            
        except Exception as e:
            logger.error(f"System mobile analytics retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
