from app.intelligence.measurement.domain.catalog import DefaultMeasurementCatalog
from app.intelligence.measurement.plugins_runtime.packs import MeasurementPack


class DefaultDomainPacks:

    @classmethod
    def build(
        cls,
    ) -> list[MeasurementPack]:
        registry = DefaultMeasurementCatalog.build()

        def definitions(
            *ids,
        ):
            return tuple(
                registry.get(
                    definition_id
                )
                for definition_id in ids
            )

        return [
            MeasurementPack(
                id="architecture",
                name="Architecture",
                domain="architecture",
                version="1.0",
                definitions=definitions(
                    "patch_complexity_delta",
                    "change_distribution_entropy",
                ),
            ),
            MeasurementPack(
                id="code-quality",
                name="Code Quality",
                domain="code_quality",
                version="1.0",
                definitions=definitions(
                    "code_churn",
                    "patch_complexity_delta",
                    "review_attention_need",
                ),
            ),
            MeasurementPack(
                id="git-analytics",
                name="Git Analytics",
                domain="git_analytics",
                version="1.0",
                definitions=definitions(
                    "code_churn",
                    "files_changed",
                    "change_surface_area",
                ),
            ),
            MeasurementPack(
                id="delivery-devops",
                name="Delivery & DevOps",
                domain="delivery_devops",
                version="1.0",
                definitions=definitions(
                    "review_attention_need",
                ),
            ),
            MeasurementPack(
                id="runtime",
                name="Runtime",
                domain="runtime",
                version="1.0",
                definitions=(),
            ),
            MeasurementPack(
                id="cloud",
                name="Cloud",
                domain="cloud",
                version="1.0",
                definitions=(),
            ),
            MeasurementPack(
                id="security",
                name="Security",
                domain="security",
                version="1.0",
                definitions=(),
            ),
            MeasurementPack(
                id="ai-engineering",
                name="AI Engineering",
                domain="ai_engineering",
                version="1.0",
                definitions=(),
            ),
            MeasurementPack(
                id="database",
                name="Database",
                domain="database",
                version="1.0",
                definitions=(),
            ),
            MeasurementPack(
                id="testing",
                name="Testing",
                domain="testing",
                version="1.0",
                definitions=(),
            ),
            MeasurementPack(
                id="documentation",
                name="Documentation",
                domain="documentation",
                version="1.0",
                definitions=(),
            ),
            MeasurementPack(
                id="team-collaboration",
                name="Team Collaboration",
                domain="team_collaboration",
                version="1.0",
                definitions=(),
            ),
            MeasurementPack(
                id="reliability",
                name="Reliability",
                domain="reliability",
                version="1.0",
                definitions=(),
            ),
            MeasurementPack(
                id="performance",
                name="Performance",
                domain="performance",
                version="1.0",
                definitions=(),
            ),
        ]


