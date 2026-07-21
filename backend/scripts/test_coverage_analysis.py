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

from app.coverage.policies.expertise_coverage_policy import (
    ExpertiseCoveragePolicy,
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
    ]

    reports = (
        ExpertiseCoveragePolicy()
        .analyze(
            estimates
        )
    )

    print(
        "\n=== COVERAGE ANALYSIS ===\n"
    )

    for report in reports:

        print(
            f"Module: "
            f"{report.module_ref.id}"
        )

        print(
            f"Experts: "
            f"{report.expert_count}"
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