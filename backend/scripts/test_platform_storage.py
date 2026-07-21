from datetime import UTC
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import sys

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1]),
)

from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.evidence.core import EvidenceContext
from app.evidence.semantic import SemanticEvidenceEngine
from app.measurement.domain import MeasurementContext
from app.measurement.scientific_engine import ScientificMeasurementEngine
from app.observation.domain import CommitFacts
from app.observation.domain import FileChangeFacts
from app.observation.domain import Observation
from app.observation.domain import ObservationCategory
from app.observation.domain import ObservationContext
from app.observation.domain import ObservationLifecycle
from app.observation.domain import ObservationProvenance
from app.observation.domain import ObservationType
from app.observation.ingestion import SyncCursor
from app.platform import PlatformRuntime
from app.platform import PlatformStorage
from app.platform import default_platform_modules


def make_observation():
    return Observation(
        observation_id="storage-commit-1",
        trace_id="trace-storage-commit-1",
        correlation_id="corr-storage-commit-1",
        timestamp=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
        observation_type=ObservationType.COMMIT,
        observation_category=ObservationCategory.SOURCE_CONTROL,
        source_platform="github",
        source_adapter="github",
        version="1.0",
        lifecycle=ObservationLifecycle.PRODUCTION,
        actors=(EntityRef(id="alice", type=EntityType.DEVELOPER),),
        targets=(EntityRef(id="src/storage.py", type=EntityType.FILE),),
        provenance=ObservationProvenance(
            source_platform="github",
            source_adapter="github",
            source_record_id="storage-commit-1",
        ),
        context=ObservationContext(repository="pia", tenant_id="tenant-a"),
        facts=CommitFacts(
            commit_id="storage-commit-1",
            message="Add durable storage",
            author_name="Alice",
            author_email="alice@example.com",
            authored_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
            total_additions=12,
            total_deletions=2,
            total_changes=14,
            files=(
                FileChangeFacts(
                    path="src/storage.py",
                    status="modified",
                    additions=12,
                    deletions=2,
                    changes=14,
                ),
            ),
        ),
    )


def main():
    with TemporaryDirectory() as directory:
        storage = PlatformStorage(directory)
        observation = make_observation()
        measurements = ScientificMeasurementEngine().measure_observations(
            [observation],
            MeasurementContext(
                timestamp=datetime.now(UTC),
                tenant_id="tenant-a",
                source_reliability={"github": 0.96},
            ),
        )
        evidence_package = SemanticEvidenceEngine().synthesize(
            list(measurements),
            EvidenceContext(tenant_id="tenant-a"),
        )

        storage.append_observation(observation)
        for measurement in measurements:
            storage.append_measurement(measurement)
        for evidence in evidence_package.evidence:
            storage.append_evidence(evidence)
        storage.save_checkpoint(
            "github",
            SyncCursor(adapter="github", cursor="abc", offset=10),
        )
        storage.append_history(
            "snapshot:1",
            {"health": 0.95, "timestamp": datetime.now(UTC)},
        )

        reloaded = PlatformStorage(directory)
        assert reloaded.observations.find("observation", observation.observation_id)
        assert len(reloaded.measurements.read_all("measurement")) == len(measurements)
        assert len(reloaded.evidence.read_all("evidence")) == len(evidence_package.evidence)
        assert reloaded.checkpoints.find("checkpoint", "github")
        assert reloaded.history.find("history", "snapshot:1")

    platform = PlatformRuntime.create()
    for module in default_platform_modules():
        platform.register_module(module)
    built = platform.build()
    built.initialize()
    built.start()
    assert built.provider.resolve(PlatformStorage)
    built.shutdown()

    print("\n=== PLATFORM STORAGE ===\n")
    print("M42 Durable Platform Storage passed.")


if __name__ == "__main__":
    main()

