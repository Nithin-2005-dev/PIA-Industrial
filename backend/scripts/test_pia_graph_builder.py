from app.domain.entity_ref import (
    EntityRef,
)
from app.domain.entity_type import (
    EntityType,
)

from app.graph.builders.pia_graph_builder import (
    PIAGraphBuilder,
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

    builder = PIAGraphBuilder()

    graph = builder.build(
        ownership,
        risks,
        successors,
    )

    print(
        "\n=== PIA GRAPH ===\n"
    )

    print(
        f"Nodes: {len(graph.nodes)}"
    )

    print(
        f"Edges: {len(graph.edges)}"
    )

    print()

    for edge in graph.edges:

        print(
            f"{edge.source_id}"
            f" --{edge.relationship}--> "
            f"{edge.target_id}"
        )


if __name__ == "__main__":
    main()