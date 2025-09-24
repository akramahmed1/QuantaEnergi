"""
Secrets Management Integration
Supports multiple secret management providers: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, Google Secret Manager
"""

import json
import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, Union
from datetime import datetime, timezone

import structlog

logger = structlog.get_logger(__name__)


class SecretProvider(str, Enum):
    """Supported secret management providers"""
    VAULT = "vault"
    AWS_SECRETS_MANAGER = "aws_secrets_manager"
    AZURE_KEY_VAULT = "azure_key_vault"
    GOOGLE_SECRET_MANAGER = "google_secret_manager"
    ENVIRONMENT = "environment"  # Fallback to environment variables


class SecretManager(ABC):
    """Abstract base class for secret managers"""
    
    @abstractmethod
    async def get_secret(self, secret_name: str, key: Optional[str] = None) -> str:
        """
        Get a secret value
        
        Args:
            secret_name: Name of the secret
            key: Optional key within the secret (for JSON secrets)
            
        Returns:
            Secret value as string
        """
        pass
    
    @abstractmethod
    async def set_secret(self, secret_name: str, secret_value: Union[str, Dict[str, Any]], key: Optional[str] = None) -> bool:
        """
        Set a secret value
        
        Args:
            secret_name: Name of the secret
            secret_value: Value to store
            key: Optional key within the secret (for JSON secrets)
            
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    async def delete_secret(self, secret_name: str) -> bool:
        """
        Delete a secret
        
        Args:
            secret_name: Name of the secret to delete
            
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    async def list_secrets(self) -> list[str]:
        """
        List all available secrets
        
        Returns:
            List of secret names
        """
        pass


class HashiCorpVaultManager(SecretManager):
    """HashiCorp Vault secrets manager"""
    
    def __init__(self, vault_url: str, vault_token: str, mount_point: str = "secret"):
        """
        Initialize Vault manager
        
        Args:
            vault_url: Vault server URL
            vault_token: Vault authentication token
            mount_point: Vault secrets mount point
        """
        try:
            import hvac
            self.client = hvac.Client(url=vault_url, token=vault_token)
            self.mount_point = mount_point
            
            # Verify connection
            if not self.client.is_authenticated():
                raise ValueError("Failed to authenticate with Vault")
                
            logger.info("Connected to HashiCorp Vault", url=vault_url)
            
        except ImportError:
            raise ImportError("hvac package is required for Vault integration")
        except Exception as e:
            logger.error("Failed to connect to Vault", error=str(e))
            raise
    
    async def get_secret(self, secret_name: str, key: Optional[str] = None) -> str:
        """Get secret from Vault"""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=secret_name,
                mount_point=self.mount_point
            )
            
            secret_data = response["data"]["data"]
            
            if key:
                if key not in secret_data:
                    raise KeyError(f"Key '{key}' not found in secret '{secret_name}'")
                return str(secret_data[key])
            
            # Return as JSON string if no key specified
            return json.dumps(secret_data)
            
        except Exception as e:
            logger.error("Failed to get secret from Vault", 
                        secret_name=secret_name, 
                        key=key, 
                        error=str(e))
            raise
    
    async def set_secret(self, secret_name: str, secret_value: Union[str, Dict[str, Any]], key: Optional[str] = None) -> bool:
        """Set secret in Vault"""
        try:
            if key:
                # Get existing secret data
                try:
                    response = self.client.secrets.kv.v2.read_secret_version(
                        path=secret_name,
                        mount_point=self.mount_point
                    )
                    secret_data = response["data"]["data"]
                except:
                    secret_data = {}
                
                secret_data[key] = secret_value
            else:
                if isinstance(secret_value, str):
                    secret_data = json.loads(secret_value)
                else:
                    secret_data = secret_value
            
            self.client.secrets.kv.v2.create_or_update_secret(
                path=secret_name,
                secret=secret_data,
                mount_point=self.mount_point
            )
            
            logger.info("Secret set in Vault", secret_name=secret_name, key=key)
            return True
            
        except Exception as e:
            logger.error("Failed to set secret in Vault", 
                        secret_name=secret_name, 
                        key=key, 
                        error=str(e))
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from Vault"""
        try:
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=secret_name,
                mount_point=self.mount_point
            )
            
            logger.info("Secret deleted from Vault", secret_name=secret_name)
            return True
            
        except Exception as e:
            logger.error("Failed to delete secret from Vault", 
                        secret_name=secret_name, 
                        error=str(e))
            return False
    
    async def list_secrets(self) -> list[str]:
        """List secrets in Vault"""
        try:
            response = self.client.secrets.kv.v2.list_secrets(
                path="",
                mount_point=self.mount_point
            )
            
            return response.get("data", {}).get("keys", [])
            
        except Exception as e:
            logger.error("Failed to list secrets from Vault", error=str(e))
            return []


class AWSSecretsManager(SecretManager):
    """AWS Secrets Manager integration"""
    
    def __init__(self, region_name: str = "us-east-1", profile_name: Optional[str] = None):
        """
        Initialize AWS Secrets Manager
        
        Args:
            region_name: AWS region
            profile_name: AWS profile name
        """
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            session = boto3.Session(profile_name=profile_name)
            self.client = session.client('secretsmanager', region_name=region_name)
            self.region_name = region_name
            
            logger.info("Connected to AWS Secrets Manager", region=region_name)
            
        except ImportError:
            raise ImportError("boto3 package is required for AWS Secrets Manager integration")
        except Exception as e:
            logger.error("Failed to connect to AWS Secrets Manager", error=str(e))
            raise
    
    async def get_secret(self, secret_name: str, key: Optional[str] = None) -> str:
        """Get secret from AWS Secrets Manager"""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_string = response['SecretString']
            
            if key:
                secret_data = json.loads(secret_string)
                if key not in secret_data:
                    raise KeyError(f"Key '{key}' not found in secret '{secret_name}'")
                return str(secret_data[key])
            
            return secret_string
            
        except Exception as e:
            logger.error("Failed to get secret from AWS Secrets Manager", 
                        secret_name=secret_name, 
                        key=key, 
                        error=str(e))
            raise
    
    async def set_secret(self, secret_name: str, secret_value: Union[str, Dict[str, Any]], key: Optional[str] = None) -> bool:
        """Set secret in AWS Secrets Manager"""
        try:
            if key:
                # Get existing secret data
                try:
                    response = self.client.get_secret_value(SecretId=secret_name)
                    secret_data = json.loads(response['SecretString'])
                except:
                    secret_data = {}
                
                secret_data[key] = secret_value
                secret_string = json.dumps(secret_data)
            else:
                if isinstance(secret_value, dict):
                    secret_string = json.dumps(secret_value)
                else:
                    secret_string = str(secret_value)
            
            self.client.update_secret(
                SecretId=secret_name,
                SecretString=secret_string
            )
            
            logger.info("Secret set in AWS Secrets Manager", secret_name=secret_name, key=key)
            return True
            
        except Exception as e:
            logger.error("Failed to set secret in AWS Secrets Manager", 
                        secret_name=secret_name, 
                        key=key, 
                        error=str(e))
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from AWS Secrets Manager"""
        try:
            self.client.delete_secret(
                SecretId=secret_name,
                ForceDeleteWithoutRecovery=True
            )
            
            logger.info("Secret deleted from AWS Secrets Manager", secret_name=secret_name)
            return True
            
        except Exception as e:
            logger.error("Failed to delete secret from AWS Secrets Manager", 
                        secret_name=secret_name, 
                        error=str(e))
            return False
    
    async def list_secrets(self) -> list[str]:
        """List secrets in AWS Secrets Manager"""
        try:
            response = self.client.list_secrets()
            return [secret['Name'] for secret in response.get('SecretList', [])]
            
        except Exception as e:
            logger.error("Failed to list secrets from AWS Secrets Manager", error=str(e))
            return []


class AzureKeyVaultManager(SecretManager):
    """Azure Key Vault integration"""
    
    def __init__(self, vault_url: str, credential: Optional[Any] = None):
        """
        Initialize Azure Key Vault
        
        Args:
            vault_url: Azure Key Vault URL
            credential: Azure credential (defaults to DefaultAzureCredential)
        """
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
            
            if credential is None:
                credential = DefaultAzureCredential()
            
            self.client = SecretClient(vault_url=vault_url, credential=credential)
            self.vault_url = vault_url
            
            logger.info("Connected to Azure Key Vault", url=vault_url)
            
        except ImportError:
            raise ImportError("azure-keyvault-secrets package is required for Azure Key Vault integration")
        except Exception as e:
            logger.error("Failed to connect to Azure Key Vault", error=str(e))
            raise
    
    async def get_secret(self, secret_name: str, key: Optional[str] = None) -> str:
        """Get secret from Azure Key Vault"""
        try:
            secret = self.client.get_secret(secret_name)
            secret_value = secret.value
            
            if key:
                secret_data = json.loads(secret_value)
                if key not in secret_data:
                    raise KeyError(f"Key '{key}' not found in secret '{secret_name}'")
                return str(secret_data[key])
            
            return secret_value
            
        except Exception as e:
            logger.error("Failed to get secret from Azure Key Vault", 
                        secret_name=secret_name, 
                        key=key, 
                        error=str(e))
            raise
    
    async def set_secret(self, secret_name: str, secret_value: Union[str, Dict[str, Any]], key: Optional[str] = None) -> bool:
        """Set secret in Azure Key Vault"""
        try:
            if key:
                # Get existing secret data
                try:
                    secret = self.client.get_secret(secret_name)
                    secret_data = json.loads(secret.value)
                except:
                    secret_data = {}
                
                secret_data[key] = secret_value
                secret_string = json.dumps(secret_data)
            else:
                if isinstance(secret_value, dict):
                    secret_string = json.dumps(secret_value)
                else:
                    secret_string = str(secret_value)
            
            self.client.set_secret(secret_name, secret_string)
            
            logger.info("Secret set in Azure Key Vault", secret_name=secret_name, key=key)
            return True
            
        except Exception as e:
            logger.error("Failed to set secret in Azure Key Vault", 
                        secret_name=secret_name, 
                        key=key, 
                        error=str(e))
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from Azure Key Vault"""
        try:
            self.client.begin_delete_secret(secret_name)
            
            logger.info("Secret deleted from Azure Key Vault", secret_name=secret_name)
            return True
            
        except Exception as e:
            logger.error("Failed to delete secret from Azure Key Vault", 
                        secret_name=secret_name, 
                        error=str(e))
            return False
    
    async def list_secrets(self) -> list[str]:
        """List secrets in Azure Key Vault"""
        try:
            secrets = self.client.list_properties_of_secrets()
            return [secret.name for secret in secrets]
            
        except Exception as e:
            logger.error("Failed to list secrets from Azure Key Vault", error=str(e))
            return []


class GoogleSecretManager(SecretManager):
    """Google Secret Manager integration"""
    
    def __init__(self, project_id: str):
        """
        Initialize Google Secret Manager
        
        Args:
            project_id: Google Cloud project ID
        """
        try:
            from google.cloud import secretmanager
            
            self.client = secretmanager.SecretManagerServiceClient()
            self.project_id = project_id
            
            logger.info("Connected to Google Secret Manager", project_id=project_id)
            
        except ImportError:
            raise ImportError("google-cloud-secret-manager package is required for Google Secret Manager integration")
        except Exception as e:
            logger.error("Failed to connect to Google Secret Manager", error=str(e))
            raise
    
    async def get_secret(self, secret_name: str, key: Optional[str] = None) -> str:
        """Get secret from Google Secret Manager"""
        try:
            secret_path = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
            response = self.client.access_secret_version(request={"name": secret_path})
            secret_value = response.payload.data.decode("UTF-8")
            
            if key:
                secret_data = json.loads(secret_value)
                if key not in secret_data:
                    raise KeyError(f"Key '{key}' not found in secret '{secret_name}'")
                return str(secret_data[key])
            
            return secret_value
            
        except Exception as e:
            logger.error("Failed to get secret from Google Secret Manager", 
                        secret_name=secret_name, 
                        key=key, 
                        error=str(e))
            raise
    
    async def set_secret(self, secret_name: str, secret_value: Union[str, Dict[str, Any]], key: Optional[str] = None) -> bool:
        """Set secret in Google Secret Manager"""
        try:
            if key:
                # Get existing secret data
                try:
                    secret_path = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
                    response = self.client.access_secret_version(request={"name": secret_path})
                    secret_data = json.loads(response.payload.data.decode("UTF-8"))
                except:
                    secret_data = {}
                
                secret_data[key] = secret_value
                secret_string = json.dumps(secret_data)
            else:
                if isinstance(secret_value, dict):
                    secret_string = json.dumps(secret_value)
                else:
                    secret_string = str(secret_value)
            
            parent = f"projects/{self.project_id}"
            self.client.add_secret_version(
                request={
                    "parent": f"{parent}/secrets/{secret_name}",
                    "payload": {"data": secret_string.encode("UTF-8")}
                }
            )
            
            logger.info("Secret set in Google Secret Manager", secret_name=secret_name, key=key)
            return True
            
        except Exception as e:
            logger.error("Failed to set secret in Google Secret Manager", 
                        secret_name=secret_name, 
                        key=key, 
                        error=str(e))
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from Google Secret Manager"""
        try:
            secret_path = f"projects/{self.project_id}/secrets/{secret_name}"
            self.client.delete_secret(request={"name": secret_path})
            
            logger.info("Secret deleted from Google Secret Manager", secret_name=secret_name)
            return True
            
        except Exception as e:
            logger.error("Failed to delete secret from Google Secret Manager", 
                        secret_name=secret_name, 
                        error=str(e))
            return False
    
    async def list_secrets(self) -> list[str]:
        """List secrets in Google Secret Manager"""
        try:
            parent = f"projects/{self.project_id}"
            secrets = self.client.list_secrets(request={"parent": parent})
            return [secret.name.split("/")[-1] for secret in secrets]
            
        except Exception as e:
            logger.error("Failed to list secrets from Google Secret Manager", error=str(e))
            return []


class EnvironmentSecretManager(SecretManager):
    """Environment variables fallback secret manager"""
    
    def __init__(self):
        """Initialize environment secret manager"""
        logger.info("Using environment variables for secrets management")
    
    async def get_secret(self, secret_name: str, key: Optional[str] = None) -> str:
        """Get secret from environment variables"""
        try:
            env_var_name = secret_name.upper().replace("-", "_")
            secret_value = os.getenv(env_var_name)
            
            if not secret_value:
                raise KeyError(f"Environment variable '{env_var_name}' not found")
            
            if key:
                secret_data = json.loads(secret_value)
                if key not in secret_data:
                    raise KeyError(f"Key '{key}' not found in secret '{secret_name}'")
                return str(secret_data[key])
            
            return secret_value
            
        except Exception as e:
            logger.error("Failed to get secret from environment", 
                        secret_name=secret_name, 
                        key=key, 
                        error=str(e))
            raise
    
    async def set_secret(self, secret_name: str, secret_value: Union[str, Dict[str, Any]], key: Optional[str] = None) -> bool:
        """Set secret in environment variables (not supported)"""
        logger.warning("Cannot set secrets in environment variables", secret_name=secret_name)
        return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from environment variables (not supported)"""
        logger.warning("Cannot delete secrets from environment variables", secret_name=secret_name)
        return False
    
    async def list_secrets(self) -> list[str]:
        """List secrets from environment variables"""
        # This is a simplified implementation
        # In practice, you'd need to know which env vars are secrets
        return []


class SecretsManagerFactory:
    """Factory for creating secret managers"""
    
    @staticmethod
    def create_manager(provider: SecretProvider, **kwargs) -> SecretManager:
        """
        Create a secret manager instance
        
        Args:
            provider: Secret management provider
            **kwargs: Provider-specific configuration
            
        Returns:
            SecretManager instance
        """
        if provider == SecretProvider.VAULT:
            return HashiCorpVaultManager(
                vault_url=kwargs.get("vault_url"),
                vault_token=kwargs.get("vault_token"),
                mount_point=kwargs.get("mount_point", "secret")
            )
        elif provider == SecretProvider.AWS_SECRETS_MANAGER:
            return AWSSecretsManager(
                region_name=kwargs.get("region_name", "us-east-1"),
                profile_name=kwargs.get("profile_name")
            )
        elif provider == SecretProvider.AZURE_KEY_VAULT:
            return AzureKeyVaultManager(
                vault_url=kwargs.get("vault_url"),
                credential=kwargs.get("credential")
            )
        elif provider == SecretProvider.GOOGLE_SECRET_MANAGER:
            return GoogleSecretManager(
                project_id=kwargs.get("project_id")
            )
        elif provider == SecretProvider.ENVIRONMENT:
            return EnvironmentSecretManager()
        else:
            raise ValueError(f"Unsupported secret provider: {provider}")


# Global secret manager instance
_secret_manager: Optional[SecretManager] = None


def get_secret_manager() -> SecretManager:
    """Get the global secret manager instance"""
    global _secret_manager
    
    if _secret_manager is None:
        # Initialize based on environment configuration
        provider = SecretProvider(os.getenv("SECRET_PROVIDER", "environment"))
        
        config = {
            "vault_url": os.getenv("VAULT_URL"),
            "vault_token": os.getenv("VAULT_TOKEN"),
            "mount_point": os.getenv("VAULT_MOUNT_POINT", "secret"),
            "region_name": os.getenv("AWS_REGION", "us-east-1"),
            "profile_name": os.getenv("AWS_PROFILE"),
            "vault_url": os.getenv("AZURE_VAULT_URL"),
            "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        }
        
        _secret_manager = SecretsManagerFactory.create_manager(provider, **config)
    
    return _secret_manager


async def get_secret(secret_name: str, key: Optional[str] = None) -> str:
    """
    Get a secret value
    
    Args:
        secret_name: Name of the secret
        key: Optional key within the secret
        
    Returns:
        Secret value
    """
    manager = get_secret_manager()
    return await manager.get_secret(secret_name, key)


async def set_secret(secret_name: str, secret_value: Union[str, Dict[str, Any]], key: Optional[str] = None) -> bool:
    """
    Set a secret value
    
    Args:
        secret_name: Name of the secret
        secret_value: Value to store
        key: Optional key within the secret
        
    Returns:
        Success status
    """
    manager = get_secret_manager()
    return await manager.set_secret(secret_name, secret_value, key)
