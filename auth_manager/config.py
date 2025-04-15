from typing import Optional
from pydantic import BaseSettings, validator
import os

class CarrierConfig(BaseSettings):
    """Base configuration for carrier authentication"""
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

class AuthSettings(BaseSettings):
    """Global authentication settings"""
    # Database settings
    database_url: str = "sqlite:///tokens.db"
    
    # Token settings
    token_encryption_key: Optional[str] = None
    token_refresh_buffer_minutes: int = 10
    token_expiration_buffer_minutes: int = 5
    
    # Carrier configurations
    fedex_enabled: bool = False
    fedex_client_id: Optional[str] = None
    fedex_client_secret: Optional[str] = None
    fedex_sandbox: bool = True
    
    ups_enabled: bool = False
    ups_client_id: Optional[str] = None
    ups_client_secret: Optional[str] = None
    ups_redirect_uri: Optional[str] = None
    ups_sandbox: bool = True
    
    # Monitoring settings
    enable_metrics: bool = True
    metrics_port: int = 9090
    log_level: str = "INFO"
    
    class Config:
        env_prefix = 'AUTH_'
        case_sensitive = False

    def get_fedex_config(self) -> Optional[dict]:
        """Get FedEx configuration if enabled"""
        if not self.fedex_enabled:
            return None
        return {
            "client_id": self.fedex_client_id,
            "client_secret": self.fedex_client_secret,
            "sandbox": self.fedex_sandbox
        }
    
    def get_ups_config(self) -> Optional[dict]:
        """Get UPS configuration if enabled"""
        if not self.ups_enabled:
            return None
        return {
            "client_id": self.ups_client_id,
            "client_secret": self.ups_client_secret,
            "redirect_uri": self.ups_redirect_uri,
            "sandbox": self.ups_sandbox
        }

# Global settings instance
settings = AuthSettings() 