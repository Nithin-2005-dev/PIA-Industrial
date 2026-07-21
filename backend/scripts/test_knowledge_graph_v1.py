from datetime import UTC
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    ),
)

from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.domain.expertise_estimate import ExpertiseEstimate
from app.graph import GraphService
from app.graph import KnowledgeGraphBuilder
from app.platform import PlatformRuntime
from app.platform import default_platform_modules


def main():
    now = datetime(
        2026,
        7,
        1,
        14,
        0,
        tzinfo=UTC,
    )
    estimates = (
        ExpertiseEstimate(
            developer_ref=EntityRef(
                id="alice",
                type=EntityType.DEVELOPER,
            ),
            module_ref=EntityRef(
                id="backend/app/platform/runtime.py",
                type=EntityType.FILE,
            ),
            raw_score=10.0,
            confidence=0.8,
            updated_at=now,
        ),
        ExpertiseEstimate(
            developer_ref=EntityRef(
                id="bob",
                type=EntityType.DEVELOPER,
            ),
            module_ref=EntityRef(
                id="backend/app/platform/runtime.py",
                type=EntityType.FILE,
            ),
            raw_score=4.0,
            confidence=0.5,
            updated_at=now,
        ),
    )
    graph = KnowledgeGraphBuilder().build(
        expertise_estimates=estimates
    )
    service = GraphService(graph)

    assert len(graph.nodes) == 3
    assert len(graph.edges) == 2
    assert len(service.nodes_by_type("DEVELOPER")) == 2
    assert len(service.find_by_relationship("HAS_EXPERTISE_IN")) == 2
    assert {
        node.id
        for node in service.neighbors("backend/app/platform/runtime.py")
    } == {
        "alice",
        "bob",
    }
    assert service.shortest_path(
        "alice",
        "bob",
    ) == [
        "alice",
        "backend/app/platform/runtime.py",
        "bob",
    ]
    centrality = service.degree_centrality()
    assert (
        centrality["backend/app/platform/runtime.py"]
        > centrality["alice"]
    )
    subgraph = service.subgraph(
        {
            "alice",
            "backend/app/platform/runtime.py",
        }
    )
    assert len(subgraph.nodes) == 2
    assert len(subgraph.edges) == 1

    platform = PlatformRuntime.create()
    for module in default_platform_modules():
        platform.register_module(module)
    built = platform.build()
    built.initialize()
    assert isinstance(
        built.provider.resolve(KnowledgeGraphBuilder),
        KnowledgeGraphBuilder,
    )
    assert isinstance(
        built.provider.resolve(GraphService),
        GraphService,
    )
    built.shutdown()

    print("knowledge_graph_v1_ok")


if __name__ == "__main__":
    main()

