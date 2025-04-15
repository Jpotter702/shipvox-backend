from abc import ABC, abstractmethod
from typing import List
from .models import RateRequest, RateResponse

class RateService(ABC):
    """Base class for carrier rate services."""
    
    @abstractmethod
    async def get_rates(self, request: RateRequest) -> List[RateResponse]:
        """Get shipping rates from carrier.
        
        Args:
            request (RateRequest): The rate request details
            
        Returns:
            List[RateResponse]: List of available shipping options
            
        Raises:
            ValueError: If the request is invalid
            Exception: If the API request fails
        """
        pass
    
    @abstractmethod
    async def validate_request(self, request: RateRequest) -> None:
        """Validate carrier-specific requirements.
        
        Args:
            request (RateRequest): The rate request to validate
            
        Raises:
            ValueError: If the request is invalid
        """
        pass 