from dataclasses import dataclass


@dataclass(frozen=True)
class DepartureScenarioRequest:
    """
    What-if departure scenario.
    """

    strategy_name: str

    module_id: str

    departing_owner_id: str