# Validators
# TODO: Implement this module

import re
from typing import Dict, Any, Optional
from ..utils.exceptions import ValidationError

class ShippingValidator:
    """Validates shipping-related input data."""
    
    ZIP_CODE_PATTERN = re.compile(r'^\d{5}(-\d{4})?$')
    
    @staticmethod
    def validate_zip_code(zip_code: str, field_name: str = "zip_code") -> None:
        """
        Validate a US ZIP code.
        
        Args:
            zip_code (str): The ZIP code to validate
            field_name (str): The name of the field being validated
            
        Raises:
            ValidationError: If the ZIP code is invalid
        """
        if not zip_code:
            raise ValidationError(f"{field_name} is required")
            
        if not ShippingValidator.ZIP_CODE_PATTERN.match(zip_code):
            raise ValidationError(f"Invalid {field_name} format: {zip_code}")
    
    @staticmethod
    def validate_dimensions(dimensions: Dict[str, float]) -> None:
        """
        Validate package dimensions.
        
        Args:
            dimensions (Dict[str, float]): Dictionary with length, width, height
            
        Raises:
            ValidationError: If dimensions are invalid
        """
        required_fields = ['length', 'width', 'height']
        
        for field in required_fields:
            if field not in dimensions:
                raise ValidationError(f"Missing dimension: {field}")
                
            value = dimensions[field]
            if not isinstance(value, (int, float)):
                raise ValidationError(f"{field} must be a number")
                
            if value <= 0:
                raise ValidationError(f"{field} must be positive")
    
    @staticmethod
    def validate_weight(weight: float) -> None:
        """
        Validate package weight.
        
        Args:
            weight (float): The package weight in pounds
            
        Raises:
            ValidationError: If weight is invalid
        """
        if not isinstance(weight, (int, float)):
            raise ValidationError("Weight must be a number")
            
        if weight <= 0:
            raise ValidationError("Weight must be positive")
    
    @staticmethod
    def validate_address(address: Dict[str, Any]) -> None:
        """
        Validate shipping address.
        
        Args:
            address (Dict[str, Any]): Address information
            
        Raises:
            ValidationError: If address is invalid
        """
        required_fields = ['street', 'city', 'state', 'zip_code']
        
        for field in required_fields:
            if field not in address:
                raise ValidationError(f"Missing address field: {field}")
                
            if not address[field]:
                raise ValidationError(f"Empty address field: {field}")
        
        ShippingValidator.validate_zip_code(address['zip_code'], 'zip_code')
    
    @staticmethod
    def validate_rate_request(request: Dict[str, Any]) -> None:
        """
        Validate a rate request.
        
        Args:
            request (Dict[str, Any]): Rate request data
            
        Raises:
            ValidationError: If request is invalid
        """
        required_fields = ['origin_zip', 'destination_zip', 'weight', 'dimensions']
        
        for field in required_fields:
            if field not in request:
                raise ValidationError(f"Missing required field: {field}")
        
        ShippingValidator.validate_zip_code(request['origin_zip'], 'origin_zip')
        ShippingValidator.validate_zip_code(request['destination_zip'], 'destination_zip')
        ShippingValidator.validate_weight(request['weight'])
        ShippingValidator.validate_dimensions(request['dimensions'])
    
    @staticmethod
    def validate_label_request(request: Dict[str, Any]) -> None:
        """
        Validate a label generation request.
        
        Args:
            request (Dict[str, Any]): Label request data
            
        Raises:
            ValidationError: If request is invalid
        """
        required_fields = [
            'carrier', 'service', 'from_address', 'to_address',
            'weight', 'dimensions'
        ]
        
        for field in required_fields:
            if field not in request:
                raise ValidationError(f"Missing required field: {field}")
        
        if request['carrier'] not in ['fedex', 'ups']:
            raise ValidationError(f"Invalid carrier: {request['carrier']}")
        
        ShippingValidator.validate_address(request['from_address'])
        ShippingValidator.validate_address(request['to_address'])
        ShippingValidator.validate_weight(request['weight'])
        ShippingValidator.validate_dimensions(request['dimensions'])
    
    @staticmethod
    def validate_pickup_request(request: Dict[str, Any]) -> None:
        """
        Validate a pickup scheduling request.
        
        Args:
            request (Dict[str, Any]): Pickup request data
            
        Raises:
            ValidationError: If request is invalid
        """
        required_fields = [
            'carrier', 'pickup_address', 'contact_info',
            'earliest_pickup', 'latest_pickup'
        ]
        
        for field in required_fields:
            if field not in request:
                raise ValidationError(f"Missing required field: {field}")
        
        if request['carrier'] not in ['fedex', 'ups']:
            raise ValidationError(f"Invalid carrier: {request['carrier']}")
        
        ShippingValidator.validate_address(request['pickup_address'])
        
        # Validate contact info
        if not request['contact_info'].get('name'):
            raise ValidationError("Contact name is required")
        if not request['contact_info'].get('phone'):
            raise ValidationError("Contact phone is required")
        
        # Validate pickup times
        try:
            earliest = request['earliest_pickup']
            latest = request['latest_pickup']
            
            if earliest >= latest:
                raise ValidationError("Earliest pickup time must be before latest pickup time")
        except (TypeError, ValueError):
            raise ValidationError("Invalid pickup time format")
