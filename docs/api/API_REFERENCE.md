# API Reference

The PIA Industrial backend provides a set of FastAPI-driven HTTP REST endpoints.

When running the backend locally (`uvicorn app.api.server:app`), you can interact with the full Swagger UI at:
`http://localhost:8000/docs`

## Core Endpoints

### 1. Ingestion API
**POST** `/api/v1/industrial/ingest`
- **Purpose**: Ingest a new raw industrial text document into the pipeline.
- **Request Body**:
  ```json
  {
    "text": "P-101 vibration spiked to 5.8 mm/s.",
    "source_id": "shift_log_001",
    "timestamp": "2026-06-15T14:00:00Z"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "status": "success",
    "observation_id": "obs-12345"
  }
  ```

### 2. Copilot Query API
**POST** `/api/v1/industrial/query`
- **Purpose**: Send a natural language query to the Knowledge Copilot.
- **Request Body**:
  ```json
  {
    "query": "What caused the P-101 failure?",
    "asset_id": "P-101"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "answer": "The P-101 failure was caused by mechanical wear...",
    "citations": [
      {"source_id": "shift_log_001", "confidence": 0.95}
    ]
  }
  ```

### 3. Graph Query API
**GET** `/api/v1/industrial/asset/{asset_id}/graph`
- **Purpose**: Retrieve the deterministic graph topology for a specific asset.
- **Response**: `200 OK` (Returns a JSON representation of nodes and edges).

*Note: All endpoints currently run unauthenticated for the hackathon prototype. Do not deploy these endpoints to a public IP without adding an authentication middleware.*
