from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from .organization_readiness import (
    OrganizationReadiness,
)


class OrganizationReadinessService:

    def __init__(
        self,
        intelligence_context,
    ):
        self._intelligence = (
            intelligence_context
        )

    def weakest_modules(
        self,
        limit: int = 10,
    ):

        estimates = (
            self._intelligence
            .projection
            .all_estimates()
        )

        module_ids = sorted(
            {
                estimate.module_ref.id
                for estimate in estimates
            }
        )

        readiness = []

        for module_id in module_ids:

            rankings = (
                self._intelligence
                .readiness_service
                .rank(
                    module_id,
                    limit=1,
                )
            )

            if rankings:

                score = (
                    rankings[0]
                    .readiness_score
                )

            else:

                score = 0.0

            readiness.append(
                OrganizationReadiness(
                    module_ref=EntityRef(
                        id=module_id,
                        type=EntityType.FILE,
                    ),
                    readiness_score=score,
                    rank=0,
                )
            )

        readiness.sort(
            key=lambda item: (
                item.readiness_score
            )
        )

        return [
            OrganizationReadiness(
                module_ref=item.module_ref,
                readiness_score=(
                    item.readiness_score
                ),
                rank=index + 1,
            )
            for index, item in enumerate(
                readiness[:limit]
            )
        ]