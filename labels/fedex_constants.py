"""FedEx API constants and configurations."""

FEDEX_SERVICE_CODES = {
    "FEDEX_GROUND": "Ground",
    "FEDEX_2_DAY": "2Day",
    "FEDEX_EXPRESS_SAVER": "Express Saver",
    "PRIORITY_OVERNIGHT": "Priority Overnight",
    "STANDARD_OVERNIGHT": "Standard Overnight"
}

FEDEX_PACKAGE_TYPES = {
    "YOUR_PACKAGING": "Your Packaging",
    "FEDEX_BOX": "FedEx Box",
    "FEDEX_PAK": "FedEx Pak",
    "FEDEX_TUBE": "FedEx Tube",
    "FEDEX_ENVELOPE": "FedEx Envelope"
}

FEDEX_API_ENDPOINTS = {
    "production": "https://apis.fedex.com",
    "sandbox": "https://apis-sandbox.fedex.com"
}

FEDEX_API_PATHS = {
    "ship": "/ship/v1/shipments",
    "cancel": "/ship/v1/shipments/cancel",
    "track": "/track/v1/trackingnumbers",
    "rate": "/rate/v1/rates/quotes"
}

# Validation constants
MIN_PACKAGE_WEIGHT = 0.1  # pounds
MAX_PACKAGE_WEIGHT = 150.0  # pounds
MIN_PACKAGE_DIMENSION = 0.1  # inches
MAX_PACKAGE_DIMENSION = 108.0  # inches

# Label format constants
LABEL_FORMATS = {
    "PDF": "PDF",
    "ZPL": "ZPL"
}

LABEL_STOCK_TYPES = {
    "PAPER_85X11_TOP_HALF_LABEL": "PAPER_85X11_TOP_HALF_LABEL",
    "PAPER_85X11_BOTTOM_HALF_LABEL": "PAPER_85X11_BOTTOM_HALF_LABEL",
    "PAPER_85X11": "PAPER_85X11"
} 