"""Stage 07e — Counterfactual Simulation Engine."""

from __future__ import annotations

from typing import cast

from app.simulation.engine import ScenarioComparisonEngine, SimulationEngine
from app.simulation.models import SimulationContext, SimulationScenario, SimulationAssumption
from app.simulation.interventions import ContributorDepartureIntervention, OwnershipRedistributionIntervention

from ..context import PlatformContext
from ..ui import metric, section, success, warning
from .base import PipelineStage


class SimulationStage(PipelineStage):
    """
    Generates scenarios, applies interventions, and executes branches via PlatformRuntime.
    """
    name = "Counterfactual Simulation"

    def execute(self, context: PlatformContext) -> None:
        if not context.forecast_context:
            warning("No ForecastContext available — skipping Simulation")
            return

        section("Counterfactual Simulation Engine")

        # In a real system, we resolve the SimulationRegistry. For the showcase, we'll
        # just define a couple scenarios here directly to demonstrate the capability.
        
        # Determine actual primary and secondary maintainers from expertise models
        top_devs = {}
        for m in context.expertise_models:
            top_devs[m.subject] = top_devs.get(m.subject, 0.0) + m.score
        
        sorted_devs = sorted(top_devs.items(), key=lambda x: x[1], reverse=True)
        primary_dev = sorted_devs[0][0] if sorted_devs else "unknown"
        secondary_dev = sorted_devs[1][0] if len(sorted_devs) > 1 else "unknown"

        # Scenario 1: Primary maintainer leaves
        scen1 = SimulationScenario(
            name="Primary Maintainer Departure",
            description=f"The most prolific contributor ({primary_dev}) leaves the project.",
            assumptions=(
                SimulationAssumption(f"Primary maintainer's ({primary_dev}) expertise is completely lost."),
                SimulationAssumption("No immediate backfill is available."),
            ),
            interventions=(
                ContributorDepartureIntervention(developer_id=primary_dev),
            )
        )
        
        # Scenario 2: Knowledge Transfer
        scen2 = SimulationScenario(
            name="Targeted Knowledge Transfer",
            description=f"Transfer ownership from primary ({primary_dev}) to secondary ({secondary_dev}).",
            assumptions=(
                SimulationAssumption(f"Secondary ({secondary_dev}) absorbs the knowledge smoothly."),
            ),
            interventions=(
                OwnershipRedistributionIntervention(from_developer=primary_dev, to_developer=secondary_dev),
            )
        )

        scenarios = [scen1, scen2]
        
        # Resolve engines
        sim_engine = context.resolve(SimulationEngine)
        comp_engine = context.resolve(ScenarioComparisonEngine)

        completed_scenarios = []

        for scenario in scenarios:
            metric("Evaluating Scenario", scenario.name)
            
            # 1. Generate Context (clone + intervene)
            scenario_context = sim_engine.generate_scenario_context(context, scenario)
            
            # 2. Execute Branch via Runtime
            branch_result = context.runtime.branch(
                baseline_context=scenario_context.baseline_context, 
                scenario=scenario_context.scenario,
                built_runtime=context.service_provider._built_runtime if hasattr(context.service_provider, '_built_runtime') else None
            )
            
            # 3. Store result in scenario context
            scenario_context.execution_result = branch_result.execution_result
            
            # 4. We can only do comparison if the baseline has already been run... 
            # Wait, the main pipeline hasn't run Org Intelligence yet!
            # The baseline_context doesn't have Org Intelligence yet!
            # Ah! If the Simulation runs *before* Org Intelligence, how do we compare?
            # The comparison must be done *after* the baseline runs, or the SimulationStage just stores the branches.
            
            completed_scenarios.append(branch_result)

        # Store in PlatformContext
        context.simulation_context = SimulationContext(
            scenarios=tuple(completed_scenarios)
        )

        success(f"Generated {len(scenarios)} counterfactual scenarios")
