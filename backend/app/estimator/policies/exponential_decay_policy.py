from datetime import datetime
from math import exp

from .decay_policy import DecayPolicy


class ExponentialDecayPolicy(
    DecayPolicy
):
    """
    Exponential expertise decay.

    More recent expertise retains
    more value than older expertise.
    """

    def __init__(
        self,
        decay_rate: float = 0.001,
    ):
        self._decay_rate = decay_rate

    def apply(
        self,
        score: float,
        last_updated: datetime,
        current_time: datetime,
    ) -> float:

        elapsed_days = (
            current_time - last_updated
        ).days

        decay_factor = exp(
            -self._decay_rate
            * elapsed_days
        )

        return (
            score
            * decay_factor
        )