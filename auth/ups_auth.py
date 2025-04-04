# Ups Auth
# TODO: Implement this module

import aiohttp
from typing import Dict
from .base_auth import BaseCarrierAuth

class UPSAuth(BaseCarrierAuth):
    """UPS OAuth2 authentication implementation."""
    
    def __init__(self, client_id: str, client_secret: str, environment: str = "production"):
        """
        Initialize UPS authentication handler.
        
        Args:
            client_id (str): UPS API client ID
            client_secret (str): UPS API client secret
            environment (str): 'production' or 'sandbox'
        """
        super().__init__(client_id, client_secret, environment)
        self._base_url = (
            "https://onlinetools.ups.com" if environment == "production"
            else "https://wwwcie.ups.com"
        )
    
    async def get_access_token(self) -> str:
        """
        Get a valid UPS access token.
        
        Returns:
            str: The access token
        """
        if not self._is_token_valid():
            token_response = await self._fetch_new_token()
            self._update_token(token_response)
        return self._token["access_token"]
    
    async def _fetch_new_token(self) -> Dict:
        """
        Fetch a new access token from UPS OAuth endpoint.
        
        Returns:
            Dict: The token response
        """
        url = f"{self._base_url}/security/v1/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "x-merchant-id": self.client_id
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to get UPS token: {error_text}")
                return await response.json()
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get the authentication headers for UPS API requests.
        
        Returns:
            Dict[str, str]: The headers dictionary
        """
        return {
            "Authorization": f"Bearer {self._token['access_token']}",
            "Content-Type": "application/json",
            "x-merchant-id": self.client_id
        }
