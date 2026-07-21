import time
import uuid
import json
from typing import Any, List, Optional, Dict
from .models import ExecutionRequest, AgentObservation, CapabilityCard, CapabilityResult, PreconditionFailure, CapabilityStatus, CapabilityProvenance, Explanation
from .registry import CapabilityRegistry
from .interpreters import INTERPRETERS
from .events import get_event_bus
from .adapter import PlatformResultAdapter, MissingMeasurementException

class CapabilityPlanner:
    """Maps semantic capabilities requested by the Planner to concrete ExecutionRequests."""
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def map_capabilities(self, capabilities: List[str]) -> List[ExecutionRequest]:
        requests = []
        for cap in capabilities:
            tool = self.registry.get(cap)
            if tool:
                requests.append(ExecutionRequest(
                    capability=cap,
                    arguments={}, # Default args for now
                    cacheable=tool.contract.cacheable
                ))
            else:
                # If exact name not found, try to find a match
                for t in self.registry.get_all():
                    if cap.lower() in t.name.lower():
                        requests.append(ExecutionRequest(
                            capability=t.name,
                            arguments={},
                            cacheable=t.contract.cacheable
                        ))
                        break
        return requests


class Executor:
    """
    Executes a concrete ExecutionRequest deterministically.
    Uses an ExecutionQueue for asynchronous readiness.
    Enforces Preconditions and returns CapabilityResult.
    """
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry
        self.event_bus = get_event_bus()
        self._execution_cache: Dict[str, AgentObservation] = {}

    def execute_queue(self, requests: List[ExecutionRequest], platform_result: Any) -> List[AgentObservation]:
        """Process a queue of execution requests."""
        observations = []
        
        # Instantiate adapter once (Fail-fast if not compatible)
        try:
            adapter = PlatformResultAdapter(platform_result)
        except Exception as e:
            # If the platform result has no context (e.g. repo not loaded), fail all requests gracefully.
            for req in requests:
                obs = AgentObservation(
                    tool=req.capability,
                    arguments=req.arguments,
                    latency_ms=0,
                    output=PreconditionFailure(capability=req.capability, missing_repository_state=[str(e)])
                )
                observations.append(obs)
            return observations
            
        for req in requests:
            self.event_bus.publish("ToolStarted", "executor", tool=req.capability)
            
            # Check cache
            cache_key = f"{req.capability}_{json.dumps(req.arguments, sort_keys=True)}"
            if req.cacheable and cache_key in self._execution_cache:
                obs = self._execution_cache[cache_key]
                obs = AgentObservation(
                    tool=obs.tool,
                    arguments=obs.arguments,
                    latency_ms=0.5, # near instant cache hit
                    output=obs.output,
                    confidence=obs.confidence,
                    evidence_ids=obs.evidence_ids,
                    timestamp=time.time(),
                    cache_hit=True
                )
                self.event_bus.publish("ToolFinished", "executor", tool=req.capability, latency=obs.latency_ms, success=True, cache_hit=True)
                observations.append(obs)
                continue

            obs = self._execute_single(req, adapter)
            
            if req.cacheable and not isinstance(obs.output, PreconditionFailure):
                self._execution_cache[cache_key] = obs
                
            success = not isinstance(obs.output, PreconditionFailure)
            self.event_bus.publish("ToolFinished", "executor", tool=req.capability, latency=obs.latency_ms, success=success, cache_hit=False)
            observations.append(obs)
            
        return observations

    def _execute_single(self, action: ExecutionRequest, adapter: PlatformResultAdapter) -> AgentObservation:
        tool_spec = self.registry.get(action.capability)
        if not tool_spec:
            pf = PreconditionFailure(
                capability=action.capability,
                recommended_capabilities=["TopContributors", "Ownership"]
            )
            return AgentObservation(tool=action.capability, arguments=action.arguments, latency_ms=0, output=pf)

        start_time = time.perf_counter_ns()
        
        # 1. Enforce preconditions
        contract = tool_spec.contract
        repo_summary = adapter.repository_summary()
        
        provenance = CapabilityProvenance(
            measurement=",".join(contract.required_measurements),
            stage="executor",
            timestamp=time.time(),
            snapshot_id=repo_summary.get("repository", "unknown"),
            confidence=1.0,
            algorithm=contract.id,
            adapter_version=getattr(adapter, "version", ""),
            source_snapshot=repo_summary.get("repository", "unknown"),
            source_commit_window=repo_summary.get("commit_window", 0),
        )
        
        if contract.implemented != CapabilityStatus.IMPLEMENTED:
            # Handle PLANNED / EXPERIMENTAL gracefully
            res = CapabilityResult(
                capability_id=contract.id,
                status="NOT_IMPLEMENTED",
                confidence=0.0,
                summary=f"This capability '{action.capability}' is registered but not yet implemented.",
                evidence_ids=[],
                raw_output=None,
                normalized_output=None,
                warnings=["Capability not implemented."],
                recommendations=[],
                metadata={"status": contract.implemented.name},
                execution_time_ms=(time.perf_counter_ns() - start_time) / 1e6,
                provenance=provenance
            )
            return AgentObservation(tool=action.capability, arguments=action.arguments, latency_ms=res.execution_time_ms, output=res)

        # 2. Execute capability deterministically via Adapter
        raw_data = None
        status = "SUCCESS"
        error_msg = ""
        
        try:
            time.sleep(contract.expected_latency_ms / 1000.0)
            
            # Map Capability IDs to adapter methods dynamically
            method_map = {
                "cap_top_contributors": adapter.top_contributors,
                "cap_ownership": adapter.ownership,
                "cap_bus_factor": adapter.bus_factor,
                "cap_health": adapter.health,
                "cap_forecast": adapter.forecast,
                "cap_causal_analysis": adapter.causal,
                "cap_knowledge_graph": adapter.knowledge_graph,
                "cap_dev_departure_simulation": adapter.simulation,
                "cap_ownership_simulation": adapter.simulation,
                "cap_architecture_simulation": adapter.simulation,
                "cap_forecast_simulation": adapter.simulation,
                "cap_risk_simulation": adapter.simulation,
                "cap_simulation": adapter.simulation,
            }
            
            if contract.id in method_map:
                raw_data = method_map[contract.id]()
            else:
                status = "ERROR"
                error_msg = f"Execution for '{action.capability}' (id: {contract.id}) is not mapped in Executor."
                raw_data = {"error": error_msg}
                
        except Exception as e:
            status = "ERROR"
            error_msg = str(e)
            raw_data = {"error": error_msg}

        # 3. Interpret into Domain Report
        domain_report = None
        explanation = None
        if status == "SUCCESS":
            interpreter = INTERPRETERS.get(contract.id)
            if interpreter:
                domain_report = interpreter.interpret(raw_data, contract)
                explanation = Explanation(
                    why=f"Derived from {len(contract.required_measurements)} deterministic measurements.",
                    how=f"Interpreted via {interpreter.__class__.__name__}",
                    derived_from=contract.required_measurements,
                    confidence_reason="Directly extracted from validated Platform DTOs."
                )

        latency = (time.perf_counter_ns() - start_time) / 1e6
        
        evidence_id = str(uuid.uuid4())[:8]

        # 3. Return Standardized CapabilityResult
        res = CapabilityResult(
            capability_id=contract.id,
            status=status,
            confidence=tool_spec.confidence,
            summary=f"Successfully executed {action.capability}" if status == "SUCCESS" else f"Failed to execute {action.capability}: {error_msg}",
            evidence_ids=[evidence_id],
            raw_output=raw_data,
            normalized_output=raw_data,
            warnings=[],
            recommendations=[],
            metadata={},
            execution_time_ms=latency,
            provenance=provenance,
            report=domain_report,
            explanation=explanation
        )

        return AgentObservation(
            tool=action.capability,
            arguments=action.arguments,
            latency_ms=latency,
            output=res,
            confidence=tool_spec.confidence,
            evidence_ids=[evidence_id],
            timestamp=time.time()
        )
