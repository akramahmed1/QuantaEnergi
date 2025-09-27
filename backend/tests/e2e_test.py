"""
End-to-End Tests for QuantaEnergi API
Tests the complete user journey: Auth → Trade → Position → ESG → DB Verification
"""

import pytest
import httpx
import asyncio
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

# Test data
TEST_USER = {"username": "testuser", "password": "testpass"}
TEST_TRADE = {"asset": "TEST", "quantity": 10, "price": 100}
TEST_TRADE_ID = 1
TEST_ESG_ID = 1

class TestE2E:
    """End-to-end test suite"""
    
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
        # Create test user with hashed password
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("testpass")
        
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hashed_password,
            is_active=True
        )
        
        # Create test trade
        test_trade = Trade(
            id=TEST_TRADE_ID,
            asset="AAPL",
            quantity=100,
            price=150.0
        )
        
        # Create test ESG data
        test_esg = ESG(
            id=TEST_ESG_ID,
            trade_id=TEST_TRADE_ID,
            co2=42.5,
            certs="gold"
        )
        
        try:
            db_session.add(test_user)
            db_session.add(test_trade)
            db_session.add(test_esg)
            db_session.commit()
            print(f"✓ Test data created: User testuser, Trade {TEST_TRADE_ID}, ESG {TEST_ESG_ID}")
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
    
    def test_login_get_token(self, setup_test_data):
        """Test 1: Login and get JWT token"""
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/auth/login",
                json=TEST_USER
            )
            
            assert response.status_code == 200
            token_data = response.json()
            assert "access_token" in token_data
            assert "token_type" in token_data
            assert token_data["token_type"] == "bearer"
            assert len(token_data["access_token"]) > 0
            print(f"✓ Login successful, token type: {token_data['token_type']}")
    
    def test_create_trade(self, auth_token):
        """Test 2: Create a new trade using JWT token"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/trades",
                json=TEST_TRADE,
                headers=headers
            )
            
            assert response.status_code == 200
            trade_data = response.json()
            assert "id" in trade_data
            assert "trade" in trade_data
            assert "user" in trade_data
            assert trade_data["trade"]["asset"] == TEST_TRADE["asset"]
            assert trade_data["user"] == TEST_USER["username"]
            assert trade_data["id"] > 1  # Real DB ID
            print(f"✓ Trade created: {trade_data}")
    
    def test_get_position(self, auth_token):
        """Test 3: Get position for existing trade"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        with httpx.Client() as client:
            response = client.get(
                f"{BASE_URL}/trades/{TEST_TRADE_ID}/position",
                headers=headers
            )
            
            assert response.status_code == 200
            position_data = response.json()
            # Position should include data from test trade (AAPL, qty=100, price=150)
            print(f"✓ Position retrieved: {position_data}")
    
    def test_track_esg(self, auth_token):
        """Test 4: Track ESG metrics for a trade"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/esg/track",
                json={"trade_id": TEST_TRADE_ID},
                headers=headers
            )
            
            assert response.status_code == 200
            esg_data = response.json()
            assert "co2" in esg_data  # Should include CO2 and certs data
            print(f"✓ ESG tracking successful: {esg_data}")
    
    def test_full_chain_verification(self, auth_token, db_session):
        """Test 5: Full chain test with database verification"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get initial counts
        initial_trade_count = db_session.query(Trade).count()
        initial_esg_count = db_session.query(ESG).count()
        
        with httpx.Client() as client:
            # 1. Create a new trade
            response = client.post(
                f"{BASE_URL}/trades",
                json={"asset": "E2E_TEST", "quantity": 50, "price": 200},
                headers=headers
            )
            assert response.status_code == 200
            trade_result = response.json()
            trade_id = trade_result["id"]
            print(f"✓ E2E Trade created with ID: {trade_id}")
            
            # 2. Track ESG for the new trade
            response = client.post(
                f"{BASE_URL}/esg/track",
                json={"trade_id": trade_id},
                headers=headers
            )
            assert response.status_code == 200
            esg_result = response.json()
            print(f"✓ E2E ESG tracking: {esg_result}")
            
            # 3. Verify data in database
            trade_query = db_session.query(Trade).filter(Trade.id == trade_id).first()
            if trade_query:
                print(f"✓ E2E Trade found in DB: {trade_query.asset}, qty={trade_query.quantity}, price={trade_query.price}")
            
            esg_query = db_session.query(ESG).filter(ESG.trade_id == trade_id).first()
            if esg_query:
                print(f"✓ E2E ESG found in DB: co2={esg_query.co2}, certs={esg_query.certs}")
            
            # 4. Verify counts increased
            final_trade_count = db_session.query(Trade).count()
            final_esg_count = db_session.query(ESG).count()
            assert final_trade_count > initial_trade_count
            assert final_esg_count > initial_esg_count
            print(f"✓ DB counts increased: trades {initial_trade_count}→{final_trade_count}, ESG {initial_esg_count}→{final_esg_count}")
            
            # 5. Cleanup test data
            try:
                db_session.execute(text("DELETE FROM esg WHERE trade_id > 1"))
                db_session.execute(text("DELETE FROM trades WHERE id > 1"))
                db_session.commit()
                print("✓ Test data cleaned up")
            except Exception as e:
                print(f"⚠ Cleanup warning: {e}")
                db_session.rollback()
    
    def test_unauthorized_access(self):
        """Test 6: Verify unauthorized access is blocked"""
        with httpx.Client() as client:
            # Try to access protected endpoint without token
            response = client.post(
                f"{BASE_URL}/trades",
                json=TEST_TRADE
            )
            assert response.status_code == 403  # HTTPBearer returns 403 for missing credentials
            print("✓ Unauthorized access properly blocked")
    
    def test_invalid_token(self):
        """Test 7: Verify invalid token is rejected"""
        headers = {"Authorization": "Bearer invalid_token_12345"}
        
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/trades",
                json=TEST_TRADE,
                headers=headers
            )
            assert response.status_code == 401
            print("✓ Invalid token properly rejected")
    
    def test_dashboard_endpoint(self, auth_token):
        """Test 8: Verify dashboard endpoint works with aggregates"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        with httpx.Client() as client:
            response = client.get(
                f"{BASE_URL}/dashboard",
                headers=headers
            )
            
            assert response.status_code == 200
            dashboard_data = response.json()
            assert "user" in dashboard_data
            assert "stats" in dashboard_data
            assert "trades" in dashboard_data["stats"]
            assert "avg_co2" in dashboard_data["stats"]
            assert dashboard_data["user"] == TEST_USER["username"]
            print(f"✓ Dashboard data: {dashboard_data}")

def test_health_check():
    """Test 9: Verify health check endpoint works"""
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        print("✓ Health check passed")

def test_swagger_docs():
    """Test 10: Verify Swagger UI is accessible"""
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/docs")
        assert response.status_code == 200
        print("✓ Swagger UI accessible")

def test_openapi_spec():
    """Test 11: Verify OpenAPI spec is available"""
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/openapi.json")
        assert response.status_code == 200
        spec_data = response.json()
        assert "info" in spec_data
        assert "paths" in spec_data
        print("✓ OpenAPI specification available")

# Cleanup function for manual verification
def cleanup_test_data():
    """Manual cleanup function for test data verification"""
    engine = create_engine(TEST_DB_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Show all trades
        trades = session.query(Trade).all()
        print(f"\n📊 All Trades in Database:")
        for trade in trades:
            print(f"  ID: {trade.id}, Asset: {trade.asset}, Qty: {trade.quantity}, Price: {trade.price}")
        
        # Show all ESG records
        esg_records = session.query(ESG).all()
        print(f"\n🌱 All ESG Records in Database:")
        for esg in esg_records:
            print(f"  ID: {esg.id}, Trade ID: {esg.trade_id}, CO2: {esg.co2}, Certs: {esg.certs}")
        
        # Show trade count
        trade_count = session.query(Trade).count()
        esg_count = session.query(ESG).count()
        print(f"\n📈 Database Summary:")
        print(f"  Total Trades: {trade_count}")
        print(f"  Total ESG Records: {esg_count}")
        
    except Exception as e:
        print(f"❌ Error during cleanup verification: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 QuantaEnergi E2E Test Suite")
    print("=" * 50)
    print("Run with: poetry run pytest tests/e2e_test.py -v")
    print("=" * 50)
    print("After tests, run cleanup_test_data() to verify DB changes")
    print("Manual verification:")
    print("1. Check Swagger UI at http://127.0.0.1:8000/docs")
    print("2. Look for 'Authorize' button in Swagger UI")
    print("3. Use pgAdmin to check database tables")
    print("4. Run: python -c 'from tests.e2e_test import cleanup_test_data; cleanup_test_data()'")
