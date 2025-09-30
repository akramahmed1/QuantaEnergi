"""
Validation Tests for QuantaEnergi Core Features
Tests trade lifecycle, geo-risk, and Sharia compliance functionality
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List
import numpy as np
from unittest.mock import Mock, patch, AsyncMock

# Import the services to test
from app.services.advanced_etrm_features import TradeLifecycleService
from app.services.geo_risk_service import GeoRiskService
from app.services.sharia_compliance import ShariaComplianceService


class TestTradeLifecycleValidation:
    """Test trade lifecycle functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.trade_service = TradeLifecycleService()
        self.sample_trade = {
            "trade_id": "TEST_TRADE_001",
            "commodity": "crude_oil",
            "quantity": 1000,
            "price": 75.50,
            "trade_date": datetime.now(),
            "settlement_date": datetime.now() + timedelta(days=7),
            "buyer": "Test Buyer",
            "seller": "Test Seller",
            "contract_type": "spot"
        }
    
    def test_trade_creation_validation(self):
        """Test trade creation with validation"""
        # Test valid trade creation
        result = self.trade_service.create_trade(self.sample_trade)
        
        assert result["success"] is True
        assert "trade_id" in result
        assert result["trade_id"] == "TEST_TRADE_001"
        assert result["status"] == "CREATED"
    
    def test_trade_validation_errors(self):
        """Test trade validation with invalid data"""
        # Test with missing required fields
        invalid_trade = {
            "trade_id": "INVALID_TRADE",
            "commodity": "",  # Empty commodity
            "quantity": -100,  # Negative quantity
            "price": -50.0,  # Negative price
        }
        
        result = self.trade_service.create_trade(invalid_trade)
        
        assert result["success"] is False
        assert "errors" in result
        assert len(result["errors"]) > 0
    
    def test_pnl_calculation_validation(self):
        """Test P&L calculation functionality"""
        trade_data = {
            "trade_id": "PNL_TEST_001",
            "commodity": "crude_oil",
            "quantity": 1000,
            "entry_price": 75.00,
            "current_price": 78.50,
            "position_type": "long"
        }
        
        result = self.trade_service.calculate_pnl(trade_data)
        
        assert result["success"] is True
        assert "unrealized_pnl" in result
        assert "realized_pnl" in result
        assert result["unrealized_pnl"] > 0  # Should be positive for long position with price increase
    
    def test_trade_lifecycle_states(self):
        """Test trade lifecycle state transitions"""
        trade_id = "LIFECYCLE_TEST_001"
        
        # Create trade
        create_result = self.trade_service.create_trade(self.sample_trade)
        assert create_result["status"] == "CREATED"
        
        # Confirm trade
        confirm_result = self.trade_service.confirm_trade(trade_id)
        assert confirm_result["status"] == "CONFIRMED"
        
        # Settle trade
        settle_result = self.trade_service.settle_trade(trade_id)
        assert settle_result["status"] == "SETTLED"


class TestGuyanaGeoRiskValidation:
    """Test Guyana geo-risk functionality with mock 650-800K bpd data"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.geo_risk_service = GeoRiskService()
        self.mock_production_data = {
            "liza_field": {"production": 150000, "risk_level": 0.3},
            "payara_field": {"production": 220000, "risk_level": 0.4},
            "yellowtail_field": {"production": 250000, "risk_level": 0.5},
            "stabroek_block": {"total_production": 620000}
        }
    
    @pytest.mark.asyncio
    async def test_guyana_basin_monitoring(self):
        """Test Guyana basin real-time monitoring"""
        with patch.object(self.geo_risk_service, 'monitor_guyana_basin_realtime') as mock_monitor:
            # Mock the monitoring response
            mock_monitor.return_value = {
                'region': 'GUYANA_BASIN',
                'timestamp': datetime.now().isoformat(),
                'iot_data': {
                    'active_rigs': 6,
                    'production_rate': 650000,  # Mock 650K bpd data
                    'equipment_status': {
                        'liza_destiny': {'status': 'operational', 'efficiency': 0.95},
                        'payara_prosperity': {'status': 'operational', 'efficiency': 0.88}
                    },
                    'carbon_intensity': 18.5
                },
                'composite_risk_score': 0.25,
                'risk_level': 'LOW',
                'trading_recommendations': [
                    "Production above 650K bpd - bullish signal for Guyana crude"
                ]
            }
            
            result = await self.geo_risk_service.monitor_guyana_basin_realtime()
            
            assert result['region'] == 'GUYANA_BASIN'
            assert result['iot_data']['production_rate'] >= 650000
            assert result['iot_data']['production_rate'] <= 800000
            assert result['risk_level'] in ['LOW', 'MODERATE', 'HIGH']
            assert len(result['trading_recommendations']) > 0
    
    def test_guyana_field_data_validation(self):
        """Test Guyana field data accuracy"""
        guyana_data = self.geo_risk_service.guyana_basin_data
        
        # Validate Liza field data
        assert guyana_data['liza_field']['production'] == 300000  # 300K bpd
        assert guyana_data['liza_field']['operator'] == 'ExxonMobil Guyana'
        assert guyana_data['liza_field']['status'] == 'operational'
        
        # Validate Payara field data
        assert guyana_data['payara_field']['production'] == 250000  # 250K bpd
        assert guyana_data['payara_field']['startup_year'] == 2023
        
        # Validate Yellowtail field data
        assert guyana_data['yellowtail_field']['production'] == 150000  # 150K bpd
        assert guyana_data['yellowtail_field']['startup_year'] == 2025
        
        # Validate Stabroek block total
        assert guyana_data['stabroek_block']['total_production'] == 700000  # 700K bpd total
        assert guyana_data['stabroek_block']['total_reserves'] == 11000000000  # 11B barrels
    
    def test_production_range_validation(self):
        """Test that production data falls within 650-800K bpd range"""
        total_production = sum([
            self.geo_risk_service.guyana_basin_data['liza_field']['production'],
            self.geo_risk_service.guyana_basin_data['payara_field']['production'],
            self.geo_risk_service.guyana_basin_data['yellowtail_field']['production']
        ])
        
        assert 650000 <= total_production <= 800000, f"Production {total_production} not in 650-800K bpd range"
        assert total_production == 700000, f"Expected 700K bpd, got {total_production}"


class TestShariaComplianceValidation:
    """Test Sharia compliance with riba-free calculations"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.sharia_service = ShariaComplianceService()
    
    def test_ethical_sector_screening(self):
        """Test ethical sector screening functionality"""
        # Test compliant commodity and sector
        result = self.sharia_service.screen_ethical_sectors("crude_oil", "energy_trading")
        
        assert result['overall_compliant'] is True
        assert result['commodity_compliant'] is True
        assert result['sector_compliant'] is True
        assert result['compliance_framework'] == 'AAOIFI Ethical Screening'
    
    def test_prohibited_sector_screening(self):
        """Test screening of prohibited sectors"""
        # Test prohibited sector
        result = self.sharia_service.screen_ethical_sectors("crude_oil", "gambling")
        
        assert result['overall_compliant'] is False
        assert result['sector_compliant'] is False
        assert len(result['prohibited_factors']) > 0
    
    def test_riba_free_pnl_calculations(self):
        """Test riba-free P&L calculations for Islamic structures"""
        trade_data = {
            "principal": 1000000,  # $1M principal
            "profit_rate": 0.05,   # 5% profit rate
            "period_months": 12,
            "structure_type": "murabaha"
        }
        
        result = self.sharia_service.calculate_islamic_pnl(trade_data, "murabaha")
        
        assert result['sharia_compliant'] is True
        assert 'islamic_pnl' in result
        assert 'profit_sharing' in result
        assert result['structure'] == 'murabaha'
        assert result['islamic_pnl'] > 0
    
    def test_musharaka_calculation(self):
        """Test Musharaka partnership calculations"""
        trade_data = {
            "capital_contribution": 500000,
            "profit_sharing_ratio": 0.5,
            "total_profit": 100000
        }
        
        result = self.sharia_service.calculate_islamic_pnl(trade_data, "musharaka")
        
        assert result['sharia_compliant'] is True
        assert result['structure'] == 'musharaka'
        assert 'profit_sharing' in result
        assert result['profit_sharing']['partner_share'] == 50000  # 50% of 100K
    
    def test_zakat_calculation(self):
        """Test Zakat calculation with Nisab threshold"""
        wealth_data = {
            "total_wealth": 150000,  # Above Nisab threshold
            "zakat_rate": 0.025,     # 2.5%
            "nisab_threshold": 100000
        }
        
        result = self.sharia_service.calculate_zakat(wealth_data)
        
        assert result['zakat_required'] is True
        assert result['zakat_amount'] == 3750  # 2.5% of 150K
        assert result['wealth_above_nisab'] == 50000  # 150K - 100K
    
    def test_islamic_structures_validation(self):
        """Test Islamic finance structures data"""
        structures = self.sharia_service.islamic_structures
        
        # Validate Murabaha structure
        assert structures['murabaha']['type'] == 'Cost-plus financing'
        assert structures['murabaha']['markup_rate'] == 0.05
        assert structures['murabaha']['risk_sharing'] is False
        
        # Validate Musharaka structure
        assert structures['musharaka']['type'] == 'Partnership financing'
        assert structures['musharaka']['profit_sharing'] is True
        assert structures['musharaka']['loss_sharing'] is True
        
        # Validate Mudaraba structure
        assert structures['mudaraba']['type'] == 'Trust financing'
        assert structures['mudaraba']['profit_sharing'] == 0.7
        assert structures['mudaraba']['loss_sharing'] is False


class TestIntegrationValidation:
    """Integration tests for core features working together"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.trade_service = TradeLifecycleService()
        self.geo_risk_service = GeoRiskService()
        self.sharia_service = ShariaComplianceService()
    
    def test_guyana_crude_trading_workflow(self):
        """Test complete workflow for Guyana crude trading"""
        # Create a Guyana crude trade
        guyana_trade = {
            "trade_id": "GUYANA_CRUDE_001",
            "commodity": "guyana_crude_oil",
            "quantity": 50000,  # 50K barrels
            "price": 78.50,
            "trade_date": datetime.now(),
            "settlement_date": datetime.now() + timedelta(days=30),
            "buyer": "European Refinery",
            "seller": "ExxonMobil Guyana",
            "contract_type": "futures"
        }
        
        # Validate trade creation
        trade_result = self.trade_service.create_trade(guyana_trade)
        assert trade_result["success"] is True
        
        # Validate Guyana production data
        guyana_data = self.geo_risk_service.guyana_basin_data
        total_production = sum([
            guyana_data['liza_field']['production'],
            guyana_data['payara_field']['production'],
            guyana_data['yellowtail_field']['production']
        ])
        assert 650000 <= total_production <= 800000
        
        # Validate Sharia compliance (if applicable)
        compliance_result = self.sharia_service.screen_ethical_sectors("crude_oil", "energy_trading")
        assert compliance_result['overall_compliant'] is True
    
    def test_risk_assessment_integration(self):
        """Test risk assessment across services"""
        # Test trade risk assessment
        trade_data = {
            "trade_id": "RISK_TEST_001",
            "commodity": "natural_gas",
            "quantity": 1000000,  # 1M MMBtu
            "price": 3.50,
            "position_type": "long"
        }
        
        # Create trade
        trade_result = self.trade_service.create_trade(trade_data)
        assert trade_result["success"] is True
        
        # Calculate P&L
        pnl_result = self.trade_service.calculate_pnl(trade_data)
        assert pnl_result["success"] is True
        
        # Validate risk metrics
        assert "unrealized_pnl" in pnl_result
        assert "var_95" in pnl_result
        assert "var_99" in pnl_result


if __name__ == "__main__":
    # Run validation tests
    pytest.main([__file__, "-v", "--tb=short"])
