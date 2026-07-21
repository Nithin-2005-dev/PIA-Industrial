# M74 Frontend API Coverage

This document outlines the API coverage mapping for every primary screen in the PIA Industrial UI, verifying that every page is connected to a live backend endpoint as required by the M74 milestone.

| Screen | Frontend Component | API Endpoint | Backend Service | Data Source | Integration Status |
|--------|-------------------|--------------|-----------------|-------------|-------------------|
| **Industrial Overview** | `IndustrialOverviewPage.tsx` | `GET /api/v1/industrial/overview` | `DecisionIntelligenceService` / `ComplianceIntelligenceService` | P-101 Demo Dataset | REAL PIPELINE |
| **Assets List** | `AssetsPage.tsx` | `GET /api/v1/industrial/assets` | `AssetIntelligenceService` | P-101 Demo Dataset | REAL PIPELINE |
| **Asset 360 (P-101)** | `AssetDetailsPage.tsx` | `GET /api/v1/industrial/assets/{id}` | `AssetIntelligenceService` | P-101 Demo Dataset | REAL PIPELINE |
| **RCA Trigger** | `AssetDetailsPage.tsx` (RCA Tab) | `POST /api/v1/industrial/assets/{id}/rca` | `IndustrialCausalRCA` | Deterministic Rules | REAL PIPELINE |
| **Counterfactual** | `AssetDetailsPage.tsx` (Counterfactual Tab) | `POST /api/v1/industrial/assets/{id}/simulation` | `CounterfactualMaintenanceEngine` | Deterministic Engine | REAL PIPELINE |
| **Documents Pipeline** | `DocumentsPage.tsx` | `GET /api/v1/industrial/documents` | `ObservationStore` (Aggregated) | P-101 Demo Dataset | MOCKED PIPELINE STATE (based on real observations) |
| **Knowledge Graph** | `InteractiveGraph.tsx` | `GET /api/v1/industrial/graph` | `IndustrialGraphManager` | P-101 Demo Dataset | REAL PIPELINE |
| **Maintenance** | `MaintenancePage.tsx` | `GET /api/v1/industrial/maintenance` | `MaintenanceIntelligenceService` (Aggregated) | P-101 Demo Dataset | REAL PIPELINE |
| **Failure Patterns** | `FailuresPage.tsx` | `GET /api/v1/industrial/failures` | `MaintenanceIntelligenceService` (Aggregated) | P-101 Demo Dataset | REAL PIPELINE |
| **Compliance** | `CompliancePage.tsx` | `GET /api/v1/industrial/compliance` | `ComplianceIntelligenceService` (Aggregated) | P-101 Demo Dataset | REAL PIPELINE |
| **Decisions** | `DecisionsPage.tsx` | `GET /api/v1/industrial/decisions` | `DecisionIntelligenceService` | P-101 Demo Dataset | REAL PIPELINE |
| **Industrial Copilot** | `ChatAgentSidebar.tsx` | `POST /api/v1/industrial/query` | `IndustrialKnowledgeCopilot` (Mock semantic router) | Deterministic Rules | MOCKED ROUTER |

## Implementation Notes
- **Documents Pipeline**: The `demo_seeder` does not actually process PDFs through OCR. The backend endpoint simulates the visual states based on the real loaded structured observations to fulfill the demo requirement.
- **Industrial Copilot**: The `demo_seeder` does not connect to a live LLM to save hackathon costs and latency. We have implemented a deterministic semantic router in `/api/v1/industrial/query` that explicitly understands P-101 questions and returns hardcoded responses.
- **All other endpoints** connect natively to the real Python deterministic engines built in M58-M71.
