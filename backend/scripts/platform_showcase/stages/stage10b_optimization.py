"""Stage 10b — Portfolio Optimization Stage

Runs after Decision Stage to optimize the generated decisions into a recommended portfolio.
"""

from __future__ import annotations

from app.decision.optimization import DecisionOptimizationEngine, DecisionOptimizationRequest
from app.executive.intervention_cost import InterventionCost
from app.simulation.cost_model import CostModel
from scripts.platform_showcase.context import PlatformContext
from scripts.platform_showcase.stages.base import PipelineStage

from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from dataclasses import dataclass

@dataclass
class DecisionImpact:
    module_ref: EntityRef
    action: str
    expected_health_gain: float

class PortfolioOptimizationStage(PipelineStage):
    name = "Portfolio Optimization"

    def execute(self, context: PlatformContext) -> None:
        decisions = getattr(context, "decisions", ())
        if not decisions:
            return
            
        costs = []
        impacts = []
        
        for decision in decisions:
            # We just create a dummy cost and impact for the optimizer to work with.
            # In a full system, decisions would map cleanly to Interventions and specific EntityRefs.
            est_cost = 5.0
            gain = 2.0
            if "Transfer" in decision.action:
                est_cost = 3.0
                gain = 5.0
            elif "cross-training" in decision.action or "program" in decision.action:
                est_cost = 10.0
                gain = 8.0
            elif decision.priority == "high":
                gain = 10.0
            elif decision.priority == "medium":
                gain = 5.0
            else:
                gain = 1.0
                
            # Reconstruct the module reference since canonical Decision doesn't store it explicitly
            ref = EntityRef(id=decision.id, type=EntityType.MODULE)

            costs.append(InterventionCost(module_ref=ref, action=decision.action, estimated_cost=est_cost))
            impacts.append(DecisionImpact(module_ref=ref, action=decision.action, expected_health_gain=gain))

        request = DecisionOptimizationRequest(
            impacts=tuple(impacts),
            costs=tuple(costs),
            budget=30.0, # 30 dev days
            max_items=5,
        )

        engine = DecisionOptimizationEngine()
        portfolio = engine.optimize(request)
        
        # Save portfolio to metrics so Executive Dashboard can render it
        context.metrics["optimization_portfolio"] = portfolio
