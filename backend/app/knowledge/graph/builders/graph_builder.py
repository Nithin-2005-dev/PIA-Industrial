from abc import ABC, abstractmethod

from app.knowledge.graph.organizational_graph import (
    OrganizationalGraph,
)


class GraphBuilder(ABC):

    @abstractmethod
    def build(
        self,
        *args,
        **kwargs,
    ) -> OrganizationalGraph:
        pass