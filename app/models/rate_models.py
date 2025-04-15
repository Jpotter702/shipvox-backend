"""Rate models for ShipVox API."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class RateRequestModel(BaseModel):
    """API rate request model."""
    origin_zip: str = Field(..., description="Origin ZIP code")
    destination_zip: str = Field(..., description="Destination ZIP code")
    weight: float = Field(..., gt=0, description="Package weight in pounds")
    length: float = Field(..., gt=0, description="Package length in inches")
    width: float = Field(..., gt=0, description="Package width in inches")
    height: float = Field(..., gt=0, description="Package height in inches")
    service_code: Optional[str] = Field(None, description="Specific service code if desired")
    is_residential: bool = Field(True, description="Whether delivery is to residential address")
    insurance_amount: Optional[float] = Field(None, description="Insurance amount if needed")

class RateResponseModel(BaseModel):
    """API rate response model."""
    carrier: str = Field(..., description="Carrier name (e.g., FedEx)")
    service: str = Field(..., description="Service name (e.g., Ground)")
    cost: float = Field(..., description="Shipping cost")
    delivery_days: Optional[int] = Field(None, description="Estimated delivery days")
    service_code: str = Field(..., description="Carrier's service code")