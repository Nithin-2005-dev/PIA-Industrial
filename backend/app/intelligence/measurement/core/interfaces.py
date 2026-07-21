from abc import ABC, abstractmethod

from app.intelligence.measurement.domain import Measurement, MeasurementContext, ValidationResult
from app.ingestion.observation.domain import Observation


class MeasurementEvaluator(ABC):
    
    @property
    @abstractmethod
    def metric_name(self) -> str:
        """The canonical name of the metric."""
        raise NotImplementedError
        
    @property
    @abstractmethod
    def logic_version(self) -> str:
        """
        The version of the calculation logic (e.g., 'v1.0.0').
        MUST be bumped if the underlying math or logic changes.
        """
        raise NotImplementedError

    @abstractmethod
    def evaluate(
        self,
        observation: Observation,
        context: MeasurementContext,
    ) -> list[Measurement]:
        raise NotImplementedError


class MeasurementNormalizer(ABC):

    @abstractmethod
    def supports(
        self,
        measurement: Measurement,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def normalize(
        self,
        measurement: Measurement,
    ) -> Measurement:
        raise NotImplementedError


class MeasurementValidator(ABC):

    @abstractmethod
    def validate(
        self,
        measurement: Measurement,
    ) -> ValidationResult:
        raise NotImplementedError


class ConfidenceEstimator(ABC):

    @abstractmethod
    def estimate(
        self,
        measurement: Measurement,
        context: MeasurementContext,
    ) -> Measurement:
        raise NotImplementedError


class QualityScorer(ABC):

    @abstractmethod
    def score(
        self,
        measurement: Measurement,
        validation: ValidationResult,
        context: MeasurementContext,
    ) -> Measurement:
        raise NotImplementedError


