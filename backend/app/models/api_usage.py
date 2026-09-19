from sqlalchemy import Column, String, DateTime, Integer, Float
from datetime import datetime
from app.database import Base


class ApiUsage(Base):
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    api_name = Column(String(100), nullable=False, index=True)
    endpoint = Column(String(200))
    request_count = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    last_used = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
