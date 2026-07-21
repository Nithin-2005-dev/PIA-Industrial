import pytest
import os
import asyncio
from datetime import datetime, timezone
from evaluation.framework.validators.incremental_validator import IncrementalValidator
from app.core.sync_engine import get_sync_engine, SyncMode
import app.core.core_modules
from app.infrastructure.github.source import OfflineSnapshotSource
from app.infrastructure.database.sqlite_provider import get_provider
from app.infrastructure.database.models import MeasurementRecord

class MockGitHubSourcePlugin:
    source_id = "github"
    def __init__(self, token=None):
        self.source = OfflineSnapshotSource("evaluation/datasets/v1/facebook_react")
        
    def fetch_repository_metadata(self, repository: str) -> dict:
        data = self.source.get_repository("facebook", "react")
        return {
            "name": data.get("name", ""),
            "full_name": data.get("full_name", repository),
            "description": data.get("description", ""),
            "default_branch": data.get("default_branch", "main"),
            "language": data.get("language", ""),
            "topics": data.get("topics", []),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "created_at": data.get("created_at", ""),
            "pushed_at": data.get("pushed_at", ""),
            "size_kb": data.get("size", 0),
        }

    async def fetch_commits(self, repository: str, branch: str, limit: int = 100, since_sha=None, **kwargs):
        commits = []
        raw_commits = list(self.source.get_commits("facebook", "react"))
        raw_commits.reverse() # Oldest first
        
        for c in raw_commits:
            commits.append({
                "sha": c.get("sha", ""),
                "message": (c.get("commit", {}).get("message", "") or "")[:500],
                "author_email": (c.get("commit", {}).get("author", {}) or {}).get("email", ""),
                "author_name": (c.get("commit", {}).get("author", {}) or {}).get("name", ""),
                "timestamp": (c.get("commit", {}).get("author", {}) or {}).get("date", ""),
                "additions": (c.get("stats", {}) or {}).get("additions", 0),
                "deletions": (c.get("stats", {}) or {}).get("deletions", 0),
            })
            
        if since_sha:
            idx = next((i for i, c in enumerate(commits) if c["sha"] == since_sha), -1)
            if idx != -1:
                commits = commits[idx+1:]
                
        return commits[:limit]

    async def fetch_file_tree(self, repository, commit_sha, **kwargs):
        return []

    async def get_rate_limit(self):
        return {"remaining": 60, "limit": 60, "reset_at": 0}


def test_incremental():
    asyncio.run(run_incremental())

async def run_incremental():
    import app.core.sync_engine
    app.core.sync_engine.GitHubSourcePlugin = MockGitHubSourcePlugin
    
    # 1. Clear DB
    import app.infrastructure.database.sqlite_provider
    if app.infrastructure.database.sqlite_provider._provider:
        app.infrastructure.database.sqlite_provider._provider.close()
        app.infrastructure.database.sqlite_provider._provider = None

    db_files = ["pia_store.db", "pia_store.db-wal", "pia_store.db-shm", "pia_events.db", "pia_events.db-wal", "pia_events.db-shm"]
    for dbf in db_files:
        if os.path.exists(dbf):
            try:
                os.remove(dbf)
            except Exception:
                pass
                
    # DEBUG
    from app.infrastructure.database.models import CommitRecord
    print("COUNT AFTER CLEAR:", get_provider().count(CommitRecord))

    sync = get_sync_engine()
    
    # 2. Run Full Sync up to commit_limit=5
    print("Running Full Sync (limit=5)...")
    job = await sync.sync('facebook/react', mode=SyncMode.FULL, commit_limit=5, github_token="offline")
    while job.status in ('pending', 'running'):
        await asyncio.sleep(1)
    
    provider = get_provider()
    from app.infrastructure.database.models import CommitRecord
    full_count = provider.count(CommitRecord)
    
    # Capture timestamp
    timestamp_between_syncs = datetime.now(timezone.utc).isoformat() + "Z"
    
    print(f"Timestamp between syncs: {timestamp_between_syncs}")
    await asyncio.sleep(1) # Ensure time difference
    
    # 3. Run Incremental Sync up to commit_limit=1 (1 new commit)
    print("Running Incremental Sync (limit=1)...")
    job = await sync.sync('facebook/react', mode=SyncMode.INCREMENTAL, commit_limit=1, github_token="offline")
    while job.status in ('pending', 'running'):
        await asyncio.sleep(1)
        
    # 4. Validate
    print("Validating Incremental Sync...")
    passed, report = IncrementalValidator.validate(timestamp_between_syncs, full_count)
    with open("incremental_report.txt", "w") as f:
        f.write(report)
    print("\n" + report)
    assert passed, "Incremental Validation Failed. See report."
