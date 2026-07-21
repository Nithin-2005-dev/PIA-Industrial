import uuid
import time
from typing import Optional
from app.kernel.runtime import CognitiveRuntime
from app.kernel.models import AgentPolicy, ExecutionStatus, WorkspaceSession
from app.api.dtos.v1 import ExecutionTraceDTO_v1, TraceEventDTO_v1
from app.core.core_modules import GitHubAdapterFactory
from app.kernel.provider_manager import ProviderManager
from app.kernel.provider import MockLLMProvider # In a full system, this could be the real LLM

class QueryService:
    def __init__(self):
        # In a real DI setup, we'd inject this
        pass

    def execute_query(
        self,
        query: str,
        workspace_id: Optional[str] = None,
        dataset_version: str = "v1",
        repository: Optional[str] = None,
        repository_session_id: Optional[str] = None,
    ) -> ExecutionTraceDTO_v1:
        session_id = str(uuid.uuid4())
        query_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 1. Check Operational Store for recent execution
        from app.infrastructure.database.sqlite_provider import get_provider
        from app.infrastructure.database.models import (
            CommitRecord,
            DeveloperRecord,
            EvidenceRecord,
            ExecutionRecord,
            FileRecord,
            MeasurementRecord,
            RepositorySessionRecord,
            RuleExecutionRecord,
        )
        provider = get_provider()
        repository = _normalize_repository(repository or workspace_id or "")

        sessions = provider.query(RepositorySessionRecord, limit=1000)
        selected_session = None
        if repository_session_id:
            selected_session = provider.get_by_id(RepositorySessionRecord, repository_session_id)
        if selected_session is None and repository:
            selected_session = next(
                (
                    s for s in sessions
                    if _normalize_repository(s.repository) == repository
                ),
                None
            )
        if selected_session is None and sessions:
            selected_session = sessions[0]

        if selected_session:
            workspace_id = selected_session.workspace_id or selected_session.identity.workspace_id or workspace_id
            repository = _normalize_repository(selected_session.repository)
        else:
            workspace_id = workspace_id or "default"
        
        # Get the latest successful execution for this workspace
        executions = provider.query(
            ExecutionRecord, 
            filters={"workspace_id": workspace_id, "status": "success"}, 
            limit=1
        )
        # Note: In SQLiteProvider, we might need a custom query to sort by date descending.
        # But for now, we'll just check if any exists.
        
        try:
            platform_result = None
            if executions:
                latest_execution = executions[0]
                from app.core.api.contracts import RuntimePipelineResult
                from scripts.platform_showcase.context import PlatformContext
                from pathlib import Path

                measurements = [m for mid in latest_execution.measurement_ids if (m := provider.get_by_id(MeasurementRecord, mid))]
                evidence = [e for eid in latest_execution.evidence_ids if (e := provider.get_by_id(EvidenceRecord, eid))]
                reasoning = [r for rid in latest_execution.reasoning_ids if (r := provider.get_by_id(RuleExecutionRecord, rid))]

                ctx = PlatformContext(
                    repository=repository or workspace_id or "default",
                    branch=selected_session.branch if selected_session else "main",
                    commit_limit=0,
                    github_token=None,
                    tenant_id="default",
                    output_directory=Path("outputs/showcase")
                )
                ctx.measurements = measurements
                ctx.evidence_package = evidence
                ctx.reasoning_results = reasoning
                platform_result = RuntimePipelineResult(context=ctx, completed_stages=(), execution_order=())

            if platform_result is None and repository:
                from app.core.runtime import PlatformRuntime
                platform = PlatformRuntime.create()
                platform_result = platform.run(repository=repository, commits=50)

            if platform_result is not None:
                policy = AgentPolicy()
                provider_mgr = ProviderManager(
                    providers=[MockLLMProvider(latency_ms=10, token_rate=100)],
                    policy=policy
                )
                runtime = CognitiveRuntime(provider_manager=provider_mgr, agent_policy=policy)

                from app.kernel.models import CognitiveSession
                workspace = WorkspaceSession(repository=repository or workspace_id or "default")
                session = CognitiveSession(session_id=session_id, workspace_session=workspace)
                state = runtime.answer(platform_result=platform_result, question=query, session=session)

                trace_events = [
                    TraceEventDTO_v1(
                        stage=t.stage,
                        execution_time_ms=t.execution_time_ms,
                        decision=t.decision,
                        output_summary=t.output_summary,
                        cache_hit=t.cache_hit
                    )
                    for t in (state.reasoning_trace or [])
                ]
                return ExecutionTraceDTO_v1(
                    query_id=query_id,
                    status=state.status.value,
                    answer=state.answer.response if state.answer else (state.executive_response.summary if state.executive_response else "Execution completed without a text response."),
                    reasoning_trace=trace_events,
                    total_latency_ms=(time.time() - start_time) * 1000
                )
        except Exception:
            pass

        session_id_filter = selected_session.object_id if selected_session else None
        commits = provider.query(CommitRecord, limit=1000)
        developers = provider.query(DeveloperRecord, limit=1000)
        files = provider.query(FileRecord, limit=1000)
        measurements = provider.query(MeasurementRecord, limit=1000)
        evidence = provider.query(EvidenceRecord, limit=1000)

        if session_id_filter:
            commits = [c for c in commits if c.repository_session_id == session_id_filter]
            developers = [d for d in developers if d.repository_session_id == session_id_filter]
            files = [f for f in files if f.repository_session_id == session_id_filter]
            measurements = [m for m in measurements if m.repository_session_id == session_id_filter]
            evidence = [e for e in evidence if e.repository_session_id == session_id_filter]

        answer = (
            f"{selected_session.repository if selected_session else repository or 'This workspace'} is connected. "
            f"I found {len(commits)} commits, {len(developers)} developers, {len(files)} files, "
            f"{len(measurements)} measurements, and {len(evidence)} evidence records. "
            f"Latest sync status: {(selected_session.sync_status if selected_session else 'unknown')}. "
            "Ask about ownership, risk, measurements, evidence, files, or recent execution state."
        )

        return ExecutionTraceDTO_v1(
            query_id=query_id,
            status=ExecutionStatus.SUCCESS.value,
            answer=answer,
            reasoning_trace=[
                TraceEventDTO_v1(
                    stage="operational_store_summary",
                    execution_time_ms=(time.time() - start_time) * 1000,
                    decision="Answered from persisted repository records",
                    output_summary="Generated deterministic repository summary",
                    cache_hit=True,
                )
            ],
            total_latency_ms=(time.time() - start_time) * 1000
        )


def _normalize_repository(repository: Optional[str]) -> str:
    return (repository or "").strip().strip("/").lower()
