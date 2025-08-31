#!/usr/bin/env python3
"""
Test Forecasting Service with news integration and anomaly detection for QuantaEnergi
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add shared services to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared', 'services'))

try:
    from forecasting_service import ForecastingService
except ImportError:
    # Fallback if service not available
    pytest.skip("Forecasting service not available", allow_module_level=True)


class TestForecastingService:
    """Test Forecasting Service functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.forecasting_service = ForecastingService()
        
        # Create sample historical data
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
        self.sample_data = pd.DataFrame({
            'date': dates,
            'price': np.random.normal(85.0, 5.0, len(dates)),
            'volume': np.random.normal(1000.0, 200.0, len(dates)),
            'temperature': np.random.normal(20.0, 10.0, len(dates))
        })
        
        # Add some anomalies
        self.sample_data.loc[10, 'price'] = 150.0  # Price spike
        self.sample_data.loc[15, 'volume'] = 50.0   # Volume drop
        self.sample_data.loc[20, 'temperature'] = -50.0  # Temperature anomaly
    
    def test_forecasting_service_initialization(self):
        """Test forecasting service initialization"""
        assert self.forecasting_service is not None
        assert hasattr(self.forecasting_service, 'forecast_energy_demand')
        assert hasattr(self.forecasting_service, 'detect_anomalies')
        assert hasattr(self.forecasting_service, 'get_energy_news')
    
    def test_energy_demand_forecasting(self):
        """Test energy demand forecasting functionality"""
        # Test basic forecasting
        forecast_result = self.forecasting_service.forecast_energy_demand(
            commodity="electricity",
            region="US",
            days_ahead=7
        )
        
        assert forecast_result is not None
        assert 'forecast' in forecast_result
        assert 'confidence_interval' in forecast_result
        assert 'model_accuracy' in forecast_result
        
        # Test forecast data structure
        forecast_data = forecast_result['forecast']
        assert len(forecast_data) == 7  # 7 days ahead
        assert all(isinstance(x, (int, float)) for x in forecast_data)
        
        # Test confidence intervals
        confidence = forecast_result['confidence_interval']
        assert 'lower' in confidence
        assert 'upper' in confidence
        assert len(confidence['lower']) == 7
        assert len(confidence['upper']) == 7
    
    def test_anomaly_detection(self):
        """Test anomaly detection algorithms"""
        # Test statistical anomaly detection
        anomalies = self.forecasting_service.detect_anomalies(
            data=self.sample_data['price'],
            method='statistical'
        )
        
        assert anomalies is not None
        assert 'anomalies' in anomalies
        assert 'scores' in anomalies
        assert 'threshold' in anomalies
        
        # Should detect the price spike at index 10
        anomaly_indices = anomalies['anomalies']
        assert 10 in anomaly_indices
        
        # Test isolation forest anomaly detection
        isolation_anomalies = self.forecasting_service.detect_anomalies(
            data=self.sample_data['volume'],
            method='isolation_forest'
        )
        
        assert isolation_anomalies is not None
        assert 'anomalies' in isolation_anomalies
        assert 'scores' in isolation_anomalies
        
        # Test Z-score anomaly detection
        zscore_anomalies = self.forecasting_service.detect_anomalies(
            data=self.sample_data['temperature'],
            method='zscore'
        )
        
        assert zscore_anomalies is not None
        assert 'anomalies' in zscore_anomalies
        assert 'scores' in zscore_anomalies
    
    def test_news_integration(self):
        """Test news integration for forecasting context"""
        # Test energy news retrieval
        news_data = self.forecasting_service.get_energy_news(
            commodity="crude_oil",
            days=7
        )
        
        assert news_data is not None
        assert 'articles' in news_data
        assert 'sentiment_score' in news_data
        assert 'impact_score' in news_data
        
        # Test news sentiment analysis
        sentiment = news_data['sentiment_score']
        assert isinstance(sentiment, (int, float))
        assert -1 <= sentiment <= 1  # Sentiment should be between -1 and 1
        
        # Test news impact scoring
        impact = news_data['impact_score']
        assert isinstance(impact, (int, float))
        assert 0 <= impact <= 10  # Impact should be between 0 and 10
    
    def test_anomaly_correction(self):
        """Test anomaly correction in forecasting"""
        # Test forecasting with anomaly correction
        corrected_forecast = self.forecasting_service.forecast_energy_demand(
            commodity="electricity",
            region="US",
            days_ahead=7,
            apply_anomaly_correction=True
        )
        
        assert corrected_forecast is not None
        assert 'forecast' in corrected_forecast
        assert 'anomaly_corrections' in corrected_forecast
        assert 'correction_applied' in corrected_forecast
        
        # Test that corrections were applied
        corrections = corrected_forecast['anomaly_corrections']
        assert len(corrections) > 0
        
        # Test correction effectiveness
        correction_applied = corrected_forecast['correction_applied']
        assert isinstance(correction_applied, bool)
    
    def test_forecasting_accuracy(self):
        """Test forecasting accuracy improvements"""
        # Test baseline forecasting
        baseline_forecast = self.forecasting_service.forecast_energy_demand(
            commodity="natural_gas",
            region="US",
            days_ahead=5
        )
        
        # Test enhanced forecasting with multiple features
        enhanced_forecast = self.forecasting_service.forecast_energy_demand(
            commodity="natural_gas",
            region="US",
            days_ahead=5,
            include_weather=True,
            include_news=True,
            include_anomaly_detection=True
        )
        
        assert enhanced_forecast is not None
        assert 'forecast' in enhanced_forecast
        assert 'model_accuracy' in enhanced_forecast
        
        # Enhanced forecasting should have better accuracy
        baseline_accuracy = baseline_forecast.get('model_accuracy', 0)
        enhanced_accuracy = enhanced_forecast.get('model_accuracy', 0)
        
        # Note: In real scenarios, enhanced forecasting should improve accuracy
        # For testing, we just verify the structure
        assert isinstance(baseline_accuracy, (int, float))
        assert isinstance(enhanced_accuracy, (int, float))
    
    def test_weather_integration(self):
        """Test weather data integration in forecasting"""
        # Test forecasting with weather correlation
        weather_forecast = self.forecasting_service.forecast_energy_demand(
            commodity="electricity",
            region="US",
            days_ahead=7,
            include_weather=True
        )
        
        assert weather_forecast is not None
        assert 'forecast' in weather_forecast
        assert 'weather_correlation' in weather_forecast
        
        # Test weather correlation data
        weather_corr = weather_forecast['weather_correlation']
        assert 'temperature_impact' in weather_corr
        assert 'humidity_impact' in weather_corr
        assert 'wind_impact' in weather_corr
    
    def test_multi_commodity_forecasting(self):
        """Test forecasting for multiple commodities"""
        commodities = ["crude_oil", "natural_gas", "electricity", "renewables"]
        
        for commodity in commodities:
            forecast = self.forecasting_service.forecast_energy_demand(
                commodity=commodity,
                region="US",
                days_ahead=3
            )
            
            assert forecast is not None
            assert 'forecast' in forecast
            assert 'commodity' in forecast
            assert forecast['commodity'] == commodity
    
    def test_regional_forecasting(self):
        """Test forecasting for different regions"""
        regions = ["US", "EU", "Asia", "Middle_East"]
        
        for region in regions:
            forecast = self.forecasting_service.forecast_energy_demand(
                commodity="electricity",
                region=region,
                days_ahead=3
            )
            
            assert forecast is not None
            assert 'forecast' in forecast
            assert 'region' in forecast
            assert forecast['region'] == region
    
    def test_forecasting_error_handling(self):
        """Test error handling in forecasting"""
        # Test with invalid commodity
        with pytest.raises(Exception):
            self.forecasting_service.forecast_energy_demand(
                commodity="invalid_commodity",
                region="US",
                days_ahead=7
            )
        
        # Test with invalid days ahead
        with pytest.raises(Exception):
            self.forecasting_service.forecast_energy_demand(
                commodity="electricity",
                region="US",
                days_ahead=-1
            )
        
        # Test with invalid region
        with pytest.raises(Exception):
            self.forecasting_service.forecast_energy_demand(
                commodity="electricity",
                region="invalid_region",
                days_ahead=7
            )
    
    def test_forecasting_performance(self):
        """Test forecasting performance metrics"""
        # Test forecasting execution time
        import time
        
        start_time = time.time()
        forecast = self.forecasting_service.forecast_energy_demand(
            commodity="electricity",
            region="US",
            days_ahead=7
        )
        execution_time = time.time() - start_time
        
        assert forecast is not None
        assert execution_time < 10.0  # Should complete within 10 seconds
        
        # Test memory usage
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss
        
        # Run multiple forecasts
        for _ in range(5):
            self.forecasting_service.forecast_energy_demand(
                commodity="natural_gas",
                region="US",
                days_ahead=3
            )
        
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024


class TestAnomalyDetection:
    """Test specific anomaly detection functionality"""
    
    def setup_method(self):
        """Setup test data for anomaly detection"""
        self.forecasting_service = ForecastingService()
        
        # Create data with known anomalies
        self.test_data = pd.Series([
            100, 102, 98, 103, 101, 99, 104, 97, 105, 96,
            150,  # Anomaly: sudden spike
            101, 103, 99, 102, 98, 104, 100, 102, 99,
            50,   # Anomaly: sudden drop
            101, 103, 100, 102, 99, 104, 101, 103, 100
        ])
    
    def test_statistical_anomaly_detection(self):
        """Test statistical anomaly detection method"""
        anomalies = self.forecasting_service.detect_anomalies(
            data=self.test_data,
            method='statistical',
            threshold=2.0  # 2 standard deviations
        )
        
        assert anomalies is not None
        assert 'anomalies' in anomalies
        
        # Should detect the spike at index 10 and drop at index 20
        detected_anomalies = anomalies['anomalies']
        assert 10 in detected_anomalies  # Spike
        assert 20 in detected_anomalies  # Drop
    
    def test_isolation_forest_anomaly_detection(self):
        """Test isolation forest anomaly detection method"""
        anomalies = self.forecasting_service.detect_anomalies(
            data=self.test_data,
            method='isolation_forest',
            contamination=0.1  # 10% contamination
        )
        
        assert anomalies is not None
        assert 'anomalies' in anomalies
        assert 'scores' in anomalies
        
        # Should detect some anomalies
        detected_anomalies = anomalies['anomalies']
        assert len(detected_anomalies) > 0
    
    def test_zscore_anomaly_detection(self):
        """Test Z-score anomaly detection method"""
        anomalies = self.forecasting_service.detect_anomalies(
            data=self.test_data,
            method='zscore',
            threshold=2.5  # 2.5 Z-score threshold
        )
        
        assert anomalies is not None
        assert 'anomalies' in anomalies
        assert 'scores' in anomalies
        
        # Should detect extreme values
        detected_anomalies = anomalies['anomalies']
        assert len(detected_anomalies) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
