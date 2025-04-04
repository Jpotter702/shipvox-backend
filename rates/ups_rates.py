# Ups Rates
# TODO: Implement this module

import aiohttp
from typing import Dict, List, Optional
from dataclasses import dataclass
from auth.ups_auth import UPSAuth

@dataclass
class UPSRateRequest:
    """Represents a UPS rate request."""
    origin_zip: str
    destination_zip: str
    weight: float  # in pounds
    length: float  # in inches
    width: float   # in inches
    height: float  # in inches

@dataclass
class UPSRateResponse:
    """Represents a UPS rate response."""
    service_name: str
    service_code: str
    cost: float
    estimated_days: int
    delivery_date: str

class UPSRates:
    """Handles rate requests to the UPS API."""
    
    def __init__(self, auth: UPSAuth, environment: str = "production"):
        """
        Initialize the UPS rates handler.
        
        Args:
            auth (UPSAuth): UPS authentication handler
            environment (str): 'production' or 'sandbox'
        """
        self.auth = auth
        self._base_url = (
            "https://onlinetools.ups.com" if environment == "production"
            else "https://wwwcie.ups.com"
        )
    
    async def get_rates(self, request: UPSRateRequest) -> List[UPSRateResponse]:
        """
        Get shipping rates from UPS.
        
        Args:
            request (UPSRateRequest): The rate request details
            
        Returns:
            List[UPSRateResponse]: List of available shipping options
            
        Raises:
            Exception: If the API request fails
        """
        url = f"{self._base_url}/api/rating/v1/Shop"
        headers = await self.auth.get_auth_headers()
        
        payload = {
            "RateRequest": {
                "Request": {
                    "SubVersion": "1707",
                    "RequestOption": "Shop",
                    "TransactionReference": {
                        "CustomerContext": "Rate Request"
                    }
                },
                "PickupType": {
                    "Code": "01"  # Daily Pickup
                },
                "CustomerClassification": {
                    "Code": "01"  # Standard
                },
                "Shipment": {
                    "Shipper": {
                        "Address": {
                            "PostalCode": request.origin_zip,
                            "CountryCode": "US"
                        }
                    },
                    "ShipTo": {
                        "Address": {
                            "PostalCode": request.destination_zip,
                            "CountryCode": "US"
                        }
                    },
                    "Package": {
                        "PackagingType": {
                            "Code": "02"  # Package
                        },
                        "Dimensions": {
                            "UnitOfMeasurement": {
                                "Code": "IN"
                            },
                            "Length": str(request.length),
                            "Width": str(request.width),
                            "Height": str(request.height)
                        },
                        "PackageWeight": {
                            "UnitOfMeasurement": {
                                "Code": "LBS"
                            },
                            "Weight": str(request.weight)
                        }
                    }
                }
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"UPS API error: {error_text}")
                        
                    data = await response.json()
                    return self._parse_response(data)
        except Exception as e:
            raise Exception(f"Failed to get UPS rates: {str(e)}")
    
    def _parse_response(self, data: Dict) -> List[UPSRateResponse]:
        """
        Parse the UPS API response into rate options.
        
        Args:
            data (Dict): The API response data
            
        Returns:
            List[UPSRateResponse]: List of parsed rate options
        """
        rate_options = []
        
        for service in data.get("RateResponse", {}).get("RatedShipment", []):
            service_name = service.get("Service", {}).get("Description", "")
            service_code = service.get("Service", {}).get("Code", "")
            
            # Get the total cost
            total_cost = float(service.get("TotalCharges", {}).get("MonetaryValue", 0))
            
            # Get estimated transit time
            transit_time = service.get("GuaranteedDelivery", {}).get("BusinessDaysInTransit", "")
            estimated_days = self._parse_transit_time(transit_time)
            
            # Get delivery date
            delivery_date = service.get("GuaranteedDelivery", {}).get("DeliveryByTime", "")
            
            rate_options.append(UPSRateResponse(
                service_name=service_name,
                service_code=service_code,
                cost=total_cost,
                estimated_days=estimated_days,
                delivery_date=delivery_date
            ))
        
        return rate_options
    
    def _parse_transit_time(self, transit_time: str) -> int:
        """
        Parse UPS transit time string into days.
        
        Args:
            transit_time (str): UPS transit time string
            
        Returns:
            int: Estimated days for delivery
        """
        try:
            return int(transit_time)
        except (ValueError, TypeError):
            return 5  # Default to 5 days if unknown
