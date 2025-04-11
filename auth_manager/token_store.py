from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from .database import get_db
from .models import TokenRecord
from .encryption import TokenEncryption
from .exceptions import (
    TokenNotFoundError, TokenStoreError, TokenExpiredError,
    TokenValidationError, TokenEncryptionError
)

class TokenStore:
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize TokenStore with optional encryption"""
        self.encryption = TokenEncryption(encryption_key) if encryption_key else None
        
    def _encrypt_token(self, token: str) -> str:
        """Encrypt token if encryption is enabled"""
        return self.encryption.encrypt(token) if self.encryption else token
        
    def _decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt token if encryption is enabled"""
        return self.encryption.decrypt(encrypted_token) if self.encryption else encrypted_token

    def _validate_tokens(self, tokens: Dict[str, Any]) -> None:
        """Validate token data structure"""
        required_fields = ['access_token', 'refresh_token', 'expires_in']
        for field in required_fields:
            if field not in tokens:
                raise TokenValidationError(f"Missing required field: {field}")

    def save_tokens(self, user_id: str, carrier: str, tokens: Dict[str, Any]) -> None:
        """
        Save or update tokens for a user and carrier
        
        Args:
            user_id: Unique identifier for the user
            carrier: Carrier identifier (e.g., 'fedex', 'ups')
            tokens: Dictionary containing token information
        """
        try:
            self._validate_tokens(tokens)
            
            with get_db() as db:
                # Calculate expiration
                expires_at = datetime.utcnow() + timedelta(seconds=tokens['expires_in'])
                
                # Create composite ID
                record_id = f"{user_id}:{carrier}"
                
                # Encrypt sensitive data if encryption is enabled
                access_token = self._encrypt_token(tokens['access_token'])
                refresh_token = self._encrypt_token(tokens['refresh_token'])
                
                # Create or update token record
                token_record = db.query(TokenRecord).filter_by(id=record_id).first()
                if token_record:
                    # Update existing record
                    token_record.access_token = access_token
                    token_record.refresh_token = refresh_token
                    token_record.expires_at = expires_at
                    token_record.token_type = tokens.get('token_type', 'Bearer')
                    token_record.scope = tokens.get('scope')
                    token_record.additional_data = tokens.get('additional_data')
                    token_record.updated_at = datetime.utcnow()
                else:
                    # Create new record
                    token_record = TokenRecord(
                        id=record_id,
                        user_id=user_id,
                        carrier=carrier,
                        access_token=access_token,
                        refresh_token=refresh_token,
                        expires_at=expires_at,
                        token_type=tokens.get('token_type', 'Bearer'),
                        scope=tokens.get('scope'),
                        additional_data=tokens.get('additional_data')
                    )
                    db.add(token_record)
                
                db.commit()
                
        except TokenValidationError:
            raise
        except Exception as e:
            raise TokenStoreError(f"Failed to save tokens: {str(e)}")

    def get_tokens(self, user_id: str, carrier: str) -> Dict[str, Any]:
        """
        Retrieve tokens for a user and carrier
        
        Returns:
            Dict containing token information
        """
        try:
            with get_db() as db:
                record_id = f"{user_id}:{carrier}"
                token_record = db.query(TokenRecord).filter_by(id=record_id).first()
                
                if not token_record:
                    raise TokenNotFoundError(f"No tokens found for user {user_id} and carrier {carrier}")
                
                if token_record.is_expired:
                    raise TokenExpiredError("Token has expired")
                
                return {
                    'access_token': self._decrypt_token(token_record.access_token),
                    'refresh_token': self._decrypt_token(token_record.refresh_token),
                    'expires_at': token_record.expires_at,
                    'is_expired': token_record.is_expired,
                    'token_type': token_record.token_type,
                    'scope': token_record.scope,
                    'additional_data': token_record.additional_data
                }
                
        except (TokenNotFoundError, TokenExpiredError):
            raise
        except Exception as e:
            raise TokenStoreError(f"Failed to retrieve tokens: {str(e)}")

    def delete_tokens(self, user_id: str, carrier: str) -> None:
        """Delete tokens for a user and carrier"""
        try:
            with get_db() as db:
                record_id = f"{user_id}:{carrier}"
                db.query(TokenRecord).filter_by(id=record_id).delete()
                db.commit()
        except Exception as e:
            raise TokenStoreError(f"Failed to delete tokens: {str(e)}")

    def get_refresh_token(self, user_id: str, carrier: str) -> str:
        """Get refresh token for a user and carrier"""
        try:
            with get_db() as db:
                record_id = f"{user_id}:{carrier}"
                token_record = db.query(TokenRecord).filter_by(id=record_id).first()
                
                if not token_record:
                    raise TokenNotFoundError(f"No tokens found for user {user_id} and carrier {carrier}")
                
                return self._decrypt_token(token_record.refresh_token)
                
        except TokenNotFoundError:
            raise
        except Exception as e:
            raise TokenStoreError(f"Failed to retrieve refresh token: {str(e)}")
