import asyncio
import logging
from typing import Optional

from app.infrastructure.database.provider import PersistenceProvider
from app.infrastructure.database.models import RepositorySessionRecord
from app.core.sync_engine import SyncEngine, SyncMode, GitHubSourcePlugin

logger = logging.getLogger(__name__)

class SyncWatcher:
    """
    Background daemon that periodically checks watched repositories for new commits.
    If new commits are found, it automatically triggers an incremental sync.
    """
    def __init__(self, provider: PersistenceProvider, sync_engine: SyncEngine):
        self._provider = provider
        self._sync_engine = sync_engine
        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()

    def start(self, interval_seconds: int = 30):
        if self._task is not None:
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(self._watch_loop(interval_seconds))
        logger.info(f"SyncWatcher started with interval {interval_seconds}s")

    async def stop(self):
        if self._task is None:
            return
        self._stop_event.set()
        await self._task
        self._task = None
        logger.info("SyncWatcher stopped")

    async def _watch_loop(self, interval_seconds: int):
        while not self._stop_event.is_set():
            try:
                await self._check_repositories()
            except Exception as e:
                logger.error(f"Error in SyncWatcher loop: {e}")
            
            # Wait for interval or stop event
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=interval_seconds)
            except asyncio.TimeoutError:
                pass # Normal timeout, continue loop

    async def _check_repositories(self):
        # Find all sessions with watch_mode enabled or that were left in "syncing" state (interrupted)
        sessions = self._provider.query(RepositorySessionRecord, limit=100000)
        watched = [
            s for s in sessions 
            if s.metadata.get("watch_mode") is True or s.sync_status == "syncing"
        ]

        if not watched:
            return

        plugin = GitHubSourcePlugin()

        for session in watched:
            try:
                # Check if already running in memory to prevent duplicate spawned jobs
                active_jobs = self._sync_engine.get_active_jobs()
                is_running = any(j.repository == session.repository for j in active_jobs)
                if is_running:
                    continue

                # Fetch only the latest 1 commit to check the HEAD SHA
                commits = await plugin.fetch_commits(
                    repository=session.repository, 
                    branch=session.branch, 
                    limit=1
                )
                
                if not commits:
                    continue
                
                remote_head_sha = commits[0]["sha"]
                
                # If remote is different from local head, OR if it's stuck in "syncing" status, trigger sync
                if remote_head_sha != session.head_commit_sha or session.sync_status == "syncing":
                    if session.sync_status == "syncing":
                        logger.info(f"Resuming stuck sync for {session.repository} on startup.")
                    else:
                        logger.info(f"New commit detected for {session.repository}. Triggering incremental sync.")
                    
                    # Reset status before starting new job so we don't spam
                    session.sync_status = "pending"
                    self._provider.update(session)
                    
                    await self._sync_engine.sync(
                        repository=session.repository,
                        mode=SyncMode.INCREMENTAL,
                        branch=session.branch,
                        commit_limit=-1, # Ingest all new commits
                        workspace_id=session.workspace_id
                    )
            except Exception as e:
                logger.error(f"Failed to check watch status for {session.repository}: {e}")

# Singleton
_watcher: Optional[SyncWatcher] = None

def get_sync_watcher() -> SyncWatcher:
    global _watcher
    if _watcher is None:
        from app.infrastructure.database.sqlite_provider import get_provider
        from app.core.sync_engine import get_sync_engine
        
        _watcher = SyncWatcher(
            provider=get_provider(),
            sync_engine=get_sync_engine()
        )
    return _watcher
