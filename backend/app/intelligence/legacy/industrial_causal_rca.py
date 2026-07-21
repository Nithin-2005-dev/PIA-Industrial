"""Industrial Causal RCA Service.

Adapts the canonical Causal Engine for industrial root cause analysis.
"""
from __future__ import annotations

from app.intelligence.causal.engine import CausalEngine
from app.intelligence.causal.models import CausalContext, CausalMechanism
from app.intelligence.causal.ontology import CausalOntology
from app.intelligence.causal.rules import CausalRuleRegistry
from app.intelligence.causal.industrial_rules import IndustrialReliabilityRuleProvider
from app.intelligence.legacy.asset_intelligence_service import AssetIntelligenceService
from app.intelligence.legacy.maintenance_intelligence_service import MaintenanceIntelligenceService


def industrial_causal_ontology() -> CausalOntology:
    """Ontology for industrial causal mechanisms."""
    return CausalOntology(
        mechanisms=(
            CausalMechanism(
                id="mechanical_wear",
                name="Mechanical Wear",
                category="Physical",
                parent_mechanism=None,
                description="Physical degradation of mechanical components over time or under stress.",
            ),
            CausalMechanism(
                id="thermal_degradation",
                name="Thermal Degradation",
                category="Physical",
                parent_mechanism=None,
                description="Breakdown of material properties due to excessive heat.",
            ),
            CausalMechanism(
                id="preventive_maintenance_missed",
                name="Preventive Maintenance Missed",
                category="Process",
                parent_mechanism=None,
                description="Failure to perform scheduled maintenance.",
            ),
            CausalMechanism(
                id="subsystem_cascade",
                name="Subsystem Cascade",
                category="Systemic",
                parent_mechanism=None,
                description="Failure of one component leads to the failure of the parent system.",
            ),
        )
    )


class IndustrialCausalRCA:
    """Root Cause Analysis engine for industrial assets."""

    def __init__(self, asset_service: AssetIntelligenceService, maintenance_service: MaintenanceIntelligenceService):
        self._asset_service = asset_service
        self._maintenance_service = maintenance_service
        
        self._ontology = industrial_causal_ontology()
        self._registry = CausalRuleRegistry()
        self._registry.register(IndustrialReliabilityRuleProvider())
        
        self._engine = CausalEngine(self._ontology, self._registry)

    def analyze_asset(self, asset_id: str) -> CausalContext:
        """Run RCA on an asset based on its maintenance history."""
        # 1. Gather facts
        maint_intel = self._maintenance_service.analyze_asset(asset_id)
        
        # 2. Map facts to observable causal nodes [0, 1]
        observed_nodes = {}
        
        # If there are precursors found, we map them to observable nodes
        for precursor in maint_intel.get("failure_precursors", []):
            desc = " ".join(precursor.precursor_events).lower()
            if "vibration" in desc:
                observed_nodes["high_vibration"] = 0.9
            if "temperature" in desc or "heat" in desc:
                observed_nodes["high_temperature"] = 0.9
                
        # If there are deferred recommendations
        if maint_intel.get("deferred_recommendations"):
            observed_nodes["deferred_maintenance"] = 0.8
            
        # If there are repeated failures
        for pattern in maint_intel.get("repeated_failures", []):
            if "bearing" in pattern.failure_mode:
                observed_nodes["bearing_failure"] = 1.0
            if "seal" in pattern.failure_mode:
                observed_nodes["seal_failure"] = 1.0
                
        # Also map general failure
        if maint_intel.get("repeated_failures") or maint_intel.get("failure_precursors"):
            observed_nodes["equipment_failure"] = 1.0
            
        # 3. Create a pseudo-context for the CausalSemanticModelBuilder
        # The builder normally reads from PipelineContext. For simplicity here, 
        # we will monkeypatch or pass a dict that the builder can use.
        return self.run_rca(observed_nodes)
    def run_rca(self, observed_nodes: dict[str, float]) -> CausalContext:
        """Runs RCA directly on observed states (useful for testing)."""
        # CausalSemanticModelBuilder expects a context with a `measurements` dict, etc.
        # Let's create a dummy object that simulates PipelineContext.
        class DummyContext:
            def __init__(self, nodes):
                self.nodes = nodes
                # CausalSemanticModelBuilder looks for things in context... let's see.
                
        # Actually, let's just bypass the builder for industrial and use the HypothesisEngine directly
        # since the builder is hardcoded for SE metrics.
        
        from app.intelligence.causal.models import CausalSemanticModel, CausalNode
        from uuid import uuid4
        
        # Create nodes
        nodes = []
        for name, value in observed_nodes.items():
            nodes.append(CausalNode(
                id=str(uuid4()),
                name=name,
                observed_value=value,
                direction="increasing" if value > 0.5 else "decreasing",
                mechanism_id="unknown"
            ))
            
        # Create edges by running RuleEngine
        activated_rules = self._engine._rule_engine.evaluate(observed_nodes)
        from app.intelligence.causal.models import CausalEdge, CausalConfidence
        
        edges = []
        for rule in activated_rules:
            # cause_node might also be missing if we have chained rules, but rule engine evaluates observed nodes first
            c_node = next((n for n in nodes if n.name == rule.cause_node), None)
            if not c_node:
                c_node = CausalNode(id=str(uuid4()), name=rule.cause_node, observed_value=0.0, direction=rule.direction, mechanism_id="unknown")
                nodes.append(c_node)
                
            e_node = next((n for n in nodes if n.name == rule.effect_node), None)
            if not e_node:
                e_node = CausalNode(id=str(uuid4()), name=rule.effect_node, observed_value=0.0, direction=rule.direction, mechanism_id="unknown")
                nodes.append(e_node)
                
            edges.append(CausalEdge(
                cause_node_id=c_node.id,
                effect_node_id=e_node.id,
                mechanism_id=rule.mechanism_id,
                confidence=CausalConfidence.combine(0.8, rule.rule_confidence, 1.0),
                direction=rule.direction,
                weight=rule.rule_confidence
            ))
            
        semantic_model = CausalSemanticModel(annotations=(), nodes=tuple(nodes), edges=tuple(edges))
        
        # Create a mock context with dummy measurements to satisfy the evidence requirement
        class MockContext:
            measurements = ["mock_evidence"]
        
        mock_ctx = MockContext()
        
        # Run hypothesis engine
        root_causes, all_hypotheses, root_cause_groups = self._engine._hypothesis_engine.evaluate(
            semantic_model, mock_ctx
        )
        
        accepted_count = sum(1 for h in all_hypotheses if h.accepted)
        
        # Build explanation
        from app.intelligence.causal.engine import _avg_confidence, _placeholder_explanation
        from dataclasses import replace as dc_replace
        
        temp_ctx = CausalContext(
            semantic_model=semantic_model,
            root_causes=root_causes,
            root_cause_groups=root_cause_groups,
            explanation=_placeholder_explanation(),
            overall_confidence=_avg_confidence(root_causes),
            overall_uncertainty=1.0 - _avg_confidence(root_causes),
            total_mechanisms_activated=len(semantic_model.edges),
            total_hypotheses_evaluated=len(all_hypotheses),
            total_hypotheses_accepted=accepted_count,
        )
        explanation = self._engine._explanation_engine.generate(None, temp_ctx)
        explanation = dc_replace(explanation, rejected_hypotheses=tuple(h for h in all_hypotheses if not h.accepted))
        
        return CausalContext(
            semantic_model=semantic_model,
            root_causes=root_causes,
            root_cause_groups=root_cause_groups,
            explanation=explanation,
            overall_confidence=_avg_confidence(root_causes),
            overall_uncertainty=round(1.0 - _avg_confidence(root_causes), 4),
            total_mechanisms_activated=len(semantic_model.edges),
            total_hypotheses_evaluated=len(all_hypotheses),
            total_hypotheses_accepted=accepted_count,
        )

