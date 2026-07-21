from dataclasses import dataclass


@dataclass(frozen=True)
class InterventionScenarioRequest:

    strategy_name: str

    module_id: str

    horizon: int 