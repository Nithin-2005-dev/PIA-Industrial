"""Stage 05 - synthesize canonical evidence from measurements."""

from __future__ import annotations

import time
from collections import Counter

from app.evidence.core import EvidenceContext
from app.evidence.synthesis.engine import EvidenceSynthesisEngine

from ..context import PlatformContext
from ..ui import metric, ranking, section, success, warning
from .base import PipelineStage


class EvidenceStage(PipelineStage):
    name = "Measurement to Evidence"

    def execute(self, context: PlatformContext) -> None:
        if not context.measurements:
            warning("No measurements available")
            return

        started = time.perf_counter()
        engine = context.resolve(EvidenceSynthesisEngine)
        evidence_context = EvidenceContext(
            tenant_id=context.tenant_id,
            metadata={"repository": context.repository},
        )
        package = engine.synthesize(context.measurements, evidence_context)

        context.evidence_package = package
        context.metrics["evidence"] = len(package.evidence)
        context.metrics["evidence_seconds"] = time.perf_counter() - started
        context.metrics["evidence_for_expertise"] = len(package.for_expertise())
        context.metrics["rejected_evidence"] = package.rejected_count

        evidence_items = list(package.evidence)

        section("Evidence Package")
        metric("Pipeline Version", package.pipeline_version)
        metric("Generated Evidence", len(evidence_items))
        metric("Usable for Expertise", len(package.for_expertise()))
        metric("Rejected Items", package.rejected_count)
        metric("Input Measurements", package.metadata.get("input_measurements", 0))
        metric("Validated Measurements", package.metadata.get("validated_measurements", 0))
        metric("Synthesis Time", f"{context.metrics['evidence_seconds']:.3f}s")

        self._evidence_health(evidence_items)
        self._summaries(evidence_items)
        self._lineage(evidence_items)
        self._samples(evidence_items)
        success("Evidence layer synthesized canonical evidence package")

    def _evidence_health(self, evidence_items) -> None:
        section("Evidence Health")
        metric("Evidence Present", "PASS" if evidence_items else "FAIL")
        metric(
            "Confidence Propagated",
            "PASS" if all(item.confidence >= 0.0 for item in evidence_items) else "FAIL",
        )
        metric(
            "Uncertainty Propagated",
            "PASS" if all(item.uncertainty >= 0.0 for item in evidence_items) else "FAIL",
        )
        metric(
            "Explainability Preserved",
            "PASS" if all(item.traceability.explanation for item in evidence_items) else "FAIL",
        )
        metric(
            "Lineage Preserved",
            "PASS" if all(item.lineage.source_measurement_ids for item in evidence_items) else "FAIL",
        )

    def _summaries(self, evidence_items) -> None:
        categories = Counter(item.category for item in evidence_items)
        severity = Counter(item.severity.value for item in evidence_items)
        priority = Counter(item.priority.value for item in evidence_items)
        ranking("Evidence Categories", [f"{key:<24} {value}" for key, value in categories.items()])
        ranking("Severity", [f"{key:<24} {value}" for key, value in severity.items()])
        ranking("Priority", [f"{key:<24} {value}" for key, value in priority.items()])

    def _lineage(self, evidence_items) -> None:
        measurements = sum(len(item.supporting_measurements) for item in evidence_items)
        rules = sum(len(item.traceability.synthesis_rule_ids) for item in evidence_items)
        section("Evidence Lineage")
        metric("Supporting Measurements", measurements)
        metric("Synthesis Rules", rules)

    def _samples(self, evidence_items) -> None:
        ranking(
            "Sample Evidence",
            [
                (
                    f"{item.name:<34} confidence={item.confidence:.3f} "
                    f"uncertainty={item.uncertainty:.3f} quality={item.quality:.3f}"
                )
                for item in evidence_items[:8]
            ],
        )
