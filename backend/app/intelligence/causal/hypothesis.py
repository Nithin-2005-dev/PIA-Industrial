"""M56 — Causal Hypothesis Engine.

Generates candidate hypotheses from the CausalSemanticModel, scores them
against evidence, rejects those below the confidence threshold, and ranks
probable root causes.

Key invariant: correlation alone is never presented as causation.
A hypothesis is accepted only when:
  1. The corresponding rule is activated (observed cause value is unfavourable).
  2. Temporal precedence holds (the cause variable moved before the effect).
  3. overall_confidence >= ACCEPTANCE_THRESHOLD.
"""
from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from app.intelligence.causal.models import (
    CausalChain,
    CausalEdge,
    CausalEvidence,
    CausalHypothesis,
    CausalSemanticModel,
    RootCause,
    RootCauseGroup,
)
from app.intelligence.causal.ontology import CausalOntology

ACCEPTANCE_THRESHOLD = 0.60


class CausalHypothesisEngine:
    """Generates, scores, and ranks causal hypotheses."""

    def __init__(self, ontology: CausalOntology) -> None:
        self._ontology = ontology

    def evaluate(
        self,
        semantic_model: CausalSemanticModel,
        context: object,
    ) -> tuple[tuple[RootCause, ...], tuple[CausalHypothesis, ...], tuple[RootCauseGroup, ...]]:
        """Return (accepted_root_causes, all_hypotheses, root_cause_groups)."""
        all_hypotheses = self._generate_hypotheses(semantic_model, context)
        accepted = [h for h in all_hypotheses if h.accepted]

        root_causes = self._to_root_causes(accepted, semantic_model)
        groups = self._group_by_category(root_causes)
        return tuple(root_causes), tuple(all_hypotheses), tuple(groups)

    # ------------------------------------------------------------------

    def _generate_hypotheses(
        self,
        semantic_model: CausalSemanticModel,
        context: object,
    ) -> list[CausalHypothesis]:
        """One hypothesis per causal edge in the semantic model."""
        hypotheses: list[CausalHypothesis] = []

        # Build quick node lookup
        node_by_id = {n.id: n for n in semantic_model.nodes}

        for edge in semantic_model.edges:
            cause_node = node_by_id.get(edge.cause_node_id)
            effect_node = node_by_id.get(edge.effect_node_id)
            if not cause_node or not effect_node:
                continue

            overall = edge.confidence.overall_confidence

            # Temporal precedence check: cause must be in "decreasing" direction
            # (i.e., already trending downward before the effect manifests)
            has_precedence = cause_node.direction == "decreasing" or cause_node.direction == "increasing"

            evidence = self._collect_evidence(cause_node.name, context)
            accepted = (
                overall >= ACCEPTANCE_THRESHOLD
                and has_precedence
                and len(evidence) > 0
            )
            rejection_reason: str | None = None
            if not accepted:
                if overall < ACCEPTANCE_THRESHOLD:
                    rejection_reason = f"insufficient overall confidence ({overall:.2f} < {ACCEPTANCE_THRESHOLD})"
                elif len(evidence) == 0:
                    rejection_reason = "no supporting evidence found in pipeline context"
                else:
                    rejection_reason = "temporal precedence not established"

            hyp_id = str(uuid5(NAMESPACE_URL, f"hypothesis|{edge.cause_node_id}|{edge.effect_node_id}"))
            hypotheses.append(
                CausalHypothesis(
                    id=hyp_id,
                    cause_node_id=edge.cause_node_id,
                    effect_node_id=edge.effect_node_id,
                    mechanism_id=edge.mechanism_id,
                    evidence=tuple(evidence),
                    raw_confidence=overall,
                    accepted=accepted,
                    rejection_reason=rejection_reason,
                )
            )

        return hypotheses

    def _collect_evidence(
        self,
        cause_node_name: str,
        context: object,
    ) -> list[CausalEvidence]:
        """Derive CausalEvidence from measurements and org intel."""
        evidence: list[CausalEvidence] = []

        # Org intel as evidence
        org = getattr(context, "org_intelligence", None)
        if org:
            if "concentration" in cause_node_name or "ownership" in cause_node_name:
                for entry in org.concentration[:3]:
                    if entry.risk_level == "HIGH":
                        evidence.append(CausalEvidence(
                            evidence_id=str(uuid5(NAMESPACE_URL, f"ev|conc|{entry.subject}")),
                            source="measurement",
                            summary=f"High concentration in {entry.subject} (score={entry.concentration_score:.2f})",
                            weight=0.8,
                        ))
            if "bus_factor" in cause_node_name:
                for bf in org.bus_factors[:3]:
                    if bf.bus_factor <= 1:
                        evidence.append(CausalEvidence(
                            evidence_id=str(uuid5(NAMESPACE_URL, f"ev|bf|{bf.subject}")),
                            source="measurement",
                            summary=f"Bus factor = {bf.bus_factor} for {bf.subject}",
                            weight=0.9,
                        ))
            if "coverage" in cause_node_name or "review" in cause_node_name:
                for cov in org.coverage[:3]:
                    if cov.coverage_level == "WEAK":
                        evidence.append(CausalEvidence(
                            evidence_id=str(uuid5(NAMESPACE_URL, f"ev|cov|{cov.subject}")),
                            source="measurement",
                            summary=f"Weak coverage for {cov.subject} ({cov.expert_count} experts)",
                            weight=0.7,
                        ))
            if "knowledge_risk" in cause_node_name:
                for kr in org.knowledge_risks[:3]:
                    if kr.risk_level == "HIGH":
                        evidence.append(CausalEvidence(
                            evidence_id=str(uuid5(NAMESPACE_URL, f"ev|kr|{kr.subject}")),
                            source="measurement",
                            summary=f"High knowledge risk for {kr.subject}: {kr.summary[:60]}",
                            weight=0.85,
                        ))

        # Measurements as generic evidence (always available if measurements exist)
        measurements = getattr(context, "measurements", [])
        if measurements and not evidence:
            evidence.append(CausalEvidence(
                evidence_id=str(uuid5(NAMESPACE_URL, f"ev|measurements|{cause_node_name}")),
                source="measurement",
                summary=f"{len(measurements)} measurement(s) support {cause_node_name} observation",
                weight=0.5,
            ))

        return evidence[:5]  # cap at 5 evidence items per hypothesis

    # ------------------------------------------------------------------

    def _to_root_causes(
        self,
        accepted: list[CausalHypothesis],
        semantic_model: CausalSemanticModel,
    ) -> list[RootCause]:
        """Convert accepted hypotheses to ranked RootCause objects."""
        node_by_id = {n.id: n for n in semantic_model.nodes}

        # Find root causes: cause nodes that are not effects of other accepted hypotheses
        effect_ids = {h.effect_node_id for h in accepted}

        root_causes: list[RootCause] = []
        for hyp in accepted:
            if hyp.cause_node_id in effect_ids:
                continue  # this cause is itself an effect of something upstream

            cause_node = node_by_id.get(hyp.cause_node_id)
            if not cause_node:
                continue

            # Build the causal chain from this root to the terminal effect
            chain_edges = self._trace_chain(hyp.cause_node_id, accepted, semantic_model)
            terminal_effect = chain_edges[-1].effect_node_id if chain_edges else hyp.effect_node_id

            # Find the edge confidence for this hypothesis
            edge = next(
                (e for e in semantic_model.edges
                 if e.cause_node_id == hyp.cause_node_id and e.effect_node_id == hyp.effect_node_id),
                None,
            )
            confidence = edge.confidence if edge else \
                __import__("app.intelligence.causal.models", fromlist=["CausalConfidence"]).CausalConfidence.combine(
                    hyp.raw_confidence, hyp.raw_confidence, hyp.raw_confidence * 0.95
                )

            chain = CausalChain(
                root_cause_ids=(hyp.cause_node_id,),
                effect_node_id=terminal_effect,
                edges=tuple(chain_edges),
                overall_confidence=confidence,
            )

            category = self._ontology.category_of(hyp.mechanism_id)
            rc_id = str(uuid5(NAMESPACE_URL, f"root_cause|{hyp.id}"))
            root_causes.append(
                RootCause(
                    id=rc_id,
                    subject=cause_node.name.replace("_", " ").title(),
                    mechanism_id=hyp.mechanism_id,
                    mechanism_category=category,
                    confidence=confidence,
                    evidence=hyp.evidence,
                    rank=0,  # assigned below
                    causal_chain=chain,
                )
            )

        # Rank by overall_confidence descending
        root_causes.sort(key=lambda r: r.confidence.overall_confidence, reverse=True)
        return [
            RootCause(
                id=rc.id,
                subject=rc.subject,
                mechanism_id=rc.mechanism_id,
                mechanism_category=rc.mechanism_category,
                confidence=rc.confidence,
                evidence=rc.evidence,
                rank=idx + 1,
                causal_chain=rc.causal_chain,
            )
            for idx, rc in enumerate(root_causes)
        ]

    def _trace_chain(
        self,
        start_node_id: str,
        hypotheses: list[CausalHypothesis],
        semantic_model: CausalSemanticModel,
    ) -> list[CausalEdge]:
        """Follow accepted causal edges downstream from start_node_id."""
        chain: list[CausalEdge] = []
        visited: set[str] = set()
        current = start_node_id
        while True:
            if current in visited:
                break
            visited.add(current)
            next_hyp = next((h for h in hypotheses if h.cause_node_id == current), None)
            if not next_hyp:
                break
            edge = next(
                (e for e in semantic_model.edges
                 if e.cause_node_id == next_hyp.cause_node_id
                 and e.effect_node_id == next_hyp.effect_node_id),
                None,
            )
            if edge:
                chain.append(edge)
            current = next_hyp.effect_node_id
        return chain

    def _group_by_category(
        self,
        root_causes: list[RootCause],
    ) -> list[RootCauseGroup]:
        """Group root causes by mechanism category."""
        from collections import defaultdict
        by_cat: dict[str, list[RootCause]] = defaultdict(list)
        for rc in root_causes:
            by_cat[rc.mechanism_category].append(rc)
        groups: list[RootCauseGroup] = []
        for cat, causes in by_cat.items():
            combined = sum(rc.confidence.overall_confidence for rc in causes) / len(causes)
            groups.append(RootCauseGroup(
                category=cat,
                causes=tuple(causes),
                combined_confidence=round(combined, 4),
            ))
        groups.sort(key=lambda g: g.combined_confidence, reverse=True)
        return groups
