from datetime import datetime, timedelta
from typing import Dict, Optional
from ..exceptions import AuthenticationError

class TokenValidator:
    """Token validation and management mixin"""
    
    def __init__(self):
        self._token: Optional[Dict] = None
        self._token_expiry: Optional[datetime] = None
    
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
    
    def get_current_token(self) -> Dict:
        """
        Get the current token if valid.
        
        Returns:
            Dict: The current token
            
        Raises:
            AuthenticationError: If no valid token is available
        """
        if not self._is_token_valid():
            raise AuthenticationError("No valid token available")
        return self._token