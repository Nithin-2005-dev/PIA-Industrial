import pytest
import asyncio

from app.kernel.graph import GraphEngine, NodeType
from app.kernel.models import CapabilityResult
from app.kernel.reasoning.builder import ReasoningGraphBuilder
from app.kernel.reasoning.rule_engine import RuleEngine, create_single_point_of_failure_rule
from app.kernel.reasoning.strategy import StrategyEngine
from app.kernel.intelligence.ontology import CoreOntology
from app.kernel.intelligence.translator import BusinessTranslator
from app.kernel.intelligence.priority import PriorityEngine
from app.kernel.decision.root_cause import RootCauseAnalyzer
from app.kernel.decision.optimizer import GraphOptimizer
from app.kernel.decision.mitigation import MitigationEngine
from app.kernel.decision.allocation import ResourceAllocator
from app.kernel.resources import ResourceManager
from app.kernel.scheduler import Scheduler
from app.kernel.presentation.visualize import GraphVisualizer
from app.kernel.presentation.phrasing import InsightPhraser
from app.kernel.presentation.report import ExecutiveReportGenerator

# Mock Provider for the test
class MockProviderManager:
    def get_provider(self, name: str):
        return MockProvider()

class MockProvider:
    def generate(self, *args, **kwargs):
        class MockResponse:
            content = "This is a beautifully styled, authoritative executive summary warning of severe operational risk due to a single point of failure in a critical module."
        return MockResponse()

def test_presentation_pipeline():
    asyncio.run(_run_test_presentation_pipeline())

async def _run_test_presentation_pipeline():
    # Setup Phase 1-4
    graph = GraphEngine()
    results = [
        CapabilityResult(
            capability_id="cap_bus_factor",
            status="SUCCESS",
            confidence=1.0,
            summary="Bus factor is 1 for critical module",
            evidence_ids=[],
            raw_output={"bus_factor": 1},
            normalized_output={},
            warnings=[],
            recommendations=[],
            metadata={},
            execution_time_ms=10.0
        )
    ]
    
    # Run the full gauntlet
    ReasoningGraphBuilder(graph).build_from_results(results)
    
    rule_engine = RuleEngine(graph)
    rule_engine.register_rule(create_single_point_of_failure_rule())
    StrategyEngine(graph, rule_engine).execute_reasoning_cycle()
    
    PriorityEngine(graph).score_graph_inferences()
    BusinessTranslator(graph, CoreOntology()).translate_inferences_to_impact()
    
    RootCauseAnalyzer(graph).analyze_root_causes()
    GraphOptimizer(graph).optimize()
    MitigationEngine(graph).generate_mitigations()
    
    res = ResourceManager()
    sched = Scheduler()
    ResourceAllocator(graph, res, sched).allocate_mitigations()
    
    # 5. Presentation Phase
    
    # A. Phrasing
    phraser = InsightPhraser(graph, MockProvider())
    phrased_impacts = await phraser.phrase_impacts()
    assert len(phrased_impacts) == 1
    
    # B. Visualization
    visualizer = GraphVisualizer(graph)
    mermaid = visualizer.generate_mermaid_diagram()
    assert "```mermaid" in mermaid
    
    # C. Executive Report
    generator = ExecutiveReportGenerator(graph)
    report = generator.generate_markdown_report(phrased_impacts)
    
    assert "Executive Intelligence Report" in report
    assert "operational risk" in report # From mock 
    assert "Review system architecture" in report # From mitigation
    assert "/100" in report # From priority or similar score format
    assert "```mermaid" in report # From visualization
    
    # Save the report for manual review (optional artifact)
    with open("tests/test_report_output.md", "w") as f:
        f.write(report)
