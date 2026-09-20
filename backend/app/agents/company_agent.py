from typing import Dict, Any, List, Optional
from httpx import AsyncClient, Timeout
from app.sources.brreg import BrregAdapter
from app.sources.company_web import CompanyWebAdapter
from app.validators.identity import IdentityVerifier
from app.validators.fact import FactValidator
from app.models.company import Company
from app.models.fact import Fact
from app.models.source import Source
from app.models.search_history import SearchHistory
from app.models.api_usage import ApiUsage
from app.database import SessionLocal
from app.utils.cache import get_global_budget
from datetime import datetime
import hashlib


class CompanyAgent:
    """Main agent for researching Norwegian companies"""
    
    def __init__(self):
        self.client = AsyncClient(timeout=Timeout(15.0))
        self.sources = [
            BrregAdapter(self.client),
            CompanyWebAdapter(self.client),
        ]
        self.validator = FactValidator()
        self.identity_verifier = IdentityVerifier()
        self.request_budget = get_global_budget()
    
    def _generate_id(self) -> str:
        """Generate a unique ID"""
        import secrets
        return secrets.token_urlsafe(36)
    
    async def research_company(self, organization_number: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Research a company by organization number.
        Returns complete company profile with verified facts.
        """
        # Validate organization number
        if not self.identity_verifier.is_valid_norwegian_org_number(organization_number):
            # Track invalid search
            db = SessionLocal()
            try:
                search_history = SearchHistory(
                    id=self._generate_id(),
                    user_id=user_id,
                    organization_number=organization_number,
                    company_name=None,
                    status="error"
                )
                db.add(search_history)
                db.commit()
            except Exception as e:
                print(f"Failed to track search history: {e}")
                db.rollback()
            finally:
                db.close()
            
            return {
                "status": "error",
                "code": "INVALID_ORGANIZATION_NUMBER",
                "message": "Invalid Norwegian organization number format"
            }
        
        # Check request budget
        if not self.request_budget.can_make_request():
            return {
                "status": "error",
                "code": "REQUEST_LIMIT_EXCEEDED",
                "message": "Request budget exceeded. Please try again later."
            }
        
        # Normalize organization number
        normalized_org_number = self.identity_verifier._normalize_org_number(organization_number)
        
        # Stage 1: Company resolution from primary source
        company_info = await self._resolve_company(normalized_org_number)
        
        if not company_info:
            # Track failed search
            db = SessionLocal()
            try:
                search_history = SearchHistory(
                    id=self._generate_id(),
                    user_id=user_id,
                    organization_number=normalized_org_number,
                    company_name=None,
                    status="not_found"
                )
                db.add(search_history)
                db.commit()
            except Exception as e:
                print(f"Failed to track search history: {e}")
                db.rollback()
            finally:
                db.close()
            
            return {
                "status": "not_found",
                "message": "Company not found in primary registry"
            }
        
        company_name = company_info.get("company_name")
        
        # Stage 2: Search additional sources
        all_facts = []
        all_sources = []
        warnings = []
        
        for source in self.sources:
            try:
                # Search for company
                search_results = await source.search(normalized_org_number, company_name)
                
                # Record search request
                self.request_budget.record_request(
                    url=f"{source.name}_search",
                    method="SEARCH",
                    status=200
                )
                
                for result in search_results:
                    # Verify company identity
                    is_valid, reason, confidence = self.identity_verifier.verify_company_identity(
                        normalized_org_number,
                        company_name,
                        result
                    )
                    
                    if not is_valid:
                        warnings.append(f"Rejected source {source.name}: {reason}")
                        continue
                    
                    # Fetch content
                    content = await source.fetch(result["url"])
                    if not content:
                        warnings.append(f"Could not fetch content from {result['url']}")
                        continue
                    
                    # Record successful fetch
                    self.request_budget.record_request(
                        url=result["url"],
                        method="GET",
                        status=200
                    )
                    
                    # Extract facts
                    extracted_facts = await source.extract(content, normalized_org_number)
                    
                    # Validate and record each fact
                    for field, value in extracted_facts.items():
                        if value is None:
                            continue
                        
                        fact = {
                            "field": field,
                            "value": value,
                            "source_url": result["url"],
                            "source_name": source.name,
                            "retrieved_at": datetime.utcnow().isoformat(),
                            "verified": True,
                            "confidence": confidence
                        }
                        
                        # Validate fact
                        is_valid, validation_reason = self.validator.validate(fact)
                        if is_valid:
                            all_facts.append(fact)
                        else:
                            warnings.append(f"Rejected fact {field}: {validation_reason}")
                    
                    # Record source
                    source_record = {
                        "url": result["url"],
                        "name": source.name,
                        "retrieved_at": datetime.utcnow().isoformat(),
                        "http_status": 200
                    }
                    all_sources.append(source_record)
                    
            except Exception as e:
                warnings.append(f"Error with source {source.name}: {str(e)}")
        
        # Stage 3: Store in database
        db = SessionLocal()
        try:
            # Check if company already exists
            existing_company = db.query(Company).filter(
                Company.organization_number == normalized_org_number
            ).first()
            
            if existing_company:
                # Update existing company
                for key, value in company_info.items():
                    if key not in ["raw_data", "organization_number"]:
                        setattr(existing_company, key, value)
                existing_company.last_verified_at = datetime.utcnow()
                existing_company.updated_at = datetime.utcnow()
                company_id = existing_company.id
            else:
                # Create new company
                new_company = Company(
                    organization_number=normalized_org_number,
                    name=company_info.get("company_name"),
                    status=company_info.get("status"),
                    company_type=company_info.get("company_type"),
                    registration_date=company_info.get("registration_date"),
                    business_address=company_info.get("business_address"),
                    postal_address=company_info.get("postal_address"),
                    municipality=company_info.get("municipality"),
                    industry=company_info.get("industry"),
                    industry_code=company_info.get("industry_code"),
                    last_verified_at=datetime.utcnow()
                )
                db.add(new_company)
                db.commit()
                db.refresh(new_company)
                company_id = new_company.id
            
            # Store facts
            for fact_data in all_facts:
                # Check for existing fact
                existing_fact = db.query(Fact).filter(
                    Fact.company_id == company_id,
                    Fact.field == fact_data["field"],
                    Fact.source_url == fact_data["source_url"]
                ).first()
                
                if not existing_fact:
                    new_fact = Fact(
                        company_id=company_id,
                        field=fact_data["field"],
                        value=str(fact_data["value"]),
                        source_url=fact_data["source_url"],
                        source_name=fact_data["source_name"],
                        retrieved_at=datetime.utcnow(),
                        confidence=fact_data.get("confidence", 0.8),
                        verified=fact_data["verified"]
                    )
                    db.add(new_fact)
            
            # Store sources
            for source_data in all_sources:
                content_hash = hashlib.md5(source_data["url"].encode()).hexdigest()
                
                existing_source = db.query(Source).filter(
                    Source.company_id == company_id,
                    Source.url == source_data["url"]
                ).first()
                
                if not existing_source:
                    new_source = Source(
                        company_id=company_id,
                        url=source_data["url"],
                        name=source_data["name"],
                        retrieved_at=datetime.utcnow(),
                        http_status=source_data.get("http_status"),
                        content_hash=content_hash
                    )
                    db.add(new_source)
            
            db.commit()
            
            # Track search history
            search_history = SearchHistory(
                id=self._generate_id(),
                organization_number=normalized_org_number,
                company_name=company_info.get("company_name"),
                status="success"
            )
            db.add(search_history)
            db.commit()
            
        except Exception as e:
            db.rollback()
            warnings.append(f"Database error: {str(e)}")
        finally:
            db.close()
        
        # Stage 4: Build response
        response = {
            "status": "success",
            "organization_number": normalized_org_number,
            "company": company_info,
            "facts": all_facts,
            "sources": all_sources,
            "warnings": warnings
        }
        
        return response
    
    async def _resolve_company(self, organization_number: str) -> Optional[Dict[str, Any]]:
        """Resolve company from primary source (Brønnøysund)"""
        brreg = BrregAdapter(self.client)
        results = await brreg.search(organization_number)
        
        if results:
            return results[0]
        return None
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
