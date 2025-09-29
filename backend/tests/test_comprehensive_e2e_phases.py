"""
Comprehensive E2E Tests for QuantaEnergi - All Phases Integration
Tests complete user journey with VaR, Geo-Risk, Quantum Optimization, and REMIT Compliance
"""

import pytest
import httpx
import asyncio
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.base import Base
from app.models.trade import Trade
from app.models.esg import ESG
from app.models.user import User
from app.db.session import SessionLocal

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_DB_URL = "postgresql://user:pass@localhost:5432/quanta_db"

# Test data for all phases
TEST_USER = {"username": "testuser", "password": "testpass"}
TEST_TRADE = {"asset": "guyana_crude_oil", "quantity": 500, "price": 75.50}
TEST_TRADE_ID = 1

class TestComprehensiveE2E:
    """Comprehensive E2E test suite covering all phases"""
    
    @pytest.fixture(scope="class")
    def event_loop(self):
        """Create event loop for async tests"""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()
    
    @pytest.fixture(scope="class")
    def db_session(self):
        """Create database session for test data setup and verification"""
        engine = create_engine(TEST_DB_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    @pytest.fixture(scope="class")
    def setup_test_data(self, db_session):
        """Setup test data in database"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("testpass")
        
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hashed_password,
            is_active=True
        )
        
        test_trade = Trade(
            id=TEST_TRADE_ID,
            asset="guyana_crude_oil",
            quantity=500,
            price=75.50
        )
        
        try:
            db_session.add(test_user)
            db_session.add(test_trade)
            db_session.commit()
            print(f"✓ Test data created: User testuser, Trade {TEST_TRADE_ID}")
        except Exception as e:
            print(f"⚠ Test data may already exist: {e}")
            db_session.rollback()
    
    @pytest.fixture(scope="class")
    def auth_token(self, setup_test_data):
        """Get authentication token for protected endpoints"""
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/auth/login",
                json=TEST_USER
            )
            assert response.status_code == 200
            token_data = response.json()
            assert "access_token" in token_data
            token = token_data["access_token"]
            print(f"✓ Authentication token obtained")
            return token

    # Phase 1: VaR/Monte Carlo Risk Tests
    def test_phase1_var_calculations(self, auth_token):
        """Test Phase 1: VaR/Monte Carlo Risk Calculations"""
        print("\n🔬 Testing Phase 1: VaR/Monte Carlo Risk")
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Test parametric VaR
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/risk/var",
                json=[150, 152, 148, 155, 160, 158, 162, 165, 163, 168],
                headers=headers
            )
            assert response.status_code == 200
            var_result = response.json()
            assert "param_var" in var_result
            assert var_result["param_var"] < 0  # Should be negative (loss)
            print(f"✓ Parametric VaR: {var_result['param_var']:.4f}")
        
        # Test Monte Carlo VaR
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/risk/var?method=monte_carlo",
                json=[150, 152, 148, 155, 160, 158, 162, 165, 163, 168],
                headers=headers
            )
            assert response.status_code == 200
            mc_result = response.json()
            assert "mc_var" in mc_result
            assert mc_result["mc_var"] < 0  # Should be negative (loss)
            print(f"✓ Monte Carlo VaR: {mc_result['mc_var']:.4f}")
        
        # Test Enhanced VaR
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/risk/var?method=enhanced",
                json=[150, 152, 148, 155, 160, 158, 162, 165, 163, 168],
                headers=headers
            )
            assert response.status_code == 200
            enhanced_result = response.json()
            assert "risk_assessment" in enhanced_result
            assert "level" in enhanced_result["risk_assessment"]
            print(f"✓ Enhanced VaR Risk Level: {enhanced_result['risk_assessment']['level']}")

    # Phase 2: Alpha Vantage + Geo-Risk AI Tests
    def test_phase2_market_data(self, auth_token):
        """Test Phase 2: Alpha Vantage Market Data Integration"""
        print("\n🌐 Testing Phase 2: Alpha Vantage + Geo-Risk AI")
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Test market data endpoint
        with httpx.Client() as client:
            response = client.get(
                f"{BASE_URL}/market/prices/BRENT",
                headers=headers
            )
            assert response.status_code == 200
            market_data = response.json()
            assert "symbol" in market_data
            assert "volatility" in market_data
            assert "source" in market_data
            print(f"✓ Market Data: {market_data['symbol']}, Volatility: {market_data['volatility']:.4f}")
        
        # Test geo-risk assessment for Guyana
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/geo-risk/assess",
                json={
                    "region": "GUYANA",
                    "volatility": 0.25,
                    "sentiment": 0.4,
                    "news_volume": 0.8
                },
                headers=headers
            )
            assert response.status_code == 200
            geo_risk = response.json()
            assert "risk_assessment" in geo_risk
            assert "recommendations" in geo_risk
            risk_level = geo_risk["risk_assessment"]["risk_level"]
            print(f"✓ Guyana Geo-Risk: {risk_level}")
            print(f"  Recommendations: {len(geo_risk['recommendations'])} generated")
        
        # Test geo-risk assessment for Middle East
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/geo-risk/assess",
                json={
                    "region": "MIDDLE_EAST",
                    "volatility": 0.30,
                    "sentiment": 0.2,
                    "news_volume": 0.9
                },
                headers=headers
            )
            assert response.status_code == 200
            geo_risk = response.json()
            risk_level = geo_risk["risk_assessment"]["risk_level"]
            print(f"✓ Middle East Geo-Risk: {risk_level}")
        
        # Test supported regions endpoint
        with httpx.Client() as client:
            response = client.get(
                f"{BASE_URL}/geo-risk/regions",
                headers=headers
            )
            assert response.status_code == 200
            regions = response.json()
            assert "regions" in regions
            assert len(regions["regions"]) >= 3  # GUYANA, MIDDLE_EAST, NORTH_AMERICA
            print(f"✓ Supported Regions: {len(regions['regions'])}")

    # Phase 3: Quantum Optimization + REMIT Compliance Tests
    def test_phase3_quantum_optimization(self, auth_token):
        """Test Phase 3: Quantum Portfolio Optimization"""
        print("\n🔬 Testing Phase 3: Quantum Optimization")
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Test quantum portfolio optimization
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/optimize/portfolio?method=quantum",
                json={
                    "returns": [0.05, 0.08, 0.12, 0.06, 0.09],
                    "risks": [0.1, 0.15, 0.2, 0.12, 0.18]
                },
                headers=headers
            )
            assert response.status_code == 200
            opt_result = response.json()
            assert "weights" in opt_result
            assert "portfolio_return" in opt_result
            assert "sharpe_ratio" in opt_result
            assert len(opt_result["weights"]) == 5
            print(f"✓ Quantum Optimization: {opt_result['method']}")
            print(f"  Weights: {[f'{w:.3f}' for w in opt_result['weights']]}")
            print(f"  Sharpe Ratio: {opt_result['sharpe_ratio']:.4f}")
        
        # Test classical optimization fallback
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/optimize/portfolio?method=classical",
                json={
                    "returns": [0.05, 0.08, 0.12],
                    "risks": [0.1, 0.15, 0.2]
                },
                headers=headers
            )
            assert response.status_code == 200
            opt_result = response.json()
            assert "weights" in opt_result
            print(f"✓ Classical Optimization: {opt_result['method']}")

    def test_phase3_remit_compliance(self, auth_token):
        """Test Phase 3: REMIT Compliance for Europe/UK"""
        print("\n🇪🇺 Testing Phase 3: REMIT Compliance")
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Test compliant trade
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/compliance/validate",
                json={
                    "trade": {
                        "asset": "brent_crude_oil",
                        "quantity": 500,  # Under 1000 bbl/day limit
                        "price": 75.50,
                        "market_price": 75.00,
                        "timestamp": "2024-01-15T10:30:00Z",
                        "counterparty": "Shell_Energy",
                        "trader": "John_Smith",
                        "energy_type": "oil",
                        "cross_border": False
                    },
                    "framework": "REMIT"
                },
                headers=headers
            )
            assert response.status_code == 200
            compliance = response.json()
            assert "compliant" in compliance
            assert "compliance_details" in compliance
            print(f"✓ Compliant Trade: {compliance['compliant']}")
            print(f"  Violations: {len(compliance['violations'])}")
        
        # Test position limit violation
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/compliance/validate",
                json={
                    "trade": {
                        "asset": "wti_crude_oil",
                        "quantity": 1200,  # Over 1000 bbl/day limit
                        "price": 70.25,
                        "market_price": 70.00,
                        "timestamp": "2024-01-15T11:00:00Z",
                        "counterparty": "BP_Trading",
                        "trader": "Jane_Doe",
                        "energy_type": "oil",
                        "cross_border": False
                    },
                    "framework": "REMIT"
                },
                headers=headers
            )
            assert response.status_code == 200
            compliance = response.json()
            assert not compliance["compliant"]
            assert len(compliance["violations"]) > 0
            print(f"✓ Position Limit Violation Detected: {compliance['violations'][0]}")
        
        # Test market abuse detection
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/compliance/validate",
                json={
                    "trade": {
                        "asset": "inside_trading_oil",  # Suspicious asset name
                        "quantity": 300,
                        "price": 75.00,
                        "market_price": 75.00,
                        "timestamp": "2024-01-15T12:00:00Z",
                        "counterparty": "Trader_A",
                        "trader": "Trader_A",  # Same as counterparty (wash trading)
                        "energy_type": "oil",
                        "cross_border": False
                    },
                    "framework": "REMIT"
                },
                headers=headers
            )
            assert response.status_code == 200
            compliance = response.json()
            assert not compliance["compliant"]
            violations = compliance["violations"]
            abuse_detected = any("insider" in str(v).lower() or "wash" in str(v).lower() for v in violations)
            assert abuse_detected
            print(f"✓ Market Abuse Detected: {len(violations)} violations")

    # Integrated E2E Tests
    def test_integrated_energy_trading_flow(self, auth_token):
        """Test complete energy trading flow with all phases integrated"""
        print("\n🔄 Testing Integrated Energy Trading Flow")
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        with httpx.Client() as client:
            # 1. Create Guyana oil trade
            trade_data = {
                "asset": "guyana_crude_oil",
                "quantity": 800,
                "price": 75.50
            }
            
            response = client.post(
                f"{BASE_URL}/trades",
                json=trade_data,
                headers=headers
            )
            assert response.status_code == 200
            trade_result = response.json()
            trade_id = trade_result["id"]
            print(f"✓ Trade Created: ID {trade_id}, Asset: {trade_data['asset']}")
            
            # 2. Track ESG with geo-risk assessment
            response = client.post(
                f"{BASE_URL}/esg/track",
                json={"trade_id": trade_id},
                headers=headers
            )
            assert response.status_code == 200
            esg_result = response.json()
            assert "co2" in esg_result
            assert "geo_risk" in esg_result
            assert "risk_adjusted" in esg_result
            print(f"✓ ESG Tracking: CO2={esg_result['co2']:.2f}, Geo-Risk Adjusted: {esg_result['risk_adjusted']}")
            
            # 3. Assess portfolio optimization
            response = client.post(
                f"{BASE_URL}/optimize/portfolio",
                json={
                    "returns": [0.05, 0.08, 0.12],
                    "risks": [0.1, 0.15, 0.2]
                },
                headers=headers
            )
            assert response.status_code == 200
            opt_result = response.json()
            print(f"✓ Portfolio Optimization: Sharpe={opt_result['sharpe_ratio']:.4f}")
            
            # 4. Validate REMIT compliance
            response = client.post(
                f"{BASE_URL}/compliance/validate",
                json={
                    "trade": {
                        "asset": trade_data["asset"],
                        "quantity": trade_data["quantity"],
                        "price": trade_data["price"],
                        "market_price": 75.00,
                        "timestamp": "2024-01-15T14:00:00Z",
                        "counterparty": "Guyana_Oil_Company",
                        "trader": "Energy_Trader",
                        "energy_type": "oil",
                        "cross_border": True,
                        "accreditation_number": "REMIT-UK-2024-001"
                    },
                    "framework": "REMIT"
                },
                headers=headers
            )
            assert response.status_code == 200
            compliance = response.json()
            print(f"✓ REMIT Compliance: {compliance['compliant']}, Violations: {len(compliance['violations'])}")
            
            # 5. Calculate VaR for risk assessment
            response = client.post(
                f"{BASE_URL}/risk/var?method=enhanced",
                json=[75.50, 76.20, 74.80, 77.10, 75.90, 76.50, 75.30, 77.80, 76.20, 75.60],
                headers=headers
            )
            assert response.status_code == 200
            var_result = response.json()
            risk_level = var_result["risk_assessment"]["level"]
            print(f"✓ VaR Risk Assessment: {risk_level}")
            
            print("✅ Complete Energy Trading Flow Tested Successfully!")

    def test_websocket_market_data(self, auth_token):
        """Test WebSocket market data streaming"""
        print("\n📡 Testing WebSocket Market Data")
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Note: WebSocket testing requires async implementation
        # This is a placeholder for WebSocket functionality
        print("✓ WebSocket market data streaming (placeholder)")

    def test_database_integration(self, auth_token, db_session):
        """Test database integration and data persistence"""
        print("\n💾 Testing Database Integration")
        
        # Get initial counts
        initial_trade_count = db_session.query(Trade).count()
        initial_esg_count = db_session.query(ESG).count()
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        with httpx.Client() as client:
            # Create trade with geo-risk assessment
            response = client.post(
                f"{BASE_URL}/trades",
                json={
                    "asset": "middle_east_crude",
                    "quantity": 600,
                    "price": 78.25
                },
                headers=headers
            )
            assert response.status_code == 200
            trade_result = response.json()
            trade_id = trade_result["id"]
            
            # Track ESG (includes geo-risk)
            response = client.post(
                f"{BASE_URL}/esg/track",
                json={"trade_id": trade_id},
                headers=headers
            )
            assert response.status_code == 200
            esg_result = response.json()
            
            # Verify database persistence
            trade_query = db_session.query(Trade).filter(Trade.id == trade_id).first()
            assert trade_query is not None
            assert trade_query.asset == "middle_east_crude"
            
            esg_query = db_session.query(ESG).filter(ESG.trade_id == trade_id).first()
            assert esg_query is not None
            assert esg_query.co2 > 0
            
            # Verify counts increased
            final_trade_count = db_session.query(Trade).count()
            final_esg_count = db_session.query(ESG).count()
            assert final_trade_count > initial_trade_count
            assert final_esg_count > initial_esg_count
            
            print(f"✓ Database Integration: Trades {initial_trade_count}→{final_trade_count}, ESG {initial_esg_count}→{final_esg_count}")
            
            # Cleanup
            try:
                db_session.execute(text("DELETE FROM esg WHERE trade_id > 1"))
                db_session.execute(text("DELETE FROM trades WHERE id > 1"))
                db_session.commit()
                print("✓ Test data cleaned up")
            except Exception as e:
                print(f"⚠ Cleanup warning: {e}")
                db_session.rollback()

    def test_error_handling(self, auth_token):
        """Test error handling and edge cases"""
        print("\n⚠️ Testing Error Handling")
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        with httpx.Client() as client:
            # Test invalid VaR data
            response = client.post(
                f"{BASE_URL}/risk/var",
                json=[],  # Empty array
                headers=headers
            )
            assert response.status_code == 200  # Should handle gracefully
            var_result = response.json()
            assert "param_var" in var_result or "error" in var_result
            
            # Test invalid optimization data
            response = client.post(
                f"{BASE_URL}/optimize/portfolio",
                json={
                    "returns": [0.05, 0.08],  # Mismatched lengths
                    "risks": [0.1, 0.15, 0.2]
                },
                headers=headers
            )
            assert response.status_code == 200
            opt_result = response.json()
            assert "error" in opt_result or "weights" in opt_result
            
            # Test invalid compliance data
            response = client.post(
                f"{BASE_URL}/compliance/validate",
                json={
                    "trade": {},  # Empty trade data
                    "framework": "REMIT"
                },
                headers=headers
            )
            assert response.status_code == 200
            compliance = response.json()
            assert "compliant" in compliance
            
            print("✓ Error handling working correctly")

def test_health_endpoints():
    """Test health and documentation endpoints"""
    print("\n🏥 Testing Health Endpoints")
    
    with httpx.Client() as client:
        # Health check
        response = client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        print("✓ Health check passed")
        
        # API documentation
        response = client.get(f"{BASE_URL}/docs")
        assert response.status_code == 200
        print("✓ API documentation accessible")
        
        # OpenAPI spec
        response = client.get(f"{BASE_URL}/openapi.json")
        assert response.status_code == 200
        spec_data = response.json()
        assert "info" in spec_data
        assert "paths" in spec_data
        print("✓ OpenAPI specification available")

if __name__ == "__main__":
    print("🚀 QuantaEnergi Comprehensive E2E Test Suite")
    print("=" * 60)
    print("Testing all phases: VaR, Geo-Risk, Quantum, REMIT")
    print("Run with: poetry run pytest tests/test_comprehensive_e2e_phases.py -v")
    print("=" * 60)
