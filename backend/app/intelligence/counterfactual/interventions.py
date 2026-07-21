from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import SimulationIntervention


@dataclass(frozen=True)
class ContributorDepartureIntervention(SimulationIntervention):
    name: str = "Contributor Departure"
    developer_id: str = "unknown"

    def apply(self, context: Any) -> None:
        """
        Removes the specified developer's expertise from the context.
        This modifies both context.expertise_models and context.knowledge_graph.
        """
        # 1. Modify expertise_models list
        if hasattr(context, "expertise_models"):
            context.expertise_models = [
                m for m in context.expertise_models
                if getattr(m, "subject", "") != self.developer_id
            ]

        # 2. Modify knowledge_graph
        graph = getattr(context, "knowledge_graph", None)
        if graph is not None:
            if hasattr(graph, "nodes") and isinstance(graph.nodes, list):
                # Custom OrganizationalGraph (frozen dataclass, but list is mutable)
                new_nodes = [
                    n for n in graph.nodes
                    if not (n.type == "expertise" and getattr(n.attributes, "get", lambda k, d=None: d)("subject") == self.developer_id)
                ]
                graph.nodes[:] = new_nodes
            elif hasattr(graph, "remove_node"):
                # NetworkX Graph
                to_remove = [
                    node for node, data in graph.nodes(data=True)
                    if data.get("type") == "expertise" and data.get("subject") == self.developer_id
                ]
                for node in to_remove:
                    graph.remove_node(node)

    def restart_stage(self) -> str:
        return "knowledge"


@dataclass(frozen=True)
class OwnershipRedistributionIntervention(SimulationIntervention):
    name: str = "Ownership Redistribution"
    from_developer: str = "unknown"
    to_developer: str = "unknown"

    def apply(self, context: Any) -> None:
        """
        Transfers expertise from one developer to another.
        """
        # 1. Modify expertise_models list
        if hasattr(context, "expertise_models"):
            new_models = []
            for m in context.expertise_models:
                if getattr(m, "subject", "") == self.from_developer:
                    # We can't mutate frozen dataclasses easily without import, 
                    # so we rely on the graph mutation for downstream Org Intelligence.
                    pass
                new_models.append(m)
            context.expertise_models = new_models

        # 2. Modify knowledge_graph
        graph = getattr(context, "knowledge_graph", None)
        if graph is not None:
            if hasattr(graph, "nodes") and isinstance(graph.nodes, list):
                for n in graph.nodes:
                    if n.type == "expertise" and n.attributes and n.attributes.get("subject") == self.from_developer:
                        n.attributes["subject"] = self.to_developer
            elif hasattr(graph, "nodes"):
                for node, data in graph.nodes(data=True):
                    if data.get("type") == "expertise" and data.get("subject") == self.from_developer:
                        data["subject"] = self.to_developer

    def restart_stage(self) -> str:
        return "intelligence"


@dataclass(frozen=True)
class DocumentationImprovementIntervention(SimulationIntervention):
    name: str = "Documentation Improvement"
    boost_factor: float = 1.2

    def apply(self, context: Any) -> None:
        """
        Simulates an improvement in documentation metrics, boosting expertise scores by a factor.
        """
        graph = getattr(context, "knowledge_graph", None)
        if graph is not None:
            if hasattr(graph, "nodes") and isinstance(graph.nodes, list):
                for n in graph.nodes:
                    if n.type == "expertise" and n.attributes and "score" in n.attributes:
                        n.attributes["score"] *= self.boost_factor
            elif hasattr(graph, "nodes"):
                for node, data in graph.nodes(data=True):
                    if data.get("type") == "expertise" and "score" in data:
                        data["score"] *= self.boost_factor

    def restart_stage(self) -> str:
        return "estimation"


@dataclass(frozen=True)
class ReviewerLossIntervention(SimulationIntervention):
    name: str = "Reviewer Loss"
    reviewer_id: str = "unknown"

    def apply(self, context: Any) -> None:
        # Same as contributor departure for now, as reviewers and contributors share expertise models
        ContributorDepartureIntervention(developer_id=self.reviewer_id).apply(context)

    def restart_stage(self) -> str:
        return "knowledge"


@dataclass(frozen=True)
class TeamExpansionIntervention(SimulationIntervention):
    name: str = "Team Expansion"
    new_developer_id: str = "new_hire"
    category: str = "core"

    def apply(self, context: Any) -> None:
        """
        Adds a new developer with baseline expertise to a specified category.
        """
        graph = getattr(context, "knowledge_graph", None)
        if graph is not None:
            if hasattr(graph, "add_node"):
                # NetworkX
                node_id = f"expertise_{self.new_developer_id}_{self.category}"
                graph.add_node(node_id, type="expertise", subject=self.new_developer_id, category=self.category, score=0.5, confidence=0.5)

    def restart_stage(self) -> str:
        return "knowledge"


@dataclass(frozen=True)
class RepositorySplitIntervention(SimulationIntervention):
    name: str = "Repository Split"
    category_to_remove: str = "unknown"

    def apply(self, context: Any) -> None:
        """
        Simulates splitting a repository by removing all expertise/knowledge in a specific category.
        """
        graph = getattr(context, "knowledge_graph", None)
        if graph is not None:
            if hasattr(graph, "remove_node"):
                to_remove = [
                    node for node, data in graph.nodes(data=True)
                    if data.get("type") == "expertise" and data.get("category") == self.category_to_remove
                ]
                for node in to_remove:
                    graph.remove_node(node)

    def restart_stage(self) -> str:
        return "knowledge"


@dataclass(frozen=True)
class IncreasedPRVolumeIntervention(SimulationIntervention):
    name: str = "Increased PR Volume"

    def apply(self, context: Any) -> None:
        pass

    def restart_stage(self) -> str:
        return "evidence"


@dataclass(frozen=True)
class ReviewBottleneckIntervention(SimulationIntervention):
    name: str = "Review Bottleneck"

    def apply(self, context: Any) -> None:
        pass

    def restart_stage(self) -> str:
        return "evidence"


@dataclass(frozen=True)
class ReducedTestCoverageIntervention(SimulationIntervention):
    name: str = "Reduced Test Coverage"

    def apply(self, context: Any) -> None:
        pass

    def restart_stage(self) -> str:
        return "measurement"
