class AuthenticationError(Exception):
    """Base exception for authentication errors"""
    pass

class TokenNotFoundError(AuthenticationError):
    """Raised when token is not found"""
    pass

class TokenStoreError(AuthenticationError):
    """Raised when token store operation fails"""
    pass

class TokenExpiredError(AuthenticationError):
    """Raised when token has expired"""
    pass

class TokenValidationError(AuthenticationError):
    """Raised when token validation fails"""
    pass

class TokenEncryptionError(AuthenticationError):
    """Raised when token encryption/decryption fails"""
    pass

class CarrierNotSupportedError(AuthenticationError):
    """Raised when requested carrier is not supported"""
    pass

class InvalidAuthFlowError(AuthenticationError):
    """Raised when invalid auth flow is requested for carrier"""
    pass 