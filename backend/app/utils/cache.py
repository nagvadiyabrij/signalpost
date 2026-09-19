import hashlib
import json
from typing import Optional, Any
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.source import Source


class CacheManager:
    """Manages caching of HTTP responses and research results"""
    
    @staticmethod
    def get_content_hash(content: str) -> str:
        """Generate hash of content for cache key"""
        return hashlib.md5(content.encode()).hexdigest()
    
    @staticmethod
    def is_cache_fresh(retrieved_at: datetime, max_age_hours: int = 24) -> bool:
        """Check if cached data is still fresh"""
        age = datetime.utcnow() - retrieved_at
        return age < timedelta(hours=max_age_hours)
    
    @staticmethod
    def get_cached_source(url: str) -> Optional[Source]:
        """Get cached source if available and fresh"""
        db = SessionLocal()
        try:
            source = db.query(Source).filter(Source.url == url).first()
            if source and CacheManager.is_cache_fresh(source.retrieved_at):
                return source
            return None
        finally:
            db.close()
    
    @staticmethod
    def cache_source(url: str, name: str, content: str, http_status: int) -> Source:
        """Cache a source response"""
        db = SessionLocal()
        try:
            content_hash = CacheManager.get_content_hash(content)
            
            # Check if already exists
            existing = db.query(Source).filter(Source.url == url).first()
            if existing:
                existing.content_hash = content_hash
                existing.http_status = http_status
                existing.retrieved_at = datetime.utcnow()
                db.commit()
                db.refresh(existing)
                return existing
            
            # Create new cache entry
            new_source = Source(
                company_id=None,  # Will be set when associated with company
                url=url,
                name=name,
                retrieved_at=datetime.utcnow(),
                http_status=http_status,
                content_hash=content_hash
            )
            db.add(new_source)
            db.commit()
            db.refresh(new_source)
            return new_source
        finally:
            db.close()


class RequestBudget:
    """Manages request budget to stay within limits"""
    
    def __init__(self, max_requests: int = 1800):
        self.max_requests = max_requests
        self.requests_used = 0
        self.request_log = []
    
    def can_make_request(self) -> bool:
        """Check if we can make another request"""
        return self.requests_used < self.max_requests
    
    def record_request(self, url: str, method: str = "GET", status: int = 200):
        """Record a request"""
        self.requests_used += 1
        self.request_log.append({
            "url": url,
            "method": method,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_usage(self) -> dict:
        """Get current usage statistics"""
        return {
            "requests_used": self.requests_used,
            "requests_remaining": self.max_requests - self.requests_used,
            "usage_percentage": (self.requests_used / self.max_requests) * 100
        }
    
    def reset(self):
        """Reset the budget"""
        self.requests_used = 0
        self.request_log = []
