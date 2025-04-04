#   Init  
# TODO: Implement this module

from typing import Dict, Type
from .label_creator import LabelCreator, LabelRequest, LabelResponse
from .fedex_ship import FedExLabelCreator
from .ups_ship import UPSLabelCreator
from ..auth import AuthManager

class LabelManager:
    """Manages label creation for different carriers."""
    
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self._creators: Dict[str, LabelCreator] = {}
        
    async def get_creator(self, carrier: str) -> LabelCreator:
        """
        Get a label creator for the specified carrier.
        
        Args:
            carrier (str): The carrier name ('FedEx' or 'UPS')
            
        Returns:
            LabelCreator: The label creator instance
            
        Raises:
            ValueError: If the carrier is not supported
        """
        carrier = carrier.lower()
        if carrier not in self._creators:
            if carrier == 'fedex':
                auth = await self.auth_manager.get_fedex_auth()
                self._creators[carrier] = FedExLabelCreator(auth)
            elif carrier == 'ups':
                auth = await self.auth_manager.get_ups_auth()
                self._creators[carrier] = UPSLabelCreator(auth)
            else:
                raise ValueError(f"Unsupported carrier: {carrier}")
        return self._creators[carrier]
    
    async def create_label(self, carrier: str, request: LabelRequest) -> LabelResponse:
        """
        Create a shipping label for the specified carrier.
        
        Args:
            carrier (str): The carrier name ('FedEx' or 'UPS')
            request (LabelRequest): The label generation request
            
        Returns:
            LabelResponse: The generated label and associated data
            
        Raises:
            ValueError: If the carrier is not supported
            LabelError: If label generation fails
        """
        creator = await self.get_creator(carrier)
        return await creator.create_label(request)
    
    async def void_label(self, carrier: str, tracking_number: str) -> bool:
        """
        Void a shipping label for the specified carrier.
        
        Args:
            carrier (str): The carrier name ('FedEx' or 'UPS')
            tracking_number (str): The tracking number of the label to void
            
        Returns:
            bool: True if voided successfully, False otherwise
            
        Raises:
            ValueError: If the carrier is not supported
            LabelError: If voiding fails
        """
        creator = await self.get_creator(carrier)
        return await creator.void_label(tracking_number)
    
    async def get_label_status(self, carrier: str, tracking_number: str) -> Dict[str, Any]:
        """
        Get the status of a shipping label for the specified carrier.
        
        Args:
            carrier (str): The carrier name ('FedEx' or 'UPS')
            tracking_number (str): The tracking number to check
            
        Returns:
            Dict[str, Any]: Label status information
            
        Raises:
            ValueError: If the carrier is not supported
            LabelError: If status check fails
        """
        creator = await self.get_creator(carrier)
        return await creator.get_label_status(tracking_number)

# Create a singleton instance
_label_manager: LabelManager = None

def get_label_manager(auth_manager: AuthManager = None) -> LabelManager:
    """
    Get the singleton label manager instance.
    
    Args:
        auth_manager (AuthManager, optional): The auth manager to use. If not provided,
            a new one will be created.
            
    Returns:
        LabelManager: The label manager instance
    """
    global _label_manager
    if _label_manager is None:
        if auth_manager is None:
            from ..auth import get_auth_manager
            auth_manager = get_auth_manager()
        _label_manager = LabelManager(auth_manager)
    return _label_manager

__all__ = [
    'LabelManager',
    'LabelCreator',
    'LabelRequest',
    'LabelResponse',
    'FedExLabelCreator',
    'UPSLabelCreator',
    'get_label_manager'
]
