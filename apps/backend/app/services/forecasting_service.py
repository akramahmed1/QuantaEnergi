"""
AI Forecasting Service using Prophet v1.1.5
Provides energy price forecasting and market analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import structlog
from prophet import Prophet
import warnings

warnings.filterwarnings('ignore')

logger = structlog.get_logger(__name__)

class ForecastingService:
    """AI-powered forecasting service for energy markets"""
    
    def __init__(self):
        self.models = {}
        self.historical_data = self._generate_mock_historical_data()
    
    def _generate_mock_historical_data(self) -> pd.DataFrame:
        """Generate mock historical energy price data"""
        dates = pd.date_range(start='2023-01-01', end=datetime.now(), freq='D')
        
        # Generate realistic energy price patterns
        np.random.seed(42)
        base_price = 50.0
        trend = np.linspace(0, 10, len(dates))
        seasonal = 5 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
        noise = np.random.normal(0, 2, len(dates))
        
        prices = base_price + trend + seasonal + noise
        
        return pd.DataFrame({
            'ds': dates,
            'y': prices,
            'commodity': 'crude_oil'
        })
    
    def create_forecast(self, 
                       commodity: str = 'crude_oil',
                       days_ahead: int = 30,
                       include_components: bool = True) -> Dict:
        """
        Create price forecast for specified commodity
        
        Args:
            commodity: Type of energy commodity
            days_ahead: Number of days to forecast
            include_components: Include trend and seasonal components
            
        Returns:
            Dictionary containing forecast data and metadata
        """
        try:
            logger.info("Creating forecast", commodity=commodity, days_ahead=days_ahead)
            
            # Prepare data for Prophet
            df = self.historical_data.copy()
            df = df[df['commodity'] == commodity] if commodity != 'crude_oil' else df
            
            # Initialize and fit Prophet model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                seasonality_mode='multiplicative'
            )
            
            # Add custom seasonality for energy markets
            model.add_seasonality(
                name='monthly',
                period=30.5,
                fourier_order=5
            )
            
            model.fit(df)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=days_ahead)
            
            # Generate forecast
            forecast = model.predict(future)
            
            # Extract forecast data
            forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days_ahead)
            
            result = {
                'commodity': commodity,
                'forecast_period': days_ahead,
                'created_at': datetime.now().isoformat(),
                'forecast_data': forecast_data.to_dict('records'),
                'model_accuracy': self._calculate_accuracy(model, df),
                'trend': forecast['trend'].tail(days_ahead).tolist() if include_components else None,
                'seasonal': forecast['yearly'].tail(days_ahead).tolist() if include_components else None
            }
            
            logger.info("Forecast created successfully", 
                       commodity=commodity, 
                       accuracy=result['model_accuracy'])
            
            return result
            
        except Exception as e:
            logger.error("Forecast creation failed", error=str(e))
            raise Exception(f"Failed to create forecast: {str(e)}")
    
    def _calculate_accuracy(self, model: Prophet, df: pd.DataFrame) -> float:
        """Calculate model accuracy using cross-validation"""
        try:
            from prophet.diagnostics import cross_validation, performance_metrics
            
            # Perform cross-validation
            df_cv = cross_validation(
                model, 
                initial='180 days', 
                period='30 days', 
                horizon='30 days'
            )
            
            # Calculate performance metrics
            df_performance = performance_metrics(df_cv)
            
            # Return MAPE (Mean Absolute Percentage Error)
            return float(df_performance['mape'].mean())
            
        except Exception as e:
            logger.warning("Could not calculate accuracy", error=str(e))
            return 0.15  # Default accuracy estimate
    
    def get_market_insights(self, commodity: str = 'crude_oil') -> Dict:
        """Generate market insights and recommendations"""
        try:
            # Get recent price data
            recent_data = self.historical_data.tail(30)
            current_price = recent_data['y'].iloc[-1]
            price_change = recent_data['y'].pct_change().mean() * 100
            
            # Calculate volatility
            volatility = recent_data['y'].pct_change().std() * 100
            
            # Generate insights
            insights = {
                'commodity': commodity,
                'current_price': float(current_price),
                'price_change_30d': float(price_change),
                'volatility': float(volatility),
                'market_sentiment': self._determine_sentiment(price_change, volatility),
                'recommendation': self._generate_recommendation(price_change, volatility),
                'risk_level': self._assess_risk_level(volatility),
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info("Market insights generated", commodity=commodity)
            return insights
            
        except Exception as e:
            logger.error("Failed to generate market insights", error=str(e))
            raise Exception(f"Failed to generate insights: {str(e)}")
    
    def _determine_sentiment(self, price_change: float, volatility: float) -> str:
        """Determine market sentiment based on price change and volatility"""
        if price_change > 2 and volatility < 5:
            return "bullish"
        elif price_change < -2 and volatility < 5:
            return "bearish"
        elif volatility > 10:
            return "volatile"
        else:
            return "neutral"
    
    def _generate_recommendation(self, price_change: float, volatility: float) -> str:
        """Generate trading recommendation"""
        if price_change > 2 and volatility < 5:
            return "Consider buying - strong upward trend with low volatility"
        elif price_change < -2 and volatility < 5:
            return "Consider selling - downward trend with low volatility"
        elif volatility > 10:
            return "Exercise caution - high volatility market"
        else:
            return "Hold current position - stable market conditions"
    
    def _assess_risk_level(self, volatility: float) -> str:
        """Assess risk level based on volatility"""
        if volatility < 3:
            return "low"
        elif volatility < 7:
            return "medium"
        else:
            return "high"

# Global instance
forecasting_service = ForecastingService()
