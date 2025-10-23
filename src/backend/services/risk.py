"""
Risk Calculation Service for QuantaEnergi
Implements VaR (Value at Risk) calculations using numpy.percentile
Integrates with crude_oil_ensemble.pkl model for enhanced forecasting
"""

import numpy as np
import joblib
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RiskCalculator:
    """Risk calculation service with VaR and stress testing capabilities"""
    
    def __init__(self):
        """Initialize risk calculator with ML model"""
        self.ensemble_model = None
        self.scaler = None
        self._load_models()
        
    def _load_models(self):
        """Load pre-trained ensemble model and scaler"""
        try:
            # Load the ensemble model
            model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'crude_oil_ensemble.pkl')
            scaler_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'crude_oil_ensemble_scaler.pkl')
            
            if os.path.exists(model_path):
                self.ensemble_model = joblib.load(model_path)
                logger.info("Ensemble model loaded successfully")
            else:
                logger.warning("Ensemble model not found, using fallback calculations")
                
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
                logger.info("Scaler loaded successfully")
            else:
                logger.warning("Scaler not found, using standard scaling")
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.ensemble_model = None
            self.scaler = None
    
    def calculate_var(self, positions: List[float], confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR) using numpy.percentile
        
        Args:
            positions: List of position values or returns
            confidence: Confidence level (0.95 for 95% VaR, 0.99 for 99% VaR)
            
        Returns:
            VaR value as a float
        """
        try:
            if not positions or len(positions) == 0:
                logger.warning("Empty positions list provided")
                return 0.0
            
            # Convert to numpy array for efficient computation
            positions_array = np.array(positions)
            
            # Calculate VaR using percentile method
            # For VaR, we want the (1-confidence) percentile of losses
            var_percentile = (1 - confidence) * 100
            var_value = np.percentile(positions_array, var_percentile)
            
            logger.info(f"VaR calculated: {var_value:.4f} at {confidence*100}% confidence")
            return float(var_value)
            
        except Exception as e:
            logger.error(f"Error calculating VaR: {e}")
            return 0.0
    
    def calculate_expected_shortfall(self, positions: List[float], confidence: float = 0.95) -> float:
        """
        Calculate Expected Shortfall (Conditional VaR)
        
        Args:
            positions: List of position values or returns
            confidence: Confidence level
            
        Returns:
            Expected Shortfall value
        """
        try:
            if not positions or len(positions) == 0:
                return 0.0
            
            positions_array = np.array(positions)
            var_value = self.calculate_var(positions, confidence)
            
            # Calculate expected shortfall as mean of losses beyond VaR
            tail_losses = positions_array[positions_array <= var_value]
            
            if len(tail_losses) == 0:
                return var_value
            
            expected_shortfall = np.mean(tail_losses)
            return float(expected_shortfall)
            
        except Exception as e:
            logger.error(f"Error calculating Expected Shortfall: {e}")
            return 0.0
    
    def calculate_portfolio_var(self, portfolio_data: Dict[str, Any], confidence: float = 0.95) -> Dict[str, Any]:
        """
        Calculate portfolio-level VaR with enhanced ML integration
        
        Args:
            portfolio_data: Dictionary containing portfolio information
            confidence: Confidence level for VaR calculation
            
        Returns:
            Dictionary with VaR metrics and analysis
        """
        try:
            positions = portfolio_data.get('positions', [])
            total_value = portfolio_data.get('total_value', 0)
            
            if not positions or total_value <= 0:
                return {
                    'var_95': 0.0,
                    'var_99': 0.0,
                    'expected_shortfall_95': 0.0,
                    'expected_shortfall_99': 0.0,
                    'portfolio_risk_score': 0.0,
                    'calculated_at': datetime.utcnow().isoformat()
                }
            
            # Extract position values
            position_values = [pos.get('value', 0) for pos in positions]
            
            # Calculate VaR at different confidence levels
            var_95 = self.calculate_var(position_values, 0.95)
            var_99 = self.calculate_var(position_values, 0.99)
            
            # Calculate Expected Shortfall
            es_95 = self.calculate_expected_shortfall(position_values, 0.95)
            es_99 = self.calculate_expected_shortfall(position_values, 0.99)
            
            # Calculate portfolio risk score
            risk_score = self._calculate_portfolio_risk_score(portfolio_data)
            
            # Enhanced analysis using ML model if available
            ml_insights = self._get_ml_insights(portfolio_data)
            
            return {
                'var_95': round(var_95, 4),
                'var_99': round(var_99, 4),
                'expected_shortfall_95': round(es_95, 4),
                'expected_shortfall_99': round(es_99, 4),
                'portfolio_risk_score': round(risk_score, 4),
                'ml_insights': ml_insights,
                'calculated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio VaR: {e}")
            return {
                'var_95': 0.0,
                'var_99': 0.0,
                'expected_shortfall_95': 0.0,
                'expected_shortfall_99': 0.0,
                'portfolio_risk_score': 1.0,
                'error': str(e),
                'calculated_at': datetime.utcnow().isoformat()
            }
    
    def _calculate_portfolio_risk_score(self, portfolio_data: Dict[str, Any]) -> float:
        """Calculate overall portfolio risk score"""
        try:
            positions = portfolio_data.get('positions', [])
            total_value = portfolio_data.get('total_value', 0)
            
            if not positions or total_value <= 0:
                return 0.0
            
            # Calculate concentration risk
            position_values = [pos.get('value', 0) for pos in positions]
            concentration_risk = self._calculate_concentration_risk(position_values, total_value)
            
            # Calculate volatility risk
            volatility_risk = self._calculate_volatility_risk(positions)
            
            # Calculate correlation risk (simplified)
            correlation_risk = self._calculate_correlation_risk(positions)
            
            # Weighted risk score
            risk_score = (
                concentration_risk * 0.4 +
                volatility_risk * 0.4 +
                correlation_risk * 0.2
            )
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating portfolio risk score: {e}")
            return 0.5
    
    def _calculate_concentration_risk(self, position_values: List[float], total_value: float) -> float:
        """Calculate portfolio concentration risk using HHI"""
        try:
            if not position_values or total_value <= 0:
                return 0.0
            
            # Calculate Herfindahl-Hirschman Index
            weights = [value / total_value for value in position_values]
            hhi = sum(w**2 for w in weights)
            
            # Normalize HHI (0 = perfect diversification, 1 = perfect concentration)
            n = len(weights)
            if n <= 1:
                return 1.0
            
            normalized_hhi = (hhi - 1/n) / (1 - 1/n)
            return min(normalized_hhi, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating concentration risk: {e}")
            return 0.5
    
    def _calculate_volatility_risk(self, positions: List[Dict[str, Any]]) -> float:
        """Calculate portfolio volatility risk"""
        try:
            if not positions:
                return 0.0
            
            # Extract volatility from positions (if available)
            volatilities = []
            for pos in positions:
                vol = pos.get('volatility', 0.2)  # Default 20% volatility
                volatilities.append(vol)
            
            # Calculate weighted average volatility
            total_value = sum(pos.get('value', 0) for pos in positions)
            if total_value <= 0:
                return 0.0
            
            weighted_vol = sum(
                (pos.get('value', 0) / total_value) * pos.get('volatility', 0.2)
                for pos in positions
            )
            
            # Normalize volatility risk (0.1 = low risk, 0.5 = high risk)
            return min(weighted_vol / 0.5, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating volatility risk: {e}")
            return 0.5
    
    def _calculate_correlation_risk(self, positions: List[Dict[str, Any]]) -> float:
        """Calculate portfolio correlation risk (simplified)"""
        try:
            if len(positions) <= 1:
                return 0.0
            
            # Simplified correlation risk based on commodity types
            commodities = [pos.get('commodity', 'unknown') for pos in positions]
            
            # Count unique commodities
            unique_commodities = len(set(commodities))
            total_positions = len(positions)
            
            # Higher correlation risk with fewer unique commodities
            correlation_risk = 1.0 - (unique_commodities / total_positions)
            return correlation_risk
            
        except Exception as e:
            logger.error(f"Error calculating correlation risk: {e}")
            return 0.5
    
    def _get_ml_insights(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get ML-based insights using the ensemble model"""
        try:
            if not self.ensemble_model:
                return {
                    'ml_available': False,
                    'message': 'ML model not available'
                }
            
            # Prepare features for ML model
            features = self._prepare_ml_features(portfolio_data)
            
            if features is None:
                return {
                    'ml_available': False,
                    'message': 'Insufficient data for ML analysis'
                }
            
            # Scale features if scaler is available
            if self.scaler:
                features_scaled = self.scaler.transform([features])
            else:
                features_scaled = [features]
            
            # Get ML predictions
            prediction = self.ensemble_model.predict(features_scaled)[0]
            
            return {
                'ml_available': True,
                'predicted_risk': float(prediction),
                'confidence': 0.85,  # Placeholder confidence
                'model_version': 'crude_oil_ensemble_v1.0'
            }
            
        except Exception as e:
            logger.error(f"Error getting ML insights: {e}")
            return {
                'ml_available': False,
                'error': str(e)
            }
    
    def _prepare_ml_features(self, portfolio_data: Dict[str, Any]) -> Optional[List[float]]:
        """Prepare features for ML model"""
        try:
            positions = portfolio_data.get('positions', [])
            total_value = portfolio_data.get('total_value', 0)
            
            if not positions or total_value <= 0:
                return None
            
            # Extract key features
            num_positions = len(positions)
            avg_position_size = total_value / num_positions if num_positions > 0 else 0
            
            # Calculate concentration metrics
            position_values = [pos.get('value', 0) for pos in positions]
            max_position = max(position_values) if position_values else 0
            concentration_ratio = max_position / total_value if total_value > 0 else 0
            
            # Calculate volatility metrics
            volatilities = [pos.get('volatility', 0.2) for pos in positions]
            avg_volatility = np.mean(volatilities) if volatilities else 0.2
            
            # Prepare feature vector (simplified for demo)
            features = [
                num_positions,
                avg_position_size / 1000000,  # Normalize to millions
                concentration_ratio,
                avg_volatility,
                total_value / 1000000  # Normalize to millions
            ]
            
            return features
            
        except Exception as e:
            logger.error(f"Error preparing ML features: {e}")
            return None
    
    def stress_test(self, portfolio_data: Dict[str, Any], scenarios: List[str] = None) -> Dict[str, Any]:
        """
        Perform stress testing on portfolio
        
        Args:
            portfolio_data: Portfolio data
            scenarios: List of stress test scenarios
            
        Returns:
            Stress test results
        """
        try:
            if scenarios is None:
                scenarios = ['market_crash', 'oil_price_shock', 'interest_rate_spike']
            
            results = {}
            
            for scenario in scenarios:
                scenario_result = self._run_stress_scenario(portfolio_data, scenario)
                results[scenario] = scenario_result
            
            return {
                'stress_test_results': results,
                'overall_stress_score': self._calculate_overall_stress_score(results),
                'calculated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in stress testing: {e}")
            return {
                'error': str(e),
                'calculated_at': datetime.utcnow().isoformat()
            }
    
    def _run_stress_scenario(self, portfolio_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Run individual stress test scenario"""
        try:
            positions = portfolio_data.get('positions', [])
            total_value = portfolio_data.get('total_value', 0)
            
            # Define stress factors for different scenarios
            stress_factors = {
                'market_crash': 0.3,  # 30% loss
                'oil_price_shock': 0.4,  # 40% loss for oil positions
                'interest_rate_spike': 0.2,  # 20% loss
                'currency_crisis': 0.25,  # 25% loss
                'liquidity_crisis': 0.35  # 35% loss
            }
            
            stress_factor = stress_factors.get(scenario, 0.2)
            
            # Calculate stressed portfolio value
            stressed_value = total_value * (1 - stress_factor)
            loss_amount = total_value - stressed_value
            
            return {
                'scenario': scenario,
                'stress_factor': stress_factor,
                'original_value': total_value,
                'stressed_value': stressed_value,
                'loss_amount': loss_amount,
                'loss_percentage': stress_factor * 100
            }
            
        except Exception as e:
            logger.error(f"Error running stress scenario {scenario}: {e}")
            return {
                'scenario': scenario,
                'error': str(e)
            }
    
    def _calculate_overall_stress_score(self, stress_results: Dict[str, Any]) -> float:
        """Calculate overall stress test score"""
        try:
            if not stress_results:
                return 0.0
            
            # Calculate weighted average of stress factors
            total_weight = 0
            weighted_score = 0
            
            for scenario, result in stress_results.items():
                if 'stress_factor' in result:
                    weight = 1.0  # Equal weight for all scenarios
                    weighted_score += result['stress_factor'] * weight
                    total_weight += weight
            
            if total_weight == 0:
                return 0.0
            
            return weighted_score / total_weight
            
        except Exception as e:
            logger.error(f"Error calculating overall stress score: {e}")
            return 0.0

# Global instance for easy import
risk_calculator = RiskCalculator()

# Convenience functions for direct use
def calculate_var(positions: List[float], confidence: float = 0.95) -> float:
    """Calculate VaR using the global risk calculator"""
    return risk_calculator.calculate_var(positions, confidence)

def calculate_portfolio_var(portfolio_data: Dict[str, Any], confidence: float = 0.95) -> Dict[str, Any]:
    """Calculate portfolio VaR using the global risk calculator"""
    return risk_calculator.calculate_portfolio_var(portfolio_data, confidence)

def stress_test_portfolio(portfolio_data: Dict[str, Any], scenarios: List[str] = None) -> Dict[str, Any]:
    """Perform stress testing using the global risk calculator"""
    return risk_calculator.stress_test(portfolio_data, scenarios)
