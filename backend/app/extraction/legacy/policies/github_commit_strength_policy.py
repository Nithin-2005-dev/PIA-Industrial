from app.domain.event import Event

from .evidence_strength_policy import (
    EvidenceStrengthPolicy,
)


class GitHubCommitStrengthPolicy(
    EvidenceStrengthPolicy
):

    def strength(
        self,
        event: Event,
    ) -> float:

        changes = event.payload.get(
            "total_changes",
            0,
        )

        if changes <= 10:
            return 0.1

        if changes <= 100:
            return 1.0

        if changes <= 500:
            return 3.0

        if changes <= 1000:
            return 5.0

        return 10.0