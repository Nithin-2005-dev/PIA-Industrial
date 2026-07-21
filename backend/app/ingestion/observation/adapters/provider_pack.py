from __future__ import annotations

from datetime import UTC
from datetime import datetime
from typing import Any

from app.ingestion.observation.ingestion.models import RawObservationRecord
from app.ingestion.observation.ingestion.models import SyncCursor
from app.ingestion.observation.ingestion.models import SyncRequest


class ProviderPayloadAdapter:
    name = "provider"
    provider = "provider"
    supported_record_types: tuple[str, ...] = ()

    def __init__(
        self,
        records: tuple[dict[str, Any], ...] = (),
    ):
        self._records = records

    def fetch(
        self,
        request: SyncRequest,
    ) -> tuple[tuple[RawObservationRecord, ...], SyncCursor]:
        offset = (
            request.cursor.offset
            if request.cursor is not None
            else 0
        )
        batch = self._records[
            offset : offset + request.batch_size
        ]
        raw_records = []
        for index, payload in enumerate(
            batch,
            start=offset,
        ):
            record = self.to_record(
                payload,
                request,
                index,
            )
            if request.since is not None and record.observed_at < request.since:
                continue
            if request.until is not None and record.observed_at > request.until:
                continue
            raw_records.append(record)

        next_offset = offset + len(batch)
        cursor = (
            raw_records[-1].cursor
            if raw_records
            else (
                request.cursor.cursor
                if request.cursor is not None
                else None
            )
        )
        return (
            tuple(raw_records),
            SyncCursor(
                adapter=self.name,
                cursor=cursor,
                offset=next_offset,
                updated_at=datetime.now(UTC),
            ),
        )

    def to_record(
        self,
        payload: dict[str, Any],
        request: SyncRequest,
        offset: int,
    ) -> RawObservationRecord:
        raise NotImplementedError

    def _record(
        self,
        *,
        request: SyncRequest,
        record_id: str,
        record_type: str,
        payload: dict[str, Any],
        observed_at,
        offset: int,
        signature: str | None = None,
    ) -> RawObservationRecord:
        return RawObservationRecord(
            source=request.source,
            record_id=str(record_id),
            record_type=record_type,
            payload=payload,
            observed_at=self._time(observed_at),
            signature=signature,
            cursor=str(record_id),
            offset=offset,
        )

    def _time(
        self,
        value,
    ) -> datetime:
        if value is None:
            return datetime.now(UTC)
        if isinstance(value, datetime):
            return (
                value
                if value.tzinfo is not None
                else value.replace(tzinfo=UTC)
            )
        return datetime.fromisoformat(
            str(value).replace(
                "Z",
                "+00:00",
            )
        )


class GitHubRestObservationAdapter(ProviderPayloadAdapter):
    name = "github_rest"
    provider = "github"
    supported_record_types = (
        "commit",
        "pull_request",
        "review",
        "comment",
        "merge",
        "release",
        "documentation",
    )

    def to_record(
        self,
        payload: dict[str, Any],
        request: SyncRequest,
        offset: int,
    ) -> RawObservationRecord:
        event = payload.get("event")
        if event == "pull_request":
            pull_request = payload.get("pull_request", payload)
            record_id = str(
                pull_request.get("id")
                or pull_request.get("number")
            )
            merged_at = pull_request.get("merged_at")
            record_type = (
                "merge"
                if merged_at
                else "pull_request"
            )
            return self._record(
                request=request,
                record_id=record_id,
                record_type=record_type,
                payload={
                    "author": self._login(pull_request.get("user")),
                    "title": pull_request.get("title", ""),
                    "state": pull_request.get("state", "unknown"),
                    "created_at": pull_request.get("created_at"),
                    "updated_at": pull_request.get("updated_at"),
                    "closed_at": pull_request.get("closed_at"),
                    "merged_at": merged_at,
                    "source_branch": self._ref(pull_request, "head"),
                    "target_branch": self._ref(pull_request, "base"),
                    "changed_files": pull_request.get("changed_files"),
                    "source_ref": self._ref(pull_request, "head") or "",
                    "target_ref": self._ref(pull_request, "base") or "",
                    "merged_by": self._login(pull_request.get("merged_by")),
                    "commit_id": self._sha(pull_request.get("merge_commit_sha")),
                },
                observed_at=(
                    merged_at
                    or pull_request.get("updated_at")
                    or pull_request.get("created_at")
                ),
                offset=offset,
            )

        if event == "pull_request_review":
            review = payload.get("review", payload)
            return self._record(
                request=request,
                record_id=str(review.get("id")),
                record_type="review",
                payload={
                    "reviewer": self._login(review.get("user")),
                    "subject_id": str(
                        payload.get("pull_request", {}).get("id", "")
                    ),
                    "state": str(review.get("state", "unknown")).lower(),
                    "submitted_at": review.get("submitted_at"),
                    "comment_count": review.get("comment_count", 0),
                },
                observed_at=review.get("submitted_at"),
                offset=offset,
            )

        if event == "issue_comment":
            comment = payload.get("comment", payload)
            return self._record(
                request=request,
                record_id=str(comment.get("id")),
                record_type="comment",
                payload={
                    "author": self._login(comment.get("user")),
                    "subject_id": str(payload.get("issue", {}).get("id", "")),
                    "body": comment.get("body", ""),
                    "created_at": comment.get("created_at"),
                    "updated_at": comment.get("updated_at"),
                },
                observed_at=comment.get("created_at"),
                offset=offset,
            )

        if event == "release":
            release = payload.get("release", payload)
            return self._record(
                request=request,
                record_id=str(release.get("id") or release.get("tag_name")),
                record_type="release",
                payload={
                    "author": self._login(release.get("author")),
                    "version": release.get("tag_name", ""),
                    "status": payload.get("action", "published"),
                    "released_at": release.get("published_at"),
                },
                observed_at=release.get("published_at"),
                offset=offset,
            )

        if event == "documentation":
            return self._record(
                request=request,
                record_id=str(payload.get("path")),
                record_type="documentation",
                payload={
                    "path": payload.get("path", ""),
                    "state": payload.get("state", "updated"),
                    "title": payload.get("title"),
                    "author": self._login(payload.get("author")),
                },
                observed_at=payload.get("observed_at"),
                offset=offset,
            )

        commit = payload.get("commit", payload)
        sha = payload.get("sha") or commit.get("sha")
        commit_body = commit.get("commit", commit)
        author = commit_body.get("author", {})
        committer = commit_body.get("committer", {})
        stats = commit.get("stats", payload.get("stats", {}))
        files = commit.get("files", payload.get("files", ()))
        return self._record(
            request=request,
            record_id=str(sha),
            record_type="commit",
            payload={
                "author": (
                    self._login(payload.get("author"))
                    or self._login(commit.get("author"))
                    or author.get("name")
                ),
                "author_name": author.get("name"),
                "author_email": author.get("email"),
                "message": commit_body.get("message", ""),
                "authored_at": author.get("date"),
                "committer_name": committer.get("name"),
                "committer_email": committer.get("email"),
                "committed_at": committer.get("date"),
                "parent_ids": tuple(
                    parent.get("sha")
                    for parent in commit.get("parents", ())
                    if parent.get("sha")
                ),
                "total_additions": stats.get("additions", 0),
                "total_deletions": stats.get("deletions", 0),
                "total_changes": stats.get("total", 0),
                "files": tuple(
                    {
                        "path": file.get("filename") or file.get("path"),
                        "status": file.get("status", "modified"),
                        "additions": file.get("additions", 0),
                        "deletions": file.get("deletions", 0),
                        "changes": file.get("changes", 0),
                    }
                    for file in files
                ),
                "targets": tuple(
                    file.get("filename") or file.get("path")
                    for file in files
                    if file.get("filename") or file.get("path")
                ),
            },
            observed_at=author.get("date") or committer.get("date"),
            offset=offset,
            signature=payload.get("signature"),
        )

    def _login(
        self,
        user,
    ) -> str | None:
        if isinstance(user, dict):
            return user.get("login") or user.get("name")
        return user

    def _ref(
        self,
        pull_request: dict[str, Any],
        key: str,
    ) -> str | None:
        value = pull_request.get(key)
        if isinstance(value, dict):
            return value.get("ref")
        return value

    def _sha(
        self,
        value,
    ) -> str | None:
        if value is None:
            return None
        return str(value)


class JiraObservationAdapter(ProviderPayloadAdapter):
    name = "jira"
    provider = "jira"
    supported_record_types = (
        "issue",
        "incident",
        "comment",
    )

    def to_record(
        self,
        payload: dict[str, Any],
        request: SyncRequest,
        offset: int,
    ) -> RawObservationRecord:
        fields = payload.get("fields", payload)
        issue_type = str(
            fields.get("issuetype", {}).get("name", "")
        ).lower()
        record_type = (
            "incident"
            if issue_type == "incident"
            else "issue"
        )
        status = fields.get("status", {})
        creator = fields.get("creator") or fields.get("reporter") or {}
        return self._record(
            request=request,
            record_id=str(payload.get("key") or payload.get("id")),
            record_type=record_type,
            payload={
                "author": creator.get("accountId") or creator.get("displayName"),
                "title": fields.get("summary", ""),
                "state": status.get("name", "unknown"),
                "severity": fields.get("priority", {}).get("name", "unknown"),
                "status": status.get("name", "unknown"),
                "created_at": fields.get("created"),
                "updated_at": fields.get("updated"),
                "closed_at": fields.get("resolutiondate"),
                "started_at": fields.get("created"),
                "resolved_at": fields.get("resolutiondate"),
                "service": fields.get("service"),
                "labels": tuple(fields.get("labels", ())),
            },
            observed_at=fields.get("updated") or fields.get("created"),
            offset=offset,
        )


class SlackObservationAdapter(ProviderPayloadAdapter):
    name = "slack"
    provider = "slack"
    supported_record_types = (
        "comment",
        "incident",
    )

    def to_record(
        self,
        payload: dict[str, Any],
        request: SyncRequest,
        offset: int,
    ) -> RawObservationRecord:
        record_type = payload.get("record_type", "comment")
        observed_at = payload.get("event_time") or self._slack_time(
            payload.get("ts")
        )
        return self._record(
            request=request,
            record_id=str(payload.get("client_msg_id") or payload.get("ts")),
            record_type=record_type,
            payload={
                "author": payload.get("user"),
                "subject_id": payload.get("thread_ts") or payload.get("channel", ""),
                "body": payload.get("text", ""),
                "created_at": observed_at,
                "updated_at": payload.get("edited", {}).get("ts"),
                "title": payload.get("title", payload.get("text", "")),
                "severity": payload.get("severity", "unknown"),
                "status": payload.get("status", "open"),
                "started_at": observed_at,
                "resolved_at": payload.get("resolved_at"),
                "service": payload.get("service"),
            },
            observed_at=observed_at,
            offset=offset,
        )

    def _slack_time(
        self,
        value,
    ) -> datetime:
        if value is None:
            return datetime.now(UTC)
        seconds = float(value)
        return datetime.fromtimestamp(
            seconds,
            tz=UTC,
        )


class GitHubActionsObservationAdapter(ProviderPayloadAdapter):
    name = "github_actions"
    provider = "github_actions"
    supported_record_types = (
        "build",
        "test",
        "deployment",
    )

    def to_record(
        self,
        payload: dict[str, Any],
        request: SyncRequest,
        offset: int,
    ) -> RawObservationRecord:
        record_type = payload.get("record_type", "build")
        record_id = str(
            payload.get("id")
            or payload.get("run_id")
            or payload.get("deployment_id")
        )
        started_at = (
            payload.get("started_at")
            or payload.get("run_started_at")
            or payload.get("created_at")
        )
        completed_at = payload.get("completed_at")
        return self._record(
            request=request,
            record_id=record_id,
            record_type=record_type,
            payload={
                "author": payload.get("actor"),
                "status": payload.get("conclusion") or payload.get("status", "unknown"),
                "started_at": started_at,
                "completed_at": completed_at,
                "duration_seconds": payload.get("duration_seconds"),
                "passed": payload.get("passed", 0),
                "failed": payload.get("failed", 0),
                "skipped": payload.get("skipped", 0),
                "environment": payload.get("environment", "unknown"),
                "deployed_at": payload.get("deployed_at") or completed_at or started_at,
                "version": payload.get("version"),
            },
            observed_at=completed_at or started_at,
            offset=offset,
        )


def default_observation_adapters(
) -> tuple[ProviderPayloadAdapter, ...]:
    return (
        GitHubRestObservationAdapter(),
        JiraObservationAdapter(),
        SlackObservationAdapter(),
        GitHubActionsObservationAdapter(),
    )
