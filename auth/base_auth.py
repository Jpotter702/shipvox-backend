# Base Auth
# TODO: Implement this module

from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime, timedelta

class BaseCarrierAuth(ABC):
    """Abstract base class for carrier authentication implementations."""
    
    def __init__(self, client_id: str, client_secret: str, environment: str = "production"):
        """
        Initialize the carrier authentication handler.
        
        Args:
            client_id (str): The client ID for the carrier API
            client_secret (str): The client secret for the carrier API
            environment (str): The environment to use ('production' or 'sandbox')
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.environment = environment
        self._token: Optional[Dict] = None
        self._token_expiry: Optional[datetime] = None
    
    @abstractmethod
    async def get_access_token(self) -> str:
        """
        Get a valid access token for the carrier API.
        This method should handle token caching and renewal.
        
        Returns:
            str: The access token
        """
        pass
    
    @abstractmethod
    async def _fetch_new_token(self) -> Dict:
        """
        Fetch a new access token from the carrier's OAuth endpoint.
        
        Returns:
            Dict: The token response containing access_token and expiry
        """
        pass
    
    def _is_token_valid(self) -> bool:
        """
        Check if the current token is still valid.
        
        Returns:
            bool: True if the token is valid, False otherwise
        """
        if not self._token or not self._token_expiry:
            return False
        return datetime.now() < self._token_expiry - timedelta(minutes=5)
    
    def _update_token(self, token_response: Dict) -> None:
        """
        Update the stored token information.
        
        Args:
            token_response (Dict): The token response from the carrier
        """
        self._token = token_response
        expires_in = token_response.get('expires_in', 3600)
        self._token_expiry = datetime.now() + timedelta(seconds=expires_in)
    
    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get the authentication headers required for API requests.
        
        Returns:
            Dict[str, str]: The headers dictionary
        """
        pass
