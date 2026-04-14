osint_framework/
│
├── target_report.md          # Output file [cite: 17]
├── main.py                   # Entry point: Orchestrates the pipeline
│
├── core/
│   ├── engine.py             # Manages the execution flow (dispatching adapters)
│   ├── models.py             # Unified data schemas (e.g., Pydantic models)
│   └── analyzer.py           # Phase II: Entity resolution and risk scoring [cite: 11, 15]
│
├── adapters/                 # Phase I: Data Acquisition [cite: 6]
│   ├── base.py               # Abstract Base Class defining the Adapter interface
│   ├── github_adapter.py     # Concrete implementation for GitHub
│   ├── google_search_adapter.py       # Concrete implementation for News
│   └── opencorporates_adapter.py      # Concrete implementcation for company
│
└── reporting/                # Phase III: Reporting Engine [cite: 16]
    └── generator.py          # Handles Markdown/PDF rendering


