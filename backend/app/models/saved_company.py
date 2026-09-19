from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class SavedCompany(Base):
    __tablename__ = "saved_companies"
    
    id = Column(String(36), primary_key=True, index=True)  # UUID
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="saved_companies")
    company = relationship("Company")
