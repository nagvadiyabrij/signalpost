from sqlalchemy import Column, String, DateTime, Integer
from datetime import datetime
from app.database import Base


class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_number = Column(String(20), nullable=False, index=True)
    company_name = Column(String(500))
    status = Column(String(50))
    searched_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
