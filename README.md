# PIA Industrial

## Unified Asset & Operations Brain

PIA Industrial transforms fragmented industrial information into evidence-backed operational intelligence.

**Documents → Evidence → Knowledge → Intelligence → Decisions**

---

## The Problem

Heavy Industry runs on isolated systems and tribal knowledge. Vital operational context is locked in unstructured formats like OEM manuals, maintenance work orders, shift logs, inspection reports, and regulatory requirements. 

Simple document storage and vector search (RAG) cannot solve cross-document operational reasoning. If an engineer asks, "What caused the pump failure?", a standard RAG system might return a paragraph from a manual, but it cannot connect a vibration anomaly from Tuesday's shift log to a deferred maintenance order from last month to compute the causal chain.

---

## The Solution

PIA Industrial is a deterministic intelligence platform powered by an Industrial Knowledge Graph.

We combine:
- **Universal Document Ingestion** (parsing manuals, shift logs, SAP/Maximo outputs)
- **Industrial Entity Extraction** (recognizing pumps, valves, failure modes)
- **Knowledge Graph & Hybrid Retrieval** (connecting related facts)
- **Deterministic Intelligence Engines** (Causal RCA, Counterfactuals, Maintenance Intelligence)

---

## Why PIA Industrial Is Different

* **Traditional Search**: Finds documents.
* **Standard RAG**: Finds relevant information and generates grounded answers.
* **PIA Industrial**: Connects evidence across assets and time, computes operational intelligence, evaluates causal hypotheses and counterfactual scenarios, and prioritizes decisions. The LLM acts *only* as a Copilot to summarize the deterministic facts.

---

## Architecture

![Architecture Diagram](docs/architecture/ARCHITECTURE.md)

**Sources** → **Document Intelligence** → **Observations** → **Knowledge Graph** → **Intelligence Engines** → **Copilot**

For detailed system context, see [Architecture Documentation](docs/architecture/ARCHITECTURE.md).

---

## Core Features

- **Universal Industrial Document Ingestion**
- **Industrial Entity Extraction**
- **Provenance-Aware Knowledge Graph**
- **Hybrid RAG**
- **Asset Intelligence 360**
- **Maintenance & Failure Intelligence**
- **Evidence-Backed RCA**
- **Counterfactual Maintenance Simulation**
- **Compliance Intelligence**
- **Expertise & Knowledge Concentration**
- **Decision Intelligence**
- **Citation-Grounded Copilot**

---

## Starting Paths

PIA Industrial supports both a synthetic demo and a real empty-workspace upload flow.

### Quick Demo

Select `P-101 Demo Plant` in the UI. P-101 is synthetic sample data that passes through the same ingestion and graph flow as uploaded documents.

### Real Platform Flow

Create a new workspace, upload supported documents from the Documents page, then review discovered assets, evidence, graph relationships, search, Copilot answers, and applicable intelligence.

Supported prototype uploads: TXT, MD, LOG, CSV, XLSX, XLS, and text-based PDF files.

For the M75 platform proof, see [M75 Real Platform Flow](docs/industrial/M75_REAL_PLATFORM_FLOW.md).

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-org/pia-industrial.git
cd pia-industrial

# 2. Setup the backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 3. Start the backend server
uvicorn app.api.server:app --reload
```

---

## Technology Stack

- **Python** (Backend Core)
- **FastAPI** (API Layer)
- **NetworkX** (In-Memory Knowledge Graph)
- **SQLite** (Observation & Event Store)

---

## Testing

To run the complete test suite (Unit, Integration, and Validation tests):

```bash
cd backend
python -m pytest tests/
```

*Status: 153+ tests passing in the latest M73 build.*

---

## Evaluation

Our intelligence engines are evaluated using a synthetic benchmark suite designed for industrial causal reasoning.

See [Evaluation Methodology](docs/evaluation/EVALUATION.md).

---

## Repository Structure

For a map of the complete monorepo, see [Repository Structure](docs/architecture/REPOSITORY_STRUCTURE.md).

---

## Documentation

| Guide | Description |
|---|---|
| [Getting Started](docs/GETTING_STARTED.md) | Full setup and installation guide |
| [Configuration](docs/CONFIGURATION.md) | Environment variables |
| [Architecture](docs/architecture/ARCHITECTURE.md) | System design and data flow |
| [Industrial Ontology](docs/industrial/INDUSTRIAL_ONTOLOGY.md) | Entities and relationships |
| [API Reference](docs/api/API_REFERENCE.md) | Public API endpoints |
| [Demo Guide](docs/demo/DEMO_GUIDE.md) | Step-by-step P-101 demo |
| [Contributing](CONTRIBUTING.md) | How to contribute |
| [Security](SECURITY.md) | Vulnerability reporting |

---

## Project Status

**Status: Hackathon / Research Prototype**

This system is currently designed for demonstration and architectural validation. 

---

## Limitations

- Synthetic demonstration dataset.
- NetworkX in-memory graph scalability (requires migration to Neo4j/Memgraph for production).
- No live SCADA/sensor integration implemented in this prototype.

---

## Roadmap

- Real industrial validation.
- Enterprise graph database migration.
- Live Maximo/SAP connectors.
- P&ID computer vision extraction.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Security

See [SECURITY.md](SECURITY.md).

---

## License

**LICENSE SELECTION REQUIRED**

---

## Disclaimer

PIA Industrial is decision-support software. It does not replace qualified engineers, operators, inspectors, or safety personnel. Always verify AI-generated insights against real-world telemetry and physical inspections.
