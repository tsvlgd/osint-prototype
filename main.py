# main.py
import asyncio
import os
import json
from dotenv import load_dotenv

# Import our custom adapters
from adapters.google_search_adapter import GoogleSearchAdapter
from adapters.technical_adapter import TechnicalInfrastructureAdapter
from adapters.opencorporates_adapter import OpenCorporatesAdapter

# Import the orchestrator
from core.engine import OSINTEngine

# Load environment variables from the .env file
load_dotenv()

async def main():
    # The target we are investigating
    target_query = "Travis Haasch” CEO of AIGeeks" 

    print("==================================================")
    print(f"Initializing OSINT Framework for target: {target_query}")
    print("==================================================")

    # 1. Grab keys from environment
    google_key = os.getenv("GOOGLE_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    # corp_token = os.getenv("OPENCORPORATES_API_TOKEN")

    if not google_key:
        print("[!] ERROR: GOOGLE_API_KEY is required in the .env file.")
        return

    # 2. Instantiate Phase I Adapters
    google_adapter = GoogleSearchAdapter(api_key=google_key)
    tech_adapter = TechnicalInfrastructureAdapter(github_token=github_token)
    corp_adapter = OpenCorporatesAdapter()

    # 3. Instantiate Phase II Engine
    engine = OSINTEngine(google_adapter, tech_adapter, corp_adapter)

    # 4. Run the Pipeline
    investigation = await engine.run_investigation(target_query)

    # 5. Output the Results (Terminal Output for Testing)
    print("\n==================================================")
    print(f"FINAL STATE: {investigation.status}")
    print(f"TOTAL VERIFIED RECORDS: {len(investigation.records)}")
    print("==================================================\n")
    
    for record in investigation.records:
        print(f"[Score: {record.confidence:.2f}] Source: {record.source_name}")
        print(f"   URL: {record.source_url}")
        print(f"   DATA: {json.dumps(record.raw_data, indent=2)}")
        print("-" * 60)

if __name__ == "__main__":
    # Standard boilerplate for running an asyncio program
    asyncio.run(main())