"""Main application routes and handlers."""
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import os

from app import app
from app.config import Config
from auth import auth_manager
from rates import RateComparer, ServiceNormalizer
from labels import get_label_manager, Address, Package, LabelRequest
from utils.log import logger
from utils.validators import ShippingValidator
from utils.exceptions import (
    ValidationError, AuthenticationError, APIError, 
    RateError, LabelError, ServiceMappingError
)

# Initialize configuration
config = Config()

# Set up logging
logger.setLevel(config.log_level)
if config.log_file:
    logger.add_file_handler(config.log_file)

# Initialize auth manager
auth_manager.initialize_with_config(config.fedex_config, config.ups_config)

# Initialize service normalizer
service_normalizer = ServiceNormalizer()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for label PDFs
os.makedirs("static/labels", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Request/Response Models
class AddressModel(BaseModel):
    """Address model."""
    name: str
    company: Optional[str] = None
    street1: str
    street2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    country: str = "US"
    phone: str
    email: Optional[str] = None

class DimensionsModel(BaseModel):
    """Package dimensions model."""
    length: float = Field(..., gt=0)
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)

class RateRequest(BaseModel):
    """Rate request model."""
    origin_zip: str
    destination_zip: str
    weight: float = Field(..., gt=0)
    dimensions: DimensionsModel
    pickup_requested: bool = False

class RateOption(BaseModel):
    """Rate option model."""
    carrier: str
    service: str
    normalized_service: str
    cost: float
    estimated_days: int

class RateResponse(BaseModel):
    """Rate response model."""
    cheapest_option: Optional[RateOption]
    cheapest_fastest_option: Optional[RateOption]
    all_options: List[RateOption]

class LabelGenerationRequest(BaseModel):
    """Label generation request model."""
    carrier: str
    service_code: str
    from_address: AddressModel
    to_address: AddressModel
    weight: float = Field(..., gt=0)
    dimensions: DimensionsModel
    packaging_type: str
    insurance_amount: Optional[float] = None
    signature_required: bool = False
    saturday_delivery: bool = False
    reference: Optional[str] = None

class LabelResponse(BaseModel):
    """Label response model."""
    tracking_number: str
    label_url: str
    cost: float
    carrier: str
    service: str
    estimated_delivery: Optional[str] = None

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/rates", response_model=RateResponse)
async def get_rates(request: RateRequest) -> RateResponse:
    """Get shipping rates from all carriers."""
    try:
        # Validate request
        ShippingValidator.validate_rate_request({
            "origin_zip": request.origin_zip,
            "destination_zip": request.destination_zip,
            "weight": request.weight,
            "dimensions": request.dimensions.dict()
        })
        
        # Create rate comparer
        rate_comparer = RateComparer(service_normalizer)
        
        # Get FedEx rates
        try:
            fedex_auth = await auth_manager.get_fedex_auth()
            fedex_rates = await fedex_auth.get_rates(
                request.origin_zip,
                request.destination_zip,
                request.weight,
                request.dimensions.dict()
            )
            for rate in fedex_rates:
                rate_comparer.add_rate_option("FedEx", rate)
        except Exception as e:
            logger.error(f"Failed to get FedEx rates: {str(e)}")
        
        # Get UPS rates
        try:
            ups_auth = await auth_manager.get_ups_auth()
            ups_rates = await ups_auth.get_rates(
                request.origin_zip,
                request.destination_zip,
                request.weight,
                request.dimensions.dict()
            )
            for rate in ups_rates:
                rate_comparer.add_rate_option("UPS", rate)
        except Exception as e:
            logger.error(f"Failed to get UPS rates: {str(e)}")
        
        # Get best options
        cheapest, fastest = rate_comparer.get_best_options()
        all_options = rate_comparer.get_all_options()
        
        if not all_options:
            raise APIError(
                carrier="SYSTEM",
                status_code=404,
                message="No rates available from any carrier"
            )
        
        return RateResponse(
            cheapest_option=cheapest,
            cheapest_fastest_option=fastest,
            all_options=all_options
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except APIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.exception("Error getting rates")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/labels", response_model=LabelResponse)
async def create_label(request: LabelGenerationRequest) -> LabelResponse:
    """Create a shipping label."""
    try:
        # Validate addresses
        ShippingValidator.validate_address(request.from_address.dict())
        ShippingValidator.validate_address(request.to_address.dict())
        
        # Create label request
        label_request = LabelRequest(
            from_address=Address(**request.from_address.dict()),
            to_address=Address(**request.to_address.dict()),
            package=Package(
                weight=request.weight,
                length=request.dimensions.length,
                width=request.dimensions.width,
                height=request.dimensions.height,
                packaging_type=request.packaging_type
            ),
            service_code=request.service_code,
            insurance_amount=request.insurance_amount,
            signature_required=request.signature_required,
            saturday_delivery=request.saturday_delivery,
            reference=request.reference
        )
        
        # Get label manager and create label
        label_manager = get_label_manager(auth_manager)
        response = await label_manager.create_label(request.carrier.lower(), label_request)
        
        # Save label PDF and return URL
        label_path = f"static/labels/{response.tracking_number}.pdf"
        with open(label_path, "wb") as f:
            f.write(response.label_data)
        
        return LabelResponse(
            tracking_number=response.tracking_number,
            label_url=f"/static/labels/{response.tracking_number}.pdf",
            cost=response.cost,
            carrier=response.carrier,
            service=response.service,
            estimated_delivery=response.estimated_delivery.isoformat() if response.estimated_delivery else None
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except LabelError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.exception("Error creating label")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/labels/{tracking_number}")
async def void_label(tracking_number: str, carrier: str) -> Dict[str, bool]:
    """Void a shipping label."""
    try:
        label_manager = get_label_manager(auth_manager)
        success = await label_manager.void_label(carrier.lower(), tracking_number)
        return {"success": success}
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except LabelError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.exception("Error voiding label")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/labels/{tracking_number}/status")
async def get_label_status(tracking_number: str, carrier: str) -> Dict[str, Any]:
    """Get shipping label status."""
    try:
        label_manager = get_label_manager(auth_manager)
        status = await label_manager.get_label_status(carrier.lower(), tracking_number)
        return status
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except LabelError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.exception("Error getting label status")
        raise HTTPException(status_code=500, detail=str(e))
