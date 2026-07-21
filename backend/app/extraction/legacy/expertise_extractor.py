from uuid import NAMESPACE_URL
from uuid import uuid5

from app.domain.evidence import Evidence
from app.domain.event import Event
from app.domain.event_type import EventType
from app.domain.predicate_type import PredicateType

from app.extraction.entities.legacy.policies.evidence_strength_policy import (
    EvidenceStrengthPolicy,
)

from .evidence_extractor import EvidenceExtractor


class ExpertiseExtractor(
    EvidenceExtractor
):

    def __init__(
        self,
        strength_policy: EvidenceStrengthPolicy,
    ):
        self._strength_policy = (
            strength_policy
        )

    def extract(
        self,
        event: Event,
    ) -> list[Evidence]:

        if event.type != EventType.COMMIT:
            return []

        strength = (
            self._strength_policy
            .strength(event)
        )

        evidence = []

        for target in event.target_refs:

            evidence.append(
                Evidence(
                    id=self._evidence_id(
                        event,
                        target.id,
                    ),

                    source_event_id=event.id,

                    subject_ref=event.actor_ref,

                    predicate=PredicateType.MODIFIED,

                    object_ref=target,

                    confidence=1.0,

                    metadata={
                        "strength": strength,
                    },
                )
            )

        return evidence

    def _evidence_id(
        self,
        event: Event,
        target_id: str,
    ):

        return uuid5(
            NAMESPACE_URL,
            f"{event.id}:{target_id}",
        )