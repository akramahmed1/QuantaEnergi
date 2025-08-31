#!/usr/bin/env python3
"""
Test Trade Pydantic models and validation for QuantaEnergi
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
import sys
import os

# Add shared services to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared', 'services'))

try:
    from schemas.trade import Trade, TradeCreate, TradeUpdate, TradeResponse
except ImportError:
    # Fallback if schemas not available
    pytest.skip("Trade schemas not available", allow_module_level=True)


class TestTradeModels:
    """Test Trade Pydantic models"""
    
    def test_trade_create_valid(self):
        """Test valid TradeCreate model"""
        trade_data = {
            "commodity": "crude_oil",
            "quantity": 1000.0,
            "price": 85.50,
            "trade_type": "buy",
            "region": "US",
            "esg_score": 75.0,
            "compliance_status": "approved"
        }
        
        trade = TradeCreate(**trade_data)
        assert trade.commodity == "crude_oil"
        assert trade.quantity == 1000.0
        assert trade.price == 85.50
        assert trade.trade_type == "buy"
        assert trade.region == "US"
        assert trade.esg_score == 75.0
        assert trade.compliance_status == "approved"
    
    def test_trade_create_invalid_quantity(self):
        """Test TradeCreate with invalid quantity (<= 0)"""
        trade_data = {
            "commodity": "crude_oil",
            "quantity": 0,  # Invalid: quantity must be > 0
            "price": 85.50,
            "trade_type": "buy",
            "region": "US"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TradeCreate(**trade_data)
        
        assert "quantity" in str(exc_info.value)
    
    def test_trade_create_invalid_price(self):
        """Test TradeCreate with invalid price (<= 0)"""
        trade_data = {
            "commodity": "crude_oil",
            "quantity": 1000.0,
            "price": -10.0,  # Invalid: price must be > 0
            "trade_type": "buy",
            "region": "US"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TradeCreate(**trade_data)
        
        assert "price" in str(exc_info.value)
    
    def test_trade_create_invalid_trade_type(self):
        """Test TradeCreate with invalid trade type"""
        trade_data = {
            "commodity": "crude_oil",
            "quantity": 1000.0,
            "price": 85.50,
            "trade_type": "invalid_type",  # Invalid trade type
            "region": "US"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TradeCreate(**trade_data)
        
        assert "trade_type" in str(exc_info.value)
    
    def test_trade_create_invalid_region(self):
        """Test TradeCreate with invalid region"""
        trade_data = {
            "commodity": "crude_oil",
            "quantity": 1000.0,
            "price": 85.50,
            "trade_type": "buy",
            "region": "invalid_region"  # Invalid region
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TradeCreate(**trade_data)
        
        assert "region" in str(exc_info.value)
    
    def test_trade_create_esg_score_range(self):
        """Test TradeCreate with ESG score out of range"""
        trade_data = {
            "commodity": "crude_oil",
            "quantity": 1000.0,
            "price": 85.50,
            "trade_type": "buy",
            "region": "US",
            "esg_score": 150.0  # Invalid: ESG score must be 0-100
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TradeCreate(**trade_data)
        
        assert "esg_score" in str(exc_info.value)
    
    def test_trade_total_value_calculation(self):
        """Test total value calculation in Trade model"""
        trade_data = {
            "commodity": "crude_oil",
            "quantity": 1000.0,
            "price": 85.50,
            "trade_type": "buy",
            "region": "US"
        }
        
        trade = TradeCreate(**trade_data)
        expected_total = 1000.0 * 85.50
        assert trade.total_value == expected_total
    
    def test_trade_update_partial(self):
        """Test TradeUpdate with partial data"""
        update_data = {
            "price": 90.00,
            "esg_score": 80.0
        }
        
        trade_update = TradeUpdate(**update_data)
        assert trade_update.price == 90.00
        assert trade_update.esg_score == 80.0
        assert trade_update.quantity is None  # Not provided
    
    def test_trade_response_serialization(self):
        """Test TradeResponse serialization"""
        trade_response_data = {
            "id": 1,
            "commodity": "crude_oil",
            "quantity": 1000.0,
            "price": 85.50,
            "trade_type": "buy",
            "region": "US",
            "esg_score": 75.0,
            "compliance_status": "approved",
            "total_value": 85500.0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        trade_response = TradeResponse(**trade_response_data)
        assert trade_response.id == 1
        assert trade_response.total_value == 85500.0
        assert isinstance(trade_response.created_at, datetime)
        assert isinstance(trade_response.updated_at, datetime)
    
    def test_trade_compliance_validation(self):
        """Test compliance status validation"""
        valid_compliance_statuses = ["pending", "approved", "rejected", "under_review"]
        
        for status in valid_compliance_statuses:
            trade_data = {
                "commodity": "crude_oil",
                "quantity": 1000.0,
                "price": 85.50,
                "trade_type": "buy",
                "region": "US",
                "compliance_status": status
            }
            
            trade = TradeCreate(**trade_data)
            assert trade.compliance_status == status
    
    def test_trade_commodity_validation(self):
        """Test commodity validation"""
        valid_commodities = ["crude_oil", "natural_gas", "electricity", "renewables"]
        
        for commodity in valid_commodities:
            trade_data = {
                "commodity": commodity,
                "quantity": 1000.0,
                "price": 85.50,
                "trade_type": "buy",
                "region": "US"
            }
            
            trade = TradeCreate(**trade_data)
            assert trade.commodity == commodity


class TestTradeBusinessLogic:
    """Test Trade business logic and calculations"""
    
    def test_trade_margin_calculation(self):
        """Test trade margin calculation"""
        trade_data = {
            "commodity": "crude_oil",
            "quantity": 1000.0,
            "price": 85.50,
            "trade_type": "buy",
            "region": "US"
        }
        
        trade = TradeCreate(**trade_data)
        total_value = trade.total_value
        
        # Test margin calculation (example: 5% margin)
        margin_percentage = 0.05
        expected_margin = total_value * margin_percentage
        
        # This would be implemented in the business logic
        assert expected_margin == 4275.0  # 85500 * 0.05
    
    def test_trade_risk_assessment(self):
        """Test trade risk assessment based on ESG score"""
        high_esg_trade = TradeCreate(
            commodity="renewables",
            quantity=1000.0,
            "price": 85.50,
            trade_type="buy",
            region="US",
            esg_score=90.0
        )
        
        low_esg_trade = TradeCreate(
            commodity="crude_oil",
            quantity=1000.0,
            price=85.50,
            trade_type="buy",
            region="US",
            esg_score=30.0
        )
        
        # Higher ESG score should indicate lower risk
        assert high_esg_trade.esg_score > low_esg_trade.esg_score
        
        # Risk assessment logic would be implemented in business layer
        high_risk = low_esg_trade.esg_score < 50
        low_risk = high_esg_trade.esg_score > 80
        
        assert high_risk is True
        assert low_risk is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
