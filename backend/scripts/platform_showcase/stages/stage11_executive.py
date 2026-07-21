"""Stage 11 - Executive Dashboard.

Consumes decisions AND org_intelligence to render a rich executive view.
"""

from __future__ import annotations

from ..context import PlatformContext
from ..ui import lineage, metric, ranking, section, success, warning
from .base import PipelineStage


class ExecutiveDashboardStage(PipelineStage):
    name = "Executive Dashboard"

    def execute(self, context: PlatformContext) -> None:
        reasoning_graph = getattr(context, "reasoning_graph", None)
        if not reasoning_graph:
            warning("No GraphEngine available (Stage 9 and 10 skipped or failed)")
            return

        from app.kernel.presentation.report import ExecutiveReportGenerator
        
        section("Executive Dashboard (Graph OS)")
        metric("Observations",       len(context.observations))
        metric("Measurements",       len(context.measurements))
        
        # Use our beautiful presentation engine
        generator = ExecutiveReportGenerator(reasoning_graph)
        
        # Since we are running synchronously in the CLI showcase without an LLM injected by default,
        # we will generate the report without phrased narrative impacts (fallback to deterministic text).
        report_md = generator.generate_markdown_report(phrased_impacts={})
        
        print("\n\n" + "="*80)
        print("                BEAUTIFUL EXECUTIVE PRESENTATION")
        print("="*80 + "\n")
        print(report_md)
        print("\n" + "="*80 + "\n")
        
        from ..ui import MODULE_DISPLAY_NAMES
        stage_names = context.metrics.get("execution_stage_names", ())
        if stage_names:
            seen = set()
            path = ["GitHub Commit"]
            for name in stage_names:
                if name not in seen:
                    seen.add(name)
                    path.append(name)
        else:
            order = context.metrics.get("execution_order", ())
            path = ["GitHub Commit"] + [
                MODULE_DISPLAY_NAMES.get(m, m) for m in dict.fromkeys(order)
            ]

        lineage("Canonical Lineage", path=path)
        success("Executive dashboard beautifully rendered from deterministic graph topological outputs")


