"""Shared test fixtures and configuration."""

import pytest
import os
from auth_manager.config import settings
from datetime import datetime
from labels.label_creator import Address, Package, LabelRequest
from unittest.mock import patch, AsyncMock

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment"""
    # Override settings for testing
    settings.database_url = "sqlite:///:memory:"
    settings.token_encryption_key = "test_encryption_key"
    settings.enable_metrics = False
    
    # Set test environment variables
    os.environ["AUTH_FEDEX_ENABLED"] = "true"
    os.environ["AUTH_FEDEX_CLIENT_ID"] = "test_fedex_id"
    os.environ["AUTH_FEDEX_CLIENT_SECRET"] = "test_fedex_secret"
    os.environ["AUTH_FEDEX_SANDBOX"] = "true"
    
    os.environ["AUTH_UPS_ENABLED"] = "true"
    os.environ["AUTH_UPS_CLIENT_ID"] = "test_ups_id"
    os.environ["AUTH_UPS_CLIENT_SECRET"] = "test_ups_secret"
    os.environ["AUTH_UPS_REDIRECT_URI"] = "http://localhost/callback"
    os.environ["AUTH_UPS_SANDBOX"] = "true"
    
    yield
    
    # Cleanup
    for key in list(os.environ.keys()):
        if key.startswith("AUTH_"):
            del os.environ[key] 

@pytest.fixture
def valid_address():
    """Create a valid shipping address."""
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
    """Create a valid package."""
    return Package(
        weight=10.5,
        length=12.0,
        width=8.0,
        height=6.0,
        packaging_type="YOUR_PACKAGING"
    )

@pytest.fixture
def valid_label_request(valid_address, valid_package):
    """Create a valid label request."""
    return LabelRequest(
        from_address=valid_address,
        to_address=valid_address,
        package=valid_package,
        service_code="FEDEX_GROUND"
    )

@pytest.fixture
def mock_fedex_auth():
    """Mock FedEx authentication."""
    with patch("auth.auth_manager.get_fedex_auth") as mock:
        mock_auth = AsyncMock()
        mock_auth.get_auth_headers.return_value = {"Authorization": "Bearer test_token"}
        mock.return_value = mock_auth
        yield mock

@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp session."""
    with patch("aiohttp.ClientSession") as mock:
        mock_session = AsyncMock()
        mock.return_value.__aenter__.return_value = mock_session
        yield mock_session 