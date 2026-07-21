from abc import ABC, abstractmethod

from app.domain.event import Event
from app.domain.evidence import Evidence


class EvidenceExtractor(ABC):

    @abstractmethod
    def extract(
        self,
        event: Event,
    ) -> list[Evidence]:
        raise NotImplementedError