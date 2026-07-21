# Problem Statement Alignment

This document maps the capabilities of PIA Industrial directly to the target hackathon problem statement to demonstrate how the platform solves the core challenges.

## 1. Heterogeneous Document Ingestion
**Challenge**: Industrial data exists in fragmented, unstructured formats (PDFs, shift logs, spreadsheets).
**Implementation**: PIA Industrial's `IngestionPipeline` (via `backend/app/ingestion/`) processes various file types deterministically. The demo dataset (P-101) ingests `.txt` maintenance manuals and shift logs, extracting observations, measurements, and contextual entities using rule-based parsing.

## 2. Industrial Entity Extraction
**Challenge**: Standard NLP misses domain-specific equipment tags and asset references.
**Implementation**: The platform implements deterministic pattern matching (`backend/app/knowledge/extraction/`) to reliably identify equipment tags like `P-101` and map them directly to a unified asset ontology without LLM hallucination risks.

## 3. Knowledge Graph
**Challenge**: RAG lacks structural understanding of how assets and failures relate.
**Implementation**: PIA Industrial builds a dynamic `NetworkX`-powered Knowledge Graph (`IndustrialGraphManager`). Extracted entities become nodes, and their contextual co-occurrences form edges, allowing the system to understand that a "seal failure" on "P-101" is linked to "high vibration".

## 4. RAG / Copilot
**Challenge**: Generic chatbots hallucinate or provide ungrounded advice.
**Implementation**: The Industrial Copilot (`workspace_runtime.py`) uses a deterministic evidence-retrieval pattern. It restricts search exclusively to the isolated workspace and returns citations that map directly back to the source document and chunk, ensuring 100% grounding.

## 5. Maintenance Intelligence
**Challenge**: Maintenance logs are hard to synthesize across long timelines.
**Implementation**: The `MaintenanceIntelligenceService` queries the Knowledge Graph to aggregate historical findings, repeated failures, and deferred recommendations per asset, synthesizing an automatic maintenance profile.

## 6. Root Cause Analysis (RCA)
**Challenge**: Identifying the root cause of an industrial failure requires tracing complex symptom chains.
**Implementation**: The `CausalRCAEngine` traverses the Knowledge Graph from a symptom node (e.g. "Vibration") to identify probabilistic failure mechanisms (e.g. "Bearing Wear") based on historical evidence co-occurrence.

## 7. Compliance
**Challenge**: Ensuring an asset meets regulatory or safety standards is a manual review process.
**Implementation**: The `ComplianceIntelligenceService` evaluates asset profiles against known rule families and historical inspection records to flag regulatory gaps automatically.

## 8. Lessons Learned / Failure Intelligence
**Challenge**: Knowledge leaves the plant when experts retire.
**Implementation**: The `ExpertiseIntelligenceService` quantifies organizational knowledge concentration by tracking which individuals or manuals are the sole source of critical failure evidence, preventing knowledge silos.

## 9. Evaluation Criteria Alignment
**Implementation**: The platform satisfies the hackathon's core criteria for accuracy (deterministic graph retrieval), security (workspace isolation), and user experience (responsive React UI with clear error and empty states). Generalization is proven via the HX-204 unseen dataset.
