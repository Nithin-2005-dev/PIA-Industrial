from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyScenarioRequest:

    module_id: str

    departing_owner_id: str

    horizon: int = 3