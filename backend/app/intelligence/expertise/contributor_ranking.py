from dataclasses import dataclass

from .expertise_profile import (
    ExpertiseProfile,
)


@dataclass(frozen=True)
class ContributorRanking:

    profile: ExpertiseProfile

    rank: int