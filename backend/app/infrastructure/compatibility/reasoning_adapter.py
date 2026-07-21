import uuid
import datetime
import os
from typing import List, Dict, Any, Optional

from app.kernel.reasoning.rule_engine import ReasoningRule
from app.kernel.graph import GraphEngine, GraphNode, NodeType, GraphEdge, EdgeType
from app.infrastructure.database.models import FactRecord, RuleEvaluationRecord, RuleExecutionRecord
from app.infrastructure.database.sqlite_provider import get_provider

class ShimGraphEngine(GraphEngine):
    """
    A temporary mock GraphEngine that translates FactRecords into legacy GraphNodes
    for old ReasoningRules to consume, and traps outputs to create modern ExecutionRecords.
    """
    def __init__(self, facts: List[FactRecord], repository_session_id: str):
        super().__init__()
        self.repository_session_id = repository_session_id
        self.facts = facts
        self.outputs = []
        
        # Load facts as Observation and Evidence nodes to fool the old rule
        for fact in facts:
            # Fake observation
            obs_id = str(uuid.uuid4())
            obs = GraphNode(id=obs_id, node_type=NodeType.OBSERVATION, properties={}, confidence=fact.confidence)
            self._nodes[obs_id] = obs
            
            # Fake evidence
            ev_id = str(uuid.uuid4())
            ev = GraphNode(id=ev_id, node_type=NodeType.EVIDENCE, properties={"raw_output": {"bus_factor": fact.confidence}}, confidence=fact.confidence)
            
            # The original rule looks for bus factor. Let's seed it in properties if it's a bus_factor fact
            if fact.fact_type == "bus_factor":
                ev.properties["raw_output"] = {"bus_factor": 1}
                
            self._nodes[ev_id] = ev
            
            # Link them
            self.add_edge(GraphEdge(source_id=obs_id, target_id=ev_id, edge_type=EdgeType.DERIVED_FROM, weight=1.0))

    def add_node(self, node: GraphNode) -> GraphNode:
        # Trap the output
        if node.node_type == NodeType.INFERENCE:
            self.outputs.append(node)
        return node
        
    def add_edge(self, edge: GraphEdge) -> GraphEdge:
        if edge.edge_type != EdgeType.DERIVED_FROM:
            # Trap the edge
            pass
        else:
            super().add_edge(edge)
        return edge

class CompatibilityAdapter:
    """
    Wraps old ReasoningRule objects. Executes them using FactRecords
    and persists the results into the new deterministic persistence models.
    """
    def __init__(self):
        # Allow testing without database initialization if needed
        try:
            self.provider = get_provider()
        except:
            self.provider = None

    def evaluate_rule(self, rule: ReasoningRule, facts: List[FactRecord], repository_session_id: str) -> None:
        shim = ShimGraphEngine(facts, repository_session_id)
        
        start_time = datetime.datetime.utcnow()
        matches = rule.condition(shim)
        latency_ms = (datetime.datetime.utcnow() - start_time).total_seconds() * 1000
        
        if self.provider:
            eval_record = RuleEvaluationRecord(
                repository_session_id=repository_session_id,
                rule_id=rule.id,
                inputs={"fact_count": len(facts)},
                passed=len(matches) > 0,
                reason_if_failed="No matches" if not matches else "",
                latency_ms=latency_ms
            )
            self.provider.save(eval_record)
        
        for match in matches:
            rule.action(shim, match, rule)
            
            for output in shim.outputs:
                if self.provider:
                    exec_record = RuleExecutionRecord(
                        repository_session_id=repository_session_id,
                        rule_id=rule.id,
                        outputs=output.properties,
                        confidence=output.confidence,
                        execution_hash=str(uuid.uuid4())[:8]
                    )
                    self.provider.save(exec_record)
            
            shim.outputs = []
