import os
from datetime import datetime
from core.models import TargetInvestigation

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class ReportGenerator:
    """Transforms TargetInvestigation state into professional Markdown and PDF reports."""

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

    def generate_pdf(self, investigation: TargetInvestigation) -> str:
        """Generate a professional PDF report from investigation data."""
        if not HAS_REPORTLAB:
            raise ImportError(
                "reportlab is required for PDF generation. "
                "Install with: pip install reportlab"
            )

        safe_target = (
            investigation.target_query.replace(" ", "_").replace('"', "").lower()
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = (
            f"{self.output_dir}/{safe_target}_osint_report_{timestamp}.pdf"
        )

        doc = SimpleDocTemplate(
            filename, pagesize=letter,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=18
        )

        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1f77b4"),
            spaceAfter=12
        )

        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#2c3e50"),
            spaceAfter=10
        )

        story.append(Paragraph("OSINT Target Intelligence Report", title_style))
        story.append(Spacer(1, 0.2 * inch))

        metadata = [
            ["Target Query", investigation.target_query],
            ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")],
            ["Status", investigation.status],
            ["Total Assets", str(len(investigation.records))]
        ]

        metadata_table = Table(metadata, colWidths=[2 * inch, 4 * inch])
        metadata_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ecf0f1")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey)
        ]))

        story.append(metadata_table)
        story.append(Spacer(1, 0.3 * inch))

        story.append(Paragraph("Executive Summary", heading_style))
        summary_text = (
            "This report was generated using a modular, Search-First Discovery Architecture. "
            "Initial footprinting was conducted via passive social discovery, followed by "
            "strict entity resolution to eliminate false positives. Verified technical and "
            "regulatory assets were subsequently extracted and analyzed for risk indicators."
        )
        story.append(Paragraph(summary_text, styles["BodyText"]))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("Categorized Data & Audit Trail", heading_style))

        categorized_records = {}
        for r in investigation.records:
            if r.source_name not in categorized_records:
                categorized_records[r.source_name] = []
            categorized_records[r.source_name].append(r)

        for source, records in categorized_records.items():
            story.append(Paragraph(f"Source: {source}", styles["Heading3"]))

            table_data = [
                ["Timestamp", "Conf", "Asset Type", "Data", "URL"]
            ]

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
                if len(data_snapshot) > 40:
                    data_snapshot = data_snapshot[:37] + "..."

                url_text = r.source_url if r.source_url else "N/A"

                table_data.append([time_str, conf_str, asset_type, data_snapshot, url_text])

            table = Table(table_data, colWidths=[1.3 * inch, 0.6 * inch, 1.0 * inch, 1.2 * inch, 1.2 * inch])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("FONTSIZE", (0, 1), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("WORDWRAP", (0, 0), (-1, -1), True)
            ]))

            story.append(table)
            story.append(Spacer(1, 0.2 * inch))

        doc.build(story)
        return filename
