"""
Vault Secrets Management Service
Provides secure secrets management with HashiCorp Vault integration
"""

import os
import json
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import structlog
import asyncio
import aiohttp
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = structlog.get_logger(__name__)

class VaultSecretsManager:
    """
    Vault-based secrets management service for QuantaEnergi
    """
    
    def __init__(self, vault_url: str = None, vault_token: str = None):
        self.vault_url = vault_url or os.getenv("VAULT_URL", "http://vault:8200")
        self.vault_token = vault_token or os.getenv("VAULT_TOKEN")
        self.session = None
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Vault paths for different secret types
        self.secret_paths = {
            "database": "secret/data/quantaenergi/database",
            "api_keys": "secret/data/quantaenergi/api-keys",
            "jwt": "secret/data/quantaenergi/jwt",
            "blockchain": "secret/data/quantaenergi/blockchain",
            "quantum": "secret/data/quantaenergi/quantum",
            "ai_ml": "secret/data/quantaenergi/ai-ml",
            "compliance": "secret/data/quantaenergi/compliance",
            "monitoring": "secret/data/quantaenergi/monitoring"
        }
        
        logger.info("VaultSecretsManager initialized", vault_url=self.vault_url)
    
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for local secrets"""
        key_env = os.getenv("QUANTAENERGI_ENCRYPTION_KEY")
        if key_env:
            return base64.b64decode(key_env)
        
        # Generate new key if not exists
        password = os.getenv("QUANTAENERGI_MASTER_PASSWORD", "default-password").encode()
        salt = os.getenv("QUANTAENERGI_SALT", "default-salt").encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        
        logger.warning("Generated new encryption key. Set QUANTAENERGI_ENCRYPTION_KEY environment variable for production")
        return key
    
    async def get_secret(self, secret_type: str, key: str = None) -> Any:
        """
        Get secret from Vault
        
        Args:
            secret_type: Type of secret (database, api_keys, jwt, etc.)
            key: Specific key within the secret (optional)
            
        Returns:
            Secret value or dictionary of secrets
        """
        try:
            if not self.vault_token:
                logger.warning("No Vault token available, using local secrets")
                return await self._get_local_secret(secret_type, key)
            
            session = await self.get_session()
            path = self.secret_paths.get(secret_type)
            
            if not path:
                raise ValueError(f"Unknown secret type: {secret_type}")
            
            headers = {
                "X-Vault-Token": self.vault_token,
                "Content-Type": "application/json"
            }
            
            async with session.get(f"{self.vault_url}/v1/{path}", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    secrets = data.get("data", {}).get("data", {})
                    
                    if key:
                        return secrets.get(key)
                    return secrets
                elif response.status == 404:
                    logger.warning(f"Secret not found in Vault: {secret_type}")
                    return await self._get_local_secret(secret_type, key)
                else:
                    logger.error(f"Vault request failed: {response.status}")
                    return await self._get_local_secret(secret_type, key)
                    
        except Exception as e:
            logger.error(f"Failed to get secret from Vault: {e}")
            return await self._get_local_secret(secret_type, key)
    
    async def set_secret(self, secret_type: str, secrets: Dict[str, Any]) -> bool:
        """
        Set secret in Vault
        
        Args:
            secret_type: Type of secret
            secrets: Dictionary of secrets to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.vault_token:
                logger.warning("No Vault token available, storing locally")
                return await self._set_local_secret(secret_type, secrets)
            
            session = await self.get_session()
            path = self.secret_paths.get(secret_type)
            
            if not path:
                raise ValueError(f"Unknown secret type: {secret_type}")
            
            headers = {
                "X-Vault-Token": self.vault_token,
                "Content-Type": "application/json"
            }
            
            payload = {"data": secrets}
            
            async with session.post(f"{self.vault_url}/v1/{path}", 
                                  headers=headers, 
                                  json=payload) as response:
                if response.status == 200:
                    logger.info(f"Secret stored successfully in Vault: {secret_type}")
                    return True
                else:
                    logger.error(f"Failed to store secret in Vault: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to set secret in Vault: {e}")
            return await self._set_local_secret(secret_type, secrets)
    
    async def rotate_secret(self, secret_type: str, key: str) -> bool:
        """
        Rotate a specific secret
        
        Args:
            secret_type: Type of secret
            key: Key to rotate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Rotating secret: {secret_type}/{key}")
            
            # Get current secret
            current_secret = await self.get_secret(secret_type, key)
            if not current_secret:
                logger.error(f"Secret not found: {secret_type}/{key}")
                return False
            
            # Generate new secret based on type
            new_secret = await self._generate_new_secret(secret_type, key)
            
            # Store new secret
            secrets = await self.get_secret(secret_type) or {}
            secrets[key] = new_secret
            
            success = await self.set_secret(secret_type, secrets)
            
            if success:
                logger.info(f"Secret rotated successfully: {secret_type}/{key}")
                # TODO: Notify services to refresh secrets
                await self._notify_secret_rotation(secret_type, key)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to rotate secret: {e}")
            return False
    
    async def _generate_new_secret(self, secret_type: str, key: str) -> str:
        """Generate new secret based on type and key"""
        import secrets
        import string
        
        if "password" in key.lower():
            # Generate strong password
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
            return ''.join(secrets.choice(chars) for _ in range(32))
        
        elif "token" in key.lower() or "jwt" in key.lower():
            # Generate JWT-like token
            chars = string.ascii_letters + string.digits
            return ''.join(secrets.choice(chars) for _ in range(64))
        
        elif "key" in key.lower() or "secret" in key.lower():
            # Generate API key
            chars = string.ascii_letters + string.digits
            return ''.join(secrets.choice(chars) for _ in range(32))
        
        else:
            # Default: random string
            return secrets.token_urlsafe(32)
    
    async def _notify_secret_rotation(self, secret_type: str, key: str):
        """Notify services about secret rotation"""
        # TODO: Implement service notification mechanism
        logger.info(f"Notifying services about secret rotation: {secret_type}/{key}")
    
    async def _get_local_secret(self, secret_type: str, key: str = None) -> Any:
        """Get secret from local encrypted storage"""
        try:
            # Check environment variables first
            env_key = f"QUANTAENERGI_{secret_type.upper()}_{key.upper()}" if key else None
            if env_key and os.getenv(env_key):
                return os.getenv(env_key)
            
            # Check encrypted local file
            local_file = f"/tmp/quantaenergi_{secret_type}.enc"
            if os.path.exists(local_file):
                with open(local_file, 'rb') as f:
                    encrypted_data = f.read()
                
                decrypted_data = self.cipher.decrypt(encrypted_data)
                secrets = json.loads(decrypted_data.decode())
                
                if key:
                    return secrets.get(key)
                return secrets
            
            # Return default secrets for development
            return await self._get_default_secret(secret_type, key)
            
        except Exception as e:
            logger.error(f"Failed to get local secret: {e}")
            return await self._get_default_secret(secret_type, key)
    
    async def _set_local_secret(self, secret_type: str, secrets: Dict[str, Any]) -> bool:
        """Set secret in local encrypted storage"""
        try:
            local_file = f"/tmp/quantaenergi_{secret_type}.enc"
            encrypted_data = self.cipher.encrypt(json.dumps(secrets).encode())
            
            with open(local_file, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info(f"Secret stored locally: {secret_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set local secret: {e}")
            return False
    
    async def _get_default_secret(self, secret_type: str, key: str = None) -> Any:
        """Get default secrets for development"""
        default_secrets = {
            "database": {
                "url": "postgresql://quantaenergi:password@localhost:5432/quantaenergi",
                "password": "password",
                "username": "quantaenergi"
            },
            "api_keys": {
                "openweathermap": "demo-api-key",
                "ice": "demo-ice-key",
                "cme": "demo-cme-key",
                "eex": "demo-eex-key"
            },
            "jwt": {
                "secret": "quantaenergi-jwt-secret-key",
                "algorithm": "HS256",
                "expiration": "24h"
            },
            "blockchain": {
                "ethereum_url": "https://sepolia.infura.io/v3/demo",
                "private_key": "demo-private-key",
                "contract_address": "0x1234567890123456789012345678901234567890"
            },
            "quantum": {
                "qiskit_token": "demo-qiskit-token",
                "backend": "qasm_simulator"
            },
            "ai_ml": {
                "huggingface_token": "demo-hf-token",
                "openai_key": "demo-openai-key"
            },
            "compliance": {
                "ferc_api_key": "demo-ferc-key",
                "remit_api_key": "demo-remit-key"
            },
            "monitoring": {
                "prometheus_url": "http://prometheus:9090",
                "grafana_url": "http://grafana:3000",
                "jaeger_url": "http://jaeger:14268"
            }
        }
        
        secrets = default_secrets.get(secret_type, {})
        if key:
            return secrets.get(key)
        return secrets
    
    async def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return await self.get_secret("database")
    
    async def get_api_key(self, service: str) -> str:
        """Get API key for external service"""
        api_keys = await self.get_secret("api_keys")
        return api_keys.get(service, "")
    
    async def get_jwt_config(self) -> Dict[str, Any]:
        """Get JWT configuration"""
        return await self.get_secret("jwt")
    
    async def get_blockchain_config(self) -> Dict[str, Any]:
        """Get blockchain configuration"""
        return await self.get_secret("blockchain")
    
    async def get_quantum_config(self) -> Dict[str, Any]:
        """Get quantum computing configuration"""
        return await self.get_secret("quantum")
    
    async def get_ai_ml_config(self) -> Dict[str, Any]:
        """Get AI/ML configuration"""
        return await self.get_secret("ai_ml")
    
    async def get_compliance_config(self) -> Dict[str, Any]:
        """Get compliance configuration"""
        return await self.get_secret("compliance")
    
    async def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return await self.get_secret("monitoring")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Vault health"""
        try:
            session = await self.get_session()
            async with session.get(f"{self.vault_url}/v1/sys/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "healthy",
                        "vault_available": True,
                        "vault_data": data
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "vault_available": False,
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            return {
                "status": "unhealthy",
                "vault_available": False,
                "error": str(e)
            }
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()

# Global instance
secrets_manager = VaultSecretsManager()
