from dataclasses import dataclass


@dataclass(frozen=True)
class ObservationRequest:
    adapter: str
    reason: str
    required_signals: tuple[str, ...]
    priority: int


class ActiveMeasurementService:

    def requests_for_low_confidence(
        self,
        measurement_id: str,
        confidence: float,
        required_signals: tuple[str, ...],
    ) -> list[ObservationRequest]:
        if confidence >= 0.7:
            return []

        return [
            ObservationRequest(
                adapter="best_available",
                reason=(
                    "measurement confidence below active collection "
                    "threshold"
                ),
                required_signals=required_signals,
                priority=10,
            )
        ]


