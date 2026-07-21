"""Stage 07 - build knowledge and reasoning from expertise models."""

from __future__ import annotations

from collections import defaultdict
from uuid import NAMESPACE_URL, uuid5

from ..context import KnowledgeModel, PlatformContext, ReasoningResult
from ..ui import metric, ranking, section, success, warning
from .base import PipelineStage


class KnowledgeReasoningStage(PipelineStage):
    name = "Expertise to Knowledge and Reasoning"

    def execute(self, context: PlatformContext) -> None:
        expertise_models = context.expertise_models
        if not expertise_models:
            warning("No expertise models available")
            return

        knowledge = self._build_knowledge(expertise_models)
        reasoning = self._build_reasoning(knowledge)

        context.knowledge = knowledge
        context.reasoning_results = reasoning
        context.metrics["knowledge_models"] = len(knowledge)
        context.metrics["reasoning_results"] = len(reasoning)

        section("Knowledge")
        metric("Knowledge Models", len(knowledge))
        metric(
            "Confidence Propagated",
            "PASS" if all(item.average_confidence >= 0.0 for item in knowledge) else "FAIL",
        )
        metric(
            "Uncertainty Propagated",
            "PASS" if all(item.average_uncertainty >= 0.0 for item in knowledge) else "FAIL",
        )
        ranking(
            "Knowledge Topics",
            [
                (
                    f"{item.topic:<24} expertise={item.expertise_count} "
                    f"confidence={item.average_confidence:.3f}"
                )
                for item in knowledge
            ],
        )

        section("Reasoning")
        metric("Reasoning Results", len(reasoning))
        metric(
            "Explainability Preserved",
            "PASS" if all(item.rationale for item in reasoning) else "FAIL",
        )
        ranking(
            "Reasoning Conclusions",
            [
                f"{item.subject:<24} {item.conclusion} ({item.confidence:.3f})"
                for item in reasoning
            ],
        )
        success("Knowledge and reasoning layers built from expertise")

    def _build_knowledge(self, expertise_models) -> list[KnowledgeModel]:
        grouped = defaultdict(list)
        for model in expertise_models:
            grouped[model.category].append(model)

        knowledge = []
        for category, models in grouped.items():
            average_score = sum(item.score for item in models) / len(models)
            average_confidence = sum(item.confidence for item in models) / len(models)
            average_uncertainty = sum(item.uncertainty for item in models) / len(models)
            knowledge.append(
                KnowledgeModel(
                    id=str(uuid5(NAMESPACE_URL, f"knowledge|{category}")),
                    topic=category,
                    expertise_count=len(models),
                    average_score=average_score,
                    average_confidence=average_confidence,
                    average_uncertainty=average_uncertainty,
                    summary=(
                        f"{category} knowledge is supported by {len(models)} "
                        f"expertise model(s)."
                    ),
                )
            )

        knowledge.sort(key=lambda item: item.average_score, reverse=True)
        return knowledge

    def _build_reasoning(self, knowledge) -> list[ReasoningResult]:
        results = []
        for item in knowledge:
            if item.average_score >= 0.70:
                conclusion = "high-confidence organizational signal"
            elif item.average_score >= 0.40:
                conclusion = "moderate organizational signal"
            else:
                conclusion = "emerging organizational signal"

            results.append(
                ReasoningResult(
                    id=str(uuid5(NAMESPACE_URL, f"reasoning|{item.id}|{conclusion}")),
                    subject=item.topic,
                    conclusion=conclusion,
                    confidence=item.average_confidence,
                    uncertainty=item.average_uncertainty,
                    rationale=(
                        f"Reasoned from {item.expertise_count} expertise model(s) "
                        f"with average score {item.average_score:.3f}."
                    ),
                    knowledge_ids=(item.id,),
                )
            )

        results.sort(key=lambda item: item.confidence, reverse=True)
        return results
