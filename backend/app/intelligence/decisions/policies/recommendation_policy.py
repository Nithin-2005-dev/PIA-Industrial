from abc import ABC, abstractmethod

from app.query.query_result import (
    QueryResult,
)

from app.intelligence.decisions.reviewer_recommendation import (
    ReviewerRecommendation,
)


class RecommendationPolicy(ABC):

    @abstractmethod
    def recommend(
        self,
        file_experts: dict[
            str,
            list[QueryResult],
        ],
        limit: int,
    ) -> list[ReviewerRecommendation]:
        pass