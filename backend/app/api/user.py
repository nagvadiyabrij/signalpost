from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.search_history import SearchHistory
from app.models.saved_company import SavedCompany
from app.models.company import Company
from app.models.fact import Fact
from app.api.auth import get_current_user
import secrets


router = APIRouter(prefix="/api/user", tags=["user"])


class CompanySaveRequest(BaseModel):
    company_id: int


class SavedCompanyResponse(BaseModel):
    id: str
    company_id: int
    organization_number: str
    company_name: str
    created_at: datetime


class SearchHistoryResponse(BaseModel):
    id: str
    organization_number: str
    company_name: Optional[str]
    status: str
    searched_at: datetime


@router.get("/history", response_model=List[SearchHistoryResponse])
async def get_user_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's search history"""
    history = db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).order_by(
        SearchHistory.searched_at.desc()
    ).limit(50).all()
    
    return [
        SearchHistoryResponse(
            id=search.id,
            organization_number=search.organization_number,
            company_name=search.company_name,
            status=search.status,
            searched_at=search.searched_at
        )
        for search in history
    ]


@router.post("/saved", response_model=SavedCompanyResponse)
async def save_company(
    request: CompanySaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a company to user's favorites"""
    # Check if already saved
    existing = db.query(SavedCompany).filter(
        SavedCompany.user_id == current_user.id,
        SavedCompany.company_id == request.company_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Company already saved"
        )
    
    # Check if company exists
    company = db.query(Company).filter(Company.id == request.company_id).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )
    
    # Create saved company
    saved_company = SavedCompany(
        id=secrets.token_urlsafe(36),
        user_id=current_user.id,
        company_id=request.company_id
    )
    
    db.add(saved_company)
    db.commit()
    db.refresh(saved_company)
    
    return SavedCompanyResponse(
        id=saved_company.id,
        company_id=saved_company.company_id,
        organization_number=company.organization_number,
        company_name=company.name,
        created_at=saved_company.created_at
    )


@router.get("/saved", response_model=List[SavedCompanyResponse])
async def get_saved_companies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's saved companies"""
    saved = db.query(SavedCompany).filter(
        SavedCompany.user_id == current_user.id
    ).join(Company).order_by(
        SavedCompany.created_at.desc()
    ).all()
    
    return [
        SavedCompanyResponse(
            id=item.SavedCompany.id,
            company_id=item.SavedCompany.company_id,
            organization_number=item.Company.organization_number,
            company_name=item.Company.name,
            created_at=item.SavedCompany.created_at
        )
        for item in saved
    ]


@router.delete("/saved/{saved_id}")
async def delete_saved_company(
    saved_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a saved company"""
    saved = db.query(SavedCompany).filter(
        SavedCompany.id == saved_id,
        SavedCompany.user_id == current_user.id
    ).first()
    
    if not saved:
        raise HTTPException(
            status_code=404,
            detail="Saved company not found"
        )
    
    db.delete(saved)
    db.commit()
    
    return {"message": "Company removed from saved items"}


@router.get("/dashboard")
async def get_user_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user dashboard data"""
    # Count user's searches
    search_count = db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).count()
    
    # Count saved companies
    saved_count = db.query(SavedCompany).filter(
        SavedCompany.user_id == current_user.id
    ).count()
    
    # Count verified facts from user's saved companies
    saved_company_ids = [sc.company_id for sc in db.query(SavedCompany).filter(
        SavedCompany.user_id == current_user.id
    ).all()]
    
    facts_count = 0
    if saved_company_ids:
        facts_count = db.query(Fact).filter(
            Fact.company_id.in_(saved_company_ids),
            Fact.verified == True
        ).count()
    
    # Get recent searches
    recent_searches = db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).order_by(
        SearchHistory.searched_at.desc()
    ).limit(5).all()
    
    return {
        "companies_searched": search_count,
        "saved_companies": saved_count,
        "facts_retrieved": facts_count,
        "recent_searches": [
            {
                "organization_number": search.organization_number,
                "company_name": search.company_name,
                "status": search.status,
                "searched_at": search.searched_at.isoformat() if search.searched_at else None
            }
            for search in recent_searches
        ]
    }