"""
Test suite for analytics services
Tests forecasting, quantum optimization, and blockchain services
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from app.services.forecasting_service import ForecastingService
from app.services.quantum_optimization_service import QuantumOptimizationService
from app.services.blockchain_service import BlockchainService

class TestForecastingService:
    """Test cases for AI forecasting service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = ForecastingService()
    
    def test_generate_mock_data(self):
        """Test mock data generation"""
        data = self.service.generate_mock_data(periods=100)
        
        assert isinstance(data, pd.DataFrame)
        assert 'ds' in data.columns
        assert 'y' in data.columns
        assert len(data) == 100
        
        # Check that dates are properly formatted
        assert pd.api.types.is_datetime64_any_dtype(data['ds'])
        
        # Check that prices are numeric
        assert pd.api.types.is_numeric_dtype(data['y'])
        assert data['y'].min() > 0  # Prices should be positive
    
    def test_train_model(self):
        """Test Prophet model training"""
        data = self.service.generate_mock_data(periods=100)
        self.service.train_model(data)
        
        assert self.service.model is not None
        assert self.service.df is not None
        assert len(self.service.df) == 100
    
    def test_predict_prices(self):
        """Test price prediction"""
        data = self.service.generate_mock_data(periods=100)
        self.service.train_model(data)
        
        result = self.service.predict_prices(periods=30)
        
        assert 'forecast' in result
        assert 'periods' in result
        assert 'unit' in result
        
        assert result['periods'] == 30
        assert result['unit'] == 'USD/MWh'
        assert len(result['forecast']) == 30
        
        # Check forecast structure
        forecast = result['forecast'][0]
        assert 'ds' in forecast
        assert 'yhat' in forecast
        assert 'yhat_lower' in forecast
        assert 'yhat_upper' in forecast
    
    def test_get_market_insights(self):
        """Test market insights generation"""
        # Create mock forecast data
        forecast_data = [
            {'yhat': 50.0, 'yhat_lower': 45.0, 'yhat_upper': 55.0},
            {'yhat': 55.0, 'yhat_lower': 50.0, 'yhat_upper': 60.0},
            {'yhat': 60.0, 'yhat_lower': 55.0, 'yhat_upper': 65.0}
        ]
        
        result = self.service.get_market_insights(forecast_data)
        
        assert 'sentiment' in result
        assert 'risk_level' in result
        assert 'recommendation' in result
        assert 'price_change_percentage' in result
        
        assert result['sentiment'] in ['Bullish', 'Bearish', 'Neutral']
        assert result['risk_level'] in ['Low', 'Medium', 'High']
        assert isinstance(result['price_change_percentage'], str)
    
    def test_empty_forecast_data_insights(self):
        """Test market insights with empty forecast data"""
        result = self.service.get_market_insights([])
        
        assert result['sentiment'] == 'Neutral'
        assert result['risk_level'] == 'Low'
        assert result['recommendation'] == 'Monitor market'
    
    def test_forecast_without_trained_model(self):
        """Test prediction without trained model"""
        with pytest.raises(ValueError, match="Model not trained"):
            self.service.predict_prices(periods=30)

class TestQuantumOptimizationService:
    """Test cases for quantum optimization service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = QuantumOptimizationService()
    
    def test_classical_portfolio_optimization(self):
        """Test classical portfolio optimization fallback"""
        returns = [0.1, 0.05, 0.08]
        volatilities = [0.2, 0.1, 0.15]
        budget = 1.0
        
        result = self.service._classical_portfolio_optimization(returns, volatilities, budget)
        
        assert 'optimized_weights' in result
        assert 'expected_return' in result
        assert 'expected_volatility' in result
        assert 'method' in result
        
        assert len(result['optimized_weights']) == 3
        assert abs(sum(result['optimized_weights']) - 1.0) < 0.01  # Should sum to 1
        assert result['method'] == 'Classical (Equal Weight)'
    
    def test_optimize_portfolio(self):
        """Test portfolio optimization"""
        returns = [0.1, 0.05, 0.08]
        volatilities = [0.2, 0.1, 0.15]
        budget = 1.0
        
        result = self.service.optimize_portfolio(returns, volatilities, budget)
        
        assert 'optimized_weights' in result
        assert 'expected_return' in result
        assert 'expected_volatility' in result
        assert 'method' in result
        
        assert len(result['optimized_weights']) == 3
        assert isinstance(result['expected_return'], (int, float))
        assert isinstance(result['expected_volatility'], (int, float))
    
    def test_optimize_portfolio_empty_assets(self):
        """Test portfolio optimization with empty assets"""
        result = self.service.optimize_portfolio([], [], 1.0)
        
        assert result['optimized_weights'] == []
        assert result['expected_return'] == 0.0
        assert result['expected_volatility'] == 0.0
        assert result['method'] == 'Classical (No Assets)'
    
    def test_optimize_trading_strategy(self):
        """Test trading strategy optimization"""
        historical_data = [
            {'price': 50.0, 'volume': 1000, 'timestamp': '2024-01-01'},
            {'price': 55.0, 'volume': 1200, 'timestamp': '2024-01-02'},
            {'price': 52.0, 'volume': 1100, 'timestamp': '2024-01-03'}
        ]
        
        result = self.service.optimize_trading_strategy(historical_data)
        
        assert 'optimized_strategy_parameters' in result
        assert 'performance_metrics' in result
        assert 'method' in result
        
        strategy_params = result['optimized_strategy_parameters']
        assert 'moving_average_period' in strategy_params
        assert 'rsi_threshold_buy' in strategy_params
        assert 'rsi_threshold_sell' in strategy_params
        assert 'sharpe_ratio' in strategy_params
        assert 'win_rate' in strategy_params
        
        performance = result['performance_metrics']
        assert 'sharpe_ratio' in performance
        assert 'win_rate' in performance
        assert 'total_trades' in performance

class TestBlockchainService:
    """Test cases for blockchain service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = BlockchainService()
    
    def test_create_carbon_trade(self):
        """Test carbon trade creation"""
        buyer_address = '0xBuyer123'
        seller_address = '0xSeller456'
        carbon_amount = 100.0
        price = 25.5
        
        result = self.service.create_carbon_trade(
            buyer_address, seller_address, carbon_amount, price
        )
        
        assert 'trade_id' in result
        assert 'buyer_address' in result
        assert 'seller_address' in result
        assert 'carbon_amount' in result
        assert 'price' in result
        assert 'currency' in result
        assert 'timestamp' in result
        assert 'status' in result
        assert 'transaction_hash' in result
        
        assert result['buyer_address'] == buyer_address
        assert result['seller_address'] == seller_address
        assert result['carbon_amount'] == carbon_amount
        assert result['price'] == price
        assert result['status'] == 'pending'
        assert result['currency'] == 'USD'
    
    def test_get_carbon_trade(self):
        """Test carbon trade retrieval"""
        # First create a trade
        trade = self.service.create_carbon_trade(
            '0xBuyer123', '0xSeller456', 100.0, 25.5
        )
        
        # Then retrieve it
        result = self.service.get_carbon_trade(trade['trade_id'])
        
        assert result is not None
        assert result['trade_id'] == trade['trade_id']
        assert result['buyer_address'] == '0xBuyer123'
        assert result['seller_address'] == '0xSeller456'
    
    def test_get_nonexistent_carbon_trade(self):
        """Test retrieval of non-existent carbon trade"""
        result = self.service.get_carbon_trade('nonexistent-trade-id')
        assert result is None
    
    def test_settle_carbon_trade(self):
        """Test carbon trade settlement"""
        # First create a trade
        trade = self.service.create_carbon_trade(
            '0xBuyer123', '0xSeller456', 100.0, 25.5
        )
        
        # Then settle it
        result = self.service.settle_carbon_trade(trade['trade_id'])
        
        assert result['status'] == 'settled'
        assert 'settlement_timestamp' in result
        assert 'settlement_hash' in result
        assert result['trade_id'] == trade['trade_id']
    
    def test_settle_nonexistent_carbon_trade(self):
        """Test settlement of non-existent carbon trade"""
        with pytest.raises(ValueError, match="Carbon trade not found"):
            self.service.settle_carbon_trade('nonexistent-trade-id')
    
    def test_settle_already_settled_trade(self):
        """Test settlement of already settled trade"""
        # Create and settle a trade
        trade = self.service.create_carbon_trade(
            '0xBuyer123', '0xSeller456', 100.0, 25.5
        )
        self.service.settle_carbon_trade(trade['trade_id'])
        
        # Try to settle again
        result = self.service.settle_carbon_trade(trade['trade_id'])
        assert result['status'] == 'settled'
    
    def test_get_esg_score(self):
        """Test ESG score retrieval"""
        company_address = 'companyA_address'
        result = self.service.get_esg_score(company_address)
        
        assert result is not None
        assert 'score' in result
        assert 'last_updated' in result
        assert 'details' in result
        
        assert isinstance(result['score'], int)
        assert 0 <= result['score'] <= 100
    
    def test_get_nonexistent_esg_score(self):
        """Test retrieval of non-existent ESG score"""
        result = self.service.get_esg_score('nonexistent-company')
        assert result is None
    
    def test_web3_availability(self):
        """Test Web3 availability detection"""
        assert hasattr(self.service, 'has_web3')
        assert isinstance(self.service.has_web3, bool)
    
    def test_carbon_trades_database(self):
        """Test carbon trades database functionality"""
        # Create multiple trades
        trade1 = self.service.create_carbon_trade(
            '0xBuyer1', '0xSeller1', 50.0, 20.0
        )
        trade2 = self.service.create_carbon_trade(
            '0xBuyer2', '0xSeller2', 75.0, 30.0
        )
        
        # Verify both trades exist
        retrieved1 = self.service.get_carbon_trade(trade1['trade_id'])
        retrieved2 = self.service.get_carbon_trade(trade2['trade_id'])
        
        assert retrieved1 is not None
        assert retrieved2 is not None
        assert retrieved1['trade_id'] != retrieved2['trade_id']

if __name__ == '__main__':
    pytest.main([__file__])
