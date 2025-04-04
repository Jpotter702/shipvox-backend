# Fedex Rates
# TODO: Implement this module

import aiohttp
from typing import Dict, List, Optional
from dataclasses import dataclass
from auth.fedex_auth import FedExAuth

@dataclass
class FedExRateRequest:
    """Represents a FedEx rate request."""
    origin_zip: str
    destination_zip: str
    weight: float  # in pounds
    length: float  # in inches
    width: float   # in inches
    height: float  # in inches

@dataclass
class FedExRateResponse:
    """Represents a FedEx rate response."""
    service_name: str
    service_code: str
    cost: float
    estimated_days: int
    delivery_date: str

class FedExRates:
    """Handles rate requests to the FedEx API."""
    
    def __init__(self, auth: FedExAuth, environment: str = "production"):
        """
        Initialize the FedEx rates handler.
        
        Args:
            auth (FedExAuth): FedEx authentication handler
            environment (str): 'production' or 'sandbox'
        """
        self.auth = auth
        self._base_url = (
            "https://apis.fedex.com" if environment == "production"
            else "https://apis-sandbox.fedex.com"
        )
    
    async def get_rates(self, request: FedExRateRequest) -> List[FedExRateResponse]:
        """
        Get shipping rates from FedEx.
        
        Args:
            request (FedExRateRequest): The rate request details
            
        Returns:
            List[FedExRateResponse]: List of available shipping options
            
        Raises:
            Exception: If the API request fails
        """
        url = f"{self._base_url}/rate/v1/rates/quotes"
        headers = await self.auth.get_auth_headers()
        
        payload = {
            "accountNumber": {
                "value": "your_account_number"  # TODO: Get from config
            },
            "requestedShipment": {
                "shipper": {
                    "address": {
                        "postalCode": request.origin_zip,
                        "countryCode": "US"
                    }
                },
                "recipient": {
                    "address": {
                        "postalCode": request.destination_zip,
                        "countryCode": "US"
                    }
                },
                "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
                "rateRequestType": ["LIST"],
                "requestedPackageLineItems": [{
                    "weight": {
                        "value": request.weight,
                        "units": "LB"
                    },
                    "dimensions": {
                        "length": request.length,
                        "width": request.width,
                        "height": request.height,
                        "units": "IN"
                    }
                }]
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"FedEx API error: {error_text}")
                        
                    data = await response.json()
                    return self._parse_response(data)
        except Exception as e:
            raise Exception(f"Failed to get FedEx rates: {str(e)}")
    
    def _parse_response(self, data: Dict) -> List[FedExRateResponse]:
        """
        Parse the FedEx API response into rate options.
        
        Args:
            data (Dict): The API response data
            
        Returns:
            List[FedExRateResponse]: List of parsed rate options
        """
        rate_options = []
        
        for quote in data.get("output", {}).get("rateReplyDetails", []):
            service_name = quote.get("serviceName", "")
            service_code = quote.get("serviceType", "")
            
            # Get the total cost
            total_cost = 0.0
            for charge in quote.get("ratedShipmentDetails", [{}])[0].get("shipmentRateDetail", {}).get("totalNetCharge", {}):
                if charge.get("name") == "Total":
                    total_cost = float(charge.get("amount", 0))
                    break
            
            # Get estimated transit time
            transit_time = quote.get("transitTime", "")
            estimated_days = self._parse_transit_time(transit_time)
            
            # Get delivery date
            delivery_date = quote.get("deliveryDate", "")
            
            rate_options.append(FedExRateResponse(
                service_name=service_name,
                service_code=service_code,
                cost=total_cost,
                estimated_days=estimated_days,
                delivery_date=delivery_date
            ))
        
        return rate_options
    
    def _parse_transit_time(self, transit_time: str) -> int:
        """
        Parse FedEx transit time string into days.
        
        Args:
            transit_time (str): FedEx transit time string
            
        Returns:
            int: Estimated days for delivery
        """
        # Map FedEx transit times to estimated days
        transit_map = {
            "SAME_DAY": 0,
            "ONE_DAY": 1,
            "TWO_DAYS": 2,
            "THREE_DAYS": 3,
            "FOUR_DAYS": 4,
            "FIVE_DAYS": 5,
            "SIX_DAYS": 6,
            "SEVEN_DAYS": 7,
            "EIGHT_DAYS": 8,
            "NINE_DAYS": 9,
            "TEN_DAYS": 10
        }
        
        return transit_map.get(transit_time, 5)  # Default to 5 days if unknown
