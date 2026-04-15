# adapters/google_search_adapter.py
import aiohttp
import asyncio
import os
from .base import BaseAdapter
from typing import List, Dict, Any

class GoogleSearchAdapter(BaseAdapter):
    def __init__(self, api_key: str = None, cx_id: str = None):
        super().__init__()
        self.source_name = "Google Dorking (Social)"
        # We grab the Serper key from the environment
        self.api_key = os.getenv("GOOGLE_API_KEY") 
        self.base_url = "https://google.serper.dev/search"

    async def fetch(self, query: str) -> List[Dict[str, Any]]:
        results = []
        if not self.api_key:
            print(f"[{self.source_name}] Error: SERPER_API_KEY missing in .env")
            return results

        # The focused query to extract the technical domain
        dork_query = f'"{query}" (website OR homepage OR "contact us" OR "about")'
        
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': dork_query,
            'num': 10
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload, timeout=10) as response:
                    if response.status != 200:
                        print(f"[{self.source_name}] API Error: {response.status}")
                        return results

                    data = await response.json()
                    
                    # Serper returns organic Google results in the 'organic' list
                    for item in data.get("organic", []):
                        link = item.get("link", "").lower()
                        
                        # Platform routing
                        if "linkedin.com" in link: platform = "LinkedIn"
                        elif "twitter.com" in link: platform = "Twitter/X"
                        elif "github.com" in link: platform = "GitHub"
                        else: platform = "Social/Web"

                        normalized = self.normalize_record(
                            raw_data={
                                "platform": platform,
                                "title": item.get("title", ""),
                                "snippet": item.get("snippet", "")
                            },
                            confidence=0.9, 
                            url=item.get("link", "")
                        )
                        results.append(normalized)

        except asyncio.TimeoutError:
             print(f"[{self.source_name}] Request timed out.")
        except Exception as e:
             print(f"[{self.source_name}] Error: {str(e)}")

        return results