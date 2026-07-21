"""
PIA Source Sync Engine.

Implements the full ingestion pipeline:

    GitHub (GitHubSourcePlugin)
         ↓
    Repository Events
         ↓
    Immutable Event Store  ←── parallel write
         ↓
    Operational Store (canonical records)
         ↓
    Projection Engine (incremental rebuild)
         ↓
    Developer Console (via WebSocket events)

Supports four synchronization modes:
    - Full Sync: ingest all history up to commit_limit
    - Incremental Sync: only new commits since last_synced_sha
    - Replay Dataset: re-ingest from an offline snapshot
    - Rebuild Projections: skip ingestion, just rebuild all projections

Sync state is persisted in the Operational Store (RepositorySessionRecord)
so interrupted syncs can be resumed.

GitHub is treated as a SOURCE PLUGIN. The kernel never imports github-specific
code — it calls SourcePlugin.fetch_*() methods. Swap for GitLabPlugin,
LocalGitPlugin, etc. with no engine changes.
"""
from __future__ import annotations

import asyncio
import datetime
import time
import uuid
import os
import logging
logger = logging.getLogger(__name__)
import subprocess
import threading
import shutil
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from app.infrastructure.database.provider import PersistenceProvider
from app.infrastructure.database.models import (
    RepositorySessionRecord, GlobalIdentity,
    CommitRecord, DeveloperRecord, FileRecord,
    WorkspaceRecord,
)
from app.core.events.store import ImmutableEventStore, StoreEvent, EventType


# ─────────────────────────────────────────────────────────
# Sync Modes
# ─────────────────────────────────────────────────────────

class SyncMode(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    REPLAY_DATASET = "replay_dataset"
    REBUILD_PROJECTIONS = "rebuild_projections"


# ─────────────────────────────────────────────────────────
# Sync Job (tracks a single sync operation)
# ─────────────────────────────────────────────────────────

class SyncStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class SyncJob:
    """A single sync job instance. Lives in memory; persisted via events."""
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    repository: str = ""
    repository_session_id: str = ""
    workspace_id: str = ""
    sync_mode: SyncMode = SyncMode.FULL
    source_plugin: str = "github"
    status: SyncStatus = SyncStatus.PENDING
    commit_limit: int = 100
    branch: str = "main"
    github_token: Optional[str] = None

    # Progress
    commits_total: int = 0
    commits_processed: int = 0
    developers_found: int = 0
    files_processed: int = 0
    objects_added: int = 0
    objects_updated: int = 0
    objects_removed: int = 0

    # State
    current_operation: str = ""
    last_commit_sha: str = ""
    api_calls_made: int = 0
    api_rate_limit_remaining: int = 5000

    # Timing
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: float = 0.0
    error: Optional[str] = None

    # Retry / cancellation
    retry_count: int = 0
    max_retries: int = 3
    cancellation_requested: bool = False


# ─────────────────────────────────────────────────────────
# Source Plugin Protocol
# ─────────────────────────────────────────────────────────

class SourcePlugin:
    """
    Abstract source adapter. Implement one per SCM system.
    The SyncEngine calls these methods — it never knows it's talking to GitHub.
    """
    source_id: str = "abstract"

    def fetch_repository_metadata(self, repository: str) -> Dict[str, Any]:
        raise NotImplementedError

    async def fetch_commits(self, repository: str, branch: str,
                      limit: int = 100, since_sha: Optional[str] = None,
                      progress_callback: Optional[Callable[[str], Any]] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def fetch_file_tree(self, repository: str, commit_sha: str,
                              progress_callback: Optional[Callable[[str], Any]] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get_rate_limit(self) -> Dict[str, int]:
        return {"remaining": 5000, "limit": 5000}


# ─────────────────────────────────────────────────────────
# GitHub Source Plugin
# ─────────────────────────────────────────────────────────

class GitHubSourcePlugin(SourcePlugin):
    """
    GitHub REST API source plugin.
    Uses the existing GitHubAdapter infrastructure if a token is provided,
    otherwise falls back to public API (rate-limited to 60 req/hr).
    """
    source_id = "github"

    def __init__(self, token: Optional[str] = None):
        self._token = token
        self._headers = {}
        if token:
            self._headers["Authorization"] = f"token {token}"
        self._headers["Accept"] = "application/vnd.github+json"
        self._headers["X-GitHub-Api-Version"] = "2022-11-28"
        
        # Local cache path for bare repositories
        self._repos_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "repos"))
        os.makedirs(self._repos_dir, exist_ok=True)

    def _get(self, url: str, params: Optional[Dict] = None) -> Any:
        import urllib.request
        import urllib.parse
        import json as _json
        if params:
            url = url + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=self._headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return _json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 403:
                raise Exception("GitHub API rate limit exceeded") from e
            raise

    def fetch_repository_metadata(self, repository: str) -> Dict[str, Any]:
        try:
            data = self._get(f"https://api.github.com/repos/{repository}")
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
        except Exception as e:
            return {"full_name": repository, "error": str(e)}

    _repo_locks: Dict[str, asyncio.Lock] = {}
    _locks_lock = threading.Lock()

    def _get_repo_lock(self, repository: str) -> asyncio.Lock:
        with self._locks_lock:
            if repository not in self._repo_locks:
                self._repo_locks[repository] = asyncio.Lock()
            return self._repo_locks[repository]

    async def _ensure_cloned(self, repository: str, progress_callback: Optional[Callable[[str], Any]] = None) -> str:
        safe_name = repository.replace("/", "_") + ".git"
        repo_path = os.path.join(self._repos_dir, safe_name)
        
        lock = self._get_repo_lock(repository)
        async with lock:
            if os.path.exists(repo_path) and not os.path.exists(os.path.join(repo_path, "HEAD")):
                # Corrupted or incomplete clone, remove it
                shutil.rmtree(repo_path, ignore_errors=True)

            loop = asyncio.get_running_loop()

            def _run_git(git_cmd):
                process = subprocess.Popen(
                    git_cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=False
                )
                
                import concurrent.futures
                futs = []
                
                # Read stderr byte by byte to handle \r without buffering
                if process.stderr:
                    buf = bytearray()
                    while True:
                        b = process.stderr.read(1)
                        if not b:
                            if buf and progress_callback:
                                line_str = buf.decode('utf-8', errors='replace').strip()
                                if line_str:
                                    if asyncio.iscoroutinefunction(progress_callback):
                                        fut = asyncio.run_coroutine_threadsafe(progress_callback(line_str), loop)
                                        futs.append(fut)
                                    else:
                                        progress_callback(line_str)
                            break
                        
                        if b in (b'\n', b'\r'):
                            if buf and progress_callback:
                                line_str = buf.decode('utf-8', errors='replace').strip()
                                if line_str:
                                    if asyncio.iscoroutinefunction(progress_callback):
                                        fut = asyncio.run_coroutine_threadsafe(progress_callback(line_str), loop)
                                        futs.append(fut)
                                    else:
                                        progress_callback(line_str)
                            buf.clear()
                        else:
                            buf.extend(b)
                
                process.wait()
                if futs:
                    concurrent.futures.wait(futs)
                    
                if process.returncode != 0:
                    raise Exception(f"Git command failed: {' '.join(git_cmd)}")

            if os.path.exists(repo_path):
                # Fetch updates
                if progress_callback:
                    if asyncio.iscoroutinefunction(progress_callback):
                        asyncio.run_coroutine_threadsafe(progress_callback("Connecting to GitHub... (fetching updates)"), loop)
                    else:
                        progress_callback("Connecting to GitHub... (fetching updates)")
                try:
                    await asyncio.to_thread(_run_git, ["git", f"--git-dir={repo_path}", "fetch", "origin", "+refs/heads/*:refs/heads/*", "--progress"])
                except Exception as e:
                    import logging
                    logging.warning(f"Git fetch failed, corrupted repo? Deleting and re-cloning: {e}")
                    import stat
                    def remove_readonly(func, path, excinfo):
                        os.chmod(path, stat.S_IWRITE)
                        func(path)
                    shutil.rmtree(repo_path, onerror=remove_readonly)
                    
            if not os.path.exists(repo_path):
                # Clone bare repository
                if progress_callback:
                    if asyncio.iscoroutinefunction(progress_callback):
                        asyncio.run_coroutine_threadsafe(progress_callback("Connecting to GitHub... (cloning repository)"), loop)
                    else:
                        progress_callback("Connecting to GitHub... (cloning repository)")
                url = f"https://github.com/{repository}.git"
                await asyncio.to_thread(_run_git, ["git", "clone", "--bare", "--progress", url, repo_path])
                
        return repo_path

    async def fetch_commits(self, repository: str, branch: str,
                      limit: int = 100, since_sha: Optional[str] = None,
                      progress_callback: Optional[Callable[[str], Any]] = None) -> List[Dict[str, Any]]:
        repo_path = await self._ensure_cloned(repository, progress_callback=progress_callback)
        
        # Build git log command
        cmd = ["git", f"--git-dir={repo_path}", "log", "--numstat", "--pretty=format:COMMIT|%H|%an|%ae|%aI|%s"]
        
        if limit > 0:
            cmd.extend(["-n", str(limit)])
            
        if since_sha:
            cmd.append(f"{since_sha}..{branch}")
        else:
            cmd.append(branch)
            
        try:
            # We still use subprocess.run for this fast operation, but in a thread to not block event loop
            result = await asyncio.to_thread(subprocess.run, cmd, check=True, capture_output=True, text=True, encoding="utf-8")
        except subprocess.CalledProcessError as e:
            print(f"Git log failed: {e.stderr}")
            return []
            
        commits = []
        current_commit = None
        
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("COMMIT|"):
                parts = line.split("|", 5)
                if len(parts) == 6:
                    current_commit = {
                        "sha": parts[1],
                        "author_name": parts[2],
                        "author_email": parts[3],
                        "timestamp": parts[4],
                        "message": parts[5][:500],
                        "additions": 0,
                        "deletions": 0,
                    }
                    commits.append(current_commit)
            elif current_commit is not None:
                # numstat line: added deleted filename
                stat_parts = line.split("\t", 2)
                if len(stat_parts) == 3:
                    try:
                        adds = int(stat_parts[0]) if stat_parts[0] != "-" else 0
                        dels = int(stat_parts[1]) if stat_parts[1] != "-" else 0
                        current_commit["additions"] += adds
                        current_commit["deletions"] += dels
                    except ValueError:
                        pass
                        
        return commits

    async def fetch_file_tree(self, repository: str, commit_sha: str,
                              progress_callback: Optional[Callable[[str], Any]] = None) -> List[Dict[str, Any]]:
        repo_path = await self._ensure_cloned(repository, progress_callback=progress_callback)
        
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                ["git", f"--git-dir={repo_path}", "ls-tree", "-r", "-l", commit_sha], 
                check=True, capture_output=True, text=True, encoding="utf-8"
            )
        except subprocess.CalledProcessError as e:
            print(f"Git ls-tree failed: {e.stderr}")
            return []
            
        files = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
                
            # Format: mode type sha size    path
            parts = line.split()
            if len(parts) >= 5 and parts[1] == "blob":
                sha = parts[2]
                size_str = parts[3]
                # the rest is the path, which might contain spaces
                path = line.split("\t", 1)[1]
                
                size = 0
                if size_str != "-":
                    try:
                        size = int(size_str)
                    except ValueError:
                        pass
                        
                ext = path.rsplit(".", 1)[-1] if "." in path else ""
                files.append({
                    "path": path,
                    "size": size,
                    "sha": sha,
                    "extension": ext,
                })
                
        return files

    def get_rate_limit(self) -> Dict[str, int]:
        try:
            data = self._get("https://api.github.com/rate_limit")
            core = data.get("resources", {}).get("core", {})
            return {
                "remaining": core.get("remaining", 0),
                "limit": core.get("limit", 60),
                "reset_at": core.get("reset", 0),
            }
        except Exception:
            return {"remaining": -1, "limit": -1}


# ─────────────────────────────────────────────────────────
# Sync Engine
# ─────────────────────────────────────────────────────────

class SyncEngine:
    """
    Orchestrates the full ingestion pipeline.
    All data flows: Source → Event Store → Operational Store → Projection Engine.
    """

    def __init__(
        self,
        provider: PersistenceProvider,
        event_store: ImmutableEventStore,
        projection_engine: Any,             # ProjectionEngine (imported lazily)
        broadcaster: Any = None,            # WebSocket broadcaster
    ):
        self._provider = provider
        self._event_store = event_store
        self._projection_engine = projection_engine
        self._broadcaster = broadcaster
        self._active_jobs: Dict[str, SyncJob] = {}
        self._history: List[SyncJob] = []   # completed jobs

    # ─── Public API ──────────────────────────────────────────

    async def sync(
        self,
        repository: str,
        mode: SyncMode = SyncMode.INCREMENTAL,
        branch: str = "main",
        commit_limit: int = 100,
        github_token: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> SyncJob:
        """Start a sync job. Returns immediately; call get_job_status() for progress."""
        repository = _normalize_repository(repository)
        job = SyncJob(
            repository=repository,
            sync_mode=mode,
            branch=branch,
            commit_limit=commit_limit,
            github_token=github_token,
            workspace_id=workspace_id or "",
        )
        self._active_jobs[job.job_id] = job
        asyncio.create_task(self._run_job(job, github_token))
        return job

    async def cancel(self, job_id: str) -> bool:
        job = self._active_jobs.get(job_id)
        if job and job.status == SyncStatus.RUNNING:
            job.cancellation_requested = True
            return True
        return False

    def get_job(self, job_id: str) -> Optional[SyncJob]:
        return self._active_jobs.get(job_id)

    def get_active_jobs(self) -> List[SyncJob]:
        return [
            j for j in self._active_jobs.values()
            if j.status in {SyncStatus.PENDING, SyncStatus.RUNNING, SyncStatus.PAUSED}
        ]

    def get_history(self, limit: int = 20) -> List[SyncJob]:
        return self._history[-limit:][::-1]

    # ─── Core Pipeline ───────────────────────────────────────

    async def _run_job(self, job: SyncJob, github_token: Optional[str]) -> None:
        job.status = SyncStatus.RUNNING
        job.started_at = datetime.datetime.utcnow().isoformat() + "Z"
        start = time.monotonic()

        plugin = GitHubSourcePlugin(token=github_token)

        # Log sync started to event store
        self._event_store.append(StoreEvent(
            event_type=EventType.SYNC_STARTED.value,
            source_component="sync_engine",
            workspace_id=job.workspace_id,
            payload={
                "job_id": job.job_id,
                "repository": job.repository,
                "sync_mode": job.sync_mode.value,
                "branch": job.branch,
                "commit_limit": job.commit_limit,
            }
        ))
        await self._emit({
            "schema_version": "v1",
            "event_type": "sync.started",
            "occurred_at": job.started_at,
            "job_id": job.job_id,
            "repository": job.repository,
            "branch": job.branch,
            "sync_mode": job.sync_mode.value,
            "status": job.status.value,
            "source_plugin": "github",
        })

        try:
            if job.sync_mode == SyncMode.REBUILD_PROJECTIONS:
                await self._rebuild_projections_only(job)
            else:
                await self._ingest_repository(job, plugin)
        except Exception as e:
            import traceback
            job.status = SyncStatus.FAILED
            job.error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            logger.exception(f"Sync failed for {job.repository}")
            self._event_store.append(StoreEvent(
                event_type=EventType.SYNC_FAILED.value,
                source_component="sync_engine",
                payload={"job_id": job.job_id, "error": str(e)},
            ))
            await self._emit({
                "schema_version": "v1",
                "event_type": "sync.failed",
                "occurred_at": datetime.datetime.utcnow().isoformat() + "Z",
                "job_id": job.job_id,
                "repository": job.repository,
                "branch": job.branch,
                "repository_session_id": job.repository_session_id,
                "status": job.status.value,
                "error": str(e),
            })
        finally:
            job.completed_at = datetime.datetime.utcnow().isoformat() + "Z"
            job.duration_ms = (time.monotonic() - start) * 1000
            if job.status == SyncStatus.RUNNING:
                job.status = SyncStatus.COMPLETED
            self._history.append(job)
            del self._active_jobs[job.job_id]

    async def _ingest_repository(self, job: SyncJob, plugin: SourcePlugin) -> None:
        """
        Full ingestion pipeline:
        1. Repository metadata → Operational Store
        2. Commits → Operational Store + Event Store
        3. Developers (resolved from commit authors) → Operational Store
        4. File tree → Operational Store
        5. Trigger projection engine for every batch
        """
        repo = _normalize_repository(job.repository)
        job.repository = repo

        # ── 1. Repository / Session ──────────────────────────
        job.current_operation = "Fetching repository metadata"
        await self._emit_progress(job)

        meta = await asyncio.to_thread(plugin.fetch_repository_metadata, repo)

        # Find or create workspace
        workspaces = self._provider.query(WorkspaceRecord, limit=1)
        if workspaces:
            workspace_id = workspaces[0].object_id
        else:
            ws = WorkspaceRecord(name="Default Workspace")
            self._provider.insert(ws)
            workspace_id = ws.object_id
        job.workspace_id = workspace_id

        # Find or create repository session (use high limit to ensure we don't miss existing ones and create duplicates)
        existing_sessions = self._provider.query(RepositorySessionRecord, limit=100000)
        session = next(
            (
                s for s in existing_sessions
                if _normalize_repository(s.repository) == repo and (s.branch or "main") == job.branch
            ),
            None
        )

        if session is None:
            session = RepositorySessionRecord(
                identity=GlobalIdentity(
                    object_type="repository_session",
                    workspace_id=workspace_id,
                ),
                workspace_id=workspace_id,
                repository=repo,
                branch=job.branch,
                commit_window=job.commit_limit,
                sync_status="syncing",
                source_plugin=plugin.source_id,
                metadata=meta,
            )
            self._provider.insert(session)
        else:
            session.repository = repo
            session.branch = job.branch
            session.commit_window = job.commit_limit
            session.sync_status = "syncing"
            session.source_plugin = plugin.source_id
            session.metadata = {**(session.metadata or {}), **meta}
            self._provider.update(session)

        job.repository_session_id = session.object_id
        since_sha = session.head_commit_sha if job.sync_mode == SyncMode.INCREMENTAL else None

        # ── 2. Commits ───────────────────────────────────────
        job.current_operation = "Fetching commits"
        await self._emit_progress(job)

        async def _progress(msg: str):
            job.current_operation = msg
            await self._emit_progress(job)

        commits_raw = await plugin.fetch_commits(
            repo, job.branch, job.commit_limit, since_sha, progress_callback=_progress
        )
        job.commits_total = len(commits_raw)
        job.api_calls_made += 1

        # Track known developers
        known_devs: Dict[str, str] = {}  # email → developer_id

        for i, raw in enumerate(commits_raw):
            if job.cancellation_requested:
                job.status = SyncStatus.CANCELLED
                return

            # Persist commit
            commit_id = str(uuid.uuid5(uuid.NAMESPACE_OID, f"commit:{repo}:{raw['sha']}"))
            commit = CommitRecord(
                identity=GlobalIdentity(
                    object_id=commit_id,
                    object_type="repo_commit",
                    workspace_id=workspace_id,
                    execution_id=job.job_id,
                ),
                repository_session_id=session.object_id,
                sha=raw["sha"],
                message=raw.get("message", ""),
                author_email=raw.get("author_email", ""),
                author_name=raw.get("author_name", ""),
                timestamp=raw.get("timestamp", ""),
                additions=raw.get("additions", 0),
                deletions=raw.get("deletions", 0),
            )
            try:
                self._provider.insert(commit)
                job.objects_added += 1
            except Exception:
                job.objects_updated += 1  # already exists

            # Log to event store
            self._event_store.append(StoreEvent(
                event_type=EventType.COMMIT_INGESTED.value,
                source_component="sync_engine",
                workspace_id=workspace_id,
                repository_session_id=session.object_id,
                payload={"sha": raw["sha"][:8], "author": raw.get("author_name", "")},
                affected_object_ids=[commit.object_id],
                affected_object_types=["repo_commit"],
            ))

            # Resolve developer
            email = raw.get("author_email", "")
            if email and email not in known_devs:
                dev_id = str(uuid.uuid5(uuid.NAMESPACE_OID, f"developer:{email}"))
                dev = DeveloperRecord(
                    identity=GlobalIdentity(
                        object_id=dev_id,
                        object_type="developer",
                        workspace_id=workspace_id,
                    ),
                    repository_session_id=session.object_id,
                    email=email,
                    login=email.split("@")[0],
                    display_name=raw.get("author_name", ""),
                    commit_count=1,
                    first_commit_at=raw.get("timestamp", ""),
                    last_commit_at=raw.get("timestamp", ""),
                )
                try:
                    self._provider.insert(dev)
                    known_devs[email] = dev.object_id
                    job.developers_found += 1
                    self._event_store.append(StoreEvent(
                        event_type=EventType.DEVELOPER_INGESTED.value,
                        source_component="sync_engine",
                        workspace_id=workspace_id,
                        repository_session_id=session.object_id,
                        payload={"email": email},
                        affected_object_ids=[dev.object_id],
                        affected_object_types=["developer"],
                    ))
                except Exception:
                    pass  # already exists

            job.commits_processed = i + 1
            job.last_commit_sha = raw["sha"]

            # Progress emit every 10 commits
            if i % 10 == 0:
                await self._emit_progress(job)
                # Yield to event loop
                await asyncio.sleep(0)

        # ── 3. File Tree (from HEAD commit) ──────────────────
        if commits_raw:
            job.current_operation = "Fetching file tree"
            await self._emit_progress(job)
            head_sha = commits_raw[0]["sha"]

            files_raw = await plugin.fetch_file_tree(repo, head_sha, progress_callback=_progress)
            job.api_calls_made += 1

            for raw_file in files_raw:
                if job.cancellation_requested:
                    break
                ext = raw_file.get("extension", "")
                language = _EXT_TO_LANGUAGE.get(ext, "")
                file_id = str(uuid.uuid5(uuid.NAMESPACE_OID, f"file:{repo}:{raw_file['path']}"))
                f = FileRecord(
                    identity=GlobalIdentity(
                        object_id=file_id,
                        object_type="file",
                        workspace_id=workspace_id,
                    ),
                    repository_session_id=session.object_id,
                    path=raw_file["path"],
                    language=language,
                    module=raw_file["path"].split("/")[0] if "/" in raw_file["path"] else "",
                    package=raw_file["path"].rsplit("/", 1)[0] if "/" in raw_file["path"] else "",
                    size_bytes=raw_file.get("size", 0),
                    last_modified_sha=head_sha,
                )
                try:
                    self._provider.insert(f)
                    job.files_processed += 1
                    job.objects_added += 1
                except Exception:
                    pass
                self._event_store.append(StoreEvent(
                    event_type=EventType.FILE_INGESTED.value,
                    source_component="sync_engine",
                    workspace_id=workspace_id,
                    repository_session_id=session.object_id,
                    payload={"path": raw_file["path"]},
                ))

        # ── 4. Update session state ──────────────────────────
        session.head_commit_sha = job.last_commit_sha
        session.sync_status = "healthy"
        session.last_synced_at = datetime.datetime.utcnow().isoformat() + "Z"
        session.languages = list({_EXT_TO_LANGUAGE.get(f.get("extension", ""), "") for f in files_raw if "extension" in f} - {""}) if 'files_raw' in locals() else []
        self._provider.update(session)

        # ── 5. Execute Platform Runtime ──────────────────────
        job.current_operation = "Executing Platform Runtime"
        await self._emit_progress(job)

        try:
            from app.core.runtime import PlatformRuntime
            from app.core.persistence_adapter import PersistenceAdapter

            # We need to run this in a thread since it's blocking
            def run_and_persist():
                runtime = PlatformRuntime.create()
                
                # Wire up event forwarding
                def forward_event(event):
                    # For a blocking thread, we must schedule the asyncio task safely
                    try:
                        loop = asyncio.get_running_loop()
                        asyncio.run_coroutine_threadsafe(
                            self._emit({
                                "schema_version": "v1",
                                "event_type": event.type,
                                "occurred_at": datetime.datetime.utcnow().isoformat() + "Z",
                                "payload": event.payload
                            }),
                            loop
                        )
                    except Exception:
                        pass
                
                # Subscribe to stage events
                runtime.event_bus.subscribe("runtime.*", forward_event)
                
                result = runtime.run(
                    repository=workspace_id, # Using workspace_id here because OperationalStoreAdapter uses it
                    commits=job.commit_limit,
                    branch=job.branch,
                    github_token="operational_store_trigger",
                    since_commit=since_sha,
                )
                
                # Persist outputs in a transaction
                adapter = PersistenceAdapter(self._provider)
                adapter.persist(
                    result=result,
                    workspace_id=workspace_id,
                    repository_session_id=session.object_id,
                    execution_id=job.job_id
                )

            await asyncio.to_thread(run_and_persist)
            
        except Exception as e:
            self._event_store.append(StoreEvent(
                event_type="runtime_execution_failed",
                source_component="sync_engine",
                payload={"error": str(e)}
            ))
            job.error = f"Runtime execution failed: {e}"

        # ── 6. Trigger Projection Engine ─────────────────────
        job.current_operation = "Updating projections"
        await self._emit_progress(job)

        await self._projection_engine.trigger(
            EventType.SYNC_COMPLETED.value,
            repository_session_id=session.object_id,
            workspace_id=workspace_id,
        )

        # ── 6. Completion ────────────────────────────────────
        self._event_store.append(StoreEvent(
            event_type=EventType.SYNC_COMPLETED.value,
            source_component="sync_engine",
            workspace_id=workspace_id,
            repository_session_id=session.object_id,
            payload={
                "repository": repo,
                "commits_ingested": job.commits_processed,
                "developers_ingested": job.developers_found,
                "files_ingested": job.files_processed,
            }
        ))
        await self._emit({
            "schema_version": "v1",
            "event_type": "sync.completed",
            "occurred_at": datetime.datetime.utcnow().isoformat() + "Z",
            "job_id": job.job_id,
            "repository": repo,
            "branch": job.branch,
            "repository_session_id": session.object_id,
            "status": SyncStatus.COMPLETED.value,
            "commits_ingested": job.commits_processed,
            "developers_ingested": job.developers_found,
            "files_ingested": job.files_processed,
            "duration_ms": (time.monotonic() * 1000),
            "triggered_projections": ["knowledge_graph_v1", "ownership_v1"],
        })

    async def _rebuild_projections_only(self, job: SyncJob) -> None:
        job.current_operation = "Rebuilding all projections"
        await self._projection_engine.rebuild_all()

    async def _emit(self, event: Dict[str, Any]) -> None:
        try:
            await self._broadcaster.broadcast(event)
        except Exception:
            pass

    async def _emit_progress(self, job: SyncJob) -> None:
        await self._emit({
            "schema_version": "v1",
            "event_type": "sync.progress",
            "occurred_at": datetime.datetime.utcnow().isoformat() + "Z",
            "job_id": job.job_id,
            "repository": job.repository,
            "branch": job.branch,
            "repository_session_id": job.repository_session_id,
            "status": job.status.value,
            "commits_processed": job.commits_processed,
            "commits_total": job.commits_total,
            "developers_found": job.developers_found,
            "files_processed": job.files_processed,
            "current_operation": job.current_operation,
            "objects_added": job.objects_added,
        })


# ─────────────────────────────────────────────────────────
# Extension → Language Map
# ─────────────────────────────────────────────────────────

_EXT_TO_LANGUAGE: Dict[str, str] = {
    "py": "Python", "js": "JavaScript", "ts": "TypeScript", "tsx": "TypeScript",
    "jsx": "JavaScript", "java": "Java", "kt": "Kotlin", "go": "Go",
    "rs": "Rust", "cpp": "C++", "c": "C", "cs": "C#", "rb": "Ruby",
    "php": "PHP", "swift": "Swift", "scala": "Scala", "clj": "Clojure",
    "hs": "Haskell", "ml": "OCaml", "ex": "Elixir", "vue": "Vue",
    "html": "HTML", "css": "CSS", "scss": "SCSS", "md": "Markdown",
    "json": "JSON", "yaml": "YAML", "yml": "YAML", "toml": "TOML",
    "sh": "Shell", "dockerfile": "Docker",
}


def _normalize_repository(repository: str) -> str:
    return (repository or "").strip().strip("/").lower()


# ─────────────────────────────────────────────────────────
# Module-level singleton
# ─────────────────────────────────────────────────────────

_engine: Optional[SyncEngine] = None


def get_sync_engine(broadcaster: Any = None) -> SyncEngine:
    global _engine
    if _engine is None:
        from app.infrastructure.database.sqlite_provider import get_provider
        from app.core.events.store import get_event_store
        from app.core.projections.engine import get_projection_engine
        
        if broadcaster is None:
            try:
                from app.api.routers.ws import SyncBroadcaster
                broadcaster = SyncBroadcaster()
            except ImportError:
                pass

        _engine = SyncEngine(
            provider=get_provider(),
            event_store=get_event_store(),
            projection_engine=get_projection_engine(),
            broadcaster=broadcaster,
        )
    return _engine
