from app.infrastructure.database.sqlite_provider import get_provider
from app.infrastructure.database.models import MeasurementRecord, EvidenceRecord
import hashlib
import json

class DeterminismValidator:
    @classmethod
    def snapshot(cls):
        """Returns a deterministic hash of the current Operational Store state."""
        provider = get_provider()
        
        # We hash the deterministic fields of all measurements and evidence
        measurements = sorted(provider.query(MeasurementRecord, limit=10000), key=lambda x: x.object_id)
        evidence = sorted(provider.query(EvidenceRecord, limit=10000), key=lambda x: x.object_id)
        
        m_hashes = []
        for m in measurements:
            # exclude timestamps and execution IDs
            payload = {
                "object_id": m.object_id,
                "type": m.identity.object_type,
                "subject_id": m.subject_id,
                "metric_name": m.metric_name,
                "metric_value": m.metric_value,
                "confidence": m.confidence,
            }
            m_hashes.append(payload)
            
        e_hashes = []
        for e in evidence:
            payload = {
                "object_id": e.object_id,
                "type": e.identity.object_type,
                "subject_id": e.subject_id,
                "evidence_type": e.evidence_type,
                "measurement_ids": sorted(e.measurement_ids) if e.measurement_ids else [],
                "confidence": e.confidence,
            }
            e_hashes.append(payload)
            
        state = {
            "measurements": m_hashes,
            "evidence": e_hashes
        }
        
        h = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
        return h, len(measurements), len(evidence), state

    @classmethod
    def compare(cls, state_a, state_b):
        """Compare two states and return a report."""
        passed = True
        report = "DeterminismValidationReport\n\n"
        
        m_a = {m["object_id"]: m for m in state_a["measurements"]}
        m_b = {m["object_id"]: m for m in state_b["measurements"]}
        
        e_a = {e["object_id"]: e for e in state_a["evidence"]}
        e_b = {e["object_id"]: e for e in state_b["evidence"]}
        
        if len(m_a) != len(m_b):
            report += f"Measurements Count Mismatch: {len(m_a)} vs {len(m_b)}\n"
            passed = False
            
        if len(e_a) != len(e_b):
            report += f"Evidence Count Mismatch: {len(e_a)} vs {len(e_b)}\n"
            passed = False
            
        m_mismatches = 0
        for k, v in m_a.items():
            if k not in m_b:
                report += f"Measurement {k} missing in Run B\n"
                m_mismatches += 1
                passed = False
            elif v != m_b[k]:
                report += f"Measurement {k} value mismatch:\n  A: {v}\n  B: {m_b[k]}\n"
                m_mismatches += 1
                passed = False
                
        e_mismatches = 0
        for k, v in e_a.items():
            if k not in e_b:
                report += f"Evidence {k} missing in Run B\n"
                e_mismatches += 1
                passed = False
            elif v != e_b[k]:
                report += f"Evidence {k} value mismatch:\n  A: {v}\n  B: {e_b[k]}\n"
                e_mismatches += 1
                passed = False
                
        report += f"\nTotal Hash Mismatches: {m_mismatches + e_mismatches}\n"
        
        return passed, report
