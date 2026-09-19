from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Fact(Base):
    __tablename__ = "facts"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    field = Column(String(200), nullable=False, index=True)
    value = Column(Text)
    
    source_url = Column(String(1000), nullable=False)
    source_name = Column(String(200), nullable=False)
    source_published_date = Column(DateTime)
    source_updated_date = Column(DateTime)
    retrieved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    financial_year = Column(Integer)
    currency = Column(String(10))
    
    confidence = Column(Float, default=0.0)
    verified = Column(Boolean, default=False, nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    company = relationship("Company", back_populates="facts")
