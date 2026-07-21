from collections import defaultdict

from app.intelligence.decisions.reviewer_recommendation import (
    ReviewerRecommendation,
)

from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType

from app.query.query_result import (
    QueryResult,
)

from .recommendation_policy import (
    RecommendationPolicy,
)


class CoverageRecommendationPolicy(
    RecommendationPolicy
):

    def recommend(
        self,
        file_experts: dict[
            str,
            list[QueryResult],
        ],
        limit: int,
    ) -> list[ReviewerRecommendation]:

        developer_scores = defaultdict(float)

        developer_coverage = defaultdict(set)

        for file_id, experts in (
            file_experts.items()
        ):

            for expert in experts:

                developer_id = (
                    expert.estimate
                    .developer_ref.id
                )

                developer_scores[
                    developer_id
                ] += (
                    expert.effective_score
                )

                developer_coverage[
                    developer_id
                ].add(file_id)

        recommendations = []

        for developer_id in (
            developer_scores
        ):

            recommendations.append(
                ReviewerRecommendation(
                    reviewer_ref=EntityRef(
                        id=developer_id,
                        type=EntityType.DEVELOPER,
                    ),
                    score=developer_scores[
                        developer_id
                    ],
                    covered_files=len(
                        developer_coverage[
                            developer_id
                        ]
                    ),
                )
            )

        recommendations.sort(
            key=lambda recommendation: (
                recommendation.covered_files,
                recommendation.score,
            ),
            reverse=True,
        )

        return recommendations[:limit]