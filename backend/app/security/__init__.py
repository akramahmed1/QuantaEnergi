"""
Security module for QuantaEnergi API
Provides comprehensive security features including secrets management, vulnerability scanning, and compliance
"""

from .secrets_manager import (
    SecretManager,
    SecretProvider,
    SecretsManagerFactory,
    get_secret_manager,
    get_secret,
    set_secret
)

from .owasp_scan import (
    OWASPScanner,
    run_security_scan
)

__all__ = [
    "SecretManager",
    "SecretProvider", 
    "SecretsManagerFactory",
    "get_secret_manager",
    "get_secret",
    "set_secret",
    "OWASPScanner",
    "run_security_scan"
]
