from abc import ABC, abstractmethod

from app.infrastructure.ports.event_query import EventQuery


from typing import Iterator

class GitHubGateway(ABC):
    """
    Boundary between our system and GitHub.
    """

    @abstractmethod
    def fetch_commits(
        self,
        query: EventQuery,
    ) -> Iterator[dict]:
        raise NotImplementedError

    @abstractmethod
    def fetch_commit_details(
        self,
        owner: str,
        repo: str,
        sha: str,
    ) -> dict:
        raise NotImplementedError