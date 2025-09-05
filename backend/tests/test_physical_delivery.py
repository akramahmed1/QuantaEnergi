"""
Test Physical Delivery Management Service
Tests asset tracking, delivery scheduling, logistics coordination
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import uuid

from app.services.physical_delivery import PhysicalDeliveryManagement, DeliveryObserver

class TestPhysicalDeliveryManagement:
    """Test physical delivery management service"""
    
    @pytest.fixture
    def delivery_service(self):
        """Create delivery service instance"""
        return PhysicalDeliveryManagement()
    
    @pytest.fixture
    def sample_delivery_data(self):
        """Sample delivery data for testing"""
        return {
            "routes": ["Route A", "Route B", "Route C"],
            "vehicles": ["Truck 1", "Truck 2"],
            "organization_id": "test-org-123",
            "priority": "high",
            "delivery_type": "energy_commodity"
        }
    
    @pytest.mark.asyncio
    async def test_track_asset_success(self, delivery_service):
        """Test successful asset tracking"""
        asset_id = "asset-123"
        location = {"latitude": 25.2048, "longitude": 55.2708}
        
        result = await delivery_service.track_asset(asset_id, location)
        
        assert result["asset_id"] == asset_id
        assert result["status"] == "tracked"
        assert result["location"]["latitude"] == 25.2048
        assert result["location"]["longitude"] == 55.2708
        assert "timestamp" in result["location"]
        assert "last_updated" in result
    
    @pytest.mark.asyncio
    async def test_track_asset_without_location(self, delivery_service):
        """Test asset tracking without location data"""
        asset_id = "asset-456"
        
        result = await delivery_service.track_asset(asset_id)
        
        assert result["asset_id"] == asset_id
        assert result["status"] == "tracked"
        assert "latitude" in result["location"]
        assert "longitude" in result["location"]
    
    @pytest.mark.asyncio
    async def test_track_asset_invalid_id(self, delivery_service):
        """Test asset tracking with invalid ID"""
        with pytest.raises(Exception):  # HTTPException from FastAPI
            await delivery_service.track_asset("")
    
    def test_schedule_delivery_success(self, delivery_service, sample_delivery_data):
        """Test successful delivery scheduling"""
        result = delivery_service.schedule_delivery(sample_delivery_data)
        
        assert "delivery_id" in result
        assert result["status"] == "scheduled"
        assert result["optimized_routes"] == sample_delivery_data["routes"][:2]
        assert "estimated_duration" in result
        assert "total_distance" in result
        assert "optimization_score" in result
        assert result["optimization_score"] == 0.85
    
    def test_schedule_delivery_empty_routes(self, delivery_service):
        """Test delivery scheduling with empty routes"""
        delivery_data = {"routes": [], "vehicles": ["Truck 1"]}
        
        result = delivery_service.schedule_delivery(delivery_data)
        
        assert result["status"] == "scheduled"
        assert result["optimized_routes"] == []
        assert result["estimated_duration"] == 0
    
    @pytest.mark.asyncio
    async def test_coordinate_logistics_success(self, delivery_service, sample_delivery_data):
        """Test successful logistics coordination"""
        # First schedule a delivery
        delivery_result = delivery_service.schedule_delivery(sample_delivery_data)
        delivery_id = delivery_result["delivery_id"]
        
        logistics_data = {
            "provider": "DHL",
            "requirements": ["temperature_controlled", "hazardous_materials"]
        }
        
        result = await delivery_service.coordinate_logistics(delivery_id, logistics_data)
        
        assert result["delivery_id"] == delivery_id
        assert result["status"] == "coordinated"
        assert result["logistics_provider"] == "DHL"
        assert "tracking_number" in result
        assert "estimated_delivery" in result
        assert result["special_requirements"] == logistics_data["requirements"]
    
    @pytest.mark.asyncio
    async def test_coordinate_logistics_nonexistent_delivery(self, delivery_service):
        """Test logistics coordination for non-existent delivery"""
        with pytest.raises(Exception):  # HTTPException from FastAPI
            await delivery_service.coordinate_logistics("nonexistent-id")
    
    @pytest.mark.asyncio
    async def test_coordinate_logistics_without_data(self, delivery_service, sample_delivery_data):
        """Test logistics coordination without logistics data"""
        delivery_result = delivery_service.schedule_delivery(sample_delivery_data)
        delivery_id = delivery_result["delivery_id"]
        
        result = await delivery_service.coordinate_logistics(delivery_id)
        
        assert result["delivery_id"] == delivery_id
        assert result["status"] == "coordinated"
        assert result["logistics_provider"] == "default"
        assert result["special_requirements"] == []
    
    @pytest.mark.asyncio
    async def test_update_delivery_status_success(self, delivery_service, sample_delivery_data):
        """Test successful delivery status update"""
        delivery_result = delivery_service.schedule_delivery(sample_delivery_data)
        delivery_id = delivery_result["delivery_id"]
        
        location = {"latitude": 25.3000, "longitude": 55.3000}
        result = await delivery_service.update_delivery_status(
            delivery_id, "in_transit", location
        )
        
        assert result["delivery_id"] == delivery_id
        assert result["status"] == "in_transit"
        assert result["location"]["latitude"] == 25.3000
        assert "updated_at" in result
    
    @pytest.mark.asyncio
    async def test_update_delivery_status_nonexistent(self, delivery_service):
        """Test status update for non-existent delivery"""
        with pytest.raises(Exception):  # HTTPException from FastAPI
            await delivery_service.update_delivery_status("nonexistent-id", "completed")
    
    @pytest.mark.asyncio
    async def test_get_delivery_analytics(self, delivery_service, sample_delivery_data):
        """Test delivery analytics generation"""
        org_id = "test-org-123"
        
        # Create multiple deliveries for the organization
        for i in range(5):
            delivery_data = sample_delivery_data.copy()
            delivery_data["organization_id"] = org_id
            delivery_result = delivery_service.schedule_delivery(delivery_data)
            
            # Update some to completed status
            if i < 3:
                await delivery_service.update_delivery_status(
                    delivery_result["delivery_id"], "completed"
                )
            else:
                await delivery_service.update_delivery_status(
                    delivery_result["delivery_id"], "in_transit"
                )
        
        analytics = await delivery_service.get_delivery_analytics(org_id)
        
        assert analytics["total_deliveries"] == 5
        assert analytics["completed_deliveries"] == 3
        assert analytics["in_transit_deliveries"] == 2
        assert "average_delivery_time" in analytics
        assert "on_time_delivery_rate" in analytics
        assert "total_distance" in analytics
        assert "optimization_score" in analytics
    
    def test_observer_pattern(self, delivery_service):
        """Test observer pattern for delivery updates"""
        updates_received = []
        
        def callback(data):
            updates_received.append(data)
        
        # Subscribe to updates
        delivery_service.observer.subscribe(callback)
        
        # Trigger updates
        delivery_data = {"routes": ["Route 1"], "vehicles": ["Truck 1"]}
        delivery_service.schedule_delivery(delivery_data)
        
        # Check if observer was notified
        assert len(updates_received) >= 1
        assert updates_received[0]["status"] == "scheduled"
    
    def test_multithreaded_scheduling(self, delivery_service):
        """Test multithreaded scheduling optimization"""
        delivery_data = {
            "routes": [f"Route {i}" for i in range(10)],
            "vehicles": [f"Truck {i}" for i in range(3)]
        }
        
        # This should complete without hanging (multithreading test)
        result = delivery_service.schedule_delivery(delivery_data)
        
        assert result["status"] == "scheduled"
        assert len(result["optimized_routes"]) <= len(delivery_data["vehicles"])
    
    def test_cleanup(self, delivery_service):
        """Test service cleanup"""
        # Should not raise exception
        delivery_service.cleanup()
        
        # Verify executor is shutdown
        assert delivery_service.executor._shutdown

@pytest.mark.asyncio
async def test_integration_10_deliveries():
    """Integration test with 10 deliveries as specified in PRD"""
    service = PhysicalDeliveryManagement()
    
    try:
        # Create 10 deliveries
        delivery_ids = []
        for i in range(10):
            delivery_data = {
                "routes": [f"Route {i}-{j}" for j in range(3)],
                "vehicles": [f"Truck {i}-{j}" for j in range(2)],
                "organization_id": f"org-{i % 3}",  # 3 different orgs
                "priority": "high" if i % 2 == 0 else "normal"
            }
            
            # Schedule delivery
            result = service.schedule_delivery(delivery_data)
            delivery_ids.append(result["delivery_id"])
            
            # Track associated asset
            asset_id = f"asset-{i}"
            await service.track_asset(asset_id)
            
            # Coordinate logistics
            await service.coordinate_logistics(
                result["delivery_id"], 
                {"provider": f"Provider-{i % 2}"}
            )
            
            # Update status
            status = "completed" if i < 7 else "in_transit"
            await service.update_delivery_status(result["delivery_id"], status)
        
        # Verify all deliveries were created
        assert len(delivery_ids) == 10
        assert len(service.deliveries) == 10
        assert len(service.assets) == 10
        
        # Test analytics for each organization
        for org_id in ["org-0", "org-1", "org-2"]:
            analytics = await service.get_delivery_analytics(org_id)
            # Debug: print analytics to understand the issue
            print(f"Analytics for {org_id}: {analytics}")
            assert analytics["total_deliveries"] > 0
        
        print("✅ Integration test with 10 deliveries completed successfully")
        
    finally:
        service.cleanup()

if __name__ == "__main__":
    # Run the integration test
    asyncio.run(test_integration_10_deliveries())
