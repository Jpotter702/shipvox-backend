"""FedEx label creation implementation."""

import aiohttp
import base64
import qrcode
from datetime import datetime
from io import BytesIO
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential

from auth import auth_manager
from utils.exceptions import (
    LabelError, ValidationError, FedExAPIError,
    PackageError, AddressError, ServiceError
)
from labels.label_creator import LabelCreator, LabelRequest, LabelResponse, Address, Package
from labels.fedex_constants import (
    FEDEX_SERVICE_CODES, FEDEX_PACKAGE_TYPES,
    FEDEX_API_ENDPOINTS, FEDEX_API_PATHS,
    MIN_PACKAGE_WEIGHT, MAX_PACKAGE_WEIGHT,
    MIN_PACKAGE_DIMENSION, MAX_PACKAGE_DIMENSION,
    LABEL_FORMATS, LABEL_STOCK_TYPES
)

class FedExLabelCreator(LabelCreator):
    """FedEx implementation of label creation using REST APIs."""
    
    def __init__(self, environment: str = "production"):
        """
        Initialize FedEx label creator.
        
        Args:
            environment (str): 'production' or 'sandbox'
        """
        if environment not in FEDEX_API_ENDPOINTS:
            raise ValueError(f"Invalid environment: {environment}. Must be one of {list(FEDEX_API_ENDPOINTS.keys())}")
        
        self._base_url = FEDEX_API_ENDPOINTS[environment]
        self._setup_retry_config()
    
    def _setup_retry_config(self):
        """Configure retry settings for API calls."""
        self._retry_config = {
            "stop": stop_after_attempt(3),
            "wait": wait_exponential(multiplier=1, min=4, max=10)
        }
    
    def _validate_request(self, request: LabelRequest) -> None:
        """Validate the label request before sending to FedEx."""
        errors: List[str] = []
        
        # Validate addresses
        self._validate_address(request.from_address, "shipper", errors)
        self._validate_address(request.to_address, "recipient", errors)
        
        # Validate package
        self._validate_package(request.package, errors)
        
        # Validate service code
        if request.service_code not in FEDEX_SERVICE_CODES:
            errors.append(f"Invalid service code: {request.service_code}. Must be one of: {', '.join(FEDEX_SERVICE_CODES.keys())}")
        
        if errors:
            raise ValidationError("\n".join(errors))
    
    def _validate_address(self, address: Address, role: str, errors: List[str]) -> None:
        """Validate an address."""
        if not address.zip_code.isalnum():
            errors.append(f"Invalid {role} ZIP code format: {address.zip_code}")
        if not address.phone.replace("+", "").replace("-", "").replace("(", "").replace(")", "").isdigit():
            errors.append(f"Invalid {role} phone number format: {address.phone}")
        if not address.country.isalpha() or len(address.country) != 2:
            errors.append(f"Invalid {role} country code: {address.country}")
    
    def _validate_package(self, package: Package, errors: List[str]) -> None:
        """Validate package details."""
        if not MIN_PACKAGE_WEIGHT <= package.weight <= MAX_PACKAGE_WEIGHT:
            errors.append(f"Package weight must be between {MIN_PACKAGE_WEIGHT} and {MAX_PACKAGE_WEIGHT} pounds")
        
        for dim_name, dim_value in [("length", package.length), 
                                  ("width", package.width), 
                                  ("height", package.height)]:
            if not MIN_PACKAGE_DIMENSION <= dim_value <= MAX_PACKAGE_DIMENSION:
                errors.append(f"Package {dim_name} must be between {MIN_PACKAGE_DIMENSION} and {MAX_PACKAGE_DIMENSION} inches")
        
        if package.packaging_type not in FEDEX_PACKAGE_TYPES:
            errors.append(f"Invalid packaging type: {package.packaging_type}. Must be one of: {', '.join(FEDEX_PACKAGE_TYPES.keys())}")
    
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
    
    def _generate_qr_code(self, tracking_number: str) -> bytes:
        """Generate QR code for tracking number."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"https://www.fedex.com/fedextrack/?trknbr={tracking_number}")
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    
    @retry(**{"stop": stop_after_attempt(3), "wait": wait_exponential(multiplier=1, min=4, max=10)})
    async def _make_api_request(self, session: aiohttp.ClientSession, 
                              method: str, url: str, 
                              headers: Dict[str, str], 
                              json: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with retry logic."""
        async with session.request(method, url, headers=headers, json=json) as response:
            if response.status != 200:
                error_text = await response.text()
                raise FedExAPIError(f"FedEx API request failed: {error_text}", 
                                  api_response={"status": response.status, "text": error_text})
            return await response.json()
    
    async def create_label(self, request: LabelRequest) -> LabelResponse:
        """Create a FedEx shipping label."""
        # Validate request
        self._validate_request(request)
        
        # Get authentication
        auth = await auth_manager.get_fedex_auth()
        headers = await auth.get_auth_headers()
        
        # Build API URL
        url = f"{self._base_url}{FEDEX_API_PATHS['ship']}"
        
        # Build payload
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
                    "imageType": LABEL_FORMATS["PDF"],
                    "labelStockType": LABEL_STOCK_TYPES["PAPER_85X11_TOP_HALF_LABEL"]
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
                data = await self._make_api_request(session, "POST", url, headers, payload)
                response = self._parse_response(data)
                
                # Generate QR code
                response.qr_code = self._generate_qr_code(response.tracking_number)
                
                return response
        except Exception as e:
            raise LabelError(f"Failed to create FedEx label: {str(e)}")
    
    async def void_label(self, tracking_number: str) -> bool:
        """Void a FedEx shipping label."""
        auth = await auth_manager.get_fedex_auth()
        headers = await auth.get_auth_headers()
        
        url = f"{self._base_url}{FEDEX_API_PATHS['cancel']}"
        payload = {
            "trackingNumber": tracking_number,
            "deletionControl": "DELETE_ALL_PACKAGES"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                data = await self._make_api_request(session, "PUT", url, headers, payload)
                return data.get("output", {}).get("cancelledShipment", False)
        except Exception as e:
            raise LabelError(f"Failed to void FedEx label: {str(e)}")
    
    async def get_label_status(self, tracking_number: str) -> Dict[str, Any]:
        """Get FedEx label status."""
        auth = await auth_manager.get_fedex_auth()
        headers = await auth.get_auth_headers()
        
        url = f"{self._base_url}{FEDEX_API_PATHS['track']}"
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
                data = await self._make_api_request(session, "POST", url, headers, payload)
                return data.get("output", {}).get("completeTrackResults", [{}])[0]
        except Exception as e:
            raise LabelError(f"Failed to get FedEx label status: {str(e)}")
    
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
