"""Stage 09 — Reasoning.

Consumes Knowledge Models, Organization Intelligence, AND Causal Intelligence.
Produces ReasoningResult objects stored in context.reasoning_results.

Causal integration (M56):
  Each reasoning conclusion now includes WHY the recommendation exists —
  tracing the causal chain from root cause through mechanism to effect.

Flow:
    Knowledge → Reasoning ← Organization Intelligence
                         ← Causal Intelligence (M56)
"""

from __future__ import annotations

from collections import defaultdict
from uuid import NAMESPACE_URL, uuid5

from ..context import OrgIntelligenceResult, PlatformContext, ReasoningResult
from ..ui import metric, ranking, section, success, warning
from .base import PipelineStage


class ReasoningStage(PipelineStage):
    """
    Stage 09 — Reasoning

    Derives conclusions from knowledge topics, enriched by organisational
    intelligence signals and causal root-cause explanations (M56).
    """

    name = "Knowledge and Org Intel to Reasoning"

    def execute(self, context: PlatformContext) -> None:
        knowledge  = context.knowledge
        org_intel  = context.org_intelligence
        causal_ctx = getattr(context, "causal_context", None)

        if not knowledge:
            warning("No knowledge models available — skipping Reasoning layer")
            return

        from app.kernel.graph import GraphEngine, NodeType
        from app.kernel.reasoning.builder import ReasoningGraphBuilder
        from app.kernel.reasoning.rule_engine import RuleEngine, create_single_point_of_failure_rule
        from app.kernel.reasoning.strategy import StrategyEngine
        from app.kernel.models import CapabilityResult
        
        # We need to map Knowledge topics into mock CapabilityResults for the GraphEngine
        # to consume, since the GraphEngine expects CapabilityResults as raw evidence.
        mock_results = []
        for k in knowledge:
            mock_results.append(CapabilityResult(
                capability_id=f"cap_{k.entity_type}",
                status="SUCCESS",
                confidence=k.average_confidence,
                summary=f"Knowledge topic {k.topic} with score {k.average_score}",
                evidence_ids=[],
                raw_output={"topic": k.topic, "score": k.average_score},
                normalized_output={},
                warnings=[],
                recommendations=[],
                metadata={},
                execution_time_ms=1.0
            ))
            
        if org_intel:
            for bf in org_intel.bus_factors:
                mock_results.append(CapabilityResult(
                    capability_id="cap_bus_factor",
                    status="SUCCESS",
                    confidence=1.0,
                    summary=f"Bus factor for {bf.subject} is {bf.bus_factor}",
                    evidence_ids=[],
                    raw_output={"bus_factor": bf.bus_factor, "subject": bf.subject},
                    normalized_output={},
                    warnings=[],
                    recommendations=[],
                    metadata={},
                    execution_time_ms=1.0
                ))

        graph = GraphEngine()
        builder = ReasoningGraphBuilder(graph)
        builder.build_from_results(mock_results)
        
        rule_engine = RuleEngine(graph)
        rule_engine.register_rule(create_single_point_of_failure_rule())
        
        strategy = StrategyEngine(graph, rule_engine)
        strategy.execute_reasoning_cycle()
        
        # Store the graph in context for the next stages
        context.reasoning_graph = graph
        
        # Map GraphEngine INFERENCE nodes to legacy ReasoningResult for pipeline validation compatibility
        results = []
        inferences = graph.get_all_nodes(NodeType.INFERENCE)
        for inf in inferences:
            results.append(
                ReasoningResult(
                    id=inf.id,
                    subject=inf.properties.get("entity", "Unknown"),
                    conclusion=inf.properties.get("insight", "Unknown Inference"),
                    confidence=round(inf.confidence, 4),
                    uncertainty=round(1.0 - inf.confidence, 4),
                    rationale=f"Derived from rule {inf.properties.get('rule_id', 'unknown')}",
                    knowledge_ids=(),
                )
            )
            
        context.reasoning_results = results
        context.metrics["reasoning_results"] = len(results)

        section("Reasoning Results (Graph OS)")
        metric("Knowledge Topics Consumed",    len(knowledge))
        metric("Org Intelligence Available",   "YES" if org_intel else "NO")
        metric("Graph Nodes Generated", len(graph.get_all_nodes()))
        metric("Graph Edges Generated", len(graph._edges))

        success("Reasoning graph successfully built and rules evaluated")

    # ------------------------------------------------------------------

    def _build_reasoning(
        self,
        knowledge,
        org_intel: OrgIntelligenceResult | None,
        causal_ctx=None,
    ) -> list[ReasoningResult]:
        risk_map          = {}
        bus_map           = {}
        coverage_map      = {}
        concentration_map = {}
        ownership_by_dev  = defaultdict(list)

        if org_intel:
            risk_map          = {r.subject: r for r in org_intel.knowledge_risks}
            bus_map           = {b.subject: b for b in org_intel.bus_factors}
            coverage_map      = {c.subject: c for c in org_intel.coverage}
            concentration_map = {c.subject: c for c in org_intel.concentration}
            for o in org_intel.ownership:
                ownership_by_dev[o.subject].append(o)

        # Build a quick root-cause lookup by mechanism category
        rc_lookup: dict[str, str] = {}
        if causal_ctx and causal_ctx.root_causes:
            for rc in causal_ctx.root_causes:
                rc_lookup[rc.subject.lower()] = (
                    f"{rc.mechanism.replace('_', ' ').title()} "
                    f"(conf={rc.overall_confidence*100:.0f}%)"
                )

        results: list[ReasoningResult] = []

        for item in knowledge:
            conclusion          = ""
            confidence_adjustment = 0.0
            rationale_parts     = []

            if item.entity_type == "developer":
                primary = [
                    o.category for o in ownership_by_dev.get(item.topic, [])
                    if o.ownership_level == "PRIMARY"
                ]
                if primary:
                    conclusion = (
                        f"Developer {item.topic} is the primary expert "
                        f"for {', '.join(primary)}."
                    )
                    confidence_adjustment += 0.1
                else:
                    conclusion = (
                        f"Developer {item.topic} provides broad support "
                        f"across multiple subsystems."
                    )

            elif item.entity_type == "subsystem":
                bf   = bus_map.get(item.topic)
                risk = risk_map.get(item.topic)
                cov  = coverage_map.get(item.topic)
                conc = concentration_map.get(item.topic)

                if bf and bf.bus_factor <= 1:
                    conclusion = (
                        f"CRITICAL: Subsystem {item.topic} has a bus factor of "
                        f"{bf.bus_factor} with {bf.coverage:.0f}% coverage gap."
                    )
                    confidence_adjustment += 0.2
                    rationale_parts.append(f"Single point of failure in {item.topic}.")

                    # Enrich with causal chain
                    causal_reason = rc_lookup.get("ownership concentration")
                    if not causal_reason:
                        causal_reason = rc_lookup.get("bus factor reduction")
                    if causal_reason:
                        rationale_parts.append(
                            f"Root cause: {causal_reason}. "
                            f"Causal chain: Ownership concentration "
                            f"-> Knowledge concentration "
                            f"-> Bus factor reduction "
                            f"-> Health deterioration."
                        )

                elif conc and conc.risk_level == "HIGH":
                    conclusion = (
                        f"WARNING: Ownership in {item.topic} is highly "
                        f"concentrated (risk score={conc.concentration_score:.2f})."
                    )
                    confidence_adjustment += 0.1
                    causal_reason = rc_lookup.get("ownership concentration")
                    if causal_reason:
                        rationale_parts.append(
                            f"Root cause: {causal_reason}. "
                            f"Causal chain: Ownership concentration "
                            f"-> Knowledge risk increase."
                        )

                elif cov and cov.coverage_level == "WEAK":
                    conclusion = (
                        f"NOTICE: Subsystem {item.topic} has weak knowledge "
                        f"coverage ({cov.expert_count} experts)."
                    )
                    causal_reason = rc_lookup.get("review diversity decline")
                    if causal_reason:
                        rationale_parts.append(
                            f"Root cause: {causal_reason}. "
                            f"Causal chain: Review diversity decline "
                            f"-> Knowledge distribution decline "
                            f"-> Succession readiness decline."
                        )
                else:
                    conclusion = f"Subsystem {item.topic} is stable and adequately covered."

            else:
                conclusion = f"Topic {item.topic} requires ongoing monitoring."

            base_rationale = (
                f"Derived from {item.expertise_count} expertise model(s) "
                f"with score {item.average_score:.3f}. "
            )
            rationale = base_rationale + " ".join(rationale_parts)

            final_confidence = min(1.0, item.average_confidence + confidence_adjustment)

            results.append(
                ReasoningResult(
                    id=str(uuid5(NAMESPACE_URL, f"reasoning|{item.id}|{conclusion}")),
                    subject=item.topic,
                    conclusion=conclusion,
                    confidence=round(final_confidence, 4),
                    uncertainty=round(item.average_uncertainty, 4),
                    rationale=rationale,
                    knowledge_ids=(item.id,),
                )
            )

        results.sort(key=lambda r: r.confidence, reverse=True)
        return results
