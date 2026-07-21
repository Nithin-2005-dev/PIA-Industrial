from dataclasses import FrozenInstanceError
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from pathlib import Path
import sys
from uuid import uuid4

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    ),
)

from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.domain.event import Event
from app.domain.event_type import EventType
from app.evidence import EqlEngine
from app.evidence import EqlParser
from app.evidence import EvidenceApi
from app.evidence import EvidenceContext
from app.evidence import EvidenceSeverity
from app.evidence import EvidenceSynthesisEngine
from app.evidence.correlation import EvidenceCorrelationEngine
from app.evidence.graph import EvidenceKnowledgeGraph
from app.evidence.ontology import EvidenceOntology
from app.evidence.ranking import EvidenceRankingEngine
from app.evidence.streaming import StreamingEvidenceEngine
from app.measurement import MeasurementContext
from app.measurement import MeasurementEngine
from app.measurement.domain import ValidationStatus


def developer(
    name,
):
    return EntityRef(
        id=name,
        type=EntityType.DEVELOPER,
    )


def module(
    name,
):
    return EntityRef(
        id=name,
        type=EntityType.FILE,
    )


def event():
    return Event(
        id=uuid4(),
        type=EventType.COMMIT,
        actor_ref=developer(
            "alice"
        ),
        target_refs=(
            module(
                "payments.py"
            ),
            module(
                "billing.py"
            ),
        ),
        occurred_at=datetime.now(
            UTC
        ),
        payload={
            "additions": 40,
            "deletions": 10,
            "total_changes": 50,
            "observation": {
                "behavioral": {
                    "commit": {
                        "files_changed": 2,
                        "total_additions": 40,
                        "total_deletions": 10,
                        "total_changes": 50,
                    }
                },
                "artifact": {
                    "files": [
                        {
                            "filename": "payments.py",
                            "changes": 35,
                            "patch": (
                                "+ if amount > 0:\n"
                                "+     for item in items:\n"
                                "- if old_amount:\n"
                            ),
                        },
                        {
                            "filename": "billing.py",
                            "changes": 15,
                            "patch": "+ while retry:\n",
                        },
                    ]
                },
            },
        },
        metadata={
            "source": "github",
            "gateway": "rest",
        },
    )


def main():
    measurement_context = MeasurementContext(
        timestamp=datetime.now(
            UTC
        ),
        tenant_id="tenant-a",
        source_reliability={
            "github": 0.95,
        },
    )

    measurements = MeasurementEngine.default().measure_event(
        event(),
        measurement_context,
    )

    assert measurements
    assert all(
        measurement.validation_status
        in {
            ValidationStatus.PASSED,
            ValidationStatus.WARNING,
        }
        for measurement in measurements
    )

    context = EvidenceContext(
        timestamp=datetime.now(
            UTC
        ),
        tenant_id="tenant-a",
        organization_id="org-a",
        installed_evidence_packs=(
            "core-software-evidence",
        ),
    )

    synthesis = EvidenceSynthesisEngine()
    package = synthesis.synthesize(
        measurements,
        context,
    )

    assert package.evidence
    assert package.for_expertise() == package.evidence

    hotspot = package.evidence[0]
    assert hotspot.name == "High-Risk Maintenance Hotspot"
    assert hotspot.severity == EvidenceSeverity.HIGH
    assert hotspot.supporting_measurements
    assert hotspot.provenance.source_layer == (
        "Measurement Operating System"
    )
    assert hotspot.lineage.source_measurement_ids
    assert hotspot.validation_results
    assert 0.0 < hotspot.confidence <= 1.0
    assert hotspot.traceability.confidence_factors[
        "measurement_confidence"
    ] > 0.0

    try:
        hotspot.confidence = 0.0
        raise AssertionError(
            "Evidence must be immutable"
        )
    except FrozenInstanceError:
        pass

    ranked = EvidenceRankingEngine().rank(
        package.evidence
    )
    assert ranked[0].confidence >= 0.0

    parsed = EqlParser().parse(
        """
        FIND Evidence
        WHERE
        confidence > 0.0
        AND severity >= HIGH
        ORDER BY priority DESC
        """
    )
    queried = EqlEngine().query(
        package.evidence,
        parsed,
    )
    assert queried

    graph = EvidenceKnowledgeGraph()
    for item in package.evidence:
        graph.add_evidence(
            item
        )

    assert graph.nodes()
    assert graph.lineage(
        hotspot.evidence_id
    )
    assert graph.impact_analysis(
        hotspot.lineage.source_measurement_ids[0]
    )

    correlations = EvidenceCorrelationEngine(
        EvidenceOntology.default()
    ).correlate(
        package.evidence
    )
    assert all(
        not correlation.implies_causation
        for correlation in correlations
    )

    api = EvidenceApi()
    api_package = api.generate(
        measurements,
        context,
    )
    assert api_package.evidence
    assert api.lookup(
        hotspot.evidence_id,
        "tenant-a",
    )
    assert api.search(
        "FIND Evidence\nWHERE\nconfidence > 0.0",
        "tenant-a",
    )
    assert api.explanation(
        hotspot.evidence_id,
        "tenant-a",
    )[
        "confidence_factors"
    ]
    assert api.lineage(
        hotspot.evidence_id,
        "tenant-a",
    )
    assert api.graph(
        "tenant-a"
    ).nodes()
    assert api.export(
        "tenant-a"
    )

    failed_measurements = tuple(
        replace(
            measurement,
            validation_status=ValidationStatus.FAILED,
        )
        if measurement.definition.id == "code_churn"
        else measurement
        for measurement in measurements
    )

    rejected_package = synthesis.synthesize(
        list(
            failed_measurements
        ),
        context,
    )
    assert all(
        evidence.name != "High-Risk Maintenance Hotspot"
        for evidence in rejected_package.evidence
    )

    updates = []
    streaming = StreamingEvidenceEngine(
        synthesis
    )
    streaming.subscribe(
        updates.append
    )
    update = streaming.ingest(
        tuple(
            measurements
        ),
        context,
    )
    replay = streaming.replay(
        context,
    )
    assert update.package.evidence
    assert replay.replay_sequence == 2
    assert updates

    print(
        "\n=== EVIDENCE INTELLIGENCE PLATFORM ===\n"
    )
    for evidence in ranked:
        print(
            f"{evidence.name:<36}"
            f"category={evidence.category:<18}"
            f"confidence={evidence.confidence:.2f} "
            f"priority={evidence.priority.value}"
        )

    print(
        "\nEvidence platform passed."
    )


if __name__ == "__main__":
    main()

