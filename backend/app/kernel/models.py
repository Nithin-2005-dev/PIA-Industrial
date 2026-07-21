import dataclasses
import hashlib
import json
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple


# ─────────────────────────────────────────────
# Enumerations (defined first, used by all dataclasses)
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class RuntimeVersion:
    runtime_version: str
    prompt_version: str
    policy_version: str
    benchmark_version: str

class Intent(Enum):
    GENERAL_CHAT = "general_chat"
    SYSTEM_PLATFORM = "system_platform"
    SYSTEM_RUNTIME = "system_runtime"
    REPOSITORY_QUERY = "repository_query"
    HYBRID_QUERY = "hybrid_query"

class Goal(Enum):
    FIND_PERSON = "find_person"
    FIND_OWNER = "find_owner"
    FIND_CONTRIBUTOR = "find_contributor"
    SIMULATE_DEPARTURE = "simulate_departure"
    SIMULATE_ARCHITECTURE = "simulate_architecture"
    SIMULATE_FORECAST = "simulate_forecast"
    SIMULATE_RISK = "simulate_risk"
    VISUALIZE_GRAPH = "visualize_graph"
    COMPARE = "compare"
    EXPLAIN = "explain"
    FORECAST = "forecast"
    SUMMARIZE = "summarize"
    ANALYZE = "analyze"
    IDENTIFY_RISK = "identify_risk"
    DIAGNOSE_CAUSALITY = "diagnose_causality"
    UNKNOWN = "unknown"

class EntityType(Enum):
    PERSON = "person"
    MODULE = "module"
    TOPIC = "topic"
    FILE = "file"
    DIRECTORY = "directory"
    PACKAGE = "package"
    FUNCTION = "function"
    CLASS = "class"
    UNKNOWN = "unknown"

class Scope(Enum):
    ORGANIZATION = "organization"
    REPOSITORY = "repository"
    FILE = "file"
    COMPONENT = "component"
    SUBSYSTEM = "subsystem"


class CognitiveTopic(Enum):
    ORGANIZATION = "organization"
    FORECAST = "forecast"
    SIMULATION = "simulation"
    OPTIMIZATION = "optimization"
    CAUSAL = "causal"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    EXECUTIVE = "executive"
    EXPERTISE = "expertise"
    REPOSITORY = "repository"
    GENERAL_KNOWLEDGE = "general_knowledge"

class CapabilityStatus(Enum):
    REGISTERED = "REGISTERED"
    IMPLEMENTED = "IMPLEMENTED"
    EXPERIMENTAL = "EXPERIMENTAL"
    DEPRECATED = "DEPRECATED"
    PLANNED = "PLANNED"
    DISABLED = "DISABLED"


class VerificationStatus(Enum):
    VERIFIED = "Verified"
    PARTIALLY_VERIFIED = "Partially Verified"
    UNVERIFIED = "Unverified"


class ExecutionNodeState(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


class CommunicationMode(Enum):
    AUTO = "auto"
    EXECUTIVE = "executive"
    ENGINEER = "engineer"
    RESEARCHER = "researcher"
    TEACHER = "teacher"
    STUDENT = "student"


class NarrativeComplexity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ExecutionComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class ExecutionStatus(Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    RUNTIME_FAILURE = "RUNTIME_FAILURE"
    KNOWLEDGE_FAILURE = "KNOWLEDGE_FAILURE"
    CAPABILITY_MISSING = "CAPABILITY_MISSING"
    NO_EVIDENCE = "NO_EVIDENCE"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"


@dataclasses.dataclass(frozen=True)
class ExecutionFailureReason:
    stage: str
    code: str
    message: str
    retry_after: Optional[int] = None


@dataclasses.dataclass(frozen=True)
class PipelineCostEstimate:
    estimated_latency_ms: float
    estimated_tokens: int
    estimated_memory_mb: float
    estimated_cost: float


@dataclasses.dataclass(frozen=True)
class PipelineStrategy:
    id: str
    description: str
    requires_reasoning: bool
    requires_optimizer: bool
    requires_llm: bool
    presentation_plugin: str
    priority: int
    complexity: ExecutionComplexity
    supported_topics: Tuple[CognitiveTopic, ...] = ()
    supported_goals: Tuple[Goal, ...] = ()
# ─────────────────────────────────────────────
# Tool Interface
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class CapabilityContract:
    id: str
    name: str
    description: str
    inputs: dict
    output_type: Any = dict
    deterministic: bool = True
    implemented: CapabilityStatus = CapabilityStatus.IMPLEMENTED
    repeatable: bool = False
    cacheable: bool = False
    timeout_ms: int = 5000
    expected_latency_ms: int = 100
    estimated_token_cost: int = 0
    required_measurements: List[str] = dataclasses.field(default_factory=list)
    required_repository_state: List[str] = dataclasses.field(default_factory=list)
    required_environment: List[str] = dataclasses.field(default_factory=list)
    postconditions: List[str] = dataclasses.field(default_factory=list)
    requires: List[str] = dataclasses.field(default_factory=list)
    produces: List[str] = dataclasses.field(default_factory=list)
    supported_goals: List[Goal] = dataclasses.field(default_factory=list)
    supported_entities: List[EntityType] = dataclasses.field(default_factory=list)
    supported_scopes: List[Scope] = dataclasses.field(default_factory=list)

@dataclasses.dataclass(frozen=True)
class CapabilityCard:
    """Defines a tool's semantic capability for the planner."""
    name: str
    description: str
    contract: CapabilityContract
    tags: List[str] = dataclasses.field(default_factory=list)
    aliases: List[str] = dataclasses.field(default_factory=list)
    cost: float = 0.0
    latency: float = 0.0
    confidence: float = 1.0
    staleness: float = 0.0
    dependencies: List[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass(frozen=True)
class AgentAction:
    """A tool call requested by the Agent Planner."""
    tool: str
    arguments: dict
    reasoning: Optional[str] = None

@dataclasses.dataclass(frozen=True)
class PreconditionFailure:
    capability: str
    missing_measurements: List[str] = dataclasses.field(default_factory=list)
    missing_repository_state: List[str] = dataclasses.field(default_factory=list)
    missing_environment: List[str] = dataclasses.field(default_factory=list)
    recommended_capabilities: List[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass(frozen=True)
class DomainReport:
    version: str = "v1"
    executive_summary: Optional[dict] = None

@dataclasses.dataclass(frozen=True)
class HealthReport(DomainReport):
    overall_health: float = 0.0
    health_grade: str = ""
    critical_modules: int = 0
    warning_modules: int = 0
    healthy_modules: int = 0
    ownership_summary: dict = dataclasses.field(default_factory=dict)
    knowledge_risk_summary: dict = dataclasses.field(default_factory=dict)
    bus_factor_summary: dict = dataclasses.field(default_factory=dict)
    coverage_summary: dict = dataclasses.field(default_factory=dict)
    forecast_summary: dict = dataclasses.field(default_factory=dict)
    confidence: float = 1.0

@dataclasses.dataclass(frozen=True)
class TopContributorReport(DomainReport):
    contributors: List[dict] = dataclasses.field(default_factory=list)
    confidence: float = 1.0

@dataclasses.dataclass(frozen=True)
class CapabilityQualityContract:
    coverage: float = 0.0
    completeness: float = 0.0
    freshness: float = 0.0
    confidence: float = 0.0
    missing_data: tuple[str, ...] = dataclasses.field(default_factory=tuple)
    limitations: tuple[str, ...] = dataclasses.field(default_factory=tuple)
    supported_queries: tuple[str, ...] = dataclasses.field(default_factory=tuple)
    guaranteed_outputs: tuple[str, ...] = dataclasses.field(default_factory=tuple)
    known_limitations: tuple[str, ...] = dataclasses.field(default_factory=tuple)
    required_inputs: tuple[str, ...] = dataclasses.field(default_factory=tuple)

@dataclasses.dataclass(frozen=True)
class GraphView:
    name: str
    metadata: dict = dataclasses.field(default_factory=dict)

@dataclasses.dataclass(frozen=True)
class ConnectedComponentView(GraphView):
    components: tuple[tuple[str, ...], ...] = dataclasses.field(default_factory=tuple)

@dataclasses.dataclass(frozen=True)
class CommunityView(GraphView):
    communities: tuple[tuple[str, ...], ...] = dataclasses.field(default_factory=tuple)

@dataclasses.dataclass(frozen=True)
class OwnershipView(GraphView):
    ownership_graph: dict = dataclasses.field(default_factory=dict)

@dataclasses.dataclass(frozen=True)
class ExpertiseView(GraphView):
    expertise_graph: dict = dataclasses.field(default_factory=dict)

@dataclasses.dataclass(frozen=True)
class DependencyView(GraphView):
    dependency_chains: tuple[tuple[str, ...], ...] = dataclasses.field(default_factory=tuple)
    critical_paths: tuple[str, ...] = dataclasses.field(default_factory=tuple)

@dataclasses.dataclass(frozen=True)
class InfluenceView(GraphView):
    central_nodes: dict = dataclasses.field(default_factory=dict)
    influence_metrics: dict = dataclasses.field(default_factory=dict)

@dataclasses.dataclass(frozen=True)
class ModuleRiskProfile:
    module: str
    bus_factor: int
    owners: tuple[str, ...] = dataclasses.field(default_factory=tuple)
    contributors: tuple[str, ...] = dataclasses.field(default_factory=tuple)
    knowledge_concentration: float = 0.0
    criticality: str = "UNKNOWN"
    coverage: float = 0.0
    confidence: float = 0.0

@dataclasses.dataclass(frozen=True)
class OwnershipProfile:
    developer: str
    owned_modules: tuple[str, ...] = dataclasses.field(default_factory=tuple)
    ownership_score: float = 0.0
    dependency_score: float = 0.0
    successors: tuple[str, ...] = dataclasses.field(default_factory=tuple)
    reviewers: tuple[str, ...] = dataclasses.field(default_factory=tuple)
    risk: str = "UNKNOWN"

@dataclasses.dataclass(frozen=True)
class OwnershipReport(DomainReport):
    profiles: tuple[OwnershipProfile, ...] = dataclasses.field(default_factory=tuple)
    quality: Optional[CapabilityQualityContract] = None

@dataclasses.dataclass(frozen=True)
class BusFactorReport(DomainReport):
    profiles: tuple[ModuleRiskProfile, ...] = dataclasses.field(default_factory=tuple)
    quality: Optional[CapabilityQualityContract] = None

@dataclasses.dataclass(frozen=True)
class ForecastReport(DomainReport):
    health_forecast: dict = dataclasses.field(default_factory=dict)
    ownership_forecast: dict = dataclasses.field(default_factory=dict)
    bus_factor_forecast: dict = dataclasses.field(default_factory=dict)
    knowledge_forecast: dict = dataclasses.field(default_factory=dict)
    risk_forecast: dict = dataclasses.field(default_factory=dict)
    confidence: float = 1.0

@dataclasses.dataclass(frozen=True)
class KnowledgeGraphReport(DomainReport):
    metadata: dict = dataclasses.field(default_factory=dict)
    statistics: dict = dataclasses.field(default_factory=dict)
    views: tuple[GraphView, ...] = dataclasses.field(default_factory=tuple)
    relationships: tuple[dict, ...] = dataclasses.field(default_factory=tuple)
    provenance: dict = dataclasses.field(default_factory=dict)
    quality: Optional[CapabilityQualityContract] = None

@dataclasses.dataclass(frozen=True)
class SimulationReport(DomainReport):
    scenario: str = ""
    affected_modules: List[str] = dataclasses.field(default_factory=list)
    confidence: float = 1.0

@dataclasses.dataclass(frozen=True)
class DeveloperDepartureSimulationReport(SimulationReport):
    ownership_changes: dict = dataclasses.field(default_factory=dict)
    health_delta: float = 0.0
    bus_factor_delta: int = 0
    knowledge_loss: float = 0.0
    recommended_mitigations: List[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass(frozen=True)
class OwnershipSimulationReport(SimulationReport):
    ownership_changes: dict = dataclasses.field(default_factory=dict)

@dataclasses.dataclass(frozen=True)
class ArchitectureSimulationReport(SimulationReport):
    health_delta: float = 0.0

@dataclasses.dataclass(frozen=True)
class ForecastSimulationReport(SimulationReport):
    forecast_changes: dict = dataclasses.field(default_factory=dict)

@dataclasses.dataclass(frozen=True)
class RiskSimulationReport(SimulationReport):
    risk_delta: dict = dataclasses.field(default_factory=dict)

@dataclasses.dataclass(frozen=True)
class CausalReport(DomainReport):
    primary_root_cause: str = ""
    secondary_causes: List[str] = dataclasses.field(default_factory=list)
    causal_chain: List[str] = dataclasses.field(default_factory=list)
    confidence: float = 1.0
    counterfactuals: List[dict] = dataclasses.field(default_factory=list)

@dataclasses.dataclass(frozen=True)
class RepositoryReport(DomainReport):
    contributors: int = 0
    owners: int = 0
    subsystems: int = 0
    critical_modules: List[str] = dataclasses.field(default_factory=list)
    architectural_hotspots: List[str] = dataclasses.field(default_factory=list)
    knowledge_hotspots: List[str] = dataclasses.field(default_factory=list)
    review_bottlenecks: List[str] = dataclasses.field(default_factory=list)
    high_churn_modules: List[str] = dataclasses.field(default_factory=list)
    high_complexity_modules: List[str] = dataclasses.field(default_factory=list)
    dependency_hotspots: List[str] = dataclasses.field(default_factory=list)
    recent_changes: dict = dataclasses.field(default_factory=dict)
    active_teams: List[str] = dataclasses.field(default_factory=list)
    inactive_components: List[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass(frozen=True)
class Explanation:
    why: str = ""
    how: str = ""
    derived_from: List[str] = dataclasses.field(default_factory=list)
    limitations: List[str] = dataclasses.field(default_factory=list)
    confidence_reason: str = ""

@dataclasses.dataclass(frozen=True)
class CapabilityProvenance:
    measurement: str = ""
    stage: str = ""
    timestamp: float = 0.0
    snapshot_id: str = ""
    confidence: float = 1.0
    algorithm: str = ""
    adapter_version: str = ""
    source_snapshot: str = ""
    source_commit_window: int = 0

@dataclasses.dataclass(frozen=True)
class CapabilityResult:
    """Standardized deterministic result for all capabilities."""
    capability_id: str
    status: str
    confidence: float
    summary: str
    evidence_ids: List[str]
    raw_output: Any
    normalized_output: Any
    warnings: List[str]
    recommendations: List[str]
    metadata: dict
    execution_time_ms: float
    provenance: Optional[CapabilityProvenance] = None
    report: Optional[DomainReport] = None
    explanation: Optional[Explanation] = None
    visualization_data: Optional[dict] = None

@dataclasses.dataclass(frozen=True)
class AgentObservation:
    """The output of an executor action, containing either a CapabilityResult or PreconditionFailure."""
    tool: str
    arguments: dict
    latency_ms: float
    output: Any  # Should be CapabilityResult or PreconditionFailure
    confidence: float = 1.0
    evidence_ids: List[str] = dataclasses.field(default_factory=list)
    timestamp: float = dataclasses.field(default_factory=time.time)
    cache_hit: bool = False

@dataclasses.dataclass(frozen=True)
class ExecutionRequest:
    capability: str
    arguments: dict
    reasoning: Optional[str] = None
    cacheable: bool = False

@dataclasses.dataclass(frozen=True)
class RuntimeEvent:
    event_type: str
    stage: str
    timestamp: float
    data: dict = dataclasses.field(default_factory=dict)

@dataclasses.dataclass(frozen=True)
class PlanningPolicy:
    max_tokens: int = 20000
    cache_policy: bool = True

@dataclasses.dataclass(frozen=True)
class ExecutionPolicy:
    max_cost: float = 5.0
    max_time: float = 120.0

@dataclasses.dataclass(frozen=True)
class ReflectionPolicy:
    reflection_threshold: float = 0.8
    verification_threshold: float = 0.9

@dataclasses.dataclass(frozen=True)
class ProviderPolicy:
    provider_priority: List[str] = dataclasses.field(default_factory=lambda: ["gemini-2.5-flash", "gemini-2.5-pro"])
    retry_policy: int = 3

@dataclasses.dataclass(frozen=True)
class StoppingPolicy:
    max_iterations: int = 6

@dataclasses.dataclass(frozen=True)
class AgentPolicy:
    planning: PlanningPolicy = dataclasses.field(default_factory=PlanningPolicy)
    execution: ExecutionPolicy = dataclasses.field(default_factory=ExecutionPolicy)
    reflection: ReflectionPolicy = dataclasses.field(default_factory=ReflectionPolicy)
    provider: ProviderPolicy = dataclasses.field(default_factory=ProviderPolicy)
    stopping: StoppingPolicy = dataclasses.field(default_factory=StoppingPolicy)

@dataclasses.dataclass(frozen=True)
class RepositoryMemory:
    facts: Tuple[str, ...] = ()
    observations: Tuple[AgentObservation, ...] = ()
    evidence: Tuple[str, ...] = ()
    semantic_summary: Optional[str] = None

@dataclasses.dataclass(frozen=True)
class AgentMemory:
    goals: Tuple[str, ...] = ()
    constraints: Tuple[str, ...] = ()
    hypotheses: Tuple[str, ...] = ()
    rejected_hypotheses: Tuple[str, ...] = ()
    completed_actions: Tuple[str, ...] = ()
    pending_actions: Tuple[str, ...] = ()
    failures: Tuple[str, ...] = ()
    questions: Tuple[str, ...] = ()

@dataclasses.dataclass(frozen=True)
class ConversationMemory:
    history: Tuple[Any, ...] = ()
    preferences: dict = dataclasses.field(default_factory=dict)
    communication_mode: CommunicationMode = CommunicationMode.AUTO

@dataclasses.dataclass(frozen=True)
class PlannerConfidence:
    topic_confidence: float = 1.0
    tool_confidence: float = 1.0
    missing_evidence_probability: float = 0.0


# ─────────────────────────────────────────────
# Semantic Query & Goal Graph
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Entity:
    type: EntityType
    value: str
    confidence: float = 1.0

@dataclasses.dataclass(frozen=True)
class ParserConfidence:
    goal: float = 1.0
    entities: float = 1.0
    scope: float = 1.0
    overall: float = 1.0
    ambiguity: bool = False
    requires_clarification: bool = False

@dataclasses.dataclass(frozen=True)
class Constraint:
    type: str
    value: Any

@dataclasses.dataclass(frozen=True)
class SemanticQuery:
    semantic_memory_id: str
    intent: Intent
    goals: List[Goal] = dataclasses.field(default_factory=list)
    topics: List[str] = dataclasses.field(default_factory=list)
    keywords: List[str] = dataclasses.field(default_factory=list)
    entities: List[Entity] = dataclasses.field(default_factory=list)
    scope: Scope = Scope.REPOSITORY
    constraints: List[Constraint] = dataclasses.field(default_factory=list)
    preferences: dict = dataclasses.field(default_factory=dict)
    time_horizon: str = "current"
    output_format: str = "text"
    conversation_entities: List[Entity] = dataclasses.field(default_factory=list)
    resolved_entities: List[Entity] = dataclasses.field(default_factory=list)
    parser_confidence: Optional[ParserConfidence] = None

@dataclasses.dataclass(frozen=True)
class GoalNode:
    id: str
    goal: Goal
    inputs: List[Entity] = dataclasses.field(default_factory=list)
    outputs: List[str] = dataclasses.field(default_factory=list)
    success_criteria: List[str] = dataclasses.field(default_factory=list)
    dependencies: List[str] = dataclasses.field(default_factory=list)
    status: ExecutionNodeState = ExecutionNodeState.PENDING
    confidence: float = 1.0

@dataclasses.dataclass(frozen=True)
class GoalGraph:
    nodes: Tuple[GoalNode, ...]
    edges: Tuple[Tuple[str, str], ...] = ()
    dependencies: dict = dataclasses.field(default_factory=dict)

    def hash(self) -> str:
        # A deterministic hash representing semantic convergence
        node_strs = sorted([f"{n.goal.name}:{','.join(sorted([e.value for e in n.inputs]))}" for n in self.nodes])
        edge_strs = sorted([f"{f}->{t}" for f, t in self.edges])
        content = "|".join(node_strs) + "||" + "|".join(edge_strs)
        return hashlib.sha256(content.encode()).hexdigest()

@dataclasses.dataclass(frozen=True)
class ExecutionTemplate:
    """Pre-registered capability chains for specific goals."""
    name: str
    chain: List[str]

@dataclasses.dataclass(frozen=True)
class CapabilityCandidate:
    """A scored capability ready for the planner."""
    card: CapabilityCard
    why_selected: str
    score: float
    confidence: float
    estimated_latency: float
    estimated_cost: float
    satisfied_goals: List[Goal]
    available: bool = True
    missing_prerequisites: List[str] = dataclasses.field(default_factory=list)
    diagnostics: Dict[str, Any] = dataclasses.field(default_factory=dict)

@dataclasses.dataclass(frozen=True)
class PlanningMemory:
    rejected_plans: List[str] = dataclasses.field(default_factory=list)
    completed_goals: List[Goal] = dataclasses.field(default_factory=list)
    failed_capabilities: List[str] = dataclasses.field(default_factory=list)
    planner_critiques: List[str] = dataclasses.field(default_factory=list)
    iterations: int = 0

# ─────────────────────────────────────────────
# Intent & Goal
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class IntentClassification:
    """Classification of the user query intent."""
    intent: Intent
    confidence: float
    reason: str
    requires_repository: bool
    topics: Tuple[CognitiveTopic, ...] = ()


@dataclasses.dataclass(frozen=True)
class CognitiveGoal:
    """Represents the user's intent."""
    query: str
    classification: Optional[IntentClassification] = None


# ─────────────────────────────────────────────
# Semantic Planning Graph (DAG)
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class RejectedCapability:
    name: str
    reason: str

@dataclasses.dataclass(frozen=True)
class RequiredCapability:
    name: str
    confidence: float
    reason: str
    required_measurements: List[str] = dataclasses.field(default_factory=list)
    dependencies: List[str] = dataclasses.field(default_factory=list)
    rejected_capabilities: List[RejectedCapability] = dataclasses.field(default_factory=list)

@dataclasses.dataclass(frozen=True)
class ExecutionNode:
    """A semantic node in the execution DAG. Never names concrete tools."""
    id: str
    semantic_goal: str                          # e.g. "assess organization health"
    dependencies: Tuple[str, ...] = ()          # IDs of nodes this depends on
    required_capabilities: Tuple[CognitiveTopic, ...] = ()
    state: ExecutionNodeState = ExecutionNodeState.PENDING


@dataclasses.dataclass(frozen=True)
class ExecutionGraph:
    """Directed Acyclic Graph of semantic execution nodes."""
    nodes: Tuple[ExecutionNode, ...]
    edges: Tuple[Tuple[str, str], ...] = ()     # (from_id, to_id)

    def get_node(self, node_id: str) -> Optional[ExecutionNode]:
        for n in self.nodes:
            if n.id == node_id:
                return n
        return None

    def root_nodes(self) -> Tuple[ExecutionNode, ...]:
        """Nodes with no dependencies."""
        dep_ids = {to for _, to in self.edges}
        return tuple(n for n in self.nodes if n.id not in dep_ids)


# ─────────────────────────────────────────────
# Reflection
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class ReflectionResult:
    """Structured output of the ReflectionEngine. Never a prose paragraph."""
    assumptions: Tuple[str, ...]
    missing_evidence: Tuple[str, ...]
    alternative_explanations: Tuple[str, ...]
    unsupported_claims: Tuple[str, ...]
    contradictions: Tuple[str, ...]
    followup_questions: Tuple[str, ...]
    confidence_delta: float     # Negative = reflection reduced confidence
    should_replan: bool         # If True, PolicyEngine may trigger a second pass


# ─────────────────────────────────────────────
# Confidence (computed, never LLM-assigned)
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class AnswerConfidence:
    """Computed confidence from 5 normalized [0,1] components."""
    evidence_coverage: float
    verification_score: float
    planner_completion: float
    reflection_score: float
    reasoning_consistency: float

    @property
    def overall(self) -> float:
        return (
            self.evidence_coverage *
            self.verification_score *
            self.planner_completion *
            self.reflection_score *
            self.reasoning_consistency
        )

    def format(self) -> str:
        return (
            f"Evidence Coverage      {self.evidence_coverage:.2f}\n"
            f"Verification Score     {self.verification_score:.2f}\n"
            f"Planner Completion     {self.planner_completion:.2f}\n"
            f"Reflection Score       {self.reflection_score:.2f}\n"
            f"Reasoning Consistency  {self.reasoning_consistency:.2f}\n"
            f"─────────────────────────────\n"
            f"Overall Confidence     {self.overall:.2f}"
        )


# ─────────────────────────────────────────────
# Observability
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class CognitiveTrace:
    """Per-stage observability trace."""
    stage: str
    execution_time_ms: float
    token_usage: int
    prompt_version: str
    decision: str
    output_summary: str
    input_hash: str     # Deterministic replay without storing full payloads
    output_hash: str
    cache_hit: bool = False

@dataclasses.dataclass(frozen=True)
class StageResult:
    """Detailed contract and diagnostics for a pipeline stage."""
    stage_id: str
    stage_name: str
    status: str
    expected_input: str
    expected_output: str
    actual_output: str
    duration_ms: float
    diagnostics: Dict[str, Any]
    reason: Optional[str] = None


def _hash(obj: Any) -> str:
    """Compute a deterministic SHA-256 hash for any JSON-serializable object."""
    try:
        return hashlib.sha256(json.dumps(obj, default=str, sort_keys=True).encode()).hexdigest()[:16]
    except Exception:
        return "unhashable"


# ─────────────────────────────────────────────
# Prompt Artifacts & Context
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class PromptArtifact:
    """Structured data extracted from deterministic results, safe for LLM context."""
    id: str
    title: str
    summary: str
    evidence_ids: List[str]
    confidence: float
    data: Dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True)
class PromptContext:
    """The bundled context passed to the LLM containing artifacts and system instructions."""
    system_prompt: str
    user_query: str
    artifacts: List[PromptArtifact]
    intent: Optional[Intent] = None
    workspace_session: Optional["WorkspaceSession"] = None
    history: List["CognitiveAnswer"] = dataclasses.field(default_factory=list)


# ─────────────────────────────────────────────
# Verification
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Critique:
    """A single critique of an LLM-generated claim."""
    claim: str
    verification_status: VerificationStatus
    confidence_score: float
    reason: str


@dataclasses.dataclass(frozen=True)
class VerificationResult:
    """The final verified output after dropping unsupported claims."""
    original_text: str
    verified_text: str
    critiques: List[Critique]
    dropped_claims: int
    workspace_session: Optional["WorkspaceSession"] = None

    @property
    def verified_claims(self) -> int:
        return len(self.critiques) - self.dropped_claims


# ─────────────────────────────────────────────
# Reasoning Output
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class CognitiveAnswer:
    """The final result of an LLM reasoning cycle."""
    query: str
    response: str
    verification: VerificationResult


# ─────────────────────────────────────────────
# Legacy Plan (kept for backward compat, replaced by ExecutionGraph)
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class ReasoningPlan:
    """Deprecated: flat tool list. Use ExecutionGraph instead."""
    goal: str
    selected_tools: List[str]
    rationale: str


# ─────────────────────────────────────────────
# Evidence
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class RetrievedEvidence:
    """A wrapper for evidence fetched by the retriever."""
    artifacts: List[PromptArtifact]


# ─────────────────────────────────────────────
# Executive Output
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class ExecutiveResponse:
    """The final synthesized response ready for the user."""
    executive_summary: str
    technical_summary: str
    actionable_recommendations: List[str]
    supporting_evidence: List[str]
    confidence: float
    risks: List[str]
    alternative_strategies: List[str]


# ─────────────────────────────────────────────
# Immutable Execution State (replaces CognitiveContext)
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class ExecutionState:
    """
    The single immutable state object shared across all cognitive stages.
    Every stage returns a new ExecutionState via dataclasses.replace().
    This enables deterministic replay, branching, and time-travel debugging.
    """
    goal: CognitiveGoal
    classification: IntentClassification
    platform_result: Any
    
    # Agent Loop State
    runtime_version: Optional[RuntimeVersion] = None
    repository_memory: RepositoryMemory = dataclasses.field(default_factory=RepositoryMemory)
    agent_memory: AgentMemory = dataclasses.field(default_factory=AgentMemory)
    conversation_memory: ConversationMemory = dataclasses.field(default_factory=ConversationMemory)
    current_iteration: int = 0
    prompt_budget: int = 20000
    tool_history: Tuple[str, ...] = ()
    planner_confidence: Optional[PlannerConfidence] = None
    
    # Legacy/Synthesis State
    execution_graph: Optional[ExecutionGraph] = None
    retrieved_evidence: Optional[RetrievedEvidence] = None
    prompt_context: Optional[PromptContext] = None
    
    # Semantic Pipeline State (M57.15+)
    semantic_query: Optional[SemanticQuery] = None
    goal_graph: Optional[GoalGraph] = None
    candidate_set: Tuple[CapabilityCandidate, ...] = ()
    planning_memory: PlanningMemory = dataclasses.field(default_factory=PlanningMemory)
    answer: Optional[CognitiveAnswer] = None
    reflection: Optional[ReflectionResult] = None
    confidence: Optional[AnswerConfidence] = None
    reasoning_trace: Tuple[CognitiveTrace, ...] = ()
    executive_response: Optional[ExecutiveResponse] = None
    status: ExecutionStatus = ExecutionStatus.SUCCESS
    failure_reason: Optional[ExecutionFailureReason] = None
    stage_results: Tuple[StageResult, ...] = ()
    query_id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))


# ─────────────────────────────────────────────
# Session Memory (mutable — spans multiple turns)
# ─────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class WorkspaceSession:
    """Complete active workspace context. Replaces active_repository_context string."""
    repository: str
    branch: str = "main"
    commit_window: int = 50
    repository_size: str = "Unknown"
    commit_count: int = 0
    languages: List[str] = dataclasses.field(default_factory=list)
    frameworks: List[str] = dataclasses.field(default_factory=list)
    package_manager: str = "Unknown"
    build_system: str = "Unknown"
    root_modules: List[str] = dataclasses.field(default_factory=list)
    architecture_summary: str = "Unknown"
    loaded_layers: List[str] = dataclasses.field(default_factory=list)
    current_runtime_version: str = "M57.12"
    loaded_capabilities: int = 0
    analysis_timestamp: str = dataclasses.field(default_factory=lambda: datetime.utcnow().isoformat())
    available_measurements: Tuple[str, ...] = ()
    cached_metrics: Dict[str, Any] = dataclasses.field(default_factory=dict)
    analysis_snapshot: Optional[str] = None
    metadata: Dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class CognitiveSession:
    """Maintains short-term conversation memory and session state."""
    session_id: str
    communication_mode: CommunicationMode = CommunicationMode.AUTO
    user_preferences: Dict[str, Any] = dataclasses.field(default_factory=dict)
    workspace_session: Optional[WorkspaceSession] = None
    previous_repositories: List[str] = dataclasses.field(default_factory=list)
    last_goal: Optional[str] = None
    last_selected_capabilities: List[str] = dataclasses.field(default_factory=list)
    last_retrieved_artifacts: List[str] = dataclasses.field(default_factory=list)
    reasoning_summaries: List[str] = dataclasses.field(default_factory=list)
    history: List[CognitiveAnswer] = dataclasses.field(default_factory=list)

    @property
    def active_repository(self) -> Optional[str]:
        """Convenience accessor for the current repository name."""
        return self.workspace_session.repository if self.workspace_session else None

    def set_repository(self, repo_session: WorkspaceSession) -> None:
        if self.workspace_session and self.workspace_session.repository != repo_session.repository:
            self.previous_repositories.append(self.workspace_session.repository)
        self.workspace_session = repo_session

    def add_answer(
        self,
        answer: CognitiveAnswer,
        tools_used: List[str] = None,
        artifacts: List[str] = None
    ) -> None:
        self.history.append(answer)
        self.last_goal = answer.query
        if tools_used:
            self.last_selected_capabilities = tools_used
        if artifacts:
            self.last_retrieved_artifacts = artifacts
        # Store compact reasoning summary (not full prompt)
        if answer.response:
            self.reasoning_summaries.append(answer.response[:200])


# ─────────────────────────────────────────────
# Backward-compat alias (used by legacy code paths in runtime.py)
# ─────────────────────────────────────────────

@dataclasses.dataclass
class CognitiveContext:
    """Deprecated: legacy state container. Use ExecutionState instead."""
    session: CognitiveSession
    platform_result: Any
    goal: Optional[CognitiveGoal] = None
    plan: Optional[ReasoningPlan] = None
    retrieved_evidence: Optional[RetrievedEvidence] = None
    prompt_context: Optional[PromptContext] = None
    answer: Optional[CognitiveAnswer] = None
    executive_response: Optional[ExecutiveResponse] = None
