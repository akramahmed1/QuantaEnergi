#!/usr/bin/env python3
"""
Test JWT Refresh functionality for QuantaEnergi
"""

import pytest
import jwt
from datetime import datetime, timedelta
import sys
import os

# Add shared services to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared', 'services'))

try:
    from app.core.security import create_access_token, create_refresh_token, verify_token, refresh_access_token
except ImportError:
    # Fallback if security module not available
    pytest.skip("Security module not available", allow_module_level=True)


class TestJWTTokenCreation:
    """Test JWT token creation functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_user_id = 123
        self.test_email = "test@quantaenergi.com"
        self.test_role = "trader"
        self.secret_key = "test-secret-key-for-jwt"
        self.algorithm = "HS256"
    
    def test_create_access_token(self):
        """Test access token creation"""
        # Test basic access token creation
        access_token = create_access_token(
            data={"sub": self.test_user_id, "email": self.test_email, "role": self.test_role},
            expires_delta=timedelta(minutes=30)
        )
        
        assert access_token is not None
        assert isinstance(access_token, str)
        assert len(access_token) > 0
        
        # Test token decoding
        decoded_token = jwt.decode(access_token, self.secret_key, algorithms=[self.algorithm])
        
        assert decoded_token["sub"] == self.test_user_id
        assert decoded_token["email"] == self.test_email
        assert decoded_token["role"] == self.test_role
        assert "exp" in decoded_token
        assert "iat" in decoded_token
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        # Test refresh token creation
        refresh_token = create_refresh_token(
            data={"sub": self.test_user_id, "email": self.test_email}
        )
        
        assert refresh_token is not None
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 0
        
        # Test token decoding
        decoded_token = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
        
        assert decoded_token["sub"] == self.test_user_id
        assert decoded_token["email"] == self.test_email
        assert "exp" in decoded_token
        assert "iat" in decoded_token
        
        # Refresh tokens should have longer expiration
        current_time = datetime.utcnow()
        exp_time = datetime.fromtimestamp(decoded_token["exp"])
        assert exp_time > current_time + timedelta(days=6)  # Should be valid for at least 6 days
    
    def test_token_expiration(self):
        """Test token expiration handling"""
        # Test access token with short expiration
        short_expiry_token = create_access_token(
            data={"sub": self.test_user_id},
            expires_delta=timedelta(seconds=1)  # 1 second expiration
        )
        
        # Token should be valid initially
        decoded_token = jwt.decode(short_expiry_token, self.secret_key, algorithms=[self.algorithm])
        assert decoded_token["sub"] == self.test_user_id
        
        # Wait for expiration
        import time
        time.sleep(2)
        
        # Token should now be expired
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(short_expiry_token, self.secret_key, algorithms=[self.algorithm])
    
    def test_token_payload_structure(self):
        """Test token payload structure and validation"""
        # Test token with minimal payload
        minimal_token = create_access_token(
            data={"sub": self.test_user_id}
        )
        
        decoded_token = jwt.decode(minimal_token, self.secret_key, algorithms=[self.algorithm])
        
        # Required fields
        assert "sub" in decoded_token
        assert "exp" in decoded_token
        assert "iat" in decoded_token
        
        # Optional fields should not be present
        assert "email" not in decoded_token
        assert "role" not in decoded_token
        
        # Test token with extended payload
        extended_token = create_access_token(
            data={
                "sub": self.test_user_id,
                "email": self.test_email,
                "role": self.test_role,
                "permissions": ["read", "write"],
                "org_id": 456
            }
        )
        
        decoded_extended = jwt.decode(extended_token, self.secret_key, algorithms=[self.algorithm])
        
        # All fields should be present
        assert decoded_extended["sub"] == self.test_user_id
        assert decoded_extended["email"] == self.test_email
        assert decoded_extended["role"] == self.test_role
        assert decoded_extended["permissions"] == ["read", "write"]
        assert decoded_extended["org_id"] == 456


class TestJWTTokenVerification:
    """Test JWT token verification functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_user_id = 123
        self.secret_key = "test-secret-key-for-jwt"
        self.algorithm = "HS256"
        
        # Create a valid token for testing
        self.valid_token = create_access_token(
            data={"sub": self.test_user_id},
            expires_delta=timedelta(minutes=30)
        )
    
    def test_verify_valid_token(self):
        """Test verification of valid token"""
        # Test valid token verification
        payload = verify_token(self.valid_token)
        
        assert payload is not None
        assert payload["sub"] == self.test_user_id
        assert "exp" in payload
        assert "iat" in payload
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token"""
        # Test invalid token format
        invalid_token = "invalid.token.format"
        
        with pytest.raises(Exception):
            verify_token(invalid_token)
    
    def test_verify_expired_token(self):
        """Test verification of expired token"""
        # Create expired token
        expired_token = create_access_token(
            data={"sub": self.test_user_id},
            expires_delta=timedelta(seconds=1)
        )
        
        # Wait for expiration
        import time
        time.sleep(2)
        
        # Token should be expired
        with pytest.raises(Exception):
            verify_token(expired_token)
    
    def test_verify_token_with_wrong_secret(self):
        """Test verification with wrong secret key"""
        # Create token with one secret
        token = create_access_token(
            data={"sub": self.test_user_id},
            expires_delta=timedelta(minutes=30)
        )
        
        # Try to verify with wrong secret
        wrong_secret = "wrong-secret-key"
        
        with pytest.raises(Exception):
            verify_token(token, secret_key=wrong_secret)
    
    def test_verify_token_missing_subject(self):
        """Test verification of token without subject"""
        # Create token without subject
        token_without_sub = create_access_token(
            data={"email": "test@example.com"},
            expires_delta=timedelta(minutes=30)
        )
        
        # Token should still be valid but without subject
        payload = verify_token(token_without_sub)
        assert payload is not None
        assert "sub" not in payload
        assert payload["email"] == "test@example.com"


class TestJWTRefreshFunctionality:
    """Test JWT refresh functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_user_id = 123
        self.test_email = "test@quantaenergi.com"
        self.secret_key = "test-secret-key-for-jwt"
        self.algorithm = "HS256"
    
    def test_refresh_access_token(self):
        """Test refreshing access token with valid refresh token"""
        # Create refresh token
        refresh_token = create_refresh_token(
            data={"sub": self.test_user_id, "email": self.test_email}
        )
        
        # Refresh access token
        new_access_token = refresh_access_token(refresh_token)
        
        assert new_access_token is not None
        assert isinstance(new_access_token, str)
        assert len(new_access_token) > 0
        
        # Verify new access token
        decoded_token = jwt.decode(new_access_token, self.secret_key, algorithms=[self.algorithm])
        
        assert decoded_token["sub"] == self.test_user_id
        assert decoded_token["email"] == self.test_user_email
        assert "exp" in decoded_token
        assert "iat" in decoded_token
        
        # New token should have fresh expiration
        current_time = datetime.utcnow()
        exp_time = datetime.fromtimestamp(decoded_token["exp"])
        assert exp_time > current_time + timedelta(minutes=25)  # Should be valid for at least 25 minutes
    
    def test_refresh_with_invalid_refresh_token(self):
        """Test refresh with invalid refresh token"""
        # Test with invalid token format
        invalid_refresh_token = "invalid.refresh.token"
        
        with pytest.raises(Exception):
            refresh_access_token(invalid_refresh_token)
    
    def test_refresh_with_expired_refresh_token(self):
        """Test refresh with expired refresh token"""
        # Create expired refresh token
        expired_refresh_token = create_refresh_token(
            data={"sub": self.test_user_id},
            expires_delta=timedelta(seconds=1)
        )
        
        # Wait for expiration
        import time
        time.sleep(2)
        
        # Should not be able to refresh with expired token
        with pytest.raises(Exception):
            refresh_access_token(expired_refresh_token)
    
    def test_refresh_token_reuse_prevention(self):
        """Test that refresh tokens cannot be reused"""
        # Create refresh token
        refresh_token = create_refresh_token(
            data={"sub": self.test_user_id}
        )
        
        # Use refresh token first time
        first_access_token = refresh_access_token(refresh_token)
        assert first_access_token is not None
        
        # Try to use same refresh token again
        with pytest.raises(Exception):
            second_access_token = refresh_access_token(refresh_token)
    
    def test_refresh_token_rotation(self):
        """Test refresh token rotation for security"""
        # Create initial refresh token
        initial_refresh_token = create_refresh_token(
            data={"sub": self.test_user_id}
        )
        
        # Refresh access token (should also rotate refresh token)
        new_access_token, new_refresh_token = refresh_access_token(
            initial_refresh_token,
            rotate_refresh_token=True
        )
        
        assert new_access_token is not None
        assert new_refresh_token is not None
        
        # Old refresh token should be invalid
        with pytest.raises(Exception):
            refresh_access_token(initial_refresh_token)
        
        # New refresh token should work
        second_access_token = refresh_access_token(new_refresh_token)
        assert second_access_token is not None


class TestJWTSecurityFeatures:
    """Test JWT security features"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_user_id = 123
        self.secret_key = "test-secret-key-for-jwt"
        self.algorithm = "HS256"
    
    def test_token_signature_verification(self):
        """Test token signature verification"""
        # Create valid token
        valid_token = create_access_token(
            data={"sub": self.test_user_id}
        )
        
        # Verify signature
        payload = verify_token(valid_token)
        assert payload is not None
        
        # Tamper with token (change payload)
        tampered_token = valid_token[:-10] + "tampered"
        
        with pytest.raises(Exception):
            verify_token(tampered_token)
    
    def test_token_algorithm_validation(self):
        """Test token algorithm validation"""
        # Create token with specific algorithm
        token = create_access_token(
            data={"sub": self.test_user_id}
        )
        
        # Verify with correct algorithm
        payload = verify_token(token)
        assert payload is not None
        
        # Try to verify with wrong algorithm
        with pytest.raises(Exception):
            jwt.decode(token, self.secret_key, algorithms=["RS256"])
    
    def test_token_audience_validation(self):
        """Test token audience validation"""
        # Create token with audience
        token_with_audience = create_access_token(
            data={"sub": self.test_user_id, "aud": "quantaenergi-users"}
        )
        
        # Verify with correct audience
        payload = verify_token(token_with_audience, audience="quantaenergi-users")
        assert payload is not None
        
        # Try to verify with wrong audience
        with pytest.raises(Exception):
            verify_token(token_with_audience, audience="wrong-audience")
    
    def test_token_issuer_validation(self):
        """Test token issuer validation"""
        # Create token with issuer
        token_with_issuer = create_access_token(
            data={"sub": self.test_user_id, "iss": "quantaenergi"}
        )
        
        # Verify with correct issuer
        payload = verify_token(token_with_issuer, issuer="quantaenergi")
        assert payload is not None
        
        # Try to verify with wrong issuer
        with pytest.raises(Exception):
            verify_token(token_with_issuer, issuer="wrong-issuer")


class TestJWTIntegration:
    """Test JWT integration with application"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_user_id = 123
        self.test_email = "test@quantaenergi.com"
        self.test_role = "trader"
    
    def test_jwt_in_authentication_flow(self):
        """Test JWT in complete authentication flow"""
        # 1. User login - create access and refresh tokens
        access_token = create_access_token(
            data={"sub": self.test_user_id, "email": self.test_email, "role": self.test_role}
        )
        refresh_token = create_refresh_token(
            data={"sub": self.test_user_id, "email": self.test_email}
        )
        
        assert access_token is not None
        assert refresh_token is not None
        
        # 2. Use access token for API calls
        payload = verify_token(access_token)
        assert payload["sub"] == self.test_user_id
        assert payload["email"] == self.test_email
        assert payload["role"] == self.test_role
        
        # 3. When access token expires, use refresh token
        new_access_token = refresh_access_token(refresh_token)
        assert new_access_token is not None
        
        # 4. Verify new access token
        new_payload = verify_token(new_access_token)
        assert new_payload["sub"] == self.test_user_id
        assert new_payload["email"] == self.test_email
        assert new_payload["role"] == self.test_role
    
    def test_jwt_role_based_access(self):
        """Test JWT role-based access control"""
        # Create tokens with different roles
        admin_token = create_access_token(
            data={"sub": 456, "email": "admin@quantaenergi.com", "role": "admin"}
        )
        trader_token = create_access_token(
            data={"sub": 789, "email": "trader@quantaenergi.com", "role": "trader"}
        )
        viewer_token = create_access_token(
            data={"sub": 101, "email": "viewer@quantaenergi.com", "role": "viewer"}
        )
        
        # Verify tokens
        admin_payload = verify_token(admin_token)
        trader_payload = verify_token(trader_token)
        viewer_payload = verify_token(viewer_token)
        
        assert admin_payload["role"] == "admin"
        assert trader_payload["role"] == "trader"
        assert viewer_payload["role"] == "viewer"
        
        # Test role-based access logic
        def check_admin_access(token):
            payload = verify_token(token)
            return payload["role"] == "admin"
        
        def check_trader_access(token):
            payload = verify_token(token)
            return payload["role"] in ["admin", "trader"]
        
        assert check_admin_access(admin_token) is True
        assert check_admin_access(trader_token) is False
        assert check_admin_access(viewer_token) is False
        
        assert check_trader_access(admin_token) is True
        assert check_trader_access(trader_token) is True
        assert check_trader_access(viewer_token) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
