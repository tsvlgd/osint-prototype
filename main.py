import asyncio
import os
import json
from dotenv import load_dotenv

from adapters.google_search_adapter import GoogleSearchAdapter
from adapters.technical_adapter import TechnicalInfrastructureAdapter
from adapters.opencorporates_adapter import OpenCorporatesAdapter
from core.engine import OSINTEngine

from reporting.generator import ReportGenerator

load_dotenv()


async def main():
    target_query = "Travis Haasch” CEO of AIGeeks"

    print("=" * 50)
    print(f"Initializing OSINT Framework for target: {target_query}")
    print("=" * 50)

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

    print("\n" + "=" * 50)
    print(f"FINAL STATE: {investigation.status}")
    print(f"TOTAL VERIFIED RECORDS: {len(investigation.records)}")
    print("=" * 50 + "\n")


    if len(investigation.records) > 0:
        print("\nGenerating Phase III Markdown Report...")
        report_engine = ReportGenerator()
        report_path = report_engine.generate(investigation)
        print(f"[*] Report successfully generated at: {report_path}\n")
    else:
        print("\n[!] No verified records found. Skipping report generation.\n")


if __name__ == "__main__":
    asyncio.run(main())
