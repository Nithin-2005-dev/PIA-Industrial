from __future__ import annotations

import copy
from typing import Any

from .models import (
    ScenarioComparison,
    ScenarioContext,
    ScenarioExecutionResult,
    SimulationScenario,
)


class SimulationEngine:
    """
    Generates isolated simulation scenarios from a baseline context.
    Does NOT execute the downstream pipeline; only prepares the branched contexts.
    """

    def generate_scenario_context(
        self,
        baseline_context: Any,
        scenario: SimulationScenario,
    ) -> ScenarioContext:
        """
        Creates an isolated, branched context for a scenario by cloning the baseline
        and applying the scenario's interventions.
        """
        cloned = self._clone_context(baseline_context)

        # Apply interventions
        for intervention in scenario.interventions:
            intervention.apply(cloned)

        return ScenarioContext(
            scenario=scenario,
            baseline_context=baseline_context,
            cloned_context=cloned,
        )

    def _clone_context(self, context: Any) -> Any:
        """
        Safely clone the PlatformContext.
        We cannot blind deepcopy because it contains runtime and service provider references.
        """
        # Create a shallow copy of the context object
        import dataclasses
        if dataclasses.is_dataclass(context):
            cloned = copy.copy(context)
        else:
            # Fallback for generic objects
            cloned = copy.copy(context)

        # Deep copy the graph
        if hasattr(cloned, "knowledge_graph") and cloned.knowledge_graph is not None:
            if hasattr(cloned.knowledge_graph, "copy"):
                # NetworkX copy
                cloned.knowledge_graph = cloned.knowledge_graph.copy()
            else:
                # Custom graph
                cloned.knowledge_graph = copy.deepcopy(cloned.knowledge_graph)
                
        # Copy lists
        if hasattr(cloned, "expertise_models"):
            cloned.expertise_models = list(cloned.expertise_models)
        
        # Deep copy metrics to avoid sharing state
        if hasattr(cloned, "metrics"):
            cloned.metrics = copy.deepcopy(cloned.metrics)

        # Deep copy evidence package to allow isolated interventions
        if hasattr(cloned, "evidence_package") and cloned.evidence_package is not None:
            cloned.evidence_package = copy.deepcopy(cloned.evidence_package)

        if hasattr(cloned, "org_intelligence") and cloned.org_intelligence is not None:
            cloned.org_intelligence = copy.deepcopy(cloned.org_intelligence)

        if hasattr(cloned, "forecast_context") and cloned.forecast_context is not None:
            cloned.forecast_context = copy.deepcopy(cloned.forecast_context)

        return cloned


class ScenarioComparisonEngine:
    """
    Compares the execution result of a scenario against the baseline execution result.
    """

    def compare(
        self,
        baseline_org_intelligence: Any,
        scenario_org_intelligence: Any,
    ) -> ScenarioComparison:
        """
        Computes the delta, impact score, confidence, and priority.
        Calculates health over impacted subjects rather than just repository average.
        """
        # Base global averages
        b_global_health = baseline_org_intelligence.health.average_health if baseline_org_intelligence else 0.0
        s_global_health = scenario_org_intelligence.health.average_health if scenario_org_intelligence else 0.0
        
        # We don't have direct access to health per-subject in OrgHealthSummary, but we can 
        # proxy localized health by looking at coverage, bus factor, and concentration differences.
        b_bfs = {bf.subject: bf.bus_factor for bf in getattr(baseline_org_intelligence, "bus_factors", [])}
        s_bfs = {bf.subject: bf.bus_factor for bf in getattr(scenario_org_intelligence, "bus_factors", [])}
        
        b_covs = {c.subject: c.coverage_score for c in getattr(baseline_org_intelligence, "coverage", [])}
        s_covs = {c.subject: c.coverage_score for c in getattr(scenario_org_intelligence, "coverage", [])}
        
        b_cons = {c.subject: c.concentration_score for c in getattr(baseline_org_intelligence, "concentration", [])}
        s_cons = {c.subject: c.concentration_score for c in getattr(scenario_org_intelligence, "concentration", [])}
        
        impacted_subjects = set()
        for subj in set(b_bfs) | set(s_bfs):
            if b_bfs.get(subj, 1) != s_bfs.get(subj, 1):
                impacted_subjects.add(subj)
            if b_covs.get(subj, 0.0) != s_covs.get(subj, 0.0):
                impacted_subjects.add(subj)
            if b_cons.get(subj, 0.0) != s_cons.get(subj, 0.0):
                impacted_subjects.add(subj)

        if not impacted_subjects:
            b_health = b_global_health
            s_health = s_global_health
        else:
            def calc_subj_health(subj, bfs, covs, cons):
                bf_val = bfs.get(subj, 1)
                cov_score = covs.get(subj, 0.5)
                con_score = cons.get(subj, 0.0)
                bf_penalty = 1.0 if bf_val >= 3 else (0.8 if bf_val >= 2 else 0.5)
                health = cov_score * (1.0 - con_score * 0.3) * bf_penalty
                return max(0.0, min(1.0, health))
                
            b_impacted_health = sum(calc_subj_health(s, b_bfs, b_covs, b_cons) for s in impacted_subjects) / len(impacted_subjects)
            s_impacted_health = sum(calc_subj_health(s, s_bfs, s_covs, s_cons) for s in impacted_subjects) / len(impacted_subjects)
            
            b_health = b_impacted_health
            s_health = s_impacted_health

        h_delta = s_health - b_health
        
        b_avg_bf = sum(b_bfs.values()) / len(b_bfs) if b_bfs else 0.0
        s_avg_bf = sum(s_bfs.values()) / len(s_bfs) if s_bfs else 0.0
        bf_delta = s_avg_bf - b_avg_bf

        b_avg_cov = sum(b_covs.values()) / len(b_covs) if b_covs else 0.0
        s_avg_cov = sum(s_covs.values()) / len(s_covs) if s_covs else 0.0
        cov_delta = s_avg_cov - b_avg_cov

        b_risks = sum(1 for r in getattr(baseline_org_intelligence, "knowledge_risks", []) if r.risk_level == "HIGH")
        s_risks = sum(1 for r in getattr(scenario_org_intelligence, "knowledge_risks", []) if r.risk_level == "HIGH")
        risk_delta = s_risks - b_risks

        # Heuristic Impact Score
        impact = (h_delta * 100) + (bf_delta * 10) - (risk_delta * 15)
        
        # Confidence decays if impact is wildly large, just a simple heuristic
        confidence = max(0.1, 0.9 - abs(impact) * 0.01)
        
        priority = "LOW"
        if impact > 15:
            priority = "HIGH"
        elif impact > 5:
            priority = "MEDIUM"
        elif impact < -15:
            priority = "CRITICAL (Negative)"
        elif impact < -5:
            priority = "HIGH (Negative)"

        return ScenarioComparison(
            baseline_health=b_health,
            scenario_health=s_health,
            health_delta=h_delta,
            baseline_bus_factor=int(b_avg_bf),
            scenario_bus_factor=int(s_avg_bf),
            bus_factor_delta=int(bf_delta),
            baseline_coverage=b_avg_cov,
            scenario_coverage=s_avg_cov,
            coverage_delta=cov_delta,
            baseline_high_risks=b_risks,
            scenario_high_risks=s_risks,
            high_risks_delta=risk_delta,
            impact_score=impact,
            confidence=confidence,
            recommendation_priority=priority,
        )
