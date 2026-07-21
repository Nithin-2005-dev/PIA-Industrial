"""Stage 07 — build Knowledge models from Expertise models."""

from __future__ import annotations

from collections import defaultdict
from uuid import NAMESPACE_URL, uuid5

from ..context import KnowledgeModel, PlatformContext
from ..ui import metric, ranking, section, success, warning
from .base import PipelineStage


class KnowledgeStage(PipelineStage):
    """
    Expertise → Knowledge

    Groups expertise models by category to form knowledge topics.
    Propagates confidence and uncertainty across the group.
    """

    name = "Expertise to Knowledge"

    def execute(self, context: PlatformContext) -> None:
        expertise_models = context.expertise_models
        if not expertise_models:
            warning("No expertise models available — skipping Knowledge layer")
            return

        knowledge = self._build_knowledge(expertise_models)
        context.knowledge = knowledge
        context.metrics["knowledge_models"] = len(knowledge)

        section("Knowledge Topics")
        metric("Expertise Models Consumed", len(expertise_models))
        metric("Knowledge Topics Built", len(knowledge))
        metric(
            "Confidence Propagated",
            "PASS" if all(k.average_confidence >= 0.0 for k in knowledge) else "FAIL",
        )
        metric(
            "Uncertainty Propagated",
            "PASS" if all(k.average_uncertainty >= 0.0 for k in knowledge) else "FAIL",
        )

        ranking(
            "Knowledge Topics",
            [
                (
                    f"{k.topic:<28} expertise={k.expertise_count:>3} "
                    f"score={k.average_score:.3f} conf={k.average_confidence:.3f}"
                )
                for k in knowledge
            ],
        )
        success("Knowledge layer built from canonical expertise models")

    # ------------------------------------------------------------------

    def _build_knowledge(
        self,
        expertise_models,
    ) -> list[KnowledgeModel]:
        from app.observation.ingestion.topology.boundary import SubsystemResolver
        resolver = SubsystemResolver.default()

        grouped: defaultdict[tuple[str, str], list] = defaultdict(list)
        for model in expertise_models:
            if model.category == "module":
                semantic_topic = resolver.resolve(model.subject)
                entity_type = "subsystem"
            elif model.category == "developer":
                semantic_topic = model.subject
                entity_type = "developer"
            else:
                semantic_topic = model.subject
                entity_type = model.category

            grouped[(entity_type, semantic_topic)].append(model)

        knowledge = []
        for (entity_type, topic), models in grouped.items():
            average_score = sum(m.score for m in models) / len(models)
            average_confidence = sum(m.confidence for m in models) / len(models)
            average_uncertainty = sum(m.uncertainty for m in models) / len(models)
            knowledge.append(
                KnowledgeModel(
                    id=str(uuid5(NAMESPACE_URL, f"knowledge|{entity_type}|{topic}")),
                    entity_type=entity_type,
                    topic=topic,
                    expertise_count=len(models),
                    average_score=average_score,
                    average_confidence=average_confidence,
                    average_uncertainty=average_uncertainty,
                    summary=(
                        f"Knowledge about {entity_type} '{topic}' is supported by {len(models)} "
                        f"expertise model(s) with average score {average_score:.3f}."
                    ),
                )
            )

        knowledge.sort(key=lambda k: k.average_score, reverse=True)
        return knowledge
