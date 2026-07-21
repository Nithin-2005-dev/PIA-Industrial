from __future__ import annotations

import typing
from dataclasses import dataclass
from typing import Protocol

from app.intelligence.legacy.intervention_cost import InterventionCost
from app.intelligence.legacy.portfolio_item import PortfolioItem


@dataclass(frozen=True)
class DecisionOptimizationRequest:
    impacts: tuple[object, ...]
    costs: tuple[InterventionCost, ...]
    budget: float
    max_items: int | None = None


@dataclass(frozen=True)
class OptimizationPortfolio:
    selected_items: tuple[PortfolioItem, ...]
    total_expected_gain: float
    total_cost: float
    total_roi: float
    confidence: float
    uncertainty: float
    rationale: str
    rejected_count: int


class OptimizationAlgorithm(Protocol):
    name: str

    def optimize(
        self,
        request: DecisionOptimizationRequest,
        candidates: tuple[PortfolioItem, ...],
    ) -> tuple[PortfolioItem, ...]:
        ...


class OptimizationRegistry:
    def __init__(self):
        self._algorithms: dict[str, OptimizationAlgorithm] = {}
        self._default: str | None = None

    def register(self, algorithm: OptimizationAlgorithm, is_default: bool = False) -> None:
        self._algorithms[algorithm.name] = algorithm
        if is_default or self._default is None:
            self._default = algorithm.name

    def get(self, name: str | None = None) -> OptimizationAlgorithm:
        if name is None:
            name = self._default
        if name not in self._algorithms:
            raise ValueError(f"Optimization algorithm '{name}' not found.")
        return self._algorithms[name]


class GreedyOptimizer:
    name = "Greedy"

    def optimize(
        self,
        request: DecisionOptimizationRequest,
        candidates: tuple[PortfolioItem, ...],
    ) -> tuple[PortfolioItem, ...]:
        # Objective: Maximize (Benefit - Cost - Risk Penalty + Confidence Weight - Uncertainty Penalty)
        # For simplicity, we just sort candidates by ROI which loosely correlates to this objective.
        sorted_candidates = sorted(
            candidates,
            key=lambda item: (
                item.roi,
                item.expected_health_gain,
            ),
            reverse=True,
        )

        selected: list[PortfolioItem] = []
        total_cost = 0.0

        for candidate in sorted_candidates:
            if total_cost + candidate.estimated_cost <= request.budget:
                if request.max_items is not None and len(selected) >= request.max_items:
                    break
                selected.append(candidate)
                total_cost += candidate.estimated_cost

        return tuple(selected)


class KnapsackOptimizer:
    name = "Knapsack"

    def optimize(
        self,
        request: DecisionOptimizationRequest,
        candidates: tuple[PortfolioItem, ...],
    ) -> tuple[PortfolioItem, ...]:
        best: tuple[PortfolioItem, ...] = ()
        best_gain = -1.0
        best_cost = 0.0

        def visit(
            index: int,
            selected: tuple[PortfolioItem, ...],
            total_gain: float,
            total_cost: float,
        ) -> None:
            nonlocal best, best_gain, best_cost
            if total_cost > request.budget:
                return
            if request.max_items is not None and len(selected) > request.max_items:
                return
            if index == len(candidates):
                if total_gain > best_gain or (total_gain == best_gain and total_cost < best_cost):
                    best = selected
                    best_gain = total_gain
                    best_cost = total_cost
                return

            candidate = candidates[index]
            visit(index + 1, selected, total_gain, total_cost)
            visit(
                index + 1,
                (*selected, candidate),
                total_gain + candidate.expected_health_gain,
                total_cost + candidate.estimated_cost,
            )

        visit(0, (), 0.0, 0.0)
        return best


class DecisionOptimizationEngine:
    def __init__(self, registry: OptimizationRegistry | None = None):
        if registry is None:
            registry = OptimizationRegistry()
            registry.register(GreedyOptimizer(), is_default=True)
            registry.register(KnapsackOptimizer())
        self.registry = registry

    def optimize(
        self,
        request: DecisionOptimizationRequest,
        algorithm_name: str | None = None,
    ) -> OptimizationPortfolio:
        candidates = self._candidates(request.impacts, request.costs)
        
        algorithm = self.registry.get(algorithm_name)
        best = algorithm.optimize(request, candidates)

        ranked = tuple(
            PortfolioItem(
                module_ref=item.module_ref,
                action=item.action,
                expected_health_gain=item.expected_health_gain,
                estimated_cost=item.estimated_cost,
                roi=item.roi,
                rank=index + 1,
            )
            for index, item in enumerate(
                sorted(
                    best,
                    key=lambda x: (x.roi, x.expected_health_gain),
                    reverse=True,
                )
            )
        )
        total_gain = sum(item.expected_health_gain for item in ranked)
        total_cost = sum(item.estimated_cost for item in ranked)
        
        # Aggregate Confidence & Uncertainty (Simple average)
        confidence = 0.85 # Mocked for now, ideally derived from scenarios
        uncertainty = 0.15

        return OptimizationPortfolio(
            selected_items=ranked,
            total_expected_gain=total_gain,
            total_cost=total_cost,
            total_roi=(total_gain / total_cost if total_cost else 0.0),
            confidence=confidence,
            uncertainty=uncertainty,
            rationale=f"Selected {len(ranked)} interventions using {algorithm.name} optimizer to maximize health ROI.",
            rejected_count=len(candidates) - len(ranked),
        )

    def _candidates(
        self,
        impacts,
        costs,
    ) -> tuple[PortfolioItem, ...]:
        candidates = []
        for impact in impacts:
            cost = next(
                (
                    item
                    for item in costs
                    if (
                        item.action == impact.action
                        and item.module_ref.id == impact.module_ref.id
                    )
                ),
                None,
            )
            if cost is None or cost.estimated_cost <= 0:
                continue
                
            # Objective Function Component:
            # ROI = (Benefit - Risk Penalty) / Cost
            # In a full implementation, Risk Penalty, Confidence Weight, Uncertainty Penalty would be explicitly parsed from `impact` object.
            # Here we just use expected_health_gain.
            
            candidates.append(
                PortfolioItem(
                    module_ref=impact.module_ref,
                    action=impact.action,
                    expected_health_gain=impact.expected_health_gain,
                    estimated_cost=cost.estimated_cost,
                    roi=(impact.expected_health_gain / cost.estimated_cost),
                    rank=0,
                )
            )
        return tuple(candidates)
