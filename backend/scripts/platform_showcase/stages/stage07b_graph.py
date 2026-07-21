"""Stage 07b - Knowledge Graph via the canonical graph service."""

from __future__ import annotations

from app.graph.builders import KnowledgeGraphBuilder
from app.graph.validation import GraphQualityValidator

from ..context import PlatformContext
from ..ui import metric, section, success, warning
from .base import PipelineStage


class KnowledgeGraphStage(PipelineStage):
    name = "Knowledge Graph Construction"

    def execute(
        self,
        context: PlatformContext,
    ) -> None:
        knowledge_models = getattr(context, "knowledge", [])
        expertise_models = getattr(context, "expertise_models", [])
        evidence_package = getattr(context, "evidence_package", None)

        if not knowledge_models and not expertise_models:
            warning("No knowledge or expertise models - skipping Knowledge Graph")
            return

        builder = context.resolve(KnowledgeGraphBuilder)
        graph = builder.build_from_models(
            knowledge_models=knowledge_models,
            expertise_models=expertise_models,
            evidence_package=evidence_package,
        )

        validator = GraphQualityValidator()
        validation_report = validator.validate(graph)
        build_report = validator.generate_build_report(graph, validation_report)

        context.knowledge_graph = graph
        context.metrics["graph_nodes"] = len(graph.nodes)
        context.metrics["graph_edges"] = len(graph.edges)

        section("Knowledge Graph Build Report")
        metric("Nodes Created", build_report.nodes_created)
        metric("Edges Created", build_report.edges_created)
        metric("Edges Rejected", build_report.edges_rejected)
        metric("Identity Resolution Rate", f"{build_report.identity_resolution_rate:.2%}")
        metric("Relationship Coverage", f"{build_report.relationship_coverage:.2f}")
        metric("Validation Status", build_report.validation_status)
        metric("Health Score", f"{validation_report.health_score:.2f}")
        
        if validation_report.warnings:
            for w in validation_report.warnings:
                warning(f"Validation Warning: {w.message}")
        if validation_report.errors:
            for e in validation_report.errors:
                warning(f"Validation Error: {e.message}")

        success("Knowledge Graph constructed by canonical Graph Service")
