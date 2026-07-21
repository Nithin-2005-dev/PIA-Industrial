from abc import ABC, abstractmethod
from typing import Iterator
import json
from pathlib import Path
from http.client import RemoteDisconnected
import requests
import time
import random
import logging

logger = logging.getLogger(__name__)

class GitHubDataSource(ABC):
    """
    Abstract boundary for retrieving repository data from GitHub endpoints.
    Can be implemented via live REST API or offline dataset snapshots.
    """
    @abstractmethod
    def get_repository(self, owner: str, repo: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_commits(self, owner: str, repo: str, params: dict = None) -> Iterator[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_pull_requests(self, owner: str, repo: str, params: dict = None) -> Iterator[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_issues(self, owner: str, repo: str, params: dict = None) -> Iterator[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_contributors(self, owner: str, repo: str, params: dict = None) -> Iterator[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_branches(self, owner: str, repo: str, params: dict = None) -> Iterator[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_commit_details(self, owner: str, repo: str, sha: str) -> dict:
        raise NotImplementedError

class LiveGitHubSource(GitHubDataSource):
    """
    Live implementation communicating with the GitHub REST API.
    """
    BASE_URL = "https://api.github.com"

    def __init__(self, secret_provider, secret_key: str = "GITHUB_TOKEN"):
        from app.ingestion.observation.ingestion.circuit_breaker import CircuitBreaker
        self.secret_provider = secret_provider
        self.secret_key = secret_key
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout_sec=60.0)

    def _get_headers(self) -> dict:
        token = self.secret_provider.get_secret(self.secret_key)
        headers = {
            "Accept": "application/vnd.github+json",
        }
        if token and token != "dummy":
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _handle_rate_limit(self, response: requests.Response):
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        
        if remaining is not None and int(remaining) == 0 and reset is not None:
            reset_time = int(reset)
            current_time = int(time.time())
            sleep_time = max(0, reset_time - current_time)
            if sleep_time > 0:
                logger.warning(f"GitHub Rate Limit Exceeded. Blocking execution for {sleep_time} seconds until reset.")
                time.sleep(sleep_time)

    def _make_request(self, url: str, params: dict = None) -> dict:
        max_retries = 3
        for attempt in range(max_retries + 1):
            def fetch():
                response = requests.get(
                    url,
                    headers=self._get_headers(),
                    params=params or {},
                    timeout=(10, 30),
                )
                self._handle_rate_limit(response)
                response.raise_for_status()
                return response.json()

            try:
                return self.circuit_breaker.call(fetch)
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                RemoteDisconnected,
            ) as e:
                if attempt >= max_retries:
                    logger.error(f"GitHub request failed after {max_retries} retries: {e}")
                    raise
                delay = min(2 ** attempt, 5) + random.uniform(0, 0.5)
                logger.warning(
                    f"Transient network error (attempt {attempt + 1}/{max_retries}): {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)

    def _paginate(self, url: str, params: dict = None) -> Iterator[dict]:
        params = params or {}
        limit = params.pop("limit", None) or params.pop("per_page", None)
        params["per_page"] = min(limit, 100) if limit else 100
        page = 1
        
        yielded_count = 0
        while True:
            params["page"] = page
            page_data = self._make_request(url, params=params)
            
            if not page_data:
                break
                
            for item in page_data:
                yield item
                yielded_count += 1
                if limit and yielded_count >= limit:
                    return
                
            if len(page_data) < params["per_page"]:
                break
            page += 1

    def get_repository(self, owner: str, repo: str) -> dict:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        return self._make_request(url)

    def get_commits(self, owner: str, repo: str, params: dict = None) -> Iterator[dict]:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits"
        return self._paginate(url, params)

    def get_pull_requests(self, owner: str, repo: str, params: dict = None) -> Iterator[dict]:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls"
        return self._paginate(url, params)

    def get_issues(self, owner: str, repo: str, params: dict = None) -> Iterator[dict]:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/issues"
        return self._paginate(url, params)

    def get_contributors(self, owner: str, repo: str, params: dict = None) -> Iterator[dict]:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contributors"
        return self._paginate(url, params)

    def get_branches(self, owner: str, repo: str, params: dict = None) -> Iterator[dict]:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/branches"
        return self._paginate(url, params)

    def get_commit_details(self, owner: str, repo: str, sha: str) -> dict:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits/{sha}"
        return self._make_request(url)


class OfflineSnapshotSource(GitHubDataSource):
    """
    Offline implementation that reads pre-captured raw JSON datasets from disk.
    """
    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path) / "raw"
        if not self.dataset_path.exists():
            raise ValueError(f"Dataset path does not exist: {self.dataset_path}")

    def _read_json(self, filename: str):
        filepath = self.dataset_path / filename
        if not filepath.exists():
            return []
        with open(filepath, "r") as f:
            return json.load(f)

    def get_repository(self, owner: str, repo: str) -> dict:
        data = self._read_json("repository.json")
        return data if isinstance(data, dict) else (data[0] if data else {})

    def get_commits(self, owner: str, repo: str, params: dict = None) -> Iterator[dict]:
        data = self._read_json("commits.json")
        for item in data:
            yield item

    def get_pull_requests(self, owner: str, repo: str, params: dict = None) -> Iterator[dict]:
        data = self._read_json("pull_requests.json")
        for item in data:
            yield item

    def get_issues(self, owner: str, repo: str, params: dict = None) -> Iterator[dict]:
        data = self._read_json("issues.json")
        for item in data:
            yield item

    def get_contributors(self, owner: str, repo: str, params: dict = None) -> Iterator[dict]:
        data = self._read_json("contributors.json")
        for item in data:
            yield item

    def get_branches(self, owner: str, repo: str, params: dict = None) -> Iterator[dict]:
        data = self._read_json("branches.json")
        for item in data:
            yield item

    def get_commit_details(self, owner: str, repo: str, sha: str) -> dict:
        # Check if there is a specific commit detail file or look in a commits list
        file_path = self.dataset_path / f"commit_{sha}.json"
        if file_path.exists():
            return self._read_json(file_path.name)
        # Fallback to search in commits.json (note: commits.json doesn't have deep details usually)
        for commit in self._read_json("commits.json"):
            if commit.get("sha") == sha:
                return commit
        return {}
