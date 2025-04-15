from typing import Dict
import requests
from urllib.parse import urlencode
from .base import TokenValidator
from ..carrier_registry import CarrierAuthProvider
from ..exceptions import AuthenticationError

class UPSAuthProvider(CarrierAuthProvider, TokenValidator):
    """UPS authentication provider using OAuth authorization code flow"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, sandbox: bool = False):
        CarrierAuthProvider.__init__(self)
        TokenValidator.__init__(self)
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = "https://wwwcie.ups.com" if sandbox else "https://onlinetools.ups.com"
    
    def get_auth_url(self, user_context: dict) -> str:
        """Generate UPS OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "read write",  # Adjust scopes as needed
            "state": user_context.get("state", "")
        }
        return f"{self.base_url}/security/v1/oauth/authorize?{urlencode(params)}"
    
    def exchange_token(self, request_data: dict) -> dict:
        """Exchange authorization code for tokens"""
        try:
            response = requests.post(
                f"{self.base_url}/security/v1/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "code": request_data["code"],
                    "redirect_uri": self.redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            token_data = response.json()
            self._update_token(token_data)
            return token_data
        except Exception as e:
            raise AuthenticationError(f"UPS token exchange failed: {str(e)}")
    
    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        try:
            response = requests.post(
                f"{self.base_url}/security/v1/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            token_data = response.json()
            self._update_token(token_data)
            return token_data
        except Exception as e:
            raise AuthenticationError(f"UPS token refresh failed: {str(e)}")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for UPS API requests"""
        token = self.get_current_token()
        return {
            "Authorization": f"Bearer {token['access_token']}",
            "Content-Type": "application/json",
            "x-merchant-id": self.client_id
        }    