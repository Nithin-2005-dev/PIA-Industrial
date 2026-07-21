from typing import Dict, List, Optional, Any
from .models import (
    CapabilityCard, CapabilityContract, CapabilityStatus,
    TopContributorReport, OwnershipReport, BusFactorReport,
    HealthReport, ForecastReport, SimulationReport, CausalReport,
    KnowledgeGraphReport, DeveloperDepartureSimulationReport,
    OwnershipSimulationReport, ArchitectureSimulationReport,
    ForecastSimulationReport, RiskSimulationReport,
    Goal, EntityType, Scope, ExecutionTemplate
)

class CapabilityRegistry:
    """Central registry of semantic capabilities (tools) available to the cognitive layer."""
    
    def __init__(self):
        self._tools: Dict[str, CapabilityCard] = {}
        self._register_defaults()
        
    def _register_defaults(self):
        # M57.9: Register standard deterministic pipeline tools with explicit schemas
        
        self.register(CapabilityCard(
            name="TopContributors",
            description="Retrieve top contributors and their expertise metrics.",
            contract=CapabilityContract(
                id="cap_top_contributors",
                name="TopContributors",
                description="Retrieve top contributors and their expertise metrics.",
                inputs={"top_k": {"type": "integer"}},
                output_type=TopContributorReport,
                deterministic=True,
                implemented=CapabilityStatus.IMPLEMENTED,
                repeatable=False,
                cacheable=True,
                timeout_ms=5000,
                expected_latency_ms=50,
                estimated_token_cost=0,
                required_measurements=["expertise_metrics"],
                required_repository_state=["loaded"],
                required_environment=[],
                postconditions=["Returns valid expertise list"],
                requires=[],
                produces=["contributors_metrics"],
                supported_goals=[Goal.FIND_PERSON, Goal.FIND_CONTRIBUTOR],
                supported_entities=[EntityType.PERSON, EntityType.MODULE, EntityType.FILE, EntityType.DIRECTORY],
                supported_scopes=[Scope.REPOSITORY, Scope.COMPONENT, Scope.FILE]
            ),
            tags=["expertise", "developer", "author", "contributor"],
            aliases=["Find Top Developer", "Get Key Authors"],
            cost=0.01,
            latency=50
        ))
        
        self.register(CapabilityCard(
            name="Ownership",
            description="Retrieve ownership concentration and code authorship metrics.",
            contract=CapabilityContract(
                id="cap_ownership",
                name="Ownership",
                description="Retrieve ownership concentration and code authorship metrics.",
                inputs={"module_path": {"type": "string"}},
                output_type=OwnershipReport,
                deterministic=True,
                implemented=CapabilityStatus.IMPLEMENTED,
                repeatable=False,
                cacheable=True,
                timeout_ms=5000,
                expected_latency_ms=100,
                estimated_token_cost=0,
                required_measurements=["ownership_metrics"],
                required_repository_state=["loaded"],
                required_environment=[],
                postconditions=[],
                requires=["contributors_metrics"],
                produces=["ownership_metrics"],
                supported_goals=[Goal.FIND_OWNER, Goal.ANALYZE],
                supported_entities=[EntityType.PERSON, EntityType.MODULE, EntityType.FILE, EntityType.DIRECTORY, EntityType.PACKAGE],
                supported_scopes=[Scope.REPOSITORY, Scope.COMPONENT, Scope.FILE, Scope.ORGANIZATION]
            ),
            tags=["ownership", "concentration", "maintainer"],
            aliases=["Find Ownership", "Who owns this"],
            cost=0.02,
            latency=100
        ))
        
        self.register(CapabilityCard(
            name="BusFactor",
            description="Retrieve bus factor risks.",
            contract=CapabilityContract(
                id="cap_bus_factor",
                name="BusFactor",
                description="Retrieve bus factor risks.",
                inputs={},
                output_type=BusFactorReport,
                deterministic=True,
                implemented=CapabilityStatus.IMPLEMENTED,
                repeatable=False,
                cacheable=True,
                timeout_ms=5000,
                expected_latency_ms=50,
                estimated_token_cost=0,
                required_measurements=["bus_factor_metrics"],
                required_repository_state=["loaded"],
                required_environment=[],
                postconditions=[],
                requires=["ownership_metrics", "contributors_metrics"],
                produces=["bus_factor_metrics"],
                supported_goals=[Goal.IDENTIFY_RISK, Goal.ANALYZE],
                supported_entities=[EntityType.MODULE, EntityType.FILE, EntityType.DIRECTORY, EntityType.PACKAGE],
                supported_scopes=[Scope.REPOSITORY, Scope.COMPONENT, Scope.ORGANIZATION]
            ),
            tags=["risk", "bus factor", "knowledge loss"],
            aliases=["Calculate Bus Factor"],
            cost=0.01,
            latency=50
        ))

        self.register(CapabilityCard(
            name="Health",
            description="Retrieve overall repository health and technical debt metrics.",
            contract=CapabilityContract(
                id="cap_health",
                name="Health",
                description="Retrieve overall repository health and technical debt metrics.",
                inputs={},
                output_type=HealthReport,
                deterministic=True,
                implemented=CapabilityStatus.IMPLEMENTED,
                repeatable=False,
                cacheable=True,
                timeout_ms=5000,
                expected_latency_ms=150,
                estimated_token_cost=0,
                required_measurements=["health_metrics"],
                required_repository_state=["loaded"],
                required_environment=[],
                postconditions=[],
                requires=["bus_factor_metrics", "ownership_metrics"],
                produces=["health_metrics"],
                supported_goals=[Goal.SUMMARIZE, Goal.ANALYZE],
                supported_entities=[EntityType.MODULE, EntityType.FILE, EntityType.PACKAGE, EntityType.TOPIC],
                supported_scopes=[Scope.REPOSITORY, Scope.COMPONENT]
            ),
            tags=["health", "technical debt", "quality"],
            aliases=["System Health", "Repo Quality"],
            cost=0.03,
            latency=150
        ))

        self.register(CapabilityCard(
            name="Forecast",
            description="Retrieve predictive forecasts for organizational health or productivity trends.",
            contract=CapabilityContract(
                id="cap_forecast",
                name="Forecast",
                description="Retrieve predictive forecasts for organizational health or productivity trends.",
                inputs={"horizon_days": {"type": "integer"}},
                output_type=ForecastReport,
                deterministic=True,
                implemented=CapabilityStatus.IMPLEMENTED,
                repeatable=False,
                cacheable=True,
                timeout_ms=5000,
                expected_latency_ms=200,
                estimated_token_cost=0,
                required_measurements=["temporal_history"],
                required_repository_state=["loaded"],
                required_environment=[],
                postconditions=["forecast_available"],
                requires=["health_metrics"],
                produces=["forecast_metrics"],
                supported_goals=[Goal.FORECAST],
                supported_entities=[EntityType.MODULE, EntityType.FILE, EntityType.PACKAGE, EntityType.TOPIC],
                supported_scopes=[Scope.REPOSITORY, Scope.COMPONENT]
            ),
            tags=["future", "predict", "trend"],
            aliases=["Predict Future", "Extrapolate"],
            cost=0.05,
            latency=200
        ))
        
        self.register(CapabilityCard(
            name="DeveloperDepartureSimulation",
            description="Simulate the counterfactual impact of a developer leaving the project.",
            contract=CapabilityContract(
                id="cap_dev_departure_simulation",
                name="DeveloperDepartureSimulation",
                description="Simulate what happens if a developer leaves.",
                inputs={"developer_id": {"type": "string"}},
                output_type=DeveloperDepartureSimulationReport,
                deterministic=True,
                implemented=CapabilityStatus.IMPLEMENTED,
                repeatable=False,
                cacheable=True,
                timeout_ms=10000,
                expected_latency_ms=500,
                estimated_token_cost=0,
                required_measurements=["simulation_model"],
                required_repository_state=["loaded"],
                required_environment=[],
                postconditions=[],
                requires=[],
                produces=[],
                supported_goals=[Goal.SIMULATE_DEPARTURE],
                supported_entities=[EntityType.PERSON],
                supported_scopes=[Scope.ORGANIZATION, Scope.REPOSITORY]
            ),
            tags=["what if", "scenario", "counterfactual", "leaves", "departure", "quit"],
            aliases=["Run Simulation", "What happens if"],
            cost=0.10,
            latency=500
        ))

        self.register(CapabilityCard(
            name="OwnershipSimulation",
            description="Simulate the impact of ownership changes.",
            contract=CapabilityContract(
                id="cap_ownership_simulation",
                name="OwnershipSimulation",
                description="Simulate ownership modifications.",
                inputs={"scenario_name": {"type": "string"}},
                output_type=OwnershipSimulationReport,
                deterministic=True,
                implemented=CapabilityStatus.IMPLEMENTED,
                repeatable=False,
                cacheable=True,
                timeout_ms=10000,
                expected_latency_ms=500,
                estimated_token_cost=0,
                required_measurements=["simulation_model"],
                required_repository_state=["loaded"],
                required_environment=[],
                postconditions=[],
                requires=[],
                produces=[],
                supported_goals=[Goal.SIMULATE_ARCHITECTURE],
                supported_entities=[EntityType.MODULE, EntityType.PERSON],
                supported_scopes=[Scope.ORGANIZATION, Scope.REPOSITORY]
            ),
            tags=["what if", "scenario", "ownership change"],
            aliases=["Simulate Ownership"],
            cost=0.10,
            latency=500
        ))

        self.register(CapabilityCard(
            name="ArchitectureSimulation",
            description="Simulate the impact of architectural changes.",
            contract=CapabilityContract(
                id="cap_architecture_simulation",
                name="ArchitectureSimulation",
                description="Simulate architecture refactoring or component removal.",
                inputs={"scenario_name": {"type": "string"}},
                output_type=ArchitectureSimulationReport,
                deterministic=True,
                implemented=CapabilityStatus.IMPLEMENTED,
                repeatable=False,
                cacheable=True,
                timeout_ms=10000,
                expected_latency_ms=500,
                estimated_token_cost=0,
                required_measurements=["simulation_model"],
                required_repository_state=["loaded"],
                required_environment=[],
                postconditions=[],
                requires=[],
                produces=[],
                supported_goals=[Goal.SIMULATE_ARCHITECTURE],
                supported_entities=[EntityType.MODULE],
                supported_scopes=[Scope.REPOSITORY]
            ),
            tags=["what if", "scenario", "refactor", "remove module"],
            aliases=["Simulate Architecture"],
            cost=0.10,
            latency=500
        ))

        self.register(CapabilityCard(
            name="ForecastSimulation",
            description="Simulate forecast trends under different assumptions.",
            contract=CapabilityContract(
                id="cap_forecast_simulation",
                name="ForecastSimulation",
                description="Simulate alternate forecast realities.",
                inputs={"scenario_name": {"type": "string"}},
                output_type=ForecastSimulationReport,
                deterministic=True,
                implemented=CapabilityStatus.IMPLEMENTED,
                repeatable=False,
                cacheable=True,
                timeout_ms=10000,
                expected_latency_ms=500,
                estimated_token_cost=0,
                required_measurements=["simulation_model"],
                required_repository_state=["loaded"],
                required_environment=[],
                postconditions=[],
                requires=[],
                produces=[],
                supported_goals=[Goal.SIMULATE_FORECAST],
                supported_entities=[EntityType.MODULE, EntityType.FILE],
                supported_scopes=[Scope.REPOSITORY]
            ),
            tags=["what if", "scenario", "forecast"],
            aliases=["Simulate Forecast"],
            cost=0.10,
            latency=500
        ))

        self.register(CapabilityCard(
            name="RiskSimulation",
            description="Simulate risk impact like bus factor changes.",
            contract=CapabilityContract(
                id="cap_risk_simulation",
                name="RiskSimulation",
                description="Simulate bus factor or knowledge risks.",
                inputs={"scenario_name": {"type": "string"}},
                output_type=RiskSimulationReport,
                deterministic=True,
                implemented=CapabilityStatus.IMPLEMENTED,
                repeatable=False,
                cacheable=True,
                timeout_ms=10000,
                expected_latency_ms=500,
                estimated_token_cost=0,
                required_measurements=["simulation_model"],
                required_repository_state=["loaded"],
                required_environment=[],
                postconditions=[],
                requires=[],
                produces=[],
                supported_goals=[Goal.SIMULATE_RISK],
                supported_entities=[EntityType.MODULE, EntityType.FILE],
                supported_scopes=[Scope.REPOSITORY]
            ),
            tags=["what if", "scenario", "bus factor change"],
            aliases=["Simulate Risk"],
            cost=0.10,
            latency=500
        ))
        
        self.register(CapabilityCard(
            name="CausalAnalysis",
            description="Retrieve causal explanations, root cause analysis, and evidence links.",
            contract=CapabilityContract(
                id="cap_causal_analysis",
                name="CausalAnalysis",
                description="Retrieve causal explanations, root cause analysis, and evidence links.",
                inputs={"symptom": {"type": "string"}},
                output_type=CausalReport,
                deterministic=True,
                implemented=CapabilityStatus.IMPLEMENTED,
                repeatable=False,
                cacheable=True,
                timeout_ms=5000,
                expected_latency_ms=300,
                estimated_token_cost=0,
                required_measurements=["causal_graph"],
                required_repository_state=["loaded"],
                required_environment=[],
                postconditions=[],
                requires=[],
                produces=[],
                supported_goals=[Goal.DIAGNOSE_CAUSALITY],
                supported_entities=[EntityType.MODULE, EntityType.TOPIC],
                supported_scopes=[Scope.REPOSITORY, Scope.COMPONENT]
            ),
            tags=["why", "root cause", "explanation"],
            aliases=["Find Cause", "Why did this happen"],
            cost=0.08,
            latency=300
        ))
        
        self.register(CapabilityCard(
            name="KnowledgeGraph",
            description="Retrieve topological relationships between developers, code, and expertise.",
            contract=CapabilityContract(
                id="cap_knowledge_graph",
                name="KnowledgeGraph",
                description="Retrieve topological relationships between developers, code, and expertise.",
                inputs={"node_id": {"type": "string"}, "depth": {"type": "integer"}},
                output_type=KnowledgeGraphReport,
                deterministic=True,
                implemented=CapabilityStatus.IMPLEMENTED,
                repeatable=False,
                cacheable=True,
                timeout_ms=5000,
                expected_latency_ms=250,
                estimated_token_cost=0,
                required_measurements=["knowledge_graph_model"],
                required_repository_state=["loaded"],
                required_environment=[],
                postconditions=[],
                requires=[],
                produces=[],
                supported_goals=[Goal.VISUALIZE_GRAPH, Goal.FIND_PERSON],
                supported_entities=[EntityType.PERSON, EntityType.MODULE, EntityType.CLASS, EntityType.FUNCTION],
                supported_scopes=[Scope.REPOSITORY, Scope.COMPONENT]
            ),
            tags=["topology", "graph", "relationships", "dependencies"],
            aliases=["Map Graph", "Find Relations"],
            cost=0.05,
            latency=250
        ))

        # Register Execution Templates (Chains)
        self.register_template(ExecutionTemplate(
            name="Ownership Chain",
            chain=["cap_ownership", "cap_bus_factor"]
        ))
        
        self.register_template(ExecutionTemplate(
            name="Simulation Chain",
            chain=["cap_ownership", "cap_dev_departure_simulation", "cap_forecast"]
        ))
        
        self.register_template(ExecutionTemplate(
            name="Health Chain",
            chain=["cap_health", "cap_forecast", "cap_risk_simulation"]
        ))

        # ΓöÇΓöÇΓöÇ IDE-Style PLANNED Capabilities ΓöÇΓöÇΓöÇ
        
        self.register(CapabilityCard(
            name="SymbolSearch",
            description="Search for symbols (classes, functions, variables) across the repository.",
            contract=CapabilityContract(
                id="cap_symbol_search",
                name="SymbolSearch",
                description="Search for symbols across the repository.",
                inputs={"symbol_name": {"type": "string"}},
                output_type=dict,
                deterministic=True,
                implemented=CapabilityStatus.PLANNED,
                repeatable=False,
                cacheable=True,
                timeout_ms=2000,
                expected_latency_ms=100,
                estimated_token_cost=0,
                required_measurements=[],
                required_repository_state=["indexed"],
                required_environment=["indexed_repository"],
                postconditions=[],
                requires=[],
                produces=[]
            ),
            tags=["symbol", "search", "find", "code"],
            aliases=["Find Symbol", "Search Code"],
            cost=0.0,
            latency=100
        ))

        self.register(CapabilityCard(
            name="FindUsages",
            description="Find all usages/references of a specific symbol.",
            contract=CapabilityContract(
                id="cap_find_usages",
                name="FindUsages",
                description="Find all usages of a specific symbol.",
                inputs={"symbol_id": {"type": "string"}},
                output_type=dict,
                deterministic=True,
                implemented=CapabilityStatus.PLANNED,
                repeatable=False,
                cacheable=True,
                timeout_ms=2000,
                expected_latency_ms=150,
                estimated_token_cost=0,
                required_measurements=[],
                required_repository_state=["indexed"],
                required_environment=["indexed_repository"],
                postconditions=[],
                requires=[],
                produces=[]
            ),
            tags=["usage", "reference", "find", "callers"],
            aliases=["Find References", "Who calls this"],
            cost=0.0,
            latency=150
        ))

        self.register(CapabilityCard(
            name="CompareBranches",
            description="Compare two branches for semantic differences.",
            contract=CapabilityContract(
                id="cap_compare_branches",
                name="CompareBranches",
                description="Compare two branches for semantic differences.",
                inputs={"base_branch": {"type": "string"}, "head_branch": {"type": "string"}},
                output_type=dict,
                deterministic=True,
                implemented=CapabilityStatus.PLANNED,
                repeatable=False,
                cacheable=True,
                timeout_ms=5000,
                expected_latency_ms=500,
                estimated_token_cost=0,
                required_measurements=[],
                required_repository_state=["loaded"],
                required_environment=[],
                postconditions=[],
                requires=[],
                produces=[]
            ),
            tags=["compare", "branch", "diff"],
            aliases=["Compare", "Diff Branches"],
            cost=0.0,
            latency=500
        ))

    def register(self, tool: CapabilityCard) -> None:
        self._tools[tool.name] = tool
        
    def register_template(self, template: ExecutionTemplate) -> None:
        if not hasattr(self, '_templates'):
            self._templates = {}
        self._templates[template.name] = template

    def get_all(self) -> List[CapabilityCard]:
        return list(self._tools.values())
        
    def get(self, name: str) -> Optional[CapabilityCard]:
        return self._tools.get(name)

    def get_templates(self) -> List[ExecutionTemplate]:
        return list(getattr(self, '_templates', {}).values())
