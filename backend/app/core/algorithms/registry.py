"""
PIA Algorithm Registry.

Algorithms are first-class engineering objects in PIA.
Every deterministic heuristic that produces a Measurement must register here.

Registering an algorithm exposes:
  - Inputs, outputs, formula (for Measurement Explorer)
  - Version history (for algorithm comparison)
  - Benchmark accuracy scores (for quality tracking)
  - Consumer list (which projections/rules depend on this)
  - Diagnostic metadata (latency, memory, confidence range)

Adding a new algorithm or bumping a version requires NO changes to ProjectionEngine or QueryService.
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class AlgorithmInput:
    name: str
    type: str
    description: str
    required: bool = True
    example: Any = None


@dataclass
class AlgorithmOutput:
    name: str
    type: str
    description: str
    unit: Optional[str] = None


@dataclass
class AlgorithmBenchmark:
    dataset_id: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    evaluated_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z")
    notes: str = ""


@dataclass
class AlgorithmDefinition:
    """
    A registered, versioned algorithm definition.
    Immutable after registration — new versions create new entries.
    """
    algorithm_id: str
    name: str
    version: str
    description: str
    formula: str
    inputs: List[AlgorithmInput] = field(default_factory=list)
    outputs: List[AlgorithmOutput] = field(default_factory=list)
    normalization: str = ""
    confidence_range: tuple = (0.0, 1.0)
    thresholds: Dict[str, float] = field(default_factory=dict)
    consumers: List[str] = field(default_factory=list)   # projection/rule names that use this
    benchmarks: List[AlgorithmBenchmark] = field(default_factory=list)
    registered_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z")
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False
    superseded_by: Optional[str] = None   # algorithm_id of successor version

    # Runtime diagnostics (populated at execution time)
    avg_latency_ms: float = 0.0
    avg_memory_mb: float = 0.0
    failure_count: int = 0
    execution_count: int = 0


class AlgorithmRegistry:
    """
    Global registry of all versioned algorithms used in PIA.
    Prefer the module-level singleton `_registry` over creating new instances.
    """

    def __init__(self):
        self._algorithms: Dict[str, AlgorithmDefinition] = {}  # algorithm_id -> definition
        self._by_name: Dict[str, List[str]] = {}               # name -> [algorithm_ids sorted by version]

    def register(self, definition: AlgorithmDefinition) -> None:
        """Register a new algorithm or version. Duplicate algorithm_ids are rejected."""
        if definition.algorithm_id in self._algorithms:
            raise ValueError(f"Algorithm '{definition.algorithm_id}' is already registered. "
                             f"Bump the version and use a new algorithm_id.")
        self._algorithms[definition.algorithm_id] = definition
        self._by_name.setdefault(definition.name, []).append(definition.algorithm_id)

    def get(self, algorithm_id: str) -> Optional[AlgorithmDefinition]:
        return self._algorithms.get(algorithm_id)

    def get_latest(self, name: str) -> Optional[AlgorithmDefinition]:
        """Return the most recently registered version of an algorithm by name."""
        ids = self._by_name.get(name, [])
        if not ids:
            return None
        return self._algorithms[ids[-1]]

    def get_all_versions(self, name: str) -> List[AlgorithmDefinition]:
        return [self._algorithms[i] for i in self._by_name.get(name, [])]

    def list_all(self) -> List[AlgorithmDefinition]:
        return list(self._algorithms.values())

    def record_execution(self, algorithm_id: str, latency_ms: float,
                          memory_mb: float, failed: bool = False) -> None:
        """Update runtime diagnostics for an algorithm. Called by the measurement pipeline."""
        algo = self._algorithms.get(algorithm_id)
        if algo is None:
            return
        n = algo.execution_count
        algo.avg_latency_ms = (algo.avg_latency_ms * n + latency_ms) / (n + 1)
        algo.avg_memory_mb = (algo.avg_memory_mb * n + memory_mb) / (n + 1)
        algo.execution_count += 1
        if failed:
            algo.failure_count += 1


# ─────────────────────────────────────────────────────────
# Module-level singleton + built-in PIA algorithm registrations
# ─────────────────────────────────────────────────────────

_registry = AlgorithmRegistry()


def get_algorithm_registry() -> AlgorithmRegistry:
    return _registry


def _register_builtin_algorithms() -> None:
    """Register all core PIA measurement algorithms at startup."""
    algorithms = [
        AlgorithmDefinition(
            algorithm_id="bus_factor_v1",
            name="bus_factor",
            version="1.0",
            description="Measures the minimum number of developers whose departure would significantly impair the project.",
            formula="BusFactor = min{k : top-k contributors own ≥ threshold% of commits}",
            inputs=[
                AlgorithmInput("commits", "List[Commit]", "Commit history for the window"),
                AlgorithmInput("threshold", "float", "Ownership concentration threshold (default 0.50)"),
            ],
            outputs=[AlgorithmOutput("bus_factor", "int", "Minimum team size for bus factor risk")],
            normalization="Clamped to [1, team_size]",
            thresholds={"critical": 1.0, "warning": 2.0},
            consumers=["KnowledgeGraphProjection", "RiskProjection"],
            tags=["ownership", "risk", "team"],
        ),
        AlgorithmDefinition(
            algorithm_id="ownership_gini_v1",
            name="ownership_gini",
            version="1.0",
            description="Gini coefficient measuring commit ownership concentration across developers.",
            formula="Gini = (2 * sum(i * x_i) / (n * sum(x_i))) - (n+1)/n",
            inputs=[
                AlgorithmInput("commit_counts", "Dict[developer, int]", "Per-developer commit counts"),
            ],
            outputs=[AlgorithmOutput("gini", "float", "Gini coefficient [0=equal, 1=fully concentrated]")],
            normalization="Bounded [0, 1]",
            consumers=["OwnershipProjection", "KnowledgeGraphProjection"],
            tags=["ownership", "concentration"],
        ),
        AlgorithmDefinition(
            algorithm_id="knowledge_concentration_v1",
            name="knowledge_concentration",
            version="1.0",
            description="Measures how concentrated file ownership is across developers for a module or file set.",
            formula="KnowledgeConcentration = Σ(file_ownership_fraction² for each developer)",
            inputs=[
                AlgorithmInput("file_ownership", "Dict[file, Dict[developer, fraction]]", "Per-file ownership distribution"),
            ],
            outputs=[AlgorithmOutput("concentration", "float", "Herfindahl-Hirschman concentration score")],
            normalization="Bounded [0, 1]",
            consumers=["KnowledgeGraphProjection", "RiskProjection"],
            tags=["knowledge", "ownership", "risk"],
        ),
        AlgorithmDefinition(
            algorithm_id="expertise_score_v1",
            name="expertise_score",
            version="1.0",
            description="Measures a developer's expertise in a module based on recency-weighted commit contributions.",
            formula="ExpertiseScore = Σ(recency_weight(t) * commit_complexity(c))",
            inputs=[
                AlgorithmInput("commits", "List[Commit]", "Commits by the developer in the module"),
                AlgorithmInput("decay_factor", "float", "Recency decay factor (default 0.95/month)"),
            ],
            outputs=[AlgorithmOutput("expertise_score", "float", "Expertise score [0, 1]")],
            normalization="Normalized against max score in repository",
            consumers=["ExpertiseProjection", "OwnershipProjection"],
            tags=["expertise", "developer", "knowledge"],
        ),
        AlgorithmDefinition(
            algorithm_id="transfer_risk_v1",
            name="transfer_risk",
            version="1.0",
            description="Measures the risk of knowledge loss if a specific developer departs.",
            formula="TransferRisk = BusFactor * KnowledgeConcentration * ExpertiseScore",
            inputs=[
                AlgorithmInput("bus_factor", "int", "Bus factor for affected modules"),
                AlgorithmInput("knowledge_concentration", "float", "Knowledge concentration score"),
                AlgorithmInput("expertise_scores", "Dict[developer, float]", "Developer expertise scores"),
            ],
            outputs=[AlgorithmOutput("transfer_risk", "float", "Transfer risk score [0, 1]")],
            normalization="Normalized to [0, 1] against worst-case scenario",
            consumers=["RiskProjection"],
            tags=["risk", "transfer", "departure"],
        ),
    ]
    for algo in algorithms:
        _registry.register(algo)


# Register built-in algorithms at import time
_register_builtin_algorithms()
