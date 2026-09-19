from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.company import Company
from app.models.fact import Fact
from app.models.source import Source
from app.models.search_history import SearchHistory
from app.models.saved_company import SavedCompany
from app.models.audit_log import AuditLog
from app.api.auth import get_current_user, get_admin_user
from app.models import AuditLog
import secrets


router = APIRouter(prefix="/api/admin", tags=["admin"])


# Pydantic models
class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime]


class UserUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None


class CompanyResponse(BaseModel):
    id: int
    organization_number: str
    name: str
    status: str
    company_type: str
    created_at: datetime
    last_verified_at: Optional[datetime]


class FactResponse(BaseModel):
    id: int
    company_id: int
    field: str
    value: str
    source_url: str
    source_name: str
    verified: bool
    confidence: float
    financial_year: Optional[int]
    currency: Optional[str]
    retrieved_at: datetime


class SourceResponse(BaseModel):
    id: int
    url: str
    name: str
    http_status: int
    retrieved_at: datetime


class StatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_companies: int
    verified_facts: int
    total_sources: int
    searches_today: int
    api_requests: int
    estimated_cost: float


@router.get("/stats", response_model=StatsResponse)
async def get_admin_stats(admin_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Get admin dashboard statistics"""
    from app.utils.cache import get_global_budget
    
    # Count users
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # Count companies
    total_companies = db.query(Company).count()
    
    # Count verified facts
    verified_facts = db.query(Fact).filter(Fact.verified == True).count()
    
    # Count sources
    total_sources = db.query(Source).count()
    
    # Count searches today
    today = datetime.utcnow().date()
    searches_today = db.query(SearchHistory).filter(
        SearchHistory.searched_at >= today
    ).count()
    
    # Get API budget info
    budget = get_global_budget()
    usage = budget.get_usage()
    
    return StatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_companies=total_companies,
        verified_facts=verified_facts,
        total_sources=total_sources,
        searches_today=searches_today,
        api_requests=usage["requests_used"],
        estimated_cost=0.0  # TODO: Calculate actual cost
    )


@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users with pagination and search"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    users = query.offset(skip).limit(limit).all()
    
    return [
        UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
        for user in users
    ]


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create audit log before changes
    old_values = {
        "name": user.name,
        "is_active": user.is_active,
        "role": user.role.value
    }
    
    if user_update.name is not None:
        user.name = user_update.name
    
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    if user_update.role is not None:
        if user_update.role == "ADMIN":
            user.role = UserRole.ADMIN
        elif user_update.role == "USER":
            user.role = UserRole.USER
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # Create audit log
    audit_log = AuditLog(
        id=secrets.token_urlsafe(36),
        user_id=admin_user.id,
        action="USER_UPDATED",
        target_type="USER",
        target_id=user_id,
        metadata_json={
            "old_values": old_values,
            "new_values": {
                "name": user.name,
                "is_active": user.is_active,
                "role": user.role.value
            }
        }
    )
    db.add(audit_log)
    db.commit()
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login_at=user.last_login_at
    )


@router.get("/companies", response_model=List[CompanyResponse])
async def get_companies(
    skip: int = 0,
    limit: int = 50,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all companies with pagination"""
    companies = db.query(Company).offset(skip).limit(limit).all()
    
    return [
        CompanyResponse(
            id=company.id,
            organization_number=company.organization_number,
            name=company.name,
            status=company.status,
            company_type=company.company_type,
            created_at=company.created_at,
            last_verified_at=company.last_verified_at
        )
        for company in companies
    ]


@router.get("/facts", response_model=List[FactResponse])
async def get_facts(
    skip: int = 0,
    limit: int = 50,
    verified_only: bool = False,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all facts with pagination and filters"""
    query = db.query(Fact)
    
    if verified_only:
        query = query.filter(Fact.verified == True)
    
    facts = query.offset(skip).limit(limit).all()
    
    return [
        FactResponse(
            id=fact.id,
            company_id=fact.company_id,
            field=fact.field,
            value=fact.value,
            source_url=fact.source_url,
            source_name=fact.source_name,
            verified=fact.verified,
            confidence=fact.confidence,
            financial_year=fact.financial_year,
            currency=fact.currency,
            retrieved_at=fact.retrieved_at
        )
        for fact in facts
    ]


@router.get("/sources", response_model=List[SourceResponse])
async def get_sources(
    skip: int = 0,
    limit: int = 50,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all sources with pagination"""
    sources = db.query(Source).offset(skip).limit(limit).all()
    
    return [
        SourceResponse(
            id=source.id,
            url=source.url,
            name=source.name,
            http_status=source.http_status,
            retrieved_at=source.retrieved_at
        )
        for source in sources
    ]


@router.get("/searches")
async def get_searches(
    skip: int = 0,
    limit: int = 50,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get search history with pagination"""
    searches = db.query(SearchHistory).order_by(
        SearchHistory.searched_at.desc()
    ).offset(skip).limit(limit).all()
    
    return {
        "searches": [
            {
                "id": search.id,
                "organization_number": search.organization_number,
                "company_name": search.company_name,
                "status": search.status,
                "searched_at": search.searched_at.isoformat() if search.searched_at else None,
                "user_id": search.user_id
            }
            for search in searches
        ],
        "total": db.query(SearchHistory).count()
    }


@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 50,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get audit logs with pagination"""
    logs = db.query(AuditLog).order_by(
        AuditLog.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return {
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "metadata": log.metadata_json,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ],
        "total": db.query(AuditLog).count()
    }


@router.get("/system")
async def get_system_health(admin_user: User = Depends(get_admin_user)):
    """Get system health status"""
    from app.utils.cache import get_global_budget
    
    budget = get_global_budget()
    usage = budget.get_usage()
    
    # Check database connectivity
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        db.execute("SELECT 1")
        db_status = "Connected"
    except:
        db_status = "Disconnected"
    finally:
        db.close()
    
    # Check registry API
    import httpx
    registry_status = "Unknown"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://data.brreg.no/enhetsregisteret/api/", timeout=5.0)
            registry_status = "Connected" if response.status_code == 200 else "Disconnected"
    except:
        registry_status = "Disconnected"
    
    return {
        "database": db_status,
        "registry_api": registry_status,
        "search_api": "Not configured",
        "llm_api": "Not configured" if not admin_user else "Configured",
        "cache": "Connected",
        "budget": usage
    }
