"""
Test suite for compliance services
Tests Sharia compliance, regulatory reporting, and billing services
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from app.services.sharia_compliance import ShariaComplianceService, ComplianceStatus
from app.services.compliance_reporting import ComplianceReportingService, ReportType
from app.services.billing_service import BillingService, SubscriptionTier

class TestShariaComplianceService:
    """Test cases for Sharia compliance service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = ShariaComplianceService()
        self.sample_trade = {
            'id': 'test-trade-123',
            'commodity': 'electricity',
            'price': 50.0,
            'quantity': 100,
            'trade_type': 'spot',
            'delivery_date': '2024-02-01',
            'delivery_location': 'New York'
        }
    
    def test_halal_commodity_check(self):
        """Test halal commodity validation"""
        # Test halal commodity
        result = self.service._check_commodity_halal(self.sample_trade)
        assert result['status'] == ComplianceStatus.COMPLIANT.value
        assert 'halal' in result['message'].lower()
        
        # Test haram commodity
        haram_trade = self.sample_trade.copy()
        haram_trade['commodity'] = 'alcohol'
        result = self.service._check_commodity_halal(haram_trade)
        assert result['status'] == ComplianceStatus.NON_COMPLIANT.value
        assert 'haram' in result['message'].lower()
    
    def test_riba_compliance_check(self):
        """Test riba (usury) compliance checking"""
        # Test compliant profit margin
        result = self.service._check_riba_compliance(self.sample_trade)
        assert result['status'] in [ComplianceStatus.COMPLIANT.value, ComplianceStatus.REQUIRES_REVIEW.value]
        
        # Test excessive profit margin
        high_profit_trade = self.sample_trade.copy()
        high_profit_trade['price'] = 1000.0  # Very high price
        result = self.service._check_riba_compliance(high_profit_trade)
        assert result['status'] == ComplianceStatus.REQUIRES_REVIEW.value
    
    def test_gharar_compliance_check(self):
        """Test gharar (uncertainty) compliance checking"""
        # Test compliant trade with clear specifications
        result = self.service._check_gharar_compliance(self.sample_trade)
        assert result['status'] == ComplianceStatus.COMPLIANT.value
        
        # Test trade with missing delivery specifications
        incomplete_trade = self.sample_trade.copy()
        incomplete_trade['delivery_date'] = ''
        result = self.service._check_gharar_compliance(incomplete_trade)
        assert result['status'] == ComplianceStatus.NON_COMPLIANT.value
    
    def test_ramadan_trading_check(self):
        """Test Ramadan trading period checking"""
        result = self.service._check_ramadan_trading(self.sample_trade)
        assert result['status'] in [ComplianceStatus.COMPLIANT.value, ComplianceStatus.REQUIRES_REVIEW.value]
        assert 'ramadan' in result['message'].lower()
    
    def test_maysir_compliance_check(self):
        """Test maysir (gambling) compliance checking"""
        # Test spot trade (compliant)
        result = self.service._check_maysir_compliance(self.sample_trade)
        assert result['status'] == ComplianceStatus.COMPLIANT.value
        
        # Test speculative trade (non-compliant)
        speculative_trade = self.sample_trade.copy()
        speculative_trade['trade_type'] = 'speculation'
        result = self.service._check_maysir_compliance(speculative_trade)
        assert result['status'] == ComplianceStatus.NON_COMPLIANT.value
    
    def test_zakat_compliance_check(self):
        """Test zakat compliance checking"""
        result = self.service._check_zakat_compliance(self.sample_trade)
        assert result['status'] == ComplianceStatus.COMPLIANT.value
        assert 'zakat' in result['message'].lower()
    
    def test_complete_compliance_check(self):
        """Test complete Sharia compliance checking"""
        result = self.service.check_trade_compliance(self.sample_trade)
        
        assert 'trade_id' in result
        assert 'overall_status' in result
        assert 'compliance_checks' in result
        assert 'recommendations' in result
        assert 'compliance_score' in result
        assert 'checked_at' in result
        
        assert result['trade_id'] == self.sample_trade['id']
        assert isinstance(result['compliance_score'], (int, float))
        assert 0 <= result['compliance_score'] <= 100
    
    def test_sharia_board_approval(self):
        """Test Sharia board approval workflow"""
        result = self.service.get_sharia_board_approval('test-trade-123')
        
        assert 'trade_id' in result
        assert 'sharia_board_approval' in result
        assert 'approved_by' in result
        assert 'approval_date' in result
        assert 'fatwa_number' in result
        assert 'conditions' in result
        assert 'valid_until' in result
        
        assert result['trade_id'] == 'test-trade-123'
        assert result['sharia_board_approval'] is True

class TestComplianceReportingService:
    """Test cases for compliance reporting service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = ComplianceReportingService()
        self.sample_data = [
            {
                'id': 'trade-1',
                'commodity': 'electricity',
                'price': 50.0,
                'quantity': 100,
                'timestamp': datetime.now().isoformat(),
                'notional_amount': 5000.0
            },
            {
                'id': 'trade-2',
                'commodity': 'solar_energy',
                'price': 45.0,
                'quantity': 200,
                'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
                'notional_amount': 9000.0
            }
        ]
    
    def test_cftc_report_generation(self):
        """Test CFTC report generation"""
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        result = self.service.generate_report(
            report_type='cftc',
            start_date=start_date,
            end_date=end_date,
            data=self.sample_data,
            anonymize=True
        )
        
        assert 'report_id' in result
        assert 'report_type' in result
        assert 'report_name' in result
        assert 'generated_at' in result
        assert 'report_period' in result
        assert 'data_summary' in result
        assert 'compliance_status' in result
        assert 'anonymized' in result
        
        assert result['report_type'] == 'cftc'
        assert result['anonymized'] is True
        assert result['data_summary']['total_records'] == 2
    
    def test_emir_report_generation(self):
        """Test EMIR report generation"""
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        result = self.service.generate_report(
            report_type='emir',
            start_date=start_date,
            end_date=end_date,
            data=self.sample_data,
            anonymize=True
        )
        
        assert result['report_type'] == 'emir'
        assert result['anonymized'] is True
        assert result['data_summary']['total_records'] == 2
    
    def test_gdpr_report_generation(self):
        """Test GDPR report generation"""
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        result = self.service.generate_report(
            report_type='gdpr',
            start_date=start_date,
            end_date=end_date,
            data=self.sample_data,
            anonymize=True
        )
        
        assert result['report_type'] == 'gdpr'
        assert result['anonymized'] is True
    
    def test_guyana_report_generation(self):
        """Test Guyana report generation"""
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        result = self.service.generate_report(
            report_type='guyana',
            start_date=start_date,
            end_date=end_date,
            data=self.sample_data,
            anonymize=True
        )
        
        assert result['report_type'] == 'guyana'
        assert result['anonymized'] is True
    
    def test_data_anonymization(self):
        """Test data anonymization functionality"""
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        result = self.service.generate_report(
            report_type='cftc',
            start_date=start_date,
            end_date=end_date,
            data=self.sample_data,
            anonymize=True
        )
        
        # Check that sensitive data is anonymized
        for record in result['report_data']:
            if 'trader_id' in record and record['trader_id']:
                assert record['trader_id'].startswith('ANON_')
    
    def test_csv_export(self):
        """Test CSV export functionality"""
        report = {
            'report_id': 'test-report-123',
            'report_data': [
                {'field1': 'value1', 'field2': 'value2'},
                {'field1': 'value3', 'field2': 'value4'}
            ]
        }
        
        csv_content = self.service.export_report_csv(report)
        
        assert isinstance(csv_content, str)
        assert 'field1,field2' in csv_content
        assert 'value1,value2' in csv_content
        assert 'value3,value4' in csv_content
    
    def test_consolidated_report_generation(self):
        """Test consolidated report generation"""
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        result = self.service.generate_consolidated_report(
            report_types=['cftc', 'emir', 'gdpr'],
            start_date=start_date,
            end_date=end_date,
            data=self.sample_data
        )
        
        assert 'consolidated_report_id' in result
        assert 'individual_reports' in result
        assert 'overall_compliance_status' in result
        assert 'summary' in result
        
        assert len(result['individual_reports']) == 3
        assert 'cftc' in result['individual_reports']
        assert 'emir' in result['individual_reports']
        assert 'gdpr' in result['individual_reports']

class TestBillingService:
    """Test cases for billing service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = BillingService()
        self.sample_user = {
            'email': 'test@example.com',
            'name': 'Test User',
            'user_id': 'user-123'
        }
    
    def test_customer_creation(self):
        """Test customer creation"""
        result = self.service.create_customer(self.sample_user)
        
        assert 'customer_id' in result
        assert 'email' in result
        assert 'name' in result
        assert 'created_at' in result
        assert 'subscription_status' in result
        
        assert result['email'] == self.sample_user['email']
        assert result['name'] == self.sample_user['name']
    
    def test_subscription_creation(self):
        """Test subscription creation"""
        # First create a customer
        customer = self.service.create_customer(self.sample_user)
        
        # Then create a subscription
        result = self.service.create_subscription(
            customer_id=customer['customer_id'],
            plan_tier='basic'
        )
        
        assert 'subscription_id' in result
        assert 'customer_id' in result
        assert 'plan_tier' in result
        assert 'status' in result
        assert 'price' in result
        assert 'currency' in result
        
        assert result['customer_id'] == customer['customer_id']
        assert result['plan_tier'] == 'basic'
    
    def test_subscription_retrieval(self):
        """Test subscription retrieval"""
        # Create customer and subscription
        customer = self.service.create_customer(self.sample_user)
        subscription = self.service.create_subscription(
            customer_id=customer['customer_id'],
            plan_tier='professional'
        )
        
        # Retrieve subscription
        result = self.service.get_subscription(subscription['subscription_id'])
        
        assert 'subscription_id' in result
        assert 'customer_id' in result
        assert 'status' in result
        assert 'current_period_start' in result
        assert 'current_period_end' in result
        
        assert result['subscription_id'] == subscription['subscription_id']
    
    def test_subscription_cancellation(self):
        """Test subscription cancellation"""
        # Create customer and subscription
        customer = self.service.create_customer(self.sample_user)
        subscription = self.service.create_subscription(
            customer_id=customer['customer_id'],
            plan_tier='enterprise'
        )
        
        # Cancel subscription
        result = self.service.cancel_subscription(
            subscription_id=subscription['subscription_id'],
            immediately=False
        )
        
        assert 'subscription_id' in result
        assert 'status' in result
        assert 'cancelled_at' in result
        assert 'cancel_at_period_end' in result
        
        assert result['subscription_id'] == subscription['subscription_id']
        assert result['status'] in ['cancelled', 'cancelling']
    
    def test_payment_intent_creation(self):
        """Test payment intent creation"""
        result = self.service.create_payment_intent(
            amount=99.99,
            currency='usd',
            customer_id='test-customer-123'
        )
        
        assert 'payment_intent_id' in result
        assert 'amount' in result
        assert 'currency' in result
        assert 'status' in result
        assert 'client_secret' in result
        
        assert result['amount'] == 99.99
        assert result['currency'] == 'usd'
    
    def test_usage_stats_retrieval(self):
        """Test usage statistics retrieval"""
        customer_id = 'test-customer-123'
        period_start = datetime.now() - timedelta(days=30)
        period_end = datetime.now()
        
        result = self.service.get_usage_stats(
            customer_id=customer_id,
            period_start=period_start,
            period_end=period_end
        )
        
        assert 'customer_id' in result
        assert 'period' in result
        assert 'trades_count' in result
        assert 'api_calls_count' in result
        assert 'storage_used_gb' in result
        assert 'generated_at' in result
        
        assert result['customer_id'] == customer_id
        assert isinstance(result['trades_count'], int)
        assert isinstance(result['api_calls_count'], int)
    
    def test_available_plans_retrieval(self):
        """Test available plans retrieval"""
        result = self.service.get_available_plans()
        
        assert 'plans' in result
        assert 'generated_at' in result
        
        plans = result['plans']
        assert 'basic' in plans
        assert 'professional' in plans
        assert 'enterprise' in plans
        
        # Check basic plan structure
        basic_plan = plans['basic']
        assert 'name' in basic_plan
        assert 'price' in basic_plan
        assert 'currency' in basic_plan
        assert 'interval' in basic_plan
        assert 'features' in basic_plan
        assert 'limits' in basic_plan
        
        assert basic_plan['price'] == 99.00
        assert basic_plan['currency'] == 'usd'
        assert basic_plan['interval'] == 'month'

if __name__ == '__main__':
    pytest.main([__file__])
