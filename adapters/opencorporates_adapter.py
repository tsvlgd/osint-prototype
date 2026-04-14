import aiohttp
import asyncio
from .base import BaseAdapter
from typing import List, Dict, Any

class OpenCorporatesAdapter(BaseAdapter):
    def __init__(self, api_token: str = None):
        """
        OpenCorporates can be queried without an API token for basic searches,
        but a token increases rate limits.
        """
        super().__init__()
        self.source_name = "OpenCorporates (Regulatory)"
        self.base_url = "https://api.opencorporates.com/v0.4/companies/search"
        self.api_token = api_token

    async def fetch(self, query: str) -> List[Dict[str, Any]]:
        results = []
        
        # We query the API and explicitly ask to only see active companies
        params = {
            'q': query,
            'current_status': 'Active',
            'per_page': 5 # Keep the payload small and relevant
        }
        
        if self.api_token:
            params['api_token'] = self.api_token

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=10) as response:
                    
                    if response.status == 404:
                        return results # No legal entity found
                        
                    if response.status != 200:
                        print(f"[{self.source_name}] API Error: {response.status}")
                        return results

                    data = await response.json()
                    companies = data.get("results", {}).get("companies", [])
                    
                    for item in companies:
                        company_data = item.get("company", {})
                        
                        normalized = self.normalize_record(
                            raw_data={
                                "legal_name": company_data.get("name"),
                                "jurisdiction": company_data.get("jurisdiction_code"),
                                "incorporation_date": company_data.get("incorporation_date"),
                                "registry_url": company_data.get("registry_url")
                            },
                            # Legal registries are highly authoritative, so base confidence is high
                            confidence=0.95, 
                            url=company_data.get("opencorporates_url")
                        )
                        results.append(normalized)

        except asyncio.TimeoutError:
             print(f"[{self.source_name}] Request timed out.")
        except Exception as e:
             print(f"[{self.source_name}] Error: {str(e)}")

        return results