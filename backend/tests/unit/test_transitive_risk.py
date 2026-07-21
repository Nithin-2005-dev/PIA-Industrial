import pytest
from app.intelligence.risk.knowledge_risk_service import KnowledgeRiskService
from app.intelligence.risk.bus_factor import BusFactor
from app.intelligence.risk.risk_level import RiskLevel
from app.intelligence.risk.knowledge_risk import KnowledgeRisk
from app.knowledge.graph.organizational_graph import OrganizationalGraph
from app.knowledge.graph.graph_node import GraphNode
from app.knowledge.graph.graph_edge import GraphEdge
from app.knowledge.graph.graph_service import GraphService

class MockOwnershipService:
    def owners_of(self, module_id: str) -> list:
        # Mock 1 owner for API, 5 owners for Gateway
        if module_id == "Stripe_API_Wrapper":
            return ["Dev_C"]
        return ["Dev_A", "Dev_B", "Dev_C", "Dev_D", "Dev_E"]

class MockBusFactorService:
    def analyze(self, module_id: str) -> BusFactor:
        if module_id == "Stripe_API_Wrapper":
            return BusFactor(module_ref=module_id, risk_level=RiskLevel.HIGH, value=1, coverage=1.0, shannon_entropy=0.0, gini_coefficient=0.0, hhi=1.0, uncertainty=0.0, confidence=1.0)
        return BusFactor(module_ref=module_id, risk_level=RiskLevel.LOW, value=5, coverage=1.0, shannon_entropy=2.0, gini_coefficient=0.0, hhi=0.2, uncertainty=0.0, confidence=1.0)

class MockPolicy:
    def evaluate(self, bus_factor: BusFactor, owner_count: int) -> KnowledgeRisk:
        return KnowledgeRisk(
            module_ref=bus_factor.module_ref,
            risk_level=bus_factor.risk_level,
            bus_factor=bus_factor.value,
            ownership_count=owner_count,
            summary="Mock summary",
        )

def test_transitive_risk_bubbling():
    # 1. Setup Graph with dependency
    graph = OrganizationalGraph(
        nodes=[
            GraphNode("Payment_Gateway", "module", {}),
            GraphNode("Stripe_API_Wrapper", "module", {})
        ],
        edges=[
            GraphEdge("Payment_Gateway", "Stripe_API_Wrapper", "depends_on", 1.0)
        ]
    )
    
    graph_service = GraphService(graph)
    
    # 2. Setup Services
    ownership = MockOwnershipService()
    bus_factor = MockBusFactorService()
    policy = MockPolicy()
    
    service = KnowledgeRiskService(
        ownership_service=ownership,
        bus_factor_service=bus_factor,
        policy=policy,
        graph_service=graph_service
    )
    
    # 3. Analyze Transitive Risk
    # Direct risk of Payment_Gateway is LOW (5 owners)
    # But it DEPENDS_ON Stripe_API_Wrapper which is HIGH (1 owner)
    risk = service.analyze_transitive_risk("Payment_Gateway")
    
    # 4. Assert Risk bubbled up
    assert risk.risk_level == RiskLevel.HIGH
    assert "Transitive Risk Alert" in risk.summary
    assert "Stripe_API_Wrapper" in risk.summary
    assert risk.bus_factor == 1 # Inherited from Stripe_API_Wrapper

def test_transitive_risk_cycle():
    # 1. Setup Graph with cycle
    graph = OrganizationalGraph(
        nodes=[
            GraphNode("A", "module", {}),
            GraphNode("B", "module", {})
        ],
        edges=[
            GraphEdge("A", "B", "depends_on", 1.0),
            GraphEdge("B", "A", "depends_on", 1.0)
        ]
    )
    
    graph_service = GraphService(graph)
    
    # 2. Setup Services
    ownership = MockOwnershipService()
    bus_factor = MockBusFactorService() # Returns LOW by default
    policy = MockPolicy()
    
    service = KnowledgeRiskService(
        ownership_service=ownership,
        bus_factor_service=bus_factor,
        policy=policy,
        graph_service=graph_service
    )
    
    # 3. Analyze Transitive Risk
    risk = service.analyze_transitive_risk("A")
    
    # 4. Assert it doesn't infinite loop and returns safely
    assert risk.risk_level == RiskLevel.LOW
