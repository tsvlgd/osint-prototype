import logging
from src.core.models import TargetInvestigation

logger = logging.getLogger("OSINT_Analyzer")


class OSINTAnalyzer:
    """Phase II: Analysis, Entity Resolution, and Risk Scoring."""

    @staticmethod
    def filter_and_score(
        investigation: TargetInvestigation,
    ) -> TargetInvestigation:
        """Filter false positives and calculate risk scores."""
        clean_records = []
        total_risk = 0

        for r in investigation.records:
            if r.confidence <= 0.5:
                logger.debug(f"Dropped low-confidence record from {r.source_name}")
                continue

            risk = 0
            raw_str = str(r.raw_data).lower()
            current_conf = r.confidence

            if r.source_name == "Tech Infra (GitHub + WHOIS)":
                if "leaked" in raw_str or "password" in raw_str:
                    risk += 10
                if "clienttransferprohibited" in raw_str:
                    risk += 1

            if r.source_name == "OpenCorporates (Regulatory)":
                if "dissolved" in raw_str or "inactive" in raw_str:
                    risk += 5

            if "Social" in r.source_name:
                query_terms = investigation.target_query.lower().split()
                match_count = sum(1 for term in query_terms if term in raw_str)
                if match_count == 0:
                    current_conf -= 0.50

            r.confidence = current_conf
            r.raw_data["calculated_risk"] = risk
            total_risk += risk

            clean_records.append(r)

        investigation.records = clean_records
        logger.info(
            f"Analysis complete: {len(clean_records)} verified records. "
            f"Total Risk: {total_risk}"
        )

        investigation.status = f"completed (Total Risk: {total_risk})"
        return investigation