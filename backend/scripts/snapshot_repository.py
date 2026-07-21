import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
import hashlib

from app.adapters.github.source import LiveGitHubSource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockSecretProvider:
    def __init__(self, token: str):
        self.token = token
    def get_secret(self, key: str) -> str:
        return self.token

def calculate_checksum(data) -> str:
    serialized = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(serialized).hexdigest()

def save_json(data, path: Path) -> str:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return calculate_checksum(data)

def main():
    parser = argparse.ArgumentParser(description="Snapshot a GitHub repository for benchmarking.")
    parser.add_argument("--repo", type=str, required=True, help="Format: owner/repo")
    parser.add_argument("--token", type=str, required=True, help="GitHub PAT token")
    parser.add_argument("--version", type=str, default="v1", help="Dataset version (default: v1)")
    parser.add_argument("--commits", type=int, default=100, help="Number of commits to pull")
    args = parser.parse_args()

    owner, repo = args.repo.split("/")
    
    provider = MockSecretProvider(args.token)
    source = LiveGitHubSource(provider)
    
    # Setup directories
    repo_slug = args.repo.replace("/", "_")
    base_dir = Path(f"evaluation/datasets/{args.version}/{repo_slug}")
    raw_dir = base_dir / "raw"
    normalized_dir = base_dir / "normalized"
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    normalized_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Snapshotting {args.repo} into {base_dir}")
    
    checksums = {}
    
    # 1. Repository
    logger.info("Fetching repository info...")
    repo_data = source.get_repository(owner, repo)
    checksums["repository.json"] = save_json(repo_data, raw_dir / "repository.json")
    
    default_branch = repo_data.get("default_branch", "main")
    
    # 2. Commits
    logger.info(f"Fetching {args.commits} commits...")
    commits = list(source.get_commits(owner, repo, {"limit": args.commits}))
    checksums["commits.json"] = save_json(commits, raw_dir / "commits.json")
    
    snapshot_commit = commits[0]["sha"] if commits else ""
    
    # Fetch commit details (raw)
    for c in commits:
        sha = c["sha"]
        details = source.get_commit_details(owner, repo, sha)
        save_json(details, raw_dir / f"commit_{sha}.json")
    
    # 3. PRs, Issues, Contributors, Branches (Limited subsets for benchmarks)
    logger.info("Fetching Pull Requests...")
    prs = list(source.get_pull_requests(owner, repo, {"limit": 50}))
    checksums["pull_requests.json"] = save_json(prs, raw_dir / "pull_requests.json")
    
    logger.info("Fetching Issues...")
    issues = list(source.get_issues(owner, repo, {"limit": 50}))
    checksums["issues.json"] = save_json(issues, raw_dir / "issues.json")
    
    logger.info("Fetching Contributors...")
    contributors = list(source.get_contributors(owner, repo, {"limit": 100}))
    checksums["contributors.json"] = save_json(contributors, raw_dir / "contributors.json")
    
    logger.info("Fetching Branches...")
    branches = list(source.get_branches(owner, repo, {"limit": 20}))
    checksums["branches.json"] = save_json(branches, raw_dir / "branches.json")
    
    # Manifest
    manifest = {
        "dataset_version": args.version,
        "repository": args.repo,
        "default_branch": default_branch,
        "snapshot_commit": snapshot_commit,
        "generator_version": "1.0",
        "schema_version": "1.0",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "checksums": checksums,
        "stats": {
            "commits": len(commits),
            "pull_requests": len(prs),
            "issues": len(issues),
            "contributors": len(contributors)
        }
    }
    
    save_json(manifest, base_dir / "manifest.json")
    logger.info(f"Snapshot complete. Wrote manifest to {base_dir / 'manifest.json'}")

if __name__ == "__main__":
    main()
