from typing import Any
from dataclasses import asdict, is_dataclass
from app.core.api.contracts import RuntimePipelineResult

class PlatformCompatibilityException(Exception):
    """Raised when the PlatformResult is missing required base context sections."""
    pass

class MissingMeasurementException(Exception):
    """Raised when a specific measurement or context is missing from the PlatformResult."""
    pass

class PlatformResultAdapter:
    """
    Exclusive interface for accessing deterministic intelligence from the PlatformRuntime.
    No code outside this adapter may inspect RuntimePipelineResult directly.
    """
    version = "v1"

    def __init__(self, result: RuntimePipelineResult):
        self._result = result
        self._context = getattr(result, "context", None)
        
        self._verify_compatibility()

    def _verify_compatibility(self) -> None:
        """Verifies that the underlying platform context meets M57.13 requirements."""
        if self._context is None:
            raise PlatformCompatibilityException("PlatformResult has no context.")
        
        # We enforce that these core intelligence objects exist (even if None) to ensure
        # we are running against a compatible v1 PlatformRuntime pipeline.
        required_sections = [
            "org_intelligence",
            "forecast_context",
            "causal_context",
            "simulation_context",
            "knowledge_graph"
        ]
        
        for section in required_sections:
            if not hasattr(self._context, section):
                raise PlatformCompatibilityException(f"PlatformContext is missing required section: '{section}'")

    def organization(self) -> Any:
        val = getattr(self._context, "org_intelligence", None)
        if val is None:
            raise MissingMeasurementException("Organization intelligence is missing.")
        return asdict(val) if is_dataclass(val) else val

    def top_contributors(self) -> dict:
        observations = getattr(self._context, "observations", [])
        from collections import Counter
        counter = Counter()
        for obs in observations:
            for actor in obs.actors:
                counter[actor.id] += 1
        return {
            "contributors": [
                {"name": author, "commits": count}
                for author, count in counter.most_common(10)
            ]
        }

    def ownership(self) -> Any:
        val = getattr(self._context, "org_intelligence", None)
        if val is None:
            raise MissingMeasurementException("Organization intelligence is missing.")
        return val

    def bus_factor(self) -> Any:
        val = getattr(self._context, "org_intelligence", None)
        if val is None:
            raise MissingMeasurementException("Organization intelligence is missing.")
        return val

    def expertise(self) -> Any:
        return self.organization()

    def health(self) -> Any:
        val = getattr(self._context, "org_intelligence", None)
        if val is None:
            raise MissingMeasurementException("Organization intelligence is missing.")
        return val

    def forecast(self) -> Any:
        val = getattr(self._context, "forecast_context", None)
        if val is None:
            raise MissingMeasurementException("Forecast context is missing.")
        return val

    def causal(self) -> Any:
        val = getattr(self._context, "causal_context", None)
        if val is None:
            raise MissingMeasurementException("Causal context is missing.")
        return val

    def simulation(self) -> Any:
        val = getattr(self._context, "simulation_context", None)
        if val is None:
            raise MissingMeasurementException("Simulation context is missing.")
        return val

    def knowledge_graph(self) -> Any:
        val = getattr(self._context, "knowledge_graph", None)
        if val is None:
            raise MissingMeasurementException("Knowledge graph is missing.")
        return val

    def repository_summary(self) -> dict:
        return {
            "repository": getattr(self._context, "repository", "unknown"),
            "branch": getattr(self._context, "branch", "unknown"),
            "commit_window": getattr(self._context, "commit_limit", 0),
        }
