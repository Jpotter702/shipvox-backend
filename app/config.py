# Config
# TODO: Implement this module

from pathlib import Path
from typing import Dict, Any, Optional
import os
import json

class Config:
    """Application configuration manager."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file (Optional[str]): Path to config file. If None, uses environment variables.
        """
        self._config: Dict[str, Any] = {}
        self._load_config(config_file)
    
    def _load_config(self, config_file: Optional[str]) -> None:
        """Load configuration from file or environment."""
        if config_file:
            self._load_from_file(config_file)
        else:
            self._load_from_env()
            
        # Validate required settings
        self._validate_config()
    
    def _load_from_file(self, config_file: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                self._config = json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load config file: {str(e)}")
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        self._config = {
            "environment": os.getenv("SHIPVOX_ENVIRONMENT", "sandbox"),
            "log_level": os.getenv("SHIPVOX_LOG_LEVEL", "INFO"),
            "log_file": os.getenv("SHIPVOX_LOG_FILE"),
            "fedex": {
                "client_id": os.getenv("FEDEX_CLIENT_ID"),
                "client_secret": os.getenv("FEDEX_CLIENT_SECRET"),
                "account_number": os.getenv("FEDEX_ACCOUNT_NUMBER")
            },
            "ups": {
                "client_id": os.getenv("UPS_CLIENT_ID"),
                "client_secret": os.getenv("UPS_CLIENT_SECRET"),
                "account_number": os.getenv("UPS_ACCOUNT_NUMBER")
            }
        }
    
    def _validate_config(self) -> None:
        """Validate required configuration settings."""
        required_settings = [
            ("environment", "SHIPVOX_ENVIRONMENT"),
            ("fedex.client_id", "FEDEX_CLIENT_ID"),
            ("fedex.client_secret", "FEDEX_CLIENT_SECRET"),
            ("fedex.account_number", "FEDEX_ACCOUNT_NUMBER"),
            ("ups.client_id", "UPS_CLIENT_ID"),
            ("ups.client_secret", "UPS_CLIENT_SECRET"),
            ("ups.account_number", "UPS_ACCOUNT_NUMBER")
        ]
        
        missing = []
        for path, env_var in required_settings:
            value = self.get(path)
            if not value:
                missing.append(f"{path} ({env_var})")
                
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation path.
        
        Args:
            path (str): Configuration path (e.g., 'fedex.client_id')
            default (Any): Default value if path not found
            
        Returns:
            Any: Configuration value
        """
        parts = path.split('.')
        value = self._config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
                
        return value
    
    @property
    def environment(self) -> str:
        """Get application environment."""
        return self.get("environment", "sandbox")
    
    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self.get("log_level", "INFO")
    
    @property
    def log_file(self) -> Optional[str]:
        """Get log file path."""
        return self.get("log_file")
    
    @property
    def fedex_config(self) -> Dict[str, str]:
        """Get FedEx configuration."""
        return self.get("fedex", {})
    
    @property
    def ups_config(self) -> Dict[str, str]:
        """Get UPS configuration."""
        return self.get("ups", {})
