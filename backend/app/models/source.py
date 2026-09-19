from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    url = Column(String(1000), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    
    retrieved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    published_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    content_hash = Column(String(100))
    http_status = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", back_populates="sources")
