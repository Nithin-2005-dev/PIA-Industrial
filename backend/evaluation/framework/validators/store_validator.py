from app.infrastructure.database.sqlite_provider import get_provider
from app.infrastructure.database.models import (
    MeasurementRecord, 
    EvidenceRecord, 
    ExecutionRecord, 
    WorkspaceRecord, 
    RepositorySessionRecord
)
import math

class StoreValidator:
    @classmethod
    def validate(cls):
        provider = get_provider()
        
        results = {
            "Measurements": "PASS",
            "Evidence": "PASS",
            "Executions": "PASS",
            "Workspaces": "PASS",
            "Repositories": "PASS"
        }
        
        errors = []

        def assert_identity(record, name):
            if not getattr(record, "identity", None):
                errors.append(f"{name} {record.object_id}: Missing GlobalIdentity")
                return False
            if not record.identity.object_id:
                errors.append(f"{name} {record.object_id}: Missing object_id")
                return False
            if not record.identity.version:
                errors.append(f"{name} {record.object_id}: Missing version")
            if not record.identity.execution_id and name != "WorkspaceRecord":
                # Workspace might not have execution_id, but the rest should.
                if name != "RepositorySessionRecord":
                    errors.append(f"{name} {record.object_id}: Missing execution_id")
            if not record.identity.workspace_id:
                if name != "WorkspaceRecord":
                    errors.append(f"{name} {record.object_id}: Missing workspace_id")
            if not record.identity.created_at:
                errors.append(f"{name} {record.object_id}: Missing created_at")
            return True

        # 1. Executions
        executions = provider.query(ExecutionRecord, limit=1000)
        for ex in executions:
            if not assert_identity(ex, "ExecutionRecord"):
                results["Executions"] = "FAIL"

        # 2. Measurements
        measurements = provider.query(MeasurementRecord, limit=5000)
            
        for m in measurements:
            if not assert_identity(m, "MeasurementRecord"):
                results["Measurements"] = "FAIL"
                continue
                
            if m.metric_value is None or math.isnan(m.metric_value) or math.isinf(m.metric_value):
                errors.append(f"Measurement {m.object_id}: Invalid metric_value {m.metric_value}")
                results["Measurements"] = "FAIL"
                
            if m.confidence is None or math.isnan(m.confidence) or math.isinf(m.confidence):
                errors.append(f"Measurement {m.object_id}: Invalid confidence {m.confidence}")
                results["Measurements"] = "FAIL"
                
            if not m.subject_id:
                errors.append(f"Measurement {m.object_id}: Missing subject_id")
                results["Measurements"] = "FAIL"

        # 3. Evidence
        evidence = provider.query(EvidenceRecord, limit=5000)
        for e in evidence:
            if not assert_identity(e, "EvidenceRecord"):
                results["Evidence"] = "FAIL"
                continue
                
            if not e.measurement_ids or not isinstance(e.measurement_ids, list):
                errors.append(f"Evidence {e.object_id}: Missing or invalid measurement_ids")
                results["Evidence"] = "FAIL"
                
            if not e.subject_id:
                errors.append(f"Evidence {e.object_id}: Missing subject_id")
                results["Evidence"] = "FAIL"
                
            if not e.evidence_type:
                errors.append(f"Evidence {e.object_id}: Missing evidence_type")
                results["Evidence"] = "FAIL"
                
            if e.confidence is None or math.isnan(e.confidence) or math.isinf(e.confidence):
                errors.append(f"Evidence {e.object_id}: Invalid confidence {e.confidence}")
                results["Evidence"] = "FAIL"

        # 4. Workspaces & Repositories
        workspaces = provider.query(WorkspaceRecord, limit=100)
        for w in workspaces:
            if not assert_identity(w, "WorkspaceRecord"):
                results["Workspaces"] = "FAIL"
                
        repos = provider.query(RepositorySessionRecord, limit=100)
        for r in repos:
            if not assert_identity(r, "RepositorySessionRecord"):
                results["Repositories"] = "FAIL"
                
        report = "OperationalStoreValidationReport\n\n"
        for k, v in results.items():
            report += f"{k}\n{v}\n\n"
            
        if errors:
            report += "Errors:\n" + "\n".join(errors[:20]) + ("\n...and more" if len(errors)>20 else "")
            
        passed = all(v == "PASS" for v in results.values())
        return passed, report
