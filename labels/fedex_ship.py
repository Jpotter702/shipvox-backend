import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional
import base64
from auth import auth_manager
from utils.exceptions import LabelError
from labels.label_creator import LabelCreator, LabelRequest, LabelResponse, Address, Package

class FedExLabelCreator(LabelCreator):
    """FedEx implementation of label creation using REST APIs."""
    
    def __init__(self, environment: str = "production"):
        """
        Initialize FedEx label creator.
        
        Args:
            environment (str): 'production' or 'sandbox'
        """
        self._base_url = (
            "https://apis.fedex.com" if environment == "production"
            else "https://apis-sandbox.fedex.com"
        )
    
    async def create_label(self, request: LabelRequest) -> LabelResponse:
        """Create a FedEx shipping label."""
        auth = await auth_manager.get_fedex_auth()
        headers = await auth.get_auth_headers()
        
        url = f"{self._base_url}/ship/v1/shipments"
        
        # Build FedEx REST API payload
        payload = {
            "labelResponseOptions": "URL_ONLY",
            "requestedShipment": {
                "shipper": self._format_address(request.from_address),
                "recipients": [self._format_address(request.to_address)],
                "serviceType": request.service_code,
                "emailNotificationDetail": {
                    "recipients": []
                },
                "labelSpecification": {
                    "imageType": "PDF",
                    "labelStockType": "PAPER_85X11_TOP_HALF_LABEL"
                },
                "rateRequestTypes": ["ACCOUNT"],
                "pickupType": "USE_SCHEDULED_PICKUP",
                "packagingType": request.package.packaging_type,
                "totalWeight": request.package.weight,
                "requestedPackageLineItems": [{
                    "weight": {
                        "value": request.package.weight,
                        "units": "LB"
                    },
                    "dimensions": {
                        "length": request.package.length,
                        "width": request.package.width,
                        "height": request.package.height,
                        "units": "IN"
                    }
                }]
            }
        }
        
        # Add email notifications if available
        if request.from_address.email:
            payload["requestedShipment"]["emailNotificationDetail"]["recipients"].append({
                "emailAddress": request.from_address.email,
                "notificationTypes": ["SHIP"]
            })
        if request.to_address.email:
            payload["requestedShipment"]["emailNotificationDetail"]["recipients"].append({
                "emailAddress": request.to_address.email,
                "notificationTypes": ["DELIVERY"]
            })
        
        # Add optional services
        if request.insurance_amount:
            payload["requestedShipment"]["totalInsuredValue"] = {
                "amount": request.insurance_amount,
                "currency": "USD"
            }
        
        if request.signature_required:
            payload["requestedShipment"]["specialServicesRequested"] = {
                "specialServiceTypes": ["SIGNATURE_OPTION"],
                "signatureOptionDetail": {
                    "signatureOptionType": "DIRECT"
                }
            }
        
        if request.saturday_delivery:
            if "specialServicesRequested" not in payload["requestedShipment"]:
                payload["requestedShipment"]["specialServicesRequested"] = {
                    "specialServiceTypes": []
                }
            payload["requestedShipment"]["specialServicesRequested"]["specialServiceTypes"].append("SATURDAY_DELIVERY")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise LabelError(f"FedEx label creation failed: {error_text}")
                    
                    data = await response.json()
                    return self._parse_response(data)
        except Exception as e:
            raise LabelError(f"Failed to create FedEx label: {str(e)}")
    
    async def void_label(self, tracking_number: str) -> bool:
        """Void a FedEx shipping label."""
        auth = await auth_manager.get_fedex_auth()
        headers = await auth.get_auth_headers()
        
        url = f"{self._base_url}/ship/v1/shipments/cancel"
        payload = {
            "trackingNumber": tracking_number,
            "deletionControl": "DELETE_ALL_PACKAGES"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        return True
                    return False
        except Exception as e:
            raise LabelError(f"Failed to void FedEx label: {str(e)}")
    
    async def get_label_status(self, tracking_number: str) -> Dict[str, Any]:
        """Get FedEx label status."""
        auth = await auth_manager.get_fedex_auth()
        headers = await auth.get_auth_headers()
        
        url = f"{self._base_url}/track/v1/trackingnumbers"
        payload = {
            "includeDetailedScans": True,
            "trackingInfo": [{
                "trackingNumberInfo": {
                    "trackingNumber": tracking_number
                }
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        raise LabelError("Failed to get label status")
                    return await response.json()
        except Exception as e:
            raise LabelError(f"Failed to get FedEx label status: {str(e)}")
    
    def _format_address(self, address: Address) -> Dict[str, Any]:
        """Format address for FedEx REST API."""
        formatted = {
            "contact": {
                "personName": address.name,
                "phoneNumber": address.phone
            },
            "address": {
                "streetLines": [address.street1] + ([address.street2] if address.street2 else []),
                "city": address.city,
                "stateOrProvinceCode": address.state,
                "postalCode": address.zip_code,
                "countryCode": address.country,
                "residential": True
            }
        }
        
        if address.company:
            formatted["contact"]["companyName"] = address.company
            
        if address.email:
            formatted["contact"]["emailAddress"] = address.email
            
        return formatted
    
    def _parse_response(self, data: Dict[str, Any]) -> LabelResponse:
        """Parse FedEx REST API response into LabelResponse."""
        output = data["output"]
        shipment = output["transactionShipments"][0]
        
        return LabelResponse(
            tracking_number=shipment["masterTrackingNumber"],
            label_data=base64.b64decode(shipment["pieceResponses"][0]["packageDocuments"][0]["url"]),
            label_format="PDF",
            carrier="FedEx",
            service=shipment["serviceType"],
            cost=float(shipment["completedShipmentDetail"]["shipmentRating"]["totalNetFedExCharge"]),
            created_at=datetime.now(),
            estimated_delivery=datetime.strptime(
                shipment["completedShipmentDetail"]["operationalDetail"]["deliveryDate"],
                "%Y-%m-%d"
            ) if "deliveryDate" in shipment["completedShipmentDetail"]["operationalDetail"] else None
        )
