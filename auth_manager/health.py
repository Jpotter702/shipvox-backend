from typing import Dict, Any
from datetime import datetime
from sqlalchemy import text
from .database import engine
from .config import settings
from .monitoring import logger

class HealthCheck:
    """Health check manager for monitoring system health"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
    
    def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            with engine.connect() as conn:
                # Test database connection
                start = datetime.utcnow()
                conn.execute(text("SELECT 1"))
                latency = (datetime.utcnow() - start).total_seconds()
                
                return {
                    "status": "healthy",
                    "latency": latency,
                    "connection": "established"
                }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "connection": "failed"
            }
    
    def check_token_store(self) -> Dict[str, Any]:
        """Check token store health"""
        try:
            # Check if token store is properly configured
            if not settings.token_encryption_key:
                return {
                    "status": "warning",
                    "message": "Token encryption not configured"
                }
            
            return {
                "status": "healthy",
                "encryption": "configured"
            }
        except Exception as e:
            logger.error(f"Token store health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def check_carriers(self) -> Dict[str, Any]:
        """Check carrier configurations"""
        status = {
            "fedex": {
                "enabled": settings.fedex_enabled,
                "configured": bool(settings.fedex_client_id and settings.fedex_client_secret)
            },
            "ups": {
                "enabled": settings.ups_enabled,
                "configured": bool(
                    settings.ups_client_id and 
                    settings.ups_client_secret and 
                    settings.ups_redirect_uri
                )
            }
        }
        
        return status
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        db_health = self.check_database()
        token_health = self.check_token_store()
        carrier_health = self.check_carriers()
        
        # Determine overall status
        if db_health["status"] == "unhealthy":
            overall_status = "unhealthy"
        elif token_health["status"] == "unhealthy":
            overall_status = "unhealthy"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
            "components": {
                "database": db_health,
                "token_store": token_health,
                "carriers": carrier_health
            }
        }

# Global health check instance
health_check = HealthCheck() 