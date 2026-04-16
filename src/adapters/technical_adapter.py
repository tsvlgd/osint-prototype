import aiohttp
import asyncio
import whois
from .base import BaseAdapter
from typing import List, Dict, Any, Optional


class TechnicalInfrastructureAdapter(BaseAdapter):
    """Adapter for GitHub and WHOIS infrastructure queries."""

    def __init__(self, github_token: str = None):
        super().__init__()
        self.source_name = "Tech Infra (GitHub + WHOIS)"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

    async def _fetch_github(self, query: str) -> List[Dict[str, Any]]:
        """Fetch GitHub repositories matching the query."""
        url = f"https://api.github.com/search/repositories?q={query}"
        results = []
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        for item in data.get("items", [])[:3]:
                            results.append(
                                self.normalize_record(
                                    raw_data={
                                        "type": "repository",
                                        "repo_name": item["full_name"],
                                        "description": item["description"],
                                    },
                                    confidence=0.8,
                                    url=item["html_url"],
                                )
                            )
        except Exception as e:
            print(f"[{self.source_name}] GitHub Error: {str(e)}")
        return results

    async def _fetch_whois(self, domain: str) -> List[Dict[str, Any]]:
        """Fetch WHOIS information for verified domain only."""
        results = []
        if not domain or "." not in domain or len(domain.split(".")) < 2:
            return results

        try:
            domain_info = await asyncio.wait_for(
                asyncio.to_thread(whois.whois, domain),
                timeout=15.0
            )

            if getattr(domain_info, "domain_name", None):
                results.append(
                    self.normalize_record(
                        raw_data={
                            "type": "domain_registration",
                            "registrar": domain_info.registrar,
                            "creation_date": str(domain_info.creation_date),
                            "name_servers": domain_info.name_servers,
                        },
                        confidence=0.95,
                        url=f"https://whois.domaintools.com/{domain}",
                    )
                )
        except asyncio.TimeoutError:
            print(f"[{self.source_name}] WHOIS Timeout on {domain} (exceeded 15s)")
        except Exception as e:
            print(f"[{self.source_name}] WHOIS Error on {domain}: {str(e)}")

        return results

    async def fetch(
        self, search_query: str, verified_domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch technical infrastructure data from GitHub and WHOIS in parallel."""
        github_task = self._fetch_github(search_query)
        whois_task = self._fetch_whois(verified_domain)

        results = await asyncio.gather(github_task, whois_task)
        return [item for sublist in results for item in sublist]



