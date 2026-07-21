from typing import Any
import json
import uuid

from app.infrastructure.database.provider import PersistenceProvider
from app.infrastructure.database.models import (
    GlobalIdentity,
    MeasurementRecord,
    EvidenceRecord,
    ReasoningRecord,
    ExecutionRecord
)
from app.core.api.contracts import RuntimePipelineResult


class PersistenceAdapter:
    """
    Decomposes a PlatformResult into canonical operational store records
    and persists them atomically.
    """
    def __init__(self, provider: PersistenceProvider):
        self._provider = provider

    def persist(
        self,
        result: RuntimePipelineResult,
        workspace_id: str,
        repository_session_id: str,
        execution_id: str,
        query: str = "",
        intent: str = "runtime_execution"
    ) -> ExecutionRecord:
        """
        Persists the final pipeline output into the Operational Store.
        Uses a single transaction to ensure consistency.
        """
        ctx = result.context
        
        measurements = getattr(ctx, "measurements", []) or []
        evidence_pkg = getattr(ctx, "evidence_package", None)
        evidence_list = evidence_pkg.evidence if evidence_pkg and hasattr(evidence_pkg, "evidence") else []
        
        print(f"[PersistenceAdapter] Context has {len(measurements)} measurements")
        print(f"[PersistenceAdapter] Context has {len(evidence_list)} evidence")
        
        with self._provider.transaction():
            # 1. Persist Measurements
            measurement_ids = []
            for m in measurements:
                metric_name = m.definition.id if hasattr(m, "definition") and hasattr(m.definition, "id") else getattr(m, "metric", "unknown")
                subject_id = m.provenance.target_entity if hasattr(m, "provenance") and getattr(m.provenance, "target_entity", None) else "unknown"
                
                # Deterministic ID based on identity components
                payload = f"measurement:{metric_name}:{subject_id}"
                det_id = str(uuid.uuid5(uuid.NAMESPACE_OID, payload))
                
                m_record = MeasurementRecord(
                    identity=GlobalIdentity(
                        object_id=det_id,
                        object_type="measurement",
                        workspace_id=workspace_id,
                        execution_id=execution_id,
                    ),
                    repository_session_id=repository_session_id,
                    metric_name=metric_name,
                    metric_value=m.value,
                    confidence=m.confidence,
                    subject_id=subject_id,
                    subject_type=m.provenance.target_entity_type if hasattr(m, "provenance") and getattr(m.provenance, "target_entity_type", None) else "unknown",
                    metadata={"metadata": dict(m.metadata)} if hasattr(m, "metadata") else {}
                )
                
                existing = self._provider.get_by_id(MeasurementRecord, det_id)
                if existing:
                    self._provider.update(m_record)
                else:
                    self._provider.insert(m_record)
                measurement_ids.append(m_record.object_id)
                
            # 2. Persist Evidence
            evidence_ids = []
            for e in evidence_list:
                evidence_type = e.category if hasattr(e, "category") else "unknown"
                e_subject_id = e.metadata.get("target_entity", "unknown") if hasattr(e, "metadata") else "unknown"
                
                payload = f"evidence:{evidence_type}:{e_subject_id}"
                det_id = str(uuid.uuid5(uuid.NAMESPACE_OID, payload))
                
                e_record = EvidenceRecord(
                    identity=GlobalIdentity(
                        object_id=det_id,
                        object_type="evidence",
                        workspace_id=workspace_id,
                        execution_id=execution_id,
                    ),
                    repository_session_id=repository_session_id,
                    evidence_type=evidence_type,
                    summary=getattr(e, "description", getattr(e, "name", "")),
                    confidence=getattr(e, "confidence", 0.0),
                    measurement_ids=list(getattr(getattr(e, "provenance", None), "measurement_ids", [])),
                    subject_id=e_subject_id,
                    subject_type=e.metadata.get("target_entity_type", "unknown") if hasattr(e, "metadata") else "unknown",
                    metadata={"metadata": dict(e.metadata)} if hasattr(e, "metadata") else {}
                )
                
                existing = self._provider.get_by_id(EvidenceRecord, det_id)
                if existing:
                    self._provider.update(e_record)
                else:
                    self._provider.insert(e_record)
                evidence_ids.append(e_record.object_id)
                
            # 3. Persist Reasoning
            reasoning_ids = []
            for r in getattr(ctx, "reasoning_results", []) or []:
                r_record = ReasoningRecord(
                    identity=GlobalIdentity(
                        object_type="reasoning",
                        workspace_id=workspace_id,
                        execution_id=execution_id,
                    ),
                    repository_session_id=repository_session_id,
                    execution_id=execution_id,
                    reasoning_type="agent_reasoning",
                    conclusion=str(r), # or serialize
                )
                self._provider.insert(r_record)
                reasoning_ids.append(r_record.object_id)

            # 4. Graph structure persistence (Optional, but graph usually rebuilt via projections. 
            # We can log graph size in execution stats)
            nodes = len(ctx.knowledge_graph.nodes) if getattr(ctx, "knowledge_graph", None) else 0
            edges = len(ctx.knowledge_graph.edges) if getattr(ctx, "knowledge_graph", None) else 0

            # 5. Persist Execution Record
            total_duration = sum(s.duration for s in result.completed_stages)
            stage_latencies = {s.name: s.duration for s in result.completed_stages}

            execution_record = ExecutionRecord(
                identity=GlobalIdentity(
                    object_type="execution",
                    workspace_id=workspace_id,
                    execution_id=execution_id,
                ),
                repository_session_id=repository_session_id,
                query=query,
                intent=intent,
                status="success" if not result.errors else "failed",
                measurement_ids=measurement_ids,
                evidence_ids=evidence_ids,
                reasoning_ids=reasoning_ids,
                total_latency_ms=total_duration * 1000,
                stage_latencies=stage_latencies,
                metadata={
                    "nodes": nodes,
                    "edges": edges,
                    "measurements_generated": len(measurement_ids),
                    "evidence_generated": len(evidence_ids),
                    "algorithms_executed": len(result.completed_stages),
                    "errors": result.errors
                }
            )
            self._provider.insert(execution_record)
            
            return execution_record
