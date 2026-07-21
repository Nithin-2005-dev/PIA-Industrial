import os

from app.adapters.github.adapter import GitHubAdapter
from app.adapters.github.rest_gateway import GitHubRestGateway

from app.extractor.expertise_extractor import (
    ExpertiseExtractor,
)
from app.extractor.policies.github_commit_strength_policy import (
    GitHubCommitStrengthPolicy,
)

from app.ports.event_query import EventQuery


def main():

    token = os.environ["GITHUB_TOKEN"]

    gateway = GitHubRestGateway(
        token=token,
    )

    adapter = GitHubAdapter(
        gateway=gateway,
    )

    extractor = ExpertiseExtractor(
        GitHubCommitStrengthPolicy(),
    )

    query = EventQuery(
        identifier="facebook/react",
        filters={
            "per_page": 1,
        },
    )

    events = adapter.collect(query)

    print("\n=== EVENTS ===\n")

    for event in events:
        print(event)

    print("\n=== EVIDENCE ===\n")

    for event in events:

        evidence_list = extractor.extract(
            event,
        )

        for evidence in evidence_list:
            print(evidence)


if __name__ == "__main__":
    main()