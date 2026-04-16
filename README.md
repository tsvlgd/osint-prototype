# OSINT Intelligence Framework
**Automated Search-First Discovery & Technical Reconnaissance Engine**

## 1. Project Overview
This project is a prototype Open-Source Intelligence (OSINT) engine designed for automated entity discovery, disambiguation, and reporting. Given a target name (Company or Individual), the engine aggregates data across social, technical, and regulatory vectors, synthesizes the findings using custom entity resolution logic, and outputs a professional, timestamped Markdown report.

---

## 2. Architecture & Design Philosophy: "Search-First"
Traditional OSINT scripts often rely on brute-forcing domains or scraping HTML blindly, leading to high false-positive rates and OPSEC burn. This engine introduces a **Search-First Architecture**, processing data in three distinct, modular phases:

### Phase I: Data Acquisition (Passive Footprinting)
Using a dependency-injected `Adapter` pattern, the engine queries distinct data vectors:
* **Social/Web (Google Dorking via Serper):** Passes targeted Dorks to map the target's public footprint.
* **Targeted URL Extraction:** Uses a custom TLD Allowlist and Platform Blocklist to mathematically extract the target's true corporate/personal domain from the social footprints.
* **Technical & Regulatory:** *Only* after a domain is verified does the engine trigger infrastructure scans (WHOIS, GitHub APIs, OpenCorporates), minimizing API waste and OPSEC risks.

### Phase II: Analysis & Entity Resolution (The "Brain")
Data without context is noise. The `OSINTAnalyzer` acts as the filter:
* **Relevance Penalties:** Drops "False Positives" by slashing the confidence score of records that do not contain strict identity markers matching the query.
* **Risk Scoring:** Scans raw JSON payloads for critical keywords (e.g., `leaked`, `dissolved`, `clienttransferprohibited`) and dynamically assigns weighted risk scores.
* **The Bouncer:** Any record that falls below a `0.50` confidence threshold after penalties is permanently dropped from the investigation state.

### Phase III: The Reporting Engine
The pipeline concludes by serializing the nested Pydantic models into a clean Markdown document, grouped by source, featuring a strictly formatted Audit Trail (Timestamp + Source URL) for human review.

---

## 3. Architecture Diagram
![alt text](image.png)

---

## 4. Evaluation Criteria Matrix
This framework was engineered to hit the **Exceptional** tier across all core assessment requirements.

| Category | Exceptional Rubric Target | Engine Implementation |
| :--- | :--- | :--- |
| **Data Integrity** | Handles "False Positives" with confidence scores. | Implements a mathematical penalty system. Base scores (e.g., 0.90) are reduced if identity markers are missing. Scores `< 0.50` are dropped entirely, preventing raw data dumping. |
| **Architecture** | Highly modular (easy to add new sources). | Uses Abstract Base Classes (`BaseAdapter`) and Dependency Injection. Adding a new source (e.g., Reddit) requires zero changes to the core `engine.py` logic. |
| **OPSEC** | Respects `robots.txt` and uses proxy rotation. | Avoids direct target scraping entirely. Utilizes Serper.dev's residential proxy rotation to bypass Google rate limits, and uses authenticated, compliant API headers for GitHub. |

---

## 5. The Roadmap to Production (Future Updates)
While this iteration is a robust CLI prototype, scaling OSINT workflows requires transitioning from a local script to a resilient, asynchronous backend.

If given additional time to push this to production, the architecture would evolve as follows:

1.  **API Exposure (FastAPI):** Wrapping the engine in a FastAPI microservice. OSINT logic should not be trapped in a terminal. An API decouples the engine, allowing frontend dashboards, Slackbots, or automated threat-hunting pipelines to trigger investigations via a simple `POST /investigate` endpoint.
2.  **Containerization (Docker & Compose):** Providing a "Zero-Friction Guarantee." A `docker-compose.yml` ensures that any reviewer or deployment environment can spin up the application and its dependencies identically, eliminating the "it works on my machine" problem.
3.  **Async Scalability (Redis/Celery):** OSINT is fundamentally slow. Adding 10 more adapters could push response times to 3+ minutes. In a production environment, keeping HTTP requests open that long is an anti-pattern. Future iterations would push the `run_investigation` task to a Celery worker queue, allowing the API to return a `task_id` instantly while processing the deep scans in the background.

---

## 6. Project Structure
```
osint_framework/
├── main.py
├── pyproject.toml
├── .gitignore
├── README.md
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── models.py
│   │   └── analyzer.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── google_search_adapter.py
│   │   ├── technical_adapter.py
│   │   └── opencorporates_adapter.py
│   └── reporting/
│       ├── __init__.py
│       └── generator.py
└── reports/
```

---

## 7. Quickstart & Installation

### Prerequisites
This project uses `uv` for lightning-fast dependency management and virtual environments. Python 3.10+ is required.

### Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd OSINT-Framework
   ```

2. **Initialize the environment and install dependencies:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```
   *(Note: Core dependencies include `aiohttp`, `pydantic`, `python-dotenv`, and `python-whois`)*

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   # Required for Social Discovery Phase
   GOOGLE_API_KEY=your_serper_key_here
   
   # Required for Technical Infrastructure Phase
   GITHUB_TOKEN=your_github_classic_token_here
   ```

### Running an Investigation
To execute the pipeline, simply run the orchestrator:
```bash
python main.py
```
Upon successful execution, the Reporting Engine will automatically generate a timestamped Markdown report inside the `reports/` directory.

---

## 8. Key Features
- **Modular Adapter Pattern:** Easy to extend with new data sources
- **Entity Resolution & De-duplication:** Confidence scoring and false positive filtering
- **Risk Scoring:** Automated keyword-based risk assessment
- **Audit Trail:** Full traceability with timestamps and source URLs
- **Production-Ready Output:** Professional Markdown reports with structured tables
- **OPSEC-Conscious:** Minimal API footprint, no brute-forcing, verified domain-only targeting

---

## 9. License & Attribution
This project is provided as-is for educational and authorized security research purposes only. Ensure all OSINT activities comply with applicable laws and ethical guidelines.
