# Label Creator
# TODO: Implement this module

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class Address:
    """Represents a shipping address."""
    name: str
    company: Optional[str]
    street1: str
    street2: Optional[str]
    city: str
    state: str
    zip_code: str
    country: str
    phone: str
    email: Optional[str]

@dataclass
class Package:
    """Represents package details."""
    weight: float  # in pounds
    length: float  # in inches
    width: float   # in inches
    height: float  # in inches
    packaging_type: str
    reference: Optional[str] = None

@dataclass
class LabelRequest:
    """Represents a label generation request."""
    from_address: Address
    to_address: Address
    package: Package
    service_code: str
    is_residential: bool = True
    insurance_amount: Optional[float] = None
    signature_required: bool = False
    saturday_delivery: bool = False
    reference: Optional[str] = None

@dataclass
class LabelResponse:
    """Represents a label generation response."""
    tracking_number: str
    label_data: bytes  # PDF or ZPL format
    label_format: str  # 'PDF' or 'ZPL'
    carrier: str
    service: str
    cost: float
    created_at: datetime
    estimated_delivery: Optional[datetime] = None
    qr_code: Optional[bytes] = None

class LabelCreator(ABC):
    """Abstract base class for carrier-specific label creation."""
    
    @abstractmethod
    async def create_label(self, request: LabelRequest) -> LabelResponse:
        """
        Create a shipping label.
        
        Args:
            request (LabelRequest): The label generation request
            
        Returns:
            LabelResponse: The generated label and associated data
            
        Raises:
            LabelError: If label generation fails
        """
        pass
    
    @abstractmethod
    async def void_label(self, tracking_number: str) -> bool:
        """
        Void a previously created shipping label.
        
        Args:
            tracking_number (str): The tracking number of the label to void
            
        Returns:
            bool: True if voided successfully, False otherwise
            
        Raises:
            LabelError: If voiding fails
        """
        pass
    
    @abstractmethod
    async def get_label_status(self, tracking_number: str) -> Dict[str, Any]:
        """
        Get the status of a shipping label.
        
        Args:
            tracking_number (str): The tracking number to check
            
        Returns:
            Dict[str, Any]: Label status information
            
        Raises:
            LabelError: If status check fails
        """
        pass
