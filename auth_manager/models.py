from sqlalchemy import Column, String, DateTime, JSON
from datetime import datetime
from .database import Base

class TokenRecord(Base):
    __tablename__ = "carrier_tokens"
    
    id = Column(String, primary_key=True)  # Composite of user_id + carrier
    user_id = Column(String, index=True)
    carrier = Column(String, index=True)
    access_token = Column(String)
    refresh_token = Column(String)
    token_type = Column(String)
    expires_at = Column(DateTime)
    scope = Column(String, nullable=True)
    additional_data = Column(JSON, nullable=True)  # For carrier-specific data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def is_expired(self):
        """Check if token is expired with 5 minute buffer"""
        if not self.expires_at:
            return True
        return datetime.utcnow() + datetime.timedelta(minutes=5) >= self.expires_at 