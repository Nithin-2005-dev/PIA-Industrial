from datetime import UTC
from datetime import datetime

from app.coverage.coverage_service import (
    CoverageService,
)

from app.coverage.policies.expertise_coverage_policy import (
    ExpertiseCoveragePolicy,
)

from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.domain.expertise_estimate import (
    ExpertiseEstimate,
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

        ExpertiseEstimate(
            developer_ref=EntityRef(
                id="charlie",
                type=EntityType.DEVELOPER,
            ),
            module_ref=EntityRef(
                id="payments.py",
                type=EntityType.FILE,
            ),
            raw_score=20,
            confidence=1.0,
            updated_at=now,
        ),

        ExpertiseEstimate(
            developer_ref=EntityRef(
                id="david",
                type=EntityType.DEVELOPER,
            ),
            module_ref=EntityRef(
                id="analytics.py",
                type=EntityType.FILE,
            ),
            raw_score=85,
            confidence=1.0,
            updated_at=now,
        ),

        ExpertiseEstimate(
            developer_ref=EntityRef(
                id="emma",
                type=EntityType.DEVELOPER,
            ),
            module_ref=EntityRef(
                id="analytics.py",
                type=EntityType.FILE,
            ),
            raw_score=80,
            confidence=1.0,
            updated_at=now,
        ),

        ExpertiseEstimate(
            developer_ref=EntityRef(
                id="frank",
                type=EntityType.DEVELOPER,
            ),
            module_ref=EntityRef(
                id="analytics.py",
                type=EntityType.FILE,
            ),
            raw_score=75,
            confidence=1.0,
            updated_at=now,
        ),
    ]

    service = CoverageService(
        ExpertiseCoveragePolicy()
    )

    gaps = service.top_gaps(
        estimates
    )

    print(
        "\n=== COVERAGE GAPS ===\n"
    )

    for gap in gaps:

        report = gap.report

        print(
            f"Rank #{gap.rank}"
        )

        print(
            f"Module: "
            f"{report.module_ref.id}"
        )

        print(
            f"Coverage Score: "
            f"{report.coverage_score:.2f}"
        )

        print(
            f"Coverage Level: "
            f"{report.coverage_level}"
        )

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()