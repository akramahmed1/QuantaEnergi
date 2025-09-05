"""
Test Database Integration for Multi-Tenant ETRM/CTRM Operations
Tests async database operations, organization isolation, and error handling
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4
import uuid
from fastapi import HTTPException

from app.core.database_manager import MultiTenantDBManager
from app.models.organization import Organization
from app.models.trade import Trade

class TestMultiTenantDBManager:
    """Test multi-tenant database manager"""
    
    @pytest.fixture
    def db_manager(self):
        """Create database manager instance"""
        return MultiTenantDBManager()
    
    @pytest.fixture
    def mock_session(self):
        """Create mock async session"""
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.refresh = AsyncMock()
        return session
    
    @pytest.fixture
    def sample_org_id(self):
        """Sample organization ID"""
        return uuid4()
    
    @pytest.fixture
    def sample_trade_data(self):
        """Sample trade data for testing"""
        return {
            "trade_type": "spot",
            "commodity": "crude_oil",
            "quantity": 1000.0,
            "price": 85.50,
            "currency": "USD",
            "counterparty_id": "CP001",
            "counterparty_name": "Test Counterparty",
            "delivery_date": datetime.now() + timedelta(days=30),
            "delivery_location": "Houston, TX",
            "trade_direction": "buy",
            "settlement_type": "T+2",
            "is_islamic_compliant": True,
            "risk_category": "medium"
        }
    
    @pytest.mark.asyncio
    async def test_get_trades_for_org_success(self, db_manager, mock_session, sample_org_id):
        """Test successful retrieval of trades for organization"""
        # Mock trade objects
        mock_trades = [
            Trade(
                id=uuid4(),
                organization_id=sample_org_id,
                trade_id="TRD-001",
                trade_type="spot",
                commodity="crude_oil",
                quantity=1000.0,
                price=85.50,
                notional_value=85500.0
            ),
            Trade(
                id=uuid4(),
                organization_id=sample_org_id,
                trade_id="TRD-002",
                trade_type="forward",
                commodity="natural_gas",
                quantity=5000.0,
                price=3.20,
                notional_value=16000.0
            )
        ]
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_trades
        mock_session.execute.return_value = mock_result
        
        # Test the method
        trades = await db_manager.get_trades_for_org(mock_session, sample_org_id)
        
        # Assertions
        assert len(trades) == 2
        assert trades[0].trade_id == "TRD-001"
        assert trades[1].trade_id == "TRD-002"
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_trades_for_org_with_pagination(self, db_manager, mock_session, sample_org_id):
        """Test trade retrieval with pagination"""
        mock_trades = [Trade(id=uuid4(), organization_id=sample_org_id, trade_id=f"TRD-{i:03d}") for i in range(5)]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_trades
        mock_session.execute.return_value = mock_result
        
        trades = await db_manager.get_trades_for_org(mock_session, sample_org_id, limit=5, offset=10)
        
        assert len(trades) == 5
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_trade_success(self, db_manager, mock_session, sample_org_id, sample_trade_data):
        """Test successful trade creation"""
        # Mock the created trade
        mock_trade = Trade(
            id=uuid4(),
            organization_id=sample_org_id,
            trade_id="TRD-20241201-12345678-1234567890",
            **sample_trade_data
        )
        
        # Mock session behavior
        mock_session.add = MagicMock()
        mock_session.refresh.return_value = mock_trade
        
        # Test the method
        created_trade = await db_manager.add_trade(mock_session, sample_trade_data, sample_org_id, "user123")
        
        # Assertions
        assert created_trade is not None
        assert created_trade.organization_id == sample_org_id
        assert created_trade.trade_type == "spot"
        assert created_trade.commodity == "crude_oil"
        assert created_trade.notional_value == 1000.0 * 85.50
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_trade_integrity_error(self, db_manager, mock_session, sample_org_id, sample_trade_data):
        """Test trade creation with integrity error"""
        from sqlalchemy.exc import IntegrityError
        
        # Mock integrity error on commit
        mock_session.commit.side_effect = IntegrityError("statement", "params", "orig")
        
        # Test should raise HTTPException
        with pytest.raises(HTTPException):  # HTTPException from FastAPI
            await db_manager.add_trade(mock_session, sample_trade_data, sample_org_id, "user123")
        
        mock_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_trade_status_success(self, db_manager, mock_session, sample_org_id):
        """Test successful trade status update"""
        # Mock existing trade
        mock_trade = Trade(
            id=uuid4(),
            organization_id=sample_org_id,
            trade_id="TRD-001",
            status="captured"
        )
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_trade
        mock_session.execute.return_value = mock_result
        
        # Test the method
        updated_trade = await db_manager.update_trade_status(
            mock_session, "TRD-001", sample_org_id, "confirmed", "user123"
        )
        
        # Assertions
        assert updated_trade.status == "confirmed"
        assert updated_trade.updated_by == "user123"
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_trade_status_not_found(self, db_manager, mock_session, sample_org_id):
        """Test trade status update when trade not found"""
        # Mock empty result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Test should raise HTTPException
        with pytest.raises(HTTPException):  # HTTPException from FastAPI
            await db_manager.update_trade_status(
                mock_session, "NONEXISTENT", sample_org_id, "confirmed", "user123"
            )
    
    @pytest.mark.asyncio
    async def test_get_organization_by_id_success(self, db_manager, mock_session):
        """Test successful organization retrieval"""
        org_id = uuid4()
        mock_org = Organization(
            id=org_id,
            name="Test Organization",
            code="TEST",
            organization_type="trading_firm",
            classification="tier1",
            primary_region="US"
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_org
        mock_session.execute.return_value = mock_result
        
        org = await db_manager.get_organization_by_id(mock_session, org_id)
        
        assert org is not None
        assert org.name == "Test Organization"
        assert org.code == "TEST"
    
    @pytest.mark.asyncio
    async def test_get_organization_by_id_not_found(self, db_manager, mock_session):
        """Test organization retrieval when not found"""
        org_id = uuid4()
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        org = await db_manager.get_organization_by_id(mock_session, org_id)
        
        assert org is None
    
    @pytest.mark.asyncio
    async def test_get_trade_analytics_success(self, db_manager, mock_session, sample_org_id):
        """Test successful trade analytics generation"""
        # Mock trades for analytics
        mock_trades = [
            Trade(
                id=uuid4(),
                organization_id=sample_org_id,
                trade_type="spot",
                commodity="crude_oil",
                quantity=1000.0,
                price=85.50,
                notional_value=85500.0,
                status="completed",
                is_islamic_compliant=True
            ),
            Trade(
                id=uuid4(),
                organization_id=sample_org_id,
                trade_type="forward",
                commodity="natural_gas",
                quantity=5000.0,
                price=3.20,
                notional_value=16000.0,
                status="pending",
                is_islamic_compliant=False
            )
        ]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_trades
        mock_session.execute.return_value = mock_result
        
        analytics = await db_manager.get_trade_analytics(mock_session, sample_org_id)
        
        # Assertions
        assert analytics["total_trades"] == 2
        assert analytics["total_notional_value"] == 101500.0
        assert analytics["total_quantity"] == 6000.0
        assert analytics["average_trade_value"] == 50750.0
        assert analytics["islamic_compliant_trades"] == 1
        assert analytics["islamic_compliance_rate"] == 0.5
        assert "status_distribution" in analytics
        assert "commodity_distribution" in analytics
    
    @pytest.mark.asyncio
    async def test_soft_delete_trade_success(self, db_manager, mock_session, sample_org_id):
        """Test successful soft delete of trade"""
        # Mock existing trade
        mock_trade = Trade(
            id=uuid4(),
            organization_id=sample_org_id,
            trade_id="TRD-001",
            is_deleted=False
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_trade
        mock_session.execute.return_value = mock_result
        
        result = await db_manager.soft_delete_trade(
            mock_session, "TRD-001", sample_org_id, "user123"
        )
        
        assert result is True
        assert mock_trade.is_deleted is True
        assert mock_trade.deleted_by == "user123"
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_soft_delete_trade_not_found(self, db_manager, mock_session, sample_org_id):
        """Test soft delete when trade not found"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        result = await db_manager.soft_delete_trade(
            mock_session, "NONEXISTENT", sample_org_id, "user123"
        )
        
        assert result is False

@pytest.mark.asyncio
async def test_integration_10_db_operations():
    """Integration test with 10 database operations as specified in PRD"""
    db_manager = MultiTenantDBManager()
    mock_session = AsyncMock()
    
    # Mock session behavior for all operations
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.refresh = AsyncMock()
    
    org_id = uuid4()
    user_id = "test_user"
    
    # Operation 1: Get organization
    mock_org = Organization(id=org_id, name="Test Org", code="TEST", organization_type="trading_firm", classification="tier1", primary_region="US")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_org
    mock_session.execute.return_value = mock_result
    
    org = await db_manager.get_organization_by_id(mock_session, org_id)
    assert org is not None
    
    # Operations 2-6: Add 5 trades
    for i in range(5):
        trade_data = {
            "trade_type": "spot",
            "commodity": f"commodity_{i}",
            "quantity": 1000.0 + i * 100,
            "price": 85.50 + i * 0.5,
            "counterparty_id": f"CP{i:03d}",
            "delivery_date": datetime.now() + timedelta(days=30),
            "delivery_location": f"Location {i}"
        }
        
        mock_trade = Trade(
            id=uuid4(),
            organization_id=org_id,
            trade_id=f"TRD-{i:03d}",
            trade_type=trade_data["trade_type"],
            commodity=trade_data["commodity"],
            quantity=trade_data["quantity"],
            price=trade_data["price"],
            counterparty_id=trade_data["counterparty_id"],
            delivery_date=trade_data["delivery_date"],
            delivery_location=trade_data["delivery_location"],
            notional_value=trade_data["quantity"] * trade_data["price"]
        )
        mock_session.refresh.return_value = mock_trade
        
        trade = await db_manager.add_trade(mock_session, trade_data, org_id, user_id)
        assert trade is not None
    
    # Operations 7-8: Update 2 trade statuses
    mock_trade = Trade(id=uuid4(), organization_id=org_id, trade_id="TRD-001")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_trade
    mock_session.execute.return_value = mock_result
    
    for status in ["confirmed", "settled"]:
        updated_trade = await db_manager.update_trade_status(
            mock_session, "TRD-001", org_id, status, user_id
        )
        assert updated_trade is not None
    
    # Operation 9: Get trade analytics
    mock_trades = [Trade(id=uuid4(), organization_id=org_id, notional_value=1000.0) for _ in range(3)]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_trades
    mock_session.execute.return_value = mock_result
    
    analytics = await db_manager.get_trade_analytics(mock_session, org_id)
    assert analytics["total_trades"] == 3
    
    # Operation 10: Soft delete a trade
    mock_trade = Trade(id=uuid4(), organization_id=org_id, trade_id="TRD-001", is_deleted=False)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_trade
    mock_session.execute.return_value = mock_result
    
    result = await db_manager.soft_delete_trade(mock_session, "TRD-001", org_id, user_id)
    assert result is True
    
    print("✅ Integration test with 10 database operations completed successfully")

if __name__ == "__main__":
    # Run the integration test
    asyncio.run(test_integration_10_db_operations())
