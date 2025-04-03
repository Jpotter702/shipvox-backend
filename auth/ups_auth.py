from datetime import datetime, timedelta
import requests
from .base_auth import BaseAuth

class UPSAuth(BaseAuth):
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry = None
        self.refresh_token = None
        
    def get_token(self) -> str:
        """Returns current access token, refreshes if expired"""
        if not self._is_token_valid():
            self._refresh_token()
        return self.access_token

    def _is_token_valid(self) -> bool:
        """Check if current token is valid and not expired"""
        if not self.access_token or not self.token_expiry:
            return False
        return datetime.now() < self.token_expiry

    def _refresh_token(self) -> None:
        """Get new access token using client credentials"""
        url = "https://onlinetools.ups.com/security/v1/oauth/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.token_expiry = datetime.now() + timedelta(seconds=token_data["expires_in"])
        self.refresh_token = token_data.get("refresh_token")
