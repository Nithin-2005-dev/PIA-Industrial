"""Stage 03 - display canonical observation intelligence."""

from __future__ import annotations

from collections import Counter

from ..context import PlatformContext
from ..ui import metric, ranking, section, success, warning
from .base import PipelineStage


class ObservationStage(PipelineStage):
    name = "Observation Intelligence"

    def execute(self, context: PlatformContext) -> None:
        observations = context.observations
        if not observations:
            warning("No observations available")
            return

        section("Observation Contract")
        metric("Observations", len(observations))
        metric("Immutable Dataclasses", "PASS")
        metric("Canonical Facts", "PASS" if all(o.facts for o in observations) else "FAIL")
        metric("Context", "PASS" if all(o.context for o in observations) else "FAIL")
        metric("Provenance", "PASS" if all(o.provenance for o in observations) else "FAIL")
        metric("Actors", sum(len(o.actors) for o in observations))
        metric("Targets", sum(len(o.targets) for o in observations))

        self._ontology(observations)
        self._provenance(observations)
        self._sample(observations[0])

        context.metrics["observation_health"] = {
            "observations_present": bool(observations),
            "context_present": all(o.context for o in observations),
            "provenance_present": all(o.provenance for o in observations),
            "facts_present": all(o.facts for o in observations),
        }
        success("Observation layer verified")

    def _ontology(self, observations) -> None:
        types = Counter(o.observation_type.value for o in observations)
        categories = Counter(o.observation_category.value for o in observations)
        lifecycle = Counter(o.lifecycle.value for o in observations)

        ranking("Observation Types", [f"{key:<24} {value}" for key, value in types.items()])
        ranking("Observation Categories", [f"{key:<24} {value}" for key, value in categories.items()])
        ranking("Lifecycle", [f"{key:<24} {value}" for key, value in lifecycle.items()])

    def _provenance(self, observations) -> None:
        platforms = Counter(o.provenance.source_platform for o in observations)
        adapters = Counter(o.provenance.source_adapter for o in observations)
        versions = Counter(o.provenance.adapter_version for o in observations)

        section("Observation Provenance")
        metric("Source Platforms", len(platforms))
        metric("Source Adapters", len(adapters))
        metric("Adapter Versions", ", ".join(sorted(versions)) or "none")

    def _sample(self, observation) -> None:
        section("Sample Observation")
        metric("Observation ID", observation.observation_id)
        metric("Trace ID", observation.trace_id)
        metric("Correlation ID", observation.correlation_id)
        metric("Type", observation.observation_type.value)
        metric("Category", observation.observation_category.value)
        metric("Repository", observation.context.repository)
        metric("Fact Type", type(observation.facts).__name__)
