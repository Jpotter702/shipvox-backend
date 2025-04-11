from typing import Dict
import requests
from ..carrier_registry import CarrierAuthProvider
from ..exceptions import AuthenticationError, InvalidAuthFlowError

class FedExAuthProvider(CarrierAuthProvider):
    """FedEx authentication provider using client credentials flow"""
    
    def __init__(self, client_id: str, client_secret: str, sandbox: bool = False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://apis-sandbox.fedex.com" if sandbox else "https://apis.fedex.com"
    
    def get_auth_url(self, user_context: dict) -> str:
        """
        FedEx uses client credentials flow, so no auth URL needed
        This method exists for interface consistency
        """
        raise InvalidAuthFlowError("FedEx does not support OAuth authorization flow")
    
    def exchange_token(self, request_data: dict) -> dict:
        """Get initial access token using client credentials"""
        try:
            response = requests.post(
                f"{self.base_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise AuthenticationError(f"FedEx token exchange failed: {str(e)}")
    
    def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh tokens - for FedEx this is same as getting new token
        since it uses client credentials flow
        """
        return self.exchange_token({}) 