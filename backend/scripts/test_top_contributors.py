from datetime import UTC
from datetime import datetime

from app.domain.entity_ref import (
    EntityRef,
)
from app.domain.entity_type import (
    EntityType,
)

from app.domain.expertise_estimate import (
    ExpertiseEstimate,
)

from app.expertise_mapping.expertise_mapping_service import (
    ExpertiseMappingService,
)

from app.expertise_mapping.policies.breadth_mapping_policy import (
    BreadthMappingPolicy,
)


def main():

    now = datetime.now(
        UTC
    )

    estimates = [

        ExpertiseEstimate(
            developer_ref=EntityRef(
                id="alice",
                type=EntityType.DEVELOPER,
            ),
            module_ref=EntityRef(
                id="auth.py",
                type=EntityType.FILE,
            ),
            raw_score=80,
            confidence=1.0,
            updated_at=now,
        ),

        ExpertiseEstimate(
            developer_ref=EntityRef(
                id="alice",
                type=EntityType.DEVELOPER,
            ),
            module_ref=EntityRef(
                id="billing.py",
                type=EntityType.FILE,
            ),
            raw_score=60,
            confidence=1.0,
            updated_at=now,
        ),

        ExpertiseEstimate(
            developer_ref=EntityRef(
                id="bob",
                type=EntityType.DEVELOPER,
            ),
            module_ref=EntityRef(
                id="auth.py",
                type=EntityType.FILE,
            ),
            raw_score=30,
            confidence=1.0,
            updated_at=now,
        ),
    ]

    service = (
        ExpertiseMappingService(
            BreadthMappingPolicy()
        )
    )

    rankings = (
        service.top_contributors(
            estimates
        )
    )

    print(
        "\n=== TOP CONTRIBUTORS ===\n"
    )

    for ranking in rankings:

        profile = ranking.profile

        print(
            f"Rank #{ranking.rank}"
        )

        print(
            f"Developer: "
            f"{profile.developer_ref.id}"
        )

        print(
            f"Modules: "
            f"{profile.module_count}"
        )

        print(
            f"Covered Modules: "
            f"{profile.covered_modules}"
        )

        print(
            f"Total Expertise: "
            f"{profile.total_expertise}"
        )

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()