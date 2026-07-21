import uuid
from typing import List
from app.infrastructure.database.models import EvidenceRecord, FactRecord

class FactBuilder:
    def __init__(self, provider):
        self.provider = provider
        
    def build_facts(self, execution_id: str, dataset_id: str) -> List[FactRecord]:
        """
        Transforms EvidenceRecords into immutable FactRecords.
        In the future this resolves conflicts and dedupes.
        For migration validation, it 1:1 maps evidence properties to Facts.
        """
        evidence_records = self.provider.query(EvidenceRecord, limit=10000)
        
        facts = []
        for ev in evidence_records:
            if hasattr(ev, 'properties') and 'raw_output' in ev.properties:
                raw = ev.properties['raw_output']
                for key, val in raw.items():
                    # Deterministic hash based on evidence + key
                    fact_hash = f"{ev.object_id}_{key}_{val}"
                    f = FactRecord(
                        fact_type=key,
                        confidence=ev.confidence,
                        hash=fact_hash, 
                        evidence_ids=[ev.object_id],
                        properties={"value": val}
                    )
                    facts.append(f)
                    self.provider.save(f)
                    
        return facts
