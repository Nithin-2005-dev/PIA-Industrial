from typing import Iterator
from app.infrastructure.github.source import GitHubDataSource
from app.ingestion.observation.adapters.github import GitHubObservationTranslator
from app.ingestion.observation.domain import Observation
from app.ingestion.observation.integration import observation_to_event
from app.infrastructure.ports.event_query import EventQuery
from app.infrastructure.ports.event_source_port import ObservationSourcePort
from app.ingestion.observation.ingestion.resilience import with_resilience


class GitHubAdapter(ObservationSourcePort):
    """
    GitHub source adapter.

    The adapter authenticates and fetches through the source, then delegates
    translation to the observation layer. It does not calculate measurements,
    evidence, risk, confidence, or business meaning.
    """

    def __init__(
        self,
        source: GitHubDataSource,
        translator: GitHubObservationTranslator | None = None,
    ):
        self._source = source
        self._translator = translator or GitHubObservationTranslator()

    def is_circuit_open(self) -> bool:
        """Check if the underlying source's circuit breaker is open."""
        if hasattr(self._source, "circuit_breaker"):
            return self._source.circuit_breaker.is_open()
        return False

    @with_resilience(max_retries=3, base_delay=1.0)
    def collect(
        self,
        query: EventQuery,
    ) -> Iterator[Observation]:
        owner, repo = query.identifier.split("/")
        raw_commits_generator = self._source.get_commits(
            owner=owner, repo=repo, params=dict(query.filters) if query.filters else None
        )

        for raw_commit in raw_commits_generator:
            sha = raw_commit[
                "sha"
            ]

            details = self._source.get_commit_details(
                owner=owner,
                repo=repo,
                sha=sha,
            )

            yield self._translator.commit(
                raw_commit,
                details,
                repository=query.identifier,
            )

    def collect_events(
        self,
        query: EventQuery,
    ):
        """
        Deprecated compatibility bridge for legacy scripts.
        """
        return [
            observation_to_event(
                observation
            )
            for observation in self.collect(
                query
            )
        ]
