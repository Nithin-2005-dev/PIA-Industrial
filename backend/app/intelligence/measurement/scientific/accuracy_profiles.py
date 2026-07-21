from dataclasses import dataclass


@dataclass(frozen=True)
class MeasurementAccuracyProfile:
    measurement_id: str
    expected_error: float
    confidence_calibration: str
    known_biases: tuple[str, ...]
    sensitivity: str
    robustness: str
    reliability: float
    minimum_required_signals: tuple[str, ...]
    recommended_interpretation: str
    failure_conditions: tuple[str, ...]


class AccuracyProfileRegistry:

    def __init__(
        self,
    ):
        self._profiles = {}

    def register(
        self,
        profile: MeasurementAccuracyProfile,
    ):
        self._profiles[
            profile.measurement_id
        ] = profile

    def get(
        self,
        measurement_id: str,
    ) -> MeasurementAccuracyProfile | None:
        return self._profiles.get(
            measurement_id
        )

    def all(
        self,
    ) -> list[MeasurementAccuracyProfile]:
        return list(
            self._profiles.values()
        )


