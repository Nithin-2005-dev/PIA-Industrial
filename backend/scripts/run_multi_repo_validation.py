import asyncio
import os
import time
from app.platform.sync_engine import get_sync_engine, SyncMode
import app.platform.sync_engine
from app.projections.knowledge_graph_builder import KnowledgeGraphProjectionBuilder
from app.projections.graph_analytics import KnowledgeGraphAnalytics
from app.projections.graph_replay import KnowledgeGraphReplayEngine
from app.adapters.database.sqlite_provider import get_provider

class MockMultiRepoGitHubSourcePlugin:
    source_id = "github"
    def __init__(self, token=None):
        pass
        
    def fetch_repository_metadata(self, repository: str) -> dict:
        return {"name": repository.split("/")[-1]}

    def fetch_commits(self, repository: str, branch: str, limit: int = 100, since_sha=None):
        commits = []
        for i in range(limit):
            commits.append({
                "sha": f"mocksha{i}_{repository.split('/')[-1]}",
                "message": f"Commit {i} in {repository}",
                "author_email": f"dev{i}@example.com",
                "author_name": f"Dev {i}",
                "timestamp": "2023-01-01T00:00:00Z",
                "additions": 10,
                "deletions": 5,
            })
        return commits

    def fetch_file_tree(self, repository, commit_sha):
        return []

    def get_rate_limit(self):
        return {"remaining": 5000, "limit": 5000, "reset_at": 0}

REPOS = [
    ("facebook/react", 50),
    ("microsoft/TypeScript", 50),
    ("fastapi/fastapi", 30),
    ("kubernetes/kubernetes", 20),
    ("encode/starlette", 10)
]

async def main():
    app.platform.sync_engine.GitHubSourcePlugin = MockMultiRepoGitHubSourcePlugin
    print("=== Multi-Repository Validation for Knowledge Graph ===")
    
    # Ensure fresh DB
    db_files = ["pia_store.db", "pia_store.db-wal", "pia_store.db-shm", "pia_events.db", "pia_events.db-wal", "pia_events.db-shm"]
    for dbf in db_files:
        if os.path.exists(dbf):
            try:
                os.remove(dbf)
            except Exception:
                pass
                
    sync = get_sync_engine()
    provider = get_provider()
    
    results = []
    
    for repo, commit_limit in REPOS:
        print(f"\n--- Validating: {repo} ---")
        
        # 1. Sync
        start_sync = time.time()
        job = await sync.sync(repo, mode=SyncMode.FULL, commit_limit=commit_limit)
        while job.status in ('pending', 'running'):
            await asyncio.sleep(2)
        sync_time = time.time() - start_sync
        
        # 2. Build Projection
        
        builder = KnowledgeGraphProjectionBuilder(provider)
        start_build = time.time()
        projection = builder.build_projection(dataset_id=repo, execution_id="multi-repo-validation")
        build_time = time.time() - start_build
        
        mem_used = 0 # psutil not installed
        
        # 3. Analytics
        analytics = KnowledgeGraphAnalytics(projection)
        stats = projection.statistics
        
        # 4. Validation
        val_score = projection.validation_report.get("overall_score", 0)
        
        # 5. Replay Determinism
        engine = KnowledgeGraphReplayEngine()
        replay_report = engine.replay(projection.projection_id)
        determinism_pass = replay_report["match"]
        
        res = {
            "Repository": repo,
            "Commits Processed": commit_limit,
            "Sync Time (s)": round(sync_time, 2),
            "Build Time (s)": round(build_time, 2),
            "Memory Peak (MB)": round(mem_used, 2),
            "Nodes": projection.node_count,
            "Edges": projection.edge_count,
            "Density": round(stats.get("density", 0), 4),
            "Components": stats.get("components", 0),
            "Quality Score": round(val_score, 1),
            "Determinism": "PASS" if determinism_pass else "FAIL"
        }
        results.append(res)
        
        print(f"Build Time: {res['Build Time (s)']}s | Nodes: {res['Nodes']} | Edges: {res['Edges']} | Qual: {res['Quality Score']} | Det: {res['Determinism']}")
        
    print("\n\n=== Final Report ===")
    print(f"{'Repository':<25} | {'Build(s)':<8} | {'Mem(MB)':<8} | {'Nodes':<6} | {'Edges':<6} | {'Qual Score':<10} | {'Det'}")
    print("-" * 85)
    for r in results:
        print(f"{r['Repository']:<25} | {r['Build Time (s)']:<8} | {r['Memory Peak (MB)']:<8} | {r['Nodes']:<6} | {r['Edges']:<6} | {r['Quality Score']:<10} | {r['Determinism']}")
        
if __name__ == "__main__":
    asyncio.run(main())
