from .intervention_plan import (
    InterventionPlan,
)


class InterventionPlanner:

    def create_plan(
        self,
        module_ref,
        interventions,
    ):

        interventions = sorted(
            interventions,
            key=lambda intervention: (
                intervention.expected_health_gain
            ),
            reverse=True,
        )

        total_gain = sum(
            intervention.expected_health_gain
            for intervention in interventions
        )

        return InterventionPlan(
            module_ref=module_ref,
            interventions=interventions,
            total_expected_gain=(
                total_gain
            ),
        )