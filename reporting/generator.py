import os
from datetime import datetime
from core.models import TargetInvestigation


class ReportGenerator:
    """Transforms TargetInvestigation state into a professional Markdown report."""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate(self, investigation: TargetInvestigation) -> str:
        """Generate a professional Markdown report from investigation data."""
        safe_target = (
            investigation.target_query.replace(" ", "_").replace('"', "").lower()
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = (
            f"{self.output_dir}/{safe_target}_osint_report_{timestamp}.md"
        )

        categorized_records = {}
        for r in investigation.records:
            if r.source_name not in categorized_records:
                categorized_records[r.source_name] = []
            categorized_records[r.source_name].append(r)

        with open(filename, "w", encoding="utf-8") as f:
            f.write("# OSINT Target Intelligence Report\n")
            f.write(f"**Target Query:** `{investigation.target_query}`\n")
            f.write(
                f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            )
            f.write(f"**Final Status:** {investigation.status}\n")
            f.write(f"**Total Verified Assets:** {len(investigation.records)}\n")
            f.write("---\n\n")

            f.write("## 1. Executive Summary\n")
            f.write(
                "This report was generated using a modular, Search-First Discovery "
                "Architecture. Initial footprinting was conducted via passive social "
                "discovery, followed by strict entity resolution to eliminate false "
                "positives. Verified technical and regulatory assets were subsequently "
                "extracted and analyzed for risk indicators.\n\n"
            )

            f.write("## 2. Categorized Data & Audit Trail\n\n")

            for source, records in categorized_records.items():
                f.write(f"### Source: {source}\n")
                f.write(
                    "| Timestamp (UTC) | Conf | Asset/Platform | Raw Data Snapshot | "
                    "Source URL |\n"
                )
                f.write("|---|---|---|---|---|\n")

                for r in records:
                    time_str = r.retrieval_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    conf_str = f"{r.confidence:.2f}"

                    asset_type = (
                        r.raw_data.get("platform")
                        or r.raw_data.get("type")
                        or "Asset"
                    )

                    data_snapshot = (
                        str(r.raw_data).replace("\n", " ").replace("|", "-")
                    )
                    if len(data_snapshot) > 80:
                        data_snapshot = data_snapshot[:77] + "..."

                    url_md = f"[Link]({r.source_url})"

                    f.write(
                        f"| {time_str} | {conf_str} | {asset_type} | "
                        f"`{data_snapshot}` | {url_md} |\n"
                    )
                f.write("\n")

            f.write("---\n")
            f.write("*End of Report*\n")

        return filename
