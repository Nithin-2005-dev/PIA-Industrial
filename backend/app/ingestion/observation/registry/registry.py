from dataclasses import dataclass

from app.ingestion.observation.domain import ObservationCategory
from app.ingestion.observation.domain import ObservationLifecycle
from app.ingestion.observation.domain import ObservationType


@dataclass(frozen=True)
class ObservationDefinition:
    id: str
    observation_type: ObservationType
    category: ObservationCategory
    schema: str
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...]
    validation_rules: tuple[str, ...]
    supported_adapters: tuple[str, ...]
    version: str
    lifecycle: ObservationLifecycle


class ObservationRegistry:

    def __init__(
        self,
        definitions: tuple[ObservationDefinition, ...] = (),
    ):
        self._definitions = {
            definition.id: definition
            for definition in definitions
        }

    @classmethod
    def default(
        cls,
    ) -> "ObservationRegistry":
        return cls(
            definitions=(
                _definition(
                    ObservationType.COMMIT,
                    ObservationCategory.SOURCE_CONTROL,
                    "CommitFacts",
                    ("commit_id", "message", "authored_at"),
                    ("files", "parent_ids", "signature_verified"),
                    ("github", "github_rest", "gitlab", "azure_devops"),
                ),
                _definition(
                    ObservationType.PULL_REQUEST,
                    ObservationCategory.CODE_REVIEW,
                    "PullRequestFacts",
                    ("pull_request_id", "title", "state", "created_at"),
                    ("commit_ids", "changed_files"),
                    ("github", "github_rest", "gitlab", "azure_devops"),
                ),
                _definition(
                    ObservationType.ISSUE,
                    ObservationCategory.PROJECT_MANAGEMENT,
                    "IssueFacts",
                    ("issue_id", "title", "state", "created_at"),
                    ("labels", "closed_at"),
                    ("github", "github_rest", "gitlab", "azure_devops", "jira"),
                ),
                _definition(
                    ObservationType.REVIEW,
                    ObservationCategory.CODE_REVIEW,
                    "ReviewFacts",
                    ("review_id", "subject_id", "state"),
                    ("reviewer", "submitted_at", "comment_count"),
                    ("github", "github_rest", "gitlab", "azure_devops"),
                ),
                _definition(
                    ObservationType.COMMENT,
                    ObservationCategory.CODE_REVIEW,
                    "CommentFacts",
                    ("comment_id", "subject_id", "body", "created_at"),
                    ("author", "updated_at"),
                    (
                        "github",
                        "github_rest",
                        "gitlab",
                        "bitbucket",
                        "jira",
                        "linear",
                        "slack",
                        "teams",
                        "email",
                    ),
                ),
                _definition(
                    ObservationType.MERGE,
                    ObservationCategory.SOURCE_CONTROL,
                    "MergeFacts",
                    ("merge_id", "source_ref", "target_ref", "merged_at"),
                    ("merged_by", "commit_id"),
                    ("github", "github_rest", "gitlab", "bitbucket", "azure_devops"),
                ),
                _definition(
                    ObservationType.BUILD,
                    ObservationCategory.CI_CD,
                    "BuildFacts",
                    ("build_id", "status", "started_at"),
                    ("completed_at", "duration_seconds"),
                    (
                        "github",
                        "github_rest",
                        "github_actions",
                        "gitlab",
                        "gitlab_ci",
                        "azure_devops",
                        "azure_pipelines",
                    ),
                ),
                _definition(
                    ObservationType.INCIDENT,
                    ObservationCategory.RUNTIME,
                    "IncidentFacts",
                    ("incident_id", "title", "severity", "status", "started_at"),
                    ("resolved_at", "service"),
                    ("jira", "linear", "slack", "teams", "email", "pagerduty"),
                ),
                _definition(
                    ObservationType.RELEASE,
                    ObservationCategory.CI_CD,
                    "ReleaseFacts",
                    ("release_id", "version", "status", "released_at"),
                    ("author",),
                    ("github", "github_rest", "gitlab", "bitbucket", "azure_devops"),
                ),
                _definition(
                    ObservationType.DEPLOYMENT,
                    ObservationCategory.CI_CD,
                    "DeploymentFacts",
                    ("deployment_id", "environment", "status", "deployed_at"),
                    ("version",),
                    (
                        "github",
                        "github_rest",
                        "github_actions",
                        "gitlab",
                        "gitlab_ci",
                        "azure_devops",
                        "azure_pipelines",
                    ),
                ),
                _definition(
                    ObservationType.RUNTIME,
                    ObservationCategory.RUNTIME,
                    "RuntimeFacts",
                    ("runtime_id", "observed_at", "service", "status"),
                    ("counters",),
                    ("prometheus", "datadog", "cloudwatch", "azure_monitor"),
                ),
                _definition(
                    ObservationType.SECURITY,
                    ObservationCategory.SECURITY,
                    "SecurityFacts",
                    ("finding_id", "scanner", "observed_at", "category", "state"),
                    ("affected_refs",),
                    ("github_dependabot", "snyk", "semgrep", "codeql"),
                ),
                _definition(
                    ObservationType.TEST,
                    ObservationCategory.TESTING,
                    "TestFacts",
                    ("test_run_id", "status", "started_at"),
                    ("completed_at", "passed", "failed", "skipped"),
                    (
                        "junit",
                        "pytest",
                        "github",
                        "github_rest",
                        "github_actions",
                        "gitlab",
                        "gitlab_ci",
                        "azure_devops",
                    ),
                ),
                _definition(
                    ObservationType.CLOUD,
                    ObservationCategory.CLOUD,
                    "CloudFacts",
                    ("resource_id", "resource_type", "observed_at", "state"),
                    ("region",),
                    ("aws", "azure", "gcp"),
                ),
                _definition(
                    ObservationType.INFRASTRUCTURE,
                    ObservationCategory.INFRASTRUCTURE,
                    "InfrastructureFacts",
                    ("resource_id", "resource_type", "observed_at", "state"),
                    ("location",),
                    ("terraform", "kubernetes", "ansible"),
                ),
                _definition(
                    ObservationType.AI_SYSTEM,
                    ObservationCategory.AI,
                    "AISystemFacts",
                    ("system_id", "observed_at", "provider", "model", "state"),
                    (),
                    ("openai", "anthropic", "azure_ai", "vertex_ai"),
                ),
                _definition(
                    ObservationType.DOCUMENTATION,
                    ObservationCategory.DOCUMENTATION,
                    "DocumentationFacts",
                    ("document_id", "path", "observed_at", "state"),
                    ("title",),
                    ("github", "github_rest", "gitlab", "confluence"),
                ),
            )
        )

    def register(
        self,
        definition: ObservationDefinition,
    ) -> None:
        self._definitions[
            definition.id
        ] = definition

    def for_observation(
        self,
        observation_type: ObservationType,
        version: str,
    ) -> ObservationDefinition:
        key = f"{observation_type.value}.v{version.split('.')[0]}"
        return self._definitions[
            key
        ]

    def all(
        self,
    ) -> tuple[ObservationDefinition, ...]:
        return tuple(
            self._definitions.values()
        )


def _definition(
    observation_type: ObservationType,
    category: ObservationCategory,
    schema: str,
    required_fields: tuple[str, ...],
    optional_fields: tuple[str, ...],
    supported_adapters: tuple[str, ...],
) -> ObservationDefinition:
    return ObservationDefinition(
        id=f"{observation_type.value}.v1",
        observation_type=observation_type,
        category=category,
        schema=schema,
        required_fields=required_fields,
        optional_fields=optional_fields,
        validation_rules=(
            "schema",
            "type",
            "timestamp",
            "duplicate",
            "malformed",
            "required",
            "source",
            "version",
        ),
        supported_adapters=supported_adapters,
        version="1.0",
        lifecycle=ObservationLifecycle.PRODUCTION,
    )
