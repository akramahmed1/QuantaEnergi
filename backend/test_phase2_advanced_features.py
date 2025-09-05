"""
Test Phase 2 Advanced Features Implementation
Tests advanced risk analytics, quantum portfolio optimization, and supply chain management
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
try:
    import numpy as np
except ImportError:
    np = None

# Import the services to test
from app.services.advanced_risk_analytics import AdvancedRiskAnalytics
from app.services.quantum_portfolio_optimizer import QuantumPortfolioOptimizer
from app.services.supply_chain_manager import SupplyChainManager, SupplyChainStatus

class TestAdvancedRiskAnalytics:
    """Test advanced risk analytics service"""
    
    @pytest.fixture
    def risk_analytics(self):
        return AdvancedRiskAnalytics()
    
    @pytest.fixture
    def sample_portfolio_data(self):
        return {
            "positions": [
                {
                    "commodity": "crude_oil",
                    "notional_value": 1000000.0,
                    "expected_return": 0.08,
                    "volatility": 0.25
                },
                {
                    "commodity": "natural_gas",
                    "notional_value": 500000.0,
                    "expected_return": 0.06,
                    "volatility": 0.30
                }
            ],
            "market_data": {
                "crude_oil": {"price": 85.0, "volume": 1000000},
                "natural_gas": {"price": 3.50, "volume": 500000}
            },
            "correlations": {
                "0": {"0": 1.0, "1": 0.3},
                "1": {"0": 0.3, "1": 1.0}
            }
        }
    
    @pytest.mark.asyncio
    async def test_calculate_var_monte_carlo(self, risk_analytics, sample_portfolio_data):
        """Test Monte Carlo VaR calculation"""
        result = await risk_analytics.calculate_var_monte_carlo(sample_portfolio_data)
        
        assert result["success"] is True
        assert "var_result" in result
        assert "var_value" in result["var_result"]
        assert "confidence_level" in result["var_result"]
        assert "time_horizon" in result["var_result"]
        assert "num_simulations" in result["var_result"]
        assert "simulation_summary" in result["var_result"]
        assert "risk_breakdown" in result["var_result"]
    
    @pytest.mark.asyncio
    async def test_stress_test_portfolio(self, risk_analytics, sample_portfolio_data):
        """Test portfolio stress testing"""
        stress_scenarios = [
            {
                "name": "Market Crash",
                "market_shocks": {
                    "crude_oil": 0.7,
                    "natural_gas": 0.8
                }
            },
            {
                "name": "Supply Shock",
                "market_shocks": {
                    "crude_oil": 1.3,
                    "natural_gas": 1.4
                }
            }
        ]
        
        result = await risk_analytics.stress_test_portfolio(sample_portfolio_data, stress_scenarios)
        
        assert result["success"] is True
        assert "stress_test_result" in result
        assert result["stress_test_result"]["scenarios_tested"] == 2
        assert "aggregate_result" in result["stress_test_result"]
        assert "scenario_results" in result["stress_test_result"]
    
    @pytest.mark.asyncio
    async def test_calculate_expected_shortfall(self, risk_analytics, sample_portfolio_data):
        """Test Expected Shortfall calculation"""
        result = await risk_analytics.calculate_expected_shortfall(sample_portfolio_data)
        
        assert result["success"] is True
        assert "expected_shortfall_result" in result
        assert "var_value" in result["expected_shortfall_result"]
        assert "expected_shortfall" in result["expected_shortfall_result"]
        assert "confidence_level" in result["expected_shortfall_result"]
        assert "tail_risk_measure" in result["expected_shortfall_result"]
    
    @pytest.mark.asyncio
    async def test_generate_risk_report(self, risk_analytics, sample_portfolio_data):
        """Test comprehensive risk report generation"""
        result = await risk_analytics.generate_risk_report(sample_portfolio_data)
        
        assert result["success"] is True
        assert "risk_report" in result
        assert "portfolio_summary" in result["risk_report"]
        assert "var_analysis" in result["risk_report"]
        assert "expected_shortfall_analysis" in result["risk_report"]
        assert "stress_testing" in result["risk_report"]
        assert "risk_recommendations" in result["risk_report"]
    
    def test_monte_carlo_simulation_internal(self, risk_analytics, sample_portfolio_data):
        """Test internal Monte Carlo simulation methods"""
        positions = sample_portfolio_data["positions"]
        market_data = sample_portfolio_data["market_data"]
        correlations = sample_portfolio_data["correlations"]
        
        # Test simulation
        simulation_result = asyncio.run(risk_analytics._run_monte_carlo_simulation(
            positions, market_data, correlations, 1, 1000
        ))
        
        assert "returns_matrix" in simulation_result
        assert "portfolio_changes" in simulation_result
        assert "total_changes" in simulation_result
        assert "summary" in simulation_result
        assert "mean" in simulation_result["summary"]
        assert "std" in simulation_result["summary"]
        assert "percentiles" in simulation_result["summary"]
    
    def test_correlated_returns_generation(self, risk_analytics, sample_portfolio_data):
        """Test correlated returns generation"""
        positions = sample_portfolio_data["positions"]
        correlations = sample_portfolio_data["correlations"]
        
        returns_matrix = risk_analytics._generate_correlated_returns(
            positions, correlations, 1, 1000
        )
        
        assert returns_matrix.shape == (1000, 2)
        assert isinstance(returns_matrix, np.ndarray)
    
    def test_portfolio_changes_calculation(self, risk_analytics, sample_portfolio_data):
        """Test portfolio changes calculation"""
        positions = sample_portfolio_data["positions"]
        returns_matrix = np.random.random((100, 2)) * 0.1 - 0.05  # Small returns
        
        portfolio_changes = risk_analytics._calculate_portfolio_changes(positions, returns_matrix)
        
        assert portfolio_changes.shape == (100, 2)
        assert isinstance(portfolio_changes, np.ndarray)
    
    def test_energy_calculation(self, risk_analytics):
        """Test energy calculation for QUBO matrix"""
        state = np.array([0.5, 0.5])
        qubo_matrix = np.array([[1.0, 0.1], [0.1, 1.0]])
        
        energy = risk_analytics._calculate_energy(state, qubo_matrix)
        
        assert isinstance(energy, float)
        assert energy > 0

class TestQuantumPortfolioOptimizer:
    """Test quantum portfolio optimization service"""
    
    @pytest.fixture
    def quantum_optimizer(self):
        return QuantumPortfolioOptimizer()
    
    @pytest.fixture
    def sample_portfolio_data(self):
        return {
            "positions": [
                {
                    "commodity": "crude_oil",
                    "notional_value": 1000000.0,
                    "expected_return": 0.08,
                    "volatility": 0.25
                },
                {
                    "commodity": "natural_gas",
                    "notional_value": 500000.0,
                    "expected_return": 0.06,
                    "volatility": 0.30
                }
            ]
        }
    
    @pytest.fixture
    def sample_constraints(self):
        return {
            "risk_aversion": 1.0,
            "max_weight": 0.3,
            "min_weight": 0.0
        }
    
    @pytest.mark.asyncio
    async def test_quantum_annealing_optimization(self, quantum_optimizer, sample_portfolio_data, sample_constraints):
        """Test quantum annealing optimization"""
        result = await quantum_optimizer.optimize_portfolio_quantum(
            sample_portfolio_data, sample_constraints, "quantum_annealing"
        )
        
        assert result["success"] is True
        assert "optimization_result" in result
        assert "optimal_weights" in result["optimization_result"]
        assert "expected_return" in result["optimization_result"]
        assert "portfolio_risk" in result["optimization_result"]
        assert "sharpe_ratio" in result["optimization_result"]
        assert "optimization_method" in result["optimization_result"]
    
    @pytest.mark.asyncio
    async def test_quantum_genetic_optimization(self, quantum_optimizer, sample_portfolio_data, sample_constraints):
        """Test quantum genetic optimization"""
        result = await quantum_optimizer.optimize_portfolio_quantum(
            sample_portfolio_data, sample_constraints, "quantum_genetic"
        )
        
        assert result["success"] is True
        assert "optimization_result" in result
        assert "optimal_weights" in result["optimization_result"]
        assert "optimization_method" in result["optimization_result"]
    
    @pytest.mark.asyncio
    async def test_hybrid_quantum_optimization(self, quantum_optimizer, sample_portfolio_data, sample_constraints):
        """Test hybrid quantum optimization"""
        result = await quantum_optimizer.optimize_portfolio_quantum(
            sample_portfolio_data, sample_constraints, "hybrid_quantum"
        )
        
        assert result["success"] is True
        assert "optimization_result" in result
        assert "optimal_weights" in result["optimization_result"]
        assert "optimization_method" in result["optimization_result"]
    
    @pytest.mark.asyncio
    async def test_compare_optimization_methods(self, quantum_optimizer, sample_portfolio_data, sample_constraints):
        """Test comparison of optimization methods"""
        result = await quantum_optimizer.compare_optimization_methods(sample_portfolio_data, sample_constraints)
        
        assert result["success"] is True
        assert "method_comparison" in result
        assert "quantum_annealing" in result["method_comparison"]
        assert "quantum_genetic" in result["method_comparison"]
        assert "hybrid_quantum" in result["method_comparison"]
    
    def test_quantum_state_initialization(self, quantum_optimizer):
        """Test quantum state initialization"""
        num_assets = 5
        quantum_state = quantum_optimizer._initialize_quantum_state(num_assets)
        
        assert len(quantum_state) == num_assets
        assert np.isclose(np.sum(quantum_state), 1.0, atol=1e-10)
        assert all(quantum_state >= 0)
    
    def test_qubo_matrix_creation(self, quantum_optimizer, sample_portfolio_data, sample_constraints):
        """Test QUBO matrix creation"""
        positions = sample_portfolio_data["positions"]
        constraints = sample_constraints
        
        qubo_matrix = quantum_optimizer._create_qubo_matrix(positions, constraints)
        
        assert qubo_matrix.shape == (2, 2)
        assert isinstance(qubo_matrix, np.ndarray)
        assert np.all(np.isfinite(qubo_matrix))
    
    def test_quantum_annealing_simulation(self, quantum_optimizer, sample_portfolio_data, sample_constraints):
        """Test quantum annealing simulation"""
        positions = sample_portfolio_data["positions"]
        constraints = sample_constraints
        
        # Test internal quantum annealing
        quantum_state = quantum_optimizer._initialize_quantum_state(len(positions))
        qubo_matrix = quantum_optimizer._create_qubo_matrix(positions, constraints)
        
        optimal_solution = asyncio.run(quantum_optimizer._simulate_quantum_annealing(
            quantum_state, qubo_matrix
        ))
        
        assert len(optimal_solution) == len(positions)
        assert np.isclose(np.sum(optimal_solution), 1.0, atol=1e-10)
        assert all(optimal_solution >= 0)
    
    def test_binary_to_weights_conversion(self, quantum_optimizer, sample_portfolio_data):
        """Test binary solution to weights conversion"""
        positions = sample_portfolio_data["positions"]
        binary_solution = np.array([0.6, 0.4])
        
        weights = quantum_optimizer._binary_to_weights(binary_solution, positions)
        
        assert len(weights) == len(positions)
        assert abs(sum(weights.values()) - 1.0) < 1e-10
        assert all(0 <= w <= 1 for w in weights.values())
    
    def test_portfolio_metrics_calculation(self, quantum_optimizer, sample_portfolio_data):
        """Test portfolio metrics calculation"""
        positions = sample_portfolio_data["positions"]
        weights = {
            "crude_oil": 0.6,
            "natural_gas": 0.4
        }
        
        metrics = quantum_optimizer._calculate_portfolio_metrics(weights, positions)
        
        assert "expected_return" in metrics
        assert "portfolio_risk" in metrics
        assert "sharpe_ratio" in metrics
        assert all(isinstance(v, float) for v in metrics.values())
    
    def test_constraint_validation(self, quantum_optimizer):
        """Test optimization constraints validation"""
        constraints = {"risk_aversion": 2.0}
        
        validated = quantum_optimizer._validate_optimization_constraints(constraints)
        
        assert "risk_aversion" in validated
        assert "max_weight" in validated
        assert "min_weight" in validated
        assert validated["risk_aversion"] == 2.0
        assert validated["max_weight"] == 0.3  # Default value

class TestSupplyChainManager:
    """Test supply chain management service"""
    
    @pytest.fixture
    def supply_chain_manager(self):
        return SupplyChainManager()
    
    @pytest.fixture
    def sample_supply_chain_data(self):
        return {
            "commodity": "crude_oil",
            "quantity": 10000,
            "source_location": "Houston",
            "destination": "New York",
            "delivery_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "transport_mode": "pipeline",
            "storage_requirements": {"temperature": "ambient", "pressure": "normal"},
            "quality_specifications": {"sulfur": "0.5%", "gravity": "32.5"}
        }
    
    @pytest.mark.asyncio
    async def test_create_supply_chain(self, supply_chain_manager, sample_supply_chain_data):
        """Test supply chain creation"""
        result = await supply_chain_manager.create_supply_chain(sample_supply_chain_data)
        
        assert result["success"] is True
        assert "supply_chain_id" in result
        assert "supply_chain" in result
        assert result["supply_chain"]["commodity"] == "crude_oil"
        assert result["supply_chain"]["quantity"] == 10000
        assert result["supply_chain"]["status"] == SupplyChainStatus.PLANNED.value
        assert "cost_estimates" in result["supply_chain"]
        assert "risk_assessment" in result["supply_chain"]
        assert "logistics_route" in result["supply_chain"]
        assert "inventory_allocation" in result["supply_chain"]
    
    @pytest.mark.asyncio
    async def test_update_supply_chain_status(self, supply_chain_manager, sample_supply_chain_data):
        """Test supply chain status update"""
        # First create a supply chain
        create_result = await supply_chain_manager.create_supply_chain(sample_supply_chain_data)
        supply_chain_id = create_result["supply_chain_id"]
        
        # Update status
        status_update = {
            "status": SupplyChainStatus.IN_TRANSIT.value,
            "current_location": "Dallas",
            "estimated_arrival": (datetime.now() + timedelta(days=3)).isoformat(),
            "notes": "Pipeline transit in progress"
        }
        
        result = await supply_chain_manager.update_supply_chain_status(supply_chain_id, status_update)
        
        assert result["success"] is True
        assert result["supply_chain"]["status"] == SupplyChainStatus.IN_TRANSIT.value
        assert result["supply_chain"]["current_location"] == "Dallas"
        assert "status_history" in result["supply_chain"]
        assert len(result["supply_chain"]["status_history"]) > 0
    
    @pytest.mark.asyncio
    async def test_track_supply_chain(self, supply_chain_manager, sample_supply_chain_data):
        """Test supply chain tracking"""
        # Create and update supply chain
        create_result = await supply_chain_manager.create_supply_chain(sample_supply_chain_data)
        supply_chain_id = create_result["supply_chain_id"]
        
        await supply_chain_manager.update_supply_chain_status(supply_chain_id, {
            "status": SupplyChainStatus.IN_TRANSIT.value,
            "current_location": "Dallas"
        })
        
        # Track supply chain
        result = await supply_chain_manager.track_supply_chain(supply_chain_id)
        
        assert result["success"] is True
        assert "tracking_info" in result
        assert result["tracking_info"]["current_status"] == SupplyChainStatus.IN_TRANSIT.value
        assert result["tracking_info"]["progress_percentage"] == 50.0
        assert result["tracking_info"]["current_location"] == "Dallas"
        assert "route_progress" in result["tracking_info"]
        assert "status_history" in result["tracking_info"]
    
    @pytest.mark.asyncio
    async def test_optimize_supply_chain(self, supply_chain_manager, sample_supply_chain_data):
        """Test supply chain optimization"""
        # Create supply chain
        create_result = await supply_chain_manager.create_supply_chain(sample_supply_chain_data)
        supply_chain_id = create_result["supply_chain_id"]
        
        # Optimize supply chain
        optimization_criteria = {
            "minimize_cost": True,
            "minimize_time": True,
            "max_risk_tolerance": 0.5
        }
        
        result = await supply_chain_manager.optimize_supply_chain(supply_chain_id, optimization_criteria)
        
        assert result["success"] is True
        assert "optimization_result" in result
        assert "original_route" in result["optimization_result"]
        assert "optimized_route" in result["optimization_result"]
        assert "cost_savings" in result["optimization_result"]
        assert "time_savings" in result["optimization_result"]
        assert "risk_improvement" in result["optimization_result"]
    
    @pytest.mark.asyncio
    async def test_get_supply_chain_analytics(self, supply_chain_manager, sample_supply_chain_data):
        """Test supply chain analytics"""
        # Create multiple supply chains
        await supply_chain_manager.create_supply_chain(sample_supply_chain_data)
        
        # Create another supply chain
        second_supply_chain = sample_supply_chain_data.copy()
        second_supply_chain["commodity"] = "natural_gas"
        await supply_chain_manager.create_supply_chain(second_supply_chain)
        
        # Get analytics
        result = await supply_chain_manager.get_supply_chain_analytics()
        
        assert result["success"] is True
        assert "analytics" in result
        assert result["analytics"]["total_supply_chains"] == 2
        assert "performance_metrics" in result["analytics"]
        assert "status_distribution" in result["analytics"]
        assert "cost_analysis" in result["analytics"]
    
    def test_cost_estimation(self, supply_chain_manager, sample_supply_chain_data):
        """Test cost estimation calculation"""
        cost_estimates = supply_chain_manager._calculate_cost_estimates(sample_supply_chain_data)
        
        assert "transport_cost" in cost_estimates
        assert "storage_cost" in cost_estimates
        assert "insurance_cost" in cost_estimates
        assert "total_cost" in cost_estimates
        assert "cost_per_unit" in cost_estimates
        assert cost_estimates["total_cost"] > 0
        assert cost_estimates["cost_per_unit"] > 0
    
    def test_risk_assessment(self, supply_chain_manager, sample_supply_chain_data):
        """Test supply chain risk assessment"""
        risk_assessment = supply_chain_manager._assess_supply_chain_risk(sample_supply_chain_data)
        
        assert "risk_score" in risk_assessment
        assert "risk_level" in risk_assessment
        assert "risk_factors" in risk_assessment
        assert "mitigation_strategies" in risk_assessment
        assert isinstance(risk_assessment["risk_score"], float)
        assert risk_assessment["risk_level"] in ["low", "medium", "high"]
        assert len(risk_assessment["risk_factors"]) > 0
        assert len(risk_assessment["mitigation_strategies"]) > 0
    
    def test_logistics_route_planning(self, supply_chain_manager, sample_supply_chain_data):
        """Test logistics route planning"""
        route = supply_chain_manager._plan_logistics_route(sample_supply_chain_data)
        
        assert "route_id" in route
        assert "source" in route
        assert "destination" in route
        assert "transport_mode" in route
        assert "estimated_distance" in route
        assert "estimated_duration" in route
        assert "waypoints" in route
        assert "restrictions" in route
        assert route["estimated_distance"] > 0
        assert route["estimated_duration"] > 0
        assert len(route["waypoints"]) > 0
    
    def test_waypoint_generation(self, supply_chain_manager):
        """Test waypoint generation for different transport modes"""
        source = "Houston"
        destination = "New York"
        
        # Test pipeline waypoints
        pipeline_waypoints = supply_chain_manager._generate_waypoints(source, destination, "pipeline")
        assert len(pipeline_waypoints) > 0
        assert any(w["type"] == "pump" for w in pipeline_waypoints)
        
        # Test tanker waypoints
        tanker_waypoints = supply_chain_manager._generate_waypoints(source, destination, "tanker")
        assert len(tanker_waypoints) > 0
        assert any(w["type"] == "loading_port" for w in tanker_waypoints)
    
    def test_inventory_allocation(self, supply_chain_manager, sample_supply_chain_data):
        """Test inventory allocation"""
        allocation = supply_chain_manager._allocate_inventory(sample_supply_chain_data)
        
        assert "allocation_id" in allocation
        assert "commodity" in allocation
        assert "requested_quantity" in allocation
        assert "allocated_quantity" in allocation
        assert "available_inventory" in allocation
        assert "allocation_status" in allocation
        assert allocation["commodity"] == "crude_oil"
        assert allocation["requested_quantity"] == 10000
        assert allocation["allocated_quantity"] > 0
    
    def test_progress_percentage_calculation(self, supply_chain_manager):
        """Test progress percentage calculation"""
        # Test different statuses
        planned_chain = {"status": SupplyChainStatus.PLANNED.value}
        in_transit_chain = {"status": SupplyChainStatus.IN_TRANSIT.value}
        delivered_chain = {"status": SupplyChainStatus.DELIVERED.value}
        
        assert supply_chain_manager._calculate_progress_percentage(planned_chain) == 0.0
        assert supply_chain_manager._calculate_progress_percentage(in_transit_chain) == 50.0
        assert supply_chain_manager._calculate_progress_percentage(delivered_chain) == 100.0
    
    def test_route_progress_tracking(self, supply_chain_manager):
        """Test route progress tracking"""
        supply_chain = {
            "source_location": "Houston",
            "destination": "New York",
            "status": SupplyChainStatus.IN_TRANSIT.value,
            "current_location": "Dallas",
            "logistics_route": {
                "waypoints": [
                    {"location": "Houston", "type": "source", "estimated_time": 0},
                    {"location": "Dallas", "type": "transit", "estimated_time": 8},
                    {"location": "New York", "type": "destination", "estimated_time": 24}
                ]
            }
        }
        
        route_progress = supply_chain_manager._get_route_progress(supply_chain)
        
        assert len(route_progress) == 3
        assert any(w["status"] == "completed" for w in route_progress)
        assert any(w["status"] == "current" for w in route_progress)
        assert any(w["status"] == "pending" for w in route_progress)

if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v"])
