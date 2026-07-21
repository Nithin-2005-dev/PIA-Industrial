from collections import defaultdict

from app.domain.entity_ref import (
    EntityRef,
)
from app.domain.entity_type import (
    EntityType,
)

from app.intelligence.expertise_profile import (
    ExpertiseProfile,
)

from .expertise_mapping_policy import (
    ExpertiseMappingPolicy,
)


class BreadthMappingPolicy(
    ExpertiseMappingPolicy
):

    def build_profiles(
        self,
        expertise_estimates,
    ):

        developer_scores = (
            defaultdict(list)
        )

        developer_modules = (
            defaultdict(set)
        )

        for estimate in (
            expertise_estimates
        ):

            developer_id = (
                estimate
                .developer_ref
                .id
            )

            developer_scores[
                developer_id
            ].append(
                estimate.raw_score
            )

            developer_modules[
                developer_id
            ].add(
                estimate
                .module_ref
                .id
            )

        profiles = []

        for (
            developer_id,
            scores,
        ) in developer_scores.items():

            total = sum(scores)

            modules = sorted(
                developer_modules[
                    developer_id
                ]
            )

            profiles.append(
                ExpertiseProfile(
                    developer_ref=EntityRef(
                        id=developer_id,
                        type=(
                            EntityType.DEVELOPER
                        ),
                    ),
                    module_count=len(
                        modules
                    ),
                    covered_modules=modules,
                    total_expertise=total,
                    average_expertise=(
                        total
                        / len(modules)
                    ),
                )
            )

        profiles.sort(
            key=lambda profile: (
                profile.total_expertise
            ),
            reverse=True,
        )

        return profiles