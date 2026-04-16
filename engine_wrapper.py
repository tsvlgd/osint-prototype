import asyncio
import os
from dotenv import load_dotenv
from src.adapters.google_search_adapter import GoogleSearchAdapter
from src.adapters.technical_adapter import TechnicalInfrastructureAdapter
from src.adapters.opencorporates_adapter import OpenCorporatesAdapter
from src.core.engine import OSINTEngine
from reporting.generator import ReportGenerator

load_dotenv()


async def run_osint_investigation(target_query: str) -> tuple:
    """Runs the engine and returns the path to the generated report and investigation object."""
    google_key = os.getenv("GOOGLE_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")

    google_adapter = GoogleSearchAdapter(api_key=google_key)
    tech_adapter = TechnicalInfrastructureAdapter(github_token=github_token)
    corp_adapter = OpenCorporatesAdapter()

    engine = OSINTEngine(google_adapter, tech_adapter, corp_adapter)
    investigation = await engine.run_investigation(target_query)

    if len(investigation.records) > 0:
        report_engine = ReportGenerator()
        report_path = report_engine.generate(investigation)
        return report_path, investigation
    else:
        return None, investigation
