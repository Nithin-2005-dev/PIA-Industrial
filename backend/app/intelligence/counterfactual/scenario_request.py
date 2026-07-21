from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioRequest:
    """
    Input scenario definition.
    """

    strategy_name: str

    module_id: str

    horizon: int = 3