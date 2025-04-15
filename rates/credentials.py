from typing import Dict, Optional
import os
from pydantic import BaseModel

class CarrierCredentials(BaseModel):
    """Base class for carrier credentials."""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    account_number: Optional[str] = None
    
    @property
    def is_active(self) -> bool:
        """Check if the carrier has all required credentials."""
        return all([
            self.api_key is not None,
            self.api_secret is not None,
            self.account_number is not None
        ])

class CredentialsManager:
    """Manages carrier credentials and activation status."""
    
    def __init__(self):
        self.credentials: Dict[str, CarrierCredentials] = {
            "FedEx": CarrierCredentials(
                api_key=os.getenv("FEDEX_API_KEY"),
                api_secret=os.getenv("FEDEX_API_SECRET"),
                account_number=os.getenv("FEDEX_ACCOUNT_NUMBER")
            ),
            "UPS": CarrierCredentials(
                api_key=os.getenv("UPS_API_KEY"),
                api_secret=os.getenv("UPS_API_SECRET"),
                account_number=os.getenv("UPS_ACCOUNT_NUMBER")
            )
        }
    
    def is_carrier_active(self, carrier: str) -> bool:
        """Check if a carrier is active (has all required credentials)."""
        if carrier not in self.credentials:
            return False
        return self.credentials[carrier].is_active
    
    def get_credentials(self, carrier: str) -> Optional[CarrierCredentials]:
        """Get credentials for a specific carrier."""
        return self.credentials.get(carrier) 