from cryptography.fernet import Fernet
import base64
from typing import Optional
import os

class TokenEncryption:
    def __init__(self, key: Optional[str] = None):
        """Initialize encryption with key or generate new one"""
        if key:
            # Ensure key is properly padded for Fernet
            key_bytes = key.encode()
            key_b64 = base64.b64encode(key_bytes.ljust(32)[:32])
            self.fernet = Fernet(key_b64)
        else:
            # Try to get key from environment
            env_key = os.getenv('TOKEN_ENCRYPTION_KEY')
            if env_key:
                key_bytes = env_key.encode()
                key_b64 = base64.b64encode(key_bytes.ljust(32)[:32])
                self.fernet = Fernet(key_b64)
            else:
                # Generate new key if none provided
                self.fernet = Fernet(Fernet.generate_key())

    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        try:
            return self.fernet.encrypt(data.encode()).decode()
        except Exception as e:
            raise TokenEncryptionError(f"Failed to encrypt data: {str(e)}")

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt encrypted string data"""
        try:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            raise TokenEncryptionError(f"Failed to decrypt data: {str(e)}") 