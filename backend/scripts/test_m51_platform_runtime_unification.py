from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    ),
)

from app.platform import PlatformRuntime
from app.platform.canonical_pipeline import CanonicalPlatformPipeline
from app.platform.canonical_pipeline import CanonicalStageBinding


class SyntheticStage:
    def __init__(
        self,
        name,
        attribute,
        value,
    ):
        self.name = name
        self.attribute = attribute
        self.value = value

    def run(
        self,
        context,
    ):
        setattr(
            context,
            self.attribute,
            self.value,
        )
        context.metrics[self.attribute] = len(self.value)


def synthetic_bindings(
    self,
):
    return [
        CanonicalStageBinding(
            "observation",
            SyntheticStage("Observation", "observations", [1]),
            "RuntimePipelineInput",
            "PlatformContext.observations",
        ),
        CanonicalStageBinding(
            "measurement",
            SyntheticStage("Measurement", "measurements", [1]),
            "PlatformContext.observations",
            "PlatformContext.measurements",
        ),
        CanonicalStageBinding(
            "evidence",
            SyntheticStage("Evidence", "evidence_package", [1]),
            "PlatformContext.measurements",
            "PlatformContext.evidence_package",
        ),
        CanonicalStageBinding(
            "estimation",
            SyntheticStage("Expertise", "expertise_models", [1]),
            "PlatformContext.evidence_package",
            "PlatformContext.expertise_models",
        ),
        CanonicalStageBinding(
            "knowledge",
            SyntheticStage("Knowledge", "knowledge", [1]),
            "PlatformContext.expertise_models",
            "PlatformContext.knowledge",
        ),
        CanonicalStageBinding(
            "graph",
            SyntheticStage("Knowledge Graph", "knowledge_graph", [1]),
            "PlatformContext.knowledge",
            "PlatformContext.knowledge_graph",
        ),
        CanonicalStageBinding(
            "temporal",
            SyntheticStage("Temporal Intelligence", "historical_context", [1]),
            "PlatformContext.knowledge_graph",
            "PlatformContext.historical_context",
        ),
        CanonicalStageBinding(
            "intelligence",
            SyntheticStage("Organization Intelligence", "org_intelligence", [1]),
            "PlatformContext.historical_context",
            "PlatformContext.org_intelligence",
        ),
        CanonicalStageBinding(
            "agent",
            SyntheticStage("Reasoning", "reasoning_results", [1]),
            "PlatformContext.org_intelligence",
            "PlatformContext.reasoning_results",
        ),
        CanonicalStageBinding(
            "decision",
            SyntheticStage("Decision", "decisions", [1]),
            "PlatformContext.reasoning_results",
            "PlatformContext.decisions",
        ),
        CanonicalStageBinding(
            "executive",
            SyntheticStage("Executive", "metadata", {"executive": True}),
            "PlatformContext.decisions",
            "RuntimePipelineResult",
        ),
    ]


def main():
    runtime = PlatformRuntime.create()
    started = []
    completed = []
    runtime.event_bus.subscribe(
        "runtime.stage.started",
        started.append,
    )
    runtime.event_bus.subscribe(
        "runtime.stage.completed",
        completed.append,
    )

    with patch.object(
        CanonicalPlatformPipeline,
        "_bindings_by_runtime_order",
        synthetic_bindings,
    ):
        result = runtime.run(
            repository="facebook/react",
            commits=100,
        )

    assert result.succeeded

    # ------------------------------------------------------------------
    # 1. Execution order — every module in the exact canonical sequence.
    # ------------------------------------------------------------------
    expected_module_order = (
        "observation",
        "measurement",
        "evidence",
        "estimation",
        "knowledge",
        "graph",        # Knowledge Graph must appear as a first-class stage
        "temporal",
        "intelligence",
        "agent",
        "decision",
        "executive",
    )
    assert tuple(stage.module for stage in result.completed_stages) == (
        expected_module_order
    ), (
        "Completed stages module order does not match the canonical pipeline. "
        "Actual: " + str(tuple(s.module for s in result.completed_stages))
    )

    # ------------------------------------------------------------------
    # 2. Knowledge Graph is present in completed_stages.
    # ------------------------------------------------------------------
    completed_stage_names = tuple(s.name for s in result.completed_stages)
    assert "Knowledge Graph" in completed_stage_names, (
        "Knowledge Graph stage is missing from completed_stages. "
        "Actual names: " + str(completed_stage_names)
    )

    # ------------------------------------------------------------------
    # 3. Knowledge Graph appears in execution_order stored in context metrics.
    # ------------------------------------------------------------------
    execution_order: tuple[str, ...] = result.context.metrics.get(
        "execution_order", ()
    )
    assert "graph" in execution_order, (
        "'graph' module is missing from context.metrics['execution_order']. "
        "Actual order: " + str(execution_order)
    )

    # ------------------------------------------------------------------
    # 4. Knowledge Graph display name appears in execution_stage_names.
    # ------------------------------------------------------------------
    stage_names: tuple[str, ...] = result.context.metrics.get(
        "execution_stage_names", ()
    )
    assert "Knowledge Graph" in stage_names, (
        "'Knowledge Graph' is missing from context.metrics['execution_stage_names']. "
        "Actual: " + str(stage_names)
    )

    # ------------------------------------------------------------------
    # 5. Correct dependency ordering: knowledge < graph < intelligence.
    # ------------------------------------------------------------------
    order_list = list(execution_order)
    assert order_list.index("knowledge") < order_list.index("graph"), (
        "'graph' must come after 'knowledge' in execution_order. "
        "Actual order: " + str(order_list)
    )
    assert order_list.index("graph") < order_list.index("temporal"), (
        "'temporal' must come after 'graph' in execution_order. "
        "Actual order: " + str(order_list)
    )
    assert order_list.index("temporal") < order_list.index("intelligence"), (
        "'intelligence' must come after 'temporal' in execution_order. "
        "Actual order: " + str(order_list)
    )

    # ------------------------------------------------------------------
    # 6. Runtime events: every started stage has a matching completed stage.
    # ------------------------------------------------------------------
    assert tuple(event.payload["stage"] for event in started) == tuple(
        stage.name for stage in result.completed_stages
    )
    assert len(completed) == len(result.completed_stages)

    # ------------------------------------------------------------------
    # 7. All contracts are declared.
    # ------------------------------------------------------------------
    assert all(stage.input_contract for stage in result.completed_stages)
    assert all(stage.output_contract for stage in result.completed_stages)

    assert result.context.decisions == [1]

    print("m51_platform_runtime_unification_ok")
    print(f"  pipeline stages ({len(result.completed_stages)}): "
          + " -> ".join(s.name for s in result.completed_stages))
    print(f"  execution_order: {execution_order}")
    print("  Knowledge Graph: present and correctly ordered [OK]")


if __name__ == "__main__":
    main()
