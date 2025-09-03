"""
Test Phase 1 ETRM Features Implementation
Tests core ETRM/CTRM features and Middle East compliance
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Import the services to test
from app.services.trade_lifecycle import TradeLifecycle, TradeStage
from app.services.position_manager import PositionManager
from app.services.sharia import ShariaScreeningEngine, IslamicTradingValidator
from app.services.credit_manager import CreditManager
from app.services.regulatory_reporting import RegulatoryReporting

class TestTradeLifecycle:
    """Test trade lifecycle service"""
    
    @pytest.fixture
    def trade_lifecycle(self):
        return TradeLifecycle()
    
    @pytest.fixture
    def sample_trade_data(self):
        return {
            "parties": ["Trader A", "Trader B"],
            "commodity": "crude_oil",
            "quantity": 1000,
            "price": 85.0,
            "delivery_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "trade_type": "spot",
            "delivery_location": "Houston",
            "transport_mode": "pipeline",
            "sharia_compliant": True
        }
    
    @pytest.mark.asyncio
    async def test_capture_trade(self, trade_lifecycle, sample_trade_data):
        """Test trade capture functionality"""
        result = await trade_lifecycle.capture_trade(sample_trade_data)
        
        assert result["success"] is True
        assert "trade_id" in result
        assert result["trade"]["status"] == TradeStage.CAPTURE.value
        assert result["trade"]["commodity"] == "crude_oil"
        assert result["trade"]["quantity"] == 1000
        assert result["trade"]["price"] == 85.0
    
    @pytest.mark.asyncio
    async def test_validate_trade(self, trade_lifecycle, sample_trade_data):
        """Test trade validation"""
        # First capture a trade
        capture_result = await trade_lifecycle.capture_trade(sample_trade_data)
        trade_id = capture_result["trade_id"]
        
        # Then validate it
        validation_result = await trade_lifecycle.validate_trade(trade_id)
        
        assert validation_result["success"] is True
        assert validation_result["valid"] is True
        assert TradeStage.VALIDATION.value in validation_result["trade"]["stages"]
    
    @pytest.mark.asyncio
    async def test_generate_confirmation(self, trade_lifecycle, sample_trade_data):
        """Test trade confirmation generation"""
        # Capture and validate trade
        capture_result = await trade_lifecycle.capture_trade(sample_trade_data)
        trade_id = capture_result["trade_id"]
        await trade_lifecycle.validate_trade(trade_id)
        
        # Generate confirmation
        confirmation_result = await trade_lifecycle.generate_confirmation(trade_id)
        
        assert confirmation_result["success"] is True
        assert "confirmation" in confirmation_result
        assert confirmation_result["confirmation"]["status"] == "confirmed"
        assert TradeStage.CONFIRMATION.value in confirmation_result["trade"]["stages"]
    
    @pytest.mark.asyncio
    async def test_complete_trade_lifecycle(self, trade_lifecycle, sample_trade_data):
        """Test complete trade lifecycle from capture to completion"""
        # Capture trade
        capture_result = await trade_lifecycle.capture_trade(sample_trade_data)
        trade_id = capture_result["trade_id"]
        
        # Validate trade
        await trade_lifecycle.validate_trade(trade_id)
        
        # Generate confirmation
        await trade_lifecycle.generate_confirmation(trade_id)
        
        # Allocate trade
        allocation_data = {
            "delivery_schedules": ["2025-02-15", "2025-02-16"],
            "storage_locations": ["Houston Terminal"],
            "transport_routes": ["Pipeline A"]
        }
        allocation_result = await trade_lifecycle.allocate_trade(trade_id, allocation_data)
        assert allocation_result["success"] is True
        
        # Process settlement
        settlement_data = {
            "delivery_confirmed": True,
            "actual_delivery_date": datetime.now().isoformat(),
            "quantity_delivered": 1000,
            "quality_specifications": {"sulfur": "0.5%", "gravity": "32.5"}
        }
        settlement_result = await trade_lifecycle.process_settlement(trade_id, settlement_data)
        assert settlement_result["success"] is True
        
        # Generate invoice
        invoice_result = await trade_lifecycle.generate_invoice(trade_id)
        assert invoice_result["success"] is True
        
        # Process payment
        payment_data = {
            "amount": 85000.0,
            "payment_method": "wire_transfer",
            "reference_number": "PAY123456"
        }
        payment_result = await trade_lifecycle.process_payment(trade_id, payment_data)
        assert payment_result["success"] is True
        
        # Check final status
        status_result = await trade_lifecycle.get_trade_status(trade_id)
        assert status_result["current_stage"] == TradeStage.COMPLETED.value
        assert len(status_result["stages_completed"]) == 8  # All stages completed

class TestEnhancedPositionManager:
    """Test enhanced position manager with new features"""
    
    @pytest.fixture
    def position_manager(self):
        return PositionManager()
    
    @pytest.fixture
    def sample_positions(self):
        return [
            {
                "commodity": "crude_oil",
                "net_volume": 1000.0,
                "avg_entry_price": 85.0,
                "notional_value": 85000.0
            },
            {
                "commodity": "natural_gas",
                "net_volume": 5000.0,
                "avg_entry_price": 3.50,
                "notional_value": 17500.0
            }
        ]
    
    @pytest.mark.asyncio
    async def test_calculate_positions(self, position_manager):
        """Test position calculation by commodity and period"""
        # Create some test positions first
        deal_data = {
            "deal_id": "TEST-DEAL-001",
            "commodity": "crude_oil",
            "quantity": 1000,
            "price": 85.0,
            "trade_type": "spot",
            "direction": "long",
            "sharia_compliant": True
        }
        position_manager.create_position(deal_data)
        
        # Calculate positions
        positions = await position_manager.calculate_positions("crude_oil", "monthly")
        
        assert len(positions) > 0
        assert positions[0]["commodity"] == "crude_oil"
        assert "net_volume" in positions[0]
        assert "avg_entry_price" in positions[0]
    
    def test_mark_to_market(self, position_manager, sample_positions):
        """Test mark-to-market calculation with multithreading"""
        mtm_value = position_manager.mark_to_market(sample_positions)
        
        assert isinstance(mtm_value, float)
        assert mtm_value > 0
        # Expected: 1000 * 85.0 + 5000 * 3.50 = 85000 + 17500 = 102500
        assert mtm_value == 102500.0
    
    @pytest.mark.asyncio
    async def test_hedge_accounting(self, position_manager):
        """Test hedge accounting effectiveness"""
        hedge_data = {
            "hedge_ratio": 0.85,
            "correlation": 0.90,
            "effective": True
        }
        
        is_effective = await position_manager.hedge_accounting(hedge_data)
        assert is_effective is True
        
        # Test ineffective hedge
        ineffective_hedge = {
            "hedge_ratio": 0.60,
            "correlation": 0.50,
            "effective": False
        }
        
        is_effective = await position_manager.hedge_accounting(ineffective_hedge)
        assert is_effective is False

class TestEnhancedShariaCompliance:
    """Test enhanced Sharia compliance features"""
    
    @pytest.fixture
    def sharia_validator(self):
        return IslamicTradingValidator()
    
    @pytest.fixture
    def sample_trade(self):
        return {
            "asset_type": "crude_oil",
            "interest_rate": 0.0,
            "uncertainty_level": 0.05,
            "has_asset": True,
            "asset_backing_ratio": 0.85
        }
    
    @pytest.mark.asyncio
    async def test_validate_transaction(self, sharia_validator, sample_trade):
        """Test comprehensive Sharia validation"""
        # Test compliant trade
        is_compliant = await sharia_validator.validate_transaction(sample_trade)
        assert is_compliant is True
        
        # Test non-compliant trade with interest
        non_compliant_trade = sample_trade.copy()
        non_compliant_trade["interest_rate"] = 0.05
        
        with pytest.raises(Exception) as exc_info:
            await sharia_validator.validate_transaction(non_compliant_trade)
        assert "Riba (interest) is prohibited" in str(exc_info.value.detail)
        
        # Test non-compliant trade with excessive gharar
        high_gharar_trade = sample_trade.copy()
        high_gharar_trade["uncertainty_level"] = 0.15
        
        with pytest.raises(Exception) as exc_info:
            await sharia_validator.validate_transaction(high_gharar_trade)
        assert "Excessive gharar" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_ensure_asset_backing(self, sharia_validator, sample_trade):
        """Test asset backing validation"""
        # Test trade with sufficient asset backing
        has_backing = await sharia_validator.ensure_asset_backing(sample_trade)
        assert has_backing is True
        
        # Test trade with insufficient asset backing
        insufficient_trade = sample_trade.copy()
        insufficient_trade["asset_backing_ratio"] = 0.50
        
        with pytest.raises(Exception) as exc_info:
            await sharia_validator.ensure_asset_backing(insufficient_trade)
        assert "Insufficient asset backing" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_ramadan_restrictions(self, sharia_validator):
        """Test Ramadan trading restrictions"""
        # Test with current date (will depend on when test is run)
        # This is a simplified test that doesn't rely on mocking
        is_restricted = await sharia_validator.is_ramadan_restricted()
        # Just verify the function runs without error
        assert isinstance(is_restricted, bool)
    
    @pytest.mark.asyncio
    async def test_generate_sharia_audit(self, sharia_validator):
        """Test Sharia audit report generation"""
        audit_report = await sharia_validator.generate_sharia_audit("TRADE-123")
        
        assert "audit_id" in audit_report
        assert audit_report["trade_id"] == "TRADE-123"
        assert audit_report["sharia_board_approval"] is True
        assert "compliance_score" in audit_report

class TestCreditManager:
    """Test credit management service"""
    
    @pytest.fixture
    def credit_manager(self):
        return CreditManager()
    
    @pytest.fixture
    def sample_credit_limit(self):
        return {
            "credit_limit": 1000000.0,
            "currency": "USD",
            "limit_type": "total",
            "collateral_required": False
        }
    
    @pytest.fixture
    def sample_positions(self):
        return [
            {
                "counterparty_id": "CP001",
                "notional_value": 500000.0,
                "unrealized_pnl": 25000.0
            },
            {
                "counterparty_id": "CP001",
                "notional_value": 300000.0,
                "unrealized_pnl": -15000.0
            }
        ]
    
    @pytest.mark.asyncio
    async def test_set_credit_limit(self, credit_manager, sample_credit_limit):
        """Test setting credit limit for counterparty"""
        result = await credit_manager.set_credit_limit("CP001", sample_credit_limit)
        
        assert result["success"] is True
        assert "credit_limit" in result
        assert result["credit_limit"]["counterparty_id"] == "CP001"
        assert result["credit_limit"]["credit_limit"] == 1000000.0
    
    @pytest.mark.asyncio
    async def test_calculate_exposure(self, credit_manager, sample_credit_limit, sample_positions):
        """Test exposure calculation"""
        # Set credit limit first
        await credit_manager.set_credit_limit("CP001", sample_credit_limit)
        
        # Calculate exposure
        result = await credit_manager.calculate_exposure("CP001", sample_positions)
        
        assert result["success"] is True
        assert "exposure" in result
        assert result["exposure"]["total_exposure"] == 800000.0  # 500k + 300k
        assert result["exposure"]["unrealized_pnl"] == 10000.0   # 25k - 15k
        assert result["exposure"]["net_exposure"] == 810000.0    # 800k + 10k
        assert result["exposure"]["utilization_ratio"] == 81.0   # 810k/1000k * 100
    
    @pytest.mark.asyncio
    async def test_check_credit_availability(self, credit_manager, sample_credit_limit, sample_positions):
        """Test credit availability checking"""
        # Set credit limit and calculate exposure
        await credit_manager.set_credit_limit("CP001", sample_credit_limit)
        await credit_manager.calculate_exposure("CP001", sample_positions)
        
        # Check if trade can be executed
        result = await credit_manager.check_credit_availability("CP001", 100000.0)
        
        assert result["success"] is True
        assert result["can_execute"] is True
        assert result["available_credit"] == 190000.0  # 1000k - 810k
        assert result["remaining_credit"] == 90000.0   # 190k - 100k
        
        # Test trade that exceeds available credit
        large_trade_result = await credit_manager.check_credit_availability("CP001", 200000.0)
        assert large_trade_result["can_execute"] is False
    
    @pytest.mark.asyncio
    async def test_generate_credit_report(self, credit_manager, sample_credit_limit, sample_positions):
        """Test credit report generation"""
        # Set up test data
        await credit_manager.set_credit_limit("CP001", sample_credit_limit)
        await credit_manager.calculate_exposure("CP001", sample_positions)
        
        # Generate single counterparty report
        single_report = await credit_manager.generate_credit_report("CP001")
        assert single_report["success"] is True
        assert "report" in single_report
        assert single_report["report"]["counterparty_id"] == "CP001"
        
        # Generate portfolio report
        portfolio_report = await credit_manager.generate_credit_report()
        assert portfolio_report["success"] is True
        assert "portfolio_summary" in portfolio_report["report"]
        assert portfolio_report["report"]["portfolio_summary"]["total_counterparties"] == 1

class TestRegulatoryReporting:
    """Test regulatory reporting service"""
    
    @pytest.fixture
    def regulatory_reporting(self):
        return RegulatoryReporting()
    
    @pytest.fixture
    def sample_trades(self):
        return [
            {
                "jurisdiction": "US",
                "commodity": "crude_oil",
                "quantity": 1000,
                "notional_value": 85000.0,
                "risk_level": "medium"
            },
            {
                "jurisdiction": "EU",
                "commodity": "electricity",
                "quantity": 500,
                "notional_value": 22500.0,
                "risk_level": "low"
            },
            {
                "jurisdiction": "Guyana",
                "commodity": "crude_oil",
                "quantity": 2000,
                "notional_value": 170000.0,
                "risk_level": "high"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_generate_cftc_reports(self, regulatory_reporting, sample_trades):
        """Test CFTC report generation"""
        result = await regulatory_reporting.generate_cftc_reports(sample_trades)
        
        assert result["success"] is True
        assert "report" in result
        assert result["report"]["regulator"] == "CFTC"
        assert result["report"]["jurisdiction"] == "US"
        assert result["report"]["total_trades"] == 1  # Only US trades
        assert result["report"]["total_notional"] == 85000.0
    
    @pytest.mark.asyncio
    async def test_generate_emir_reports(self, regulatory_reporting, sample_trades):
        """Test EMIR report generation"""
        result = await regulatory_reporting.generate_emir_reports(sample_trades)
        
        assert result["success"] is True
        assert "report" in result
        assert result["report"]["regulator"] == "EMIR"
        assert result["report"]["jurisdiction"] == "EU"
        assert result["report"]["total_trades"] == 1  # Only EU trades
    
    @pytest.mark.asyncio
    async def test_generate_acer_reports(self, regulatory_reporting, sample_trades):
        """Test ACER report generation"""
        result = await regulatory_reporting.generate_acer_reports(sample_trades)
        
        assert result["success"] is True
        assert "report" in result
        assert result["report"]["regulator"] == "ACER"
        assert result["report"]["total_trades"] == 1  # Only energy trades
    
    @pytest.mark.asyncio
    async def test_generate_guyana_epa_reports(self, regulatory_reporting, sample_trades):
        """Test Guyana EPA report generation"""
        result = await regulatory_reporting.generate_guyana_epa_reports(sample_trades)
        
        assert result["success"] is True
        assert "report" in result
        assert result["report"]["regulator"] == "EPA"
        assert result["report"]["jurisdiction"] == "Guyana"
        assert result["report"]["total_trades"] == 1  # Only Guyana trades
    
    @pytest.mark.asyncio
    async def test_anonymize_data(self, regulatory_reporting):
        """Test GDPR data anonymization"""
        user_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-1234",
            "age": 35,
            "preferences": ["energy", "trading"]
        }

        anonymized = await regulatory_reporting.anonymize_data(user_data)

        assert anonymized["gdpr_compliant"] is True
        assert "anon_" in anonymized["name"]
        assert "anon_" in anonymized["email"]
        assert "anon_" in anonymized["phone"]
        assert anonymized["age"] == 35  # Non-sensitive field preserved
        assert anonymized["preferences"] == ["energy", "trading"]  # Non-sensitive field preserved

if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v"])
