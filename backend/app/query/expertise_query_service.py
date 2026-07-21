from app.estimator.expertise_projection import (
    ExpertiseProjection,
)

from .query_result import QueryResult


class ExpertiseQueryService:

    def __init__(
        self,
        projection: ExpertiseProjection,
    ):
        self._projection = projection

    def top_experts(
        self,
        module_id: str,
        limit: int = 5,
    ) -> list[QueryResult]:
        """
        Returns the highest ranked experts
        for a given module.
        """

        results: list[QueryResult] = []

        for estimate in self._projection.all_estimates():

            if estimate.module_ref.id != module_id:
                continue

            effective_score = (
                estimate.raw_score
                * estimate.confidence
            )

            results.append(
                QueryResult(
                    estimate=estimate,
                    effective_score=effective_score,
                )
            )

        results.sort(
            key=lambda result: result.effective_score,
            reverse=True,
        )

        return results[:limit]

    def module_experts(
        self,
        module_id: str,
    ) -> list[QueryResult]:
        """
        Returns all experts for a module.
        """

        return self.top_experts(
            module_id=module_id,
            limit=10_000,
        )

    def developer_expertise(
        self,
        developer_id: str,
    ) -> list[QueryResult]:
        """
        Returns all expertise estimates
        associated with a developer.
        """

        results: list[QueryResult] = []

        for estimate in self._projection.all_estimates():

            if estimate.developer_ref.id != developer_id:
                continue

            effective_score = (
                estimate.raw_score
                * estimate.confidence
            )

            results.append(
                QueryResult(
                    estimate=estimate,
                    effective_score=effective_score,
                )
            )

        results.sort(
            key=lambda result: result.effective_score,
            reverse=True,
        )

        return results