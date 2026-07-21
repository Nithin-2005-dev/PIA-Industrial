from pathlib import Path
import sys

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    ),
)

from app.decision import DecisionOptimizationEngine
from app.decision import DecisionOptimizationRequest
from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.executive.intervention_cost import InterventionCost
from app.intervention.intervention_impact import InterventionImpact
from app.platform import PlatformRuntime
from app.platform import default_platform_modules


def _module(
    identifier: str,
) -> EntityRef:
    return EntityRef(
        id=identifier,
        type=EntityType.FILE,
    )


def main():
    runtime_module = _module("backend/app/platform/runtime.py")
    graph_module = _module("backend/app/graph/graph_service.py")
    impacts = (
        InterventionImpact(
            module_ref=runtime_module,
            action="Immediate knowledge transfer",
            expected_health_gain=30,
            reason="High risk",
        ),
        InterventionImpact(
            module_ref=runtime_module,
            action="Train additional experts",
            expected_health_gain=16,
            reason="Coverage",
        ),
        InterventionImpact(
            module_ref=graph_module,
            action="Reduce knowledge concentration",
            expected_health_gain=20,
            reason="Concentration",
        ),
    )
    costs = (
        InterventionCost(
            module_ref=runtime_module,
            action="Immediate knowledge transfer",
            estimated_cost=10,
        ),
        InterventionCost(
            module_ref=runtime_module,
            action="Train additional experts",
            estimated_cost=15,
        ),
        InterventionCost(
            module_ref=graph_module,
            action="Reduce knowledge concentration",
            estimated_cost=20,
        ),
    )
    plan = DecisionOptimizationEngine().optimize(
        DecisionOptimizationRequest(
            impacts=impacts,
            costs=costs,
            budget=25,
            max_items=2,
        )
    )
    assert plan.total_cost <= 25
    assert plan.total_expected_gain == 46
    assert len(plan.selected_items) == 2
    assert plan.selected_items[0].rank == 1
    assert plan.total_roi > 0
    assert plan.rejected_count == 1

    platform = PlatformRuntime.create()
    for module in default_platform_modules():
        platform.register_module(module)
    built = platform.build()
    built.initialize()
    assert isinstance(
        built.provider.resolve(DecisionOptimizationEngine),
        DecisionOptimizationEngine,
    )
    assert "decision" in platform.modules.startup_order()
    built.shutdown()

    print("decision_optimization_ok")


if __name__ == "__main__":
    main()

