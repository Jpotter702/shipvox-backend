import pytest
import os
from auth_manager.config import settings

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