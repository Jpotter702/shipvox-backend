class TokenStoreError(Exception):
    """Base exception for token store errors"""
    pass

class TokenNotFoundError(TokenStoreError):
    """Raised when tokens are not found"""
    pass

class TokenEncryptionError(TokenStoreError):
    """Raised when encryption/decryption fails"""
    pass

class TokenExpiredError(TokenStoreError):
    """Raised when token is expired"""
    pass

class TokenValidationError(TokenStoreError):
    """Raised when token validation fails"""
    pass 