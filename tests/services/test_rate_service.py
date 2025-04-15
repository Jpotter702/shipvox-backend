"""Tests for rate service."""

import pytest
from app.models.rate_models import RateRequestModel
from app.services.rate_service import RateService

@pytest.fixture
def rate_service():
    return RateService()

@pytest.fixture
def valid_rate_request():
    return RateRequestModel(
        origin_zip="38115",
        destination_zip="90210",
        weight=10.5,
        length=12.0,
        width=8.0,
        height=6.0
    )

@pytest.mark.asyncio
async def test_get_rates_success(rate_service, valid_rate_request):
    """Test successful rate calculation."""
    rates = await rate_service.get_rates(valid_rate_request)
    assert isinstance(rates, list)
    assert len(rates) > 0
    assert all(
        hasattr(rate, "carrier_name") and
        hasattr(rate, "service_name") and
        hasattr(rate, "cost") and
        hasattr(rate, "estimated_delivery_days") and
        hasattr(rate, "service_code")
        for rate in rates
    )

@pytest.mark.asyncio
async def test_get_rates_with_service_code(rate_service, valid_rate_request):
    """Test rate calculation with specific service code."""
    valid_rate_request.service_code = "FEDEX_GROUND"
    rates = await rate_service.get_rates(valid_rate_request)
    assert len(rates) > 0
    assert all(
        rate.service_code == "FEDEX_GROUND"
        for rate in rates
    )

@pytest.mark.asyncio
async def test_get_rates_with_insurance(rate_service, valid_rate_request):
    """Test rate calculation with insurance."""
    valid_rate_request.insurance_amount = 100.0
    rates = await rate_service.get_rates(valid_rate_request)
    assert len(rates) > 0
    # Insurance should increase the cost
    assert all(
        rate.cost > 0
        for rate in rates
    )

@pytest.mark.asyncio
async def test_get_rates_with_residential(rate_service, valid_rate_request):
    """Test rate calculation for residential delivery."""
    valid_rate_request.is_residential = True
    rates = await rate_service.get_rates(valid_rate_request)
    assert len(rates) > 0
    # Residential delivery should have different rates
    assert all(
        rate.cost > 0
        for rate in rates
    )

@pytest.mark.asyncio
async def test_get_rates_invalid_zip(rate_service):
    """Test rate calculation with invalid ZIP code."""
    invalid_request = RateRequestModel(
        origin_zip="00000",  # Invalid ZIP
        destination_zip="90210",
        weight=10.5,
        length=12.0,
        width=8.0,
        height=6.0
    )
    rates = await rate_service.get_rates(invalid_request)
    assert len(rates) == 0  # Should return empty list for invalid ZIP 