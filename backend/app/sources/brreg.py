from typing import List, Dict, Any, Optional
from httpx import AsyncClient
from app.sources.base import SourceAdapter
import json


class BrregAdapter(SourceAdapter):
    """Norwegian Brønnøysund Register Centre adapter"""
    
    def __init__(self, client: AsyncClient):
        super().__init__(client)
        self.name = "Brønnøysundregistrene"
        self.base_url = "https://data.brreg.no/enhetsregisteret/api"
    
    def get_priority(self) -> int:
        return 1  # Highest priority - official government source
    
    async def search(self, organization_number: str, company_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for company by organization number"""
        results = []
        
        try:
            # Brønnøysund API endpoint for organization number
            url = f"{self.base_url}/enheter/{organization_number}"
            
            response = await self.client.get(url, timeout=15.0)
            
            if response.status_code == 200:
                data = response.json()
                results.append({
                    "url": url,
                    "organization_number": data.get("organisasjonsnummer"),
                    "company_name": data.get("navn"),
                    "status": "Active" if data.get("registrertIForetaksregisteret") else "Inactive",
                    "company_type": data.get("organisasjonsform", {}).get("beskrivelse"),
                    "registration_date": data.get("registreringsdatoIForetaksregisteret"),
                    "business_address": self._format_address(data.get("forretningsadresse")),
                    "postal_address": self._format_address(data.get("postadresse")),
                    "municipality": data.get("kommune"),
                    "industry": data.get("naeringskode1", {}).get("beskrivelse"),
                    "industry_code": data.get("naeringskode1", {}).get("kode"),
                    "raw_data": data
                })
            elif response.status_code == 404:
                # Company not found
                print(f"Company {organization_number} not found in Brønnøysund registry")
            else:
                print(f"Brreg API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Brreg search error: {e}")
        
        return results
    
    async def fetch(self, url: str) -> Optional[str]:
        """Fetch content from Brønnøysund API"""
        try:
            response = await self.client.get(url, timeout=15.0)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"Brreg fetch error: {e}")
            return None
    
    async def extract(self, content: str, organization_number: str) -> Dict[str, Any]:
        """Extract structured facts from Brønnøysund response"""
        try:
            data = json.loads(content)
            
            facts = {
                "organization_number": data.get("organisasjonsnummer"),
                "company_name": data.get("navn"),
                "status": "Active" if data.get("registrertIForetaksregisteret") else "Inactive",
                "company_type": data.get("organisasjonsform", {}).get("beskrivelse"),
                "registration_date": data.get("registreringsdatoIForetaksregisteret"),
                "business_address": self._format_address(data.get("forretningsadresse")),
                "postal_address": self._format_address(data.get("postadresse")),
                "municipality": data.get("kommune"),
                "industry": data.get("naeringskode1", {}).get("beskrivelse"),
                "industry_code": data.get("naeringskode1", {}).get("kode"),
            }
            
            return facts
        except Exception as e:
            print(f"Brreg extract error: {e}")
            return {}
    
    def _format_address(self, address_data: Optional[Dict]) -> Optional[str]:
        """Format address object to string"""
        if not address_data:
            return None
        
        parts = [
            address_data.get("adresse"),
            address_data.get("postnummer"),
            address_data.get("poststed"),
            address_data.get("kommune"),
            address_data.get("land")
        ]
        
        return ", ".join(filter(None, parts))
