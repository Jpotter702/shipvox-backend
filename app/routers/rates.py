"""Rates router for ShipVox API."""

from fastapi import APIRouter, HTTPException
from typing import List
from app.models.rate_models import RateRequestModel, RateResponseModel
from app.services.rate_service import RateService

router = APIRouter(prefix="/rates", tags=["rates"])

@router.post("/calculate", response_model=List[RateResponseModel])
async def calculate_rates(request: RateRequestModel):
    """Calculate shipping rates endpoint."""
    try:
        service = RateService()
        return await service.get_rates(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 