from app.intelligence.legacy.ownership_service import (
    OwnershipService,
)

from app.intelligence.risk.bus_factor_service import (
    BusFactorService,
)

from .knowledge_risk import (
    KnowledgeRisk,
)

from .policies.knowledge_risk_policy import (
    KnowledgeRiskPolicy,
)


from typing import Any
class KnowledgeRiskService:

    def __init__(
        self,
        ownership_service: OwnershipService,
        bus_factor_service: BusFactorService,
        policy: KnowledgeRiskPolicy,
        graph_service: Any = None,
    ):
        self._ownership_service = ownership_service
        self._bus_factor_service = bus_factor_service
        self._policy = policy
        self._graph_service = graph_service

    def analyze(
        self,
        module_id: str,
    ) -> KnowledgeRisk:
        return self.analyze_transitive_risk(module_id)

    def analyze_transitive_risk(
        self, 
        module_id: str, 
        visited: set[str] | None = None
    ) -> KnowledgeRisk:
        """
        Recursively calculates the Transitive Blast Radius (Phase 33).
        A module's true risk is the maximum of its own direct risk and the risks 
        of all modules it critically depends on.
        """
        if visited is None:
            visited = set()

        if module_id in visited:
            # Handle cycle by returning a low risk placeholder, since cycle means we already evaluated this path
            from app.intelligence.risk.bus_factor import BusFactor
            from app.intelligence.risk.risk_level import RiskLevel
            return KnowledgeRisk(
                module_ref=module_id,
                risk_level=RiskLevel.LOW,
                bus_factor=99,
                ownership_count=99,
                summary="Cycle detected, breaking.",
            )

        visited.add(module_id)

        # 1. Calculate the Direct Risk
        ownership = self._ownership_service.owners_of(module_id)
        bus_factor = self._bus_factor_service.analyze(module_id)
        direct_risk = self._policy.evaluate(bus_factor, len(ownership))

        # 2. Fetch Dependencies
        # We look for DEPENDS_ON edges where source == module_id
        edges = self._graph_service.outgoing(module_id)
        dependencies = [
            edge.target_id for edge in edges 
            if getattr(edge, 'relationship', None) == "depends_on"
        ]

        # 3. Calculate Transitive Risks recursively
        max_risk = direct_risk
        
        _risk_ranks = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        for dep_id in dependencies:
            dep_risk = self.analyze_transitive_risk(dep_id, visited)
            # Compare risks (HIGH > MEDIUM > LOW)
            if _risk_ranks[dep_risk.risk_level.value] > _risk_ranks[max_risk.risk_level.value]:
                max_risk = KnowledgeRisk(
                    module_ref=module_id, # We bubble it up to the current module!
                    risk_level=dep_risk.risk_level,
                    bus_factor=dep_risk.bus_factor,
                    ownership_count=dep_risk.ownership_count,
                    summary=f"Transitive Risk Alert: Inherited critical risk from dependency '{dep_id}'. {dep_risk.summary}",
                )

        return max_risk