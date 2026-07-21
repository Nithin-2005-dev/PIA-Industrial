from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EstimationContext:
    """
    Context required for a latent state transition.

    Keeps estimators independent from
    infrastructure concerns.
    """

    current_time: datetime

    learning_rate: float

    replay_mode: bool = False