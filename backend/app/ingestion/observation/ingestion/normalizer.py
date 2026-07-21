from __future__ import annotations

from datetime import datetime, timezone
import logging
from uuid import NAMESPACE_URL
from uuid import uuid5
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, ValidationError, Field

logger = logging.getLogger(__name__)

from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.ingestion.observation.domain import BuildFacts
from app.ingestion.observation.domain import CommentFacts
from app.ingestion.observation.domain import CommitFacts
from app.ingestion.observation.domain import DeploymentFacts
from app.ingestion.observation.domain import DocumentationFacts
from app.ingestion.observation.domain import FileChangeFacts
from app.ingestion.observation.domain import IncidentFacts
from app.ingestion.observation.domain import IssueFacts
from app.ingestion.observation.domain import MergeFacts
from app.ingestion.observation.domain import Observation
from app.ingestion.observation.domain import ObservationCategory
from app.ingestion.observation.domain import ObservationContext
from app.ingestion.observation.domain import ObservationLifecycle
from app.ingestion.observation.domain import ObservationProvenance
from app.ingestion.observation.domain import ObservationType
from app.ingestion.observation.domain import PullRequestFacts
from app.ingestion.observation.domain import ReleaseFacts
from app.ingestion.observation.domain import ReviewFacts
from app.ingestion.observation.domain import TestFacts
from app.ingestion.observation.domain import ProcessingMode
from app.ingestion.observation.ingestion.identity import UnifiedIdentityResolver
from app.ingestion.observation.ingestion.models import RawObservationRecord


class SchemaMismatchError(Exception):
    """Raised when an incoming raw payload fails Pydantic schema validation."""
    pass

class BaseEventSchema(BaseModel):
    """Semantic contract for incoming raw events."""
    author: Optional[str] = Field(None, alias="user")
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None
    status: Optional[str] = None
    state: Optional[str] = None
    message: Optional[str] = None
    
    class Config:
        extra = "allow"
        populate_by_name = True


class ObservationNormalizer:
    def __init__(
        self,
        identity_resolver: UnifiedIdentityResolver | None = None,
    ):
        self._identity_resolver = identity_resolver or UnifiedIdentityResolver()

    def normalize(
        self,
        record: RawObservationRecord,
    ) -> Observation:
        try:
            # Validate schema contract
            validated = BaseEventSchema(**record.payload)
        except ValidationError as e:
            raise SchemaMismatchError(f"Validation failed: {e}") from e

        payload = record.payload
        observation_type = ObservationType(record.record_type)
        facts = self._facts_for(
            observation_type,
            record,
        )
        author = (
            payload.get("author")
            or payload.get("user")
            or payload.get("merged_by")
            or payload.get("reviewer")
        )
        identity = self._identity_resolver.resolve(
            record.source.provider,
            author,
        )
        actors = (
            (
                EntityRef(
                    id=identity.developer_id,
                    type=EntityType.DEVELOPER,
                ),
            )
            if identity is not None
            else ()
        )

        return Observation(
            observation_id=self._stable_id(
                record.source.provider,
                record.record_type,
                record.record_id,
            ),
            trace_id=self._stable_id(
                record.source.provider,
                "trace",
                record.record_id,
            ),
            correlation_id=str(
                payload.get(
                    "correlation_id",
                    record.record_id,
                )
            ),
            timestamp=record.observed_at,
            observation_type=observation_type,
            observation_category=self._category_for(observation_type),
            source_platform=record.source.provider,
            source_adapter=record.source.adapter,
            version="1.0",
            lifecycle=ObservationLifecycle.PRODUCTION,
            actors=actors,
            targets=self._targets_for(payload),
            provenance=ObservationProvenance(
                source_platform=record.source.provider,
                source_adapter=record.source.adapter,
                source_record_id=record.record_id,
                fetched_at=record.observed_at,
                replay_ref=record.cursor,
            ),
            context=ObservationContext(
                repository=record.source.repository,
                organization=record.source.organization,
                tenant_id=record.source.tenant_id,
                branch=payload.get("branch"),
                labels=tuple(payload.get("labels", ())),
                metadata={
                    "offset": record.offset,
                    "signature": record.signature,
                },
            ),
            facts=facts,
            processing_mode=ProcessingMode.LIVE,
        )

    def _facts_for(
        self,
        observation_type: ObservationType,
        record: RawObservationRecord,
    ):
        payload = record.payload
        if observation_type == ObservationType.COMMIT:
            files = tuple(
                FileChangeFacts(
                    path=file.get("path") or file.get("filename") or "",
                    status=file.get("status", "modified"),
                    additions=int(file.get("additions", 0) or 0),
                    deletions=int(file.get("deletions", 0) or 0),
                    changes=int(file.get("changes", 0) or 0),
                    previous_path=file.get("previous_path"),
                    patch=file.get("patch"),
                )
                for file in payload.get("files", ())
            )
            return CommitFacts(
                commit_id=record.record_id,
                message=payload.get("message", ""),
                author_name=payload.get("author_name") or payload.get("author"),
                author_email=payload.get("author_email"),
                authored_at=self._time(payload.get("authored_at"), record.observed_at),
                committer_name=payload.get("committer_name"),
                committer_email=payload.get("committer_email"),
                committed_at=self._time(payload.get("committed_at"), record.observed_at),
                parent_ids=tuple(payload.get("parent_ids", ())),
                total_additions=int(payload.get("total_additions", 0) or 0),
                total_deletions=int(payload.get("total_deletions", 0) or 0),
                total_changes=int(payload.get("total_changes", 0) or 0),
                files=files,
                signature_verified=payload.get("signature_verified"),
            )
        if observation_type == ObservationType.PULL_REQUEST:
            return PullRequestFacts(
                pull_request_id=record.record_id,
                title=payload.get("title", ""),
                state=payload.get("state", "unknown"),
                author=payload.get("author"),
                created_at=self._time(payload.get("created_at"), record.observed_at),
                updated_at=self._time(payload.get("updated_at"), None),
                closed_at=self._time(payload.get("closed_at"), None),
                merged_at=self._time(payload.get("merged_at"), None),
                source_branch=payload.get("source_branch"),
                target_branch=payload.get("target_branch"),
                commit_ids=tuple(payload.get("commit_ids", ())),
                changed_files=payload.get("changed_files"),
            )
        if observation_type == ObservationType.REVIEW:
            return ReviewFacts(
                review_id=record.record_id,
                subject_id=payload.get("subject_id", ""),
                reviewer=payload.get("reviewer"),
                state=payload.get("state", "unknown"),
                submitted_at=self._time(payload.get("submitted_at"), record.observed_at),
                comment_count=int(payload.get("comment_count", 0) or 0),
            )
        if observation_type == ObservationType.COMMENT:
            return CommentFacts(
                comment_id=record.record_id,
                subject_id=payload.get("subject_id", ""),
                author=payload.get("author"),
                body=payload.get("body", ""),
                created_at=self._time(payload.get("created_at"), record.observed_at),
                updated_at=self._time(payload.get("updated_at"), None),
            )
        if observation_type == ObservationType.ISSUE:
            return IssueFacts(
                issue_id=record.record_id,
                title=payload.get("title", ""),
                state=payload.get("state", "unknown"),
                author=payload.get("author"),
                created_at=self._time(payload.get("created_at"), record.observed_at),
                updated_at=self._time(payload.get("updated_at"), None),
                closed_at=self._time(payload.get("closed_at"), None),
                labels=tuple(payload.get("labels", ())),
            )
        if observation_type == ObservationType.MERGE:
            return MergeFacts(
                merge_id=record.record_id,
                source_ref=payload.get("source_ref", ""),
                target_ref=payload.get("target_ref", ""),
                merged_by=payload.get("merged_by"),
                merged_at=self._time(payload.get("merged_at"), record.observed_at),
                commit_id=payload.get("commit_id"),
            )
        if observation_type == ObservationType.BUILD:
            return BuildFacts(
                build_id=record.record_id,
                status=payload.get("status", "unknown"),
                started_at=self._time(payload.get("started_at"), record.observed_at),
                completed_at=self._time(payload.get("completed_at"), None),
                duration_seconds=payload.get("duration_seconds"),
            )
        if observation_type == ObservationType.DEPLOYMENT:
            return DeploymentFacts(
                deployment_id=record.record_id,
                environment=payload.get("environment", "unknown"),
                status=payload.get("status", "unknown"),
                deployed_at=self._time(payload.get("deployed_at"), record.observed_at),
                version=payload.get("version"),
            )
        if observation_type == ObservationType.INCIDENT:
            return IncidentFacts(
                incident_id=record.record_id,
                title=payload.get("title", ""),
                severity=payload.get("severity", "unknown"),
                status=payload.get("status", "unknown"),
                started_at=self._time(payload.get("started_at"), record.observed_at),
                resolved_at=self._time(payload.get("resolved_at"), None),
                service=payload.get("service"),
            )
        if observation_type == ObservationType.RELEASE:
            return ReleaseFacts(
                release_id=record.record_id,
                version=payload.get("version", ""),
                status=payload.get("status", "unknown"),
                released_at=self._time(payload.get("released_at"), record.observed_at),
                author=payload.get("author"),
            )
        if observation_type == ObservationType.TEST:
            return TestFacts(
                test_run_id=record.record_id,
                status=payload.get("status", "unknown"),
                started_at=self._time(payload.get("started_at"), record.observed_at),
                completed_at=self._time(payload.get("completed_at"), None),
                passed=int(payload.get("passed", 0) or 0),
                failed=int(payload.get("failed", 0) or 0),
                skipped=int(payload.get("skipped", 0) or 0),
            )
        if observation_type == ObservationType.DOCUMENTATION:
            return DocumentationFacts(
                document_id=record.record_id,
                path=payload.get("path", ""),
                observed_at=record.observed_at,
                state=payload.get("state", "unknown"),
                title=payload.get("title"),
            )
        raise ValueError(f"unsupported observation type: {observation_type.value}")

    def _targets_for(
        self,
        payload: dict,
    ) -> tuple[EntityRef, ...]:
        targets = []
        for target in payload.get("targets", ()):
            targets.append(
                EntityRef(
                    id=str(target),
                    type=EntityType.FILE,
                )
            )
        return tuple(targets)

    def _category_for(
        self,
        observation_type: ObservationType,
    ) -> ObservationCategory:
        if observation_type in {ObservationType.COMMIT, ObservationType.MERGE}:
            return ObservationCategory.SOURCE_CONTROL
        if observation_type in {
            ObservationType.PULL_REQUEST,
            ObservationType.REVIEW,
            ObservationType.COMMENT,
        }:
            return ObservationCategory.CODE_REVIEW
        if observation_type == ObservationType.ISSUE:
            return ObservationCategory.PROJECT_MANAGEMENT
        if observation_type in {
            ObservationType.BUILD,
            ObservationType.DEPLOYMENT,
            ObservationType.RELEASE,
        }:
            return ObservationCategory.CI_CD
        if observation_type == ObservationType.INCIDENT:
            return ObservationCategory.RUNTIME
        if observation_type == ObservationType.TEST:
            return ObservationCategory.TESTING
        if observation_type == ObservationType.DOCUMENTATION:
            return ObservationCategory.DOCUMENTATION
        return ObservationCategory.SOURCE_CONTROL

    def _time(
        self,
        value,
        default,
    ):
        if value is None:
            return default
        if isinstance(value, datetime):
            if value.tzinfo is None:
                logger.warning(f"Naive timestamp detected: {value}. Normalizing to UTC.")
                return value.replace(tzinfo=timezone.utc)
            return value
        
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            logger.warning(f"Naive timestamp string detected: {value}. Normalizing to UTC.")
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed

    def _stable_id(
        self,
        *parts: str,
    ) -> str:
        return str(
            uuid5(
                NAMESPACE_URL,
                "|".join(parts),
            )
        )

