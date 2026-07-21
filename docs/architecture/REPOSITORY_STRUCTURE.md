# Repository Structure

PIA Industrial is structured as a domain-driven monorepo to clearly separate ingestion, data storage, deterministic intelligence, and the RAG presentation layer.

## Root Level
```text
pia-industrial/
├── backend/            # The core deterministic intelligence engine (Python/FastAPI)
├── frontend/           # The Hackathon UI and Copilot chat (React/Vite)
├── data/               # Demonstration datasets and synthetic inputs
├── docs/               # System documentation and architecture diagrams
├── .github/            # CI/CD and Issue templates
├── CHANGELOG.md        # Release history
├── CONTRIBUTING.md     # Development guidelines
├── README.md           # Primary entry point
└── SECURITY.md         # Vulnerability and security policies
```

## Backend Modules (`backend/app/`)

The `app` directory contains the primary intellectual property of PIA Industrial.

```text
backend/app/
├── api/                # FastAPI routers and HTTP interfaces
├── core/               # Configuration, dependency injection, and security
├── domain/             # Core industrial models (e.g. Asset, Observation, EntityRef)
├── ingestion/          # Adapters and parsers (e.g. Maximo, PDF, OCR)
├── extraction/         # NLP, entity recognition, and dictionary extractors
├── knowledge/          # The Industrial Knowledge Graph and Hybrid Retriever
├── intelligence/       # The deterministic engines (RCA, Counterfactual, Maintenance, Compliance)
├── kernel/             # The Copilot orchestration and LLM context generation
└── infrastructure/     # Database providers (SQLite) and file storage
```

## Other Backend Directories

```text
backend/
├── scripts/            # Database seeders (e.g., demo_seeder.py)
└── tests/              
    ├── unit/           # Unit tests for individual algorithms
    ├── integration/    # Full pipeline tests
    └── validation/     # Golden benchmark validations for RCA and Compliance
```
