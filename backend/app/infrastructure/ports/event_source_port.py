from abc import ABC, abstractmethod

from app.ingestion.observation.domain import Observation

from .event_query import EventQuery


class ObservationSourcePort(ABC):
    """
    Contract for external observation sources.

    Implementations translate external systems into canonical immutable
    Observations. Vendor payloads must not leak through this port.
    """

    @abstractmethod
    def collect(
        self,
        query: EventQuery,
    ) -> list[Observation]:
        """
        Collect observations satisfying the given query.

        Returns:
            A list of canonical immutable Observations.
        """
        raise NotImplementedError


class EventSourcePort(ObservationSourcePort):
    """
    Deprecated compatibility alias.

    New adapters should implement ObservationSourcePort and return
    `app.ingestion.observation.domain.Observation`.
    """
