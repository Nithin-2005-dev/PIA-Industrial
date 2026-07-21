import hashlib
import json
import datetime
import uuid
from typing import Dict, List, Optional
from app.infrastructure.database.sqlite_provider import SQLiteProvider, get_provider
from app.infrastructure.database.models import MeasurementRecord, EvidenceRecord, KnowledgeGraphProjectionRecord, GlobalIdentity

class KnowledgeGraphProjectionBuilder:
    def __init__(self, provider: SQLiteProvider = None):
        self._provider = provider or get_provider()

    def build_projection(self, dataset_id: Optional[str] = None, execution_id: Optional[str] = None) -> KnowledgeGraphProjectionRecord:
        start_time = datetime.datetime.now()
        nodes = {}
        edges = []
        
        measurements = self._provider.query(MeasurementRecord, limit=10000)
        evidence = self._provider.query(EvidenceRecord, limit=10000)
        
        # Canonical Node Types
        canonical = {"MEASUREMENT", "EVIDENCE", "DEVELOPER", "FILE", "MODULE", "REPOSITORY", "COMMIT"}
        
        for m in measurements:
            m_id = str(m.object_id)
            nodes[m_id] = {
                "id": m_id,
                "type": "MEASUREMENT",
                "attributes": {
                    "metric_name": m.metric_name,
                    "metric_value": m.metric_value,
                    "confidence": m.confidence,
                    "subject_id": m.subject_id,
                    "subject_type": m.subject_type,
                    "provenance": m_id
                }
            }
            
            if m.subject_id and m.subject_type and str(m.subject_type).upper() in canonical:
                target_id = str(m.subject_id)
                if target_id not in nodes:
                    nodes[target_id] = {"id": target_id, "type": str(m.subject_type).upper(), "attributes": {"provenance": m_id}}
                
                edges.append({
                    "source": m_id,
                    "target": target_id,
                    "type": "MEASURES",
                    "provenance": m_id,
                    "confidence": m.confidence
                })

        for e in evidence:
            e_id = str(e.object_id)
            nodes[e_id] = {
                "id": e_id,
                "type": "EVIDENCE",
                "attributes": {
                    "evidence_type": e.evidence_type,
                    "summary": e.summary,
                    "confidence": e.confidence,
                    "provenance": e_id
                }
            }
            
            if e.subject_id and e.subject_type and str(e.subject_type).upper() in canonical:
                target_id = str(e.subject_id)
                if target_id not in nodes:
                    nodes[target_id] = {"id": target_id, "type": str(e.subject_type).upper(), "attributes": {"provenance": e_id}}
                
                edges.append({
                    "source": e_id,
                    "target": target_id,
                    "type": "SUPPORTS",
                    "provenance": e_id,
                    "confidence": e.confidence
                })
            
            if hasattr(e, "measurement_ids") and e.measurement_ids:
                for m_id in e.measurement_ids:
                    if m_id in nodes:
                        edges.append({
                            "source": m_id,
                            "target": e_id,
                            "type": "SYNTHESIZES_TO",
                            "provenance": e_id,
                            "confidence": e.confidence
                        })

        node_list = list(nodes.values())
        
        # Sort nodes and edges for deterministic hashing
        node_list.sort(key=lambda x: x["id"])
        edges.sort(key=lambda x: f"{x['source']}-{x['target']}-{x['type']}")

        # Compute Stage Hashes
        m_dicts = [{"id": m.object_id, "metric": m.metric_name, "value": m.metric_value} for m in measurements]
        m_dicts.sort(key=lambda x: x["id"])
        m_hash = hashlib.sha256(json.dumps(m_dicts, sort_keys=True).encode('utf-8')).hexdigest()
        
        e_dicts = [{"id": e.object_id, "type": e.evidence_type, "confidence": e.confidence} for e in evidence]
        e_dicts.sort(key=lambda x: x["id"])
        e_hash = hashlib.sha256(json.dumps(e_dicts, sort_keys=True).encode('utf-8')).hexdigest()

        # Compute Content-Addressed Hash (SHA-256)
        canonical_str = json.dumps({"nodes": node_list, "edges": edges}, sort_keys=True)
        projection_hash = hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()
        
        duration = (datetime.datetime.now() - start_time).total_seconds() * 1000.0

        projection = KnowledgeGraphProjectionRecord(
            identity=GlobalIdentity(object_type="projection"),
            projection_id=str(uuid.uuid4()),
            projection_hash=projection_hash,
            measurement_hash=m_hash,
            evidence_hash=e_hash,
            dataset_id=dataset_id,
            execution_id=execution_id,
            node_count=len(node_list),
            edge_count=len(edges),
            build_duration_ms=duration,
            nodes=node_list,
            edges=edges
        )
        
        # Calculate Build-Time Analytics
        from app.projections.graph_analytics import KnowledgeGraphAnalytics
        analytics = KnowledgeGraphAnalytics(projection).compute_build_time_analytics()
        projection.statistics = analytics
        
        # Run Validation
        from evaluation.framework.validators.layered_validators import LayeredValidator
        validation_report = LayeredValidator.validate(projection)
        projection.validation_report = validation_report
        
        # Persist Projection to Operational Store
        self._provider.insert(projection)
        
        return projection
