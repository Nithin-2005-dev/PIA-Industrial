from evaluation.framework.validators.layered_validators import LayeredValidator
from app.core.sync_engine import get_sync_engine, SyncMode
from app.infrastructure.github.source import OfflineSnapshotSource
from app.projections.knowledge_graph_builder import KnowledgeGraphProjectionBuilder
import app.core.core_modules
import asyncio
import os
import pytest

class MockGitHubSourcePlugin:
    source_id = "github"
    def __init__(self, token=None):
        self.source = OfflineSnapshotSource("evaluation/datasets/v1/facebook_react")
        
    def fetch_repository_metadata(self, repository: str) -> dict:
        return {"name": "react"}

    async def fetch_commits(self, repository: str, branch: str, limit: int = 100, since_sha=None, **kwargs):
        commits = []
        raw_commits = list(self.source.get_commits("facebook", "react"))
        raw_commits.reverse()
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


def test_graph_projection():
    asyncio.run(run_graph_projection())

async def run_graph_projection():
    app.core.sync_engine.GitHubSourcePlugin = MockGitHubSourcePlugin
    
    # 1. Clear DB
    db_files = ["pia_store.db", "pia_store.db-wal", "pia_store.db-shm", "pia_events.db", "pia_events.db-wal", "pia_events.db-shm"]
    for dbf in db_files:
        if os.path.exists(dbf):
            try:
                os.remove(dbf)
            except Exception:
                pass
                
    sync = get_sync_engine()
    
    # 2. Run Full Sync
    print("Running Full Sync...")
    job = await sync.sync('facebook/react', mode=SyncMode.FULL, commit_limit=5, github_token="offline")
    while job.status in ('pending', 'running'):
        await asyncio.sleep(1)
        
    # 3. Build Graph
    print("Building Knowledge Graph Projection...")
    builder = KnowledgeGraphProjectionBuilder()
    graph = builder.build_projection()
    
    # 4. Validate
    print("Validating Graph Quality...")
    report = LayeredValidator.validate(graph)
    print(f"Overall Score: {report['overall_score']}")
    for c in report["contracts"]:
        print(f"[{c['status']}] {c['name']} (Score: {c['score']})")
    assert report["passed"], "Graph Validation Failed."
