import aiohttp
import asyncio
import urllib.parse
from .base import BaseAdapter
from typing import List, Dict, Any

class GoogleSearchAdapter(BaseAdapter):
    def __init__(self, api_key: str, cx_id: str):
        """
        Requires a Google API Key and a Custom Search Engine ID (cx).
        """
        super().__init__()
        self.source_name = "Google Dorking (Social)"
        self.api_key = api_key
        self.cx_id = cx_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    async def fetch(self, query: str) -> List[Dict[str, Any]]:
        results = []
        
        dork_query = f'(site:linkedin.com/in OR site:twitter.com) "{query}"'
        
        params = {
            'key': self.api_key,
            'cx': self.cx_id,
            'q': dork_query,
            'num': 5  # Fetch the top 5 results to keep noise low
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"{self.base_url}?{query_string}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    
                    if response.status != 200:
                        print(f"[{self.source_name}] API Error: {response.status}")
                        return results

                    data = await response.json()
                    
                    for item in data.get("items", []):
                        
                        platform = "LinkedIn" if "linkedin.com" in item["link"] else "Twitter" if "twitter.com" in item["link"] else "Web"

                        normalized = self.normalize_record(
                            raw_data={
                                "platform": platform,
                                "title": item.get("title", ""),
                                "snippet": item.get("snippet", "")
                            },
                            confidence=0.9, 
                            url=item["link"]
                        )
                        results.append(normalized)

        except asyncio.TimeoutError:
             print(f"[{self.source_name}] Request timed out.")
        except Exception as e:
             print(f"[{self.source_name}] Error: {str(e)}")

        return results



# With this setup, we avoid the heavy lifting of browser automation. We are letting Google's index do the hard work of finding the social footprints.
# now have an infrastructure adapter (GitHub) and a social footprint adapter (Google Dorking).