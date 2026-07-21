import json
from pathlib import Path

from app.adapters.github.rest_gateway import GitHubRestGateway
from app.ports.event_query import EventQuery


TOKEN = ""  # or load from env
REPOSITORY = "facebook/react"


def main():

    gateway = GitHubRestGateway(TOKEN)

    query = EventQuery(
        identifier=REPOSITORY,
        filters={
            "per_page": 1,
        },
    )

    commits = gateway.fetch_commits(query)

    output_dir = Path("outputs/github_raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "raw_commit_list.json", "w", encoding="utf-8") as f:
        json.dump(commits, f, indent=4)

    sha = commits[0]["sha"]

    owner, repo = REPOSITORY.split("/")

    details = gateway.fetch_commit_details(
        owner=owner,
        repo=repo,
        sha=sha,
    )

    with open(output_dir / "raw_commit_details.json", "w", encoding="utf-8") as f:
        json.dump(details, f, indent=4)

    print("=" * 60)
    print("GitHub raw responses captured successfully.")
    print(f"Commit SHA : {sha}")
    print(f"Saved      : {output_dir / 'raw_commit_list.json'}")
    print(f"Saved      : {output_dir / 'raw_commit_details.json'}")
    print("=" * 60)


if __name__ == "__main__":
    main()