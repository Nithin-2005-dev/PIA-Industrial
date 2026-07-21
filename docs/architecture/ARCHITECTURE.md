# PIA Industrial: Unified Asset & Operations Brain

## System Architecture

The following diagram illustrates the data flow and system boundaries of the PIA Industrial platform.

```mermaid
graph TD
    %% External Systems
    subgraph "External Sources"
        MAXIMO[Maximo/EAM]
        PDF[Manuals & PDFs]
        SCADA[SCADA/Sensors]
        LOGS[Shift Logs]
    end

    %% Ingestion Layer
    subgraph "Ingestion & Extraction (app.ingestion & app.extraction)"
        INGEST_ADAPTER[Industrial Adapter]
        OCR[PDF Extractor]
        NORMALIZER[Observation Normalizer]
        EXTRACTOR[Dictionary & Expertise Extractors]
        RESOLVER[Entity Resolver]
    end

    %% Knowledge Layer
    subgraph "Knowledge Graph & Storage (app.knowledge)"
        GRAPH_BUILDER[Knowledge Graph Builder]
        GRAPH_DB[(Industrial Knowledge Graph)]
        OBS_DB[(Observation Store)]
        HYBRID_RAG[Hybrid Retriever]
    end

    %% Intelligence Layer
    subgraph "Deterministic Intelligence Engines (app.intelligence)"
        CAUSAL[Causal RCA Engine]
        MAINTENANCE[Maintenance Engine]
        RISK[Risk & Expertise Engine]
        COMPLIANCE[Compliance Engine]
        DECISION[Decision Prioritization]
    end

    %% Copilot Layer
    subgraph "Copilot Experience (app.kernel & Frontend)"
        COPILOT[Knowledge Copilot]
        LLM[LLM Context Generator]
        UI[Hackathon UX]
    end

    %% Flow: Ingestion -> Extraction
    MAXIMO -->|JSON/API| INGEST_ADAPTER
    PDF -->|Raw Text| OCR
    SCADA -->|Time-series| INGEST_ADAPTER
    LOGS -->|Unstructured Text| OCR

    INGEST_ADAPTER --> NORMALIZER
    OCR --> NORMALIZER
    
    NORMALIZER -->|Normalized Observations| EXTRACTOR
    EXTRACTOR -->|Raw Entities| RESOLVER
    RESOLVER -->|Canonical Assets/Components| GRAPH_BUILDER

    %% Flow: Knowledge Graph
    GRAPH_BUILDER -->|Nodes & Edges| GRAPH_DB
    NORMALIZER -->|Immutable Facts| OBS_DB

    %% Flow: Intelligence
    GRAPH_DB -->|Topology| CAUSAL
    OBS_DB -->|Events| CAUSAL
    GRAPH_DB --> MAINTENANCE
    OBS_DB --> MAINTENANCE
    GRAPH_DB --> RISK
    GRAPH_DB --> COMPLIANCE
    
    CAUSAL --> DECISION
    MAINTENANCE --> DECISION
    RISK --> DECISION
    COMPLIANCE --> DECISION

    %% Flow: Copilot
    DECISION -->|Actionable Recommendations| COPILOT
    HYBRID_RAG -->|Context & Provenance| COPILOT
    GRAPH_DB <-->|Traversals| HYBRID_RAG
    COPILOT <-->|Natural Language| LLM
    COPILOT <-->|Queries/Answers| UI
```

## Key Principles
1. **LLMs understand language. Deterministic engines compute facts.**
2. All counterfactual simulations, causal tracking, and maintenance scoring are executed by deterministic graph algorithms.
3. The LLM simply provides the linguistic interface to explain these deterministic insights with strict provenance.

## System Context
PIA Industrial acts as the intelligence layer sitting above legacy industrial systems (Maximo, SAP EAM, SCADA historians) and unstructured knowledge repositories (SharePoint manuals, shift logs). It ingests this fragmented data, normalizes it into a unified ontology, and computes operational insights.

## Major Components
1. **app.ingestion**: Normalizes unstructured text and APIs into immutable `Observation` facts.
2. **app.extraction**: Resolves raw strings ("main pump", "P-101") into canonical `EntityRef` objects.
3. **app.knowledge**: Maintains the `IndustrialGraphManager` (NetworkX) and the `ObservationStore` (SQLite).
4. **app.intelligence**: The suite of deterministic engines (Causal RCA, Counterfactuals, Compliance, Maintenance).
5. **app.kernel**: The Copilot runtime that safely interfaces with the LLM.

## Canonical Data Pipeline
1. **Ingest**: A shift log is uploaded.
2. **Extract**: NLP identifies "high vibration" on "P-101".
3. **Persist**: The fact is saved to the SQLite `ObservationStore`.
4. **Graph Build**: The `KnowledgeGraphBuilder` adds an edge from `Observation` -> `P-101`.
5. **Compute**: The `IndustrialCausalRCA` engine triggers, analyzing the graph topology to identify "Mechanical Wear" as the root cause.
6. **Decide**: The `DecisionIntelligenceService` flags P-101 for immediate intervention.
7. **Interact**: The user asks the Copilot, "Why did P-101 fail?" The Copilot fetches the exact causal chain and cites the original shift log.

## Deterministic vs LLM Responsibilities
| Responsibility | Engine |
|---|---|
| Computing Risk Scores | Deterministic (`Risk & Expertise Engine`) |
| Identifying Root Causes | Deterministic (`Causal RCA Engine`) |
| Simulating Interventions | Deterministic (`Counterfactual Engine`) |
| Parsing Natural Language Queries | LLM (`Copilot Context Generator`) |
| Summarizing Findings | LLM (`Copilot Answer Builder`) |

## Persistence Layer
- **Observation Store**: SQLite relational database storing immutable facts.
- **Knowledge Graph**: In-memory NetworkX graph representing the current topological state. (Planned migration to Neo4j/Memgraph for scale).

## API & Frontend
- **API**: FastAPI providing REST endpoints for ingestion, graph querying, and Copilot execution.
- **Frontend**: React application utilizing Vanilla CSS for a premium industrial UI.

## Trust Boundaries
- All user input is sanitized before entering the extraction pipeline.
- The LLM is **never** granted write access to the Knowledge Graph or the Observation Store. It only has read access via strictly typed Tool bindings.
