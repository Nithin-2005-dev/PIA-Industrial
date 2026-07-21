from datetime import datetime

from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.ingestion.observation.domain import CommitFacts
from app.ingestion.observation.domain import FileChangeFacts
from app.ingestion.observation.domain import Observation
from app.ingestion.observation.domain import ObservationCategory
from app.ingestion.observation.domain import ObservationContext
from app.ingestion.observation.domain import ObservationLifecycle
from app.ingestion.observation.domain import ObservationProvenance
from app.ingestion.observation.domain import ObservationType
from app.ingestion.observation.integration.event_compat import stable_observation_id


class GitHubObservationTranslator:

    adapter_name = "github_rest"
    platform = "github"

    def commit(
        self,
        raw_commit: dict,
        details: dict,
        repository: str | None = None,
        tenant_id: str | None = None,
    ) -> Observation:
        sha = raw_commit[
            "sha"
        ]
        authored_at = self._parse_time(
            raw_commit.get(
                "commit",
                {},
            ).get(
                "author",
                {},
            ).get(
                "date",
            )
        )

        author = raw_commit.get(
            "author"
        ) or {}
        author_login = author.get(
            "login"
        ) or "unknown"

        files = tuple(
            FileChangeFacts(
                path=str(
                    file.get(
                        "filename",
                        "",
                    )
                ),
                previous_path=file.get(
                    "previous_filename"
                ),
                status=str(
                    file.get(
                        "status",
                        "modified",
                    )
                ),
                additions=int(
                    file.get(
                        "additions",
                        0,
                    )
                    or 0
                ),
                deletions=int(
                    file.get(
                        "deletions",
                        0,
                    )
                    or 0
                ),
                changes=int(
                    file.get(
                        "changes",
                        0,
                    )
                    or 0
                ),
                patch=file.get(
                    "patch"
                ),
            )
            for file in details.get(
                "files",
                (),
            )
        )

        stats = details.get(
            "stats",
            {},
        )

        targets = tuple(
            EntityRef(
                id=file.path,
                type=EntityType.FILE,
            )
            for file in files
        )

        return Observation(
            observation_id=stable_observation_id(
                self.platform,
                "commit",
                sha,
            ),
            trace_id=stable_observation_id(
                self.platform,
                "trace",
                sha,
            ),
            correlation_id=sha,
            timestamp=authored_at,
            observation_type=ObservationType.COMMIT,
            observation_category=ObservationCategory.SOURCE_CONTROL,
            source_platform=self.platform,
            source_adapter=self.adapter_name,
            version="1.0",
            lifecycle=ObservationLifecycle.PRODUCTION,
            actors=(
                EntityRef(
                    id=author_login,
                    type=EntityType.DEVELOPER,
                ),
            ),
            targets=targets,
            provenance=ObservationProvenance(
                source_platform=self.platform,
                source_adapter=self.adapter_name,
                source_record_id=sha,
            ),
            context=ObservationContext(
                repository=repository,
                tenant_id=tenant_id,
            ),
            facts=CommitFacts(
                commit_id=sha,
                message=str(
                    raw_commit.get(
                        "commit",
                        {},
                    ).get(
                        "message",
                        "",
                    )
                ),
                author_name=(
                    raw_commit.get(
                        "commit",
                        {},
                    ).get(
                        "author",
                        {},
                    ).get(
                        "name"
                    )
                ),
                author_email=(
                    raw_commit.get(
                        "commit",
                        {},
                    ).get(
                        "author",
                        {},
                    ).get(
                        "email"
                    )
                ),
                authored_at=authored_at,
                committer_name=(
                    raw_commit.get(
                        "commit",
                        {},
                    ).get(
                        "committer",
                        {},
                    ).get(
                        "name"
                    )
                ),
                committer_email=(
                    raw_commit.get(
                        "commit",
                        {},
                    ).get(
                        "committer",
                        {},
                    ).get(
                        "email"
                    )
                ),
                committed_at=self._parse_time(
                    raw_commit.get(
                        "commit",
                        {},
                    ).get(
                        "committer",
                        {},
                    ).get(
                        "date",
                    )
                ),
                parent_ids=tuple(
                    str(
                        parent.get(
                            "sha",
                            "",
                        )
                    )
                    for parent in raw_commit.get(
                        "parents",
                        (),
                    )
                    if parent.get(
                        "sha"
                    )
                ),
                total_additions=int(
                    stats.get(
                        "additions",
                        0,
                    )
                    or 0
                ),
                total_deletions=int(
                    stats.get(
                        "deletions",
                        0,
                    )
                    or 0
                ),
                total_changes=int(
                    stats.get(
                        "total",
                        0,
                    )
                    or 0
                ),
                files=files,
                signature_verified=(
                    details.get(
                        "commit",
                        {},
                    ).get(
                        "verification",
                        {},
                    ).get(
                        "verified"
                    )
                ),
            ),
        )

    def _parse_time(
        self,
        value: str | None,
    ) -> datetime:
        if not value:
            raise ValueError(
                "timestamp is required"
            )
        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )

