"""
Test Phase 2 Complete Features Implementation
Tests IoT integration, mobile app, and admin dashboard services
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import numpy as np

# Import the services to test
from app.services.iot_integration_service import IoTIntegrationService, DeviceType, DataType
from app.services.mobile_app_service import MobileAppService, NotificationType, SyncStatus
from app.services.admin_dashboard_service import AdminDashboardService, UserRole, SystemStatus

class TestIoTIntegrationService:
    """Test IoT integration service"""
    
    @pytest.fixture
    def iot_service(self):
        return IoTIntegrationService()
    
    @pytest.fixture
    def sample_device_config(self):
        return {
            "device_id": "SENSOR-001",
            "device_type": DeviceType.SENSOR.value,
            "data_type": DataType.TEMPERATURE.value,
            "location": "Houston Refinery",
            "capabilities": ["temperature_monitoring", "data_transmission"],
            "config": {"sampling_rate": "1Hz", "calibration_date": "2024-01-01"},
            "metadata": {"manufacturer": "QuantaTech", "model": "QT-1000"}
        }
    
    @pytest.fixture
    def sample_data_payload(self):
        return {
            "timestamp": datetime.now().isoformat(),
            "value": 75.5,
            "metadata": {"sensor_health": "good", "battery_level": 85}
        }
    
    @pytest.mark.asyncio
    async def test_register_device(self, iot_service, sample_device_config):
        """Test IoT device registration"""
        result = await iot_service.register_device(sample_device_config)
        
        assert result["success"] is True
        assert "device" in result
        assert result["device"]["device_id"] == "SENSOR-001"
        assert result["device"]["device_type"] == DeviceType.SENSOR.value
        assert result["device"]["data_type"] == DataType.TEMPERATURE.value
        assert result["device"]["status"] == "active"
        assert "internal_id" in result["device"]
    
    @pytest.mark.asyncio
    async def test_send_data(self, iot_service, sample_device_config, sample_data_payload):
        """Test sending data from IoT device"""
        # First register the device
        await iot_service.register_device(sample_device_config)
        
        # Send data
        result = await iot_service.send_data("SENSOR-001", sample_data_payload)
        
        assert result["success"] is True
        assert "data_id" in result
        assert "processed_data" in result
        assert result["processed_data"]["processed_value"] == 75.5
        assert result["processed_data"]["data_type"] == DataType.TEMPERATURE.value
    
    @pytest.mark.asyncio
    async def test_create_alert_rule(self, iot_service, sample_device_config):
        """Test creating IoT alert rule"""
        # First register the device
        await iot_service.register_device(sample_device_config)
        
        # Create alert rule
        alert_config = {
            "name": "High Temperature Alert",
            "device_id": "SENSOR-001",
            "condition": "above",
            "threshold": 80.0,
            "action": "notification"
        }
        
        result = await iot_service.create_alert_rule(alert_config)
        
        assert result["success"] is True
        assert "alert_id" in result
        assert "alert_rule" in result
        assert result["alert_rule"]["name"] == "High Temperature Alert"
        assert result["alert_rule"]["device_id"] == "SENSOR-001"
    
    @pytest.mark.asyncio
    async def test_create_trading_trigger(self, iot_service, sample_device_config):
        """Test creating IoT trading trigger"""
        # First register the device
        await iot_service.register_device(sample_device_config)
        
        # Create trading trigger
        trigger_config = {
            "name": "Temperature Trading Trigger",
            "device_id": "SENSOR-001",
            "condition": "above",
            "threshold": 85.0,
            "trading_action": "sell"
        }
        
        result = await iot_service.create_trading_trigger(trigger_config)
        
        assert result["success"] is True
        assert "trigger_id" in result
        assert "trading_trigger" in result
        assert result["trading_trigger"]["name"] == "Temperature Trading Trigger"
    
    @pytest.mark.asyncio
    async def test_get_device_status(self, iot_service, sample_device_config):
        """Test getting device status"""
        # First register the device
        await iot_service.register_device(sample_device_config)
        
        # Get device status
        result = await iot_service.get_device_status("SENSOR-001")
        
        assert result["success"] is True
        assert "status" in result
        assert "device" in result["status"]
        assert "recent_data" in result["status"]
        assert "analytics" in result["status"]
    
    @pytest.mark.asyncio
    async def test_get_system_analytics(self, iot_service, sample_device_config):
        """Test getting IoT system analytics"""
        # First register the device
        await iot_service.register_device(sample_device_config)
        
        # Get system analytics
        result = await iot_service.get_system_analytics()
        
        assert result["success"] is True
        assert "analytics" in result
        assert result["analytics"]["total_devices"] == 1
        assert "performance_metrics" in result["analytics"]
        assert "status_distribution" in result["analytics"]
    
    def test_data_validation_and_processing(self, iot_service, sample_device_config):
        """Test data validation and processing"""
        # Register device
        asyncio.run(iot_service.register_device(sample_device_config))
        
        # Test different data types
        test_cases = [
            (DataType.TEMPERATURE.value, 75.5, 75.5),
            (DataType.PRESSURE.value, 1500.0, 1500.0),
            (DataType.FLOW_RATE.value, 100.0, 100.0),
            (DataType.VOLUME.value, 5000.0, 5000.0),
            (DataType.QUALITY.value, 95.0, 95.0)
        ]
        
        for data_type, input_value, expected_value in test_cases:
            # Update device data type
            device = iot_service.connected_devices["SENSOR-001"]
            device["data_type"] = data_type
            
            # Test data processing
            processed_data = iot_service._process_device_data("SENSOR-001", {
                "timestamp": datetime.now().isoformat(),
                "value": input_value
            })
            
            assert processed_data["processed_value"] == expected_value
            assert processed_data["data_type"] == data_type

class TestMobileAppService:
    """Test mobile app service"""
    
    @pytest.fixture
    def mobile_service(self):
        return MobileAppService()
    
    @pytest.fixture
    def sample_device_info(self):
        return {
            "device_id": "MOBILE-001",
            "platform": "ios",
            "app_version": "1.0.0",
            "device_model": "iPhone 15 Pro",
            "os_version": "iOS 17.0",
            "screen_resolution": "1179x2556",
            "timezone": "America/New_York",
            "language": "en"
        }
    
    @pytest.fixture
    def sample_notification_data(self):
        return {
            "title": "Trade Alert",
            "body": "New trade executed successfully",
            "type": NotificationType.TRADE_ALERT.value,
            "data": {"trade_id": "TRADE-001"},
            "priority": "high"
        }
    
    @pytest.mark.asyncio
    async def test_register_mobile_device(self, mobile_service, sample_device_info):
        """Test mobile device registration"""
        result = await mobile_service.register_mobile_device(sample_device_info)
        
        assert result["success"] is True
        assert "device" in result
        assert result["device"]["device_id"] == "MOBILE-001"
        assert result["device"]["platform"] == "ios"
        assert result["device"]["app_version"] == "1.0.0"
        assert result["device"]["status"] == "active"
        assert "internal_id" in result["device"]
    
    @pytest.mark.asyncio
    async def test_register_push_token(self, mobile_service, sample_device_info):
        """Test push token registration"""
        # First register the device
        await mobile_service.register_mobile_device(sample_device_info)
        
        # Register push token
        result = await mobile_service.register_push_token("MOBILE-001", "token123", "ios")
        
        assert result["success"] is True
        assert "token_id" in result
        
        # Verify device has push enabled
        device = mobile_service.registered_devices["MOBILE-001"]
        assert device["push_enabled"] is True
    
    @pytest.mark.asyncio
    async def test_send_push_notification(self, mobile_service, sample_device_info, sample_notification_data):
        """Test sending push notification"""
        # First register the device and push token
        await mobile_service.register_mobile_device(sample_device_info)
        await mobile_service.register_push_token("MOBILE-001", "token123", "ios")
        
        # Send notification
        result = await mobile_service.send_push_notification(["MOBILE-001"], sample_notification_data)
        
        assert result["success"] is True
        assert "notification_id" in result
        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["device_id"] == "MOBILE-001"
    
    @pytest.mark.asyncio
    async def test_start_offline_sync(self, mobile_service, sample_device_info):
        """Test starting offline synchronization"""
        # First register the device
        await mobile_service.register_mobile_device(sample_device_info)
        
        # Start sync
        sync_config = {"data_types": ["trades", "positions"], "priority": "high"}
        result = await mobile_service.start_offline_sync("MOBILE-001", sync_config)
        
        assert result["success"] is True
        assert "session_id" in result
        assert "sync_session" in result
        assert result["sync_session"]["status"] == SyncStatus.IN_PROGRESS.value
    
    @pytest.mark.asyncio
    async def test_get_sync_status(self, mobile_service, sample_device_info):
        """Test getting sync status"""
        # First register the device and start sync
        await mobile_service.register_mobile_device(sample_device_info)
        sync_config = {"data_types": ["trades"]}
        sync_result = await mobile_service.start_offline_sync("MOBILE-001", sync_config)
        session_id = sync_result["session_id"]
        
        # Get sync status
        result = await mobile_service.get_sync_status("MOBILE-001", session_id)
        
        assert result["success"] is True
        assert "sync_status" in result
        assert result["sync_status"]["session_id"] == session_id
    
    @pytest.mark.asyncio
    async def test_get_mobile_optimized_data(self, mobile_service, sample_device_info):
        """Test getting mobile-optimized data"""
        # First register the device
        await mobile_service.register_mobile_device(sample_device_info)
        
        # Get different types of data
        data_types = ["trades", "positions", "market_data", "notifications"]
        
        for data_type in data_types:
            result = await mobile_service.get_mobile_optimized_data("MOBILE-001", data_type)
            
            assert result["success"] is True
            assert result["data_type"] == data_type
            assert "data" in result
            assert "optimized_for" in result
            assert result["optimized_for"]["platform"] == "ios"
    
    @pytest.mark.asyncio
    async def test_update_device_preferences(self, mobile_service, sample_device_info):
        """Test updating device preferences"""
        # First register the device
        await mobile_service.register_mobile_device(sample_device_info)
        
        # Update preferences
        preferences = {
            "push_enabled": False,
            "timezone": "Europe/London",
            "language": "fr"
        }
        
        result = await mobile_service.update_device_preferences("MOBILE-001", preferences)
        
        assert result["success"] is True
        assert "device" in result
        assert result["device"]["push_enabled"] is False
        assert result["device"]["timezone"] == "Europe/London"
        assert result["device"]["language"] == "fr"
    
    @pytest.mark.asyncio
    async def test_get_device_analytics(self, mobile_service, sample_device_info):
        """Test getting device analytics"""
        # First register the device
        await mobile_service.register_mobile_device(sample_device_info)
        
        # Get device analytics
        result = await mobile_service.get_device_analytics("MOBILE-001")
        
        assert result["success"] is True
        assert "analytics" in result
        assert "usage_metrics" in result["analytics"]
        assert "sync_statistics" in result["analytics"]
        assert "notification_statistics" in result["analytics"]
        assert "performance_metrics" in result["analytics"]
    
    @pytest.mark.asyncio
    async def test_get_system_mobile_analytics(self, mobile_service, sample_device_info):
        """Test getting system mobile analytics"""
        # First register the device
        await mobile_service.register_mobile_device(sample_device_info)
        
        # Get system analytics
        result = await mobile_service.get_system_mobile_analytics()
        
        assert result["success"] is True
        assert "analytics" in result
        assert result["analytics"]["total_devices"] == 1
        assert "platform_distribution" in result["analytics"]
        assert "version_distribution" in result["analytics"]
        assert "push_notifications" in result["analytics"]
        assert "sync_statistics" in result["analytics"]

class TestAdminDashboardService:
    """Test admin dashboard service"""
    
    @pytest.fixture
    def admin_service(self):
        return AdminDashboardService()
    
    @pytest.fixture
    def sample_user_data(self):
        return {
            "username": "trader1",
            "email": "trader1@quantaenergi.com",
            "role": UserRole.TRADER.value,
            "first_name": "John",
            "last_name": "Doe",
            "department": "Trading",
            "phone": "+1-555-0002",
            "location": "Houston"
        }
    
    @pytest.fixture
    def sample_alert_data(self):
        return {
            "title": "High CPU Usage",
            "message": "CPU usage has exceeded 90%",
            "severity": "warning",
            "metadata": {"threshold": 90, "current_value": 95}
        }
    
    @pytest.fixture
    def sample_maintenance_data(self):
        return {
            "title": "Database Maintenance",
            "description": "Scheduled database optimization and cleanup",
            "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
            "affected_services": ["database", "trading_engine"],
            "metadata": {"estimated_downtime": "2 hours"}
        }
    
    @pytest.mark.asyncio
    async def test_create_user(self, admin_service, sample_user_data):
        """Test creating a new user"""
        result = await admin_service.create_user(sample_user_data, "admin")
        
        assert result["success"] is True
        assert "user" in result
        assert result["user"]["username"] == "trader1"
        assert result["user"]["email"] == "trader1@quantaenergi.com"
        assert result["user"]["role"] == UserRole.TRADER.value
        assert result["user"]["status"] == "active"
        assert "internal_id" in result["user"]
    
    @pytest.mark.asyncio
    async def test_update_user(self, admin_service, sample_user_data):
        """Test updating user information"""
        # First create the user
        await admin_service.create_user(sample_user_data, "admin")
        
        # Update user
        update_data = {
            "email": "trader1.updated@quantaenergi.com",
            "role": UserRole.RISK_MANAGER.value
        }
        
        result = await admin_service.update_user("trader1", update_data, "admin")
        
        assert result["success"] is True
        assert "user" in result
        assert result["user"]["email"] == "trader1.updated@quantaenergi.com"
        assert result["user"]["role"] == UserRole.RISK_MANAGER.value
        assert "last_updated" in result["user"]
    
    @pytest.mark.asyncio
    async def test_delete_user(self, admin_service, sample_user_data):
        """Test deleting a user"""
        # First create the user
        await admin_service.create_user(sample_user_data, "admin")
        
        # Delete user
        result = await admin_service.delete_user("trader1", "admin")
        
        assert result["success"] is True
        assert "deleted_user" in result
        assert result["deleted_user"]["username"] == "trader1"
        
        # Verify user is removed
        user_list = await admin_service.get_user_list("admin")
        assert user_list["total_count"] == 1  # Only admin user remains
    
    @pytest.mark.asyncio
    async def test_get_user_list(self, admin_service, sample_user_data):
        """Test getting user list"""
        # First create a user
        await admin_service.create_user(sample_user_data, "admin")
        
        # Get user list
        result = await admin_service.get_user_list("admin")
        
        assert result["success"] is True
        assert "users" in result
        assert result["total_count"] == 2  # admin + trader1
        
        # Test filtering
        filtered_result = await admin_service.get_user_list("admin", {"role": UserRole.TRADER.value})
        assert filtered_result["total_count"] == 1
        assert filtered_result["users"][0]["role"] == UserRole.TRADER.value
    
    @pytest.mark.asyncio
    async def test_get_system_metrics(self, admin_service):
        """Test getting system metrics"""
        result = await admin_service.get_system_metrics("admin")
        
        assert result["success"] is True
        assert "system_metrics" in result
        assert "system_status" in result["system_metrics"]
        assert "metrics" in result["system_metrics"]
        assert "alerts" in result["system_metrics"]
        assert "performance_summary" in result["system_metrics"]
        
        # Check metrics structure
        metrics = result["system_metrics"]["metrics"]
        assert "cpu_usage" in metrics
        assert "memory_usage" in metrics
        assert "disk_usage" in metrics
        assert "network_throughput" in metrics
        assert "active_connections" in metrics
    
    @pytest.mark.asyncio
    async def test_create_system_alert(self, admin_service, sample_alert_data):
        """Test creating system alert"""
        result = await admin_service.create_system_alert(sample_alert_data, "admin")
        
        assert result["success"] is True
        assert "alert" in result
        assert result["alert"]["title"] == "High CPU Usage"
        assert result["alert"]["message"] == "CPU usage has exceeded 90%"
        assert result["alert"]["severity"] == "warning"
        assert result["alert"]["status"] == "active"
        assert result["alert"]["created_by"] == "admin"
    
    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, admin_service, sample_alert_data):
        """Test acknowledging system alert"""
        # First create the alert
        alert_result = await admin_service.create_system_alert(sample_alert_data, "admin")
        alert_id = alert_result["alert"]["alert_id"]
        
        # Acknowledge alert
        result = await admin_service.acknowledge_alert(alert_id, "admin")
        
        assert result["success"] is True
        assert "alert" in result
        assert result["alert"]["status"] == "acknowledged"
        assert result["alert"]["acknowledged_by"] == "admin"
        assert result["alert"]["acknowledged_at"] is not None
    
    @pytest.mark.asyncio
    async def test_get_audit_logs(self, admin_service, sample_user_data):
        """Test getting audit logs"""
        # First create a user to generate some logs
        await admin_service.create_user(sample_user_data, "admin")
        
        # Get audit logs
        result = await admin_service.get_audit_logs("admin")
        
        assert result["success"] is True
        assert "audit_logs" in result
        assert result["total_count"] > 0
        
        # Test filtering
        filtered_result = await admin_service.get_audit_logs("admin", {"action_type": "create_user"})
        assert filtered_result["total_count"] > 0
        for log in filtered_result["audit_logs"]:
            assert log["action_type"] == "create_user"
    
    @pytest.mark.asyncio
    async def test_schedule_maintenance(self, admin_service, sample_maintenance_data):
        """Test scheduling maintenance"""
        result = await admin_service.schedule_maintenance(sample_maintenance_data, "admin")
        
        assert result["success"] is True
        assert "maintenance" in result
        assert result["maintenance"]["title"] == "Database Maintenance"
        assert result["maintenance"]["status"] == "scheduled"
        assert result["maintenance"]["created_by"] == "admin"
        assert "maintenance_id" in result["maintenance"]
    
    @pytest.mark.asyncio
    async def test_get_maintenance_schedules(self, admin_service, sample_maintenance_data):
        """Test getting maintenance schedules"""
        # First schedule maintenance
        await admin_service.schedule_maintenance(sample_maintenance_data, "admin")
        
        # Get maintenance schedules
        result = await admin_service.get_maintenance_schedules("admin")
        
        assert result["success"] is True
        assert "maintenance_schedules" in result
        assert result["total_count"] > 0
        
        # Test filtering
        filtered_result = await admin_service.get_maintenance_schedules("admin", {"status": "scheduled"})
        assert filtered_result["total_count"] > 0
        for schedule in filtered_result["maintenance_schedules"]:
            assert schedule["status"] == "scheduled"
    
    @pytest.mark.asyncio
    async def test_get_dashboard_summary(self, admin_service, sample_user_data):
        """Test getting dashboard summary"""
        # First create a user to generate some data
        await admin_service.create_user(sample_user_data, "admin")
        
        # Get dashboard summary
        result = await admin_service.get_dashboard_summary("admin")
        
        assert result["success"] is True
        assert "dashboard_summary" in result
        
        summary = result["dashboard_summary"]
        assert "user_statistics" in summary
        assert "system_health" in summary
        assert "maintenance" in summary
        assert "recent_activity" in summary
        
        # Check user statistics
        user_stats = summary["user_statistics"]
        assert user_stats["total_users"] == 2  # admin + trader1
        assert user_stats["active_users"] == 2
        assert user_stats["user_health"] == 100.0
    
    def test_role_permissions(self, admin_service):
        """Test role-based permissions"""
        
        # Test admin permissions
        admin_permissions = admin_service._get_role_permissions(UserRole.ADMIN.value)
        assert "user_management" in admin_permissions
        assert "system_monitoring" in admin_permissions
        assert "audit_logs" in admin_permissions
        
        # Test trader permissions
        trader_permissions = admin_service._get_role_permissions(UserRole.TRADER.value)
        assert "trade_execution" in trader_permissions
        assert "position_viewing" in trader_permissions
        assert "user_management" not in trader_permissions
        
        # Test compliance officer permissions
        compliance_permissions = admin_service._get_role_permissions(UserRole.COMPLIANCE_OFFICER.value)
        assert "compliance_monitoring" in compliance_permissions
        assert "regulatory_reporting" in compliance_permissions
        assert "audit_logs" in compliance_permissions
    
    def test_permission_checking(self, admin_service):
        """Test permission checking functionality"""
        
        # Admin should have all permissions
        assert admin_service._has_permission("admin", "user_management") is True
        assert admin_service._has_permission("admin", "system_monitoring") is True
        assert admin_service._has_permission("admin", "audit_logs") is True
        
        # Non-existent user should have no permissions
        assert admin_service._has_permission("nonexistent", "user_management") is False
    
    def test_system_status_determination(self, admin_service):
        """Test system status determination"""
        
        # Test healthy status
        admin_service.system_metrics.update({
            "cpu_usage": 50.0,
            "memory_usage": 60.0,
            "disk_usage": 70.0
        })
        assert admin_service._determine_system_status() == SystemStatus.HEALTHY.value
        
        # Test warning status
        admin_service.system_metrics.update({
            "cpu_usage": 85.0,
            "memory_usage": 60.0,
            "disk_usage": 70.0
        })
        assert admin_service._determine_system_status() == SystemStatus.WARNING.value
        
        # Test critical status
        admin_service.system_metrics.update({
            "cpu_usage": 95.0,
            "memory_usage": 60.0,
            "disk_usage": 70.0
        })
        assert admin_service._determine_system_status() == SystemStatus.CRITICAL.value

if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v"])
