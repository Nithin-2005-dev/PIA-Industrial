from datetime import UTC
from datetime import datetime

from app.concentration.policies.expertise_concentration_policy import (
    ExpertiseConcentrationPolicy,
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

        #
        # Healthy distribution
        #

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
            raw_score=80,
            confidence=1.0,
            updated_at=now,
        ),

        ExpertiseEstimate(
            developer_ref=EntityRef(
                id="charlie",
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

        #
        # Dangerous concentration
        #

        ExpertiseEstimate(
            developer_ref=EntityRef(
                id="david",
                type=EntityType.DEVELOPER,
            ),
            module_ref=EntityRef(
                id="payments.py",
                type=EntityType.FILE,
            ),
            raw_score=100,
            confidence=1.0,
            updated_at=now,
        ),

        ExpertiseEstimate(
            developer_ref=EntityRef(
                id="emma",
                type=EntityType.DEVELOPER,
            ),
            module_ref=EntityRef(
                id="payments.py",
                type=EntityType.FILE,
            ),
            raw_score=1,
            confidence=1.0,
            updated_at=now,
        ),

        ExpertiseEstimate(
            developer_ref=EntityRef(
                id="frank",
                type=EntityType.DEVELOPER,
            ),
            module_ref=EntityRef(
                id="payments.py",
                type=EntityType.FILE,
            ),
            raw_score=1,
            confidence=1.0,
            updated_at=now,
        ),
    ]

    reports = (
        ExpertiseConcentrationPolicy()
        .analyze(
            estimates
        )
    )

    print(
        "\n=== CONCENTRATION ANALYSIS ===\n"
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
            f"Concentration Score: "
            f"{report.concentration_score:.2f}"
        )

        print(
            f"Concentration Level: "
            f"{report.concentration_level}"
        )

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()