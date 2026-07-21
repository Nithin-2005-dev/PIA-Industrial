from math import log2

from app.ingestion.observation.domain import CommitFacts
from app.ingestion.observation.domain import FileChangeFacts
from app.ingestion.observation.domain import Observation


def commit_facts(
    observation: Observation,
) -> CommitFacts | None:
    if isinstance(
        observation.facts,
        CommitFacts,
    ):
        return observation.facts
    return None


def artifact_files(
    observation: Observation,
) -> tuple[FileChangeFacts, ...]:
    facts = commit_facts(
        observation
    )
    if facts is None:
        return ()
    return facts.files


def total_changes(
    observation: Observation,
) -> float:
    facts = commit_facts(
        observation
    )
    return float(
        facts.total_changes if facts else 0
    )


def additions(
    observation: Observation,
) -> float:
    facts = commit_facts(
        observation
    )
    return float(
        facts.total_additions if facts else 0
    )


def deletions(
    observation: Observation,
) -> float:
    facts = commit_facts(
        observation
    )
    return float(
        facts.total_deletions if facts else 0
    )


def files_changed(
    observation: Observation,
) -> float:
    return float(
        len(
            artifact_files(
                observation
            )
        )
    )


def entropy(
    values: list[float],
) -> float:
    total = sum(
        value
        for value in values
        if value > 0
    )

    if total <= 0:
        return 0.0

    result = 0.0

    for value in values:
        if value <= 0:
            continue

        probability = value / total
        result -= probability * log2(
            probability
        )

    return result
