import dataclasses
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

@dataclasses.dataclass
class TelemetryStage:
    name: str
    start_time: float
    end_time: Optional[float] = None
    latency_ms: float = 0.0
    tokens: int = 0
    cost: float = 0.0
    status: str = "PENDING"
    error: Optional[str] = None
    details: Dict = dataclasses.field(default_factory=dict)

@dataclasses.dataclass
class AgentTelemetry:
    session_id: str
    run_id: str
    start_time: float
    end_time: Optional[float] = None
    total_latency_ms: float = 0.0
    total_tokens: int = 0
    total_cost: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    provider_retries: int = 0
    provider_failovers: int = 0
    tool_count: int = 0
    iteration_count: int = 0
    stages: List[TelemetryStage] = dataclasses.field(default_factory=list)
    
    def finish(self, end_time: float):
        self.end_time = end_time
        self.total_latency_ms = (end_time - self.start_time)
        # Recalculate totals from stages
        self.total_tokens = sum(s.tokens for s in self.stages)
        self.total_cost = sum(s.cost for s in self.stages)
        self.tool_count = len([s for s in self.stages if s.name.startswith("Executor")])

class TelemetryCollector:
    """Collects and exports hierarchical telemetry for benchmarking and observability."""
    def __init__(self, output_dir: str = "outputs/telemetry"):
        self.output_dir = output_dir
        self.active_runs: Dict[str, AgentTelemetry] = {}
        
    def start_run(self, session_id: str, run_id: str, start_time: float) -> None:
        self.active_runs[run_id] = AgentTelemetry(session_id=session_id, run_id=run_id, start_time=start_time)
        
    def end_run(self, run_id: str, end_time: float) -> None:
        if run_id in self.active_runs:
            run = self.active_runs[run_id]
            run.finish(end_time)
            self._export(run)
            del self.active_runs[run_id]

    def add_stage(self, run_id: str, stage: TelemetryStage) -> None:
        if run_id in self.active_runs:
            self.active_runs[run_id].stages.append(stage)
            
    def record_metric(self, run_id: str, metric_name: str, increment: int = 1) -> None:
        if run_id in self.active_runs:
            run = self.active_runs[run_id]
            if hasattr(run, metric_name):
                setattr(run, metric_name, getattr(run, metric_name) + increment)

    def _export(self, telemetry: AgentTelemetry) -> None:
        os.makedirs(self.output_dir, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"run_{telemetry.run_id}_{timestamp}.json")
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(dataclasses.asdict(telemetry), f, indent=2)
        except Exception:
            pass

_global_collector = TelemetryCollector()

def get_telemetry_collector() -> TelemetryCollector:
    return _global_collector
