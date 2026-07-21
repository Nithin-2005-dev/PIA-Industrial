from app.kernel.graph import GraphEngine, NodeType, EdgeType
from app.kernel.reasoning.rule_engine import RuleEngine
from app.kernel.reasoning.validator import GraphValidator
from enum import Enum

class PropagationPolicy(Enum):
    WEIGHTED_AVERAGE = "weighted_average"
    MINIMUM = "minimum"
    HARMONIC_MEAN = "harmonic_mean"

class StrategyEngine:
    """
    Decides meta-execution order of rules and handles conflict resolution.
    """
    def __init__(self, graph: GraphEngine, rule_engine: RuleEngine, propagation_policy: PropagationPolicy = PropagationPolicy.MINIMUM):
        self.graph = graph
        self.rule_engine = rule_engine
        self.propagation_policy = propagation_policy
        
    def execute_reasoning_cycle(self):
        """
        Executes a deterministic reasoning cycle.
        In Phase 2, this just runs all rules. In future phases, this will resolve conflicts 
        between rules, handle priorities, and prune the graph.
        """
        # Execute rules to generate inferences
        self.rule_engine.execute_all()
        
        # Meta-strategy: Prune dead paths, resolve contradictions
        self._resolve_contradictions()
        
        # Propagate confidence through the DAG
        self._propagate_confidence()
        
        # Validate Graph
        validator = GraphValidator(self.graph)
        validator.validate()
        
    def _resolve_contradictions(self):
        """
        Stub for graph-based conflict resolution (e.g. creating CONFLICT nodes)
        """
        pass

    def _propagate_confidence(self):
        """Propagates confidence through the DAG based on policy."""
        # Topologically sort nodes, or simply iterate layer by layer
        # For simplicity, propagate Inference -> Root Cause -> Recommendation
        
        inferences = self.graph.get_all_nodes(NodeType.INFERENCE)
        for inf in inferences:
            supports = self.graph.get_edges(inf.id, direction="out", edge_type=EdgeType.SUPPORTS)
            support_confs = [self.graph.get_node(e.target_id).confidence for e in supports if self.graph.get_node(e.target_id)]
            
            if support_confs:
                if self.propagation_policy == PropagationPolicy.MINIMUM:
                    inf_conf = min(support_confs)
                elif self.propagation_policy == PropagationPolicy.WEIGHTED_AVERAGE:
                    inf_conf = sum(support_confs) / len(support_confs)
                else: # Harmonic Mean
                    inf_conf = len(support_confs) / sum(1.0 / (c + 1e-9) for c in support_confs)
                    
                # Multiply by rule weight (already embedded in the inference's base confidence when created)
                # or we can just apply the policy. Since rule engine set confidence = avg * rule_weight,
                # let's overwrite it with proper propagation.
                # Actually, RuleEngine multiplies by rule.metadata.weight. We can extract it or assume it's part of the inf logic.
                # We'll just take the min for now as requested.
                # In python, dataclass is frozen. So we can't directly mutate inf.confidence easily unless we use object.__setattr__
                object.__setattr__(inf, "confidence", inf_conf * inf.confidence) # Applying rule weight which was in inf.confidence initially

        rc_nodes = self.graph.get_all_nodes(NodeType.ROOT_CAUSE)
        for rc in rc_nodes:
            causes = self.graph.get_edges(rc.id, direction="out", edge_type=EdgeType.CAUSES)
            # CAUSES points to IMPACT, wait, Root Cause -(causes)-> Impact
            # But Root Cause is derived from Evidence in the backwards trace. 
            # In Phase 4, root_cause.py sets it. We'll let root_cause.py handle it or we can handle it there.
            pass
