# Label Creation Module

## Overview
The label creation module provides a unified interface for creating shipping labels across different carriers (currently FedEx, with UPS support planned). It handles the entire label creation process, including validation, API communication, and response processing.

## Features
- Carrier-agnostic label creation interface
- Comprehensive input validation
- Automatic QR code generation
- Support for special services (signature required, Saturday delivery, etc.)
- Label voiding capability
- Label status tracking

## Usage

### Creating a Label
```python
from labels.label_creator import Address, Package, LabelRequest
from labels.fedex_ship import FedExLabelCreator

# Create addresses
from_address = Address(
    name="John Doe",
    company="ACME Inc",
    street1="123 Shipper St",
    street2=None,
    city="Memphis",
    state="TN",
    zip_code="38115",
    country="US",
    phone="1234567890",
    email="shipper@example.com"
)

to_address = Address(
    name="Jane Smith",
    company=None,
    street1="456 Recipient Ave",
    street2="Suite 100",
    city="Atlanta",
    state="GA",
    zip_code="30301",
    country="US",
    phone="0987654321",
    email="recipient@example.com"
)

# Create package
package = Package(
    weight=10.5,
    length=12.0,
    width=8.0,
    height=6.0,
    packaging_type="YOUR_PACKAGING"
)

# Create label request
request = LabelRequest(
    from_address=from_address,
    to_address=to_address,
    package=package,
    service_code="FEDEX_GROUND",
    is_residential=True,
    insurance_amount=100.0,
    signature_required=True
)

# Create label
creator = FedExLabelCreator(environment="sandbox")  # Use "production" for live environment
response = await creator.create_label(request)

# Save label and QR code
with open(f"label_{response.tracking_number}.pdf", "wb") as f:
    f.write(response.label_data)

with open(f"qr_{response.tracking_number}.png", "wb") as f:
    f.write(response.qr_code)
```

### Voiding a Label
```python
success = await creator.void_label("123456789012")
if success:
    print("Label successfully voided")
```

### Checking Label Status
```python
status = await creator.get_label_status("123456789012")
print(f"Label status: {status['trackResults'][0]['statusDetail']['description']}")
```

## Error Handling
The module provides comprehensive error handling through custom exceptions:

- `LabelError`: Base exception for label-related errors
- `ValidationError`: Raised when input validation fails
- `FedExAPIError`: Raised when FedEx API calls fail
- `AuthenticationError`: Raised when authentication fails
- `PackageError`: Raised for package-related validation errors
- `AddressError`: Raised for address-related validation errors
- `ServiceError`: Raised for service-related validation errors

## Configuration
The module can be configured through environment variables:

- `FEDEX_API_KEY`: FedEx API key
- `FEDEX_SECRET_KEY`: FedEx secret key
- `FEDEX_ACCOUNT_NUMBER`: FedEx account number
- `FEDEX_METER_NUMBER`: FedEx meter number

## Testing
The module includes comprehensive unit tests. To run the tests:

```bash
pytest tests/labels/
```

## Future Enhancements
- UPS label creation support
- Batch label creation
- Address validation
- Rate calculation before label creation
- Custom label formats
- International shipping support 