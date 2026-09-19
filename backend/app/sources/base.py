from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from httpx import AsyncClient


class SourceAdapter(ABC):
    """Base class for all source adapters"""
    
    def __init__(self, client: AsyncClient):
        self.client = client
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def search(self, organization_number: str, company_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for company information"""
        pass
    
    @abstractmethod
    async def fetch(self, url: str) -> Optional[str]:
        """Fetch content from a URL"""
        pass
    
    @abstractmethod
    async def extract(self, content: str, organization_number: str) -> Dict[str, Any]:
        """Extract structured facts from content"""
        pass
    
    def get_priority(self) -> int:
        """Return source priority (lower = higher priority)"""
        return 10
