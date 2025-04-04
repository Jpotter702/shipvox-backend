"""Authentication module initialization."""
from typing import Dict, Optional
from pathlib import Path
import json
import os

from auth.fedex_auth import FedExAuth
from auth.ups_auth import UPSAuth
from utils.exceptions import ConfigurationError
from utils.log import logger

class AuthManager:
    """Manages carrier authentication instances."""
    
    def __init__(self):
        """Initialize the auth manager."""
        self.fedex_auth: Optional[FedExAuth] = None
        self.ups_auth: Optional[UPSAuth] = None
        self._config: Dict = {}
        
    def initialize(self, config_file: Optional[str] = None) -> None:
        """
        Initialize authentication with configuration.
        
        Args:
            config_file (Optional[str]): Path to config file. If None, uses environment variables.
        """
        if config_file:
            self._load_config_file(config_file)
        else:
            self._load_config_env()
            
        self._initialize_auth()

    def initialize_with_config(self, fedex_config: Dict, ups_config: Dict) -> None:
        """
        Initialize authentication with direct config dictionaries.
        
        Args:
            fedex_config (Dict): FedEx configuration dictionary
            ups_config (Dict): UPS configuration dictionary
        """
        self._config = {
            "fedex": fedex_config,
            "ups": ups_config
        }
        self._initialize_auth()
        
    def _load_config_file(self, config_file: str) -> None:
        """Load configuration from a JSON file."""
        try:
            with open(config_file, 'r') as f:
                self._config = json.load(f)
        except Exception as e:
            raise ConfigurationError(f"Failed to load config file: {str(e)}")
            
    def _load_config_env(self) -> None:
        """Load configuration from environment variables."""
        self._config = {
            "fedex": {
                "client_id": os.getenv("FEDEX_CLIENT_ID"),
                "client_secret": os.getenv("FEDEX_CLIENT_SECRET"),
                "environment": os.getenv("FEDEX_ENVIRONMENT", "sandbox")
            },
            "ups": {
                "client_id": os.getenv("UPS_CLIENT_ID"),
                "client_secret": os.getenv("UPS_CLIENT_SECRET"),
                "environment": os.getenv("UPS_ENVIRONMENT", "sandbox")
            }
        }
        
    def _initialize_auth(self) -> None:
        """Initialize authentication instances."""
        # Initialize FedEx auth if credentials are available
        fedex_config = self._config.get("fedex", {})
        if fedex_config.get("client_id") and fedex_config.get("client_secret"):
            self.fedex_auth = FedExAuth(
                client_id=fedex_config["client_id"],
                client_secret=fedex_config["client_secret"],
                environment=fedex_config.get("environment", "sandbox")
            )
            logger.info("FedEx authentication initialized")
        else:
            logger.warning("FedEx credentials not found")
            
        # Initialize UPS auth if credentials are available
        ups_config = self._config.get("ups", {})
        if ups_config.get("client_id") and ups_config.get("client_secret"):
            self.ups_auth = UPSAuth(
                client_id=ups_config["client_id"],
                client_secret=ups_config["client_secret"],
                environment=ups_config.get("environment", "sandbox")
            )
            logger.info("UPS authentication initialized")
        else:
            logger.warning("UPS credentials not found")
            
    async def get_fedex_auth(self) -> FedExAuth:
        """
        Get the FedEx auth instance.
        
        Returns:
            FedExAuth: The FedEx auth instance
            
        Raises:
            ConfigurationError: If FedEx auth is not initialized
        """
        if not self.fedex_auth:
            raise ConfigurationError("FedEx authentication not initialized")
        return self.fedex_auth
        
    async def get_ups_auth(self) -> UPSAuth:
        """
        Get the UPS auth instance.
        
        Returns:
            UPSAuth: The UPS auth instance
            
        Raises:
            ConfigurationError: If UPS auth is not initialized
        """
        if not self.ups_auth:
            raise ConfigurationError("UPS authentication not initialized")
        return self.ups_auth

# Create a singleton instance
auth_manager = AuthManager()

def get_auth_manager() -> AuthManager:
    """
    Get the singleton auth manager instance.
    
    Returns:
        AuthManager: The auth manager instance
    """
    global auth_manager
    return auth_manager

__all__ = ['AuthManager', 'auth_manager', 'get_auth_manager']
