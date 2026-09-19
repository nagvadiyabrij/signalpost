from typing import List, Dict, Any, Optional
from httpx import AsyncClient
from bs4 import BeautifulSoup
from app.sources.base import SourceAdapter
from urllib.parse import urljoin, urlparse
import re


class CompanyWebAdapter(SourceAdapter):
    """Adapter for extracting information from official company websites"""
    
    def __init__(self, client: AsyncClient):
        super().__init__(client)
        self.name = "Company Website"
    
    def get_priority(self) -> int:
        return 2  # Second priority - official company source
    
    async def search(self, organization_number: str, company_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for company website"""
        results = []
        
        if not company_name:
            return results
        
        try:
            # Try common website patterns
            company_slug = company_name.lower().replace(" ", "").replace("as", "").replace("asa", "")
            
            possible_domains = [
                f"https://www.{company_slug}.no",
                f"https://www.{company_slug}.com",
                f"https://{company_slug}.no",
                f"https://{company_slug}.com",
            ]
            
            for domain in possible_domains:
                try:
                    response = await self.client.get(domain, timeout=10.0, follow_redirects=True)
                    if response.status_code == 200:
                        results.append({
                            "url": str(response.url),
                            "organization_number": organization_number,
                            "company_name": company_name,
                            "source_type": "website"
                        })
                        break  # Use first successful website
                except:
                    continue
                    
        except Exception as e:
            print(f"Company web search error: {e}")
        
        return results
    
    async def fetch(self, url: str) -> Optional[str]:
        """Fetch website content"""
        try:
            response = await self.client.get(url, timeout=15.0, follow_redirects=True)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"Company web fetch error: {e}")
            return None
    
    async def extract(self, content: str, organization_number: str) -> Dict[str, Any]:
        """Extract facts from company website"""
        try:
            soup = BeautifulSoup(content, 'lxml')
            
            facts = {}
            
            # Extract email
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, content)
            if emails:
                facts["email"] = emails[0]
            
            # Extract phone numbers (Norwegian format)
            phone_pattern = r'(?:\+47|47)?\s*\d{2,3}\s*\d{2}\s*\d{2}\s*\d{2}'
            phones = re.findall(phone_pattern, content)
            if phones:
                facts["phone"] = phones[0]
            
            # Extract description from meta tags
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                facts["description"] = meta_desc['content'][:500]
            
            return facts
        except Exception as e:
            print(f"Company web extract error: {e}")
            return {}
