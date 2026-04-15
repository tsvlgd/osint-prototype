# adapters/opencorporates_adapter.py
import aiohttp
import asyncio
import os
from .base import BaseAdapter
from typing import List, Dict, Any

class OpenCorporatesAdapter(BaseAdapter):
    def __init__(self, api_token: str = None):
        super().__init__()
        self.source_name = "OpenCorporates (Regulatory)"
        # We ignore the api_token and hijack the Serper key you already have
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.base_url = "https://google.serper.dev/search"

    async def fetch(self, query: str) -> List[Dict[str, Any]]:
        results = []
        if not self.api_key:
            print(f"[{self.source_name}] Error: SERPER_API_KEY missing in .env")
            return results

        # Force Serper to only look inside OpenCorporates' database
        dork_query = f'site:opencorporates.com "{query}"'
        
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': dork_query,
            'num': 3 # We only need the top few corporate matches
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload, timeout=10) as response:
                    if response.status != 200:
                        print(f"[{self.source_name}] API Error: {response.status}")
                        return results

                    data = await response.json()
                    
                    for item in data.get("organic", []):
                        title = item.get("title", "")
                        snippet = item.get("snippet", "").lower()
                        
                        # OpenCorporates titles usually look like: "Company Name - Jurisdiction - OpenCorporates"
                        clean_name = title.replace(" - OpenCorporates", "")

                        normalized = self.normalize_record(
                            raw_data={
                                "legal_name": clean_name,
                                "registry_status": snippet # Snippet usually contains "Active", "Dissolved", etc.
                            },
                            confidence=0.90, # Slightly lower than direct API, but still very high
                            url=item.get("link", "")
                        )
                        results.append(normalized)

        except asyncio.TimeoutError:
             print(f"[{self.source_name}] Request timed out.")
        except Exception as e:
             print(f"[{self.source_name}] Error: {str(e)}")

        return results