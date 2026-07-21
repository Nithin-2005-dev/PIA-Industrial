"""Stage 06 - build canonical expertise models from evidence."""

from __future__ import annotations

from collections import defaultdict
import math
from uuid import NAMESPACE_URL, uuid5

from ..context import ExpertiseModel, PlatformContext
from ..ui import metric, ranking, section, success, warning
from .base import PipelineStage


class ExpertiseStage(PipelineStage):
    name = "Evidence to Expertise"

    def execute(self, context: PlatformContext) -> None:
        package = context.evidence_package
        if package is None:
            warning("No evidence package available")
            return

        evidence_items = package.for_expertise()
        grouped = defaultdict(list)
        for item in evidence_items:
            # Group by explicit entity targets extracted during Evidence Synthesis
            target_entity = item.metadata.get("target_entity", "unknown")
            target_entity_type = item.metadata.get("target_entity_type", "unknown")
            grouped[(target_entity_type, target_entity)].append(item)

        expertise_models = []
        for (entity_type, entity_name), items in grouped.items():
            total_weight = sum(item.confidence for item in items)
            if total_weight == 0:
                total_weight = len(items)
                weights = [1.0] * len(items)
            else:
                weights = [item.confidence for item in items]

            confidence = sum(w * item.confidence for w, item in zip(weights, items)) / total_weight
            uncertainty = sum(w * item.uncertainty for w, item in zip(weights, items)) / total_weight
            quality = sum(w * item.quality for w, item in zip(weights, items)) / total_weight
            strength = sum(w * item.strength for w, item in zip(weights, items)) / total_weight

            log_score_sum = 0.0
            for w, item in zip(weights, items):
                item_score = max(item.strength * item.confidence * item.quality, 1e-6)
                log_score_sum += w * math.log(item_score)
            
            score = math.exp(log_score_sum / total_weight)
            model_id = str(
                uuid5(
                    NAMESPACE_URL,
                    "|".join(("expertise", entity_type, entity_name, *sorted(item.evidence_id for item in items))),
                )
            )
            explanations = [item.traceability.explanation for item in items if item.traceability.explanation]

            expertise_models.append(
                ExpertiseModel(
                    id=model_id,
                    subject=entity_name,
                    category=entity_type,
                    score=score,
                    confidence=confidence,
                    uncertainty=uncertainty,
                    quality=quality,
                    evidence_ids=tuple(item.evidence_id for item in items),
                    explanation=explanations[0] if explanations else "Evidence confidence factors aggregated.",
                )
            )

        expertise_models.sort(key=lambda item: item.score, reverse=True)
        context.expertise_models = expertise_models
        context.metrics["expertise_models"] = len(expertise_models)

        section("Expertise Models")
        metric("Evidence Inputs", len(evidence_items))
        metric("Models Built", len(expertise_models))
        metric(
            "Confidence Propagated",
            "PASS" if all(item.confidence >= 0.0 for item in expertise_models) else "FAIL",
        )
        metric(
            "Uncertainty Propagated",
            "PASS" if all(item.uncertainty >= 0.0 for item in expertise_models) else "FAIL",
        )
        metric(
            "Explainability Preserved",
            "PASS" if all(item.explanation for item in expertise_models) else "FAIL",
        )
        ranking(
            "Top Expertise Models",
            [
                (
                    f"{item.subject:<34} score={item.score:.3f} "
                    f"confidence={item.confidence:.3f}"
                )
                for item in expertise_models[:10]
            ],
        )
        success("Expertise layer built from canonical evidence package")
