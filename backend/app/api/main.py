from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.agents.company_agent import CompanyAgent
from app.database import init_db
from app.validators.identity import IdentityVerifier
import uvicorn


app = FastAPI(title="Signalpost API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


class CompanySearchRequest(BaseModel):
    organization_number: str


class CompanySearchResponse(BaseModel):
    status: str
    organization_number: Optional[str] = None
    company: Optional[Dict[str, Any]] = None
    facts: Optional[List[Dict[str, Any]]] = None
    sources: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[str]] = None
    code: Optional[str] = None
    message: Optional[str] = None


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "signalpost-api"}


@app.post("/api/company/search", response_model=CompanySearchResponse)
async def search_company(request: CompanySearchRequest, background_tasks: BackgroundTasks):
    """
    Search for a Norwegian company by organization number.
    This will research the company from multiple sources and return verified facts.
    """
    # Validate organization number
    verifier = IdentityVerifier()
    if not verifier.is_valid_norwegian_org_number(request.organization_number):
        return CompanySearchResponse(
            status="error",
            code="INVALID_ORGANIZATION_NUMBER",
            message="Invalid Norwegian organization number format. Please enter a 9-digit number."
        )
    
    # Research company
    agent = CompanyAgent()
    try:
        result = await agent.research_company(request.organization_number)
        return CompanySearchResponse(**result)
    except Exception as e:
        return CompanySearchResponse(
            status="error",
            code="RESEARCH_ERROR",
            message=f"Error researching company: {str(e)}"
        )
    finally:
        await agent.close()


@app.get("/api/company/{organization_number}")
async def get_company(organization_number: str):
    """Get company profile from database"""
    from app.database import SessionLocal
    from app.models.company import Company
    from app.models.fact import Fact
    from app.models.source import Source
    
    db = SessionLocal()
    try:
        company = db.query(Company).filter(
            Company.organization_number == organization_number
        ).first()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        facts = db.query(Fact).filter(Fact.company_id == company.id, Fact.verified == True).all()
        sources = db.query(Source).filter(Source.company_id == company.id).all()
        
        return {
            "status": "success",
            "company": {
                "organization_number": company.organization_number,
                "name": company.name,
                "status": company.status,
                "company_type": company.company_type,
                "registration_date": company.registration_date,
                "business_address": company.business_address,
                "postal_address": company.postal_address,
                "municipality": company.municipality,
                "industry": company.industry,
                "industry_code": company.industry_code,
                "website": company.website,
                "phone": company.phone,
                "email": company.email,
                "description": company.description,
                "parent_company": company.parent_company,
                "last_verified_at": company.last_verified_at.isoformat() if company.last_verified_at else None
            },
            "facts": [
                {
                    "field": fact.field,
                    "value": fact.value,
                    "source_url": fact.source_url,
                    "source_name": fact.source_name,
                    "retrieved_at": fact.retrieved_at.isoformat() if fact.retrieved_at else None,
                    "financial_year": fact.financial_year,
                    "currency": fact.currency,
                    "confidence": fact.confidence
                }
                for fact in facts
            ],
            "sources": [
                {
                    "url": source.url,
                    "name": source.name,
                    "retrieved_at": source.retrieved_at.isoformat() if source.retrieved_at else None,
                    "http_status": source.http_status
                }
                for source in sources
            ]
        }
    finally:
        db.close()


@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    from app.database import SessionLocal
    from app.models.company import Company
    from app.models.fact import Fact
    from app.models.source import Source
    
    db = SessionLocal()
    try:
        company_count = db.query(Company).count()
        fact_count = db.query(Fact).filter(Fact.verified == True).count()
        source_count = db.query(Source).count()
        
        return {
            "companies_researched": company_count,
            "facts_verified": fact_count,
            "sources_collected": source_count,
            "status": "healthy"
        }
    finally:
        db.close()


@app.get("/api/company/{organizationNumber}/facts")
async def get_company_facts(organizationNumber: str):
    """Get all facts for a company"""
    from app.database import SessionLocal
    from app.models.company import Company
    from app.models.fact import Fact
    
    db = SessionLocal()
    try:
        company = db.query(Company).filter(
            Company.organization_number == organizationNumber
        ).first()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        facts = db.query(Fact).filter(
            Fact.company_id == company.id,
            Fact.verified == True
        ).all()
        
        return {
            "status": "success",
            "organization_number": organizationNumber,
            "facts": [
                {
                    "field": fact.field,
                    "value": fact.value,
                    "source_url": fact.source_url,
                    "source_name": fact.source_name,
                    "retrieved_at": fact.retrieved_at.isoformat() if fact.retrieved_at else None,
                    "financial_year": fact.financial_year,
                    "currency": fact.currency,
                    "confidence": fact.confidence
                }
                for fact in facts
            ]
        }
    finally:
        db.close()


@app.get("/api/company/{organizationNumber}/sources")
async def get_company_sources(organizationNumber: str):
    """Get all sources for a company"""
    from app.database import SessionLocal
    from app.models.company import Company
    from app.models.source import Source
    
    db = SessionLocal()
    try:
        company = db.query(Company).filter(
            Company.organization_number == organizationNumber
        ).first()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        sources = db.query(Source).filter(Source.company_id == company.id).all()
        
        return {
            "status": "success",
            "organization_number": organizationNumber,
            "sources": [
                {
                    "url": source.url,
                    "name": source.name,
                    "retrieved_at": source.retrieved_at.isoformat() if source.retrieved_at else None,
                    "published_at": source.published_at.isoformat() if source.published_at else None,
                    "updated_at": source.updated_at.isoformat() if source.updated_at else None,
                    "http_status": source.http_status
                }
                for source in sources
            ]
        }
    finally:
        db.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
