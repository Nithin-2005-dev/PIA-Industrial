from app.simulation.engine import SimulationEngine
from app.simulation.models import SimulationScenario
from app.simulation.interventions import ContributorDepartureIntervention
from scripts.platform_showcase.context import PlatformContext
from app.domain.entity_ref import EntityRef, EntityType

class MockHealthSummary:
    def __init__(self, average_health: float):
        self.average_health = average_health

class MockOrgIntelligence:
    def __init__(self):
        self.health = MockHealthSummary(85.0)
        self.forecast_available = True

class MockEvidencePackage:
    def __init__(self):
        self.evidence = ["mock_evidence"]

def test_simulation_immutability():
    # 1. Setup a baseline context
    baseline_context = PlatformContext(
        repository="mock/repo",
        branch="main",
        commit_limit=10,
        tenant_id="tenant-1",
        github_token="",
        output_directory="",
    )
    baseline_context.org_intelligence = MockOrgIntelligence()
    baseline_context.evidence_package = MockEvidencePackage()

    # 2. Setup a scenario
    intervention = ContributorDepartureIntervention(
        developer_id="alice"
    )
    scenario = SimulationScenario(
        name="Alice Departs",
        description="Test simulation",
        assumptions=(),
        interventions=(intervention,)
    )

    # 3. Generate branched context
    engine = SimulationEngine()
    scenario_context = engine.generate_scenario_context(baseline_context, scenario)

    # 4. Modify the branched context (simulating downstream changes)
    scenario_context.cloned_context.org_intelligence.health.average_health = 60.0
    scenario_context.cloned_context.evidence_package.evidence.append("scenario_evidence")

    # 5. Verify immutability of the baseline
    assert baseline_context.org_intelligence.health.average_health == 85.0, "Baseline health was mutated!"
    assert len(baseline_context.evidence_package.evidence) == 1, "Baseline evidence was mutated!"
    
    print("Simulation immutability verified. Baseline remains unchanged while clone mutates.")

if __name__ == "__main__":
    test_simulation_immutability()
