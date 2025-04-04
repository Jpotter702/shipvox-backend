"""Rates module for shipping rate comparison and normalization."""
from .rate_comparer import RateComparer
from .service_normalizer import ServiceNormalizer
from .fedex_rates import FedExRates
from .ups_rates import UPSRates

__all__ = ['RateComparer', 'ServiceNormalizer', 'FedExRates', 'UPSRates']
