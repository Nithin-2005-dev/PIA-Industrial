from app.query.expertise_query_service import (
    ExpertiseQueryService,
)

from .reviewer_recommendation import (
    ReviewerRecommendation,
)

from .policies.recommendation_policy import (
    RecommendationPolicy,
)


class ReviewerRecommendationService:

    def __init__(
        self,
        query_service: ExpertiseQueryService,
        policy: RecommendationPolicy,
    ):
        self._query_service = query_service
        self._policy = policy

    def recommend_reviewers(
        self,
        file_ids: list[str],
        limit: int = 3,
    ) -> list[ReviewerRecommendation]:

        file_experts = {}

        for file_id in file_ids:

            file_experts[file_id] = (
                self._query_service.module_experts(
                    file_id
                )
            )

        return self._policy.recommend(
            file_experts=file_experts,
            limit=limit,
        )