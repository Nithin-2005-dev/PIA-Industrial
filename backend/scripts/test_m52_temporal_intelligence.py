"""
M52 Regression Test — Temporal Intelligence Engine

Verifies:
1. TemporalPlatformModule is registered and ordered correctly.
2. Snapshot creation and repository persistence.
3. Delta and trend calculation (velocity, acceleration, momentum).
4. HistoricalContext assembly.
"""

import sys
import tempfile
from pathlib import Path
from dataclasses import dataclass, field

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1]),
)

from app.platform import PlatformRuntime
from app.temporal.snapshot_repository import SnapshotRepository
from app.temporal.temporal_engine import TemporalEngine
from scripts.platform_showcase.context import PlatformContext


@dataclass
class MockEvidencePackage:
    evidence: list = ()

@dataclass
class MockOrgHealth:
    average_health: float = 85.0

@dataclass
class MockOrgIntelligence:
    health: MockOrgHealth = field(default_factory=MockOrgHealth)


def test_temporal_engine():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # ------------------------------------------------------------------
        # Test 1: Module registration and DI
        # ------------------------------------------------------------------
        runtime = PlatformRuntime.create()
        runtime.register_default_modules()
        modules = runtime.modules.startup_order()

        assert "temporal" in modules, "Temporal module not registered"
        assert modules.index("graph") < modules.index("temporal"), "Temporal must follow graph"
        assert modules.index("temporal") < modules.index("intelligence"), "Intelligence must follow temporal"

        provider = runtime.services.build_provider()
        repository = provider.resolve(SnapshotRepository)
        # Patch the path to not pollute showcase output
        repository._root = tmp_path
        
        engine = provider.resolve(TemporalEngine)

        # ------------------------------------------------------------------
        # Run 1: First snapshot (No history)
        # ------------------------------------------------------------------
        ctx1 = PlatformContext(
            repository="test/repo",
            branch="main",
            commit_limit=10,
            github_token=None,
            tenant_id="default",
            output_directory=tmp_path,
        )
        ctx1.observations = [1, 2, 3]
        ctx1.measurements = [1, 2]
        ctx1.evidence_package = MockEvidencePackage(evidence=[1])
        ctx1.expertise_models = []
        ctx1.knowledge = []
        ctx1.knowledge_graph = None
        ctx1.org_intelligence = MockOrgIntelligence()
        
        # Build context
        historical1 = engine.build_historical_context(ctx1)
        assert historical1.snapshot_count == 0
        assert not historical1.has_history
        assert historical1.delta is None
        
        # Persist snapshot (this simulates what canonical pipeline does)
        snapshot1 = engine.create_snapshot(ctx1)
        repository.save(snapshot1)
        
        assert repository.snapshot_count("test/repo", "main") == 1

        # ------------------------------------------------------------------
        # Run 2: Second snapshot (Computes delta)
        # ------------------------------------------------------------------
        ctx2 = PlatformContext(
            repository="test/repo",
            branch="main",
            commit_limit=10,
            github_token=None,
            tenant_id="default",
            output_directory=tmp_path,
        )
        # Increase counts to create a delta
        ctx2.observations = [1, 2, 3, 4, 5]
        ctx2.measurements = [1, 2, 3]
        ctx2.evidence_package = MockEvidencePackage(evidence=[1, 2])
        ctx2.expertise_models = []
        ctx2.knowledge = []
        ctx2.knowledge_graph = None
        ctx2.org_intelligence = MockOrgIntelligence(health=MockOrgHealth(average_health=90.0))
        
        historical2 = engine.build_historical_context(ctx2)
        assert historical2.has_history
        assert historical2.snapshot_count == 1
        assert historical2.delta is not None
        
        assert historical2.delta.observation_delta == 2
        assert historical2.delta.measurement_delta == 1
        assert historical2.delta.evidence_delta == 1
        assert historical2.delta.health_delta == 5.0
        
        snapshot2 = engine.create_snapshot(ctx2)
        repository.save(snapshot2)
        assert repository.snapshot_count("test/repo", "main") == 2

        # ------------------------------------------------------------------
        # Run 3: Third snapshot (Tests trends)
        # ------------------------------------------------------------------
        ctx3 = PlatformContext(
            repository="test/repo",
            branch="main",
            commit_limit=10,
            github_token=None,
            tenant_id="default",
            output_directory=tmp_path,
        )
        # Further increase
        ctx3.observations = [1, 2, 3, 4, 5, 6, 7]  # +2
        ctx3.measurements = [1, 2, 3, 4]           # +1
        ctx3.evidence_package = MockEvidencePackage(evidence=[1, 2, 3])  # +1
        
        historical3 = engine.build_historical_context(ctx3)
        
        # Check trends for observations:
        # Snapshot 1: 3
        # Snapshot 2: 5 (velocity = 2)
        # Current temp: 7 (velocity = 2)
        # Acceleration = current vel (2) - prev vel (2) = 0
        # Momentum = velocity (2) * window (3) = 6
        
        obs_trend = next(t for t in historical3.trends if t.metric_name == "observations")
        assert obs_trend.velocity == 2.0
        assert obs_trend.acceleration == 0.0
        assert obs_trend.momentum == 6.0
        assert obs_trend.direction == "IMPROVING"

        print("m52_temporal_intelligence_ok")


if __name__ == "__main__":
    test_temporal_engine()
