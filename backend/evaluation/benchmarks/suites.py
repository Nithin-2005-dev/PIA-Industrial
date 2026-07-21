from dataclasses import dataclass, field
from typing import Any

@dataclass
class ExpectedFact:
    description: str
    assertion_type: str # e.g. 'exists', 'greater_than', 'equals', 'absent'
    target: str # e.g. 'commit_count', 'confidence', 'reasoning_graph'
    value: Any = None

@dataclass
class BenchmarkQuery:
    id: str
    question: str
    category: str
    expected_facts: list[ExpectedFact] = field(default_factory=list)

# Informational Queries
INFORMATIONAL_SUITE = [
    BenchmarkQuery(
        id="info_top_contributor",
        question="Who is the top contributor?",
        category="Informational",
        expected_facts=[
            ExpectedFact("Returned contributor exists", "exists", "contributor_name"),
            ExpectedFact("Commit count > 0", "greater_than", "commits", 0),
            ExpectedFact("Confidence exists", "exists", "confidence"),
            ExpectedFact("Evidence exists", "exists", "evidence"),
            ExpectedFact("No reasoning graph generated", "absent", "reasoning_graph")
        ]
    ),
    BenchmarkQuery(
        id="info_module_ownership",
        question="Who owns src/compiler?",
        category="Informational",
        expected_facts=[
            ExpectedFact("Owner name exists", "exists", "owner"),
            ExpectedFact("Target is src/compiler", "equals", "target_module", "src/compiler"),
            ExpectedFact("No reasoning graph generated", "absent", "reasoning_graph")
        ]
    )
]

# Diagnostic Queries
DIAGNOSTIC_SUITE = [
    BenchmarkQuery(
        id="diag_compiler_risk",
        question="Why is the compiler risky?",
        category="Diagnostic",
        expected_facts=[
            ExpectedFact("Reasoning graph is generated", "exists", "reasoning_graph"),
            ExpectedFact("Root cause identified", "exists", "root_cause"),
            ExpectedFact("Evidence chain exists", "exists", "evidence_chain")
        ]
    )
]

ALL_SUITES = {
    "informational": INFORMATIONAL_SUITE,
    "diagnostic": DIAGNOSTIC_SUITE
}
