from app.concentration.concentration_report import (
    ConcentrationReport,
)

from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.knowledge_transfer.policies.simple_transfer_policy import (
    SimpleTransferPolicy,
)

from app.ownership.ownership_estimate import (
    OwnershipEstimate,
)

from app.ownership.ownership_level import (
    OwnershipLevel,
)

from app.successor.successor_candidate import (
    SuccessorCandidate,
)


def main():

    module_ref = EntityRef(
        id="payments.py",
        type=EntityType.FILE,
    )

    ownerships = [

        OwnershipEstimate(
            owner_ref=EntityRef(
                id="david",
                type=EntityType.DEVELOPER,
            ),
            module_ref=module_ref,
            ownership_percentage=0.90,
            effective_score=95,
            ownership_level=(
                OwnershipLevel.PRIMARY
            ),
        )
    ]

    successors = [

        SuccessorCandidate(
            developer_ref=EntityRef(
                id="emma",
                type=EntityType.DEVELOPER,
            ),
            module_ref=module_ref,
            score=70,
            rank=1,
        )
    ]

    concentration_reports = [

        ConcentrationReport(
            module_ref=module_ref,
            expert_count=3,
            concentration_score=0.98,
            concentration_level="HIGH",
        )
    ]

    plans = (
        SimpleTransferPolicy()
        .recommend(
            ownerships,
            successors,
            concentration_reports,
        )
    )

    print(
        "\n=== TRANSFER PLAN ===\n"
    )

    for plan in plans:

        print(
            f"Module: "
            f"{plan.module_ref.id}"
        )

        print(
            f"Mentor: "
            f"{plan.mentor_ref.id}"
        )

        print(
            f"Learner: "
            f"{plan.learner_ref.id}"
        )

        print(
            f"Priority: "
            f"{plan.priority_score:.2f}"
        )

        print(
            f"Bus Factor: "
            f"{plan.bus_factor}"
        )

        print(
            f"Concentration: "
            f"{plan.concentration_score:.2f}"
        )

        print(
            f"Reason: "
            f"{plan.reason}"
        )

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()