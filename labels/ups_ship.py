# Ups Ship
# TODO: Implement this module

from typing import Dict, Any, Optional
from datetime import datetime
import base64
import aiohttp
from auth import auth_manager
from utils.exceptions import LabelError
from labels.label_creator import LabelCreator, LabelRequest, LabelResponse, Address, Package

class UPSLabelCreator(LabelCreator):
    """UPS implementation of the label creator using REST APIs."""
    
    def __init__(self, environment: str = "production"):
        """
        Initialize UPS label creator.
        
        Args:
            environment (str): 'production' or 'sandbox'
        """
        self._base_url = (
            "https://onlinetools.ups.com" if environment == "production"
            else "https://wwwcie.ups.com"
        )
    
    async def create_label(self, request: LabelRequest) -> LabelResponse:
        """Create a UPS shipping label."""
        auth = await auth_manager.get_ups_auth()
        headers = await auth.get_auth_headers()
        
        url = f"{self._base_url}/api/shipments/v1/ship"
        
        # Build UPS REST API payload
        payload = {
            "ShipmentRequest": {
                "Request": {
                    "RequestOption": "nonvalidate",
                    "TransactionReference": {
                        "CustomerContext": request.reference or ""
                    }
                },
                "Shipment": {
                    "Description": "Shipping Label",
                    "Shipper": self._format_address(request.from_address),
                    "ShipTo": self._format_address(request.to_address),
                    "ShipFrom": self._format_address(request.from_address),
                    "PaymentInformation": {
                        "ShipmentCharge": {
                            "Type": "01",
                            "BillShipper": {
                                "AccountNumber": auth.account_number
                            }
                        }
                    },
                    "Service": {
                        "Code": request.service_code,
                        "Description": ""
                    },
                    "Package": {
                        "Description": "",
                        "Packaging": {
                            "Code": request.package.packaging_type,
                            "Description": ""
                        },
                        "Dimensions": {
                            "UnitOfMeasurement": {
                                "Code": "IN",
                                "Description": "Inches"
                            },
                            "Length": str(request.package.length),
                            "Width": str(request.package.width),
                            "Height": str(request.package.height)
                        },
                        "PackageWeight": {
                            "UnitOfMeasurement": {
                                "Code": "LBS",
                                "Description": "Pounds"
                            },
                            "Weight": str(request.package.weight)
                        }
                    },
                    "ShipmentServiceOptions": {}
                },
                "LabelSpecification": {
                    "LabelImageFormat": {
                        "Code": "PDF",
                        "Description": "PDF"
                    },
                    "HTTPUserAgent": "Mozilla/4.5"
                }
            }
        }
        
        # Add optional services
        if request.insurance_amount:
            payload["ShipmentRequest"]["Shipment"]["Package"]["PackageServiceOptions"] = {
                "InsuredValue": {
                    "CurrencyCode": "USD",
                    "MonetaryValue": str(request.insurance_amount)
                }
            }
            
        if request.signature_required:
            if "PackageServiceOptions" not in payload["ShipmentRequest"]["Shipment"]["Package"]:
                payload["ShipmentRequest"]["Shipment"]["Package"]["PackageServiceOptions"] = {}
            payload["ShipmentRequest"]["Shipment"]["Package"]["PackageServiceOptions"]["DeliveryConfirmation"] = {
                "DCISType": "2"  # Signature Required
            }
            
        if request.saturday_delivery:
            payload["ShipmentRequest"]["Shipment"]["ShipmentServiceOptions"]["SaturdayDeliveryIndicator"] = ""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise LabelError(f"UPS label creation failed: {error_text}")
                    
                    data = await response.json()
                    return self._parse_response(data)
        except Exception as e:
            raise LabelError(f"Failed to create UPS label: {str(e)}")
    
    async def void_label(self, tracking_number: str) -> bool:
        """Void a UPS shipping label."""
        auth = await auth_manager.get_ups_auth()
        headers = await auth.get_auth_headers()
        
        url = f"{self._base_url}/api/shipments/v1/void/{tracking_number}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=headers) as response:
                    if response.status == 200:
                        return True
                    return False
        except Exception as e:
            raise LabelError(f"Failed to void UPS label: {str(e)}")
    
    async def get_label_status(self, tracking_number: str) -> Dict[str, Any]:
        """Get UPS label status."""
        auth = await auth_manager.get_ups_auth()
        headers = await auth.get_auth_headers()
        
        url = f"{self._base_url}/api/track/v1/details/{tracking_number}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        raise LabelError("Failed to get label status")
                    return await response.json()
        except Exception as e:
            raise LabelError(f"Failed to get UPS label status: {str(e)}")
    
    def _format_address(self, address: Address) -> Dict[str, Any]:
        """Format address for UPS REST API."""
        formatted = {
            "Name": address.name,
            "AttentionName": address.company or address.name,
            "Phone": {
                "Number": address.phone
            },
            "Address": {
                "AddressLine": [address.street1] + ([address.street2] if address.street2 else []),
                "City": address.city,
                "StateProvinceCode": address.state,
                "PostalCode": address.zip_code,
                "CountryCode": address.country
            }
        }
        
        if address.email:
            formatted["EMailAddress"] = address.email
            
        return formatted
    
    def _parse_response(self, data: Dict[str, Any]) -> LabelResponse:
        """Parse UPS REST API response into LabelResponse."""
        shipment = data["ShipmentResponse"]["ShipmentResults"]
        
        return LabelResponse(
            tracking_number=shipment["ShipmentIdentificationNumber"],
            label_data=base64.b64decode(shipment["PackageResults"]["ShippingLabel"]["GraphicImage"]),
            label_format="PDF",
            carrier="UPS",
            service=shipment["ServiceCode"],
            cost=float(shipment["ShipmentCharges"]["TotalCharges"]["MonetaryValue"]),
            created_at=datetime.now(),
            estimated_delivery=None  # Parse from response if available
        )
