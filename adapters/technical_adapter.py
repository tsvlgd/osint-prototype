import aiohttp
import asyncio
import whois
from .base import BaseAdapter
from typing import List, Dict, Any

class TechnicalInfrastructureAdapter(BaseAdapter):
    def __init__(self, github_token: str = None):
        super().__init__()
        self.source_name = "Tech Infra (GitHub + WHOIS)"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

    async def _fetch_github(self, query: str) -> List[Dict[str, Any]]:
        """Internal method to handle GitHub API"""
        url = f"https://api.github.com/search/repositories?q={query}"
        results = []
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        for item in data.get("items", [])[:3]: # Top 3 to reduce noise
                            results.append(self.normalize_record(
                                raw_data={
                                    "type": "repository",
                                    "repo_name": item["full_name"],
                                    "description": item["description"]
                                },
                                confidence=0.8,
                                url=item["html_url"]
                            ))
        except Exception as e:
            print(f"[GitHub Error] {str(e)}")
        return results

    async def _fetch_whois(self, domain: str) -> List[Dict[str, Any]]:
        """Internal method to handle WHOIS lookups asynchronously"""
        results = []
        try:
            # In a production system, Phase II analysis would map the name to a domain first.
            target_domain = f"{domain.replace(' ', '').lower()}.com"
            
            # Run the synchronous WHOIS lookup in a separate thread so it doesn't block async I/O
            domain_info = await asyncio.to_thread(whois.whois, target_domain)
            
            if domain_info.domain_name:
                results.append(self.normalize_record(
                    raw_data={
                        "type": "domain_registration",
                        "registrar": domain_info.registrar,
                        "creation_date": str(domain_info.creation_date),
                        "name_servers": domain_info.name_servers
                    },
                    confidence=0.9,
                    url=f"https://whois.domaintools.com/{target_domain}"
                ))
        except Exception as e:
            print(f"[WHOIS Error] {str(e)}")
        return results

    async def fetch(self, query: str) -> List[Dict[str, Any]]:
        """
        The main public method. Uses asyncio.gather to run GitHub and WHOIS lookups concurrently.
        """
        github_task = self._fetch_github(query)
        whois_task = self._fetch_whois(query)
        
        results = await asyncio.gather(github_task, whois_task)
        
        flattened_results = [item for sublist in results for item in sublist]
        return flattened_results



# By using asyncio.gather, we aren't waiting 2 seconds for GitHub and then 2 seconds for WHOIS. We fire both requests simultaneously and get all the infrastructure data back in ~2 seconds total.

# The Trade-off
# Notice that the adapter only fetches and formats the data. It does not decide if the repository actually belongs to the target company. Filtering out false positives (Entity Resolution) is the job of Phase II. Keeping these responsibilities separate ensures that if the GitHub API changes tomorrow, your core analysis logic doesn't break.