from dataclasses import replace

from app.knowledge.evidence.domain import Evidence
from app.knowledge.evidence.domain import EvidenceStatus
from app.knowledge.evidence.domain import EvidenceValidationResult
from app.knowledge.evidence.domain import EvidenceValidationStatus
from app.knowledge.evidence.ontology import EvidenceOntology


class EvidenceValidationPipeline:

    def __init__(
        self,
        ontology: EvidenceOntology,
    ):
        self._ontology = ontology

    def validate(
        self,
        evidence: Evidence,
    ) -> Evidence:
        results = (
            self._logical(evidence),
            self._semantic(evidence),
            self._ontology_check(evidence),
            self._dependency(evidence),
            self._benchmark(evidence),
            self._confidence(evidence),
            self._completeness(evidence),
            self._consistency(evidence),
            self._contradiction(evidence),
        )

        status = EvidenceStatus.VALIDATED
        if any(
            result.status == EvidenceValidationStatus.FAILED
            for result in results
        ):
            status = EvidenceStatus.REJECTED

        return replace(
            evidence,
            status=status,
            validation_results=results,
            traceability=replace(
                evidence.traceability,
                validation_checks=tuple(
                    result.name
                    for result in results
                ),
            ),
        )

    def _passed(
        self,
        name: str,
    ) -> EvidenceValidationResult:
        return EvidenceValidationResult(
            name=name,
            status=EvidenceValidationStatus.PASSED,
        )

    def _failed(
        self,
        name: str,
        error: str,
    ) -> EvidenceValidationResult:
        return EvidenceValidationResult(
            name=name,
            status=EvidenceValidationStatus.FAILED,
            errors=(error,),
        )

    def _logical(
        self,
        evidence: Evidence,
    ) -> EvidenceValidationResult:
        if not 0.0 <= evidence.confidence <= 1.0:
            return self._failed(
                "logical",
                "confidence must be between 0 and 1",
            )
        if evidence.uncertainty < 0.0:
            return self._failed(
                "logical",
                "uncertainty must be non-negative",
            )
        return self._passed(
            "logical"
        )

    def _semantic(
        self,
        evidence: Evidence,
    ) -> EvidenceValidationResult:
        if not evidence.name or not evidence.description:
            return self._failed(
                "semantic",
                "evidence requires a name and description",
            )
        return self._passed(
            "semantic"
        )

    def _ontology_check(
        self,
        evidence: Evidence,
    ) -> EvidenceValidationResult:
        if not self._ontology.has_concept(
            evidence.category
        ):
            return self._failed(
                "ontology",
                "evidence category is not in ontology",
            )
        return self._passed(
            "ontology"
        )

    def _dependency(
        self,
        evidence: Evidence,
    ) -> EvidenceValidationResult:
        required = tuple(
            evidence.metadata.get(
                "required_measurements",
                (),
            )
        )
        present = {
            measurement.definition_id
            for measurement in evidence.supporting_measurements
        }
        missing = tuple(
            measurement_id
            for measurement_id in required
            if measurement_id not in present
        )
        if missing:
            return self._failed(
                "dependency",
                "missing required measurements: "
                + ", ".join(
                    missing
                ),
            )
        return self._passed(
            "dependency"
        )

    def _benchmark(
        self,
        evidence: Evidence,
    ) -> EvidenceValidationResult:
        if evidence.benchmark_context.quality < 0.5:
            return EvidenceValidationResult(
                name="benchmark",
                status=EvidenceValidationStatus.WARNING,
                warnings=("benchmark quality is low",),
            )
        return self._passed(
            "benchmark"
        )

    def _confidence(
        self,
        evidence: Evidence,
    ) -> EvidenceValidationResult:
        if evidence.confidence <= 0.0:
            return self._failed(
                "confidence",
                "evidence confidence could not be established",
            )
        return self._passed(
            "confidence"
        )

    def _completeness(
        self,
        evidence: Evidence,
    ) -> EvidenceValidationResult:
        if not evidence.supporting_measurements:
            return self._failed(
                "completeness",
                "evidence has no supporting measurements",
            )
        return self._passed(
            "completeness"
        )

    def _consistency(
        self,
        evidence: Evidence,
    ) -> EvidenceValidationResult:
        tenants = {
            measurement.tenant_id
            for measurement in evidence.supporting_measurements
            if measurement.tenant_id is not None
        }
        if len(
            tenants
        ) > 1:
            return self._failed(
                "consistency",
                "supporting measurements cross tenant boundaries",
            )
        return self._passed(
            "consistency"
        )

    def _contradiction(
        self,
        evidence: Evidence,
    ) -> EvidenceValidationResult:
        supporting = {
            measurement.id
            for measurement in evidence.supporting_measurements
        }
        contradicting = {
            measurement.id
            for measurement in evidence.contradicting_measurements
        }
        if supporting.intersection(
            contradicting
        ):
            return self._failed(
                "contradiction",
                "a measurement both supports and contradicts evidence",
            )
        return self._passed(
            "contradiction"
        )

