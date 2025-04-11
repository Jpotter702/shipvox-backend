from typing import Dict, Type, Optional
from abc import ABC, abstractmethod
from .exceptions import CarrierNotSupportedError, InvalidAuthFlowError

class CarrierAuthProvider(ABC):
    """Abstract base class for carrier-specific auth implementations"""
    
    @abstractmethod
    def get_auth_url(self, user_context: dict) -> str:
        """Generate OAuth authorization URL"""
        pass
    
    @abstractmethod
    def exchange_token(self, request_data: dict) -> dict:
        """Exchange authorization code for tokens"""
        pass
    
    @abstractmethod
    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        pass

class CarrierRegistry:
    """Registry for carrier auth providers"""
    
    def __init__(self):
        self._providers: Dict[str, CarrierAuthProvider] = {}
    
    def register(self, carrier: str, provider: CarrierAuthProvider) -> None:
        """Register a carrier auth provider"""
        self._providers[carrier.lower()] = provider
    
    def get_provider(self, carrier: str) -> Optional[CarrierAuthProvider]:
        """Get auth provider for carrier"""
        return self._providers.get(carrier.lower())
    
    def __getitem__(self, carrier: str) -> CarrierAuthProvider:
        """Get provider with dictionary syntax"""
        provider = self.get_provider(carrier)
        if not provider:
            raise CarrierNotSupportedError(f"No auth provider registered for carrier: {carrier}")
        return provider 