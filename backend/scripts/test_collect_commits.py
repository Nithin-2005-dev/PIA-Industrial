import os

from app.adapters.github.adapter import GitHubAdapter
from app.adapters.github.rest_gateway import GitHubRestGateway

from app.ports.event_query import EventQuery


def main():

    token = os.environ["GITHUB_TOKEN"]

    gateway = GitHubRestGateway(
        token=token,
    )

    adapter = GitHubAdapter(
        gateway=gateway,
    )

    query = EventQuery(
        identifier="facebook/react",
        filters={
            "per_page": 5,
        },
    )

    events = adapter.collect(query)

    print(f"Collected {len(events)} events")

    print()

    for event in events:
        print(event)
        print("-" * 80)


if __name__ == "__main__":
    main()