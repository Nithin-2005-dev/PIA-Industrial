from app.intelligence.measurement.domain import MeasurementConcept
from app.intelligence.measurement.domain import MeasurementReference


class MeasurementOntology:

    def __init__(
        self,
        concepts: list[MeasurementConcept],
    ):
        self._concepts = {
            concept.id: concept
            for concept in concepts
        }

    @classmethod
    def default(
        cls,
    ):
        references = (
            MeasurementReference(
                title="ISO/IEC 25010 software quality model",
                source="ISO/IEC",
                identifier="25010",
            ),
            MeasurementReference(
                title="ISO/IEC 15939 measurement process",
                source="ISO/IEC",
                identifier="15939",
            ),
            MeasurementReference(
                title="Guide to the Expression of Uncertainty in Measurement",
                source="JCGM",
                identifier="GUM",
            ),
        )

        return cls(
            concepts=[
                MeasurementConcept(
                    id="structural",
                    display_name="Structural",
                    scientific_meaning="Inherent topological and syntactic properties of the artifacts.",
                    category="code_quality",
                    references=references,
                ),
                MeasurementConcept(
                    id="temporal",
                    display_name="Temporal",
                    scientific_meaning="Change frequencies, recency, and temporal patterns of activity.",
                    category="behavioral",
                    references=references,
                ),
                MeasurementConcept(
                    id="knowledge",
                    display_name="Knowledge & Ownership",
                    scientific_meaning="Distribution of expertise, ownership, and information across the organization.",
                    category="organizational",
                    references=references,
                ),
                MeasurementConcept(
                    id="review",
                    display_name="Review & Collaboration",
                    scientific_meaning="Interaction, latency, and quality of peer review processes.",
                    category="process",
                    references=references,
                ),
                MeasurementConcept(
                    id="testing",
                    display_name="Testing",
                    scientific_meaning="Validation, coverage, and reliability signals from test executions.",
                    category="quality_assurance",
                    references=references,
                ),
                MeasurementConcept(
                    id="runtime",
                    display_name="Runtime",
                    scientific_meaning="Operational metrics, availability, and performance in deployed environments.",
                    category="operations",
                    references=references,
                ),
                # Granular concepts mapping to parents
                MeasurementConcept(
                    id="complexity",
                    display_name="Complexity",
                    scientific_meaning="Structural and behavioral effort required to understand or change an artifact.",
                    category="structural",
                    parent_id="structural",
                    references=references,
                ),
                MeasurementConcept(
                    id="coupling",
                    display_name="Coupling",
                    scientific_meaning="Degree of interdependence between modules or components.",
                    category="structural",
                    parent_id="structural",
                    references=references,
                ),
                MeasurementConcept(
                    id="churn",
                    display_name="Churn",
                    scientific_meaning="Volume of code additions and deletions over time.",
                    category="temporal",
                    parent_id="temporal",
                    references=references,
                ),
                MeasurementConcept(
                    id="activity_frequency",
                    display_name="Activity Frequency",
                    scientific_meaning="Rate of engineering interactions with an artifact.",
                    category="temporal",
                    parent_id="temporal",
                    references=references,
                ),
                MeasurementConcept(
                    id="ownership",
                    display_name="Ownership",
                    scientific_meaning="Concentration and distribution of primary authors for an artifact.",
                    category="knowledge",
                    parent_id="knowledge",
                    references=references,
                ),
                MeasurementConcept(
                    id="review_latency",
                    display_name="Review Latency",
                    scientific_meaning="Time delay between contribution and review completion.",
                    category="review",
                    parent_id="review",
                    references=references,
                ),
                MeasurementConcept(
                    id="change_impact",
                    display_name="Change Impact",
                    scientific_meaning="Expected review and coordination load introduced by an observed change.",
                    category="delivery",
                    parent_id="structural",
                    references=references,
                ),
                MeasurementConcept(
                    id="information_distribution",
                    display_name="Information Distribution",
                    scientific_meaning="Dispersion of observed engineering activity across artifacts, people or time.",
                    category="information_theory",
                    parent_id="knowledge",
                    references=references,
                ),
            ],
        )

    def get(
        self,
        concept_id: str,
    ) -> MeasurementConcept:
        return self._concepts[
            concept_id
        ]

    def children_of(
        self,
        concept_id: str,
    ) -> list[MeasurementConcept]:
        return [
            concept
            for concept in self._concepts.values()
            if concept.parent_id == concept_id
        ]

    def all(
        self,
    ) -> list[MeasurementConcept]:
        return list(
            self._concepts.values()
        )
