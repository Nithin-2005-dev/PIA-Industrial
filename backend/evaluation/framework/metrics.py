from typing import List, Tuple
from pydantic import BaseModel
from evaluation.framework.manifest import PerformancePolicy
from app.kernel.models import ExecutionState

class LayerMetrics(BaseModel):
    planner_time_ms: int = 0
    graph_time_ms: int = 0
    reasoning_time_ms: int = 0
    presentation_time_ms: int = 0

class CoverageMetrics(BaseModel):
    covered_capabilities: List[str] = []
    missing_capabilities: List[str] = []

class MetricsEngine:
    """
    Extracts performance metrics from an ExecutionState and compares against a PerformancePolicy.
    """
    @staticmethod
    def extract_metrics(state: ExecutionState) -> LayerMetrics:
        metrics = LayerMetrics()
        
        # Note: We can expand this with real latency logic when tracing is enabled
        if hasattr(state, "stage_results"):
            for result in state.stage_results:
                duration = result.duration_ms
                if "planner" in result.stage_name.lower() or "planning" in result.stage_name.lower():
                    metrics.planner_time_ms += int(duration)
                elif "graph" in result.stage_name.lower():
                    metrics.graph_time_ms += int(duration)
                elif "reasoning" in result.stage_name.lower() or "rule" in result.stage_name.lower():
                    metrics.reasoning_time_ms += int(duration)
                elif "presentation" in result.stage_name.lower() or "synthesizer" in result.stage_name.lower():
                    metrics.presentation_time_ms += int(duration)
                
        return metrics

    @staticmethod
    def extract_coverage(state: ExecutionState, expected_all_caps: List[str] = None) -> CoverageMetrics:
        expected = expected_all_caps or ["TopContributors", "Ownership", "BusFactor", "Forecast", "Transfer", "Health"]
        covered = []
        if state.tool_history:
            for tool in state.tool_history:
                if tool not in covered:
                    covered.append(tool)
        
        missing = [cap for cap in expected if cap not in covered]
        return CoverageMetrics(covered_capabilities=covered, missing_capabilities=missing)

    @staticmethod
    def check_budgets(metrics: LayerMetrics, policy: PerformancePolicy) -> dict[str, bool]:
        return {
            "planner_budget": metrics.planner_time_ms <= policy.planner_ms,
            "graph_budget": metrics.graph_time_ms <= policy.graph_ms,
            "reasoning_budget": metrics.reasoning_time_ms <= policy.reasoning_ms,
            "presentation_budget": metrics.presentation_time_ms <= policy.presentation_ms
        }
