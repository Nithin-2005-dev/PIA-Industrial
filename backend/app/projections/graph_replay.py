from typing import Dict, Any, Tuple
from app.infrastructure.database.sqlite_provider import get_provider
from app.infrastructure.database.models import KnowledgeGraphProjectionRecord
from app.projections.knowledge_graph_builder import KnowledgeGraphProjectionBuilder

class KnowledgeGraphReplayEngine:
    def __init__(self):
        self.provider = get_provider()

    def replay(self, expected_projection_id: str) -> Dict[str, Any]:
        original_proj = None
        records = self.provider.query(KnowledgeGraphProjectionRecord, limit=1000)
        for r in records:
            if r.projection_id == expected_projection_id:
                original_proj = r
                break
                
        if not original_proj:
            raise ValueError(f"Projection {expected_projection_id} not found.")

        builder = KnowledgeGraphProjectionBuilder(self.provider)
        dataset_id = getattr(original_proj.identity, 'dataset_id', getattr(original_proj, 'dataset_id', None))
        execution_id = getattr(original_proj.identity, 'execution_id', getattr(original_proj, 'execution_id', None))
        new_proj = builder.build_projection(dataset_id=dataset_id, execution_id=execution_id)
        
        report = {
            "expected_projection_hash": original_proj.projection_hash,
            "actual_projection_hash": new_proj.projection_hash,
            "expected_measurement_hash": original_proj.measurement_hash,
            "actual_measurement_hash": new_proj.measurement_hash,
            "expected_evidence_hash": original_proj.evidence_hash,
            "actual_evidence_hash": new_proj.evidence_hash,
            "match": False,
            "diverged_stage": None
        }
        
        if report["actual_measurement_hash"] != report["expected_measurement_hash"]:
            report["diverged_stage"] = "Measurements"
        elif report["actual_evidence_hash"] != report["expected_evidence_hash"]:
            report["diverged_stage"] = "Evidence"
        elif report["actual_projection_hash"] != report["expected_projection_hash"]:
            report["diverged_stage"] = "Graph"
        else:
            report["match"] = True
            
        return report
