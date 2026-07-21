from dataclasses import dataclass

from app.intelligence.measurement.domain import Measurement


@dataclass(frozen=True)
class LineageNode:
    id: str
    kind: str
    label: str
    metadata: dict


@dataclass(frozen=True)
class LineageEdge:
    source_id: str
    target_id: str
    relationship: str


@dataclass(frozen=True)
class MeasurementLineageGraph:
    nodes: tuple[LineageNode, ...]
    edges: tuple[LineageEdge, ...]


class MeasurementLineageService:

    def graph_for(
        self,
        measurement: Measurement,
    ) -> MeasurementLineageGraph:
        observation_id = (
            measurement.provenance.source_observation_id
            or measurement.provenance.source_event_id
            or "unknown-observation"
        )
        adapter_id = (
            f"adapter:{measurement.provenance.source_system}:"
            f"{measurement.provenance.adapter}"
        )
        definition_id = (
            f"definition:{measurement.definition.id}:"
            f"{measurement.definition.version}"
        )

        nodes = [
            LineageNode(
                id=observation_id,
                kind="observation",
                label="Source Observation",
                metadata={},
            ),
            LineageNode(
                id=adapter_id,
                kind="adapter",
                label=measurement.provenance.adapter,
                metadata={
                    "source": measurement.provenance.source_system,
                },
            ),
            LineageNode(
                id=definition_id,
                kind="definition",
                label=measurement.definition.name,
                metadata={
                    "unit": measurement.unit.value,
                    "version": measurement.definition.version,
                },
            ),
            LineageNode(
                id=measurement.id,
                kind="measurement",
                label=measurement.definition.name,
                metadata={
                    "value": measurement.value,
                    "confidence": measurement.confidence,
                    "quality": measurement.quality_score,
                },
            ),
        ]

        edges = [
            LineageEdge(
                source_id=observation_id,
                target_id=adapter_id,
                relationship="observed_by",
            ),
            LineageEdge(
                source_id=adapter_id,
                target_id=definition_id,
                relationship="transformed_into",
            ),
            LineageEdge(
                source_id=definition_id,
                target_id=measurement.id,
                relationship="computed_as",
            ),
        ]

        for dependency_id in measurement.dependencies:
            nodes.append(
                LineageNode(
                    id=dependency_id,
                    kind="dependency",
                    label=dependency_id,
                    metadata={},
                )
            )
            edges.append(
                LineageEdge(
                    source_id=dependency_id,
                    target_id=measurement.id,
                    relationship="depends_on",
                )
            )

        return MeasurementLineageGraph(
            nodes=tuple(nodes),
            edges=tuple(edges),
        )


class MeasurementExplainer:

    def explain(
        self,
        measurement: Measurement,
    ) -> dict:
        return {
            "id": measurement.id,
            "why": measurement.definition.description,
            "concept": measurement.definition.concept_id,
            "value": measurement.value,
            "unit": measurement.unit.value,
            "confidence": measurement.confidence,
            "confidence_breakdown": (
                measurement.confidence_breakdown
                if measurement.confidence_breakdown is not None
                else None
            ),
            "uncertainty": measurement.uncertainty,
            "quality_score": measurement.quality_score,
            "dependencies": measurement.dependencies,
            "normalization": measurement.normalization_method,
            "formula": measurement.traceability.formula,
            "version": measurement.version,
            "provenance": measurement.provenance,
            "validation_status": measurement.validation_status.value,
        }


