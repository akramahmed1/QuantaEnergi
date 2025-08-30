import pytest
from datetime import datetime, timedelta
from app.schemas.trade import Trade, TradeCreate, TradeUpdate, TradeResponse, TradeType, EnergyCommodity, TradeStatus

class TestTradeModel:
    """Test Trade model validation and functionality"""
    
    def test_valid_trade_creation(self):
        """Test creating a valid trade"""
        trade_data = {
            "user_id": "user123",
            "trade_type": TradeType.BUY,
            "commodity": EnergyCommodity.CRUDE_OIL,
            "quantity": 1000.0,
            "price_per_unit": 85.50,
            "total_value": 85500.0,
            "region": "US",
            "esg_score": 75.0,
            "compliance_verified": True
        }
        
        trade = Trade(**trade_data)
        assert trade.user_id == "user123"
        assert trade.trade_type == TradeType.BUY
        assert trade.commodity == EnergyCommodity.CRUDE_OIL
        assert trade.quantity == 1000.0
        assert trade.price_per_unit == 85.50
        assert trade.total_value == 85500.0
        assert trade.status == TradeStatus.PENDING
    
    def test_total_value_validation(self):
        """Test total value validation"""
        trade_data = {
            "user_id": "user123",
            "trade_type": TradeType.BUY,
            "commodity": EnergyCommodity.CRUDE_OIL,
            "quantity": 1000.0,
            "price_per_unit": 85.50,
            "total_value": 80000.0,  # Incorrect total
            "region": "US"
        }
        
        with pytest.raises(ValueError, match="Total value.*must equal quantity.*price_per_unit"):
            Trade(**trade_data)
    
    def test_expires_at_validation(self):
        """Test expiration time validation"""
        past_time = datetime.utcnow() - timedelta(hours=1)
        
        trade_data = {
            "user_id": "user123",
            "trade_type": TradeType.BUY,
            "commodity": EnergyCommodity.CRUDE_OIL,
            "quantity": 1000.0,
            "price_per_unit": 85.50,
            "total_value": 85500.0,
            "region": "US",
            "expires_at": past_time
        }
        
        with pytest.raises(ValueError, match="Expiration time must be in the future"):
            Trade(**trade_data)
    
    def test_stop_loss_validation_long_position(self):
        """Test stop loss validation for long positions"""
        trade_data = {
            "user_id": "user123",
            "trade_type": TradeType.BUY,
            "commodity": EnergyCommodity.CRUDE_OIL,
            "quantity": 1000.0,
            "price_per_unit": 85.50,
            "total_value": 85500.0,
            "region": "US",
            "stop_loss": 90.0  # Above entry price for long position
        }
        
        with pytest.raises(ValueError, match="Stop loss for long positions must be below entry price"):
            Trade(**trade_data)
    
    def test_stop_loss_validation_short_position(self):
        """Test stop loss validation for short positions"""
        trade_data = {
            "user_id": "user123",
            "trade_type": TradeType.SHORT,
            "commodity": EnergyCommodity.CRUDE_OIL,
            "quantity": 1000.0,
            "price_per_unit": 85.50,
            "total_value": 85500.0,
            "region": "US",
            "stop_loss": 80.0  # Below entry price for short position
        }
        
        with pytest.raises(ValueError, match="Stop loss for short positions must be above entry price"):
            Trade(**trade_data)
    
    def test_esg_score_validation(self):
        """Test ESG score validation"""
        trade_data = {
            "user_id": "user123",
            "trade_type": TradeType.BUY,
            "commodity": EnergyCommodity.CRUDE_OIL,
            "quantity": 1000.0,
            "price_per_unit": 85.50,
            "total_value": 85500.0,
            "region": "US",
            "esg_score": 150.0  # Invalid ESG score > 100
        }
        
        with pytest.raises(ValueError, match="ensure this value is less than or equal to 100"):
            Trade(**trade_data)
    
    def test_quantity_validation(self):
        """Test quantity validation"""
        trade_data = {
            "user_id": "user123",
            "trade_type": TradeType.BUY,
            "commodity": EnergyCommodity.CRUDE_OIL,
            "quantity": -100.0,  # Negative quantity
            "price_per_unit": 85.50,
            "total_value": -8550.0,
            "region": "US"
        }
        
        with pytest.raises(ValueError, match="ensure this value is greater than 0"):
            Trade(**trade_data)

class TestTradeCreate:
    """Test TradeCreate model"""
    
    def test_trade_create_validation(self):
        """Test TradeCreate validation"""
        trade_create = TradeCreate(
            trade_type=TradeType.BUY,
            commodity=EnergyCommodity.NATURAL_GAS,
            quantity=500.0,
            price_per_unit=3.50,
            region="EU"
        )
        
        assert trade_create.trade_type == TradeType.BUY
        assert trade_create.commodity == EnergyCommodity.NATURAL_GAS
        assert trade_create.quantity == 500.0
        assert trade_create.price_per_unit == 3.50
        assert trade_create.region == "EU"
        assert trade_create.tags == []

class TestTradeUpdate:
    """Test TradeUpdate model"""
    
    def test_trade_update_partial(self):
        """Test partial trade update"""
        trade_update = TradeUpdate(
            stop_loss=80.0,
            notes="Updated stop loss"
        )
        
        assert trade_update.stop_loss == 80.0
        assert trade_update.notes == "Updated stop loss"
        assert trade_update.take_profit is None
        assert trade_update.tags is None

class TestTradeResponse:
    """Test TradeResponse model"""
    
    def test_trade_response_creation(self):
        """Test TradeResponse creation"""
        trade = Trade(
            user_id="user123",
            trade_type=TradeType.BUY,
            commodity=EnergyCommodity.CRUDE_OIL,
            quantity=1000.0,
            price_per_unit=85.50,
            total_value=85500.0,
            region="US"
        )
        
        response = TradeResponse(
            trade=trade,
            message="Trade created successfully"
        )
        
        assert response.trade == trade
        assert response.message == "Trade created successfully"
        assert response.timestamp is not None
