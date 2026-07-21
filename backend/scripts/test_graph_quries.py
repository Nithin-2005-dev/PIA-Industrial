from app.domain.entity_ref import (
    EntityRef,
)
from app.domain.entity_type import (
    EntityType,
)

from app.graph.builders.pia_graph_builder import (
    PIAGraphBuilder,
)

from app.graph.graph_service import (
    GraphService,
)

from app.knowledge_risk.knowledge_risk import (
    KnowledgeRisk,
)

from app.ownership.ownership_estimate import (
    OwnershipEstimate,
)
from app.ownership.ownership_level import (
    OwnershipLevel,
)

from app.risk.risk_level import (
    RiskLevel,
)

from app.successor.successor_candidate import (
    SuccessorCandidate,
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
        )
    ]

    risks = [
        KnowledgeRisk(
            module_ref=module_ref,
            risk_level=RiskLevel.HIGH,
            bus_factor=1,
            ownership_count=1,
            summary="High risk",
        )
    ]

    successors = [
        SuccessorCandidate(
            developer_ref=EntityRef(
                id="bob",
                type=EntityType.DEVELOPER,
            ),
            module_ref=module_ref,
            score=20,
            rank=1,
        )
    ]

    graph = (
        PIAGraphBuilder()
        .build(
            ownership,
            risks,
            successors,
        )
    )

    service = GraphService(
        graph,
    )

    print(
        "\n=== OWNERS ===\n"
    )

    for edge in (
        service.find_by_relationship(
            "OWNS"
        )
    ):

        print(
            edge.source_id
        )

    print(
        "\n=== SUCCESSORS ===\n"
    )

    for edge in (
        service.find_by_relationship(
            "SUCCESSOR"
        )
    ):

        print(
            edge.source_id
        )

    print(
        "\n=== RISKS ===\n"
    )

    for edge in (
        service.find_by_relationship(
            "RISK"
        )
    ):

        print(
            edge.target_id
        )


if __name__ == "__main__":
    main()