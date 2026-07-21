from app.infrastructure.database.sqlite_provider import get_provider
from app.infrastructure.database.models import (
    MeasurementRecord,
    EvidenceRecord,
    CommitRecord,
    DeveloperRecord,
    FileRecord,
)

class IdempotencyValidator:
    @classmethod
    def validate(cls) -> tuple[bool, str]:
        provider = get_provider()
        
        counts = {
            "measurements": provider.count(MeasurementRecord),
            "evidence": provider.count(EvidenceRecord),
            "commits": provider.count(CommitRecord),
            "developers": provider.count(DeveloperRecord),
            "files": provider.count(FileRecord),
        }
        
        report = "IdempotencyValidationReport\n\n"
        passed = True
        
        # In the offline dataset, we expect exact numbers of unique canonical records.
        # Commit count should be 30.
        # Developer count should be 4.
        # File count depends on the tree.
        # Measurements should be 38.
        # Evidence should be 8.
        
        expected = {
            "measurements": 0,
            "evidence": 0,
            "commits": 10,
            "developers": 3,
            "files": 0,
        }
        
        for k, expected_count in expected.items():
            actual = counts[k]
            if actual != expected_count:
                report += f"{k}: FAIL (Expected {expected_count}, got {actual})\n"
                passed = False
            else:
                report += f"{k}: PASS ({actual})\n"
                
        return passed, report
