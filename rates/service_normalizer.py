# Service Normalizer
# TODO: Implement this module

import pandas as pd
from typing import Dict, Optional
from pathlib import Path

class ServiceNormalizer:
    """Maps carrier-specific service names to normalized tiers for comparison."""
    
    def __init__(self, mapping_file: str = "data/normalized_services.csv"):
        """
        Initialize the service normalizer with a mapping file.
        
        Args:
            mapping_file (str): Path to the CSV file containing service mappings
        """
        self.mapping_file = Path(mapping_file)
        self._mappings: Optional[Dict[str, Dict[str, str]]] = None
        self._load_mappings()
    
    def _load_mappings(self) -> None:
        """Load service mappings from the CSV file."""
        try:
            df = pd.read_csv(self.mapping_file)
            self._mappings = {}
            
            # Create nested dictionary: carrier -> service_name -> normalized_service
            for _, row in df.iterrows():
                carrier = row['carrier'].lower()
                if carrier not in self._mappings:
                    self._mappings[carrier] = {}
                self._mappings[carrier][row['service_name'].lower()] = row['normalized_service']
        except Exception as e:
            raise Exception(f"Failed to load service mappings: {str(e)}")
    
    def normalize_service(self, carrier: str, service_name: str) -> str:
        """
        Normalize a carrier-specific service name to a standard tier.
        
        Args:
            carrier (str): The carrier name (e.g., 'fedex', 'ups')
            service_name (str): The carrier-specific service name
            
        Returns:
            str: The normalized service tier
            
        Raises:
            ValueError: If the service name is not found in the mappings
        """
        if not self._mappings:
            raise Exception("Service mappings not loaded")
            
        carrier = carrier.lower()
        service_name = service_name.lower()
        
        if carrier not in self._mappings:
            raise ValueError(f"Unknown carrier: {carrier}")
            
        if service_name not in self._mappings[carrier]:
            raise ValueError(f"Unknown service name for {carrier}: {service_name}")
            
        return self._mappings[carrier][service_name]
    
    def get_carrier_services(self, carrier: str) -> Dict[str, str]:
        """
        Get all service mappings for a specific carrier.
        
        Args:
            carrier (str): The carrier name
            
        Returns:
            Dict[str, str]: Dictionary of service_name -> normalized_service
        """
        if not self._mappings:
            raise Exception("Service mappings not loaded")
            
        carrier = carrier.lower()
        if carrier not in self._mappings:
            raise ValueError(f"Unknown carrier: {carrier}")
            
        return self._mappings[carrier]
    
    def add_mapping(self, carrier: str, service_name: str, normalized_service: str) -> None:
        """
        Add a new service mapping.
        
        Args:
            carrier (str): The carrier name
            service_name (str): The carrier-specific service name
            normalized_service (str): The normalized service tier
        """
        if not self._mappings:
            raise Exception("Service mappings not loaded")
            
        carrier = carrier.lower()
        if carrier not in self._mappings:
            self._mappings[carrier] = {}
            
        self._mappings[carrier][service_name.lower()] = normalized_service
        
        # Update the CSV file
        self._save_mappings()
    
    def _save_mappings(self) -> None:
        """Save the current mappings to the CSV file."""
        if not self._mappings:
            return
            
        rows = []
        for carrier, services in self._mappings.items():
            for service_name, normalized_service in services.items():
                rows.append({
                    'carrier': carrier,
                    'service_name': service_name,
                    'normalized_service': normalized_service
                })
                
        df = pd.DataFrame(rows)
        df.to_csv(self.mapping_file, index=False)
