import asyncio
import re
import logging
from typing import List
from .models import TargetInvestigation, IntelligenceRecord
from .analyzer import OSINTAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("OSINT_Engine")


class OSINTEngine:
    """Orchestrates the multi-phase OSINT investigation pipeline."""

    def __init__(self, google_adapter, tech_adapter, corp_adapter):
        """Initialize with dependency-injected adapters."""
        self.google = google_adapter
        self.tech = tech_adapter
        self.corp = corp_adapter
        self.analyzer = OSINTAnalyzer()

    def _extract_domain(self, records: List[IntelligenceRecord]) -> str:
        """Extract official domain from social footprints."""
        domain_pattern = re.compile(r"\b([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b")

        for r in records:
            snippet = r.raw_data.get("snippet", "").lower()
            matches = domain_pattern.findall(snippet)

            for match in matches:
                if not any(
                    x in match
                    for x in ["linkedin.com", "twitter.com", "t.co", "google"]
                ):
                    return match.replace("www.", "")
        return ""

    async def run_investigation(self, query: str) -> TargetInvestigation:
        """Execute the complete OSINT investigation pipeline."""
        investigation = TargetInvestigation(target_query=query, status="analyzing")
        logger.info(f"Starting investigation pipeline for: '{query}'")

        logger.info("Step 1: Running Social Discovery...")
        social_records = await self.google.fetch(query)
        for r in social_records:
            investigation.add_record(r)

        logger.info("Step 2: Extracting verified domain...")
        discovered_domain = self._extract_domain(social_records)

        if discovered_domain:
            logger.info(f"Domain discovered: {discovered_domain}")
        else:
            logger.warning("No domain discovered. Technical scans limited.")

        logger.info("Step 3: Running Technical & Regulatory Scans...")
        enrichment_tasks = [
            self.tech.fetch(search_query=query, verified_domain=discovered_domain),
            self.corp.fetch(query),
        ]

        enrichment_results = await asyncio.gather(*enrichment_tasks)
        for adapter_results in enrichment_results:
            for r in adapter_results:
                investigation.add_record(r)

        logger.info("Step 4: Running Analysis & Risk Scoring...")
        investigation = self.analyzer.filter_and_score(investigation)

        logger.info("Pipeline complete.")
        return investigation