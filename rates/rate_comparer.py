# Rate Comparer
# TODO: Implement this module

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from .service_normalizer import ServiceNormalizer

@dataclass
class RateOption:
    """Represents a shipping rate option from a carrier."""
    carrier: str
    service_name: str
    cost: float
    estimated_days: int
    normalized_service: str

class RateComparer:
    """Selects cheapest and fastest viable shipping options."""
    
    def __init__(self, service_normalizer: ServiceNormalizer):
        """
        Initialize the rate comparer.
        
        Args:
            service_normalizer (ServiceNormalizer): Service normalizer instance
        """
        self.service_normalizer = service_normalizer
        self._rate_options: List[RateOption] = []
    
    def add_rate_option(self, carrier: str, service_name: str, cost: float, 
                       estimated_days: int) -> None:
        """
        Add a rate option for comparison.
        
        Args:
            carrier (str): The carrier name
            service_name (str): The carrier-specific service name
            cost (float): The shipping cost
            estimated_days (int): Estimated delivery time in days
        """
        try:
            normalized_service = self.service_normalizer.normalize_service(
                carrier, service_name
            )
            
            rate_option = RateOption(
                carrier=carrier,
                service_name=service_name,
                cost=cost,
                estimated_days=estimated_days,
                normalized_service=normalized_service
            )
            
            self._rate_options.append(rate_option)
        except ValueError as e:
            # Log the error but continue processing other rates
            print(f"Warning: {str(e)}")
    
    def get_best_options(self) -> Tuple[Optional[RateOption], Optional[RateOption]]:
        """
        Get the cheapest and cheapest/fastest shipping options.
        
        Returns:
            Tuple[Optional[RateOption], Optional[RateOption]]: 
                (cheapest_option, cheapest_fastest_option)
        """
        if not self._rate_options:
            return None, None
            
        # Sort by cost
        sorted_by_cost = sorted(self._rate_options, key=lambda x: x.cost)
        cheapest = sorted_by_cost[0]
        
        # Find the cheapest option that's significantly faster than the cheapest
        # We consider "significantly faster" to be at least 2 days faster
        cheapest_fastest = None
        for option in sorted_by_cost:
            if option.estimated_days <= cheapest.estimated_days - 2:
                if cheapest_fastest is None or option.cost < cheapest_fastest.cost:
                    cheapest_fastest = option
        
        return cheapest, cheapest_fastest
    
    def get_all_options(self) -> List[RateOption]:
        """
        Get all rate options sorted by cost.
        
        Returns:
            List[RateOption]: List of rate options
        """
        return sorted(self._rate_options, key=lambda x: x.cost)
    
    def clear_options(self) -> None:
        """Clear all stored rate options."""
        self._rate_options = []
    
    def format_response(self) -> Dict:
        """
        Format the rate comparison results for API response.
        
        Returns:
            Dict: Formatted response with cheapest and cheapest/fastest options
        """
        cheapest, cheapest_fastest = self.get_best_options()
        
        response = {
            "cheapestOption": None,
            "cheapestFastestOption": None
        }
        
        if cheapest:
            response["cheapestOption"] = {
                "carrier": cheapest.carrier,
                "service": cheapest.service_name,
                "normalizedService": cheapest.normalized_service,
                "cost": cheapest.cost,
                "estimatedDays": cheapest.estimated_days
            }
            
        if cheapest_fastest:
            response["cheapestFastestOption"] = {
                "carrier": cheapest_fastest.carrier,
                "service": cheapest_fastest.service_name,
                "normalizedService": cheapest_fastest.normalized_service,
                "cost": cheapest_fastest.cost,
                "estimatedDays": cheapest_fastest.estimated_days
            }
            
        return response
