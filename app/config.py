import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    
    # API Timeouts
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 30))
    
    # Carrier API Credentials
    FEDEX_CLIENT_ID = os.environ.get('FEDEX_CLIENT_ID')
    FEDEX_CLIENT_SECRET = os.environ.get('FEDEX_CLIENT_SECRET')
    UPS_CLIENT_ID = os.environ.get('UPS_CLIENT_ID')
    UPS_CLIENT_SECRET = os.environ.get('UPS_CLIENT_SECRET')
    
    # Cache Configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    TOKEN_CACHE_TIMEOUT = int(timedelta(hours=1).total_seconds())
    
    # Rate Comparison Settings
    RATE_CACHE_TIMEOUT = int(timedelta(minutes=30).total_seconds())
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
