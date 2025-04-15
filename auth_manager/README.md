# Auth Manager Module

The Auth Manager module provides a unified interface for handling carrier authentication and token management.

## Features

- Carrier-specific authentication flows (FedEx, UPS)
- Secure token storage with encryption
- Token refresh management
- Health monitoring
- Metrics collection

## Configuration

The module is configured through environment variables:

```bash
# Database
AUTH_DATABASE_URL=sqlite:///tokens.db

# Token Settings
AUTH_TOKEN_ENCRYPTION_KEY=your_encryption_key
AUTH_TOKEN_REFRESH_BUFFER_MINUTES=10
AUTH_TOKEN_EXPIRATION_BUFFER_MINUTES=5

# FedEx Configuration
AUTH_FEDEX_ENABLED=true
AUTH_FEDEX_CLIENT_ID=your_client_id
AUTH_FEDEX_CLIENT_SECRET=your_client_secret
AUTH_FEDEX_SANDBOX=true

# UPS Configuration
AUTH_UPS_ENABLED=true
AUTH_UPS_CLIENT_ID=your_client_id
AUTH_UPS_CLIENT_SECRET=your_client_secret
AUTH_UPS_REDIRECT_URI=http://localhost/callback
AUTH_UPS_SANDBOX=true

# Monitoring
AUTH_ENABLE_METRICS=true
AUTH_METRICS_PORT=9090
AUTH_LOG_LEVEL=INFO
```

## Usage

### Basic Authentication Flow

```python
from auth_manager.factory import AuthManagerFactory
from auth_manager.config import settings

# Create auth manager
auth_manager = AuthManagerFactory.create(
    fedex_config=settings.get_fedex_config(),
    ups_config=settings.get_ups_config(),
    encryption_key=settings.token_encryption_key
)

# Initiate authentication
auth_url = auth_manager.initiate_auth("ups", {
    "state": "your_state",
    "user_id": "user123"
})

# Handle callback
tokens = auth_manager.handle_callback("ups", {
    "code": "authorization_code",
    "user_id": "user123"
})

# Get valid token
valid_tokens = auth_manager.get_valid_token("user123", "ups")
```

### Health Checks

```python
from auth_manager.health import health_check

# Get system health
health_status = health_check.get_overall_health()
print(health_status)
```

## API Reference

### AuthManager

- `initiate_auth(carrier: str, user_context: dict) -> str`
  - Initiates authentication flow for a carrier
  - Returns authorization URL for OAuth flows

- `handle_callback(carrier: str, request_data: dict) -> dict`
  - Handles OAuth callback
  - Returns token information

- `get_valid_token(user_id: str, carrier: str) -> dict`
  - Gets valid token, refreshing if necessary
  - Returns token information

### TokenStore

- `save_tokens(user_id: str, carrier: str, tokens: dict)`
  - Saves or updates tokens for a user and carrier

- `get_tokens(user_id: str, carrier: str) -> dict`
  - Retrieves tokens for a user and carrier

- `delete_tokens(user_id: str, carrier: str)`
  - Deletes tokens for a user and carrier

## Error Handling

The module uses custom exceptions for error handling:

- `AuthenticationError`: Base exception for auth errors
- `TokenNotFoundError`: Token not found
- `TokenExpiredError`: Token has expired
- `TokenValidationError`: Token validation failed
- `TokenEncryptionError`: Encryption/decryption failed
- `CarrierNotSupportedError`: Carrier not supported
- `InvalidAuthFlowError`: Invalid auth flow requested

## Monitoring

The module provides Prometheus metrics:

- `auth_token_refresh_total`: Total token refreshes
- `auth_token_refresh_duration_seconds`: Token refresh duration
- `auth_errors_total`: Authentication errors
- `auth_token_store_operations_total`: Token store operations

## Health Checks

Health checks monitor:
- Database connectivity
- Token store configuration
- Carrier configurations
- System uptime

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 