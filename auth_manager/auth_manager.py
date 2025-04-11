from typing import Dict, Optional
import threading
from .carrier_registry import CarrierRegistry
from .token_store import TokenStore
from .exceptions import AuthenticationError

class AuthManager:
    """Main authentication manager for handling carrier-specific auth flows"""
    
    def __init__(self, carrier_registry: CarrierRegistry, token_store: Optional[TokenStore] = None):
        self.carriers = carrier_registry
        self.token_store = token_store
        self._refresh_lock = threading.Lock()  # Add thread safety

    def initiate_auth(self, carrier: str, user_context: dict) -> str:
        """Initiate authentication flow for a carrier"""
        try:
            return self.carriers[carrier].get_auth_url(user_context)
        except Exception as e:
            raise AuthenticationError(f"Failed to initiate auth for {carrier}: {str(e)}")

    def handle_callback(self, carrier: str, request_data: dict) -> dict:
        """Handle OAuth callback and store tokens"""
        try:
            tokens = self.carriers[carrier].exchange_token(request_data)
            if self.token_store:
                self.token_store.save_tokens(
                    request_data.get("user_id"),
                    carrier,
                    tokens
                )
            return tokens
        except Exception as e:
            raise AuthenticationError(f"Failed to handle callback for {carrier}: {str(e)}")

    def refresh_token(self, carrier: str, refresh_token: str) -> dict:
        """Refresh access token for a carrier"""
        try:
            return self.carriers[carrier].refresh_token(refresh_token)
        except Exception as e:
            raise AuthenticationError(f"Failed to refresh token for {carrier}: {str(e)}")

    def get_valid_token(self, user_id: str, carrier: str) -> dict:
        """Get valid token, refreshing if necessary"""
        if not self.token_store:
            raise AuthenticationError("Token store not configured")
            
        tokens = self.token_store.get_tokens(user_id, carrier)
        
        if self.token_store.should_refresh(user_id, carrier):
            with self._refresh_lock:
                # Double-check after acquiring lock
                if self.token_store.should_refresh(user_id, carrier):
                    refresh_token = self.token_store.get_refresh_token(user_id, carrier)
                    new_tokens = self.refresh_token(carrier, refresh_token)
                    self.token_store.save_tokens(user_id, carrier, new_tokens)
                    return new_tokens
        
        return tokens
