"""Rate service for ShipVox API."""

import logging
from typing import List
from app.models.rate_models import RateRequestModel, RateResponseModel
from rates.fedex_rates import FedExRateCalculator
from rates.ups_rates import UPSRateCalculator

logger = logging.getLogger(__name__)

class RateService:
    """Service for calculating shipping rates."""
    
    def __init__(self):
        self.fedex_calculator = FedExRateCalculator()
        self.ups_calculator = UPSRateCalculator()
    
    async def get_rates(self, request: RateRequestModel) -> List[RateResponseModel]:
        """Get rates from all carriers."""
        results = []
        
        # Get FedEx rates
        try:
            fedex_rates = await self.fedex_calculator.calculate_rates(request)
            results.extend(fedex_rates)
        except Exception as e:
            logger.error(f"FedEx rate calculation failed: {str(e)}")
        
        # Get UPS rates (when implemented)
        try:
            ups_rates = await self.ups_calculator.calculate_rates(request)
            results.extend(ups_rates)
        except Exception as e:
            logger.error(f"UPS rate calculation failed: {str(e)}")
        
        # Sort by cost
        return sorted(results, key=lambda x: x.cost) 