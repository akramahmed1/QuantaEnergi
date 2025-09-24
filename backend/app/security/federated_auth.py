"""
Federated Authentication Integration
Supports Auth0, Okta, Azure AD, Google OAuth, and SAML providers
"""

from typing import Dict, List, Any, Optional, Union
from enum import Enum
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
import json
import base64
import hashlib
import secrets
from urllib.parse import urlencode, parse_qs

import structlog
from jose import jwt, JWTError
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError
from authlib.oauth2.rfc6749 import OAuth2Token
import requests

logger = structlog.get_logger(__name__)


class AuthProvider(str, Enum):
    """Supported authentication providers"""
    AUTH0 = "auth0"
    OKTA = "okta"
    AZURE_AD = "azure_ad"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    SAML = "saml"
    LDAP = "ldap"


@dataclass
class AuthProviderConfig:
    """Authentication provider configuration"""
    provider: AuthProvider
    client_id: str
    client_secret: str
    domain: str
    authorization_endpoint: Optional[str] = None
    token_endpoint: Optional[str] = None
    userinfo_endpoint: Optional[str] = None
    jwks_uri: Optional[str] = None
    scopes: List[str] = None
    additional_params: Dict[str, str] = None


@dataclass
class UserProfile:
    """User profile from federated authentication"""
    sub: str  # Subject identifier
    email: str
    name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None
    email_verified: bool = False
    phone_number: Optional[str] = None
    organization: Optional[str] = None
    roles: List[str] = None
    groups: List[str] = None
    custom_attributes: Dict[str, Any] = None


@dataclass
class AuthResult:
    """Authentication result"""
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    user_profile: Optional[UserProfile] = None
    expires_in: Optional[int] = None
    token_type: str = "Bearer"
    scope: Optional[str] = None
    error: Optional[str] = None
    error_description: Optional[str] = None


class FederatedAuthManager:
    """Manages federated authentication with multiple providers"""
    
    def __init__(self):
        """Initialize federated authentication manager"""
        self.providers: Dict[AuthProvider, AuthProviderConfig] = {}
        self.oauth_client = OAuth()
        self._setup_default_providers()
        logger.info("Federated authentication manager initialized")
    
    def _setup_default_providers(self):
        """Setup default authentication providers from environment"""
        import os
        
        # Auth0 Configuration
        if os.getenv("AUTH0_DOMAIN"):
            self.register_provider(AuthProviderConfig(
                provider=AuthProvider.AUTH0,
                client_id=os.getenv("AUTH0_CLIENT_ID"),
                client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
                domain=os.getenv("AUTH0_DOMAIN"),
                authorization_endpoint=f"https://{os.getenv('AUTH0_DOMAIN')}/authorize",
                token_endpoint=f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token",
                userinfo_endpoint=f"https://{os.getenv('AUTH0_DOMAIN')}/userinfo",
                jwks_uri=f"https://{os.getenv('AUTH0_DOMAIN')}/.well-known/jwks.json",
                scopes=["openid", "profile", "email"],
                additional_params={"audience": os.getenv("AUTH0_AUDIENCE")}
            ))
        
        # Okta Configuration
        if os.getenv("OKTA_DOMAIN"):
            self.register_provider(AuthProviderConfig(
                provider=AuthProvider.OKTA,
                client_id=os.getenv("OKTA_CLIENT_ID"),
                client_secret=os.getenv("OKTA_CLIENT_SECRET"),
                domain=os.getenv("OKTA_DOMAIN"),
                authorization_endpoint=f"https://{os.getenv('OKTA_DOMAIN')}/oauth2/v1/authorize",
                token_endpoint=f"https://{os.getenv('OKTA_DOMAIN')}/oauth2/v1/token",
                userinfo_endpoint=f"https://{os.getenv('OKTA_DOMAIN')}/oauth2/v1/userinfo",
                jwks_uri=f"https://{os.getenv('OKTA_DOMAIN')}/oauth2/v1/keys",
                scopes=["openid", "profile", "email"],
                additional_params={}
            ))
        
        # Azure AD Configuration
        if os.getenv("AZURE_TENANT_ID"):
            self.register_provider(AuthProviderConfig(
                provider=AuthProvider.AZURE_AD,
                client_id=os.getenv("AZURE_CLIENT_ID"),
                client_secret=os.getenv("AZURE_CLIENT_SECRET"),
                domain=os.getenv("AZURE_TENANT_ID"),
                authorization_endpoint=f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/authorize",
                token_endpoint=f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/token",
                userinfo_endpoint="https://graph.microsoft.com/v1.0/me",
                jwks_uri=f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/discovery/v2.0/keys",
                scopes=["openid", "profile", "email", "User.Read"],
                additional_params={}
            ))
        
        # Google OAuth Configuration
        if os.getenv("GOOGLE_CLIENT_ID"):
            self.register_provider(AuthProviderConfig(
                provider=AuthProvider.GOOGLE,
                client_id=os.getenv("GOOGLE_CLIENT_ID"),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
                domain="googleapis.com",
                authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
                token_endpoint="https://oauth2.googleapis.com/token",
                userinfo_endpoint="https://www.googleapis.com/oauth2/v2/userinfo",
                jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
                scopes=["openid", "profile", "email"],
                additional_params={}
            ))
    
    def register_provider(self, config: AuthProviderConfig):
        """
        Register an authentication provider
        
        Args:
            config: Provider configuration
        """
        self.providers[config.provider] = config
        
        # Register with OAuth client
        self.oauth_client.register(
            name=config.provider.value,
            client_id=config.client_id,
            client_secret=config.client_secret,
            server_metadata_url=self._get_metadata_url(config),
            client_kwargs={
                "scope": " ".join(config.scopes or ["openid", "profile", "email"])
            }
        )
        
        logger.info("Authentication provider registered", provider=config.provider.value)
    
    def _get_metadata_url(self, config: AuthProviderConfig) -> Optional[str]:
        """Get OIDC metadata URL for provider"""
        if config.provider == AuthProvider.AUTH0:
            return f"https://{config.domain}/.well-known/openid_configuration"
        elif config.provider == AuthProvider.OKTA:
            return f"https://{config.domain}/.well-known/openid_configuration"
        elif config.provider == AuthProvider.AZURE_AD:
            return f"https://login.microsoftonline.com/{config.domain}/v2.0/.well-known/openid_configuration"
        elif config.provider == AuthProvider.GOOGLE:
            return "https://accounts.google.com/.well-known/openid_configuration"
        return None
    
    def get_authorization_url(self, 
                            provider: AuthProvider, 
                            redirect_uri: str,
                            state: Optional[str] = None,
                            additional_params: Optional[Dict[str, str]] = None) -> str:
        """
        Get authorization URL for OAuth flow
        
        Args:
            provider: Authentication provider
            redirect_uri: Redirect URI after authorization
            state: Optional state parameter for CSRF protection
            additional_params: Additional parameters to include
            
        Returns:
            Authorization URL
        """
        if provider not in self.providers:
            raise ValueError(f"Provider {provider.value} not registered")
        
        config = self.providers[provider]
        
        # Generate state if not provided
        if not state:
            state = secrets.token_urlsafe(32)
        
        # Build authorization URL
        params = {
            "client_id": config.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(config.scopes or ["openid", "profile", "email"]),
            "state": state
        }
        
        # Add provider-specific parameters
        if config.additional_params:
            params.update(config.additional_params)
        
        # Add additional parameters
        if additional_params:
            params.update(additional_params)
        
        auth_url = f"{config.authorization_endpoint}?{urlencode(params)}"
        
        logger.info("Authorization URL generated", provider=provider.value)
        return auth_url
    
    async def exchange_code_for_token(self, 
                                    provider: AuthProvider,
                                    authorization_code: str,
                                    redirect_uri: str) -> AuthResult:
        """
        Exchange authorization code for access token
        
        Args:
            provider: Authentication provider
            authorization_code: Authorization code from callback
            redirect_uri: Redirect URI used in authorization
            
        Returns:
            Authentication result with tokens
        """
        try:
            if provider not in self.providers:
                return AuthResult(
                    success=False,
                    error="invalid_provider",
                    error_description=f"Provider {provider.value} not registered"
                )
            
            config = self.providers[provider]
            
            # Prepare token request
            token_data = {
                "grant_type": "authorization_code",
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "code": authorization_code,
                "redirect_uri": redirect_uri
            }
            
            # Make token request
            response = requests.post(
                config.token_endpoint,
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                return AuthResult(
                    success=False,
                    error=error_data.get("error", "token_exchange_failed"),
                    error_description=error_data.get("error_description", "Failed to exchange code for token")
                )
            
            token_response = response.json()
            
            # Extract user profile
            user_profile = await self._get_user_profile(
                provider, 
                token_response.get("access_token")
            )
            
            return AuthResult(
                success=True,
                access_token=token_response.get("access_token"),
                refresh_token=token_response.get("refresh_token"),
                id_token=token_response.get("id_token"),
                user_profile=user_profile,
                expires_in=token_response.get("expires_in"),
                token_type=token_response.get("token_type", "Bearer"),
                scope=token_response.get("scope")
            )
            
        except Exception as e:
            logger.error("Token exchange failed", provider=provider.value, error=str(e))
            return AuthResult(
                success=False,
                error="token_exchange_error",
                error_description=str(e)
            )
    
    async def _get_user_profile(self, provider: AuthProvider, access_token: str) -> Optional[UserProfile]:
        """
        Get user profile from provider
        
        Args:
            provider: Authentication provider
            access_token: Access token for API calls
            
        Returns:
            User profile or None
        """
        try:
            config = self.providers[provider]
            
            # Make userinfo request
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(config.userinfo_endpoint, headers=headers)
            
            if response.status_code != 200:
                logger.error("Failed to get user profile", 
                           provider=provider.value, 
                           status_code=response.status_code)
                return None
            
            user_data = response.json()
            
            # Map provider-specific fields to standard profile
            return self._map_user_profile(user_data, provider)
            
        except Exception as e:
            logger.error("Failed to get user profile", provider=provider.value, error=str(e))
            return None
    
    def _map_user_profile(self, user_data: Dict[str, Any], provider: AuthProvider) -> UserProfile:
        """
        Map provider-specific user data to standard profile
        
        Args:
            user_data: Raw user data from provider
            provider: Authentication provider
            
        Returns:
            Mapped user profile
        """
        # Common field mappings
        profile_data = {
            "sub": user_data.get("sub", user_data.get("id", "")),
            "email": user_data.get("email", ""),
            "name": user_data.get("name", ""),
            "given_name": user_data.get("given_name", user_data.get("first_name")),
            "family_name": user_data.get("family_name", user_data.get("last_name")),
            "picture": user_data.get("picture", user_data.get("avatar_url")),
            "locale": user_data.get("locale", user_data.get("language")),
            "email_verified": user_data.get("email_verified", False),
            "phone_number": user_data.get("phone_number"),
            "custom_attributes": {}
        }
        
        # Provider-specific mappings
        if provider == AuthProvider.AZURE_AD:
            profile_data["organization"] = user_data.get("organization", "")
            profile_data["roles"] = user_data.get("roles", [])
            profile_data["groups"] = user_data.get("groups", [])
        
        elif provider == AuthProvider.OKTA:
            profile_data["organization"] = user_data.get("organization", "")
            profile_data["roles"] = user_data.get("roles", [])
            profile_data["groups"] = user_data.get("groups", [])
        
        elif provider == AuthProvider.AUTH0:
            # Auth0 custom attributes are in user_metadata or app_metadata
            profile_data["custom_attributes"] = {
                "user_metadata": user_data.get("user_metadata", {}),
                "app_metadata": user_data.get("app_metadata", {})
            }
        
        # Extract custom attributes
        for key, value in user_data.items():
            if key not in ["sub", "email", "name", "given_name", "family_name", 
                          "picture", "locale", "email_verified", "phone_number",
                          "organization", "roles", "groups", "user_metadata", "app_metadata"]:
                profile_data["custom_attributes"][key] = value
        
        return UserProfile(**profile_data)
    
    async def refresh_access_token(self, 
                                 provider: AuthProvider,
                                 refresh_token: str) -> AuthResult:
        """
        Refresh access token using refresh token
        
        Args:
            provider: Authentication provider
            refresh_token: Refresh token
            
        Returns:
            New authentication result
        """
        try:
            if provider not in self.providers:
                return AuthResult(
                    success=False,
                    error="invalid_provider",
                    error_description=f"Provider {provider.value} not registered"
                )
            
            config = self.providers[provider]
            
            # Prepare refresh request
            refresh_data = {
                "grant_type": "refresh_token",
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "refresh_token": refresh_token
            }
            
            # Make refresh request
            response = requests.post(
                config.token_endpoint,
                data=refresh_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                return AuthResult(
                    success=False,
                    error=error_data.get("error", "token_refresh_failed"),
                    error_description=error_data.get("error_description", "Failed to refresh token")
                )
            
            token_response = response.json()
            
            # Get updated user profile
            user_profile = await self._get_user_profile(
                provider,
                token_response.get("access_token")
            )
            
            return AuthResult(
                success=True,
                access_token=token_response.get("access_token"),
                refresh_token=token_response.get("refresh_token"),
                id_token=token_response.get("id_token"),
                user_profile=user_profile,
                expires_in=token_response.get("expires_in"),
                token_type=token_response.get("token_type", "Bearer"),
                scope=token_response.get("scope")
            )
            
        except Exception as e:
            logger.error("Token refresh failed", provider=provider.value, error=str(e))
            return AuthResult(
                success=False,
                error="token_refresh_error",
                error_description=str(e)
            )
    
    async def validate_token(self, 
                           provider: AuthProvider,
                           access_token: str) -> bool:
        """
        Validate access token with provider
        
        Args:
            provider: Authentication provider
            access_token: Access token to validate
            
        Returns:
            Token validity status
        """
        try:
            if provider not in self.providers:
                return False
            
            config = self.providers[provider]
            
            # For OAuth providers, validate by calling userinfo endpoint
            if config.userinfo_endpoint:
                headers = {"Authorization": f"Bearer {access_token}"}
                response = requests.get(config.userinfo_endpoint, headers=headers)
                return response.status_code == 200
            
            # For JWT tokens, validate signature
            if config.jwks_uri:
                try:
                    # Decode JWT header to get key ID
                    header = jwt.get_unverified_header(access_token)
                    key_id = header.get("kid")
                    
                    if key_id:
                        # Get JWKS and validate token
                        jwks_response = requests.get(config.jwks_uri)
                        jwks = jwks_response.json()
                        
                        # Find the key
                        key = None
                        for jwk in jwks.get("keys", []):
                            if jwk.get("kid") == key_id:
                                key = jwk
                                break
                        
                        if key:
                            # Validate token (this is simplified - you'd use a proper JWT library)
                            jwt.decode(access_token, key, algorithms=["RS256"])
                            return True
                
                except JWTError:
                    return False
            
            return False
            
        except Exception as e:
            logger.error("Token validation failed", provider=provider.value, error=str(e))
            return False
    
    def get_supported_providers(self) -> List[AuthProvider]:
        """
        Get list of supported authentication providers
        
        Returns:
            List of supported providers
        """
        return list(self.providers.keys())
    
    def get_provider_config(self, provider: AuthProvider) -> Optional[AuthProviderConfig]:
        """
        Get configuration for specific provider
        
        Args:
            provider: Authentication provider
            
        Returns:
            Provider configuration or None
        """
        return self.providers.get(provider)


# Global federated auth manager instance
_federated_auth_manager: Optional[FederatedAuthManager] = None


def get_federated_auth_manager() -> FederatedAuthManager:
    """Get the global federated authentication manager instance"""
    global _federated_auth_manager
    
    if _federated_auth_manager is None:
        _federated_auth_manager = FederatedAuthManager()
    
    return _federated_auth_manager


# FastAPI integration helpers
async def create_federated_auth_routes(app, auth_manager: FederatedAuthManager):
    """
    Create FastAPI routes for federated authentication
    
    Args:
        app: FastAPI application instance
        auth_manager: Federated authentication manager
    """
    from fastapi import APIRouter, Request, Response, HTTPException, Depends
    from fastapi.responses import RedirectResponse
    
    router = APIRouter(prefix="/auth/federated", tags=["Federated Authentication"])
    
    @router.get("/providers")
    async def get_supported_providers():
        """Get list of supported authentication providers"""
        return {
            "providers": [provider.value for provider in auth_manager.get_supported_providers()]
        }
    
    @router.get("/login/{provider}")
    async def initiate_login(provider: str, request: Request):
        """Initiate OAuth login with specified provider"""
        try:
            auth_provider = AuthProvider(provider)
            redirect_uri = str(request.url_for("auth_callback", provider=provider))
            
            auth_url = auth_manager.get_authorization_url(
                auth_provider,
                redirect_uri
            )
            
            return RedirectResponse(url=auth_url)
            
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        except Exception as e:
            logger.error("Login initiation failed", provider=provider, error=str(e))
            raise HTTPException(status_code=500, detail="Login initiation failed")
    
    @router.get("/callback/{provider}")
    async def auth_callback(provider: str, request: Request):
        """Handle OAuth callback"""
        try:
            auth_provider = AuthProvider(provider)
            query_params = request.query_params
            
            # Check for error in callback
            if "error" in query_params:
                error = query_params.get("error")
                error_description = query_params.get("error_description", "")
                raise HTTPException(
                    status_code=400, 
                    detail=f"OAuth error: {error} - {error_description}"
                )
            
            # Get authorization code
            code = query_params.get("code")
            if not code:
                raise HTTPException(status_code=400, detail="Authorization code not found")
            
            # Verify state parameter (CSRF protection)
            state = query_params.get("state")
            # In production, you'd verify this against stored state
            
            # Exchange code for tokens
            redirect_uri = str(request.url_for("auth_callback", provider=provider))
            auth_result = await auth_manager.exchange_code_for_token(
                auth_provider,
                code,
                redirect_uri
            )
            
            if not auth_result.success:
                raise HTTPException(
                    status_code=400,
                    detail=f"Authentication failed: {auth_result.error_description}"
                )
            
            # In production, you'd:
            # 1. Create or update user in your database
            # 2. Generate your own JWT token
            # 3. Set secure cookies or return tokens
            
            return {
                "success": True,
                "user_profile": auth_result.user_profile.__dict__ if auth_result.user_profile else None,
                "access_token": auth_result.access_token,
                "expires_in": auth_result.expires_in
            }
            
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        except Exception as e:
            logger.error("Auth callback failed", provider=provider, error=str(e))
            raise HTTPException(status_code=500, detail="Authentication callback failed")
    
    @router.post("/refresh/{provider}")
    async def refresh_token(provider: str, refresh_token: str):
        """Refresh access token"""
        try:
            auth_provider = AuthProvider(provider)
            auth_result = await auth_manager.refresh_access_token(
                auth_provider,
                refresh_token
            )
            
            if not auth_result.success:
                raise HTTPException(
                    status_code=400,
                    detail=f"Token refresh failed: {auth_result.error_description}"
                )
            
            return {
                "success": True,
                "access_token": auth_result.access_token,
                "expires_in": auth_result.expires_in
            }
            
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        except Exception as e:
            logger.error("Token refresh failed", provider=provider, error=str(e))
            raise HTTPException(status_code=500, detail="Token refresh failed")
    
    @router.post("/validate/{provider}")
    async def validate_token(provider: str, access_token: str):
        """Validate access token"""
        try:
            auth_provider = AuthProvider(provider)
            is_valid = await auth_manager.validate_token(auth_provider, access_token)
            
            return {"valid": is_valid}
            
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        except Exception as e:
            logger.error("Token validation failed", provider=provider, error=str(e))
            raise HTTPException(status_code=500, detail="Token validation failed")
    
    # Include router in app
    app.include_router(router)
