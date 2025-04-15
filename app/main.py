"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import rates

app = FastAPI(
    title="ShipVox API",
    description="""
    ShipVox Shipping Rate API
    
    Calculate shipping rates from multiple carriers:
    * FedEx
    * UPS (coming soon)
    
    Features:
    * Multi-carrier rate comparison
    * Service-specific rate lookup
    * Residential/Commercial rates
    * Insurance cost calculation
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(rates.router) 