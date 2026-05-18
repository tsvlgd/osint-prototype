# OSINT Framework

A modular, asynchronous Open Source Intelligence (OSINT) engine that aggregates data from multiple sources in a three-phase pipeline: Social Discovery → Domain Extraction → Technical & Regulatory Analysis. Built with Python async/await for concurrent API operations.

## Project Structure

```
osint_framework/
├── .env                        # Configuration (copy from .env.example)
├── .env.example                # Configuration template
├── .gitignore                  # Git exclusions
├── README.md                   # This file
├── pyproject.toml              # Package definition & entrypoint
├── requirements.txt            # Streamlit UI dependencies
├── app.py                      # Streamlit web interface
├── arch.png                    # Pipeline architecture diagram
├── osint_framework/            # Main Python module
│   ├── __init__.py
│   ├── main.py                 # Core CLI executor
│   ├── engine_wrapper.py       # Async orchestrator
│   └── src/
│       ├── core/
│       │   ├── engine.py       # Three-phase pipeline
│       │   ├── models.py       # Pydantic data models
│       │   └── analyzer.py     # Risk scoring
│       ├── adapters/
│       │   ├── base.py         # Abstract adapter
│       │   ├── google_search_adapter.py     # Social Discovery
│       │   ├── technical_adapter.py         # GitHub + WHOIS
│       │   └── opencorporates_adapter.py    # Regulatory data
│       └── reporting/
│           └── generator.py    # PDF + Markdown reports
└── reports/                    # Generated output directory
```

## Prerequisites

- **Python:** 3.10 or higher
- **pip/uv:** Package manager (included with Python)
- **API Keys:**
  - Serper.dev API key (Google Dorking for Social Discovery)
  - GitHub Personal Access Token (Repository search)

## Setup (Shortest Path)

### Step 1: Create Virtual Environment

```bash
# Navigate to project directory
cd osint_framework

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows
```

### Step 2: Install Package in Editable Mode

This command installs the engine locally and creates a global `osint-fetch` binary executable in your venv:

```bash
# Using pip
pip install -e .

# OR using uv (faster)
uv pip install -e .
```

**Verify installation:**
```bash
which osint-fetch  # Should show: /path/to/venv/bin/osint-fetch
osint-fetch --help
```

### Step 3: Configure `.env` File

```bash
# Copy the example template
cp .env.example .env

# Edit .env with your credentials
nano .env  # or your preferred editor
```

Fill in the two required keys:
- `GOOGLE_API_KEY` - From [Serper.dev](https://serper.dev)
- `GITHUB_TOKEN` - From [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)

## Execution Methods

### Method 1: CLI Verification (Recommended for Testing)

Execute the installed binary directly:

```bash
# Basic execution
osint-fetch --target "Tesla"

# JSON output (for programmatic use)
osint-fetch --target "Tesla" --json
```

**Output:**
- **Default:** Human-readable terminal output with record summary
- **--json flag:** Structured JSON for API integration or log forwarding

### Method 2: Web UI (Optional)

Spin up the Streamlit interactive interface:

```bash
streamlit run app.py
```

The UI opens at `http://localhost:8501` with:
- Live investigation dashboard
- Interactive filtering
- PDF report generation
- Real-time status updates

## Backend Integration Hook

To integrate with your Node/Bun backend's child process spawner:

### Find Your Absolute venv Path

```bash
# With venv activated, run:
which osint-fetch

# Output example: /Users/sandesh/projects/osint_framework/venv/bin/osint-fetch
# Copy the full path (excluding the binary name)
```

### Configure Node Backend

In your Node/Bun `.env` file, set:

```env
OSINT_BIN_PATH=/Users/sandesh/projects/osint_framework/venv/bin/osint-fetch
```

### Spawn Process Example (Node.js)

```javascript
const { spawn } = require('child_process');

const proc = spawn(process.env.OSINT_BIN_PATH, [
  '--target', 'investigationTarget',
  '--json'
], {
  stdio: ['pipe', 'pipe', 'pipe']
});

proc.stdout.on('data', (data) => {
  const results = JSON.parse(data.toString());
  console.log('Investigation results:', results);
});

proc.stderr.on('data', (data) => {
  console.log('Logs:', data.toString());
});
```

## How It Works

### Three-Phase Pipeline

1. **Social Discovery** → Google Dorking finds public profiles, websites, social media
2. **Domain Extraction** → Identifies and verifies primary domain from social results
3. **Technical & Regulatory** → GitHub repos, WHOIS registration, corporate registries for verified domain

### Output

- **Markdown Reports:** Generated in `./reports/` with formatted tables and risk analysis
- **PDF Reports:** Professional styled documents with logo, tables, and metadata
- **JSON Structured Data:** For downstream processing or API integration

## Common Issues

| Issue | Solution |
|-------|----------|
| `osint-fetch: command not found` | Ensure venv is activated and `pip install -e .` was run |
| `API Error: SERPER_API_KEY missing` | Check `.env` file exists and `GOOGLE_API_KEY` is set correctly |
| `WHOIS Timeout` | Some domains take 15+ seconds; retrying usually works |
| `No records found` | Target name may not have public web presence; try variations |

## Development

Modify source files in `osint_framework/src/` and reinstall in editable mode:

```bash
pip install -e .
```

Changes take effect immediately without reinstalling.

## License

Open Source. See repository for details.
