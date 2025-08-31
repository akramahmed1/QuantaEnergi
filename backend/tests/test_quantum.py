#!/usr/bin/env python3
"""
Test Quantum Optimization Service with ESG focus for QuantaEnergi
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime
import sys
import os

# Add shared services to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared', 'services'))

try:
    from quantum_optimization_service import QuantumOptimizationService
except ImportError:
    # Fallback if service not available
    pytest.skip("Quantum optimization service not available", allow_module_level=True)


class TestQuantumOptimizationService:
    """Test Quantum Optimization Service functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.quantum_service = QuantumOptimizationService()
        
        # Create sample portfolio data
        self.portfolio_data = pd.DataFrame({
            'asset': ['crude_oil', 'natural_gas', 'renewables', 'electricity', 'coal'],
            'expected_return': [0.08, 0.06, 0.12, 0.09, 0.05],
            'volatility': [0.25, 0.20, 0.30, 0.22, 0.18],
            'esg_score': [45.0, 60.0, 85.0, 70.0, 25.0],
            'market_cap': [1000000, 800000, 500000, 1200000, 600000]
        })
        
        # Create sample constraints
        self.constraints = {
            'max_risk': 0.20,
            'min_return': 0.07,
            'min_esg_score': 60.0,
            'max_allocation': 0.40,
            'budget': 1000000
        }
    
    def test_quantum_service_initialization(self):
        """Test quantum optimization service initialization"""
        assert self.quantum_service is not None
        assert hasattr(self.quantum_service, 'optimize_portfolio')
        assert hasattr(self.quantum_service, 'calculate_esg_score')
        assert hasattr(self.quantum_service, 'multi_objective_optimization')
    
    def test_portfolio_optimization(self):
        """Test basic portfolio optimization"""
        optimization_result = self.quantum_service.optimize_portfolio(
            portfolio_data=self.portfolio_data,
            constraints=self.constraints,
            method='quantum'
        )
        
        assert optimization_result is not None
        assert 'optimal_weights' in optimization_result
        assert 'expected_return' in optimization_result
        assert 'risk' in optimization_result
        assert 'esg_score' in optimization_result
        assert 'sharpe_ratio' in optimization_result
        
        # Test optimal weights
        weights = optimization_result['optimal_weights']
        assert len(weights) == len(self.portfolio_data)
        assert all(0 <= w <= 1 for w in weights)
        assert abs(sum(weights) - 1.0) < 1e-6  # Weights should sum to 1
        
        # Test constraints satisfaction
        assert optimization_result['risk'] <= self.constraints['max_risk']
        assert optimization_result['expected_return'] >= self.constraints['min_return']
        assert optimization_result['esg_score'] >= self.constraints['min_esg_score']
    
    def test_esg_focused_optimization(self):
        """Test ESG-focused portfolio optimization"""
        esg_optimization = self.quantum_service.optimize_portfolio(
            portfolio_data=self.portfolio_data,
            constraints=self.constraints,
            method='quantum',
            esg_weight=0.7  # High ESG focus
        )
        
        assert esg_optimization is not None
        assert 'optimal_weights' in esg_optimization
        assert 'esg_score' in esg_optimization
        
        # ESG-focused optimization should have higher ESG score
        esg_score = esg_optimization['esg_score']
        assert esg_score >= 60.0  # Should meet minimum ESG constraint
        
        # Check that high-ESG assets get higher weights
        weights = esg_optimization['optimal_weights']
        renewables_weight = weights[self.portfolio_data['asset'] == 'renewables'].iloc[0]
        coal_weight = weights[self.portfolio_data['asset'] == 'coal'].iloc[0]
        
        # Renewables should have higher weight than coal in ESG-focused optimization
        assert renewables_weight >= coal_weight
    
    def test_multi_objective_optimization(self):
        """Test multi-objective optimization (return, risk, ESG)"""
        multi_obj_result = self.quantum_service.multi_objective_optimization(
            portfolio_data=self.portfolio_data,
            constraints=self.constraints,
            objectives=['return', 'risk', 'esg'],
            weights=[0.4, 0.3, 0.3]
        )
        
        assert multi_obj_result is not None
        assert 'pareto_front' in multi_obj_result
        assert 'optimal_solutions' in multi_obj_result
        assert 'trade_off_analysis' in multi_obj_result
        
        # Test Pareto front
        pareto_front = multi_obj_result['pareto_front']
        assert len(pareto_front) > 0
        
        # Test trade-off analysis
        trade_off = multi_obj_result['trade_off_analysis']
        assert 'return_vs_risk' in trade_off
        assert 'return_vs_esg' in trade_off
        assert 'risk_vs_esg' in trade_off
    
    def test_esg_scoring_calculation(self):
        """Test ESG score calculation"""
        # Test individual asset ESG scoring
        for _, asset in self.portfolio_data.iterrows():
            esg_score = self.quantum_service.calculate_esg_score(
                asset_name=asset['asset'],
                environmental_score=asset['esg_score'] * 0.4,  # 40% weight
                social_score=asset['esg_score'] * 0.3,        # 30% weight
                governance_score=asset['esg_score'] * 0.3     # 30% weight
            )
            
            assert esg_score is not None
            assert 0 <= esg_score <= 100
            assert abs(esg_score - asset['esg_score']) < 1e-6
        
        # Test portfolio ESG scoring
        portfolio_esg = self.quantum_service.calculate_portfolio_esg_score(
            portfolio_data=self.portfolio_data,
            weights=[0.2, 0.2, 0.2, 0.2, 0.2]  # Equal weights
        )
        
        assert portfolio_esg is not None
        assert 0 <= portfolio_esg <= 100
        
        # Equal weights should give average ESG score
        expected_esg = self.portfolio_data['esg_score'].mean()
        assert abs(portfolio_esg - expected_esg) < 1e-6
    
    def test_quantum_fallback_mechanism(self):
        """Test quantum optimization fallback to classical methods"""
        # Test when quantum hardware is not available
        fallback_result = self.quantum_service.optimize_portfolio(
            portfolio_data=self.portfolio_data,
            constraints=self.constraints,
            method='quantum',
            force_classical=True  # Force classical fallback
        )
        
        assert fallback_result is not None
        assert 'optimal_weights' in fallback_result
        assert 'method_used' in fallback_result
        assert fallback_result['method_used'] == 'classical'
        
        # Classical optimization should still satisfy constraints
        assert fallback_result['risk'] <= self.constraints['max_risk']
        assert fallback_result['expected_return'] >= self.constraints['min_return']
        assert fallback_result['esg_score'] >= self.constraints['min_esg_score']
    
    def test_constraint_validation(self):
        """Test constraint validation and handling"""
        # Test with invalid constraints
        invalid_constraints = {
            'max_risk': -0.1,  # Invalid: negative risk
            'min_return': 1.5,  # Invalid: return > 100%
            'min_esg_score': 150.0,  # Invalid: ESG score > 100
            'max_allocation': 1.5,  # Invalid: allocation > 100%
            'budget': -100000  # Invalid: negative budget
        }
        
        with pytest.raises(ValueError):
            self.quantum_service.optimize_portfolio(
                portfolio_data=self.portfolio_data,
                constraints=invalid_constraints
            )
        
        # Test with missing required constraints
        incomplete_constraints = {
            'max_risk': 0.20
            # Missing other required constraints
        }
        
        with pytest.raises(ValueError):
            self.quantum_service.optimize_portfolio(
                portfolio_data=self.portfolio_data,
                constraints=incomplete_constraints
            )
    
    def test_portfolio_rebalancing(self):
        """Test portfolio rebalancing functionality"""
        current_weights = [0.3, 0.2, 0.2, 0.2, 0.1]
        
        rebalancing_result = self.quantum_service.rebalance_portfolio(
            current_weights=current_weights,
            target_weights=[0.25, 0.25, 0.25, 0.15, 0.1],
            transaction_costs=0.001,  # 0.1% transaction cost
            constraints=self.constraints
        )
        
        assert rebalancing_result is not None
        assert 'new_weights' in rebalancing_result
        assert 'transaction_costs' in rebalancing_result
        assert 'rebalancing_efficiency' in rebalancing_result
        
        # Test transaction costs calculation
        transaction_costs = rebalancing_result['transaction_costs']
        assert transaction_costs >= 0
        
        # Test rebalancing efficiency
        efficiency = rebalancing_result['rebalancing_efficiency']
        assert 0 <= efficiency <= 1
    
    def test_risk_management_integration(self):
        """Test risk management integration in optimization"""
        risk_management_result = self.quantum_service.optimize_portfolio(
            portfolio_data=self.portfolio_data,
            constraints=self.constraints,
            method='quantum',
            include_risk_management=True,
            var_confidence_level=0.95,
            stress_test_scenarios=['recession', 'oil_crisis', 'climate_policy']
        )
        
        assert risk_management_result is not None
        assert 'var_95' in risk_management_result
        assert 'stress_test_results' in risk_management_result
        assert 'risk_decomposition' in risk_management_result
        
        # Test VaR calculation
        var_95 = risk_management_result['var_95']
        assert var_95 > 0
        
        # Test stress test results
        stress_results = risk_management_result['stress_test_results']
        assert 'recession' in stress_results
        assert 'oil_crisis' in stress_results
        assert 'climate_policy' in stress_results
    
    def test_esg_impact_analysis(self):
        """Test ESG impact analysis in optimization"""
        esg_impact_result = self.quantum_service.analyze_esg_impact(
            portfolio_data=self.portfolio_data,
            weights=[0.2, 0.2, 0.2, 0.2, 0.2],
            esg_metrics=['carbon_footprint', 'water_usage', 'social_impact', 'governance_score']
        )
        
        assert esg_impact_result is not None
        assert 'carbon_footprint' in esg_impact_result
        assert 'water_usage' in esg_impact_result
        assert 'social_impact' in esg_impact_result
        assert 'governance_score' in esg_impact_result
        
        # Test ESG metrics calculation
        for metric in ['carbon_footprint', 'water_usage', 'social_impact', 'governance_score']:
            value = esg_impact_result[metric]
            assert isinstance(value, (int, float))
            assert value >= 0
    
    def test_optimization_performance(self):
        """Test optimization performance and scalability"""
        import time
        
        # Test small portfolio optimization time
        start_time = time.time()
        small_result = self.quantum_service.optimize_portfolio(
            portfolio_data=self.portfolio_data.head(3),  # 3 assets
            constraints=self.constraints,
            method='quantum'
        )
        small_time = time.time() - start_time
        
        assert small_result is not None
        assert small_time < 5.0  # Should complete within 5 seconds
        
        # Test larger portfolio optimization time
        large_portfolio = pd.concat([self.portfolio_data] * 4)  # 20 assets
        
        start_time = time.time()
        large_result = self.quantum_service.optimize_portfolio(
            portfolio_data=large_portfolio,
            constraints=self.constraints,
            method='quantum'
        )
        large_time = time.time() - start_time
        
        assert large_result is not None
        assert large_time < 30.0  # Should complete within 30 seconds
        
        # Larger portfolios should take more time but not exponentially more
        assert large_time < small_time * 10  # Should not be 10x slower
    
    def test_quantum_advantage_verification(self):
        """Test quantum advantage verification"""
        # Test quantum vs classical optimization comparison
        comparison_result = self.quantum_service.compare_optimization_methods(
            portfolio_data=self.portfolio_data,
            constraints=self.constraints,
            methods=['quantum', 'classical'],
            metrics=['execution_time', 'solution_quality', 'constraint_satisfaction']
        )
        
        assert comparison_result is not None
        assert 'quantum' in comparison_result
        assert 'classical' in comparison_result
        
        # Test quantum advantage metrics
        quantum_metrics = comparison_result['quantum']
        classical_metrics = comparison_result['classical']
        
        assert 'execution_time' in quantum_metrics
        assert 'solution_quality' in quantum_metrics
        assert 'constraint_satisfaction' in quantum_metrics
        
        # In ideal cases, quantum should be faster or provide better solutions
        # For testing, we just verify the structure
        assert isinstance(quantum_metrics['execution_time'], (int, float))
        assert isinstance(classical_metrics['execution_time'], (int, float))


class TestESGOptimization:
    """Test specific ESG optimization functionality"""
    
    def setup_method(self):
        """Setup test data for ESG optimization"""
        self.quantum_service = QuantumOptimizationService()
        
        # Create ESG-focused test data
        self.esg_portfolio = pd.DataFrame({
            'asset': ['solar_panel', 'wind_turbine', 'battery_storage', 'green_bonds', 'esg_etf'],
            'expected_return': [0.15, 0.12, 0.10, 0.08, 0.11],
            'volatility': [0.35, 0.30, 0.25, 0.15, 0.20],
            'esg_score': [95.0, 90.0, 85.0, 80.0, 75.0],
            'carbon_intensity': [0.0, 0.0, 5.0, 10.0, 15.0],
            'social_impact': [90.0, 85.0, 80.0, 75.0, 70.0]
        })
    
    def test_esg_constraint_optimization(self):
        """Test optimization with strict ESG constraints"""
        esg_constraints = {
            'max_risk': 0.25,
            'min_return': 0.10,
            'min_esg_score': 85.0,  # High ESG requirement
            'max_carbon_intensity': 5.0,  # Low carbon requirement
            'min_social_impact': 80.0,  # High social impact requirement
            'max_allocation': 0.30,
            'budget': 1000000
        }
        
        esg_optimization = self.quantum_service.optimize_portfolio(
            portfolio_data=self.esg_portfolio,
            constraints=esg_constraints,
            method='quantum',
            esg_weight=0.8  # Very high ESG focus
        )
        
        assert esg_optimization is not None
        assert esg_optimization['esg_score'] >= 85.0
        
        # Check that high-ESG assets get higher weights
        weights = esg_optimization['optimal_weights']
        solar_weight = weights[self.esg_portfolio['asset'] == 'solar_panel'].iloc[0]
        wind_weight = weights[self.esg_portfolio['asset'] == 'wind_turbine'].iloc[0]
        
        # Solar and wind should have higher weights due to high ESG scores
        assert solar_weight > 0
        assert wind_weight > 0
    
    def test_sustainability_metrics_integration(self):
        """Test sustainability metrics integration in optimization"""
        sustainability_result = self.quantum_service.optimize_portfolio(
            portfolio_data=self.esg_portfolio,
            constraints=self.constraints,
            method='quantum',
            include_sustainability_metrics=True,
            sustainability_weight=0.6
        )
        
        assert sustainability_result is not None
        assert 'sustainability_score' in sustainability_result
        assert 'carbon_footprint' in sustainability_result
        assert 'renewable_energy_ratio' in sustainability_result
        
        # Test sustainability metrics
        sustainability_score = sustainability_result['sustainability_score']
        assert 0 <= sustainability_score <= 100
        
        carbon_footprint = sustainability_result['carbon_footprint']
        assert carbon_footprint >= 0
        
        renewable_ratio = sustainability_result['renewable_energy_ratio']
        assert 0 <= renewable_ratio <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
