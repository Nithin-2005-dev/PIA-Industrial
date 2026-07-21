"""Stage 02 - collect GitHub commits as canonical observations."""

from __future__ import annotations

import time
from collections import Counter
from dataclasses import dataclass
from typing import Mapping

from app.platform.core_modules import GitHubAdapterFactory

from ..context import PlatformContext
from ..ui import metric, ranking, section, success
from .base import PipelineStage


@dataclass(frozen=True)
class GitHubCollectionQuery:
    identifier: str
    filters: Mapping[str, object]


class CollectionStage(PipelineStage):
    name = "GitHub to Observation"

    def execute(self, context: PlatformContext) -> None:
        started = time.perf_counter()
        token = context.github_token
        if token is None:
            raise RuntimeError(
                "GITHUB_TOKEN or GH_TOKEN is required for the real GitHub pipeline."
            )

        adapter = context.resolve(GitHubAdapterFactory).create(token)
        query = GitHubCollectionQuery(
            identifier=context.repository,
            filters={
                "per_page": context.commit_limit,
                "sha": context.branch,
                "since_sha": context.since_commit,
            },
        )

        observations = list(adapter.collect(query))
        context.observations = observations
        context.metrics["observations"] = len(observations)
        context.metrics["collection_seconds"] = time.perf_counter() - started

        section("Collection Result")
        metric("Repository", context.repository)
        metric("Branch", context.branch)
        metric("Observations", len(observations))
        metric("Collection Time", f"{context.metrics['collection_seconds']:.3f}s")
        success("GitHub commits translated into canonical observations")

        self._repository_overview(observations)
        self._author_statistics(observations)
        self._file_statistics(observations)
        self._timeline(observations)

    def _repository_overview(self, observations) -> None:
        section("Repository Overview")
        files = set()
        additions = 0
        deletions = 0
        changes = 0

        for observation in observations:
            facts = observation.facts
            additions += getattr(facts, "total_additions", 0)
            deletions += getattr(facts, "total_deletions", 0)
            changes += getattr(facts, "total_changes", 0)
            for file in getattr(facts, "files", ()):
                files.add(file.path)

        metric("Commits", len(observations))
        metric("Unique Files", len(files))
        metric("Lines Added", additions)
        metric("Lines Deleted", deletions)
        metric("Total Line Changes", changes)

    def _author_statistics(self, observations) -> None:
        counter = Counter()
        for observation in observations:
            for actor in observation.actors:
                counter[actor.id] += 1

        ranking(
            "Top Contributors",
            [
                f"{author:<25} {count:>4} commits"
                for author, count in counter.most_common(10)
            ],
        )

    def _file_statistics(self, observations) -> None:
        files = Counter()
        directories = Counter()
        extensions = Counter()
        statuses = Counter()

        for observation in observations:
            for file in getattr(observation.facts, "files", ()):
                files[file.path] += 1
                statuses[file.status] += 1
                directory = "/".join(file.path.split("/")[:-1]) or "."
                directories[directory] += 1
                if "." in file.path:
                    extensions[file.path.rsplit(".", 1)[-1]] += 1

        ranking(
            "Most Changed Files",
            [f"{path} ({count})" for path, count in files.most_common(10)],
        )
        ranking(
            "Most Active Directories",
            [f"{path} ({count})" for path, count in directories.most_common(10)],
        )
        ranking(
            "Top File Extensions",
            [f".{ext} ({count})" for ext, count in extensions.most_common(10)],
        )
        ranking(
            "File Status Distribution",
            [f"{status:<12} {count}" for status, count in statuses.most_common()],
        )

    def _timeline(self, observations) -> None:
        months = Counter()
        weekdays = Counter()
        hours = Counter()
        for observation in observations:
            ts = observation.timestamp
            months[ts.strftime("%Y-%m")] += 1
            weekdays[ts.strftime("%A")] += 1
            hours[ts.hour] += 1

        ranking(
            "Monthly Activity",
            [f"{month} ({count})" for month, count in sorted(months.items())],
        )
        ranking(
            "Weekday Activity",
            [f"{day:<10} {count}" for day, count in weekdays.items()],
        )
        ranking(
            "Most Active Hours",
            [f"{hour:02d}:00 ({count})" for hour, count in sorted(hours.items())],
        )
