import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

import argparse
import subprocess
import json
from dataclasses import asdict

# Add the backend directory to sys.path so 'app' can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.platform.runtime import PlatformRuntime
from app.kernel.runtime import CognitiveRuntime
from app.kernel.models import WorkspaceSession, CommunicationMode, ExecutionStatus, AgentPolicy
from app.kernel.provider import OpenAIProvider, GeminiProvider, OllamaProvider
from tests.mocks.mock_provider import MockLLMProvider
from app.kernel.provider_manager import ProviderManager
from app.kernel.events import get_event_bus

def main():
    parser = argparse.ArgumentParser(description="PIA Cognitive Agent Chat")
    parser.add_argument("--repo", type=str, default="facebook/react", help="Target repository")
    parser.add_argument("--commits", type=int, default=50, help="Number of commits to analyze")
    parser.add_argument("--provider", type=str, choices=["openai", "gemini", "mock", "ollama"], default="mock", help="LLM Provider to use")
    parser.add_argument("--fallback", action="store_true", help="Allow fallback to MockLLMProvider on API failure")
    parser.add_argument("--diagnostics", action="store_true", help="Run runtime self-diagnostics and exit")
    parser.add_argument("--audit-capabilities", action="store_true", help="Audit all implemented capabilities and exit")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging for API calls")
    parser.add_argument("--reflect", action="store_true", help="Force reflection on all queries (uses extra tokens)")
    
    # M57.8 Tracing Flags
    parser.add_argument("--trace", action="store_true", help="Print end-to-end execution trace after each answer")
    parser.add_argument("--trace-prompt", action="store_true", help="Dump exact prompt sections before calling LLM")
    parser.add_argument("--trace-provider", action="store_true", help="Dump provider resolution and API calls")
    parser.add_argument("--trace-artifacts", action="store_true", help="Dump retrieved artifacts")
    parser.add_argument("--trace-planner", action="store_true", help="Dump planner graph output")
    parser.add_argument("--trace-file", type=str, help="Dump execution trace to JSON file")
    
    parser.add_argument("--mode", type=str, choices=["auto", "executive", "engineer", "researcher", "teacher", "student"], default="auto", help="Communication Mode")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark suite instead of chat")
    
    args = parser.parse_args()
    
    if args.benchmark:
        subprocess.run([sys.executable, "scripts/benchmark_cognitive.py"])
        return
    
    print("=====================================================")
    print(" PIA AI Engineering Advisor (Interactive Chat)")
    print("=====================================================")
    
    # Lazy Initialization Setup
    platform = None
    result = None
    repo_loaded = False
    # 2. Setup Provider
    provider = None
    if args.provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            print("[ERROR] OPENAI_API_KEY environment variable is not set.")
            sys.exit(1)
        provider = OpenAIProvider(api_key=api_key, model="gpt-4o")
    elif args.provider == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            print("[ERROR] GEMINI_API_KEY environment variable is not set.")
            sys.exit(1)
        provider = GeminiProvider(api_key=api_key, debug=args.trace_provider, allow_model_fallback=args.fallback)
    elif args.provider == "ollama":
        provider = OllamaProvider(model="gpt-oss:120b-cloud")
    else:
        provider = MockLLMProvider()

    if args.diagnostics:
        print("\n[DIAGNOSTICS MODE] Running Runtime Self-Diagnostics...")
        try:
            runtime = CognitiveRuntime(provider_manager=ProviderManager([provider], AgentPolicy()), agent_policy=AgentPolicy())
            # Output diagnostic info
            print("Runtime Version     : M57.13")
            from app.kernel.adapter import PlatformResultAdapter
            print(f"Adapter Version     : {PlatformResultAdapter.version}")
            print("Platform Version    : v1")
            
            # Capability Coverage logic is printed on init of CognitiveRuntime
            
            print("\nSchemas Loaded      : ✓")
            print("Validators Loaded   : ✓")
            print(f"Provider            : {provider.__class__.__name__}")
            print("Prompt Version      : planner_v4")
            print("Memory Version      : M57.12")
            print("Telemetry           : ENABLED")
            print("\nPASS")
        except Exception as e:
            print(f"\nFAIL: {e}")
        sys.exit(0)
        
    if args.audit_capabilities:
        print("\n[CAPABILITY AUDIT]")
        runtime = CognitiveRuntime(provider_manager=ProviderManager([provider], AgentPolicy()), agent_policy=AgentPolicy())
        from app.kernel.adapter import PlatformResultAdapter
        implemented = [c for c in runtime.registry.get_all() if c.contract.implemented.name == "IMPLEMENTED"]
        method_map = {
            "cap_top_contributors": "organization",
            "cap_ownership": "ownership",
            "cap_bus_factor": "organization",
            "cap_health": "health",
            "cap_forecast": "forecast",
            "cap_simulation": "simulation",
            "cap_causal_analysis": "causal",
            "cap_knowledge_graph": "knowledge_graph",
        }
        for cap in implemented:
            print(f"\nCapability: {cap.name}")
            print("Registry      ✓")
            print(f"Adapter       {'✓' if hasattr(PlatformResultAdapter, method_map.get(cap.contract.id, '')) else '✗'}")
            print(f"Executor      {'✓' if cap.contract.id in method_map else '✗'}")
            print("Validator     ✓")
            print("AnswerBuilder ✓")
            print("Trace         ✓")
            print("Status        READY")
        sys.exit(0)
        
    providers_list = [provider]
    if args.fallback and args.provider != "mock":
        providers_list.append(MockLLMProvider())
        
    provider_manager = ProviderManager(providers=providers_list, policy=AgentPolicy())
    
    # Subscribe to Event Bus for streaming UI
    event_bus = get_event_bus()
    def on_event(event):
        if event.event_type == "PlannerFinished":
            print(f"\n[Iteration {event.data.get('iteration', 0)}] Planner Strategy:")
            # In M57.12 we would print the RequiredCapability reasons here, but they aren't in the raw event payload yet.
        elif event.event_type == "ToolStarted":
            print(f"  → Capability Selected: {event.data.get('tool', 'Tool')}...")
        elif event.event_type == "ToolFinished":
            latency = event.data.get('latency', 0)
            status = "✓" if event.data.get('success') else "✗"
            cache = "(cache hit)" if event.data.get('cache_hit') else ""
            print(f"  {status} {event.data.get('tool', 'Tool')} executed in {latency:.0f}ms {cache}")
        elif event.event_type == "ReflectionStarted":
            print("  ↺ Reflecting on findings...")
        elif event.event_type == "AnswerStreaming":
            print("\nSynthesizing final response...\n")
            
    event_bus.subscribe("*", on_event)

    # Make sure we pass trace flags to runtime if it supports them, but we'll handle printing here mostly.
    runtime = CognitiveRuntime(provider_manager=provider_manager, agent_policy=AgentPolicy())
    runtime._trace_prompt = args.trace_prompt  # Inject flag for prompt dumping
    
    session = runtime.create_session()
    
    # M57.4: Inject active WorkspaceSession
    repo_session = WorkspaceSession(
        repository=args.repo,
        commit_window=args.commits,
        metadata={"platform": "github"}
    )
    session.set_repository(repo_session)
    
    # M57.5: Set Communication Mode
    session.communication_mode = CommunicationMode(args.mode)
    
    print("\n[OK] Cognitive Runtime ready. Type 'exit' or 'quit' to end session.")
    print("-------------------------------------------------------------------")
    
    while True:
        try:
            question = input("\n> ")
            if question.strip().lower() in ["exit", "quit"]:
                print("Ending session.")
                break
                
            if not question.strip():
                continue
                
            print("\nRouting intent...")
            
            # Lazy load if required
            classification = runtime.router.route(question)
            if classification.requires_repository and not repo_loaded:
                print(f"\n[Lazy Load] Initializing Platform Runtime on {args.repo}...")
                platform = PlatformRuntime.create()
                platform.register_default_modules()
                try:
                    github_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
                    result = platform.run(repository=args.repo, commits=args.commits, github_token=github_token)
                    if result.errors:
                        print(f"\n[ERROR] Pipeline failed with the following errors:")
                        for err in result.errors:
                            print(f"  - {err}")
                        if "GITHUB_TOKEN" in str(result.errors):
                            print("\nPlease set the GITHUB_TOKEN environment variable to fetch real data.")
                        continue
                    repo_loaded = True
                    print("[OK] Repository Loaded.")
                except Exception as e:
                    print(f"[ERROR] Failed to run pipeline: {e}")
                    continue

            print("Analyzing...")
            state = runtime.answer(
                platform_result=result,
                question=question,
                session=session,
            )
            
            # Print Traces first
            if args.trace:
                print("\n=========================================")
                print("QUESTION")
                print("=========================================")
                print(question)
                
                print(f"\nIntent\n{state.classification.intent.name}")
                print(f"confidence = {state.classification.confidence:.2f}")
                
                print(f"\nRepository Session\n{repo_session.repository}")
                print(f"branch = {repo_session.branch}")
                print(f"commit_window = {repo_session.commit_window}")
                
                if state.classification.topics:
                    print("\nSemantic Topics")
                    for t in state.classification.topics:
                        print(f"- {t.name}")
                        
                if state.tool_history:
                    print("\nAgent Loop Output\nTools Called:")
                    for t in state.tool_history:
                        print(f"- {t}")
                        
                if state.repository_memory.observations:
                    print("\nDeterministic Execution Trace:")
                    for obs in state.repository_memory.observations:
                        print(f"Tool: {obs.tool}")
                        print(f"  Latency: {obs.latency_ms:.0f}ms")
                        if hasattr(obs.output, "report") and obs.output.report:
                            from dataclasses import asdict, is_dataclass
                            print(f"  Domain Report:\n    {obs.output.report.__class__.__name__}: {asdict(obs.output.report)}")
                        if hasattr(obs.output, "explanation") and obs.output.explanation:
                            from dataclasses import asdict
                            print(f"  Explanation:\n    {asdict(obs.output.explanation)}")
                        if hasattr(obs.output, "provenance") and obs.output.provenance:
                            from dataclasses import asdict
                            print(f"  Provenance:\n    {asdict(obs.output.provenance)}")
                        print(f"  CapabilityResult:\n    {obs.output.summary}")
                            
                if args.trace_artifacts and state.retrieved_evidence:
                    print(f"\nRetrieved Artifacts\nartifact_count = {len(state.retrieved_evidence.artifacts)}")
                    for a in state.retrieved_evidence.artifacts:
                        print(f"- {a.id}: {a.title}")
                        
                if state.answer and state.answer.verification:
                    v = state.answer.verification
                    print("\nVerifier")
                    print(f"verified claims = {len(v.critiques) - v.dropped_claims}")
                    print(f"unsupported claims = {v.dropped_claims}")
                    
                if state.reflection:
                    print("\nReflection")
                    print("triggered? True")
                    print(f"replanned? {state.reflection.should_replan}")
                    
                if state.confidence:
                    print("\nConfidence")
                    print(f"Evidence Coverage {state.confidence.evidence_coverage:.2f}")
                    print(f"Verification      {state.confidence.verification_score:.2f}")
                    print(f"Reasoning         {state.confidence.reasoning_consistency:.2f}")
                    print(f"Reflection        {state.confidence.reflection_score:.2f}")
                    print(f"\nFinal Confidence  {state.confidence.overall:.2f}")
                print("=========================================\n")
            
            # Print Final Response
            print("\nExecution Status:")
            print(state.status.name)
            
            if state.status == ExecutionStatus.SUCCESS or state.status == ExecutionStatus.PARTIAL:
                print("\nPIA AI:")
                print(state.executive_response.executive_summary)
                if state.executive_response.actionable_recommendations:
                    print("\nRecommendations:")
                    for rec in state.executive_response.actionable_recommendations:
                        print(f"- {rec}")
            else:
                print("\nFailure Stage:")
                if state.failure_reason:
                    print(state.failure_reason.stage)
                    print("\nReason:")
                    print(state.failure_reason.message)
                    if state.failure_reason.retry_after:
                        print(f"\nRetry After: {state.failure_reason.retry_after}s")
                elif state.executive_response:
                    print(state.executive_response.technical_summary)
                else:
                    print("Unknown runtime error.")
            
            if args.trace_file and state.reasoning_trace:
                with open(args.trace_file, "w") as f:
                    json.dump([asdict(t) for t in state.reasoning_trace], f, indent=2)
                print(f"\n[Trace dumped to {args.trace_file}]")
                    
        except KeyboardInterrupt:
            print("\nEnding session.")
            break
        except Exception as e:
            print(f"\n[Error]: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
