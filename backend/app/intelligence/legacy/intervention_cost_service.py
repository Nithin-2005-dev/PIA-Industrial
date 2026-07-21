from .intervention_cost import (
    InterventionCost,
)


class InterventionCostService:
    """
    Simple heuristic cost model.

    Costs are relative effort units,
    not dollars.
    """

    COSTS = {

        "Immediate knowledge transfer": 10.0,

        "Train additional experts": 15.0,

        "Reduce knowledge concentration": 20.0,
    }

    def estimate(
        self,
        interventions,
    ):

        costs = []

        for intervention in interventions:

            estimated_cost = (
                self.COSTS.get(
                    intervention.action,
                    10.0,
                )
            )

            costs.append(
                InterventionCost(
                    module_ref=(
                        intervention.module_ref
                    ),
                    action=(
                        intervention.action
                    ),
                    estimated_cost=(
                        estimated_cost
                    ),
                )
            )

        return costs