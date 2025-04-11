# Service Normalizer
# TODO: Implement this module

import pandas as pd
from typing import Dict, Optional
from pathlib import Path

class ServiceNormalizer:
    """Normalizes service names and codes across different carriers."""
    
    def __init__(self):
        # Mapping of carrier-specific service codes to standardized codes
        self.service_mappings: Dict[str, Dict[str, str]] = {
            "FedEx": {
                "FEDEX_GROUND": "GROUND",
                "FEDEX_2_DAY": "2DAY",
                "FEDEX_OVERNIGHT": "OVERNIGHT",
                "FEDEX_EXPRESS_SAVER": "EXPRESS_SAVER",
                "FEDEX_FIRST_OVERNIGHT": "FIRST_OVERNIGHT",
                "FEDEX_PRIORITY_OVERNIGHT": "PRIORITY_OVERNIGHT",
                "FEDEX_STANDARD_OVERNIGHT": "STANDARD_OVERNIGHT"
            },
            "UPS": {
                "UPS_GROUND": "GROUND",
                "UPS_2DAY": "2DAY",
                "UPS_OVERNIGHT": "OVERNIGHT",
                "UPS_3DAY_SELECT": "3DAY",
                "UPS_NEXT_DAY_AIR": "NEXT_DAY",
                "UPS_NEXT_DAY_AIR_SAVER": "NEXT_DAY_SAVER",
                "UPS_NEXT_DAY_AIR_EARLY": "NEXT_DAY_EARLY"
            }
        }
        
        # Standardized service names
        self.standard_names: Dict[str, str] = {
            "GROUND": "Ground",
            "2DAY": "2-Day",
            "OVERNIGHT": "Overnight",
            "EXPRESS_SAVER": "Express Saver",
            "FIRST_OVERNIGHT": "First Overnight",
            "PRIORITY_OVERNIGHT": "Priority Overnight",
            "STANDARD_OVERNIGHT": "Standard Overnight",
            "3DAY": "3-Day Select",
            "NEXT_DAY": "Next Day Air",
            "NEXT_DAY_SAVER": "Next Day Air Saver",
            "NEXT_DAY_EARLY": "Next Day Air Early"
        }
    
    def normalize_service_code(self, carrier: str, service_code: str) -> Optional[str]:
        """Convert carrier-specific service code to standardized code."""
        if carrier in self.service_mappings:
            return self.service_mappings[carrier].get(service_code, service_code)
        return service_code
    
    def get_standard_name(self, service_code: str) -> str:
        """Get standardized service name for a service code."""
        return self.standard_names.get(service_code, service_code)
