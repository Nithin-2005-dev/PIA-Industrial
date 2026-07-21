import requests
from typing import Iterator

from app.infrastructure.ports.event_query import EventQuery

from app.infrastructure.github.gateway import GitHubGateway


class GitHubRestGateway(GitHubGateway):

    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        secret_provider,
        secret_key: str = "GITHUB_TOKEN"
    ):
        from app.ingestion.observation.ingestion.circuit_breaker import CircuitBreaker
        self.secret_provider = secret_provider
        self.secret_key = secret_key
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout_sec=60.0)

    def _get_headers(self) -> dict:
        token = self.secret_provider.get_secret(self.secret_key)
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }

    def _handle_rate_limit(self, response: requests.Response):
        import time
        import logging
        logger = logging.getLogger(__name__)
        
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
        import time
        import random
        import logging
        from http.client import RemoteDisconnected
        _logger = logging.getLogger(__name__)

        max_retries = 3
        for attempt in range(max_retries + 1):
            def fetch():
                response = requests.get(
                    url,
                    headers=self._get_headers(),
                    params=params or {},
                    timeout=(10, 30),  # (connect_timeout, read_timeout)
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
                    _logger.error(f"GitHub request failed after {max_retries} retries: {e}")
                    raise
                delay = min(2 ** attempt, 5) + random.uniform(0, 0.5)
                _logger.warning(
                    f"Transient network error (attempt {attempt + 1}/{max_retries}): {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)


    def fetch_commits(
        self,
        query: EventQuery,
    ) -> Iterator[dict]:

        owner, repo = query.identifier.split("/")

        url = (
            f"{self.BASE_URL}"
            f"/repos/{owner}/{repo}/commits"
        )

        params = dict(query.filters) if query.filters else {}
        
        # Support either 'limit' or 'per_page' to bound the total fetch
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

    def fetch_commit_details(
        self,
        owner: str,
        repo: str,
        sha: str,
    ) -> dict:

        url = (
            f"{self.BASE_URL}"
            f"/repos/{owner}/{repo}/commits/{sha}"
        )

        return self._make_request(url)