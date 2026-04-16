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
            risk = 0
            raw_str = str(r.raw_data).lower()
            current_conf = r.confidence

            if r.source_name == "Tech Infra (GitHub + WHOIS)":
                if any(word in raw_str for word in ["leaked", "password", "secret"]):
                    risk += 10
                if "clienttransferprohibited" in raw_str:
                    risk += 1

            if r.source_name == "OpenCorporates (Regulatory)":
                if any(
                    word in raw_str for word in ["dissolved", "inactive", "struck off"]
                ):
                    risk += 5

            if "Social" in r.source_name:
                query_terms = investigation.target_query.lower().split()
                match_count = sum(1 for term in query_terms if term in raw_str)
                if match_count == 0:
                    current_conf -= 0.50

            r.confidence = round(current_conf, 2)
            r.raw_data["calculated_risk"] = risk

            if r.confidence < 0.5:
                logger.debug(
                    f"Dropping False Positive: {r.source_url} (Score: {r.confidence})"
                )
                continue

            total_risk += risk
            clean_records.append(r)

        investigation.records = clean_records
        investigation.status = f"completed (Total Risk: {total_risk})"

        logger.info(
            f"Analysis complete: {len(clean_records)} verified records. "
            f"Total Risk Score: {total_risk}"
        )
        return investigation
