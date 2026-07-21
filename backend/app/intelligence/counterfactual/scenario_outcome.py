from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioOutcome:
    """
    Future state produced by
    scenario execution.
    """

    strategy_name: str

    predicted_health: float

    future_risk_score: float