from dataclasses import dataclass

from app.intelligence.measurement.domain import MeasurementReference


@dataclass(frozen=True)
class StandardReference:
    id: str
    name: str
    organization: str
    description: str
    applies_to: tuple[str, ...] = ()

    def as_measurement_reference(
        self,
    ) -> MeasurementReference:
        return MeasurementReference(
            title=self.name,
            source=self.organization,
            identifier=self.id,
            notes=self.description,
        )


class StandardsCatalog:

    def __init__(
        self,
    ):
        self._standards = {}

    @classmethod
    def default(
        cls,
    ):
        catalog = cls()

        for standard in (
            StandardReference(
                id="ISO-15939",
                name="ISO/IEC 15939",
                organization="ISO/IEC",
                description="Software measurement process.",
                applies_to=("measurement_process",),
            ),
            StandardReference(
                id="ISO-25010",
                name="ISO/IEC 25010",
                organization="ISO/IEC",
                description="Software product quality model.",
                applies_to=("maintainability", "reliability"),
            ),
            StandardReference(
                id="ISO-25023",
                name="ISO/IEC 25023",
                organization="ISO/IEC",
                description="Software quality measurement.",
                applies_to=("quality_measurement",),
            ),
            StandardReference(
                id="CISQ",
                name="CISQ Software Quality Measures",
                organization="CISQ",
                description="Automated software quality characteristics.",
                applies_to=("security", "reliability", "maintainability"),
            ),
            StandardReference(
                id="DORA",
                name="DORA Metrics",
                organization="DORA",
                description="Delivery performance measurement framework.",
                applies_to=("delivery", "devops"),
            ),
            StandardReference(
                id="SPACE",
                name="SPACE Framework",
                organization="GitHub/Microsoft Research",
                description="Developer productivity framework.",
                applies_to=("team_collaboration",),
            ),
            StandardReference(
                id="GQM",
                name="Goal Question Metric",
                organization="Software Engineering Research",
                description="Goal-driven measurement method.",
                applies_to=("measurement_design",),
            ),
            StandardReference(
                id="GSN",
                name="Goal Structuring Notation",
                organization="Assurance Case Research",
                description="Structured assurance argument notation.",
                applies_to=("assurance",),
            ),
        ):
            catalog.register(
                standard
            )

        return catalog

    def register(
        self,
        standard: StandardReference,
    ):
        self._standards[
            standard.id
        ] = standard

    def get(
        self,
        standard_id: str,
    ) -> StandardReference:
        return self._standards[
            standard_id
        ]

    def all(
        self,
    ) -> list[StandardReference]:
        return list(
            self._standards.values()
        )

    def for_topic(
        self,
        topic: str,
    ) -> list[StandardReference]:
        return [
            standard
            for standard in self._standards.values()
            if topic in standard.applies_to
        ]


