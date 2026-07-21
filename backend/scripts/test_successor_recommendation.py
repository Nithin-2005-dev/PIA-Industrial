from app.domain.entity_ref import (
    EntityRef,
)
from app.domain.entity_type import (
    EntityType,
)

from app.ownership.ownership_estimate import (
    OwnershipEstimate,
)
from app.ownership.ownership_level import (
    OwnershipLevel,
)

from app.successor.policies.expertise_successor_policy import (
    ExpertiseSuccessorPolicy,
)


def main():

    module_ref = EntityRef(
        id="auth.py",
        type=EntityType.FILE,
    )

    ownership = [

        OwnershipEstimate(
            owner_ref=EntityRef(
                id="alice",
                type=EntityType.DEVELOPER,
            ),
            module_ref=module_ref,
            ownership_percentage=0.70,
            effective_score=70,
            ownership_level=(
                OwnershipLevel.PRIMARY
            ),
        ),

        OwnershipEstimate(
            owner_ref=EntityRef(
                id="bob",
                type=EntityType.DEVELOPER,
            ),
            module_ref=module_ref,
            ownership_percentage=0.20,
            effective_score=20,
            ownership_level=(
                OwnershipLevel.SECONDARY
            ),
        ),

        OwnershipEstimate(
            owner_ref=EntityRef(
                id="charlie",
                type=EntityType.DEVELOPER,
            ),
            module_ref=module_ref,
            ownership_percentage=0.10,
            effective_score=10,
            ownership_level=(
                OwnershipLevel.CONTRIBUTOR
            ),
        ),
    ]

    policy = (
        ExpertiseSuccessorPolicy()
    )

    successors = (
        policy.recommend(
            ownership,
            limit=5,
        )
    )

    print(
        "\n=== SUCCESSOR RECOMMENDATIONS ===\n"
    )

    for candidate in successors:

        print(
            f"Rank #{candidate.rank}"
        )

        print(
            f"Developer: "
            f"{candidate.developer_ref.id}"
        )

        print(
            f"Score: "
            f"{candidate.score}"
        )

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()