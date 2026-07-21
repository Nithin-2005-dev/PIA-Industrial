from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import replace

from app.intelligence.measurement.domain import Measurement


@dataclass(frozen=True)
class NormalizationStageResult:
    measurement: Measurement
    stage_name: str


class NormalizationStage(ABC):
    name: str

    @abstractmethod
    def apply(
        self,
        measurement: Measurement,
    ) -> Measurement:
        raise NotImplementedError


class CleaningStage(NormalizationStage):
    name = "cleaning"

    def apply(
        self,
        measurement: Measurement,
    ) -> Measurement:
        return replace(
            measurement,
            metadata={
                **measurement.metadata,
                "cleaned": True,
            },
        )


class CalibrationStage(NormalizationStage):
    name = "calibration"

    def apply(
        self,
        measurement: Measurement,
    ) -> Measurement:
        calibration_factor = float(
            measurement.metadata.get(
                "calibration_factor",
                1.0,
            )
        )

        return replace(
            measurement,
            value=measurement.value * calibration_factor,
            metadata={
                **measurement.metadata,
                "calibration_factor": calibration_factor,
            },
        )


class ScalingStage(NormalizationStage):
    name = "scaling"

    def apply(
        self,
        measurement: Measurement,
    ) -> Measurement:
        scale = float(
            measurement.metadata.get(
                "scale",
                1.0,
            )
        )

        return replace(
            measurement,
            value=measurement.value * scale,
            metadata={
                **measurement.metadata,
                "scale": scale,
            },
        )


class BiasCorrectionStage(NormalizationStage):
    name = "bias_correction"

    def apply(
        self,
        measurement: Measurement,
    ) -> Measurement:
        bias = float(
            measurement.metadata.get(
                "bias",
                0.0,
            )
        )

        return replace(
            measurement,
            value=measurement.value - bias,
            metadata={
                **measurement.metadata,
                "bias": bias,
            },
        )


class NormalizationPipeline:

    def __init__(
        self,
        stages: list[NormalizationStage],
    ):
        self._stages = stages

    @classmethod
    def default(
        cls,
    ):
        return cls(
            stages=[
                CleaningStage(),
                CalibrationStage(),
                ScalingStage(),
                BiasCorrectionStage(),
            ]
        )

    def apply(
        self,
        measurement: Measurement,
    ) -> tuple[Measurement, tuple[str, ...]]:
        current = measurement
        stage_names = []

        for stage in self._stages:
            current = stage.apply(
                current
            )
            stage_names.append(
                stage.name
            )

        return (
            current,
            tuple(stage_names),
        )


