import argparse
import asyncio
import json
import os
import sys
from osint_framework.engine_wrapper import run_osint_investigation


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

async def run():
    # 1. Setup CLI Arguments
    parser = argparse.ArgumentParser(description="OSINT Module Bridge")
    parser.add_argument("--target", required=True, help="The entity to investigate")
    parser.add_argument("--json", action="store_true", help="Output results in JSON for the server")
    args = parser.parse_args()

    investigation = await run_osint_investigation(args.target)
    # check
    if investigation is None:
        print(json.dumps({
            "status": "No records found",
            "records": [],
            "target": args.target
        }))
        return

    if args.json:
        output = {
            "status": investigation.status,
            "records": [r.model_dump(mode='json') for r in investigation.records] 
        }
        print(json.dumps(output))
    else:
        # Human-readable output for terminal testing
        print(f"[*] Investigation complete for: {args.target}")
        print(f"[*] Records found: {len(investigation.records)}")

def main():
    """This is the synchronous entry point for the console script."""
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        sys.exit(0)
