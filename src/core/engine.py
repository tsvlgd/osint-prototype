# core/engine.py
import asyncio
import re
import logging
from typing import List
from .models import TargetInvestigation, IntelligenceRecord
from .analyzer import OSINTAnalyzer

# logging 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("OSINT_Engine")

class OSINTEngine:
    def __init__(self, google_adapter, tech_adapter, corp_adapter):
        """
        Dependency Injection: The engine controls the adapters without needing 
        to know their internal scraping/API logic.
        """
        self.google = google_adapter
        self.tech = tech_adapter
        self.corp = corp_adapter
        self.analyzer = OSINTAnalyzer()

    def _extract_domain(self, records: List[IntelligenceRecord]) -> str:
        """
        Phase I Bridge: Scans social footprints to extract the official website
        so we don't have to brute-force TLDs.
        """
        domain_pattern = re.compile(r'\b([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b')
        
        for r in records:
            snippet = r.raw_data.get("snippet", "").lower()
            matches = domain_pattern.findall(snippet)
            
            for match in matches:
                # Filter out the social platforms themselves
                if not any(x in match for x in ["linkedin.com", "twitter.com", "t.co", "google"]):
                    clean_domain = match.replace("www.", "")
                    return clean_domain
        return ""

    async def run_investigation(self, query: str) -> TargetInvestigation:
        investigation = TargetInvestigation(target_query=query, status="analyzing")
        logger.info(f"Starting investigation pipeline for: '{query}'")
        
        # --- PHASE I: DISCOVERY ---
        logger.info("Step 1: Running Social Discovery...")
        social_records = await self.google.fetch(query)
        for r in social_records:
            investigation.add_record(r)
            
        # --- PHASE I: EXTRACTION ---
        logger.info("Step 2: Attempting to extract verified domain...")
        discovered_domain = self._extract_domain(social_records)
        
        if discovered_domain:
            logger.info(f"-> Verified domain discovered: {discovered_domain}")
        else:
            logger.warning("-> No domain discovered. Technical scans will be limited to protect OPSEC.")

        # --- PHASE I: TARGETED ENRICHMENT ---
        logger.info("Step 3: Running Targeted Technical & Regulatory Scans...")
        
        enrichment_tasks = [
            self.tech.fetch(search_query=query, verified_domain=discovered_domain),
            self.corp.fetch(query) 
        ]
        
        enrichment_results = await asyncio.gather(*enrichment_tasks)
        for adapter_results in enrichment_results:
            for r in adapter_results:
                investigation.add_record(r)
                
        # --- PHASE II: ANALYSIS & DISAMBIGUATION ---
        logger.info("Step 4: Running Entity Resolution and Risk Scoring...")
        # Hand off the raw data to the Analyzer to filter FPs
        investigation = self.analyzer.filter_and_score(investigation)
        
        logger.info("Pipeline executed successfully. Awaiting Reporting Engine.")
        return investigation