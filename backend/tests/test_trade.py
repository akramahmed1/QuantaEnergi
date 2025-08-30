import pytest
from datetime import datetime, timedelta
from app.schemas.trade import (
    Trade, TradeCreate, TradeUpdate, TradeResponse,
    TradeType, EnergyCommodity, TradeStatus
)

class TestTradeModel:
    """Test Trade Pydantic model validation"""
    
    def test_valid_trade_creation(self):
        """Test creating a valid trade"""
        trade_data = {
            "user_id": 1,
            "trade_type": TradeType.BUY,
            "commodity": EnergyCommodity.CRUDE_OIL,
            "quantity": 1000.0,
            "price_per_unit": 85.50,
            "total_value": 85500.0,
            "expires_at": datetime.now() + timedelta(hours=24),
            "stop_loss": 80.0,
            "take_profit": 90.0,
            "esg_score": 75.0
        }
        
        trade = Trade(**trade_data)
        assert trade.user_id == 1
        assert trade.trade_type == TradeType.BUY
        assert trade.commodity == EnergyCommodity.CRUDE_OIL
        assert trade.quantity == 1000.0
        assert trade.price_per_unit == 85.50
        assert trade.total_value == 85500.0
        assert trade.esg_score == 75.0
    
    def test_total_value_validation(self):
        """Test total value calculation validation"""
        trade_data = {
            "user_id": 1,
            "trade_type": TradeType.SELL,
            "commodity": EnergyCommodity.NATURAL_GAS,
            "quantity": 500.0,
            "price_per_unit": 3.20,
            "total_value": 1600.0,  # Should match quantity * price_per_unit
            "expires_at": datetime.now() + timedelta(hours=12)
        }
        
        trade = Trade(**trade_data)
        expected_total = trade.quantity * trade.price_per_unit
        assert trade.total_value == expected_total
    
    def test_expiration_time_validation(self):
        """Test expiration time validation"""
        # Valid: expires in the future
        future_time = datetime.now() + timedelta(hours=1)
        trade_data = {
            "user_id": 1,
            "trade_type": TradeType.BUY,
            "commodity": EnergyCommodity.COAL,
            "quantity": 100.0,
            "price_per_unit": 50.0,
            "total_value": 5000.0,
            "expires_at": future_time
        }
        
        trade = Trade(**trade_data)
        assert trade.expires_at == future_time
        
        # Invalid: expires in the past
        past_time = datetime.now() - timedelta(hours=1)
        trade_data["expires_at"] = past_time
        
        with pytest.raises(ValueError, match="expires_at must be in the future"):
            Trade(**trade_data)
    
    def test_stop_loss_take_profit_logic(self):
        """Test stop loss and take profit validation"""
        # Valid: stop loss < current price < take profit
        trade_data = {
            "user_id": 1,
            "trade_type": TradeType.BUY,
            "commodity": EnergyCommodity.ELECTRICITY,
            "quantity": 200.0,
            "price_per_unit": 100.0,
            "total_value": 20000.0,
            "expires_at": datetime.now() + timedelta(hours=6),
            "stop_loss": 95.0,
            "take_profit": 105.0
        }
        
        trade = Trade(**trade_data)
        assert trade.stop_loss == 95.0
        assert trade.take_profit == 105.0
        
        # Invalid: stop loss > take profit
        trade_data["stop_loss"] = 110.0
        trade_data["take_profit"] = 105.0
        
        with pytest.raises(ValueError, match="stop_loss must be less than take_profit"):
            Trade(**trade_data)
    
    def test_esg_score_validation(self):
        """Test ESG score validation"""
        # Valid ESG score
        trade_data = {
            "user_id": 1,
            "trade_type": TradeType.BUY,
            "commodity": EnergyCommodity.RENEWABLES,
            "quantity": 100.0,
            "price_per_unit": 120.0,
            "total_value": 12000.0,
            "expires_at": datetime.now() + timedelta(hours=24),
            "esg_score": 85.0
        }
        
        trade = Trade(**trade_data)
        assert trade.esg_score == 85.0
        
        # Invalid ESG score (out of range)
        trade_data["esg_score"] = 150.0
        
        with pytest.raises(ValueError, match="esg_score must be between 0 and 100"):
            Trade(**trade_data)
    
    def test_quantity_validation(self):
        """Test quantity validation"""
        # Valid quantity
        trade_data = {
            "user_id": 1,
            "trade_type": TradeType.SELL,
            "commodity": EnergyCommodity.NATURAL_GAS,
            "quantity": 1000.0,
            "price_per_unit": 3.50,
            "total_value": 3500.0,
            "expires_at": datetime.now() + timedelta(hours=12)
        }
        
        trade = Trade(**trade_data)
        assert trade.quantity == 1000.0
        
        # Invalid: negative quantity
        trade_data["quantity"] = -100.0
        
        with pytest.raises(ValueError, match="quantity must be positive"):
            Trade(**trade_data)

class TestTradeCreate:
    """Test TradeCreate schema"""
    
    def test_trade_create_validation(self):
        """Test TradeCreate validation"""
        trade_create_data = {
            "trade_type": TradeType.BUY,
            "commodity": EnergyCommodity.CRUDE_OIL,
            "quantity": 500.0,
            "price_per_unit": 87.50,
            "expires_at": datetime.now() + timedelta(hours=24)
        }
        
        trade_create = TradeCreate(**trade_create_data)
        assert trade_create.trade_type == TradeType.BUY
        assert trade_create.commodity == EnergyCommodity.CRUDE_OIL
        assert trade_create.quantity == 500.0

class TestTradeUpdate:
    """Test TradeUpdate schema"""
    
    def test_trade_update_partial(self):
        """Test partial trade updates"""
        trade_update_data = {
            "stop_loss": 85.0,
            "take_profit": 90.0
        }
        
        trade_update = TradeUpdate(**trade_update_data)
        assert trade_update.stop_loss == 85.0
        assert trade_update.take_profit == 90.0
        assert trade_update.trade_type is None  # Not updated

class TestTradeResponse:
    """Test TradeResponse schema"""
    
    def test_trade_response_creation(self):
        """Test TradeResponse creation"""
        trade_response_data = {
            "id": 1,
            "user_id": 1,
            "trade_type": TradeType.BUY,
            "commodity": EnergyCommodity.CRUDE_OIL,
            "quantity": 1000.0,
            "price_per_unit": 85.50,
            "total_value": 85500.0,
            "status": TradeStatus.PENDING,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        trade_response = TradeResponse(**trade_response_data)
        assert trade_response.id == 1
        assert trade_response.status == TradeStatus.PENDING
        assert trade_response.total_value == 85500.0

class TestEnums:
    """Test enum values"""
    
    def test_trade_types(self):
        """Test TradeType enum values"""
        assert TradeType.BUY.value == "buy"
        assert TradeType.SELL.value == "sell"
        assert TradeType.SHORT.value == "short"
        assert TradeType.COVER.value == "cover"
    
    def test_energy_commodities(self):
        """Test EnergyCommodity enum values"""
        assert EnergyCommodity.CRUDE_OIL.value == "crude_oil"
        assert EnergyCommodity.NATURAL_GAS.value == "natural_gas"
        assert EnergyCommodity.COAL.value == "coal"
        assert EnergyCommodity.RENEWABLES.value == "renewables"
        assert EnergyCommodity.ELECTRICITY.value == "electricity"
    
    def test_trade_statuses(self):
        """Test TradeStatus enum values"""
        assert TradeStatus.PENDING.value == "pending"
        assert TradeStatus.EXECUTED.value == "executed"
        assert TradeStatus.CANCELLED.value == "cancelled"
        assert TradeStatus.EXPIRED.value == "expired"
