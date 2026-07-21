import pytest
import os
import asyncio
from evaluation.framework.validators.store_validator import StoreValidator
from app.core.sync_engine import get_sync_engine, SyncMode
import app.core.core_modules
from app.infrastructure.github.adapter import GitHubAdapter
from app.infrastructure.github.source import OfflineSnapshotSource
from app.infrastructure.database.sqlite_provider import get_provider

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
        for c in self.source.get_commits("facebook", "react"):
            commits.append({
                "sha": c.get("sha", ""),
                "message": (c.get("commit", {}).get("message", "") or "")[:500],
                "author_email": (c.get("commit", {}).get("author", {}) or {}).get("email", ""),
                "author_name": (c.get("commit", {}).get("author", {}) or {}).get("name", ""),
                "timestamp": (c.get("commit", {}).get("author", {}) or {}).get("date", ""),
                "additions": (c.get("stats", {}) or {}).get("additions", 0),
                "deletions": (c.get("stats", {}) or {}).get("deletions", 0),
            })
        return commits[:limit]

    async def fetch_file_tree(self, repository, commit_sha, **kwargs):
        return []

    async def get_rate_limit(self):
        return {"remaining": 60, "limit": 60, "reset_at": 0}


def test_operational_store_validation():
    asyncio.run(run_operational_store_validation())

async def run_operational_store_validation():
    # 1. Clear database to ensure pristine state
    db_files = ["pia_store.db", "pia_store.db-wal", "pia_store.db-shm", "pia_events.db", "pia_events.db-wal", "pia_events.db-shm"]
    for dbf in db_files:
        if os.path.exists(dbf):
            try:
                os.remove(dbf)
            except Exception:
                pass


    # 2. Patch GitHub Adapter to use offline dataset
    import app.core.sync_engine
    app.core.sync_engine.GitHubSourcePlugin = MockGitHubSourcePlugin
    app.core.core_modules.GitHubAdapterFactory = MockGitHubSourcePlugin # just in case
    
    # 3. Run Sync Engine
    sync = get_sync_engine()
    job = await sync.sync('facebook/react', mode=SyncMode.FULL, commit_limit=30, github_token="offline")
    while job.status in ('pending', 'running'):
        await asyncio.sleep(1)
        
    if job.status != 'completed':
        print(f"Sync failed with error: {getattr(job, 'error', 'Unknown Error')}")
    assert job.status == 'completed'
    
    # 4. Validate
    passed, report = StoreValidator.validate()
    print("\n" + report)
    assert passed, "Operational Store Validation Failed. See report."
