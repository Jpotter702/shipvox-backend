import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from auth_manager.auth_manager import AuthManager
from auth_manager.carrier_registry import CarrierRegistry
from auth_manager.token_store import TokenStore
from auth_manager.exceptions import AuthenticationError, TokenNotFoundError

@pytest.fixture
def mock_carrier():
    """Create a mock carrier provider"""
    carrier = Mock()
    carrier.get_auth_url.return_value = "https://auth.example.com"
    carrier.exchange_token.return_value = {
        "access_token": "test_access",
        "refresh_token": "test_refresh",
        "expires_in": 3600
    }
    carrier.refresh_token.return_value = {
        "access_token": "new_access",
        "refresh_token": "new_refresh",
        "expires_in": 3600
    }
    return carrier

@pytest.fixture
def mock_token_store():
    """Create a mock token store"""
    store = Mock()
    store.get_tokens.return_value = {
        "access_token": "test_access",
        "refresh_token": "test_refresh",
        "expires_at": datetime.utcnow() + timedelta(hours=1)
    }
    store.get_refresh_token.return_value = "test_refresh"
    store.should_refresh.return_value = False
    return store

@pytest.fixture
def auth_manager(mock_carrier, mock_token_store):
    """Create an AuthManager instance with mocked dependencies"""
    registry = CarrierRegistry()
    registry.register("test", mock_carrier)
    return AuthManager(registry, mock_token_store)

def test_initiate_auth(auth_manager, mock_carrier):
    """Test initiating authentication"""
    url = auth_manager.initiate_auth("test", {"state": "test_state"})
    assert url == "https://auth.example.com"
    mock_carrier.get_auth_url.assert_called_once_with({"state": "test_state"})

def test_handle_callback(auth_manager, mock_carrier, mock_token_store):
    """Test handling OAuth callback"""
    tokens = auth_manager.handle_callback("test", {
        "code": "test_code",
        "user_id": "test_user"
    })
    
    assert tokens["access_token"] == "test_access"
    mock_carrier.exchange_token.assert_called_once_with({"code": "test_code"})
    mock_token_store.save_tokens.assert_called_once()

def test_get_valid_token(auth_manager, mock_token_store):
    """Test getting valid token"""
    tokens = auth_manager.get_valid_token("test_user", "test")
    assert tokens["access_token"] == "test_access"
    mock_token_store.get_tokens.assert_called_once_with("test_user", "test")

def test_get_valid_token_refresh(auth_manager, mock_carrier, mock_token_store):
    """Test token refresh when token is expired"""
    mock_token_store.should_refresh.return_value = True
    
    tokens = auth_manager.get_valid_token("test_user", "test")
    assert tokens["access_token"] == "new_access"
    mock_carrier.refresh_token.assert_called_once_with("test_refresh")
    mock_token_store.save_tokens.assert_called_once()

def test_handle_callback_no_token_store(auth_manager, mock_carrier):
    """Test handling callback without token store"""
    auth_manager.token_store = None
    tokens = auth_manager.handle_callback("test", {"code": "test_code"})
    assert tokens["access_token"] == "test_access"
    mock_carrier.exchange_token.assert_called_once_with({"code": "test_code"})

def test_get_valid_token_no_token_store(auth_manager):
    """Test getting valid token without token store"""
    auth_manager.token_store = None
    with pytest.raises(AuthenticationError):
        auth_manager.get_valid_token("test_user", "test")

def test_handle_callback_error(auth_manager, mock_carrier):
    """Test error handling in callback"""
    mock_carrier.exchange_token.side_effect = Exception("Test error")
    with pytest.raises(AuthenticationError):
        auth_manager.handle_callback("test", {"code": "test_code"})

def test_get_valid_token_error(auth_manager, mock_token_store):
    """Test error handling in get_valid_token"""
    mock_token_store.get_tokens.side_effect = TokenNotFoundError("Token not found")
    with pytest.raises(TokenNotFoundError):
        auth_manager.get_valid_token("test_user", "test") 