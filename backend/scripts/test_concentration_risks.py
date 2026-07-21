from datetime import UTC
from datetime import datetime

from app.concentration.concentration_service import (
    ConcentrationService,
)

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
        # Healthy
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
        # Dangerous
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

    service = ConcentrationService(
        ExpertiseConcentrationPolicy()
    )

    risks = service.top_risks(
        estimates
    )

    print(
        "\n=== CONCENTRATION RISKS ===\n"
    )

    for risk in risks:

        report = risk.report

        print(
            f"Rank #{risk.rank}"
        )

        print(
            f"Module: "
            f"{report.module_ref.id}"
        )

        print(
            f"Score: "
            f"{report.concentration_score:.2f}"
        )

        print(
            f"Level: "
            f"{report.concentration_level}"
        )

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()