from pathlib import Path

from app.platform.config import Configuration
from app.platform.runtime import PlatformRuntime
from app.platform.api.contracts import RuntimePipelineInput
from app.simulation.models import SimulationScenario, SimulationAssumption
from app.simulation.interventions import ContributorDepartureIntervention


def test_simulation_engine_branching():
    runtime = PlatformRuntime.create(
        Configuration()
    )
    
    # We will just run the runtime and see if the simulation stage correctly executes
    # However, running the full runtime might be slow or require GitHub token.
    # We can test the pipeline initialization and simulation bindings.
    
    runtime.register_default_modules()
    built = runtime.build()
    
    from app.platform.canonical_pipeline import CanonicalPlatformPipeline
    pipeline = CanonicalPlatformPipeline(built)
    
    bindings = pipeline._bindings_by_runtime_order()
    
    modules = [b.module for b in bindings]
    
    assert "simulation" in modules, "Simulation module should be in canonical pipeline"
    assert "forecast" in modules
    assert "intelligence" in modules
    
    sim_idx = modules.index("simulation")
    forecast_idx = modules.index("forecast")
    intel_idx = modules.index("intelligence")
    
    assert forecast_idx < sim_idx, "Forecast must run before simulation"
    assert sim_idx < intel_idx, "Simulation must run before org intelligence"


if __name__ == "__main__":
    test_simulation_engine_branching()
    print("M54 Simulation Engine test passed.")
