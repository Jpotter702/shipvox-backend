from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timedelta
from .service_normalizer import ServiceNormalizer

@dataclass
class CarrierRate:
    carrier: str  # 'FEDEX' or 'UPS'
    service_name: str  # Original carrier service name
    service_type: str  # Normalized service type
    base_charge: float
    total_charge: float  # Including surcharges, fuel, etc
    currency: str
    transit_days: Optional[int]
    guaranteed_delivery: bool = False
    
@dataclass
class ComparisonResult:
    cheapest_option: CarrierRate
    fastest_reasonable_option: CarrierRate
    all_rates: List[CarrierRate]

class RateComparer:
    # Maximum price difference ratio for "reasonable" fast options
    MAX_PRICE_RATIO = 1.5  # 50% more expensive than cheapest
    
    def __init__(self):
        self.service_normalizer = ServiceNormalizer()

    def normalize_service_type(self, carrier: str, service_name: str, service_code: Optional[str] = None) -> str:
        """Convert carrier-specific service names to normalized types"""
        return self.service_normalizer.normalize_service(carrier, service_name, service_code)

    def compare_rates(self, fedex_rates: List[dict], ups_rates: List[dict]) -> ComparisonResult:
        """Compare rates from multiple carriers and find best options"""
        all_rates: List[CarrierRate] = []
        
        # Process FedEx rates
        for rate in fedex_rates:
            service_details = rate.get('serviceType', {})
            rate_details = rate.get('ratedShipmentDetails', [{}])[0]
            
            service_type = self.normalize_service_type(
                'FEDEX',
                service_details.get('serviceName', ''),
                service_details.get('serviceType', '')
            )
            
            rate_obj = CarrierRate(
                carrier='FEDEX',
                service_name=service_details.get('serviceName', ''),
                service_type=service_type,
                base_charge=float(rate_details.get('totalBaseCharge', 0)),
                total_charge=float(rate_details.get('totalNetCharge', 0)),
                currency=rate_details.get('currency', 'USD'),
                transit_days=rate.get('commit', {}).get('transitDays', {}).get('value'),
                guaranteed_delivery=bool(rate.get('commit', {}).get('guaranteedDaysToDelivery'))
            )
            all_rates.append(rate_obj)

        # Process UPS rates
        for rate in ups_rates:
            service = rate.get('Service', {})
            charges = rate.get('RatedShipment', {})
            
            service_type = self.normalize_service_type(
                'UPS',
                service.get('Description', ''),
                service.get('Code', '')
            )
            
            rate_obj = CarrierRate(
                carrier='UPS',
                service_name=service.get('Description', ''),
                service_type=service_type,
                base_charge=float(charges.get('BaseCharge', 0)),
                total_charge=float(charges.get('TotalCharge', 0)),
                currency=charges.get('Currency', 'USD'),
                transit_days=charges.get('GuaranteedDelivery', {}).get('BusinessDaysInTransit'),
                guaranteed_delivery=bool(charges.get('GuaranteedDelivery', {}).get('Guaranteed'))
            )
            all_rates.append(rate_obj)

        # Find cheapest option
        cheapest = min(all_rates, key=lambda x: x.total_charge)
        
        # Find fastest reasonable option
        reasonable_rates = [
            rate for rate in all_rates
            if rate.total_charge <= cheapest.total_charge * self.MAX_PRICE_RATIO
            and rate.transit_days is not None
        ]
        
        fastest_reasonable = min(
            reasonable_rates,
            key=lambda x: (x.transit_days, x.total_charge)
        ) if reasonable_rates else cheapest

        return ComparisonResult(
            cheapest_option=cheapest,
            fastest_reasonable_option=fastest_reasonable,
            all_rates=sorted(all_rates, key=lambda x: x.total_charge)
        )
