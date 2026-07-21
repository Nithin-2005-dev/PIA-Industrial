from .contributor_ranking import (
    ContributorRanking,
)

from .policies.expertise_mapping_policy import (
    ExpertiseMappingPolicy,
)


class ExpertiseMappingService:

    def __init__(
        self,
        policy: ExpertiseMappingPolicy,
    ):
        self._policy = policy

    def build_profiles(
        self,
        expertise_estimates,
    ):

        return (
            self._policy
            .build_profiles(
                expertise_estimates
            )
        )

    def top_contributors(
        self,
        expertise_estimates,
        limit: int = 10,
    ):

        profiles = (
            self.build_profiles(
                expertise_estimates
            )
        )

        return [
            ContributorRanking(
                profile=profile,
                rank=index + 1,
            )
            for index, profile in enumerate(
                profiles[:limit]
            )
        ]