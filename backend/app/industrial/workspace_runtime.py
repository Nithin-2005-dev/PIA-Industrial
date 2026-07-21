"""Persistent workspace runtime for PIA Industrial.

This module keeps the hackathon architecture lightweight while making the
industrial flow data-driven: workspace -> upload -> parse -> extract -> graph.
"""
from __future__ import annotations

import json
import logging
import re
import shutil
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.domain.entity_ref import EntityRef
from app.domain.industrial.asset import Asset
from app.domain.industrial.document import Document, DocumentFormat, DocumentMetadata, DocumentStatus, DocumentType
from app.domain.industrial.relationships import IndustrialRelationship
from app.extraction.entities.extraction_pipeline import ExtractionPipeline
from app.ingestion.ingestion_pipeline import IngestionPipeline, detect_format, guess_document_type
from app.ingestion.observation.domain import (
    DocumentIngestionFacts,
    FailureEventFacts,
    InspectionFacts,
    MaintenanceActionFacts,
    Observation,
    ObservationCategory,
    ObservationContext,
    ObservationLifecycle,
    ObservationProvenance,
    ObservationType,
    ProcessingMode,
)
from app.ingestion.observation.storage import ObservationStore
from app.intelligence.legacy.asset_intelligence_service import AssetIntelligenceService
from app.intelligence.legacy.compliance_intelligence_service import ComplianceIntelligenceService
from app.intelligence.legacy.decision_intelligence_service import DecisionIntelligenceService
from app.intelligence.legacy.expertise_intelligence_service import ExpertiseIntelligenceService
from app.intelligence.legacy.industrial_causal_rca import IndustrialCausalRCA
from app.intelligence.legacy.maintenance_intelligence_service import MaintenanceIntelligenceService
from app.knowledge.graph.industrial_graph_manager import IndustrialGraphManager
from app.knowledge.retrieval.vector_store import InMemoryVectorStore, VectorStore
from app.knowledge.retrieval.embeddings import get_default_embedding_model, EmbeddingModel
from app.knowledge.retrieval.hybrid_retriever import HybridRetriever
from app.copilot.copilot import IndustrialCopilot
from app.domain.industrial.document import DocumentChunk

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".text", ".log", ".csv", ".xlsx", ".xls"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
DATA_ROOT = Path(__file__).resolve().parents[2] / "industrial_data"
UPLOAD_ROOT = DATA_ROOT / "uploads"
DEMO_P101_DIR = Path(__file__).resolve().parents[3] / "data" / "demo" / "p101"


@dataclass
class WorkspaceRecord:
    id: str
    name: str
    description: str = ""
    status: str = "EMPTY"
    source_kind: str = "USER"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class IngestionJobRecord:
    id: str
    workspace_id: str
    document_id: str | None
    document_name: str
    status: str
    stages: list[str]
    error: str | None = None
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: str | None = None


@dataclass
class WorkspaceServices:
    graph_manager: IndustrialGraphManager
    observation_store: ObservationStore
    asset_service: AssetIntelligenceService
    maintenance_service: MaintenanceIntelligenceService
    compliance_service: ComplianceIntelligenceService
    expertise_service: ExpertiseIntelligenceService
    rca_service: IndustrialCausalRCA
    decision_service: DecisionIntelligenceService
    embedding_model: EmbeddingModel
    vector_store: VectorStore
    copilot: IndustrialCopilot


class IndustrialWorkspaceRuntime:
    """Owns workspace-scoped industrial data and services."""

    def __init__(self, data_root: Path = DATA_ROOT) -> None:
        self._data_root = data_root
        self._upload_root = data_root / "uploads"
        self._workspace_index = data_root / "workspaces.json"
        self._workspaces: dict[str, WorkspaceRecord] = {}
        self._documents: dict[str, list[dict[str, Any]]] = {}
        self._jobs: dict[str, IngestionJobRecord] = {}
        self._services: dict[str, WorkspaceServices] = {}
        self._ensure_storage()
        self._load_index()
        if "demo-p101" not in self._workspaces:
            self.create_workspace(
                name="P-101 Demo Plant",
                description="Synthetic P-101 demo dataset",
                workspace_id="demo-p101",
                source_kind="DEMO",
            )
        if not self._documents.get("demo-p101"):
            self.load_demo_dataset("demo-p101")

    def _ensure_storage(self) -> None:
        self._data_root.mkdir(parents=True, exist_ok=True)
        self._upload_root.mkdir(parents=True, exist_ok=True)

    def _load_index(self) -> None:
        if self._workspace_index.exists():
            raw = json.loads(self._workspace_index.read_text(encoding="utf-8"))
            self._workspaces = {
                item["id"]: WorkspaceRecord(**item)
                for item in raw.get("workspaces", [])
            }
        for workspace_id in self._workspaces:
            self._documents[workspace_id] = self._read_workspace_documents(workspace_id)
            self._services[workspace_id] = self._build_services(workspace_id)

    def _save_index(self) -> None:
        payload = {"workspaces": [asdict(w) for w in self._workspaces.values()]}
        self._workspace_index.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _workspace_file(self, workspace_id: str) -> Path:
        return self._data_root / f"{workspace_id}.json"

    def _read_workspace_documents(self, workspace_id: str) -> list[dict[str, Any]]:
        path = self._workspace_file(workspace_id)
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8")).get("documents", [])

    def _save_workspace_documents(self, workspace_id: str) -> None:
        payload = {"documents": self._documents.get(workspace_id, [])}
        self._workspace_file(workspace_id).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _touch_workspace(self, workspace_id: str) -> None:
        workspace = self.require_workspace(workspace_id)
        workspace.updated_at = datetime.now(UTC).isoformat()
        workspace.status = "ACTIVE" if self._documents.get(workspace_id) else "EMPTY"
        self._save_index()

    def create_workspace(
        self,
        name: str,
        description: str = "",
        workspace_id: str | None = None,
        source_kind: str = "USER",
    ) -> WorkspaceRecord:
        workspace_id = workspace_id or self._slug(name)
        if workspace_id in self._workspaces:
            return self._workspaces[workspace_id]
        record = WorkspaceRecord(
            id=workspace_id,
            name=name.strip() or "New Industrial Workspace",
            description=description,
            source_kind=source_kind,
        )
        self._workspaces[workspace_id] = record
        self._documents.setdefault(workspace_id, [])
        self._services[workspace_id] = self._build_services(workspace_id)
        self._save_index()
        self._save_workspace_documents(workspace_id)
        logger.info("industrial_workspace_created", extra={"workspace_id": workspace_id})
        return record

    def list_workspaces(self) -> list[dict[str, Any]]:
        return [self.workspace_summary(workspace.id) for workspace in self._workspaces.values()]

    def require_workspace(self, workspace_id: str | None) -> WorkspaceRecord:
        selected = workspace_id or "demo-p101"
        if selected not in self._workspaces:
            raise KeyError(selected)
        return self._workspaces[selected]

    def workspace_summary(self, workspace_id: str | None) -> dict[str, Any]:
        workspace = self.require_workspace(workspace_id)
        graph = self.services(workspace.id).graph_manager.build_graph()
        assets = [n for n in graph.nodes if n.type == "asset"]
        return {
            **asdict(workspace),
            "document_count": len(self._documents.get(workspace.id, [])),
            "asset_count": len(assets),
            "graph": {"nodes": len(graph.nodes), "edges": len(graph.edges)},
            "ingestion_status": "READY",
        }

    def services(self, workspace_id: str | None) -> WorkspaceServices:
        workspace = self.require_workspace(workspace_id)
        if workspace.id not in self._services:
            self._services[workspace.id] = self._build_services(workspace.id)
        return self._services[workspace.id]

    def documents(self, workspace_id: str | None) -> list[dict[str, Any]]:
        workspace = self.require_workspace(workspace_id)
        return list(self._documents.get(workspace.id, []))

    def graph_payload(self, workspace_id: str | None) -> dict[str, Any]:
        graph = self.services(workspace_id).graph_manager.build_graph()
        nodes = [{"id": n.id, "type": n.type, "attributes": n.attributes} for n in graph.nodes]
        edges = [
            {
                "source": e.source_id,
                "target": e.target_id,
                "type": e.relationship,
                "provenance": e.provenance.evidence_id if e.provenance else "",
                "properties": e.properties,
            }
            for e in graph.edges
        ]
        return {"nodes": nodes, "edges": edges, "total_nodes": len(nodes), "truncated": False}

    def ingest_file(self, workspace_id: str | None, source_path: Path, original_name: str | None = None) -> IngestionJobRecord:
        workspace = self.require_workspace(workspace_id)
        source_path = Path(source_path)
        original_name = original_name or source_path.name
        self._validate_upload(source_path, original_name)
        job = IngestionJobRecord(
            id=f"JOB-{uuid4().hex[:8].upper()}",
            workspace_id=workspace.id,
            document_id=None,
            document_name=original_name,
            status="PROCESSING",
            stages=["UPLOADED", "PROCESSING"],
        )
        self._jobs[job.id] = job
        try:
            safe_name = self._safe_filename(original_name)
            workspace_uploads = self._upload_root / workspace.id
            workspace_uploads.mkdir(parents=True, exist_ok=True)
            stored_path = workspace_uploads / f"{uuid4().hex}_{safe_name}"
            shutil.copyfile(source_path, stored_path)

            pipeline = IngestionPipeline()
            result = pipeline.ingest(stored_path)
            if result.status != "PROCESSED":
                raise ValueError("; ".join(result.errors) or result.status)
            document = pipeline.registry.get(result.document_id)
            if document is None:
                raise ValueError("Document registry did not return processed document")

            chunks = pipeline.registry.get_chunks(document.document_id)
            extractor = ExtractionPipeline()
            extraction = extractor.extract_from_chunks(chunks, document.document_id)
            services = self.services(workspace.id)
            services.graph_manager.builder.add_document(document)
            services.graph_manager.populate_from_entities(extraction.all_resolved_entities, document.document_id)
            self._link_document_entities(services.graph_manager, extraction.all_resolved_entities, document.document_id)
            self._append_observations(services.observation_store, workspace.id, document, extraction.all_resolved_entities)

            doc_record = self._document_record(document, chunks, extraction)
            self._documents.setdefault(workspace.id, []).append(doc_record)
            self._save_workspace_documents(workspace.id)
            self._touch_workspace(workspace.id)

            job.document_id = document.document_id
            job.status = "COMPLETED"
            job.stages = ["UPLOADED", "PROCESSING", "PARSED", "CHUNKED", "EXTRACTING_ENTITIES", "RESOLVING", "GRAPH_LINKING", "INDEXING", "COMPLETED"]
            job.completed_at = datetime.now(UTC).isoformat()
            logger.info("industrial_document_ingested", extra={"workspace_id": workspace.id, "document_id": document.document_id})
            return job
        except Exception as exc:
            job.status = "FAILED"
            job.status = "FAILED"
            job.stages.append("FAILED")
            job.completed_at = datetime.now(UTC).isoformat()
            job.errors = (str(exc),)
            logger.error("industrial_document_ingestion_failed", exc_info=exc, extra={"workspace_id": workspace.id})
            return job

    def reprocess_workspace(self, workspace_id: str) -> None:
        """Re-ingest all documents in a workspace from disk to apply new logic."""
        workspace = self.require_workspace(workspace_id)
        old_docs = list(self._documents.get(workspace.id, []))
        if not old_docs:
            return

        self._documents[workspace.id] = []
        self._services.pop(workspace.id, None)

        from app.ingestion.ingestion_pipeline import IngestionPipeline
        from app.extraction.entities.extraction_pipeline import ExtractionPipeline

        for doc_record in old_docs:
            file_path = doc_record.get("file_path")
            if not file_path or not Path(file_path).exists():
                logger.warning(f"Skipping reprocessing for {doc_record.get('name')}: file not found.")
                continue

            try:
                pipeline = IngestionPipeline()
                result = pipeline.ingest(Path(file_path))
                if result.status != "PROCESSED":
                    logger.warning(f"Failed to reprocess {file_path}: {result.errors}")
                    continue
                
                document = pipeline.registry.get(result.document_id)
                if not document:
                    continue

                chunks = pipeline.registry.get_chunks(document.document_id)
                extractor = ExtractionPipeline()
                extraction = extractor.extract_from_chunks(chunks, document.document_id)

                new_record = self._document_record(document, chunks, extraction)
                self._documents[workspace.id].append(new_record)
                
                services = self.services(workspace.id)
                
                # We must manually add the new chunks to the vector store because _build_services
                # might have already been called or we want to append them incrementally.
                embeddings = [services.embedding_model.embed_text(c.content) for c in chunks]
                services.vector_store.add_chunks(chunks, embeddings)
                
                services.graph_manager.builder.add_document(document)
                services.graph_manager.populate_from_entities(extraction.all_resolved_entities, document.document_id)
                self._link_document_entities(services.graph_manager, extraction.all_resolved_entities, document.document_id)
                self._append_observations(services.observation_store, workspace.id, document, extraction.all_resolved_entities)

                self._save_workspace_documents(workspace.id)
                self._touch_workspace(workspace.id)
            except Exception as e:
                logger.error(f"Error reprocessing {file_path}: {e}")

    def load_demo_dataset(self, workspace_id: str | None = "demo-p101") -> dict[str, Any]:
        workspace = self.require_workspace(workspace_id)
        if not DEMO_P101_DIR.exists():
            raise FileNotFoundError(f"Demo dataset not found: {DEMO_P101_DIR}")
        jobs = [self.ingest_file(workspace.id, path, path.name) for path in sorted(DEMO_P101_DIR.iterdir()) if path.is_file()]
        return {"workspace_id": workspace.id, "jobs": [asdict(job) for job in jobs]}

    def get_job(self, job_id: str) -> IngestionJobRecord | None:
        return self._jobs.get(job_id)

    def search(self, workspace_id: str | None, query: str) -> list[dict[str, Any]]:
        needle = query.strip().lower()
        if not needle:
            return []
        results: list[dict[str, Any]] = []
        for document in self.documents(workspace_id):
            if needle in document["name"].lower():
                results.append({"type": "document", "id": document["document_id"], "title": document["name"], "snippet": document["name"]})
            for entity in document.get("entities", []):
                if needle in entity["value"].lower():
                    results.append({"type": entity["type"], "id": entity["value"], "title": entity["value"], "snippet": f"Found in {document['name']}"})
            for chunk in document.get("chunks", []):
                content = chunk["content"]
                index = content.lower().find(needle)
                if index >= 0:
                    start = max(0, index - 80)
                    end = min(len(content), index + 160)
                    results.append({"type": "evidence", "id": chunk["chunk_id"], "title": document["name"], "snippet": content[start:end]})
        return results[:25]

    def answer_query(self, workspace_id: str | None, query: str) -> dict[str, Any]:
        workspace = self.require_workspace(workspace_id)
        services = self.services(workspace.id)
        
        response = services.copilot.ask(query)
        
        citations = []
        for evidence in response.evidence:
            citations.append(f"{evidence.citation_tag} - {evidence.source_name}")
            
        reasoning = [
            {"step": f"Classified intent as {response.intent}"},
            {"step": f"Retrieved {len(response.evidence)} evidence candidates"},
        ]
        
        return {
            "answer": response.answer,
            "citations": citations,
            "reasoning_trace": reasoning,
        }

    def list_assets(self, workspace_id: str | None) -> list[dict[str, Any]]:
        services = self.services(workspace_id)
        graph = services.graph_manager.build_graph()
        assets = []
        for node in graph.nodes:
            if node.type != "asset":
                continue
            profile = services.asset_service.get_asset_profile(node.id)
            maint_intel = services.maintenance_service.analyze_asset(node.id)
            findings = len(maint_intel.get("findings", ())) + len(maint_intel.get("deferred_recommendations", ()))
            failures = len(maint_intel.get("repeated_failures", ()))
            risk = "HIGH" if failures else "MEDIUM" if findings else "UNKNOWN"
            assets.append(
                {
                    "asset_id": node.id,
                    "equipment_tag": node.attributes.get("equipment_tag", node.id),
                    "name": node.attributes.get("name", node.id),
                    "asset_type": node.attributes.get("asset_type", "Unknown"),
                    "system": node.attributes.get("system", "Unknown"),
                    "risk": risk,
                    "confidence": 0.85 if profile else 0.5,
                    "last_activity": profile.timeline[-1].date.isoformat() if profile and profile.timeline else None,
                    "open_findings": findings + failures,
                }
            )
        return sorted(assets, key=lambda item: item["asset_id"])

    def _build_services(self, workspace_id: str) -> WorkspaceServices:
        embedding_model = get_default_embedding_model()
        vector_store = InMemoryVectorStore()
        graph_manager = IndustrialGraphManager()
        observation_store = ObservationStore()
        for document in self._documents.get(workspace_id, []):
            self._replay_document(graph_manager, observation_store, vector_store, embedding_model, workspace_id, document)
        asset_service = AssetIntelligenceService(graph_manager, observation_store)
        maintenance_service = MaintenanceIntelligenceService(asset_service)
        compliance_service = ComplianceIntelligenceService(asset_service)
        expertise_service = ExpertiseIntelligenceService(asset_service)
        rca_service = IndustrialCausalRCA(asset_service, maintenance_service)
        decision_service = DecisionIntelligenceService(asset_service, maintenance_service, rca_service, compliance_service, expertise_service)
        
        retriever = HybridRetriever(embedding_model, vector_store, graph_manager)
        copilot = IndustrialCopilot(retriever)
        
        return WorkspaceServices(
            graph_manager=graph_manager,
            observation_store=observation_store,
            asset_service=asset_service,
            maintenance_service=maintenance_service,
            compliance_service=compliance_service,
            expertise_service=expertise_service,
            rca_service=rca_service,
            decision_service=decision_service,
            embedding_model=embedding_model,
            vector_store=vector_store,
            copilot=copilot,
        )

    def _replay_document(
        self,
        graph_manager: IndustrialGraphManager,
        observation_store: ObservationStore,
        vector_store: VectorStore,
        embedding_model: EmbeddingModel,
        workspace_id: str,
        record: dict[str, Any],
    ) -> None:
        document = Document(
            document_id=record["document_id"],
            name=record["name"],
            document_type=DocumentType(record.get("type", DocumentType.GENERAL.value)),
            document_format=DocumentFormat(record.get("format", DocumentFormat.TXT.value)),
            file_hash=record.get("file_hash", ""),
            file_path=record.get("file_path"),
            file_size_bytes=record.get("size", 0),
            status=DocumentStatus.PROCESSED,
            ingested_at=self._parse_timestamp(record["timestamp"]),
            doc_metadata=DocumentMetadata(page_count=record.get("page_count", 0), word_count=record.get("word_count", 0)),
        )
        entities = [
            self._resolved_entity_from_record(entity)
            for entity in record.get("entities", [])
        ]
        
        chunks = []
        for c in record.get("chunks", []):
            from app.domain.industrial.document import DocumentProvenance
            provenance = DocumentProvenance(
                document_id=document.document_id,
                document_name=document.name,
                document_type=document.document_type.value,
                page_number=c.get("page_number", 1)
            )
            chunk_kwargs = c.copy()
            chunk_kwargs["provenance"] = provenance
            chunks.append(DocumentChunk(**chunk_kwargs))
            
        if chunks:
            embeddings = embedding_model.embed_batch([c.content for c in chunks])
            vector_store.add_chunks(chunks, embeddings)
            
        graph_manager.builder.add_document(document)
        graph_manager.populate_from_entities(tuple(entities), document.document_id)
        self._link_document_entities(graph_manager, tuple(entities), document.document_id)
        self._append_observations(observation_store, workspace_id, document, tuple(entities), timestamp=document.ingested_at)

    def _document_record(self, document: Document, chunks: list[Any], extraction: Any) -> dict[str, Any]:
        entities = [
            {
                "type": entity.entity_type,
                "value": entity.canonical_value,
                "raw_values": list(entity.raw_values),
                "confidence": entity.confidence,
                "methods": list(entity.extraction_methods),
                "occurrence_count": entity.occurrence_count,
                "metadata": entity.metadata,
            }
            for entity in extraction.all_resolved_entities
        ]
        return {
            "document_id": document.document_id,
            "name": document.name,
            "type": document.document_type.value,
            "format": document.document_format.value,
            "file_hash": document.file_hash,
            "file_path": document.file_path,
            "size": document.file_size_bytes,
            "status": "COMPLETED",
            "timestamp": (document.ingested_at or datetime.now(UTC)).isoformat(),
            "page_count": document.doc_metadata.page_count,
            "word_count": document.doc_metadata.word_count,
            "chunks": [
                {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                }
                for chunk in chunks
            ],
            "entities": entities,
            "entity_summary": extraction.entity_summary,
            "stages": ["UPLOADED", "PROCESSING", "PARSED", "CHUNKED", "EXTRACTING_ENTITIES", "RESOLVING", "GRAPH_LINKING", "INDEXING", "COMPLETED"],
        }

    def _resolved_entity_from_record(self, entity: dict[str, Any]) -> Any:
        from app.extraction.entities.entity_resolver import ResolvedEntity

        return ResolvedEntity(
            entity_type=entity["type"],
            canonical_value=entity["value"],
            raw_values=tuple(entity.get("raw_values", (entity["value"],))),
            confidence=entity.get("confidence", 0.8),
            extraction_methods=tuple(entity.get("methods", ("persisted",))),
            occurrence_count=entity.get("occurrence_count", 1),
            metadata=entity.get("metadata", {}),
        )

    def _link_document_entities(self, graph_manager: IndustrialGraphManager, entities: tuple[Any, ...], document_id: str) -> None:
        asset_ids = [entity.canonical_value for entity in entities if entity.entity_type == "equipment_tag"]
        equipment_types = [entity.canonical_value.replace("_", " ").title() for entity in entities if entity.entity_type == "equipment_type"]
        asset_type = equipment_types[0] if equipment_types else "Unknown"
        for asset_id in asset_ids:
            graph_manager.builder.add_asset(Asset(id=asset_id, name=asset_id, equipment_tag=asset_id, asset_type=asset_type))
        related = [
            entity.canonical_value
            for entity in entities
            if entity.entity_type in {"work_order_id", "inspection_report_id", "incident_report_id"}
        ]
        for asset_id in asset_ids:
            for entity_id in related:
                graph_manager.builder._add_edge(entity_id, asset_id, IndustrialRelationship.APPLIES_TO.value, evidence_id=document_id)

    def _append_observations(
        self,
        store: ObservationStore,
        workspace_id: str,
        document: Document,
        entities: tuple[Any, ...],
        timestamp: datetime | None = None,
    ) -> None:
        timestamp = timestamp or datetime.now(UTC)
        asset_ids = [entity.canonical_value for entity in entities if entity.entity_type == "equipment_tag"]
        targets = tuple(EntityRef(id=asset_id, type="asset") for asset_id in asset_ids)
        entity_values = {entity.entity_type: entity.canonical_value for entity in entities}
        findings = tuple(entity.canonical_value for entity in entities if entity.entity_type in {"failure_mode", "severity", "parameter_reading"})
        observations = [
            Observation(
                observation_id=f"obs_doc_{document.document_id}",
                trace_id=document.document_id,
                correlation_id=workspace_id,
                timestamp=timestamp,
                observation_type=ObservationType.DOCUMENT_INGESTION,
                observation_category=ObservationCategory.DOCUMENTATION,
                source_platform="PIA Industrial",
                source_adapter="document_upload",
                version="1.0",
                lifecycle=ObservationLifecycle.PRODUCTION,
                actors=(),
                targets=targets,
                provenance=ObservationProvenance("PIA Industrial", "document_upload", document.document_id),
                context=ObservationContext(metadata={"workspace_id": workspace_id, "document_id": document.document_id, "document_name": document.name}),
                facts=DocumentIngestionFacts(
                    document_id=document.document_id,
                    document_name=document.name,
                    document_type=document.document_type.value,
                    document_format=document.document_format.value,
                    file_hash=document.file_hash,
                    page_count=document.doc_metadata.page_count,
                    chunk_count=len(document.chunks),
                    entity_count=len(entities),
                    ingested_at=timestamp,
                ),
                processing_mode=ProcessingMode.LIVE,
            )
        ]
        if "work_order_id" in entity_values:
            observations.append(self._work_order_observation(workspace_id, document, timestamp, targets, entity_values, findings))
        if "inspection_report_id" in entity_values or document.document_type == DocumentType.INSPECTION_REPORT:
            observations.append(self._inspection_observation(workspace_id, document, timestamp, targets, entity_values, findings))
        if "incident_report_id" in entity_values or "failure_mode" in entity_values:
            observations.append(self._failure_observation(workspace_id, document, timestamp, targets, entity_values, findings))
        for observation in observations:
            try:
                store.append(observation)
            except ValueError:
                continue

    def _work_order_observation(self, workspace_id: str, document: Document, timestamp: datetime, targets: tuple[EntityRef, ...], entities: dict[str, str], findings: tuple[str, ...]) -> Observation:
        return Observation(
            observation_id=f"obs_wo_{document.document_id}",
            trace_id=document.document_id,
            correlation_id=workspace_id,
            timestamp=timestamp,
            observation_type=ObservationType.WORK_ORDER,
            observation_category=ObservationCategory.MAINTENANCE,
            source_platform="PIA Industrial",
            source_adapter="document_upload",
            version="1.0",
            lifecycle=ObservationLifecycle.PRODUCTION,
            actors=(),
            targets=targets,
            provenance=ObservationProvenance("PIA Industrial", "document_upload", document.document_id),
            context=ObservationContext(metadata={"workspace_id": workspace_id, "document_id": document.document_id, "document_name": document.name}),
            facts=MaintenanceActionFacts(
                work_order_id=entities["work_order_id"],
                asset_id=targets[0].id if targets else None,
                description="; ".join(findings),
                status="DEFERRED" if "DEFERRED" in findings or "URGENT" in findings else "COMPLETED",
                findings=findings,
                source_document_id=document.document_id,
            ),
            processing_mode=ProcessingMode.LIVE,
        )

    def _inspection_observation(self, workspace_id: str, document: Document, timestamp: datetime, targets: tuple[EntityRef, ...], entities: dict[str, str], findings: tuple[str, ...]) -> Observation:
        return Observation(
            observation_id=f"obs_ir_{document.document_id}",
            trace_id=document.document_id,
            correlation_id=workspace_id,
            timestamp=timestamp,
            observation_type=ObservationType.INSPECTION_EVENT,
            observation_category=ObservationCategory.INSPECTION,
            source_platform="PIA Industrial",
            source_adapter="document_upload",
            version="1.0",
            lifecycle=ObservationLifecycle.PRODUCTION,
            actors=(),
            targets=targets,
            provenance=ObservationProvenance("PIA Industrial", "document_upload", document.document_id),
            context=ObservationContext(metadata={"workspace_id": workspace_id, "document_id": document.document_id, "document_name": document.name}),
            facts=InspectionFacts(
                inspection_id=entities.get("inspection_report_id", document.document_id),
                asset_id=targets[0].id if targets else None,
                result="DETECTED" if findings else "SATISFACTORY",
                findings=findings,
                source_document_id=document.document_id,
            ),
            processing_mode=ProcessingMode.LIVE,
        )

    def _failure_observation(self, workspace_id: str, document: Document, timestamp: datetime, targets: tuple[EntityRef, ...], entities: dict[str, str], findings: tuple[str, ...]) -> Observation:
        return Observation(
            observation_id=f"obs_fail_{document.document_id}",
            trace_id=document.document_id,
            correlation_id=workspace_id,
            timestamp=timestamp,
            observation_type=ObservationType.FAILURE,
            observation_category=ObservationCategory.RELIABILITY,
            source_platform="PIA Industrial",
            source_adapter="document_upload",
            version="1.0",
            lifecycle=ObservationLifecycle.PRODUCTION,
            actors=(),
            targets=targets,
            provenance=ObservationProvenance("PIA Industrial", "document_upload", document.document_id),
            context=ObservationContext(metadata={"workspace_id": workspace_id, "document_id": document.document_id, "document_name": document.name}),
            facts=FailureEventFacts(
                failure_id=entities.get("incident_report_id", document.document_id),
                asset_id=targets[0].id if targets else None,
                failure_mode=entities.get("failure_mode"),
                description="; ".join(findings),
                source_document_id=document.document_id,
            ),
            processing_mode=ProcessingMode.LIVE,
        )

    def _validate_upload(self, path: Path, original_name: str) -> None:
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        if path.stat().st_size > MAX_UPLOAD_BYTES:
            raise ValueError("File exceeds 25 MB upload limit")
        # Filename sanitization is handled downstream by _safe_filename

    def _safe_filename(self, filename: str) -> str:
        name = Path(filename).name.replace("\\", "_").replace("/", "_")
        return re.sub(r"[^A-Za-z0-9._ -]", "_", name).strip() or "upload.txt"

    def _slug(self, name: str) -> str:
        base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "workspace"
        candidate = base
        counter = 2
        while candidate in self._workspaces:
            candidate = f"{base}-{counter}"
            counter += 1
        return candidate

    def reset_workspace(self, workspace_id: str | None) -> dict[str, Any]:
        """Reset a workspace to empty state, then reload demo if it's the demo workspace."""
        workspace = self.require_workspace(workspace_id)
        # Clear in-memory state
        self._documents[workspace.id] = []
        self._services[workspace.id] = self._build_services(workspace.id)
        self._save_workspace_documents(workspace.id)
        workspace.status = "EMPTY"
        workspace.updated_at = datetime.now(UTC).isoformat()
        self._save_index()
        result: dict[str, Any] = {"workspace_id": workspace.id, "status": "RESET"}
        # If it's the demo workspace, reload the demo dataset
        if workspace.source_kind == "DEMO":
            self.load_demo_dataset(workspace.id)
            result["status"] = "RESET_AND_RELOADED"
            result["documents"] = len(self._documents.get(workspace.id, []))
        return result

    def health_status(self) -> dict[str, Any]:
        """Return runtime health status."""
        workspace_count = len(self._workspaces)
        total_documents = sum(len(docs) for docs in self._documents.values())
        demo_available = "demo-p101" in self._workspaces
        demo_docs = len(self._documents.get("demo-p101", []))
        return {
            "status": "healthy",
            "runtime": "IndustrialWorkspaceRuntime",
            "workspace_count": workspace_count,
            "total_documents": total_documents,
            "persistence": str(self._data_root),
            "persistence_available": self._data_root.exists(),
            "demo_workspace_available": demo_available,
            "demo_document_count": demo_docs,
        }

    def _parse_timestamp(self, value: str) -> datetime:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed


_runtime: IndustrialWorkspaceRuntime | None = None


def get_industrial_runtime() -> IndustrialWorkspaceRuntime:
    global _runtime
    if _runtime is None:
        _runtime = IndustrialWorkspaceRuntime()
    return _runtime
