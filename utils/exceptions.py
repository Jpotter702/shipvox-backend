# Exceptions
# TODO: Implement this module

class ShipVoxError(Exception):
    """Base exception class for ShipVox application."""
    pass

class ValidationError(ShipVoxError):
    """Raised when input validation fails."""
    pass

class AuthenticationError(ShipVoxError):
    """Raised when authentication with carrier APIs fails."""
    pass

class APIError(ShipVoxError):
    """Raised when carrier API calls fail."""
    def __init__(self, carrier: str, status_code: int, message: str):
        self.carrier = carrier
        self.status_code = status_code
        self.message = message
        super().__init__(f"{carrier} API error ({status_code}): {message}")

class RateError(ShipVoxError):
    """Raised when rate calculation or comparison fails."""
    pass

class LabelError(ShipVoxError):
    """Raised when label generation fails."""
    pass

class PickupError(ShipVoxError):
    """Raised when pickup scheduling fails."""
    pass

class ConfigurationError(ShipVoxError):
    """Raised when there's an issue with the application configuration."""
    pass

class ServiceMappingError(ShipVoxError):
    """Raised when there's an issue with service name mappings."""
    pass
