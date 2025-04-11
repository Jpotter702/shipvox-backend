from pydantic import BaseModel, validator
from typing import Optional
from decimal import Decimal

class Dimensions(BaseModel):
    """Represents package dimensions in inches."""
    length: Decimal
    width: Decimal
    height: Decimal
    
    @validator('*')
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError("Dimensions must be positive")
        return v

class RateRequest(BaseModel):
    """Represents a shipping rate request."""
    origin_zip: str
    destination_zip: str
    weight: Decimal
    dimensions: Dimensions
    pickup_requested: bool = False
    
    @validator('weight')
    def validate_weight(cls, v):
        if v <= 0:
            raise ValueError("Weight must be positive")
        return v
    
    @validator('origin_zip', 'destination_zip')
    def validate_zip(cls, v):
        if not v.isdigit() or len(v) != 5:
            raise ValueError("Invalid ZIP code format")
        return v

class RateResponse(BaseModel):
    """Represents a shipping rate response from a carrier."""
    carrier: str
    service_name: str
    service_code: str
    cost: Decimal
    estimated_days: int
    delivery_date: Optional[str] = None 