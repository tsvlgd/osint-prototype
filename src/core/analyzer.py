# core/analyzer.py
import logging
from src.core.models import TargetInvestigation

logger = logging.getLogger("OSINT_Analyzer")

class OSINTAnalyzer:
    """
    Handles Phase II: Analysis & Disambiguation.
    Separated from the Engine to maintain strict modularity.
    """
    @staticmethod
    def filter_and_score(investigation: TargetInvestigation) -> TargetInvestigation:
        clean_records = []
        total_risk = 0
        
        for r in investigation.records:
            # 1. VALIDATION: Drop False Positives (Requirement)
            if r.confidence <= 0.5:
                logger.debug(f"Dropped low-confidence record from {r.source_name}")
                continue 
                
            # 2. RISK SCORING (Bonus Requirement)
            risk = 0
            raw_str = str(r.raw_data).lower()
            current_conf = r.confidence
            
            if r.source_name == "Tech Infra (GitHub + WHOIS)":
                if "leaked" in raw_str or "password" in raw_str:
                    risk += 10  # Critical Risk
                if "clienttransferprohibited" in raw_str:
                    risk += 1   # Low risk / standard OPSEC practice
                    
            if r.source_name == "OpenCorporates (Regulatory)":
                if "dissolved" in raw_str or "inactive" in raw_str:
                    risk += 5   # Medium risk: Target is associated with dead companies
            
            if "Social" in r.source_name:
                query_terms = investigation.target_query.lower().split()
                match_count = sum(1 for term in query_terms if term in raw_str)
                if match_count == 0:
                    current_conf -= 0.50  # Massive penalty for irrelevant search results
            
            # Update record confidence if it was adjusted
            r.confidence = current_conf
            
            # Attach the calculated risk to the payload so Phase III (Reporting) can see it
            r.raw_data['calculated_risk'] = risk
            total_risk += risk
            
            clean_records.append(r)
            
        investigation.records = clean_records
        logger.info(f"Phase II Complete: Kept {len(clean_records)} verified records. Total Risk Score: {total_risk}")
        
        # We append the total risk score to the status for easy access later
        investigation.status = f"completed (Total Risk: {total_risk})"
        return investigation