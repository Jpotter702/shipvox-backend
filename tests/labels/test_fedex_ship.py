"""Tests for FedEx label creation."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from labels.label_creator import Address, Package, LabelRequest
from labels.fedex_ship import FedExLabelCreator
from utils.exceptions import ValidationError, FedExAPIError

@pytest.fixture
def valid_address():
    return Address(
        name="John Doe",
        company="ACME Inc",
        street1="123 Test St",
        street2=None,
        city="Memphis",
        state="TN",
        zip_code="38115",
        country="US",
        phone="1234567890",
        email="test@example.com"
    )

@pytest.fixture
def valid_package():
    return Package(
        weight=10.5,
        length=12.0,
        width=8.0,
        height=6.0,
        packaging_type="YOUR_PACKAGING"
    )

@pytest.fixture
def valid_label_request(valid_address, valid_package):
    return LabelRequest(
        from_address=valid_address,
        to_address=valid_address,
        package=valid_package,
        service_code="FEDEX_GROUND"
    )

@pytest.fixture
def mock_fedex_auth():
    with patch("auth.auth_manager.get_fedex_auth") as mock:
        mock_auth = AsyncMock()
        mock_auth.get_auth_headers.return_value = {"Authorization": "Bearer test_token"}
        mock.return_value = mock_auth
        yield mock

@pytest.mark.asyncio
async def test_create_label_success(valid_label_request, mock_fedex_auth):
    """Test successful label creation."""
    creator = FedExLabelCreator(environment="sandbox")
    
    mock_response = {
        "output": {
            "transactionShipments": [{
                "masterTrackingNumber": "123456789012",
                "serviceType": "FEDEX_GROUND",
                "pieceResponses": [{
                    "packageDocuments": [{
                        "url": "base64_encoded_pdf"
                    }]
                }],
                "completedShipmentDetail": {
                    "shipmentRating": {
                        "totalNetFedExCharge": "25.99"
                    },
                    "operationalDetail": {
                        "deliveryDate": "2024-04-20"
                    }
                }
            }]
        }
    }
    
    with patch("aiohttp.ClientSession") as mock_session:
        mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value.status = 200
        mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        
        response = await creator.create_label(valid_label_request)
        
        assert response.tracking_number == "123456789012"
        assert response.service == "FEDEX_GROUND"
        assert response.cost == 25.99
        assert response.label_format == "PDF"
        assert response.carrier == "FedEx"
        assert response.qr_code is not None

@pytest.mark.asyncio
async def test_create_label_validation_error(valid_label_request):
    """Test label creation with invalid request."""
    creator = FedExLabelCreator()
    
    # Invalid package weight
    valid_label_request.package.weight = 0
    with pytest.raises(ValidationError):
        await creator.create_label(valid_label_request)
    
    # Invalid service code
    valid_label_request.package.weight = 10.5
    valid_label_request.service_code = "INVALID_SERVICE"
    with pytest.raises(ValidationError):
        await creator.create_label(valid_label_request)

@pytest.mark.asyncio
async def test_void_label_success(mock_fedex_auth):
    """Test successful label voiding."""
    creator = FedExLabelCreator()
    
    mock_response = {
        "output": {
            "cancelledShipment": True
        }
    }
    
    with patch("aiohttp.ClientSession") as mock_session:
        mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value.status = 200
        mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        
        result = await creator.void_label("123456789012")
        assert result is True

@pytest.mark.asyncio
async def test_get_label_status_success(mock_fedex_auth):
    """Test successful label status retrieval."""
    creator = FedExLabelCreator()
    
    mock_response = {
        "output": {
            "completeTrackResults": [{
                "trackingNumber": "123456789012",
                "trackResults": [{
                    "statusDetail": {
                        "code": "DL",
                        "description": "Delivered"
                    }
                }]
            }]
        }
    }
    
    with patch("aiohttp.ClientSession") as mock_session:
        mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value.status = 200
        mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        
        status = await creator.get_label_status("123456789012")
        assert status["trackingNumber"] == "123456789012"
        assert status["trackResults"][0]["statusDetail"]["code"] == "DL"

@pytest.mark.asyncio
async def test_api_error_handling(valid_label_request, mock_fedex_auth):
    """Test API error handling."""
    creator = FedExLabelCreator()
    
    with patch("aiohttp.ClientSession") as mock_session:
        mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value.status = 400
        mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value.text = AsyncMock(return_value="Invalid request")
        
        with pytest.raises(FedExAPIError):
            await creator.create_label(valid_label_request)

def test_invalid_environment():
    """Test invalid environment initialization."""
    with pytest.raises(ValueError):
        FedExLabelCreator(environment="invalid") 