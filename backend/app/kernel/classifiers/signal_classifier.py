from dataclasses import dataclass
from enum import Enum

from app.intelligence.measurement.domain import SoftwareSignal
from app.kernel.classifiers.signal_ontology import SignalOntology
from app.kernel.classifiers.signals import SignalDefinition
from app.kernel.classifiers.signals import SignalRegistry


class ClassificationSource(Enum):
    RULE = "rule"
    ONTOLOGY = "ontology"
    EMBEDDING = "embedding"
    LLM = "llm"
    HUMAN_REQUIRED = "human_required"


@dataclass(frozen=True)
class SignalClassification:
    signal_id: str
    category: str
    confidence: float
    source: ClassificationSource
    explanation: str
    requires_human_approval: bool = False


class RuleBasedSignalClassifier:

    def classify(
        self,
        signal: SoftwareSignal,
        registry: SignalRegistry,
    ) -> SignalClassification | None:
        for definition in registry.all():
            if (
                signal.name == definition.name
                or signal.id == definition.id
                or signal.name in definition.tags
            ):
                return SignalClassification(
                    signal_id=signal.id,
                    category=definition.semantic_category,
                    confidence=0.95,
                    source=ClassificationSource.RULE,
                    explanation=(
                        "matched signal name or tag in registry"
                    ),
                )

        lowered = signal.name.lower()

        if "coverage" in lowered:
            return SignalClassification(
                signal_id=signal.id,
                category="testing",
                confidence=0.8,
                source=ClassificationSource.RULE,
                explanation="matched coverage keyword",
            )

        if "vulnerability" in lowered or "cve" in lowered:
            return SignalClassification(
                signal_id=signal.id,
                category="security",
                confidence=0.8,
                source=ClassificationSource.RULE,
                explanation="matched security keyword",
            )

        return None


class EmbeddingSimilarityClassifier:
    """
    Deterministic token-overlap stand-in for future embedding search.
    """

    def classify(
        self,
        signal: SoftwareSignal,
        registry: SignalRegistry,
    ) -> SignalClassification | None:
        signal_tokens = set(
            signal.name.lower().replace(
                ".",
                "_",
            ).split("_")
        )

        best = None
        best_score = 0.0

        for definition in registry.all():
            tokens = set(
                definition.name.lower().split(
                    "_"
                )
            ) | set(definition.tags)

            if not tokens:
                continue

            score = len(
                signal_tokens & tokens
            ) / len(
                signal_tokens | tokens
            )

            if score > best_score:
                best = definition
                best_score = score

        if best is None or best_score <= 0:
            return None

        return SignalClassification(
            signal_id=signal.id,
            category=best.semantic_category,
            confidence=min(
                0.7,
                best_score,
            ),
            source=ClassificationSource.EMBEDDING,
            explanation="token similarity to registered signal",
        )


class LlmSignalClassifier:
    """
    Boundary for optional LLM-assisted classification.
    """

    def classify(
        self,
        signal: SoftwareSignal,
    ) -> SignalClassification | None:
        return None


class SemanticSignalClassifier:

    def __init__(
        self,
        registry: SignalRegistry,
        ontology: SignalOntology,
        approval_threshold: float = 0.75,
        llm_classifier: LlmSignalClassifier | None = None,
    ):
        self._registry = registry
        self._ontology = ontology
        self._approval_threshold = approval_threshold
        self._rule = RuleBasedSignalClassifier()
        self._embedding = EmbeddingSimilarityClassifier()
        self._llm = llm_classifier or LlmSignalClassifier()

    def classify(
        self,
        signal: SoftwareSignal,
    ) -> SignalClassification:
        candidates = [
            self._rule.classify(
                signal,
                self._registry,
            ),
            self._ontology_lookup(
                signal,
            ),
            self._embedding.classify(
                signal,
                self._registry,
            ),
            self._llm.classify(
                signal,
            ),
        ]

        candidates = [
            candidate
            for candidate in candidates
            if candidate is not None
        ]

        if not candidates:
            return SignalClassification(
                signal_id=signal.id,
                category="unknown",
                confidence=0.0,
                source=ClassificationSource.HUMAN_REQUIRED,
                explanation="no deterministic mapping found",
                requires_human_approval=True,
            )

        result = sorted(
            candidates,
            key=lambda candidate: candidate.confidence,
            reverse=True,
        )[0]

        if result.confidence < self._approval_threshold:
            return SignalClassification(
                signal_id=result.signal_id,
                category=result.category,
                confidence=result.confidence,
                source=result.source,
                explanation=result.explanation,
                requires_human_approval=True,
            )

        return result

    def _ontology_lookup(
        self,
        signal: SoftwareSignal,
    ) -> SignalClassification | None:
        relationships = self._ontology.relationships(
            signal.id
        )

        if not relationships:
            return None

        relationship = relationships[0]

        return SignalClassification(
            signal_id=signal.id,
            category=relationship.target_id,
            confidence=relationship.confidence,
            source=ClassificationSource.ONTOLOGY,
            explanation=(
                f"ontology relationship {relationship.relationship.value}"
            ),
        )


