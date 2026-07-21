import asyncio
import os
import sys
from dotenv import load_dotenv
from osint_framework.src.adapters.google_search_adapter import GoogleSearchAdapter
from osint_framework.src.adapters.technical_adapter import TechnicalInfrastructureAdapter
from osint_framework.src.adapters.opencorporates_adapter import OpenCorporatesAdapter
from osint_framework.src.core.engine import OSINTEngine
from osint_framework.reporting.generator import ReportGenerator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

load_dotenv()


async def run_osint_investigation(target_query: str) -> tuple:
    """Runs the engine and returns the path to the generated report and investigation object."""
    google_key = os.getenv("GOOGLE_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")

    if not google_key:
        print("[!] ERROR: GOOGLE_API_KEY is required in the .env file.")
        return
    google_adapter = GoogleSearchAdapter(api_key=google_key)
    tech_adapter = TechnicalInfrastructureAdapter(github_token=github_token)
    corp_adapter = OpenCorporatesAdapter()

    engine = OSINTEngine(google_adapter, tech_adapter, corp_adapter)
    investigation = await engine.run_investigation(target_query)

    if len(investigation.records) > 0:
        report_engine = ReportGenerator()
        report_path = report_engine.generate(investigation)
        return investigation, report_path
    else:
        return None
