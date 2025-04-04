"""ShipVox application module."""
from fastapi import FastAPI
from app.config import Config

# Create FastAPI app instance
app = FastAPI(
    title="ShipVox API",
    description="Unified shipping API for FedEx and UPS",
    version="1.0.0"
)

# Import views to register routes
from app import main

# Export public interface
__all__ = ['app', 'Config']
