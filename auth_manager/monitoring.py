import logging
from typing import Optional
from prometheus_client import Counter, Histogram, start_http_server
from .config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('auth_manager')

# Define metrics
TOKEN_REFRESH_COUNTER = Counter(
    'auth_token_refresh_total',
    'Total number of token refreshes',
    ['carrier', 'status']
)

TOKEN_REFRESH_DURATION = Histogram(
    'auth_token_refresh_duration_seconds',
    'Time spent refreshing tokens',
    ['carrier']
)

AUTH_ERROR_COUNTER = Counter(
    'auth_errors_total',
    'Total number of authentication errors',
    ['carrier', 'error_type']
)

TOKEN_STORE_OPERATIONS = Counter(
    'auth_token_store_operations_total',
    'Total number of token store operations',
    ['operation', 'status']
)

class MetricsManager:
    """Manager for authentication metrics"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        if enabled:
            try:
                start_http_server(settings.metrics_port)
                logger.info(f"Metrics server started on port {settings.metrics_port}")
            except Exception as e:
                logger.error(f"Failed to start metrics server: {e}")
                self.enabled = False
    
    def record_token_refresh(self, carrier: str, success: bool, duration: float):
        """Record token refresh metrics"""
        if not self.enabled:
            return
            
        status = "success" if success else "failure"
        TOKEN_REFRESH_COUNTER.labels(carrier=carrier, status=status).inc()
        if success:
            TOKEN_REFRESH_DURATION.labels(carrier=carrier).observe(duration)
    
    def record_auth_error(self, carrier: str, error_type: str):
        """Record authentication error"""
        if not self.enabled:
            return
            
        AUTH_ERROR_COUNTER.labels(carrier=carrier, error_type=error_type).inc()
    
    def record_token_store_operation(self, operation: str, success: bool):
        """Record token store operation"""
        if not self.enabled:
            return
            
        status = "success" if success else "failure"
        TOKEN_STORE_OPERATIONS.labels(operation=operation, status=status).inc()

# Global metrics manager instance
metrics = MetricsManager(enabled=settings.enable_metrics) 