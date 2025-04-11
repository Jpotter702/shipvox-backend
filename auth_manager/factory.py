from typing import Optional, Dict, Any
from pydantic import BaseModel, validator
from .auth_manager import AuthManager
from .token_store import TokenStore
from .carrier_registry import CarrierRegistry
from .providers.fedex_auth import FedExAuthProvider
from .providers.ups_auth import UPSAuthProvider

class CarrierConfig(BaseModel):
    """Base configuration model for carriers"""
    client_id: str
    client_secret: str
    sandbox: bool = False

    @validator('client_id', 'client_secret')
    def validate_credentials(cls, v):
        if not v:
            raise ValueError("Credentials cannot be empty")
        return v

class UPSConfig(CarrierConfig):
    """UPS-specific configuration"""
    redirect_uri: str

    @validator('redirect_uri')
    def validate_redirect_uri(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Redirect URI must be a valid URL")
        return v

class AuthManagerFactory:
    """Factory for creating configured AuthManager instances"""
    
    @staticmethod
    def create(
        fedex_config: Optional[Dict[str, Any]] = None,
        ups_config: Optional[Dict[str, Any]] = None,
        encryption_key: Optional[str] = None
    ) -> AuthManager:
        """
        Create AuthManager with configured providers
        
        Args:
            fedex_config: Dict with client_id, client_secret, sandbox
            ups_config: Dict with client_id, client_secret, redirect_uri, sandbox
            encryption_key: Optional encryption key for TokenStore
        """
        registry = CarrierRegistry()
        
        # Register FedEx provider if configured
        if fedex_config:
            config = CarrierConfig(**fedex_config)
            registry.register(
                "fedex",
                FedExAuthProvider(
                    client_id=config.client_id,
                    client_secret=config.client_secret,
                    sandbox=config.sandbox
                )
            )
        
        # Register UPS provider if configured
        if ups_config:
            config = UPSConfig(**ups_config)
            registry.register(
                "ups",
                UPSAuthProvider(
                    client_id=config.client_id,
                    client_secret=config.client_secret,
                    redirect_uri=config.redirect_uri,
                    sandbox=config.sandbox
                )
            )
        
        # Create token store with encryption
        token_store = TokenStore(encryption_key=encryption_key)
        
        # Create and return configured auth manager
        return AuthManager(registry, token_store) 