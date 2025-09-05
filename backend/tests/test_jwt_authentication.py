"""
Test JWT Authentication System for ETRM/CTRM Platform
Tests token generation, validation, role-based access, and rate limiting
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.jwt_auth import JWTAuthManager, auth_manager, authenticate_user, get_current_user
from app.middleware.rate_limiter import RateLimiter, rate_limiter

class TestJWTAuthManager:
    """Test JWT Authentication Manager"""
    
    @pytest.fixture
    def auth_mgr(self):
        """Create auth manager instance"""
        return JWTAuthManager()
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing"""
        return {
            "user_id": "test_user_001",
            "username": "testuser",
            "email": "test@quantaenergi.com",
            "organization_id": "123e4567-e89b-12d3-a456-426614174000",
            "role": "trader",
            "is_active": True
        }
    
    def test_create_access_token_success(self, auth_mgr, sample_user_data):
        """Test successful access token creation"""
        token = auth_mgr.create_access_token(sample_user_data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        payload = auth_mgr.verify_token(token)
        assert payload["user_id"] == sample_user_data["user_id"]
        assert payload["username"] == sample_user_data["username"]
        assert payload["type"] == "access"
    
    def test_create_refresh_token_success(self, auth_mgr, sample_user_data):
        """Test successful refresh token creation"""
        token = auth_mgr.create_refresh_token(sample_user_data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        payload = auth_mgr.verify_refresh_token(token)
        assert payload["user_id"] == sample_user_data["user_id"]
        assert payload["type"] == "refresh"
    
    def test_verify_token_success(self, auth_mgr, sample_user_data):
        """Test successful token verification"""
        token = auth_mgr.create_access_token(sample_user_data)
        payload = auth_mgr.verify_token(token)
        
        assert payload["user_id"] == sample_user_data["user_id"]
        assert payload["username"] == sample_user_data["username"]
        assert payload["role"] == sample_user_data["role"]
    
    def test_verify_token_expired(self, auth_mgr, sample_user_data):
        """Test token verification with expired token"""
        # Create token with very short expiration
        token = auth_mgr.create_access_token(
            sample_user_data, 
            expires_delta=timedelta(seconds=-1)  # Expired 1 second ago
        )
        
        with pytest.raises(HTTPException) as exc_info:
            auth_mgr.verify_token(token)
        
        assert exc_info.value.status_code == 401
        assert "expired" in str(exc_info.value.detail).lower()
    
    def test_verify_token_invalid(self, auth_mgr):
        """Test token verification with invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            auth_mgr.verify_token("invalid_token")
        
        assert exc_info.value.status_code == 401
        assert "invalid" in str(exc_info.value.detail).lower()
    
    def test_verify_token_blacklisted(self, auth_mgr, sample_user_data):
        """Test token verification with blacklisted token"""
        token = auth_mgr.create_access_token(sample_user_data)
        
        # Revoke token
        auth_mgr.revoke_token(token)
        
        with pytest.raises(HTTPException) as exc_info:
            auth_mgr.verify_token(token)
        
        assert exc_info.value.status_code == 401
        assert "revoked" in str(exc_info.value.detail).lower()
    
    def test_check_permission_admin(self, auth_mgr):
        """Test permission check for admin role"""
        # Admin should have all permissions
        assert auth_mgr.check_permission("admin", "any_permission") == True
        assert auth_mgr.check_permission("admin", "trade_capture") == True
        assert auth_mgr.check_permission("admin", "risk_edit") == True
    
    def test_check_permission_trader(self, auth_mgr):
        """Test permission check for trader role"""
        # Trader should have trader permissions
        assert auth_mgr.check_permission("trader", "trade_capture") == True
        assert auth_mgr.check_permission("trader", "position_view") == True
        assert auth_mgr.check_permission("trader", "risk_edit") == False  # Not a risk manager permission
    
    def test_check_permission_viewer(self, auth_mgr):
        """Test permission check for viewer role"""
        # Viewer should have limited permissions
        assert auth_mgr.check_permission("viewer", "trade_view") == True
        assert auth_mgr.check_permission("viewer", "position_view") == True
        assert auth_mgr.check_permission("viewer", "trade_capture") == False  # Not a viewer permission
    
    def test_check_permission_unknown_role(self, auth_mgr):
        """Test permission check for unknown role"""
        # Unknown role should have no permissions
        assert auth_mgr.check_permission("unknown_role", "any_permission") == False
    
    def test_hash_password(self, auth_mgr):
        """Test password hashing"""
        password = "test_password_123"
        hashed = auth_mgr.hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password_correct(self, auth_mgr):
        """Test password verification with correct password"""
        password = "test_password_123"
        hashed = auth_mgr.hash_password(password)
        
        assert auth_mgr.verify_password(password, hashed) == True
    
    def test_verify_password_incorrect(self, auth_mgr):
        """Test password verification with incorrect password"""
        password = "test_password_123"
        wrong_password = "wrong_password_456"
        hashed = auth_mgr.hash_password(password)
        
        assert auth_mgr.verify_password(wrong_password, hashed) == False

@pytest.mark.asyncio
async def test_authenticate_user_success():
    """Test successful user authentication"""
    # Test with mock user
    result = await authenticate_user("admin", "admin123")
    
    assert result is not None
    assert result["username"] == "admin"
    assert result["role"] == "admin"
    assert result["is_active"] == True

@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials():
    """Test authentication with invalid credentials"""
    # Test with wrong password
    result = await authenticate_user("admin", "wrong_password")
    assert result is None
    
    # Test with non-existent user
    result = await authenticate_user("nonexistent", "password")
    assert result is None

@pytest.mark.asyncio
async def test_get_current_user_success():
    """Test getting current user from valid token"""
    # Create a valid token
    user_data = {
        "user_id": "test_user_001",
        "username": "testuser",
        "email": "test@quantaenergi.com",
        "organization_id": "123e4567-e89b-12d3-a456-426614174000",
        "role": "trader"
    }
    
    token = auth_manager.create_access_token(user_data)
    
    # Mock the dependency
    with patch('app.core.jwt_auth.oauth2_scheme') as mock_scheme:
        mock_scheme.return_value = token
        
        user = await get_current_user(token)
        
        assert user["user_id"] == user_data["user_id"]
        assert user["username"] == user_data["username"]
        assert user["role"] == user_data["role"]
        assert "permissions" in user

@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    """Test getting current user with invalid token"""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("invalid_token")
    
    assert exc_info.value.status_code == 401

class TestRateLimiter:
    """Test Rate Limiter"""
    
    @pytest.fixture
    def rate_limiter_instance(self):
        """Create rate limiter instance"""
        return RateLimiter()
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_success(self, rate_limiter_instance):
        """Test successful rate limit check"""
        user_id = "test_user"
        endpoint = "trade_capture"
        user_role = "trader"
        organization_id = "test_org"
        organization_tier = "tier1"
        
        # First request should be allowed
        is_allowed, rate_info = await rate_limiter_instance.check_rate_limit(
            user_id, endpoint, user_role, organization_id, organization_tier
        )
        
        assert is_allowed == True
        assert rate_info["allowed"] == True
        assert "user_limit" in rate_info
        assert "org_limit" in rate_info
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeded(self, rate_limiter_instance):
        """Test rate limit exceeded scenario"""
        user_id = "test_user"
        endpoint = "trade_capture"
        user_role = "trader"
        organization_id = "test_org"
        organization_tier = "tier1"
        
        # Make many requests to exceed limit
        for i in range(25):  # Exceed the 20 requests per minute limit
            is_allowed, rate_info = await rate_limiter_instance.check_rate_limit(
                user_id, endpoint, user_role, organization_id, organization_tier
            )
            
            if i < 20:
                assert is_allowed == True
            else:
                assert is_allowed == False
                assert rate_info["allowed"] == False
                break
    
    @pytest.mark.asyncio
    async def test_get_rate_limit_status(self, rate_limiter_instance):
        """Test getting rate limit status"""
        user_id = "test_user"
        endpoint = "market_data"
        user_role = "trader"
        organization_id = "test_org"
        organization_tier = "tier1"
        
        status = await rate_limiter_instance.get_rate_limit_status(
            user_id, endpoint, user_role, organization_id, organization_tier
        )
        
        assert "user_limit" in status
        assert "org_limit" in status
        assert "allowed" in status
        assert status["endpoint"] == endpoint
        assert status["user_role"] == user_role

@pytest.mark.asyncio
async def test_integration_10_auth_attempts():
    """Integration test with 10 authentication attempts as specified in PRD"""
    auth_mgr = JWTAuthManager()
    rate_limiter_instance = RateLimiter()
    
    user_data = {
        "user_id": "integration_test_user",
        "username": "integration_test",
        "email": "integration@quantaenergi.com",
        "organization_id": "123e4567-e89b-12d3-a456-426614174000",
        "role": "trader",
        "is_active": True
    }
    
    try:
        # Attempt 1: Create access token
        access_token = auth_mgr.create_access_token(user_data)
        assert access_token is not None
        
        # Attempt 2: Create refresh token
        refresh_token = auth_mgr.create_refresh_token(user_data)
        assert refresh_token is not None
        
        # Attempt 3: Verify access token
        payload = auth_mgr.verify_token(access_token)
        assert payload["user_id"] == user_data["user_id"]
        
        # Attempt 4: Verify refresh token
        refresh_payload = auth_mgr.verify_refresh_token(refresh_token)
        assert refresh_payload["user_id"] == user_data["user_id"]
        
        # Attempt 5: Check permissions
        assert auth_mgr.check_permission("trader", "trade_capture") == True
        assert auth_mgr.check_permission("trader", "risk_edit") == False
        
        # Attempt 6: Hash and verify password
        password = "test_password_123"
        hashed = auth_mgr.hash_password(password)
        assert auth_mgr.verify_password(password, hashed) == True
        
        # Attempt 7: Rate limit check
        is_allowed, rate_info = await rate_limiter_instance.check_rate_limit(
            user_data["user_id"], "trade_capture", "trader", 
            user_data["organization_id"], "tier1"
        )
        assert is_allowed == True
        
        # Attempt 8: Revoke token
        auth_mgr.revoke_token(access_token)
        with pytest.raises(HTTPException):
            auth_mgr.verify_token(access_token)
        
        # Attempt 9: Create new token after revocation
        new_access_token = auth_mgr.create_access_token(user_data)
        assert new_access_token is not None
        
        # Attempt 10: Verify new token
        new_payload = auth_mgr.verify_token(new_access_token)
        assert new_payload["user_id"] == user_data["user_id"]
        
        print("✅ Integration test with 10 authentication attempts completed successfully")
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Run the integration test
    asyncio.run(test_integration_10_auth_attempts())
