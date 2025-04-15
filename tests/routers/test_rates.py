"""Tests for rates router."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_calculate_rates_success(client):
    """Test successful rate calculation."""
    response = client.post(
        "/rates/calculate",
        json={
            "origin_zip": "38115",
            "destination_zip": "90210",
            "weight": 10.5,
            "length": 12.0,
            "width": 8.0,
            "height": 6.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(
        isinstance(rate["cost"], (int, float)) 
        for rate in data
    )

def test_calculate_rates_validation(client):
    """Test input validation."""
    response = client.post(
        "/rates/calculate",
        json={
            "origin_zip": "38115",
            "destination_zip": "90210",
            "weight": -1,  # Invalid weight
            "length": 12.0,
            "width": 8.0,
            "height": 6.0
        }
    )
    assert response.status_code == 422

def test_calculate_rates_with_service_code(client):
    """Test rate calculation with specific service code."""
    response = client.post(
        "/rates/calculate",
        json={
            "origin_zip": "38115",
            "destination_zip": "90210",
            "weight": 10.5,
            "length": 12.0,
            "width": 8.0,
            "height": 6.0,
            "service_code": "FEDEX_GROUND"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(
        rate["service_code"] == "FEDEX_GROUND"
        for rate in data
    )

def test_calculate_rates_with_insurance(client):
    """Test rate calculation with insurance."""
    response = client.post(
        "/rates/calculate",
        json={
            "origin_zip": "38115",
            "destination_zip": "90210",
            "weight": 10.5,
            "length": 12.0,
            "width": 8.0,
            "height": 6.0,
            "insurance_amount": 100.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    # Insurance should increase the cost
    assert all(
        rate["cost"] > 0
        for rate in data
    ) 