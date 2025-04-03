import pandas as pd
from typing import Dict, Optional
from pathlib import Path

class ServiceNormalizer:
    """
    Normalizes carrier-specific service names to standardized service types
    for accurate cross-carrier comparisons.
    """
    
    # Standard service tiers from lowest to highest speed
    SERVICE_TIERS = [
        'Ground',
        'Economy',
        '2Day',
        'Express',
        'Overnight',
        'PriorityOvernight',
        'FirstOvernight'
    ]

    def __init__(self, mapping_file: str = 'data/normalized_services.csv'):
        self.mapping_file = Path(mapping_file)
        self._load_mappings()
        
        # Carrier-specific service code mappings
        self.fedex_mappings = {
            'FEDEX_GROUND': 'Ground',
            'GROUND': 'Ground',
            'FEDEX_2_DAY': '2Day',
            'INTERNATIONAL_ECONOMY': 'Economy',
            'INTERNATIONAL_PRIORITY': 'Express',
            'STANDARD_OVERNIGHT': 'Overnight',
            'PRIORITY_OVERNIGHT': 'PriorityOvernight',
            'FIRST_OVERNIGHT': 'FirstOvernight'
        }
        
        self.ups_mappings = {
            'GND': 'Ground',
            '2DA': '2Day',
            'IE': 'Economy',
            'IP': 'Express',
            '1DA': 'Overnight',
            '1DM': 'PriorityOvernight',
            '1DF': 'FirstOvernight'
        }

    def _load_mappings(self) -> None:
        """Load service mappings from CSV file"""
        try:
            self.mapping_df = pd.read_csv(self.mapping_file)
            # Convert to lowercase for case-insensitive matching
            self.mapping_df['carrier'] = self.mapping_df['carrier'].str.lower()
            self.mapping_df['service_name'] = self.mapping_df['service_name'].str.lower()
        except FileNotFoundError:
            self.mapping_df = pd.DataFrame(columns=['carrier', 'service_name', 'normalized_service'])

    def normalize_service(self, carrier: str, service_name: str, service_code: Optional[str] = None) -> str:
        """
        Convert carrier-specific service names to normalized service types.
        
        Args:
            carrier: Carrier name ('FEDEX' or 'UPS')
            service_name: Original service name from carrier
            service_code: Optional service code (some carriers use codes instead of names)
            
        Returns:
            Normalized service type
        """
        carrier = carrier.lower()
        service_name = service_name.lower()
        
        # First try exact match from CSV mappings
        match = self.mapping_df[
            (self.mapping_df['carrier'] == carrier) & 
            (self.mapping_df['service_name'] == service_name)
        ]
        if not match.empty:
            return match.iloc[0]['normalized_service']
            
        # Fall back to hardcoded mappings based on carrier
        if carrier == 'fedex':
            if service_code:
                return self.fedex_mappings.get(service_code, service_name)
            # Try to match service name patterns
            for fedex_service, normalized in self.fedex_mappings.items():
                if fedex_service.lower() in service_name:
                    return normalized
                    
        elif carrier == 'ups':
            if service_code:
                return self.ups_mappings.get(service_code, service_name)
            # Try to match service name patterns
            for ups_service, normalized in self.ups_mappings.items():
                if ups_service.lower() in service_name:
                    return normalized
                    
        # If no match found, return original service name
        return service_name

    def get_service_level(self, normalized_service: str) -> int:
        """
        Get numerical service level for comparing speed of service.
        Higher number = faster service.
        
        Args:
            normalized_service: Normalized service name
            
        Returns:
            Integer representing service level (0 = slowest, higher = faster)
        """
        try:
            return self.SERVICE_TIERS.index(normalized_service)
        except ValueError:
            return -1  # Unknown service type

    def is_faster_service(self, service_a: str, service_b: str) -> bool:
        """
        Compare two normalized service names to determine if first is faster.
        
        Args:
            service_a: First normalized service name
            service_b: Second normalized service name
            
        Returns:
            True if service_a is faster than service_b
        """
        level_a = self.get_service_level(service_a)
        level_b = self.get_service_level(service_b)
        return level_a > level_b

    def add_mapping(self, carrier: str, service_name: str, normalized_service: str) -> None:
        """
        Add new service mapping to CSV file.
        
        Args:
            carrier: Carrier name
            service_name: Original service name
            normalized_service: Normalized service type
        """
        new_row = pd.DataFrame([{
            'carrier': carrier.lower(),
            'service_name': service_name.lower(),
            'normalized_service': normalized_service
        }])
        self.mapping_df = pd.concat([self.mapping_df, new_row], ignore_index=True)
        self.mapping_df.to_csv(self.mapping_file, index=False)
