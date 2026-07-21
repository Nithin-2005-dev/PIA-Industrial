from typing import Any
from app.infrastructure.database.sqlite_provider import get_provider
from app.infrastructure.database.models import CommitRecord

class IncrementalValidator:
    @classmethod
    def validate(cls, timestamp_between_syncs: str, full_count: int) -> tuple[bool, str]:
        provider = get_provider()
        
        all_commits = provider.query(CommitRecord, limit=10000)
        
        updated_commits = [
            m for m in all_commits 
            if (m.identity.updated_at and m.identity.updated_at > timestamp_between_syncs) or 
               (m.identity.created_at and m.identity.created_at > timestamp_between_syncs)
        ]
        
        updated_count = len(updated_commits)
        
        report = "IncrementalSyncValidationReport\n\n"
        report += f"Total Commits: {len(all_commits)}\n"
        report += f"Updated/Inserted Commits in Incremental Sync: {updated_count}\n\n"
        
        passed = True
        
        if updated_count == 0:
            report += "FAIL: No commits were updated or inserted during the incremental sync.\n"
            passed = False
        elif updated_count >= full_count:
            report += f"FAIL: Full recompute detected! Expected a small fraction of {full_count}, but {updated_count} were updated.\n"
            passed = False
        else:
            report += f"PASS: Only {updated_count} commits were updated, confirming incremental behavior.\n"
            
        return passed, report
            
        return passed, report
