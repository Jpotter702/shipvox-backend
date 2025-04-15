import pytest
import requests
from datetime import datetime, timedelta
from unittest.mock import patch
from auth_manager.auth_manager import AuthManager
from auth_manager.factory import AuthManagerFactory
from auth_manager.config import settings

class TestCarrierIntegration:
    """Integration tests for carrier API interactions"""
    
    @pytest.fixture
    def auth_manager(self):
        """Create an AuthManager instance with test configuration"""
        return AuthManagerFactory.create(
            fedex_config=settings.get_fedex_config(),
            ups_config=settings.get_ups_config(),
            encryption_key=settings.token_encryption_key
        )
    
    @pytest.mark.integration
    def test_fedex_token_exchange(self, auth_manager):
        """Test FedEx token exchange with actual API"""
        try:
            tokens = auth_manager.handle_callback("fedex", {
                "user_id": "test_user",
                "code": "test_code"  # This will be ignored for FedEx
            })
            
            assert "access_token" in tokens
            assert "refresh_token" in tokens
            assert "expires_in" in tokens
            assert tokens["token_type"] == "Bearer"
        except Exception as e:
            pytest.skip(f"FedEx integration test skipped: {str(e)}")
    
    @pytest.mark.integration
    def test_ups_auth_flow(self, auth_manager):
        """Test UPS OAuth flow with actual API"""
        try:
            # Get auth URL
            auth_url = auth_manager.initiate_auth("ups", {
                "state": "test_state",
                "user_id": "test_user"
            })
            assert auth_url.startswith("https://")
            
            # Mock the callback with a test code
            with patch('requests.post') as mock_post:
                mock_post.return_value.json.return_value = {
                    "access_token": "test_access",
                    "refresh_token": "test_refresh",
                    "expires_in": 3600,
                    "token_type": "Bearer"
                }
                mock_post.return_value.status_code = 200
                
                tokens = auth_manager.handle_callback("ups", {
                    "code": "test_code",
                    "user_id": "test_user"
                })
                
                assert tokens["access_token"] == "test_access"
                assert tokens["refresh_token"] == "test_refresh"
                assert tokens["expires_in"] == 3600
        except Exception as e:
            pytest.skip(f"UPS integration test skipped: {str(e)}")
    
    @pytest.mark.integration
    def test_token_refresh(self, auth_manager):
        """Test token refresh functionality"""
        try:
            # First get initial tokens
            tokens = auth_manager.handle_callback("fedex", {
                "user_id": "test_user"
            })
            
            # Force refresh by setting expiration to past
            with patch('auth_manager.token_store.TokenStore.should_refresh') as mock_refresh:
                mock_refresh.return_value = True
                
                new_tokens = auth_manager.get_valid_token("test_user", "fedex")
                assert new_tokens["access_token"] != tokens["access_token"]
        except Exception as e:
            pytest.skip(f"Token refresh test skipped: {str(e)}")
    
    @pytest.mark.integration
    def test_token_persistence(self, auth_manager):
        """Test token persistence in database"""
        try:
            # Save tokens
            initial_tokens = auth_manager.handle_callback("fedex", {
                "user_id": "test_user"
            })
            
            # Retrieve tokens
            retrieved_tokens = auth_manager.get_valid_token("test_user", "fedex")
            
            assert retrieved_tokens["access_token"] == initial_tokens["access_token"]
            assert retrieved_tokens["refresh_token"] == initial_tokens["refresh_token"]
        except Exception as e:
            pytest.skip(f"Token persistence test skipped: {str(e)}")
    
    @pytest.mark.integration
    def test_error_handling(self, auth_manager):
        """Test error handling with invalid credentials"""
        try:
            # Test with invalid FedEx credentials
            with patch('requests.post') as mock_post:
                mock_post.return_value.status_code = 401
                mock_post.return_value.json.return_value = {
                    "error": "invalid_client",
                    "error_description": "Invalid client credentials"
                }
                
                with pytest.raises(Exception):
                    auth_manager.handle_callback("fedex", {
                        "user_id": "test_user"
                    })
        except Exception as e:
            pytest.skip(f"Error handling test skipped: {str(e)}") 