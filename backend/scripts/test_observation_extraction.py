import json
import os
from dataclasses import asdict
from pathlib import Path
import sys

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    ),
)

from app.adapters.github.adapter import GitHubAdapter
from app.adapters.github.rest_gateway import GitHubRestGateway
from app.ports.event_query import EventQuery


def main():
    token = os.environ[
        "GITHUB_TOKEN"
    ]

    gateway = GitHubRestGateway(
        token
    )
    adapter = GitHubAdapter(
        gateway
    )

    query = EventQuery(
        identifier="facebook/react",
        filters={
            "per_page": 1,
        },
    )

    observation = adapter.collect(
        query
    )[0]

    output_dir = Path(
        "scripts/outputs"
    )
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_dir / "observation.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            asdict(
                observation
            ),
            f,
            indent=4,
            default=str,
        )

    print(
        "=" * 80
    )
    print(
        "M36 CANONICAL OBSERVATION EXTRACTION TEST"
    )
    print(
        "=" * 80
    )

    print(
        f"Observation ID : {observation.observation_id}"
    )
    print(
        f"Type           : {observation.observation_type.value}"
    )
    print(
        f"Category       : {observation.observation_category.value}"
    )
    print(
        f"Commit ID      : {observation.facts.commit_id}"
    )
    print(
        f"Files          : {len(observation.facts.files)}"
    )
    print()
    print(
        "Observation saved to:"
    )
    print(
        output_dir / "observation.json"
    )
    print(
        "=" * 80
    )


if __name__ == "__main__":
    main()
