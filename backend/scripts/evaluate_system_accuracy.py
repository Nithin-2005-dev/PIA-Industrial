import argparse
import json
import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace as NS

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.kernel.models import AgentPolicy, ExecutionStatus, Intent, WorkspaceSession
from app.kernel.provider import OllamaProvider
from app.kernel.provider_manager import ProviderManager
from app.kernel.runtime import CognitiveRuntime
from app.platform.runtime import PlatformRuntime
from tests.mocks.mock_provider import MockLLMProvider


CASES = [
    {
        "query": "Who is the top contributor?",
        "intent": "REPOSITORY_QUERY",
        "goals": ["FIND_CONTRIBUTOR"],
        "capabilities": ["TopContributors"],
    },
    {
        "query": "Who owns ReactDOM?",
        "intent": "REPOSITORY_QUERY",
        "goals": ["FIND_OWNER"],
        "capabilities": ["TopContributors", "Ownership"],
    },
    {
        "query": "Which subsystem has the highest bus factor risk?",
        "intent": "REPOSITORY_QUERY",
        "goals": ["IDENTIFY_RISK"],
        "capabilities": ["TopContributors", "Ownership", "BusFactor"],
    },
    {
        "query": "What happens if hoxyq leaves?",
        "intent": "REPOSITORY_QUERY",
        "goals": ["SIMULATE_DEPARTURE"],
        "capabilities": ["DeveloperDepartureSimulation"],
    },
    {
        "query": "Forecast next month.",
        "intent": "REPOSITORY_QUERY",
        "goals": ["FORECAST"],
        "capabilities": ["Forecast"],
    },
    {
        "query": "Why is ownership concentration getting worse?",
        "intent": "REPOSITORY_QUERY",
        "goals": ["FIND_OWNER", "IDENTIFY_RISK", "DIAGNOSE_CAUSALITY"],
        "capabilities": ["CausalAnalysis"],
    },
    {
        "query": "Draw dependency graph.",
        "intent": "REPOSITORY_QUERY",
        "goals": ["VISUALIZE_GRAPH"],
        "capabilities": ["KnowledgeGraph"],
    },
    {
        "query": "Summarize repository health.",
        "intent": "REPOSITORY_QUERY",
        "goals": ["SUMMARIZE"],
        "capabilities": ["TopContributors", "Ownership", "BusFactor", "Health"],
    },
    {
        "query": "Which files changed most recently?",
        "intent": "REPOSITORY_QUERY",
        "goals": ["ANALYZE"],
        "capabilities": ["TopContributors"],
    },
    {
        "query": "hello",
        "intent": "GENERAL_CHAT",
        "goals": [],
        "capabilities": [],
    },
    {
        "query": "what tools do you have?",
        "intent": "SYSTEM_PLATFORM",
        "goals": [],
        "capabilities": [],
    },
]


def synthetic_platform_result():
    actor = NS(id="hoxyq")
    observation = NS(actors=[actor])
    return NS(
        context=NS(
            org_intelligence={
                "top_contributors": ["hoxyq", "eps1lon"],
                "bus_factor": 1,
                "health_score": 0.72,
                "ownership_gini": 0.82,
            },
            forecast_context={"health_trend": "declining", "risk": "medium"},
            causal_context={"primary_root_cause": "Ownership Concentration"},
            simulation_context={"departure_impact": "moderate"},
            knowledge_graph={"nodes": 12, "edges": 18},
            observations=[observation],
            repository="facebook/react",
            branch="main",
            commit_limit=50,
        )
    )


def real_platform_result(repo: str, commits: int):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN or GH_TOKEN is required for --live-platform. "
            "Set a rotated token in your shell environment before running."
        )
    platform = PlatformRuntime.create()
    platform.register_default_modules()
    result = platform.run(repository=repo, commits=commits, github_token=token)
    if getattr(result, "errors", None):
        raise RuntimeError("; ".join(str(e) for e in result.errors))
    return result


def make_provider(name: str, model: str):
    if name == "ollama":
        return OllamaProvider(model=model)
    if name == "mock":
        return MockLLMProvider()
    raise ValueError(f"Unknown provider: {name}")


def run_case(runtime: CognitiveRuntime, platform_result, repo: str, commits: int, case: dict) -> dict:
    session = runtime.create_session()
    session.set_repository(WorkspaceSession(repository=repo, commit_window=commits))
    started = time.perf_counter()
    state = runtime.answer(platform_result, case["query"], session)
    latency_ms = (time.perf_counter() - started) * 1000

    actual_goals = [node.goal.name for node in state.goal_graph.nodes] if state.goal_graph else []
    actual_capabilities = list(state.tool_history)
    expected_intent = Intent[case["intent"]]
    expected_goals = set(case["goals"])
    expected_capabilities = set(case["capabilities"])

    intent_ok = state.classification.intent == expected_intent
    goals_ok = expected_goals.issubset(set(actual_goals))
    capabilities_ok = expected_capabilities.issubset(set(actual_capabilities))
    execution_ok = (
        state.status == ExecutionStatus.SUCCESS
        if expected_intent == Intent.REPOSITORY_QUERY
        else state.executive_response is not None
    )
    evidence_ok = (
        bool(state.executive_response and state.executive_response.supporting_evidence)
        if expected_intent == Intent.REPOSITORY_QUERY
        else True
    )
    verification_ok = (
        bool(state.answer and state.answer.verification and state.answer.verification.verified_claims > 0)
        if expected_intent == Intent.REPOSITORY_QUERY
        else True
    )

    return {
        "query": case["query"],
        "latency_ms": round(latency_ms, 2),
        "expected_intent": case["intent"],
        "actual_intent": state.classification.intent.name,
        "intent_ok": intent_ok,
        "expected_goals": sorted(expected_goals),
        "actual_goals": actual_goals,
        "goals_ok": goals_ok,
        "expected_capabilities": sorted(expected_capabilities),
        "actual_capabilities": actual_capabilities,
        "capabilities_ok": capabilities_ok,
        "execution_status": state.status.name,
        "execution_ok": execution_ok,
        "evidence_ok": evidence_ok,
        "verification_ok": verification_ok,
        "confidence": state.confidence.overall if state.confidence else None,
        "stage_results": [
            {
                "stage": sr.stage_name,
                "status": sr.status,
                "reason": sr.reason,
            }
            for sr in state.stage_results
        ],
    }


def summarize(rows: list[dict]) -> dict:
    repo_rows = [r for r in rows if r["expected_intent"] == "REPOSITORY_QUERY"]
    metrics = {
        "intent_accuracy": sum(r["intent_ok"] for r in rows) / max(len(rows), 1),
        "goal_accuracy": sum(r["goals_ok"] for r in repo_rows) / max(len(repo_rows), 1),
        "capability_accuracy": sum(r["capabilities_ok"] for r in repo_rows) / max(len(repo_rows), 1),
        "execution_success": sum(r["execution_ok"] for r in rows) / max(len(rows), 1),
        "evidence_coverage": sum(r["evidence_ok"] for r in repo_rows) / max(len(repo_rows), 1),
        "verification_coverage": sum(r["verification_ok"] for r in repo_rows) / max(len(repo_rows), 1),
        "avg_latency_ms": sum(r["latency_ms"] for r in rows) / max(len(rows), 1),
    }
    metrics["overall"] = (
        metrics["intent_accuracy"]
        + metrics["goal_accuracy"]
        + metrics["capability_accuracy"]
        + metrics["execution_success"]
        + metrics["evidence_coverage"]
        + metrics["verification_coverage"]
    ) / 6.0
    return metrics


def print_summary(metrics: dict, rows: list[dict]) -> None:
    print("\nSystem Accuracy")
    print(f"Intent accuracy       : {metrics['intent_accuracy'] * 100:.1f}%")
    print(f"Goal accuracy         : {metrics['goal_accuracy'] * 100:.1f}%")
    print(f"Capability accuracy   : {metrics['capability_accuracy'] * 100:.1f}%")
    print(f"Execution success     : {metrics['execution_success'] * 100:.1f}%")
    print(f"Evidence coverage     : {metrics['evidence_coverage'] * 100:.1f}%")
    print(f"Verification coverage : {metrics['verification_coverage'] * 100:.1f}%")
    print(f"Overall               : {metrics['overall'] * 100:.1f}%")
    print(f"Average latency       : {metrics['avg_latency_ms']:.1f}ms")

    failures = [
        r for r in rows
        if not (
            r["intent_ok"]
            and r["goals_ok"]
            and r["capabilities_ok"]
            and r["execution_ok"]
            and r["evidence_ok"]
            and r["verification_ok"]
        )
    ]
    if failures:
        print("\nFailures")
    for row in failures:
        print(f"- {row['query']}")
        print(f"  intent: {row['actual_intent']} expected {row['expected_intent']}")
        print(f"  goals: {row['actual_goals']} expected {row['expected_goals']}")
        print(f"  capabilities: {row['actual_capabilities']} expected {row['expected_capabilities']}")
        print(f"  status: {row['execution_status']} evidence={row['evidence_ok']} verification={row['verification_ok']}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate PIA cognitive system accuracy.")
    parser.add_argument("--repo", default="facebook/react")
    parser.add_argument("--commits", type=int, default=50)
    parser.add_argument("--provider", choices=["mock", "ollama"], default="mock")
    parser.add_argument("--ollama-model", default="gpt-oss:120b-cloud")
    parser.add_argument("--live-platform", action="store_true")
    parser.add_argument("--output", default="outputs/system_accuracy/system_accuracy_report.json")
    args = parser.parse_args()

    provider = make_provider(args.provider, args.ollama_model)
    policy = AgentPolicy()
    runtime = CognitiveRuntime(
        provider_manager=ProviderManager([provider], policy),
        agent_policy=policy,
    )
    platform_result = (
        real_platform_result(args.repo, args.commits)
        if args.live_platform
        else synthetic_platform_result()
    )

    rows = [
        run_case(runtime, platform_result, args.repo, args.commits, case)
        for case in CASES
    ]
    metrics = summarize(rows)
    print_summary(metrics, rows)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"metrics": metrics, "rows": rows}, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"\nWrote {output}")


if __name__ == "__main__":
    main()
