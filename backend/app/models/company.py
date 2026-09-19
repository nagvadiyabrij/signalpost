from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_number = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(500), nullable=False)
    status = Column(String(100))
    company_type = Column(String(100))
    registration_date = Column(String(50))
    business_address = Column(Text)
    postal_address = Column(Text)
    municipality = Column(String(200))
    industry = Column(String(500))
    industry_code = Column(String(50))
    website = Column(String(500))
    phone = Column(String(100))
    email = Column(String(200))
    description = Column(Text)
    parent_company = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_verified_at = Column(DateTime)
    
    facts = relationship("Fact", back_populates="company", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="company", cascade="all, delete-orphan")
